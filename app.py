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

# Configuração de Logs mais detalhada
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# --- MENUS ---
def get_main_menu_keyboard():
    return {'inline_keyboard': [[{'text': '💰 Ver Saldos', 'callback_data': '/saldo'}, {'text': '📝 Últimos', 'callback_data': '/ultimos'}], [{'text': '📊 Relatórios', 'callback_data': 'menu_relatorios'}, {'text': '⚙️ Contas e Cartões', 'callback_data': 'menu_config'}], [{'text': '❓ Ajuda', 'callback_data': '/ajuda'}]]}

def get_reports_keyboard():
    return {'inline_keyboard': [[{'text': '📅 Esta Semana', 'callback_data': '/relatorio_esta_semana'}, {'text': '📆 Este Mês', 'callback_data': '/relatorio_mes_atual'}], [{'text': '🔙 Voltar', 'callback_data': '/menu'}]]}

def get_config_keyboard():
    return {'inline_keyboard': [[{'text': '➕ Nova Conta', 'callback_data': 'instrucao_conta'}, {'text': '💳 Novo Cartão', 'callback_data': 'instrucao_cartao'}], [{'text': '🔙 Voltar', 'callback_data': '/menu'}]]}

# --- AUXILIARES ---
def send_message(chat_id, text, reply_markup=None):
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup: payload['reply_markup'] = reply_markup
    try: 
        response = requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
        if response.status_code != 200:
            logger.error(f"Erro Telegram API: {response.text}")
    except Exception as e: 
        logger.error(f"Erro envio requests: {e}")

def answer_callback(callback_id):
    try: requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={'callback_query_id': callback_id})
    except: pass

