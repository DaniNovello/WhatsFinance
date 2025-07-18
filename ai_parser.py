# Arquivo: ai_parser.py
import os
import google.generativeai as genai
import json

# Configura a API do Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Configurações do modelo
generation_config = {
    "temperature": 0.2,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

def parse_transaction_with_ai(message_text):
    """
    Usa a IA do Gemini para extrair detalhes de uma transação de uma mensagem.
    """
    prompt = f"""
    Analise a seguinte mensagem de finanças e extraia as informações em um formato JSON limpo.
    As chaves possíveis no JSON são: 'description', 'amount', 'type' e 'payment_method'.
    O 'type' deve ser 'income' (para entradas) ou 'expense' (para saídas).
    O 'payment_method' pode ser 'pix', 'debit', 'credit' ou 'cash'.
    Se uma informação não estiver clara, retorne 'null' para a chave correspondente.
    Apenas o JSON deve ser retornado, sem nenhum texto ou formatação adicional.

    Exemplos:
    - Mensagem: "gastei 50 reais no ifood com o cartão de crédito"
    - JSON: {{"description": "ifood", "amount": 50.00, "type": "expense", "payment_method": "credit"}}
    
    - Mensagem: "entrada de 1000 de salário na conta"
    - JSON: {{"description": "salário", "amount": 1000.00, "type": "income", "payment_method": "debit"}}

    - Mensagem: "25 pila no busão"
    - JSON: {{"description": "busão", "amount": 25.00, "type": "expense", "payment_method": null}}

    Agora, analise a seguinte mensagem:
    Mensagem: "{message_text}"
    JSON:
    """

    try:
        response = model.generate_content(prompt)
        # Limpa a resposta para garantir que seja um JSON válido
        cleaned_response = response.text.strip().replace("`", "").replace("json", "")
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Erro ao analisar com IA: {e}")
        return None