# Arquivo: db.py
import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# --- Funções de Usuário ---
def get_user_by_phone(phone_number):
    response = supabase.table('users').select('*').eq('phone_number', phone_number).limit(1).execute()
    return response.data[0] if response.data else None


def create_credit_card(user_id, card_name):
    """Cria um novo cartão de crédito para o usuário."""
    response = supabase.table('credit_cards').insert({"user_id": user_id, "name": card_name}).execute()
    return response.data[0] if response.data else None

def create_user(phone_number, name):
    response = supabase.table('users').insert({"phone_number": phone_number, "name": name}).execute()
    return response.data[0] if response.data else None

# Adicione esta função ao seu arquivo db.py

def get_report(user_id, description, time_period):
    """Busca um relatório de gastos com base nos parâmetros."""
    today = datetime.now()
    if time_period == 'last_week':
        start_date = today - timedelta(days=7)
    elif time_period == 'last_month':
        start_date = today - timedelta(days=30)
    # Adicionar mais períodos aqui (today, yesterday, etc.)
    else:
        return 0 # Período não suportado

    response = supabase.table('transactions').select('amount').eq('user_id', user_id).ilike('description', f'%{description}%').gte('transaction_date', start_date.isoformat()).execute()
    
    if response.data:
        total = sum(float(item['amount']) for item in response.data)
        return total
    return 0

# --- Funções de Conta ---
def create_account(user_id, account_name):
    response = supabase.table('accounts').insert({"user_id": user_id, "name": account_name}).execute()
    return response.data[0] if response.data else None

def get_accounts_balance(user_id):
    response = supabase.table('accounts').select('name, balance').eq('user_id', user_id).execute()
    return response.data if response.data else []

# --- Função de Transação Otimizada ---
def process_transaction_with_rpc(user_id, data):
    """Chama a função do PostgreSQL e retorna seu resultado booleano."""
    try:
        params = {
            'p_user_id': user_id,
            'p_description': data.get('description'),
            'p_amount': data.get('amount'),
            'p_type': data.get('type'),
            'p_payment_method': data.get('payment_method')
        }
        # A resposta da função (true/false) estará em 'response.data'
        response = supabase.rpc('handle_transaction_and_update_balance', params).execute()
        return response.data
    except Exception as e:
        print(f"Erro no RPC da transação: {e}")
        return False