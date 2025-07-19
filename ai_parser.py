# Arquivo: ai_parser.py (substitua o conteúdo pelo abaixo)
import os
import google.generativeai as genai
import json
from datetime import datetime, timedelta

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

def get_ai_response(message_text):
    prompt = f"""
    Analise a mensagem do usuário e determine a intenção e as entidades.
    A intenção pode ser 'register_transaction' ou 'query_report'.

    Se a intenção for 'register_transaction', extraia: 'description', 'amount', 'type' ('income' ou 'expense'), e 'payment_method'.
    Se a intenção for 'query_report', extraia: 'description' (o que foi gasto, ex: 'uber') e um 'time_period' ('last_week', 'last_month', 'today', 'yesterday').

    Responda em formato JSON.

    Exemplos:
    - Mensagem: "gastei 50 no ifood"
    - JSON: {{"intent": "register_transaction", "entities": {{"description": "ifood", "amount": 50.00, "type": "expense"}}}}
    
    - Mensagem: "quanto gastei de uber semana passada?"
    - JSON: {{"intent": "query_report", "entities": {{"description": "uber", "time_period": "last_week"}}}}

    - Mensagem: "gastos com mercado no mes passado"
    - JSON: {{"intent": "query_report", "entities": {{"description": "mercado", "time_period": "last_month"}}}}

    - Mensagem: "recebi 100 reais"
    - JSON: {{"intent": "register_transaction", "entities": {{"description": "Transação sem descrição", "amount": 100.00, "type": "income"}}}}

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