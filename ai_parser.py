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

# --- MODELOS ESPECÍFICOS (Versão 002 - Mais Recente) ---
try:
    model_flash = genai.GenerativeModel(
        model_name="gemini-1.5-flash-002", 
        generation_config=generation_config
    )

    model_pro = genai.GenerativeModel(
        model_name="gemini-1.5-pro-002", 
        generation_config=generation_config
    )
except Exception as e:
    logger.error(f"Erro ao inicializar modelos: {e}")

def get_ai_response(message_text, image_bytes=None):
    prompt_text = f"""
    Aja como um contador especialista. Analise a entrada e extraia JSON.
    
    1. 'register_transaction':
       - description: Nome do estabelecimento/pessoa.
       - amount: Valor (float).
       - type: 'expense' (saída/gasto) ou 'income' (entrada/ganho).
       - payment_method: 'credit_card', 'debit_card', 'pix', 'money' ou null.
       - installments: Parcelas (int). Padrão 1.
       - category: Categoria sugerida.

    2. 'query_report':
       - description: termo de busca ou null.
       - time_period: today, yesterday, this_week, this_month.

    Contexto: "{message_text}"
    """
    
    content = [prompt_text]
    
    # LÓGICA DE SELEÇÃO DE MODELO
    if image_bytes:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            content.append(image)
            logger.info("📸 Imagem: Usando Gemini 1.5 PRO-002")
            selected_model = model_pro
        except Exception as e:
            logger.error(f"Erro imagem: {e}")
            selected_model = model_flash
    else:
        logger.info("📝 Texto: Usando Gemini 1.5 Flash-002")
        selected_model = model_flash

    try:
        response = selected_model.generate_content(content)
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Erro CRÍTICO na IA: {e}")
        return None

def get_financial_advice():
    return "💡 Dica: O melhor dia de compra é o dia do fechamento da sua fatura!"