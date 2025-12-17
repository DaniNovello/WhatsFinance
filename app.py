# Arquivo: app.py
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

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Variáveis de Ambiente
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
# TELEGRAM_SECRET = os.environ.get("TELEGRAM_SECRET_TOKEN") # Configure se desejar

# --- GERENCIADORES DE TECLADO (INTERFACE) ---

def get_main_menu_keyboard():
    """Menu Principal"""
    return {
        'inline_keyboard': [
            [
                {'text': '💰 Ver Saldos', 'callback_data': '/saldo'},
                {'text': '📝 Últimos Lançamentos', 'callback_data': '/ultimos'}
            ],
            [
                {'text': '📊 Relatórios', 'callback_data': 'menu_relatorios'},
                {'text': '⚙️ Contas e Cartões', 'callback_data': 'menu_config'}
            ],
            [
                {'text': '❓ Ajuda', 'callback_data': '/ajuda'},
                {'text': '💡 Conselho', 'callback_data': '/conselho'}
            ]
        ]
    }

def get_reports_keyboard():
    """Sub-menu de Relatórios"""
    return {
        'inline_keyboard': [
            [
                {'text': '📅 Esta Semana', 'callback_data': '/relatorio_esta_semana'},
                {'text': '⏮️ Semana Passada', 'callback_data': '/relatorio_semana_passada'}
            ],
            [
                {'text': '📆 Este Mês', 'callback_data': '/relatorio_mes_atual'},
                {'text': '🔙 Voltar', 'callback_data': '/menu'}
            ]
        ]
    }

def get_config_keyboard():
    """Sub-menu de Configurações"""
    return {
        'inline_keyboard': [
            [
                {'text': '➕ Nova Conta', 'callback_data': 'instrucao_conta'},
                {'text': '💳 Novo Cartão', 'callback_data': 'instrucao_cartao'}
            ],
            [
                {'text': '🔙 Voltar', 'callback_data': '/menu'}
            ]
        ]
    }

# --- FUNÇÕES AUXILIARES ---

def send_message(chat_id, text, reply_markup=None):
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup: payload['reply_markup'] = reply_markup
    try:
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
    except Exception as e:
        logger.error(f"Erro no envio: {e}")

def answer_callback(callback_id):
    try:
        requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={'callback_query_id': callback_id})
    except:
        pass

# --- ROTA WEBHOOK ---

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data: return "OK", 200

    # 1. TRATAMENTO DE CLIQUES EM BOTÕES
    if 'callback_query' in data:
        cb = data['callback_query']
        chat_id = cb['message']['chat']['id']
        callback_id = cb['id']
        raw_data = cb['data'] # O comando do botão
        
        answer_callback(callback_id)
        
        # --- Navegação de Menus ---
        if raw_data == '/menu':
            send_message(chat_id, "🤖 *Menu Principal*", reply_markup=get_main_menu_keyboard())
            
        elif raw_data == 'menu_relatorios':
            send_message(chat_id, "📊 *Selecione o período do relatório:*", reply_markup=get_reports_keyboard())
            
        elif raw_data == 'menu_config':
            send_message(chat_id, "⚙️ *Gestão de Contas e Cartões*", reply_markup=get_config_keyboard())
            
        elif raw_data == 'instrucao_conta':
            send_message(chat_id, "Para criar uma conta, digite:\n`/cadastrar_conta NomeDoBanco`\n\nEx: _/cadastrar_conta NuBank_")
            
        elif raw_data == 'instrucao_cartao':
            send_message(chat_id, "Para adicionar um cartão, digite:\n`/cadastrar_cartao NomeDoCartao`\n\nEx: _/cadastrar_cartao Visa XP_")

        elif raw_data == '/apagar_ultimo':
            # Atalho inteligente para apagar o último registro
            last = db.get_last_transactions(chat_id, limit=1)
            if last:
                db.delete_transaction(last[0]['id'], chat_id)
                send_message(chat_id, "🗑️ Último registro apagado com sucesso!")
            else:
                send_message(chat_id, "Não encontrei nada para apagar.")

        # --- Comandos Padrão (Saldos, Relatórios Específicos, Ajuda) ---
        else:
            response = commands.handle_command(raw_data, chat_id)
            # Se a resposta for o menu de ajuda, anexa o teclado principal
            keyboard = get_main_menu_keyboard() if raw_data == '/ajuda' else None
            send_message(chat_id, response, reply_markup=keyboard)
            
        return "OK", 200

    # 2. TRATAMENTO DE MENSAGENS DE TEXTO
    if 'message' in data:
        msg = data['message']
        chat_id = msg['chat']['id']
        text = msg.get('text', '').strip()
        sender_name = msg['from'].get('first_name', 'Usuário')

        # Cadastro Inicial (Sem estado complexo)
        user = db.get_user(chat_id)
        if not user:
            if text.startswith('/'):
                 send_message(chat_id, f"Olá {sender_name}! Bem-vindo. Para começar, diga-me como quer ser chamado.")
            else:
                db.create_user(chat_id, text)
                send_message(chat_id, f"Prazer, {text}! Use o menu abaixo para começar:", reply_markup=get_main_menu_keyboard())
            return "OK", 200

        # Comandos de Texto Direto (/menu, etc)
        if text == '/menu':
             send_message(chat_id, "🤖 *Menu Principal*", reply_markup=get_main_menu_keyboard())
             return "OK", 200

        if text.startswith('/'):
            response = commands.handle_command(text, chat_id)
            send_message(chat_id, response)
            return "OK", 200

        # Se não for comando, manda para a IA
        ai_data = ai_parser.get_ai_response(text)
        
        if not ai_data:
            send_message(chat_id, "🤔 Não entendi. Tente reformular ou use o /menu.")
            return "OK", 200

        intent = ai_data.get('intent')
        entities = ai_data.get('entities', {})

        if intent == 'register_transaction':
            success = db.process_transaction_with_rpc(chat_id, entities)
            if success:
                desc = entities.get('description', 'Gasto')
                val = entities.get('amount', 0)
                # Botão "Desfazer" aparece logo após registrar
                undo_kb = {'inline_keyboard': [[{'text': '🗑️ Desfazer (Apagar)', 'callback_data': '/apagar_ultimo'}]]}
                send_message(chat_id, f"✅ Registrado: *{desc}* (R${val})\nCategoria: {entities.get('category')}", reply_markup=undo_kb)
            else:
                send_message(chat_id, "Erro ao gravar no banco.")

        elif intent == 'query_report':
            # Se a IA identificar pedido de relatório, já formata bonito
            # (Poderíamos mapear para as funções de comando também)
            total = db.get_report(chat_id, entities.get('description'), entities.get('time_period'))
            send_message(chat_id, f"📊 Total encontrado: R${total:.2f}")

    return "OK", 200

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)