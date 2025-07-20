import os
from datetime import datetime, timedelta, date # <-- A CORREÇÃO ESTÁ AQUI
from supabase import create_client, Client
import calendar

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

# --- Funções de Cartão de Crédito ---
def create_credit_card(user_id, card_name):
    response = supabase.table('credit_cards').insert({"user_id": user_id, "name": card_name}).execute()
    return response.data[0] if response.data else None

# --- Funções de Transação e Relatório ---
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

def get_date_range(time_period):
    today = date.today()
    if time_period == 'today':
        return today, today
    if time_period == 'yesterday':
        yesterday = today - timedelta(days=1)
        return yesterday, yesterday
    if time_period == 'this_week':
        start_of_week = today - timedelta(days=today.weekday())
        return start_of_week, today
    if time_period == 'last_week':
        end_of_last_week = today - timedelta(days=today.weekday() + 1)
        start_of_last_week = end_of_last_week - timedelta(days=6)
        return start_of_last_week, end_of_last_week
    if time_period == 'this_month':
        start_of_month = today.replace(day=1)
        return start_of_month, today
    if time_period == 'last_month':
        first_day_of_current_month = today.replace(day=1)
        last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
        first_day_of_last_month = last_day_of_last_month.replace(day=1)
        return first_day_of_last_month, last_day_of_last_month
    return None, None

def get_report(user_id, description, time_period):
    start_date, end_date = get_date_range(time_period)
    if not start_date:
        return 0

    end_date_str = (end_date + timedelta(days=1)).isoformat()
    query = supabase.table('transactions').select('amount', count='exact').eq('user_id', user_id).eq('type', 'expense').gte('transaction_date', start_date.isoformat()).lt('transaction_date', end_date_str)
    
    if description:
        query = query.ilike('description', f'%{description}%')
    
    response = query.execute()
    return sum(float(item['amount']) for item in response.data) if response.data else 0

def get_detailed_report(user_id, time_period):
    start_date, end_date = get_date_range(time_period)
    if not start_date:
        return []

    end_date_str = (end_date + timedelta(days=1)).isoformat()
    response = supabase.table('transactions').select('description, amount, transaction_date').eq('user_id', user_id).eq('type', 'expense').gte('transaction_date', start_date.isoformat()).lt('transaction_date', end_date_str).order('transaction_date').execute()
    
    return response.data if response.data else []