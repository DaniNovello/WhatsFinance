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
    # Prompt ajustado para extrair ORIGEM e DESTINO separadamente
    prompt_text = f"""
    Aja como um especialista em leitura de comprovantes bancários (Pix, Extratos).
    Extraia os dados e retorne um JSON neste formato exato:
    
    {{
      "intent": "register_transaction",
      "entities": {{
          "payer_name": "Nome de QUEM PAGOU (Origem/De)",
          "payee_name": "Nome de QUEM RECEBEU (Destino/Para)",
          "amount": 0.00,
          "type": "expense" ou "income",
          "payment_method": "credit_card", "debit_card", "pix" ou "money",
          "category": "Motivo (ex: computador, jantar)"
      }}
    }}

    REGRAS DE EXTRAÇÃO:
    1. **Nomes (payer/payee)**:
       - 'payer_name': Procure por "De", "Pagador", "Origem".
       - 'payee_name': Procure por "Para", "Destinatário", "Destino".
       - Se só houver o nome da loja, coloque em 'payee_name' (assuma que é o destino).
       - IGNORE descrições como "pagamento", "envio", "computador".

    2. **Categoria**:
       - Use a descrição do motivo (ex: "computador") para o campo 'category'.
    
    3. **Método**:
       - Se tiver logo Pix ou "Transferência", use 'pix'.

    Mensagem/Imagem: "{message_text}"
    """
    
    content = [prompt_text]
    
    if image_bytes:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            content.append(image)
            logger.info("📸 Imagem anexada")
        except Exception as e:
            logger.error(f"Erro imagem: {e}")

    model = genai.GenerativeModel("gemini-2.5-flash", generation_config=generation_config)

    try:
        response = model.generate_content(content)
        parsed = json.loads(response.text)
        
        # Garante estrutura mínima
        if "intent" not in parsed: parsed["intent"] = "register_transaction"
        if "entities" not in parsed: parsed["entities"] = {}
        
        # Fallback para descrição padrão se a IA falhar em separar
        ents = parsed["entities"]
        if not ents.get("description"):
            # Cria um default temporário, mas o app.py vai decidir o final
            ents["description"] = ents.get("payee_name") or ents.get("payer_name")
            
        return parsed
    except Exception as e:
        logger.error(f"Erro na IA: {e}")
        return None

def get_financial_advice():
    return "💡 Dica: Mantenha suas contas em dia!"