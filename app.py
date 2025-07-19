# Arquivo: app.py (Versão Completa e Final)

import os
from flask import Flask, request
from twilio.rest import Client # <- Nova importação para o cliente Twilio
from dotenv import load_dotenv

# Importa nossos módulos customizados
import db
import commands
import ai_parser

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()
app = Flask(__name__)

# Dicionário simples para guardar o estado da conversa durante o cadastro
user_state = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    # --- 1. Extrai os dados da mensagem recebida ---
    incoming_msg = request.values.get('Body', '').strip()
    sender_phone_whatsapp = request.values.get('From', '') # Formato: "whatsapp:+55..."
    sender_phone = sender_phone_whatsapp.replace('whatsapp:', '') # Formato: "+55..."

    # --- 2. Inicializa o cliente Twilio para poder responder ---
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    twilio_client = Client(account_sid, auth_token)
    twilio_phone = os.environ.get("TWILIO_PHONE_NUMBER")
    
    response_text = "" # Variável para guardar a resposta de texto simples

    try:
        # --- 3. Verifica se o usuário já existe no banco ---
        user = db.get_user_by_phone(sender_phone)

        if not user:
            # --- LÓGICA DE CADASTRO DE NOVO USUÁRIO ---
            if user_state.get(sender_phone) == 'awaiting_name':
                new_user = db.create_user(sender_phone, incoming_msg)
                response_text = f"Ótimo, {new_user['name']}! Seu cadastro foi concluído. Digite /menu para ver as opções."
                del user_state[sender_phone]
            else:
                response_text = "Olá! Bem-vindo(a) ao seu gestor financeiro. Para começar, por favor, me diga seu nome."
                user_state[sender_phone] = 'awaiting_name'
        else:
            # --- USUÁRIO JÁ EXISTE, PROCESSA A MENSAGEM ---
            
            # Primeiro, checa se a mensagem é uma resposta de um botão do menu interativo
            if incoming_msg == "Ver Saldo":
                response_text = commands.handle_command('/saldo', user['id'])

            elif incoming_msg.lower().startswith('/'):
                # Se for um comando de texto, como /menu
                if incoming_msg.lower() == '/menu':
                    # Monta a mensagem interativa
                    body = "Olá! Como posso te ajudar hoje?"
                    sections = [
                        {
                            "title": "Ações Principais",
                            "rows": [
                                {"id": "ver_saldo_id", "title": "Ver Saldo"},
                                {"id": "ver_fatura_id", "title": "Ver Fatura"} # Adicionaremos a lógica depois
                            ]
                        }
                    ]
                    
                    # Envia a mensagem interativa e encerra, pois ela não precisa de resposta de texto
                    twilio_client.messages.create(
                        from_=f'whatsapp:{twilio_phone}',
                        to=sender_phone_whatsapp,
                        body=body,
                        button_text="Menu Principal", # Texto do botão que abre a lista
                        sections=sections
                    )
                    return "OK", 200 # Encerra aqui
                else:
                    # Trata outros comandos de texto (ex: /cadastrar_conta, etc)
                    response_text = commands.handle_command(incoming_msg.lower(), user['id'])

            else:
                # Se não for comando, usa a IA para processar
                ai_data = ai_parser.get_ai_response(incoming_msg)

                if not ai_data:
                    response_text = "😕 Desculpe, não consegui processar sua solicitação."
                else:
                    intent = ai_data.get('intent')
                    entities = ai_data.get('entities', {})

                    if intent == 'register_transaction':
                        success = db.process_transaction_with_rpc(user['id'], entities)
                        if success:
                            desc = entities.get('description', 'N/A')
                            amount = float(entities.get('amount', 0))
                            tipo = "Entrada" if entities.get('type') == 'income' else "Gasto"
                            response_text = f"✅ {tipo} de R${amount:.2f} em '{desc}' registrado!"
                        else:
                            response_text = "Ops! Para registrar uma transação, você precisa ter uma conta. Use `/cadastrar_conta [nome]`."
                    
                    elif intent == 'query_report':
                        description = entities.get('description')
                        time_period = entities.get('time_period')
                        
                        if not time_period:
                            response_text = "Para relatórios, por favor, me diga o período. Ex: 'gastos de hoje'"
                        else:
                            total = db.get_report(user['id'], description, time_period)
                            period_text = {"last_week": "na última semana", "last_month": "no último mês", "today": "hoje", "yesterday": "ontem"}
                            
                            if description:
                                response_text = f"Você gastou R${total:.2f} com '{description}' {period_text.get(time_period, '')}."
                            else:
                                response_text = f"Seu gasto total {period_text.get(time_period, '')} foi de R${total:.2f}."
                    
                    else:
                        response_text = "Não entendi. Você quer registrar um gasto ou fazer uma pergunta?"

    except Exception as e:
        # --- CAPTURA DE ERRO GERAL ---
        print(f"!!!!!!!! ERRO INESPERADO: {e} !!!!!!!!")
        response_text = "🤖 Ops! Encontrei um erro interno. Tente novamente em um instante."

    # --- 4. Envia a resposta de texto (se houver alguma) ---
    if response_text:
        twilio_client.messages.create(
            from_=f'whatsapp:{twilio_phone}',
            body=response_text,
            to=sender_phone_whatsapp
        )

    return "OK", 200 # Responde ao Twilio que a mensagem foi recebida com sucesso

if __name__ == '__main__':
    app.run(port=5000, debug=True)