# --- WEBHOOK ---
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data: return "OK", 200

    # 1. TRATA BOTÕES (CALLBACKS)
    if 'callback_query' in data:
        cb = data['callback_query']
        chat_id = cb['message']['chat']['id']
        raw_data = cb['data']
        answer_callback(cb['id'])

        logger.info(f"🔘 BOTÃO CLICADO: {raw_data} por User {chat_id}")

        # Lógica de Seleção de Cartão
        if raw_data.startswith('sel_card_'):
            logger.info("--> Entrou no fluxo sel_card")
            try:
                card_id = int(raw_data.split('_')[2])
                last = db.get_last_transactions(chat_id, 1)
                if last:
                    db.update_transaction_card(last[0]['id'], card_id)
                    send_message(chat_id, "✅ Cartão vinculado com sucesso!")
                else:
                    send_message(chat_id, "⚠️ Nenhuma transação recente para vincular.")
            except Exception as e:
                logger.error(f"Erro ao selecionar cartão: {e}")
            return "OK", 200

        # Lógica de Dúvida (Crédito ou Débito?)
        elif raw_data.startswith('set_method_'):
            logger.info("--> Entrou no fluxo set_method")
            method = raw_data.replace('set_method_', '')
            method_db = 'credit_card' if method == 'credit' else 'debit_card' if method == 'debit' else 'pix'
            
            last = db.get_last_transactions(chat_id, 1)
            if last:
                db.update_transaction_method(last[0]['id'], method_db)
                if method_db == 'credit_card':
                    cards = db.get_user_cards(chat_id)
                    kb = {'inline_keyboard': [[{'text': f"💳 {c['name']}", 'callback_data': f"sel_card_{c['id']}"}] for c in cards]} if cards else None
                    send_message(chat_id, "Em qual cartão?", reply_markup=kb)
                else:
                    send_message(chat_id, f"✅ Atualizado para {method}!")
            return "OK", 200

        # Menus
        elif raw_data == '/menu': 
            logger.info("--> Renderizando Menu Principal")
            send_message(chat_id, "🤖 *Menu Principal*", reply_markup=get_main_menu_keyboard())

        elif raw_data == 'menu_relatorios': 
            logger.info("--> Renderizando Menu Relatórios")
            send_message(chat_id, "📊 *Relatórios*", reply_markup=get_reports_keyboard())

        elif raw_data == 'menu_config': 
            logger.info("--> Renderizando Menu Configurações")
            send_message(chat_id, "⚙️ *Configurações*", reply_markup=get_config_keyboard())

        # --- BOTÕES DE INSTRUÇÃO ---
        elif raw_data == 'instrucao_conta': 
            logger.info("--> Clicou Nova Conta. Enviando instrução.")
            send_message(chat_id, "Para criar uma conta, digite:\n`/cadastrar_conta Nubank`")
        
        elif raw_data == 'instrucao_cartao': 
            logger.info("--> Clicou Novo Cartão. Enviando instrução.")
            # CORRIGIDO: Removido itálico (_) e usado código (`) para evitar erro de parse
            send_message(chat_id, "Para cadastrar cartão use:\n`/cadastrar_cartao Nome DiaFecha DiaVence`\n\nEx: `/cadastrar_cartao Nubank 04 11`")

        elif raw_data == '/apagar_ultimo':
            logger.info("--> Apagando último")
            last = db.get_last_transactions(chat_id, 1)
            if last:
                db.delete_transaction(last[0]['id'], chat_id)
                send_message(chat_id, "🗑️ Apagado!")
            else:
                send_message(chat_id, "Nada para apagar.")
        
        else:
            logger.info(f"--> Comando Genérico: {raw_data}")
            resp = commands.handle_command(raw_data, chat_id)
            send_message(chat_id, resp)
        return "OK", 200

    # 2. TRATA MENSAGENS (TEXTO OU FOTO)
    if 'message' in data:
        msg = data['message']
        chat_id = msg['chat']['id']
        text = msg.get('text', '').strip()
        sender_name = msg['from'].get('first_name', 'User')
        image_bytes = None

        logger.info(f"📩 MENSAGEM RECEBIDA de {chat_id}: {text[:20]}...")

        # Baixar Imagem (Se houver)
        if 'photo' in msg:
            logger.info("📸 Foto detectada")
            try:
                photo_id = msg['photo'][-1]['file_id']
                f_info = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={photo_id}").json()
                path = f_info['result']['file_path']
                image_bytes = requests.get(f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{path}").content
                text = msg.get('caption', '') 
                send_message(chat_id, "🔎 Analisando imagem...")
            except Exception as e:
                logger.error(f"Erro imagem: {e}")

        # Cadastro Rápido
        if not db.get_user(chat_id):
            if text.startswith('/'): send_message(chat_id, f"Olá {sender_name}! Qual seu nome?")
            else:
                db.create_user(chat_id, text)
                send_message(chat_id, f"Oi {text}!", reply_markup=get_main_menu_keyboard())
            return "OK", 200

        # Comandos Diretos
        if text == '/menu': send_message(chat_id, "Menu:", reply_markup=get_main_menu_keyboard()); return "OK", 200
        if text.startswith('/'): 
            logger.info(f"Executando comando manual: {text}")
            send_message(chat_id, commands.handle_command(text, chat_id)); 
            return "OK", 200

        # IA Parser
        logger.info("🧠 Enviando para IA...")
        ai_data = ai_parser.get_ai_response(text, image_bytes)
        
        if not ai_data:
            logger.warning("⚠️ IA retornou None")
            send_message(chat_id, "Não entendi.")
            return "OK", 200

        logger.info(f"🧠 Retorno IA: {ai_data}")
        
        intent = ai_data.get('intent')
        entities = ai_data.get('entities', {})

        if intent == 'register_transaction':
            # Verifica Parcelamento
            inst = entities.get('installments', 1)
            if isinstance(inst, int) and inst > 1:
                success = db.create_installments(chat_id, entities, inst)
                msg_extra = f" (Em {inst}x)"
            else:
                success = db.process_transaction_with_rpc(chat_id, entities)
                msg_extra = ""

            if success:
                method = entities.get('payment_method')
                val = entities.get('amount')
                desc = entities.get('description')
                
                # Se for Crédito -> Pergunta Cartão
                if method == 'credit_card':
                    cards = db.get_user_cards(chat_id)
                    kb = {'inline_keyboard': [[{'text': f"💳 {c['name']}", 'callback_data': f"sel_card_{c['id']}"}] for c in cards]} if cards else None
                    send_message(chat_id, f"✅ Registrado R${val}{msg_extra}. Qual cartão?", reply_markup=kb)
                
                # Se não souber o método -> Pergunta
                elif not method:
                    kb = {'inline_keyboard': [[{'text': '💳 Crédito', 'callback_data': 'set_method_credit'}, {'text': '💸 Débito', 'callback_data': 'set_method_debit'}, {'text': 'Pix', 'callback_data': 'set_method_pix'}]]}
                    send_message(chat_id, f"✅ Li R${val} em {desc}. Como pagou?", reply_markup=kb)
                
                else:
                    undo = {'inline_keyboard': [[{'text': '🗑️ Desfazer', 'callback_data': '/apagar_ultimo'}]]}
                    send_message(chat_id, f"✅ Salvo: {desc} (R${val}){msg_extra}", reply_markup=undo)
            else:
                logger.error("Erro ao salvar no banco")
                send_message(chat_id, "Erro ao salvar.")

        elif intent == 'query_report':
            total = db.get_report(chat_id, entities.get('description'), entities.get('time_period'))
            send_message(chat_id, f"📊 Total: R${total:.2f}")

    return "OK", 200

@app.route('/health', methods=['GET'])
def health(): return "OK", 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)