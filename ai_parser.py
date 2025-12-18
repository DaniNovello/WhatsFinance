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

# CORREÇÃO: Usando o alias padrão que é mais estável para visão
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-001", 
    generation_config=generation_config
)

def get_ai_response(message_text, image_bytes=None):
    prompt_text = f"""
    Analise a entrada (texto e/ou imagem) e retorne um JSON.
    
    1. 'register_transaction':
       - description: Nome do estabelecimento/pessoa.
       - amount: Valor TOTAL (float).
       - type: 'expense' (gasto) ou 'income' (ganho).
       - payment_method: 'credit_card', 'debit_card', 'pix', 'money' ou null (se duvida).
       - installments: Número de parcelas (int). Padrão 1.
       - category: Sugira uma categoria (Alimentação, Transporte, etc).

    2. 'query_report':
       - description: termo de busca ou null.
       - time_period: today, yesterday, this_week, this_month, current_invoice.

    Contexto: "{message_text}"
    """
    
    content = [prompt_text]
    
    # Adiciona a imagem se existir
    if image_bytes:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            content.append(image)
            logger.info("📸 Imagem anexada ao prompt da IA")
        except Exception as e:
            logger.error(f"Erro ao processar imagem: {e}")

    try:
        response = model.generate_content(content)
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Erro na IA: {e}")
        return None

def get_financial_advice():
    return "💡 Dica: O melhor dia de compra é o dia do fechamento da sua fatura!"