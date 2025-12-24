import os
import logging
from flask import Flask, request
from flask_login import LoginManager
from dotenv import load_dotenv
import requests

import db
import commands
import ai_parser

# Importa o módulo web
from web_routes import web_bp, User

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave_secreta_zenith")

# --- CONFIGURAÇÃO WEB ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'web.login'

@login_manager.user_loader
def load_user(user_id):
    u = db.get_user(user_id)
    if u: return User(u['id'], u['name'])
    return None

app.register_blueprint(web_bp)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# --- Estados e Memória ---
user_states = {} 
user_data_buffer = {}

# --- Teclados (Helpers) ---
def get_main_menu_keyboard():
    return {'inline_keyboard': [[{'text': '💰 Saldo & Faturas', 'callback_data': '/saldo'}, {'text': '📝 Últimos', 'callback_data': '/ultimos'}], [{'text': '📊 Relatórios', 'callback_data': 'menu_relatorios'}, {'text': '⚙️ Contas e Cartões', 'callback_data': 'menu_config'}]]}

def get_reports_keyboard(): 
    return {'inline_keyboard': [[{'text': '📅 Semana', 'callback_data': '/relatorio_esta_semana'}, {'text': '📆 Mês', 'callback_data': '/relatorio_mes_atual'}], [{'text': '🔙 Voltar', 'callback_data': '/menu'}]]}

def get_config_keyboard(): 
    return {'inline_keyboard': [[{'text': '➕ Nova Conta', 'callback_data': 'btn_new_account'}, {'text': '💳 Novo Cartão', 'callback_data': 'btn_new_card'}], [{'text': '🔙 Voltar', 'callback_data': '/menu'}]]}

def get_type_keyboard():
    return {'inline_keyboard': [[
        {'text': '🔴 Gastei (Saída)', 'callback_data': 'set_type_expense'},
        {'text': '🟢 Ganhei (Entrada)', 'callback_data': 'set_type_income'}
    ]]}

def get_method_keyboard():
    return {'inline_keyboard': [
        [{'text': '💳 Crédito', 'callback_data': 'set_method_credit_card'}, {'text': '🏧 Débito', 'callback_data': 'set_method_debit_card'}], 
        [{'text': '💠 Pix', 'callback_data': 'set_method_pix'}, {'text': '💵 Dinheiro', 'callback_data': 'set_method_money'}]
    ]}

def send_message(chat_id, text, reply_markup=None):
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup: payload['reply_markup'] = reply_markup
    try: 
        r = requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
        # Log para debug se falhar
        if r.status_code != 200:
            logger.error(f"Erro Telegram: {r.text}")
    except Exception as e: 
        logger.error(f"Erro request: {e}")

# --- Lógica de Salvamento ---
def trigger_save_and_continue(chat_id, entities):
    inst = entities.get('installments', 1)
    if isinstance(inst, int) and inst > 1:
        success = db.create_installments(chat_id, entities, inst)
    else:
        success = db.process_transaction_with_rpc(chat_id, entities)

    if not success:
        send_message(chat_id, "❌ Erro ao salvar no banco.")
        return

    if chat_id in user_data_buffer: del user_data_buffer[chat_id]
    if chat_id in user_states: del user_states[chat_id]
    
    ask_follow_up_questions(chat_id, entities)

