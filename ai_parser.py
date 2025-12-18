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

def get_ai_response(message_text, image_bytes=None):
    # Prompt ajustado para entender ENTRADAS (income)
    prompt_text = f"""
    Aja como um assistente financeiro pessoal. Analise a entrada e extraia um JSON.
    
    1. 'register_transaction':
       - description: Nome do estabelecimento ou pessoa.
       - amount: Valor numérico (float). Use ponto para decimais.
       - type: 'expense' (para gastos/saídas) ou 'income' (para ganhos/entradas/depósitos).
       - payment_method: 'credit_card', 'debit_card', 'pix', 'money' ou null.
       - installments: Número de parcelas (int). Padrão 1.
       - category: Sugira uma categoria (Ex: Alimentação, Transporte, Salário, Renda Extra).

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

    # ATUALIZADO: Usando o modelo gemini-2.5-flash que substituiu o 1.5
    model = genai.GenerativeModel("gemini-2.5-flash", generation_config=generation_config)

    try:
        response = model.generate_content(content)
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Erro na IA: {e}")
        # Retorna None para que o bot avise que não entendeu, em vez de quebrar
        return None

def get_financial_advice():
    return "💡 Dica: Para ter um saldo real positivo, mantenha suas faturas de cartão menores que seu dinheiro em conta!"