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

# Estados para criação de cartão/conta
user_states = {} 
user_data_buffer = {}

# --- Teclados ---
def get_main_menu_keyboard():
    return {'inline_keyboard': [[{'text': '💰 Ver Saldos', 'callback_data': '/saldo'}, {'text': '📝 Últimos', 'callback_data': '/ultimos'}], [{'text': '📊 Relatórios', 'callback_data': 'menu_relatorios'}, {'text': '⚙️ Contas e Cartões', 'callback_data': 'menu_config'}], [{'text': '❓ Ajuda', 'callback_data': '/ajuda'}]]}
def get_reports_keyboard(): return {'inline_keyboard': [[{'text': '📅 Semana', 'callback_data': '/relatorio_esta_semana'}, {'text': '📆 Mês', 'callback_data': '/relatorio_mes_atual'}], [{'text': '🔙 Voltar', 'callback_data': '/menu'}]]}
def get_config_keyboard(): return {'inline_keyboard': [[{'text': '➕ Nova Conta', 'callback_data': 'btn_new_account'}, {'text': '💳 Novo Cartão', 'callback_data': 'btn_new_card'}], [{'text': '🔙 Voltar', 'callback_data': '/menu'}]]}

def send_message(chat_id, text, reply_markup=None):
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup: payload['reply_markup'] = reply_markup
    try: requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
    except: pass

