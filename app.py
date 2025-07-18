# Arquivo: app.py
import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

# Importa nossos módulos
import db
import commands
import ai_parser

# Carrega as variáveis de ambiente
load_dotenv()
app = Flask(__name__)

# Dicionário para guardar o estado da conversa (ex: aguardando nome)
user_state = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    """Recebe e processa as mensagens do WhatsApp."""
    incoming_msg = request.values.get('Body', '').strip()
    sender_phone = request.values.get('From', '').replace('whatsapp:', '')
    
    response = MessagingResponse()
    message = response.message()

    # Verifica se o usuário existe no banco de dados
    user = db.get_user_by_phone(sender_phone)

    if not user:
        # LÓGICA DE CADASTRO DE NOVO USUÁRIO
        if user_state.get(sender_phone) == 'awaiting_name':
            new_user = db.create_user(sender_phone, incoming_msg)
            message.body(f"Ótimo, {new_user['name']}! Seu cadastro foi concluído. Digite /menu para começar.")
            del user_state[sender_phone]
        else:
            message.body("Olá! Bem-vindo(a) ao seu gestor financeiro. Para começar, por favor, me diga seu nome.")
            user_state[sender_phone] = 'awaiting_name'
    else:
        # USUÁRIO JÁ EXISTE, PROCESSA A MENSAGEM
        if incoming_msg.lower().startswith('/'):
            # Trata como um comando
            response_text = commands.handle_command(incoming_msg.lower(), user['id'])
            message.body(response_text)
        else:
            # Trata como linguagem natural com a IA
            parsed_data = ai_parser.parse_transaction_with_ai(incoming_msg)

            if parsed_data:
                # Salva a transação no banco de dados
                db.create_transaction(user['id'], parsed_data)
                
                desc = parsed_data.get('description', 'N/A')
                amount = parsed_data.get('amount', 0)
                
                # Monta uma resposta amigável
                tipo = "Entrada" if parsed_data.get('type') == 'income' else "Gasto"
                message.body(f"✅ {tipo} de R${amount:.2f} em '{desc}' registrado com sucesso!")
            else:
                message.body("Desculpe, não consegui entender a transação. Tente novamente ou use /menu para ajuda.")

    return str(response)

if __name__ == '__main__':
    app.run(port=5000, debug=True)