def ask_follow_up_questions(chat_id, transaction_data):
    tipo = transaction_data.get('type')
    pay = transaction_data.get('payment_method')
    val = transaction_data.get('amount')
    desc = transaction_data.get('description')

    if tipo == 'expense' and not pay:
        send_message(chat_id, f"📝 Registrei *{desc}* (R${val}).\nQual foi a forma de pagamento?", reply_markup=get_method_keyboard())
        return

    if pay == 'credit_card':
        cards = db.get_user_cards(chat_id)
        if cards:
            kb = {'inline_keyboard': [[{'text': f"💳 {c['name']}", 'callback_data': f"sel_card_{c['id']}"}] for c in cards]}
            send_message(chat_id, f"💳 Gasto no crédito. Em qual cartão?", reply_markup=kb)
        else:
            send_message(chat_id, f"⚠️ Registrado (sem cartão cadastrado).")
        return

    if tipo == 'income' or pay in ['debit_card', 'pix', 'money']:
        accs = db.get_user_accounts(chat_id)
        if accs:
            action_text = "Entrou em" if tipo == 'income' else "Saiu de"
            kb = {'inline_keyboard': [[{'text': f"🏦 {a['name']}", 'callback_data': f"sel_acc_{a['id']}"}] for a in accs]}
            send_message(chat_id, f"💰 {action_text} qual conta?", reply_markup=kb)
        else:
            send_message(chat_id, f"✅ Registrado!")
        return

    send_message(chat_id, f"✅ *{desc}* (R${val}) registrado!")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data: return "OK", 200

    # --- CALLBACKS (Botões) ---
    if 'callback_query' in data:
        cb = data['callback_query']
        chat_id = cb['message']['chat']['id']
        raw_data = cb['data']
        requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={'callback_query_id': cb['id']})

        if raw_data.startswith('set_type_'):
            new_type = 'income' if 'income' in raw_data else 'expense'
            if chat_id in user_data_buffer:
                ents = user_data_buffer[chat_id]
                ents['type'] = new_type
                
                # Ajuste de descrição baseado no tipo
                payer = ents.get('payer_name')
                payee = ents.get('payee_name')
                final_desc = payee if new_type == 'expense' and payee else payer
                if final_desc: ents['description'] = final_desc

                desc = ents.get('description')
                if not desc or desc.lower() in ['none', 'null']:
                    user_states[chat_id] = 'awaiting_description'
                    send_message(chat_id, f"ok, é uma {('Entrada' if new_type == 'income' else 'Saída')}.\nMas qual o nome da descrição?")
                else:
                    trigger_save_and_continue(chat_id, ents)
            else:
                send_message(chat_id, "⚠️ Sessão expirada.")
            return "OK", 200

        elif raw_data.startswith('sel_acc_'):
            acc_id = int(raw_data.split('_')[2])
            last = db.get_last_transactions(chat_id, 1)
            if last:
                db.update_transaction_account(last[0]['id'], acc_id)
                send_message(chat_id, "✅ Saldo atualizado!")
            return "OK", 200

        elif raw_data.startswith('sel_card_'):
            card_id = int(raw_data.split('_')[2])
            last = db.get_last_transactions(chat_id, 1)
            if last:
                db.update_transaction_card(last[0]['id'], card_id)
                send_message(chat_id, "✅ Fatura atualizada!")
            return "OK", 200

        elif raw_data.startswith('set_method_'):
            method = raw_data.replace('set_method_', '')
            last = db.get_last_transactions(chat_id, 1)
            if last:
                db.update_transaction_method(last[0]['id'], method)
                trans_data = last[0]
                trans_data['payment_method'] = method
                ask_follow_up_questions(chat_id, trans_data)
            return "OK", 200

        elif raw_data == '/menu': send_message(chat_id, "🤖 *Menu Principal*", reply_markup=get_main_menu_keyboard())
        elif raw_data == 'menu_relatorios': send_message(chat_id, "📊 *Relatórios*", reply_markup=get_reports_keyboard())
        elif raw_data == 'menu_config': send_message(chat_id, "⚙️ *Configurações*", reply_markup=get_config_keyboard())
        elif raw_data == '/saldo': send_message(chat_id, commands.handle_command('saldo', chat_id))
        elif raw_data == '/ultimos': send_message(chat_id, commands.handle_command('ultimos', chat_id))
        
        elif raw_data == 'btn_new_account':
            user_states[chat_id] = 'awaiting_account_name'
            send_message(chat_id, "🏦 Qual o nome do banco?")
        elif raw_data == 'btn_new_card':
            user_states[chat_id] = 'awaiting_card_name'
            user_data_buffer[chat_id] = {}
            send_message(chat_id, "💳 Qual o nome do cartão?")
        else:
            send_message(chat_id, commands.handle_command(raw_data, chat_id))
        
        return "OK", 200

    # --- MENSAGENS DE TEXTO E IMAGEM ---
    if 'message' in data:
        msg = data['message']
        chat_id = msg['chat']['id']
        text = msg.get('text', '').strip()
        
        if not db.get_user(chat_id): 
            db.create_user(chat_id, msg['from'].get('first_name', 'User'))

        # 1. Checa Comandos de Estado (Cadastro)
        if chat_id in user_states:
            state = user_states[chat_id]
            if text == '/cancelar':
                del user_states[chat_id]
                if chat_id in user_data_buffer: del user_data_buffer[chat_id]
                send_message(chat_id, "Cancelado.")
                return "OK", 200

            if state == 'awaiting_description':
                if chat_id in user_data_buffer:
                    user_data_buffer[chat_id]['description'] = text
                    trigger_save_and_continue(chat_id, user_data_buffer[chat_id])
                del user_states[chat_id]
                return "OK", 200

            if state == 'awaiting_account_name':
                db.create_account(chat_id, text)
                del user_states[chat_id]
                send_message(chat_id, f"✅ Conta *{text}* criada!", reply_markup=get_config_keyboard())
                return "OK", 200
            
            elif state == 'awaiting_card_name':
                user_data_buffer[chat_id] = {'name': text}
                user_states[chat_id] = 'awaiting_card_closing'
                send_message(chat_id, "📅 Fecha dia? (Digite apenas o número)")
                return "OK", 200
            
            elif state == 'awaiting_card_closing':
                if text.isdigit():
                    user_data_buffer[chat_id]['closing'] = int(text)
                    user_states[chat_id] = 'awaiting_card_due'
                    send_message(chat_id, "📅 Vence dia? (Digite apenas o número)")
                else:
                    send_message(chat_id, "⚠️ Digite um número válido.")
                return "OK", 200
            
            elif state == 'awaiting_card_due':
                if text.isdigit():
                    d = user_data_buffer[chat_id]
                    db.create_credit_card(chat_id, d['name'], d['closing'], int(text))
                    del user_states[chat_id]
                    send_message(chat_id, "✅ Cartão criado!", reply_markup=get_config_keyboard())
                else:
                    send_message(chat_id, "⚠️ Digite um número válido.")
                return "OK", 200

        # 2. Checa Comandos de Menu (Iniciados por /)
        if text.startswith('/'): 
            send_message(chat_id, commands.handle_command(text, chat_id))
            return "OK", 200
        
        # 3. Processamento de IA (Texto Livre ou Imagem)
        image_bytes = None
        if 'photo' in msg:
            try:
                f_id = msg['photo'][-1]['file_id']
                path = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={f_id}").json()['result']['file_path']
                image_bytes = requests.get(f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{path}").content
                text = msg.get('caption', '') # Pega a legenda da foto se houver
                send_message(chat_id, "🔎 Analisando comprovante...")
            except Exception as e:
                logger.error(f"Erro download img: {e}")

        # Se tiver Texto ou Imagem, chama a IA
        if text or image_bytes:
            ai_data = ai_parser.get_ai_response(text, image_bytes)
            
            # Se a IA retornou erro ou None
            if not ai_data:
                send_message(chat_id, "Não entendi o que você disse. Tente usar o menu ou escrever de forma mais clara.")
                return "OK", 200

            intent = ai_data.get('intent')
            entities = ai_data.get('entities', {})

            # --- ROTEAMENTO DE INTENÇÕES ---
            if intent == 'register_transaction':
                if image_bytes:
                    user_data_buffer[chat_id] = entities
                    send_message(chat_id, f"🧾 Li um valor de R${entities.get('amount')}.\nIsso é Entrada ou Saída?", reply_markup=get_type_keyboard())
                    return "OK", 200

                # Texto puro sem descrição clara
                if not entities.get('description'):
                    user_data_buffer[chat_id] = entities
                    user_states[chat_id] = 'awaiting_description'
                    send_message(chat_id, f"💰 Entendi o valor R${entities.get('amount')}. Qual a descrição?")
                    return "OK", 200

                trigger_save_and_continue(chat_id, entities)

            elif intent == 'query_report':
                report = commands.handle_command(f"relatorio_{entities.get('time_period', 'this_week')}", chat_id)
                send_message(chat_id, report)
            
            elif intent == 'greeting':
                 send_message(chat_id, commands.handle_command('start', chat_id))
            
            else:
                # Intent 'unknown' ou qualquer outra coisa que a IA inventar
                send_message(chat_id, "Desculpe, não entendi. Use /menu para ver as opções ou digite um gasto (ex: 'Almoço 30 reais').")

    return "OK", 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)