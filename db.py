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

def create_user(phone_number, name):
    response = supabase.table('users').insert({"phone_number": phone_number, "name": name}).execute()
    return response.data[0] if response.data else None

# --- Funções de Conta ---
def create_account(user_id, account_name):
    response = supabase.table('accounts').insert({"user_id": user_id, "name": account_name}).execute()
    return response.data[0] if response.data else None

def get_accounts_balance(user_id):
    response = supabase.table('accounts').select('name, balance').eq('user_id', user_id).execute()
    return response.data if response.data else []

# --- Função de Transação Otimizada ---
def process_transaction_with_rpc(user_id, data):
    """Chama a função do PostgreSQL para processar tudo de uma vez."""
    try:
        params = {
            'p_user_id': user_id,
            'p_description': data.get('description'),
            'p_amount': data.get('amount'),
            'p_type': data.get('type'),
            'p_payment_method': data.get('payment_method')
        }
        # Chama a função mágica no Supabase
        supabase.rpc('handle_transaction_and_update_balance', params).execute()
        return True # Sucesso
    except Exception as e:
        print(f"Erro no RPC da transação: {e}")
        return False