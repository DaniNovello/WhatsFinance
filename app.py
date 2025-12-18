# Arquivo: app.py
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

# Estados temporários
user_states = {} 
user_data_buffer = {}

# --- Teclados ---
def get_main_menu_keyboard():
    return {'inline_keyboard': [[{'text': '💰 Saldo & Faturas', 'callback_data': '/saldo'}, {'text': '📝 Últimos', 'callback_data': '/ultimos'}], [{'text': '📊 Relatórios', 'callback_data': 'menu_relatorios'}, {'text': '⚙️ Contas e Cartões', 'callback_data': 'menu_config'}]]}
def get_reports_keyboard(): return {'inline_keyboard': [[{'text': '📅 Semana', 'callback_data': '/relatorio_esta_semana'}, {'text': '📆 Mês', 'callback_data': '/relatorio_mes_atual'}], [{'text': '🔙 Voltar', 'callback_data': '/menu'}]]}
def get_config_keyboard(): return {'inline_keyboard': [[{'text': '➕ Nova Conta', 'callback_data': 'btn_new_account'}, {'text': '💳 Novo Cartão', 'callback_data': 'btn_new_card'}], [{'text': '🔙 Voltar', 'callback_data': '/menu'}]]}

def send_message(chat_id, text, reply_markup=None):
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup: payload['reply_markup'] = reply_markup
    try: requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
    except: pass

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data: return "OK", 200

    # 1. CALLBACKS (CLIQUE NOS BOTÕES)
    if 'callback_query' in data:
        cb = data['callback_query']
        chat_id = cb['message']['chat']['id']
        raw_data = cb['data']
        # Avisa Telegram que recebeu o clique
        requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={'callback_query_id': cb['id']})

        # --- SELEÇÃO DE CONTA (Para Entradas ou Débitos) ---
        if raw_data.startswith('sel_acc_'):
            acc_id = int(raw_data.split('_')[2])
            last = db.get_last_transactions(chat_id, 1)
            if last:
                db.update_transaction_account(last[0]['id'], acc_id)
                send_message(chat_id, "✅ Saldo da conta atualizado!")
            return "OK", 200

        # --- SELEÇÃO DE CARTÃO (Para Crédito) ---
        elif raw_data.startswith('sel_card_'):
            card_id = int(raw_data.split('_')[2])
            last = db.get_last_transactions(chat_id, 1)
            if last:
                db.update_transaction_card(last[0]['id'], card_id)
                send_message(chat_id, "✅ Lançado na fatura do cartão!")
            return "OK", 200

        # --- NAVEGAÇÃO ---
        elif raw_data == '/menu': send_message(chat_id, "🤖 *Menu Principal*", reply_markup=get_main_menu_keyboard())
        elif raw_data == 'menu_relatorios': send_message(chat_id, "📊 *Relatórios*", reply_markup=get_reports_keyboard())
        elif raw_data == 'menu_config': send_message(chat_id, "⚙️ *Configurações*", reply_markup=get_config_keyboard())
        elif raw_data == '/saldo': send_message(chat_id, commands.handle_command('saldo', chat_id))
        elif raw_data == '/ultimos': send_message(chat_id, commands.handle_command('ultimos', chat_id))
        
        # --- CRIAÇÃO ---
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

    # 2. MENSAGENS (TEXTO E FOTO)
    if 'message' in data:
        msg = data['message']
        chat_id = msg['chat']['id']
        text = msg.get('text', '').strip()
        
        # Garante usuário
        if not db.get_user(chat_id): db.create_user(chat_id, msg['from'].get('first_name', 'User'))

        # Fluxos de Criação Interativa
        if chat_id in user_states:
            state = user_states[chat_id]
            if text == '/cancelar':
                del user_states[chat_id]; send_message(chat_id, "Cancelado."); return "OK", 200
            
            if state == 'awaiting_account_name':
                db.create_account(chat_id, text)
                del user_states[chat_id]
                send_message(chat_id, f"✅ Conta *{text}* criada!", reply_markup=get_config_keyboard())
            
            elif state == 'awaiting_card_name':
                user_data_buffer[chat_id] = {'name': text}
                user_states[chat_id] = 'awaiting_card_closing'
                send_message(chat_id, "📅 Qual o dia do fechamento? (Digite só o número)")
            
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
                    send_message(chat_id, f"✅ Cartão *{dat['name']}* criado!", reply_markup=get_config_keyboard())
            return "OK", 200

        # Tratamento de Comandos
        if text == '/menu': 
            send_message(chat_id, "🤖 *Menu Principal*", reply_markup=get_main_menu_keyboard())
            return "OK", 200
        
        if text.startswith('/'): 
            send_message(chat_id, commands.handle_command(text, chat_id))
            return "OK", 200

        # IA (Foto ou Texto)
        image_bytes = None
        if 'photo' in msg:
            try:
                f_id = msg['photo'][-1]['file_id']
                path = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={f_id}").json()['result']['file_path']
                image_bytes = requests.get(f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{path}").content
                text = msg.get('caption', '')
                send_message(chat_id, "🔎 Analisando comprovante...")
            except: pass

        if text or image_bytes:
            ai_data = ai_parser.get_ai_response(text, image_bytes)
            
            if not ai_data:
                send_message(chat_id, "Não entendi.")
                return "OK", 200

            intent = ai_data.get('intent')
            entities = ai_data.get('entities', {})

            if intent == 'register_transaction':
                inst = entities.get('installments', 1)
                
                # Se for parcelado > cria parcelas, senão cria transação única
                success = db.create_installments(chat_id, entities, inst) if isinstance(inst, int) and inst > 1 else db.process_transaction_with_rpc(chat_id, entities)
                
                if success:
                    tip = entities.get('type')
                    val = entities.get('amount')
                    desc = entities.get('description')
                    pay = entities.get('payment_method')

                    # 1. É ENTRADA (Income)? -> Pergunta Conta
                    if tip == 'income':
                        accs = db.get_user_accounts(chat_id)
                        if accs:
                            kb = {'inline_keyboard': [[{'text': f"🏦 {a['name']}", 'callback_data': f"sel_acc_{a['id']}"}] for a in accs]}
                            send_message(chat_id, f"💰 Recebido R${val} de {desc}.\nEntrou em qual conta?", reply_markup=kb)
                        else:
                            send_message(chat_id, f"✅ Recebido R${val}. (Dica: Crie uma conta no menu para gerenciar seu saldo)")

                    # 2. É GASTO no CRÉDITO? -> Pergunta Cartão
                    elif pay == 'credit_card':
                        cards = db.get_user_cards(chat_id)
                        if cards:
                            kb = {'inline_keyboard': [[{'text': f"💳 {c['name']}", 'callback_data': f"sel_card_{c['id']}"}] for c in cards]}
                            send_message(chat_id, f"✅ Gasto R${val}. Qual cartão?", reply_markup=kb)
                        else:
                            send_message(chat_id, f"✅ Gasto R${val} (Crédito). (Cadastre seus cartões no menu!)")

                    # 3. É GASTO no DÉBITO/PIX? -> Pergunta Conta
                    elif pay in ['debit_card', 'pix', 'money']:
                        accs = db.get_user_accounts(chat_id)
                        if accs:
                            kb = {'inline_keyboard': [[{'text': f"🏦 {a['name']}", 'callback_data': f"sel_acc_{a['id']}"}] for a in accs]}
                            send_message(chat_id, f"✅ Gasto R${val}. Saiu de qual conta?", reply_markup=kb)
                        else:
                            send_message(chat_id, f"✅ Gasto R${val}. (Cadastre contas para controlar seu saldo)")
                    
                    else:
                        send_message(chat_id, f"✅ Registrado: {desc} (R${val})")
                else:
                    send_message(chat_id, "Erro ao salvar no banco.")

            elif intent == 'query_report':
                report = commands.handle_command(f"relatorio_{entities.get('time_period', 'this_week')}", chat_id)
                send_message(chat_id, report)

    return "OK", 200

# Health Check (Correção para logs limpos)
@app.route('/health', methods=['GET', 'HEAD'])
def health(): return "OK", 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)