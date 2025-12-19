import os
import requests
import logging
from flask import Flask, request
from dotenv import load_dotenv

import db
import commands
import ai_parser

load_dotenv()
app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# --- Estados e Memória Temporária ---
user_states = {} 
user_data_buffer = {}

# --- Teclados ---
def get_main_menu_keyboard():
    return {'inline_keyboard': [[{'text': '💰 Saldo & Faturas', 'callback_data': '/saldo'}, {'text': '📝 Últimos', 'callback_data': '/ultimos'}], [{'text': '📊 Relatórios', 'callback_data': 'menu_relatorios'}, {'text': '⚙️ Contas e Cartões', 'callback_data': 'menu_config'}]]}

def get_reports_keyboard(): 
    return {'inline_keyboard': [[{'text': '📅 Semana', 'callback_data': '/relatorio_esta_semana'}, {'text': '📆 Mês', 'callback_data': '/relatorio_mes_atual'}], [{'text': '🔙 Voltar', 'callback_data': '/menu'}]]}

def get_config_keyboard(): 
    return {'inline_keyboard': [[{'text': '➕ Nova Conta', 'callback_data': 'btn_new_account'}, {'text': '💳 Novo Cartão', 'callback_data': 'btn_new_card'}], [{'text': '🔙 Voltar', 'callback_data': '/menu'}]]}

# NOVO: Teclado para definir Tipo (Entrada/Saída) após imagem
def get_type_keyboard():
    return {'inline_keyboard': [[
        {'text': '🔴 Gastei (Saída)', 'callback_data': 'set_type_expense'},
        {'text': '🟢 Ganhei (Entrada)', 'callback_data': 'set_type_income'}
    ]]}

# Teclado para escolher método de pagamento
def get_method_keyboard():
    return {'inline_keyboard': [
        [{'text': '💳 Crédito', 'callback_data': 'set_method_credit_card'}, {'text': '🏧 Débito', 'callback_data': 'set_method_debit_card'}], 
        [{'text': '💠 Pix', 'callback_data': 'set_method_pix'}, {'text': '💵 Dinheiro', 'callback_data': 'set_method_money'}]
    ]}

def send_message(chat_id, text, reply_markup=None):
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup: payload['reply_markup'] = reply_markup
    try: requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
    except: pass

# --- Funções Auxiliares de Fluxo ---

def trigger_save_and_continue(chat_id, entities):
    """
    Função central que salva no banco e decide qual a próxima pergunta (Cartão? Conta?).
    """
    # 1. Tenta Salvar
    inst = entities.get('installments', 1)
    
    # Se for parcelado usa uma lógica, se for a vista usa RPC
    if isinstance(inst, int) and inst > 1:
        success = db.create_installments(chat_id, entities, inst)
    else:
        success = db.process_transaction_with_rpc(chat_id, entities)

    if not success:
        send_message(chat_id, "❌ Erro ao salvar no banco de dados.")
        return

    # 2. Inicia as Perguntas de Follow-up (Conta, Cartão, Método)
    # Limpa buffer pois já salvou
    if chat_id in user_data_buffer: del user_data_buffer[chat_id]
    if chat_id in user_states: del user_states[chat_id]
    
    # Chama a lógica de perguntas
    ask_follow_up_questions(chat_id, entities)

