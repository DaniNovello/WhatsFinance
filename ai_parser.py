# Arquivo: ai_parser.py
import os
import google.generativeai as genai
import json
import logging
from PIL import Image
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

generation_config = {
    "temperature": 0.2,
    "response_mime_type": "application/json"
}

# ALTERADO: Tente 'gemini-1.5-flash-latest' ou apenas 'gemini-1.5-flash'
# Se der erro de novo, use 'gemini-pro' (mas ele não suporta JSON nativo tão bem quanto o flash)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest", 
    generation_config=generation_config
)

def get_ai_response(message_text, image_bytes=None):
    prompt_text = f"""
    Analise a entrada (texto e/ou imagem) e retorne um JSON.
    Se for financeiro: extraia para 'register_transaction'.
    Se for pedido de fatura/relatório: 'query_report'.

    1. 'register_transaction':
       - description: Nome do local/pessoa.
       - amount: Valor (float).
       - type: 'expense' ou 'income'.
       - payment_method: 'credit_card', 'debit_card', 'pix', 'money' ou null.
       - category: Alimentação, Transporte, Lazer, Saúde, Casa, Outros.

    2. 'query_report':
       - description: termo de busca ou null.
       - time_period: today, yesterday, this_week, this_month, current_invoice (para faturas).

    Mensagem: "{message_text}"
    """
    
    content = [prompt_text]
    if image_bytes:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            content.append(image)
        except Exception as e:
            logger.error(f"Erro imagem: {e}")

    try:
        response = model.generate_content(content)
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Erro na IA: {e}")
        return None

def get_financial_advice():
    # Mantém simples para evitar erros
    return "💡 Dica: Verifique a data de fechamento do seu cartão para ganhar até 40 dias de prazo!"