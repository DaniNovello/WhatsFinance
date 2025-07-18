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
            response_text = commands.handle_command(incoming_msg.lower(), user['id'])
            message.body(response_text)
        else:
            parsed_data = ai_parser.parse_transaction_with_ai(incoming_msg)

            if parsed_data and 'amount' in parsed_data and 'type' in parsed_data:
                # Chama a nova função otimizada do db.py
                success = db.process_transaction_with_rpc(user['id'], parsed_data)
                
                if success:
                    desc = parsed_data.get('description', 'N/A')
                    amount = float(parsed_data.get('amount', 0))
                    tipo = "Entrada" if parsed_data.get('type') == 'income' else "Gasto"
                    message.body(f"✅ {tipo} de R${amount:.2f} em '{desc}' registrado!")
                else:
                    message.body("❌ Erro ao registrar. Verifique se você já cadastrou uma conta com /cadastrar_conta.")
            else:
                message.body("😕 Desculpe, não consegui entender. Tente de novo (ex: 'gastei 20 na padaria').")

    return str(response)

if __name__ == '__main__':
    app.run(port=5000, debug=True)