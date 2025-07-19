# Arquivo: app.py
import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

import db
import commands
import ai_parser

load_dotenv()
app = Flask(__name__)

user_state = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '').strip()
    sender_phone = request.values.get('From', '').replace('whatsapp:', '')
    
    response = MessagingResponse()
    message = response.message()

    try:
        # --- LÓGICA PRINCIPAL DO BOT ---
        user = db.get_user_by_phone(sender_phone)

        if not user:
            # Lógica de cadastro de novo usuário
            if user_state.get(sender_phone) == 'awaiting_name':
                new_user = db.create_user(sender_phone, incoming_msg)
                message.body(f"Ótimo, {new_user['name']}! Seu cadastro foi concluído. Digite /menu para começar.")
                del user_state[sender_phone]
            else:
                message.body("Olá! Bem-vindo(a) ao seu gestor financeiro. Para começar, por favor, me diga seu nome.")
                user_state[sender_phone] = 'awaiting_name'
        else:
            # Usuário já existe, processa a mensagem
            if incoming_msg.lower().startswith('/'):
                response_text = commands.handle_command(incoming_msg.lower(), user['id'])
                message.body(response_text)
            else:
                ai_data = ai_parser.get_ai_response(incoming_msg)

                if not ai_data:
                    message.body("😕 Desculpe, não consegui processar sua solicitação.")
                else:
                    intent = ai_data.get('intent')
                    entities = ai_data.get('entities', {})

                    if intent == 'register_transaction':
                        success = db.process_transaction_with_rpc(user['id'], entities)
                        if success:
                            desc = entities.get('description', 'N/A')
                            amount = float(entities.get('amount', 0))
                            tipo = "Entrada" if entities.get('type') == 'income' else "Gasto"
                            message.body(f"✅ {tipo} de R${amount:.2f} em '{desc}' registrado!")
                        else:
                            message.body("Ops! Para registrar, você precisa ter uma conta. Use `/cadastrar_conta [nome]`.")
                    
                    elif intent == 'query_report':
                        description = entities.get('description')
                        time_period = entities.get('time_period')
                        
                        if not description or not time_period:
                            message.body("Para relatórios, diga o que e quando. Ex: 'gastos com uber semana passada'")
                        else:
                            total = db.get_report(user['id'], description, time_period)
                            period_text = {"last_week": "na última semana", "last_month": "no último mês", "today": "hoje"}
                            message.body(f"Você gastou R${total:.2f} com '{description}' {period_text.get(time_period, '')}.")
                    
                    else:
                        message.body("Não entendi. Você quer registrar um gasto ou fazer uma pergunta?")

    except Exception as e:
        # --- CAPTURA DE ERRO GERAL ---
        # Se qualquer coisa der errado, o bot não vai mais travar.
        print(f"!!!!!!!! ERRO INESPERADO: {e} !!!!!!!!")
        message.body("🤖 Ops! Encontrei um erro interno. Minha equipe de engenheiros (uma pessoa só) já foi notificada. Tente novamente em um instante.")

    return str(response)

if __name__ == '__main__':
    app.run(port=5000, debug=True)