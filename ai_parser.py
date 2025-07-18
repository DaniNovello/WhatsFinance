# Arquivo: ai_parser.py (substitua o conteúdo pelo abaixo)
import os
import google.generativeai as genai
import json

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

generation_config = {"temperature": 0.2}
model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)

def parse_transaction_with_ai(message_text):
    prompt = f"""
    Analise a mensagem de finanças e extraia as informações em formato JSON.
    As chaves são: "description", "amount", "type" ('income' ou 'expense'), e "payment_method".
    - Se a mensagem for um ganho/entrada (ex: 'recebi', 'salário'), o 'type' é 'income'.
    - Se for um gasto (ex: 'gastei', 'paguei', 'compra'), o 'type' é 'expense'.
    - Se a descrição não for clara, tente inferir do contexto (ex: "10 reais de pão" -> "pão"). Se for impossível, use "Transação sem descrição".
    - O 'amount' deve ser um número.
    - O 'payment_method' é opcional.
    - Se não for possível extrair nada, retorne um JSON vazio {{}}.
    - Retorne APENAS o JSON.

    Exemplos:
    - Mensagem: "gastei 50 reais no ifood com o cartão de crédito"
    - JSON: {{"description": "ifood", "amount": 50.00, "type": "expense", "payment_method": "credit"}}
    - Mensagem: "recebi 10 reais"
    - JSON: {{"description": "Transação sem descrição", "amount": 10.00, "type": "income", "payment_method": null}}
    - Mensagem: "recebi 70 reais conta itaú"
    - JSON: {{"description": "conta itaú", "amount": 70.00, "type": "income", "payment_method": null}}

    Agora, analise a mensagem: "{message_text}"
    JSON:
    """
    try:
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("`", "").replace("json", "")
        if not cleaned_response:
            return {}
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Erro Crítico na IA: {e}")
        return {} # Retorna um dicionário vazio em caso de erro