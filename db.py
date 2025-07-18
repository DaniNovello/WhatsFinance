# Arquivo: db.py
import os
from supabase import create_client, Client

# Pega as credenciais do Supabase do arquivo .env
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def get_user_by_phone(phone_number):
    """Busca um usuário pelo número de telefone."""
    try:
        response = supabase.table('users').select('*').eq('phone_number', phone_number).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        return None

def create_user(phone_number, name):
    """Cria um novo usuário."""
    try:
        response = supabase.table('users').insert({"phone_number": phone_number, "name": name}).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        return None
        
# Adicione aqui outras funções para interagir com o banco de dados no futuro
# ex: create_transaction, get_accounts, etc.

def create_transaction(user_id, data):
    """Cria uma nova transação no banco de dados."""
    try:
        # Adiciona o user_id aos dados antes de inserir
        data['user_id'] = user_id
        
        response = supabase.table('transactions').insert(data).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Erro ao criar transação: {e}")
        return None