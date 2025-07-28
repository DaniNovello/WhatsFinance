import os
import google.generativeai as genai
import json
from datetime import datetime, timedelta

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

def get_ai_response(message_text):
    prompt = f"""
    Você é um assistente financeiro. Sua tarefa é analisar a mensagem do usuário e retornar um JSON estruturado.
    A intenção do usuário pode ser 'register_transaction' ou 'query_report'.

    1. Se for 'register_transaction', extraia: 'description', 'amount', 'type', 'payment_method'.
       - **Regra Crucial:** Palavras como 'recebi', 'ganhei', 'salário', 'depósito', 'entrada' indicam o type 'income'. Palavras como 'gastei', 'paguei', 'compra', 'saída', 'padaria', 'ifood', 'mercado' indicam 'expense'.

    2. Se for 'query_report', extraia: 'description' (o que foi gasto, ou null se for geral) e um 'time_period'.
       - Mapeie 'hoje' para 'today', 'ontem' para 'yesterday', 'essa semana' para 'this_week', 'semana passada' para 'last_week', 'esse mês' para 'this_month', 'mês passado' para 'last_month'.

    Responda APENAS com o JSON.

    Exemplos:
    - Mensagem: "recebi 800 reais do freela"
    - JSON: {{"intent": "register_transaction", "entities": {{"description": "freela", "amount": 800.00, "type": "income", "payment_method": null}}}}
    - Mensagem: "padaria 15 reais"
    - JSON: {{"intent": "register_transaction", "entities": {{"description": "padaria", "amount": 15.00, "type": "expense", "payment_method": null}}}}
    - Mensagem: "quanto gastei essa semana?"
    - JSON: {{"intent": "query_report", "entities": {{"description": null, "time_period": "this_week"}}}}
    - Mensagem: "gastos com mercado este mês"
    - JSON: {{"intent": "query_report", "entities": {{"description": "mercado", "time_period": "this_month"}}}}

    Mensagem do usuário: "{message_text}"
    JSON:
    """
    try:
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("`", "").replace("json", "")
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Erro Crítico na IA: {e}")
        return None

# --- NOVA FUNÇÃO ---
def get_financial_advice():
    """Usa a IA para gerar um conselho financeiro original."""
    prompt = """
    Você é um coach financeiro. Crie um conselho financeiro original, curto e prático para o fim de semana. 
    Use uma linguagem amigável e motivacional. Formate a resposta com um título em negrito e emojis.
    Exemplo:
    *💡 Planeje seus Gastos de Lazer*
    Antes de sair, defina um orçamento para o seu fim de semana. Saber quanto você pode gastar em restaurantes ou passeios ajuda a evitar surpresas na segunda-feira!
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Erro ao gerar conselho financeiro: {e}")
        return "Hoje a dica é: sempre revise seu orçamento. Um bom planejamento é a chave para a tranquilidade financeira!"
