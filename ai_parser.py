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
    # Prompt ajustado para permitir SAUDAÇÃO e AJUDA
    prompt_text = f"""
    Aja como um assistente financeiro inteligente (Zenith).
    Analise a mensagem ou imagem e retorne um JSON.
    
    FORMATO DE RESPOSTA (Escolha um INTENT):
    
    1. Se for gasto ou ganho:
    {{
      "intent": "register_transaction",
      "entities": {{
          "payer_name": "Quem pagou",
          "payee_name": "Quem recebeu",
          "amount": 0.00,
          "type": "expense" (ou "income"),
          "payment_method": "credit_card" (ou "debit_card", "pix", "money"),
          "category": "categoria do gasto"
      }}
    }}
    
    2. Se for pedido de relatório (ex: "quanto gastei essa semana"):
    {{
      "intent": "query_report",
      "entities": {{ "time_period": "this_week" (ou "last_week", "this_month") }}
    }}

    3. Se for cumprimento, "oi", "olá" ou pedido de ajuda:
    {{
      "intent": "greeting",
      "entities": {{}}
    }}
    
    4. Se não entender nada:
    {{
      "intent": "unknown",
      "entities": {{}}
    }}

    Mensagem do usuário: "{message_text}"
    """
    
    content = [prompt_text]
    
    if image_bytes:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            content.append(image)
        except Exception as e:
            logger.error(f"Erro imagem: {e}")

    model = genai.GenerativeModel("gemini-2.5-flash", generation_config=generation_config)

    try:
        response = model.generate_content(content)
        parsed = json.loads(response.text)
        
        # Garante estrutura mínima
        if "intent" not in parsed: parsed["intent"] = "unknown"
        if "entities" not in parsed: parsed["entities"] = {}
        
        # Fallback de descrição para transações
        if parsed["intent"] == "register_transaction":
            ents = parsed["entities"]
            if not ents.get("description"):
                ents["description"] = ents.get("payee_name") or ents.get("payer_name") or "Despesa"
            
        return parsed
    except Exception as e:
        logger.error(f"Erro na IA: {e}")
        return {"intent": "unknown", "entities": {}} # Retorna fallback seguro

def get_financial_advice():
    return "💡 Dica Zenith: Revise suas faturas semanalmente para evitar surpresas!"