# Arquivo: app.py
import os
import requests
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv

import db
import commands
import ai_parser

load_dotenv()
app = Flask(__name__)

# --- LOGGING PROFISSIONAL ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- CONFIGURAÇÕES ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_SECRET = os.environ.get("TELEGRAM_SECRET_TOKEN") # Opcional: para segurança extra
CRON_SECRET = os.environ.get("CRON_SECRET")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# --- FUNÇÕES DE ENVIO ---
def send_message(chat_id, text, reply_markup=None):
    """Envia mensagem com suporte a botões (reply_markup)."""
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    if reply_markup:
        payload['reply_markup'] = reply_markup
        
    try:
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {e}")

def answer_callback(callback_id, text=None):
    """Para a animação de 'carregando' do botão."""
    payload = {'callback_query_id': callback_id}
    if text: payload['text'] = text
    try:
        requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json=payload)
    except Exception as e:
        logger.error(f"Erro no answerCallback: {e}")

# --- MENU COM BOTÕES ---
def get_main_menu_keyboard():
    return {
        'inline_keyboard': [
            [
                {'text': '💰 Saldo', 'callback_data': '/saldo'},
                {'text': '📝 Últimos', 'callback_data': '/ultimos'}
            ],
            [
                {'text': '📊 Relatório Semanal', 'callback_data': '/relatorio_esta_semana'},
                {'text': '💡 Conselho', 'callback_data': '/conselho'}
            ],
            [
                {'text': '❓ Ajuda', 'callback_data': '/ajuda'}
            ]
        ]
    }

# --- ROTA PRINCIPAL ---
@app.route('/webhook', methods=['POST'])
def webhook():
    # Segurança (Opcional): Verifica se a requisição vem mesmo do Telegram
    # Para ativar, defina um token secreto no BotFather e no .env
    if TELEGRAM_SECRET and request.headers.get("X-Telegram-Bot-Api-Secret-Token") != TELEGRAM_SECRET:
        logger.warning("Tentativa de acesso não autorizado no Webhook.")
        # return "Unauthorized", 403 # Descomente quando configurar

    data = request.get_json()
    if not data: return "OK", 200

    # 1. TRATAMENTO DE CLIQUES EM BOTÕES (Callback Query)
    if 'callback_query' in data:
        cb = data['callback_query']
        chat_id = cb['message']['chat']['id']
        callback_id = cb['id']
        command = cb['data']
        
        # Avisa o Telegram que o clique foi recebido
        answer_callback(callback_id)
        
        # Executa o comando como se fosse texto
        logger.info(f"Botão clicado: {command} por {chat_id}")
        user = db.get_user(chat_id) # Garante que user existe
        if user:
            response = commands.handle_command(command, chat_id)
            send_message(chat_id, response)
        return "OK", 200

    # 2. TRATAMENTO DE MENSAGENS DE TEXTO
    if 'message' in data and 'text' in data['message']:
        msg = data['message']
        chat_id = msg['chat']['id']
        text = msg['text'].strip()
        sender_name = msg['from'].get('first_name', 'Usuário')

        logger.info(f"Mensagem recebida de {chat_id}: {text}")

        # Verifica Usuário
        user = db.get_user(chat_id)
        
        # FLUXO DE CADASTRO SEM ESTADO (STATELESS)
        if not user:
            if text.startswith("/"):
                send_message(chat_id, f"Olá {sender_name}! Para começar, apenas me diga: como quer ser chamado?")
            else:
                # Assume que qualquer texto que não seja comando é o nome
                db.create_user(chat_id, text)
                send_message(chat_id, f"Prazer, {text}! Tudo configurado.", reply_markup=get_main_menu_keyboard())
            return "OK", 200

        # FLUXO NORMAL
        if text == '/menu':
            send_message(chat_id, "🤖 *Menu Principal*\nEscolha uma opção:", reply_markup=get_main_menu_keyboard())
        elif text.startswith('/'):
            # Comandos manuais
            response = commands.handle_command(text, chat_id)
            send_message(chat_id, response)
        else:
            # IA Gemini
            ai_data = ai_parser.get_ai_response(text)
            
            if not ai_data:
                send_message(chat_id, "Desculpe, não entendi. Tente usar o /menu.")
                return "OK", 200

            intent = ai_data.get('intent')
            entities = ai_data.get('entities', {})

            if intent == 'register_transaction':
                success = db.process_transaction_with_rpc(chat_id, entities)
                if success:
                    cat = entities.get('category') or 'Geral'
                    val = entities.get('amount')
                    # Botão de Desfazer (Dica Pro!)
                    keyboard = {'inline_keyboard': [[{'text': '🗑️ Desfazer', 'callback_data': '/apagar_ultimo'}]]}
                    send_message(chat_id, f"✅ *Gasto Registrado!*\n📂 {cat}\n💰 R${val}", reply_markup=keyboard)
                else:
                    send_message(chat_id, "Erro ao registrar.")

            elif intent == 'query_report':
                total = db.get_report(chat_id, entities.get('description'), entities.get('time_period'))
                send_message(chat_id, f"📊 O total encontrado foi: R${total:.2f}")

    return "OK", 200

@app.route('/health', methods=['GET'])
def health():
    return "Alive", 200

# Rotas de Cron mantidas...
if __name__ == '__main__':
    app.run(port=5000, debug=True)