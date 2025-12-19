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
    # Prompt Especializado para Comprovantes Bancários Brasileiros e Conversa Natural
    prompt_text = f"""
    Aja como um especialista em finanças e leitura de comprovantes bancários (Pix, Cartão, Extratos).
    Extraia os dados e retorne JSON EXCLUSIVAMENTE neste formato:
    
    {{
      "intent": "register_transaction" OU "query_report",
      "entities": {{
          "description": "Nome da Pessoa ou Loja",
          "amount": 0.00,
          "type": "expense" ou "income",
          "payment_method": "credit_card", "debit_card", "pix", "money" ou null,
          "installments": 1,
          "category": "Categoria sugerida"
      }}
    }}

    REGRAS CRÍTICAS DE EXTRAÇÃO (IMPORTANTE):

    1. **NOME (description)**:
       - O campo 'description' deve conter APENAS o nome da Pessoa ou Estabelecimento.
       - IGNORE descrições de motivos como "computador", "aluguel", "jantar", "mensalidade". Isso vai em 'category'.
       - **Para Comprovantes PIX:**
         - Procure por "Destinatário" ou "Para" (geralmente é Saída).
         - Procure por "Pagador" ou "De" (geralmente é Entrada).
         - Tente identificar quem é a "Outra Parte" da transação (quem não é o dono do celular). Se houver dois nomes (De/Para), pegue o nome da empresa ou da pessoa estranha.

    2. **MÉTODO (payment_method)**:
       - Se ver logos do Pix, "Transferência Pix", "E2E ID" ou chaves aleatórias -> Defina 'payment_method': 'pix'.
       - Se for boleto ou código de barras -> Defina 'payment_method': 'money' (ou boleto se tivesse).
    
    3. **CATEGORIA (category)**:
       - Se houver um campo "Descrição" ou "Motivo" no comprovante (ex: "computador", "churrasco"), coloque ISSO aqui em 'category'.
       - Se não, deduza pelo nome da loja (Ex: Shell -> Transporte/Combustível).

    4. **TIPO (type)**:
       - "Comprovante de Transferência" geralmente é 'expense' (Saída).
       - "Pix Recebido" ou "Você recebeu" é 'income' (Entrada).
       - Na dúvida, deixe o padrão que achar melhor, o usuário vai confirmar depois.

    Mensagem/Contexto do usuário: "{message_text}"
    """
    
    content = [prompt_text]
    
    if image_bytes:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            content.append(image)
            logger.info("📸 Imagem anexada para análise")
        except Exception as e:
            logger.error(f"Erro ao processar imagem: {e}")

    model = genai.GenerativeModel("gemini-2.5-flash", generation_config=generation_config)

    try:
        response = model.generate_content(content)
        parsed = json.loads(response.text)
        
        # Tratamento de erros básicos
        if "intent" not in parsed: parsed["intent"] = None
        if "entities" not in parsed: parsed["entities"] = {}
        
        # Fallback de segurança para PIX
        ent = parsed["entities"]
        desc = ent.get("description", "").lower()
        if "pix" in desc or "transferencia" in desc:
            ent["payment_method"] = "pix"
            
        return parsed
    except Exception as e:
        logger.error(f"Erro na IA: {e}")
        return None

def get_financial_advice():
    return "💡 Dica: Mantenha suas contas em dia e evite juros rotativos do cartão!"