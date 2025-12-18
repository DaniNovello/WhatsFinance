import os
import google.generativeai as genai
import json
import logging
from PIL import Image
import io
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

generation_config = {
    "temperature": 0.2,
    "response_mime_type": "application/json"
}

# --- MODELO ESTÁVEL E ROBUSTO ---
# Usamos o 1.5 Flash padrão. Ele é rápido, aceita imagens e tem cota alta.
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", 
    generation_config=generation_config
)

def get_ai_response(message_text, image_bytes=None):
    prompt_text = f"""
    Aja como um assistente financeiro. Analise a entrada e extraia um JSON.
    
    1. 'register_transaction':
       - description: Nome do local/pessoa.
       - amount: Valor (float).
       - type: 'expense' (gasto) ou 'income' (ganho).
       - payment_method: 'credit_card', 'debit_card', 'pix', 'money' ou null.
       - installments: Parcelas (int). Padrão 1.
       - category: Categoria (Alimentação, Transporte, Casa, Lazer).

    2. 'query_report':
       - description: termo de busca ou null.
       - time_period: today, yesterday, this_week, this_month.

    Mensagem do usuário: "{message_text}"
    """
    
    content = [prompt_text]
    
    if image_bytes:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            content.append(image)
            logger.info("📸 Imagem anexada para análise")
        except Exception as e:
            logger.error(f"Erro ao processar imagem: {e}")

    try:
        # Tenta gerar a resposta
        response = model.generate_content(content)
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Erro na IA: {e}")
        # Se der erro de cota (429), espera um pouco e tenta de novo (simples retry)
        if "429" in str(e):
            time.sleep(2)
            try:
                response = model.generate_content(content)
                return json.loads(response.text)
            except:
                return None
        return None

def get_financial_advice():
    return "💡 Dica: Evite gastos impulsivos!"