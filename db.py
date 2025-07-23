import os
from datetime import datetime, timedelta, date, time
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# --- Funções de Usuário ---
def get_user_by_phone(phone_number):
    response = supabase.table('users').select('id, name').eq('phone_number', phone_number).limit(1).execute()
    return response.data[0] if response.data else None

def create_user(phone_number, name):
    response = supabase.table('users').insert({"phone_number": phone_number, "name": name}).execute()
    return response.data[0] if response.data else None

# --- Funções de Conta e Cartão ---
def create_account(user_id, account_name):
    response = supabase.table('accounts').insert({"user_id": user_id, "name": account_name}).execute()
    return response.data[0] if response.data else None

def get_accounts_balance(user_id):
    response = supabase.table('accounts').select('name, balance').eq('user_id', user_id).execute()
    return response.data if response.data else []

def create_credit_card(user_id, card_name):
    response = supabase.table('credit_cards').insert({"user_id": user_id, "name": card_name}).execute()
    return response.data[0] if response.data else None

# --- Funções de Transação ---
def process_transaction_with_rpc(user_id, data):
    try:
        params = {
            'p_user_id': user_id,
            'p_description': data.get('description'),
            'p_amount': data.get('amount'),
            'p_type': data.get('type'),
            'p_payment_method': data.get('payment_method')
        }
        response = supabase.rpc('handle_transaction_and_update_balance', params).execute()
        return response.data
    except Exception as e:
        print(f"Erro no RPC da transação: {e}")
        return False

# --- Funções de Relatório ---
def get_date_range(time_period):
    today = date.today()
    if time_period == 'today':
        start_date = datetime.combine(today, time.min)
        end_date = datetime.combine(today, time.max)
        return start_date, end_date
    if time_period == 'yesterday':
        yesterday = today - timedelta(days=1)
        start_date = datetime.combine(yesterday, time.min)
        end_date = datetime.combine(yesterday, time.max)
        return start_date, end_date
    if time_period == 'this_week':
        start_of_week = today - timedelta(days=today.weekday())
        start_date = datetime.combine(start_of_week, time.min)
        end_date = datetime.combine(today, time.max)
        return start_date, end_date
    if time_period == 'last_week':
        end_of_last_week = today - timedelta(days=today.weekday() + 1)
        start_of_last_week = end_of_last_week - timedelta(days=6)
        start_date = datetime.combine(start_of_last_week, time.min)
        end_date = datetime.combine(end_of_last_week, time.max)
        return start_date, end_date
    if time_period == 'this_month':
        start_of_month = today.replace(day=1)
        start_date = datetime.combine(start_of_month, time.min)
        end_date = datetime.combine(today, time.max)
        return start_date, end_date
    if time_period == 'last_month':
        first_day_of_current_month = today.replace(day=1)
        last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
        first_day_of_last_month = last_day_of_last_month.replace(day=1)
        start_date = datetime.combine(first_day_of_last_month, time.min)
        end_date = datetime.combine(last_day_of_last_month, time.max)
        return start_date, end_date
    return None, None

def get_report(user_id, description, time_period):
    start_date, end_date = get_date_range(time_period)
    if not start_date: return 0
    query = supabase.table('transactions').select('amount', count='exact').eq('user_id', user_id).eq('type', 'expense').gte('transaction_date', start_date.isoformat()).lte('transaction_date', end_date.isoformat())
    if description:
        query = query.ilike('description', f'%{description}%')
    response = query.execute()
    return sum(float(item['amount']) for item in response.data) if response.data else 0

def get_detailed_report(user_id, time_period):
    start_date, end_date = get_date_range(time_period)
    if not start_date: return []
    response = supabase.table('transactions').select('description, amount, transaction_date').eq('user_id', user_id).eq('type', 'expense').gte('transaction_date', start_date.isoformat()).lte('transaction_date', end_date.isoformat()).order('transaction_date').execute()
    return response.data if response.data else []

# --- NOVAS FUNÇÕES DE EXCLUSÃO ---
def get_last_transactions(user_id, limit=5):
    """Busca as últimas N transações de um usuário."""
    response = supabase.table('transactions').select('id, description, amount, type').eq('user_id', user_id).order('transaction_date', desc=True).limit(limit).execute()
    return response.data if response.data else []

def delete_transaction(transaction_id, user_id):
    """Chama a função RPC para apagar uma transação e corrigir o saldo."""
    try:
        supabase.rpc('delete_transaction_and_revert_balance', {'p_transaction_id': transaction_id, 'p_user_id': user_id}).execute()
        return True
    except Exception as e:
        print(f"Erro ao apagar transação: {e}")
        return False