# Arquivo: db.py (substitua o conteúdo pelo abaixo)
import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# --- Funções de Usuário ---
def get_user_by_phone(phone_number):
    response = supabase.table('users').select('*').eq('phone_number', phone_number).execute()
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
    return response.data if response.data else None

def get_default_account(user_id):
    # Por enquanto, pega a primeira conta do usuário.
    response = supabase.table('accounts').select('id, balance').eq('user_id', user_id).limit(1).execute()
    return response.data[0] if response.data else None

def update_account_balance(account_id, new_balance):
    supabase.table('accounts').update({'balance': new_balance}).eq('id', account_id).execute()

# --- Função de Transação ---
def create_transaction(user_id, data):
    data['user_id'] = user_id
    
    # Insere a transação na tabela 'transactions'
    response = supabase.table('transactions').insert(data).execute()
    
    if not response.data:
        print("Falha ao inserir transação.")
        return None

    transaction_data = response.data[0]
    amount = float(transaction_data['amount'])
    type = transaction_data['type']
    
    # LÓGICA PARA ATUALIZAR O SALDO
    # Por enquanto, vamos usar a conta default
    account = get_default_account(user_id)
    if account:
        current_balance = float(account['balance'])
        if type == 'income':
            new_balance = current_balance + amount
        elif type == 'expense':
            new_balance = current_balance - amount
        else:
            return transaction_data # Não altera o saldo se não for income/expense
            
        update_account_balance(account['id'], new_balance)
    
    return transaction_data