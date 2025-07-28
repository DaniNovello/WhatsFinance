import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client # <-- Client para enviar mensagens agendadas
from dotenv import load_dotenv

import db
import commands
import ai_parser

load_dotenv()
app = Flask(__name__)

# --- CONFIGURAÇÃO DE SEGURANÇA PARA O AGENDADOR ---
# Esta "senha" será usada para proteger suas rotas de relatório.
CRON_SECRET = os.environ.get("CRON_SECRET")

@app.route('/health', methods=['GET'])
def health_check():
    return "OK", 200

user_state = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '').strip()
    sender_phone = request.values.get('From', '').replace('whatsapp:', '')
    
    response = MessagingResponse()
    message = response.message()

    try:
        user = db.get_user_by_phone(sender_phone)
        if not user:
            # Lógica de cadastro (sem alteração)
            if user_state.get(sender_phone) == 'awaiting_name':
                new_user = db.create_user(sender_phone, incoming_msg)
                message.body(f"Ótimo, {new_user['name']}! Cadastro concluído. Digite /menu.")
                del user_state[sender_phone]
            else:
                message.body("Olá! Para começar, me diga seu nome.")
                user_state[sender_phone] = 'awaiting_name'
        else:
            # Lógica de processamento de mensagens (sem alteração)
            if incoming_msg.startswith('/'):
                response_text = commands.handle_command(incoming_msg, user['id'])
                message.body(response_text)
            else:
                ai_data = ai_parser.get_ai_response(incoming_msg)
                
                if not ai_data:
                    message.body("😕 Desculpe, não consegui processar sua solicitação.")
                
                elif ai_data.get('intent') == 'register_transaction':
                    entities = ai_data.get('entities', {})
                    success = db.process_transaction_with_rpc(user['id'], entities)
                    if success:
                        desc = entities.get('description', 'N/A')
                        amount = float(entities.get('amount', 0))
                        tipo = "Entrada" if entities.get('type') == 'income' else "Gasto"
                        message.body(f"✅ {tipo} de R${amount:.2f} em '{desc}' registrado!")
                    else:
                        message.body("❌ Erro ao registrar. Você já cadastrou uma conta com `/cadastrar_conta`?")

                elif ai_data.get('intent') == 'query_report':
                    entities = ai_data.get('entities', {})
                    total = db.get_report(user['id'], entities.get('description'), entities.get('time_period'))
                    period_text = {"last_week": "na última semana", "last_month": "no último mês", "today": "hoje", "yesterday": "ontem", "this_week": "esta semana", "this_month": "este mês"}
                    if entities.get('description'):
                        message.body(f"Você gastou R${total:.2f} com '{entities.get('description')}' {period_text.get(entities.get('time_period'), '')}.")
                    else:
                        message.body(f"Seu gasto total {period_text.get(entities.get('time_period'), '')} foi de R${total:.2f}.")
                else:
                    message.body("Não entendi. Para relatórios e outras ações, por favor, use os comandos do /menu.")

    except Exception as e:
        print(f"!!!!!!!! ERRO INESPERADO: {e} !!!!!!!!")
        message.body("🤖 Ops! Encontrei um erro interno.")
    return str(response)

# --- NOVAS ROTAS PARA O AGENDADOR EXTERNO ---

def send_proactive_message(user_phone_number, message_body):
    """Função central para enviar mensagens proativas (iniciadas pelo bot)."""
    try:
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        twilio_phone = os.environ.get("TWILIO_PHONE_NUMBER")
        client = Client(account_sid, auth_token)

        client.messages.create(
            from_=f'whatsapp:{twilio_phone}',
            body=message_body,
            to=f'whatsapp:{user_phone_number}'
        )
        print(f"Mensagem agendada enviada com sucesso para {user_phone_number}")
        return True
    except Exception as e:
        print(f"!!!!!!!! ERRO AO ENVIAR MENSAGEM PROATIVA: {e} !!!!!!!!")
        return False

@app.route('/trigger/weekly-report/<secret>', methods=['POST'])
def trigger_weekly_report(secret):
    """Quando visitado pelo Cron-Job, envia o relatório semanal para TODOS os usuários."""
    if secret != CRON_SECRET:
        return "Acesso negado.", 403

    all_users = db.get_all_users()
    print(f"Disparando relatório semanal para {len(all_users)} usuários.")

    for user in all_users:
        report_content = commands.handle_command("/relatorio_semana_passada", user['id'])
        send_proactive_message(user['phone_number'], report_content)
        
    return f"Relatório semanal enviado para {len(all_users)} usuários.", 200

@app.route('/trigger/monthly-report/<secret>', methods=['POST'])
def trigger_monthly_report(secret):
    """Quando visitado pelo Cron-Job, envia o relatório mensal para TODOS os usuários."""
    if secret != CRON_SECRET:
        return "Acesso negado.", 403
        
    all_users = db.get_all_users()
    print(f"Disparando relatório mensal para {len(all_users)} usuários.")

    for user in all_users:
        report_content = commands.handle_command("/relatorio_mes_passado", user['id'])
        send_proactive_message(user['phone_number'], report_content)

    return f"Relatório mensal enviado para {len(all_users)} usuários.", 200
# --- NOVA ROTA PARA CONSELHOS ---
@app.route('/trigger/financial-advice/<secret>', methods=['POST'])
def trigger_financial_advice(secret):
    if secret != CRON_SECRET: return "Acesso negado.", 403
    all_users = db.get_all_users()
    advice = ai_parser.get_financial_advice() # Gera um conselho único para todos
    for user in all_users:
        send_proactive_message(user['phone_number'], advice)
    return f"Conselho financeiro enviado para {len(all_users)} usuários.", 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)