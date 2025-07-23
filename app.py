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
            # Lógica de cadastro
            if user_state.get(sender_phone) == 'awaiting_name':
                new_user = db.create_user(sender_phone, incoming_msg)
                message.body(f"Ótimo, {new_user['name']}! Cadastro concluído. Digite /menu.")
                del user_state[sender_phone]
            else:
                message.body("Olá! Para começar, me diga seu nome.")
                user_state[sender_phone] = 'awaiting_name'

        # Lógica de conversa para pedir descrição
        elif user_state.get(sender_phone) and user_state[sender_phone].get('state') == 'awaiting_description':
            partial_transaction = user_state[sender_phone]['data']
            partial_transaction['description'] = incoming_msg
            
            success = db.process_transaction_with_rpc(user['id'], partial_transaction)
            if success:
                amount = float(partial_transaction.get('amount', 0))
                tipo = "Entrada" if partial_transaction.get('type') == 'income' else "Gasto"
                message.body(f"✅ {tipo} de R${amount:.2f} em '{incoming_msg}' registrado!")
            else:
                message.body("❌ Erro ao salvar a transação completa.")
            del user_state[sender_phone]

        else:
            # Fluxo normal
            if incoming_msg.lower().startswith('/'):
                response_text = commands.handle_command(incoming_msg.lower(), user['id'])
                message.body(response_text)
            else:
                ai_data = ai_parser.get_ai_response(incoming_msg)

                if not ai_data:
                    message.body("😕 Desculpe, não consegui processar sua solicitação.")
                elif ai_data.get('intent') == 'register_transaction':
                    entities = ai_data.get('entities', {})
                    if entities.get('description'):
                        # Se a descrição já veio, registra direto
                        success = db.process_transaction_with_rpc(user['id'], entities)
                        if success:
                            desc = entities.get('description', 'N/A')
                            amount = float(entities.get('amount', 0))
                            tipo = "Entrada" if entities.get('type') == 'income' else "Gasto"
                            message.body(f"✅ {tipo} de R${amount:.2f} em '{desc}' registrado!")
                        else:
                            message.body("Ops! Para registrar, você precisa ter uma conta.")
                    else:
                        # Se falta a descrição, inicia a conversa
                        user_state[sender_phone] = {'state': 'awaiting_description', 'data': entities}
                        amount = float(entities.get('amount', 0))
                        tipo = "Entrada" if entities.get('type') == 'income' else "Gasto"
                        message.body(f"{tipo} de R${amount:.2f} registrada. Com o que foi?")
                
                elif ai_data.get('intent') == 'query_report':
                    # Lógica de relatórios por texto
                    entities = ai_data.get('entities', {})
                    description = entities.get('description')
                    time_period = entities.get('time_period')
                    if not time_period:
                        message.body("Para relatórios, por favor, me diga o período. Ex: 'gastos de hoje'")
                    else:
                        total = db.get_report(user['id'], description, time_period)
                        period_text = {"last_week": "na última semana", "last_month": "no último mês", "today": "hoje", "yesterday": "ontem", "this_week": "esta semana", "this_month": "este mês"}
                        if description:
                            message.body(f"Você gastou R${total:.2f} com '{description}' {period_text.get(time_period, '')}.")
                        else:
                            message.body(f"Seu gasto total {period_text.get(time_period, '')} foi de R${total:.2f}.")

    except Exception as e:
        print(f"!!!!!!!! ERRO INESPERADO: {e} !!!!!!!!")
        message.body("🤖 Ops! Encontrei um erro interno. Tente novamente em um instante.")

    return str(response)

if __name__ == '__main__':
    app.run(port=5000, debug=True)