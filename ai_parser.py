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

    1. Se for 'register_transaction', extraia: 'description', 'amount', 'type', 'payment_method'.
    2. Se for 'query_report', extraia: 'description' (o que foi gasto, ou null se for geral) e um 'time_period'.
       - Mapeie 'hoje' para 'today'.
       - Mapeie 'ontem' para 'yesterday'.
       - Mapeie 'essa semana' ou 'esta semana' para 'this_week'.
       - Mapeie 'semana passada' para 'last_week'.
       - Mapeie 'esse mês' ou 'este mês' para 'this_month'.
       - Mapeie 'mês passado' para 'last_month'.

    Responda APENAS com o JSON.

    Exemplos:
    - Mensagem: "quanto gastei essa semana?"
    - JSON: {{"intent": "query_report", "entities": {{"description": null, "time_period": "this_week"}}}}
    - Mensagem: "gastos com mercado este mês"
    - JSON: {{"intent": "query_report", "entities": {{"description": "mercado", "time_period": "this_month"}}}}

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