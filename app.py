# Arquivo: app.py
import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

import db
import commands
import ai_parser

load_dotenv()
app = Flask(__name__)

# --- CONFIGURAÇÕES ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CRON_SECRET = os.environ.get("CRON_SECRET")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

def send_telegram_message(chat_id, text):
    """Envia mensagem para o Telegram usando a API oficial."""
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown' # Permite usar negrito com *texto*
    }
    try:
        requests.post(TELEGRAM_API_URL, json=payload)
    except Exception as e:
        print(f"Erro ao enviar mensagem Telegram: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    return "OK", 200

# Estado em memória simples para fluxo de cadastro (pode reiniciar com o servidor)
user_state = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    
    # Verifica se é uma mensagem válida de texto
    if not data or 'message' not in data:
        return "Ignored", 200

    message = data['message']
    chat_id = message.get('chat', {}).get('id')
    incoming_msg = message.get('text', '').strip()
    sender_name = message.get('from', {}).get('first_name', 'Usuário')

    if not chat_id or not incoming_msg:
        return "Ignored", 200

    try:
        # Busca usuário pelo ID do Telegram
        user = db.get_user(chat_id)

        if not user:
            # --- Fluxo de Cadastro ---
            if user_state.get(chat_id) == 'awaiting_name':
                # O usuário enviou o nome
                db.create_user(chat_id, incoming_msg)
                send_telegram_message(chat_id, f"Ótimo, {incoming_msg}! Cadastro concluído. Digite /menu para ver o que posso fazer.")
                del user_state[chat_id]
            else:
                # Primeiro contato
                send_telegram_message(chat_id, f"Olá, {sender_name}! Bem-vindo ao WhatsFinance (versão Telegram). Para começar, como você gostaria de ser chamado?")
                user_state[chat_id] = 'awaiting_name'
        else:
            # --- Fluxo Normal ---
            if incoming_msg.startswith('/'):
                response_text = commands.handle_command(incoming_msg, user['id'])
                send_telegram_message(chat_id, response_text)
            else:
                # Processamento IA
                ai_data = ai_parser.get_ai_response(incoming_msg)
                
                if not ai_data:
                    send_telegram_message(chat_id, "😕 Desculpe, não consegui entender. Tente reformular ou use /menu.")
                
                elif ai_data.get('intent') == 'register_transaction':
                    entities = ai_data.get('entities', {})
                    # Passa o user['id'] que é o ID do Telegram
                    success = db.process_transaction_with_rpc(user['id'], entities)
                    
                    if success:
                        desc = entities.get('description', 'N/A')
                        amount = float(entities.get('amount', 0))
                        tipo = "Entrada" if entities.get('type') == 'income' else "Gasto"
                        send_telegram_message(chat_id, f"✅ *{tipo}* registrado!\n📝 {desc}\n💰 R${amount:.2f}")
                    else:
                        send_telegram_message(chat_id, "❌ Erro ao registrar. Você já criou uma conta com `/cadastrar_conta`?")

                elif ai_data.get('intent') == 'query_report':
                    entities = ai_data.get('entities', {})
                    total = db.get_report(user['id'], entities.get('description'), entities.get('time_period'))
                    period_text = {"last_week": "na última semana", "last_month": "no último mês", "today": "hoje", "yesterday": "ontem", "this_week": "esta semana", "this_month": "este mês"}
                    
                    p_text = period_text.get(entities.get('time_period'), '')
                    if entities.get('description'):
                        send_telegram_message(chat_id, f"📊 Gastos com *{entities.get('description')}* {p_text}: R${total:.2f}")
                    else:
                        send_telegram_message(chat_id, f"📊 Gasto total {p_text}: R${total:.2f}")
                else:
                    send_telegram_message(chat_id, "Não entendi bem. Tente escrever algo como 'gastei 50 no mercado' ou digite /menu.")

    except Exception as e:
        print(f"!!!!!!!! ERRO NO WEBHOOK: {e} !!!!!!!!")
        send_telegram_message(chat_id, "🤖 Ops! Tive um erro interno.")

    return "OK", 200

# --- ROTAS DE CRON JOBS (Mantidas, mas enviando via Telegram) ---

@app.route('/trigger/weekly-report/<secret>', methods=['POST'])
def trigger_weekly_report(secret):
    if secret != CRON_SECRET: return "Acesso negado.", 403
    all_users = db.get_all_users()
    for user in all_users:
        # user['id'] agora é o chat_id do Telegram
        report_content = commands.handle_command("/relatorio_semana_passada", user['id'])
        send_telegram_message(user['id'], report_content)
    return f"Enviado para {len(all_users)} usuários.", 200

@app.route('/trigger/monthly-report/<secret>', methods=['POST'])
def trigger_monthly_report(secret):
    if secret != CRON_SECRET: return "Acesso negado.", 403
    all_users = db.get_all_users()
    for user in all_users:
        report_content = commands.handle_command("/relatorio_mes_passado", user['id'])
        send_telegram_message(user['id'], report_content)
    return f"Enviado para {len(all_users)} usuários.", 200

@app.route('/trigger/financial-advice/<secret>', methods=['POST'])
def trigger_financial_advice(secret):
    if secret != CRON_SECRET: return "Acesso negado.", 403
    all_users = db.get_all_users()
    advice = ai_parser.get_financial_advice()
    for user in all_users:
        send_telegram_message(user['id'], advice)
    return f"Conselho enviado para {len(all_users)} usuários.", 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)