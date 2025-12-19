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

def get_ai_response(message_text, image_bytes=None):
    # Prompt corrigido para retornar a estrutura "intent" e "entities"
    prompt_text = f"""
    Aja como um assistente financeiro. Sua tarefa é extrair dados da mensagem e retornar um JSON ESTRITAMENTE neste formato:
    
    {{
      "intent": "register_transaction" OU "query_report",
      "entities": {{
          ...dados extraídos...
      }}
    }}

    Regras para 'entities':
    1. Se for transação ('register_transaction'):
       - description: (str) Nome do estabelecimento ou pessoa.
       - amount: (float) Valor numérico.
       - type: 'expense' (gastei, paguei, saída) ou 'income' (ganhei, recebi, entrada).
       - payment_method: 'credit_card' (crédito), 'debit_card' (débito), 'pix', 'money' (dinheiro) ou null.
       - installments: (int) Número de parcelas. Padrão 1.
       - category: (str) Categoria sugerida (Ex: Alimentação, Transporte).

    2. Se for consulta ('query_report'):
       - description: termo de busca ou null.
       - time_period: 'today', 'yesterday', 'this_week', 'this_month'.

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

    # Modelo atualizado e compatível
    model = genai.GenerativeModel("gemini-2.5-flash", generation_config=generation_config)

    try:
        response = model.generate_content(content)
        parsed = json.loads(response.text)
        
        # Garante que chaves mínimas existam para não quebrar o app
        if "intent" not in parsed:
            parsed["intent"] = None
        if "entities" not in parsed:
            parsed["entities"] = {}
            
        return parsed
    except Exception as e:
        logger.error(f"Erro na IA: {e}")
        return None

def get_financial_advice():
    return "💡 Dica: Para ter um saldo real positivo, mantenha suas faturas de cartão menores que seu dinheiro em conta!"