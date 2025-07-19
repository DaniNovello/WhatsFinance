# Arquivo: ai_parser.py
import os
import google.generativeai as genai
import json
from datetime import datetime, timedelta

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

def get_ai_response(message_text):
    prompt = f"""
    Você é um assistente financeiro. Sua tarefa é analisar a mensagem do usuário e retornar um JSON estruturado.
    A intenção do usuário pode ser 'register_transaction' ou 'query_report'.

    1. Se a intenção for 'register_transaction':
       - Extraia 'description', 'amount', 'type' ('income' ou 'expense'), e 'payment_method'.
       - Se a descrição não for clara, use "Transação sem descrição".

    2. Se a intenção for 'query_report':
       - Extraia 'description' (o que foi gasto). Se for um gasto geral (ex: "quanto gastei"), retorne a descrição como null.
       - Extraia um 'time_period'. Mapeie palavras como 'hoje' para 'today', 'ontem' para 'yesterday', 'semana passada' para 'last_week', 'mês passado' para 'last_month'.

    Responda APENAS com o JSON.

    Exemplos:
    - Mensagem: "gastei 50 no ifood"
    - JSON: {{"intent": "register_transaction", "entities": {{"description": "ifood", "amount": 50.00, "type": "expense"}}}}
    
    - Mensagem: "quanto gastei de uber semana passada?"
    - JSON: {{"intent": "query_report", "entities": {{"description": "uber", "time_period": "last_week"}}}}

    - Mensagem: "gastos com mercado ontem"
    - JSON: {{"intent": "query_report", "entities": {{"description": "mercado", "time_period": "yesterday"}}}}

    - Mensagem: "quanto gastei hoje?"
    - JSON: {{"intent": "query_report", "entities": {{"description": null, "time_period": "today"}}}}

    Mensagem do usuário: "{message_text}"
    JSON:
    """
    try:
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("`", "").replace("json", "")
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Erro Crítico na IA: {e}")
        return None