def answer_callback(cb_id):
    try: requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={'callback_query_id': cb_id})
    except: pass

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data: return "OK", 200

    if 'callback_query' in data:
        cb = data['callback_query']
        chat_id = cb['message']['chat']['id']
        raw_data = cb['data']
        answer_callback(cb['id'])

        # --- SELEÇÃO DE CONTA (Para Entradas/Pix) ---
        if raw_data.startswith('sel_acc_'):
            acc_id = int(raw_data.split('_')[2])
            last = db.get_last_transactions(chat_id, 1)
            if last:
                db.update_transaction_account(last[0]['id'], acc_id)
                send_message(chat_id, "✅ Saldo atualizado na conta selecionada!")
            return "OK", 200

        # --- SELEÇÃO DE CARTÃO ---
        elif raw_data.startswith('sel_card_'):
            card_id = int(raw_data.split('_')[2])
            last = db.get_last_transactions(chat_id, 1)
            if last:
                db.update_transaction_card(last[0]['id'], card_id)
                send_message(chat_id, "✅ Cartão vinculado!")
            return "OK", 200

        # --- SELEÇÃO DE MÉTODO ---
        elif raw_data.startswith('set_method_'):
            method = raw_data.replace('set_method_', '')
            method_db = 'credit_card' if method == 'credit' else 'debit_card' if method == 'debit' else 'pix'
            last = db.get_last_transactions(chat_id, 1)
            if last:
                db.update_transaction_method(last[0]['id'], method_db)
                
                # Se for Crédito -> Pergunta Cartão
                if method_db == 'credit_card':
                    cards = db.get_user_cards(chat_id)
                    kb = {'inline_keyboard': [[{'text': f"💳 {c['name']}", 'callback_data': f"sel_card_{c['id']}"}] for c in cards]} if cards else None
                    send_message(chat_id, "Em qual cartão?", reply_markup=kb)
                
                # Se for Débito ou Pix -> Pergunta Conta
                else:
                    accs = db.get_user_accounts(chat_id)
                    kb = {'inline_keyboard': [[{'text': f"🏦 {a['name']}", 'callback_data': f"sel_acc_{a['id']}"}] for a in accs]} if accs else None
                    send_message(chat_id, f"✅ Método: {method}. Em qual conta?", reply_markup=kb)

            return "OK", 200

        # --- FLUXOS DE CRIAÇÃO INTERATIVA ---
        elif raw_data == 'btn_new_account':
            user_states[chat_id] = 'awaiting_account_name'
            send_message(chat_id, "🏦 Qual o nome da conta? (Ex: Nubank, Carteira)")
            return "OK", 200
        elif raw_data == 'btn_new_card':
            user_states[chat_id] = 'awaiting_card_name'
            user_data_buffer[chat_id] = {}
            send_message(chat_id, "💳 Qual o nome do cartão?")
            return "OK", 200
        
        # --- NAVEGAÇÃO ---
        elif raw_data == '/menu': send_message(chat_id, "🤖 *Menu*", reply_markup=get_main_menu_keyboard())
        elif raw_data == 'menu_relatorios': send_message(chat_id, "📊 *Relatórios*", reply_markup=get_reports_keyboard())
        elif raw_data == 'menu_config': send_message(chat_id, "⚙️ *Configurações*", reply_markup=get_config_keyboard())
        elif raw_data == '/apagar_ultimo':
            last = db.get_last_transactions(chat_id, 1)
            if last:
                db.delete_transaction(last[0]['id'], chat_id)
                send_message(chat_id, "🗑️ Apagado!")
            else: send_message(chat_id, "Nada para apagar.")
        else: send_message(chat_id, commands.handle_command(raw_data, chat_id))
        return "OK", 200

    # 2. MENSAGENS E IA
    if 'message' in data:
        msg = data['message']
        chat_id = msg['chat']['id']
        text = msg.get('text', '').strip()
        image_bytes = None

        # --- FLUXO DE ESTADOS (Criação Interativa) ---
        if chat_id in user_states:
            state = user_states[chat_id]
            if text == '/cancelar':
                del user_states[chat_id]
                send_message(chat_id, "Cancelado.", reply_markup=get_main_menu_keyboard())
                return "OK", 200
            
            if state == 'awaiting_account_name':
                db.create_account(chat_id, text)
                del user_states[chat_id]
                send_message(chat_id, f"✅ Conta *{text}* criada!")
            elif state == 'awaiting_card_name':
                user_data_buffer[chat_id] = {'name': text}
                user_states[chat_id] = 'awaiting_card_closing'
                send_message(chat_id, "📅 Qual o dia do fechamento? (Só números)")
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
                    send_message(chat_id, f"✅ Cartão *{dat['name']}* criado!")
            return "OK", 200

        # --- IA PARSER (Híbrido) ---
        if 'photo' in msg:
            try:
                photo_id = msg['photo'][-1]['file_id']
                file_info = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={photo_id}").json()
                path = file_info['result']['file_path']
                image_bytes = requests.get(f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{path}").content
                text = msg.get('caption', '')
                send_message(chat_id, "🔎 Analisando imagem...")
            except: pass

        if not db.get_user(chat_id):
            db.create_user(chat_id, msg['from'].get('first_name', 'User'))

        # --- CORREÇÃO MENU ---
        if text == '/menu': 
            send_message(chat_id, "🤖 *Menu Principal*", reply_markup=get_main_menu_keyboard())
            return "OK", 200

        if text.startswith('/'):
            send_message(chat_id, commands.handle_command(text, chat_id))
            return "OK", 200

        if text or image_bytes:
            ai_data = ai_parser.get_ai_response(text, image_bytes)
            if not ai_data:
                send_message(chat_id, "Não entendi.")
                return "OK", 200

            intent = ai_data.get('intent')
            entities = ai_data.get('entities', {})

            if intent == 'register_transaction':
                inst = entities.get('installments', 1)
                success = db.create_installments(chat_id, entities, inst) if isinstance(inst, int) and inst > 1 else db.process_transaction_with_rpc(chat_id, entities)
                
                if success:
                    tip = entities.get('type')
                    val = entities.get('amount')
                    desc = entities.get('description')
                    pay = entities.get('payment_method')

                    # 1. Se for ENTRADA (Income) -> Pergunta qual conta
                    if tip == 'income':
                        accs = db.get_user_accounts(chat_id)
                        kb = {'inline_keyboard': [[{'text': f"🏦 {a['name']}", 'callback_data': f"sel_acc_{a['id']}"}] for a in accs]} if accs else None
                        send_message(chat_id, f"💰 Recebido: R${val}. Em qual conta entrou?", reply_markup=kb)

                    # 2. Se for SAÍDA Crédito -> Pergunta qual cartão
                    elif pay == 'credit_card':
                        cards = db.get_user_cards(chat_id)
                        kb = {'inline_keyboard': [[{'text': f"💳 {c['name']}", 'callback_data': f"sel_card_{c['id']}"}] for c in cards]} if cards else None
                        send_message(chat_id, f"✅ Gasto R${val}. Qual cartão?", reply_markup=kb)

                    # 3. Se for SAÍDA Pix/Débito -> Pergunta qual conta (para abater)
                    elif pay in ['debit_card', 'pix']:
                        accs = db.get_user_accounts(chat_id)
                        kb = {'inline_keyboard': [[{'text': f"🏦 {a['name']}", 'callback_data': f"sel_acc_{a['id']}"}] for a in accs]} if accs else None
                        send_message(chat_id, f"✅ Gasto R${val}. De qual conta saiu?", reply_markup=kb)

                    # 4. Se não souber método -> Pergunta
                    elif not pay:
                        kb = {'inline_keyboard': [[{'text': '💳 Crédito', 'callback_data': 'set_method_credit'}, {'text': '💸 Débito', 'callback_data': 'set_method_debit'}, {'text': 'Pix', 'callback_data': 'set_method_pix'}]]}
                        send_message(chat_id, f"✅ Li R${val}. Como foi?", reply_markup=kb)
                    else:
                        send_message(chat_id, f"✅ Registrado: {desc} (R${val})")
                else:
                    send_message(chat_id, "Erro ao gravar.")

            elif intent == 'query_report':
                total = db.get_report(chat_id, entities.get('description'), entities.get('time_period'))
                send_message(chat_id, f"📊 Total: R${total:.2f}")

    return "OK", 200

# Correção para o erro 404 nos logs do Health Check
@app.route('/health', methods=['GET', 'HEAD'])
def health(): return "OK", 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)