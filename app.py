# Arquivo: app.py
import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Recebe as mensagens do WhatsApp via Twilio."""
    incoming_msg = request.values.get('Body', '').strip()
    sender_phone = request.values.get('From', '').replace('whatsapp:', '') # Limpa o número

    print(f"Mensagem de {sender_phone}: {incoming_msg}")

    # Lógica para responder (por enquanto, um simples eco)
    response = MessagingResponse()
    response.message(f"Você disse: {incoming_msg}")

    return str(response)

if __name__ == '__main__':
    app.run(port=5000, debug=True)