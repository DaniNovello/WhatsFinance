# Arquivo: ai_parser.py
import os
import google.generativeai as genai
import json
import logging

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Configuração para RESPOSTA EM JSON (Evita erros de parsing)
generation_config = {
    "temperature": 0.2,
    "response_mime_type": "application/json"
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config
)

def get_ai_response(message_text):
    prompt = f"""
    Você é um assistente financeiro. Analise a mensagem e retorne um JSON.
    Intenções possíveis: 'register_transaction' ou 'query_report'.

    1. 'register_transaction': Extraia 'description', 'amount', 'type' (income/expense), 'payment_method' e 'category'.
       - Categorias sugeridas: Alimentação, Transporte, Moradia, Lazer, Saúde, Educação, Outros.
       - Se não for claro, use 'Outros'.

    2. 'query_report': Extraia 'description' e 'time_period'.
       - time_period: today, yesterday, this_week, last_week, this_month, last_month.

    Mensagem: "{message_text}"
    """
    try:
        response = model.generate_content(prompt)
        # Com JSON Mode, a resposta já vem limpa
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Erro na IA: {e}")
        return None

def get_financial_advice():
    prompt = "Crie um conselho financeiro curto (máx 2 frases) e motivacional para hoje. Use emojis."
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "💰 Dica: Cuide dos pequenos gastos, eles somam muito no final!"