def ask_follow_up_questions(chat_id, transaction_data):
    """Verifica se precisa perguntar Conta, Cartão ou Método após salvar"""
    tipo = transaction_data.get('type')
    pay = transaction_data.get('payment_method')
    val = transaction_data.get('amount')
    desc = transaction_data.get('description')

    # Caso 1: Método desconhecido (Gasto) -> Pergunta método
    if tipo == 'expense' and not pay:
        send_message(chat_id, f"📝 Registrei *{desc}* (R${val}).\nQual foi a forma de pagamento?", reply_markup=get_method_keyboard())
        return

    # Caso 2: Crédito -> Pergunta qual cartão
    if pay == 'credit_card':
        cards = db.get_user_cards(chat_id)
        if cards:
            kb = {'inline_keyboard': [[{'text': f"💳 {c['name']}", 'callback_data': f"sel_card_{c['id']}"}] for c in cards]}
            send_message(chat_id, f"💳 Gasto no crédito. Em qual cartão?", reply_markup=kb)
        else:
            send_message(chat_id, f"⚠️ Registrado, mas você não tem cartões cadastrados.")
        return

    # Caso 3: Entrada ou Débito/Pix -> Pergunta qual conta
    if tipo == 'income' or pay in ['debit_card', 'pix', 'money']:
        accs = db.get_user_accounts(chat_id)
        if accs:
            action_text = "Entrou em" if tipo == 'income' else "Saiu de"
            kb = {'inline_keyboard': [[{'text': f"🏦 {a['name']}", 'callback_data': f"sel_acc_{a['id']}"}] for a in accs]}
            send_message(chat_id, f"💰 {action_text} qual conta?", reply_markup=kb)
        else:
            send_message(chat_id, f"✅ Registrado! (Cadastre contas para gerenciar saldo)")
        return

    # Se nada faltar
    send_message(chat_id, f"✅ *{desc}* (R${val}) registrado com sucesso!")


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data: return "OK", 200

    if 'callback_query' in data:
        cb = data['callback_query']
        chat_id = cb['message']['chat']['id']
        raw_data = cb['data']
        requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={'callback_query_id': cb['id']})

        # --- FLUXO: DEFINIÇÃO DE TIPO (ENTRADA/SAÍDA) ---
        if raw_data.startswith('set_type_'):
            new_type = 'income' if 'income' in raw_data else 'expense'
            
            # Recupera dados do buffer
            if chat_id in user_data_buffer:
                user_data_buffer[chat_id]['type'] = new_type
                entities = user_data_buffer[chat_id]
                
                # VERIFICA DESCRIÇÃO ANTES DE SALVAR
                # Se a IA não pegou o nome, ou pegou algo genérico, pergunta agora
                desc = entities.get('description')
                if not desc or desc.lower() == 'none' or desc == 'null':
                    user_states[chat_id] = 'awaiting_description'
                    send_message(chat_id, f"ok, é uma {('Entrada' if new_type == 'income' else 'Saída')}.\nMas qual a descrição? (Ex: Mercado, Salário)")
                else:
                    # Se já tem descrição, SALVA e segue o fluxo
                    trigger_save_and_continue(chat_id, entities)
            else:
                send_message(chat_id, "⚠️ Sessão expirada. Envie o comprovante novamente.")
            return "OK", 200

        # --- SELEÇÃO DE CONTA ---
        elif raw_data.startswith('sel_acc_'):
            acc_id = int(raw_data.split('_')[2])
            last = db.get_last_transactions(chat_id, 1)
            if last:
                db.update_transaction_account(last[0]['id'], acc_id)
                send_message(chat_id, "✅ Conta vinculada e saldo atualizado!")
            return "OK", 200

        # --- SELEÇÃO DE CARTÃO ---
        elif raw_data.startswith('sel_card_'):
            card_id = int(raw_data.split('_')[2])
            last = db.get_last_transactions(chat_id, 1)
            if last:
                db.update_transaction_card(last[0]['id'], card_id)
                send_message(chat_id, "✅ Fatura atualizada!")
            return "OK", 200

        # --- SELEÇÃO DE MÉTODO ---
        elif raw_data.startswith('set_method_'):
            method = raw_data.replace('set_method_', '')
            last = db.get_last_transactions(chat_id, 1)
            if last:
                db.update_transaction_method(last[0]['id'], method)
                # Recarrega para ver se precisa perguntar cartão/conta
                trans_data = last[0]
                trans_data['payment_method'] = method
                ask_follow_up_questions(chat_id, trans_data)
            return "OK", 200

        # --- NAVEGAÇÃO ---
        elif raw_data == '/menu': send_message(chat_id, "🤖 *Menu Principal*", reply_markup=get_main_menu_keyboard())
        elif raw_data == 'menu_relatorios': send_message(chat_id, "📊 *Relatórios*", reply_markup=get_reports_keyboard())
        elif raw_data == 'menu_config': send_message(chat_id, "⚙️ *Configurações*", reply_markup=get_config_keyboard())
        elif raw_data == '/saldo': send_message(chat_id, commands.handle_command('saldo', chat_id))
        elif raw_data == '/ultimos': send_message(chat_id, commands.handle_command('ultimos', chat_id))
        
        elif raw_data == 'btn_new_account':
            user_states[chat_id] = 'awaiting_account_name'
            send_message(chat_id, "🏦 Qual o nome do banco ou carteira?")
        elif raw_data == 'btn_new_card':
            user_states[chat_id] = 'awaiting_card_name'
            user_data_buffer[chat_id] = {}
            send_message(chat_id, "💳 Qual o nome do cartão?")
        else:
            send_message(chat_id, commands.handle_command(raw_data, chat_id))
        
        return "OK", 200

    if 'message' in data:
        msg = data['message']
        chat_id = msg['chat']['id']
        text = msg.get('text', '').strip()
        
        if not db.get_user(chat_id): db.create_user(chat_id, msg['from'].get('first_name', 'User'))

        # --- FLUXOS DE ESTADO (Conversa) ---
        if chat_id in user_states:
            state = user_states[chat_id]
            
            if text == '/cancelar':
                del user_states[chat_id]
                if chat_id in user_data_buffer: del user_data_buffer[chat_id]
                send_message(chat_id, "Cancelado.")
                return "OK", 200
            
            # --- FLUXO: DESCRIÇÃO FALTANTE ---
            if state == 'awaiting_description':
                if chat_id in user_data_buffer:
                    user_data_buffer[chat_id]['description'] = text
                    # Agora salva
                    trigger_save_and_continue(chat_id, user_data_buffer[chat_id])
                else:
                    send_message(chat_id, "Erro de sessão. Tente novamente.")
                    del user_states[chat_id]
                return "OK", 200

            # --- FLUXOS DE CADASTRO ---
            if state == 'awaiting_account_name':
                db.create_account(chat_id, text)
                del user_states[chat_id]
                send_message(chat_id, f"✅ Conta *{text}* criada!", reply_markup=get_config_keyboard())
            
            elif state == 'awaiting_card_name':
                user_data_buffer[chat_id] = {'name': text}
                user_states[chat_id] = 'awaiting_card_closing'
                send_message(chat_id, "📅 Qual o dia do fechamento? (Só o número)")
            
            elif state == 'awaiting_card_closing':
                if text.isdigit():
                    user_data_buffer[chat_id]['closing'] = int(text)
                    user_states[chat_id] = 'awaiting_card_due'
                    send_message(chat_id, "📅 E o dia do vencimento?")
            
            elif state == 'awaiting_card_due':
                if text.isdigit():
                    dat = user_data_buffer[chat_id]
                    db.create_credit_card(chat_id, dat['name'], dat['closing'], int(text))
                    del user_states[chat_id]
                    if chat_id in user_data_buffer: del user_data_buffer[chat_id]
                    send_message(chat_id, f"✅ Cartão *{dat['name']}* criado!", reply_markup=get_config_keyboard())
            return "OK", 200

        # Comandos básicos
        if text == '/menu': 
            send_message(chat_id, "🤖 *Menu Principal*", reply_markup=get_main_menu_keyboard())
            return "OK", 200
        
        if text.startswith('/'): 
            send_message(chat_id, commands.handle_command(text, chat_id))
            return "OK", 200

        # --- IA (Processamento de Imagem ou Texto) ---
        image_bytes = None
        if 'photo' in msg:
            try:
                f_id = msg['photo'][-1]['file_id']
                path = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={f_id}").json()['result']['file_path']
                image_bytes = requests.get(f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{path}").content
                text = msg.get('caption', '')
                send_message(chat_id, "🔎 Li o comprovante...")
            except: pass

        if text or image_bytes:
            ai_data = ai_parser.get_ai_response(text, image_bytes)
            
            if not ai_data:
                send_message(chat_id, "Não entendi.")
                return "OK", 200

            intent = ai_data.get('intent')
            entities = ai_data.get('entities', {})

            if intent == 'register_transaction':
                
                # SE FOR IMAGEM: Interrompe e pergunta o Tipo
                if image_bytes:
                    user_data_buffer[chat_id] = entities
                    # Não define state ainda, o botão define o fluxo
                    send_message(chat_id, f"🧾 Identifiquei R${entities.get('amount')}.\nIsso é uma Entrada ou Saída?", reply_markup=get_type_keyboard())
                    return "OK", 200

                # SE FOR TEXTO (ex: "Gastei 50"): Segue fluxo normal
                # Mas ainda verifica descrição
                if not entities.get('description'):
                    user_data_buffer[chat_id] = entities
                    user_states[chat_id] = 'awaiting_description'
                    send_message(chat_id, f"💰 Identifiquei R${entities.get('amount')}. Mas com o que foi esse gasto/ganho?")
                    return "OK", 200

                # Se for texto completo, salva direto
                trigger_save_and_continue(chat_id, entities)

            elif intent == 'query_report':
                report = commands.handle_command(f"relatorio_{entities.get('time_period', 'this_week')}", chat_id)
                send_message(chat_id, report)

    return "OK", 200

@app.route('/health', methods=['GET', 'HEAD'])
def health(): return "OK", 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)