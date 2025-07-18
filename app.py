# Arquivo: app.py
import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import db # Importa nosso novo arquivo db.py

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
        # Usuário não existe. Vamos criá-lo.
        if user_state.get(sender_phone) == 'awaiting_name':
            # Usuário respondeu com o nome
            new_user = db.create_user(sender_phone, incoming_msg)
            message.body(f"Ótimo, {new_user['name']}! Seu cadastro foi concluído. Digite /menu para começar.")
            del user_state[sender_phone] # Limpa o estado
        else:
            # Primeiro contato do usuário
            message.body("Olá! Bem-vindo(a) ao seu gestor financeiro. Para começar, por favor, me diga seu nome.")
            user_state[sender_phone] = 'awaiting_name' # Define o estado
    else:
        # Usuário já existe, processa a mensagem normalmente
        if incoming_msg.lower().startswith('/'):
            # Lógica para tratar comandos (será implementada)
            message.body(f"Olá, {user['name']}! Comando '{incoming_msg}' recebido.")
        else:
            # Lógica para usar a IA (será implementada)
            message.body("Vou processar sua transação com a IA em breve!")

    return str(response)

if __name__ == '__main__':
    app.run(port=5000, debug=True)