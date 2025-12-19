import os
from datetime import datetime, timedelta, date, time
from dateutil.relativedelta import relativedelta
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# --- USUÁRIO ---
def get_user(telegram_id):
    response = supabase.table('users').select('*').eq('id', telegram_id).limit(1).execute()
    return response.data[0] if response.data else None

def create_user(telegram_id, name):
    response = supabase.table('users').insert({"id": telegram_id, "name": name}).execute()
    return response.data[0] if response.data else None

# --- CONTAS E CARTÕES ---
def create_account(user_id, account_name):
    response = supabase.table('accounts').insert({"user_id": user_id, "name": account_name, "balance": 0.0}).execute()
    return response.data[0] if response.data else None

def get_user_accounts(user_id):
    response = supabase.table('accounts').select('id, name').eq('user_id', user_id).execute()
    return response.data if response.data else []

def get_accounts_balance(user_id):
    response = supabase.table('accounts').select('name, balance').eq('user_id', user_id).execute()
    return response.data if response.data else []

def create_credit_card(user_id, card_name, closing_day=1, due_day=10):
    data = {"user_id": user_id, "name": card_name, "closing_day": closing_day, "due_day": due_day}
    response = supabase.table('credit_cards').insert(data).execute()
    return response.data[0] if response.data else None

def get_user_cards(user_id):
    response = supabase.table('credit_cards').select('*').eq('user_id', user_id).execute()
    return response.data if response.data else []

def get_invoice_total(user_id, card_id=None):
    """Calcula o total da fatura aberta para cada cartão."""
    query = supabase.table('credit_cards').select('*').eq('user_id', user_id)
    if card_id: query = query.eq('id', card_id)
    cards = query.execute().data
    
    if not cards: return 0.0, []

    total_invoice = 0.0
    details = []
    today = date.today()
    
    for card in cards:
        c_day = card.get('closing_day', 1)
        # Lógica simplificada de fechamento
        if today.day >= c_day:
            start_date = date(today.year, today.month, c_day)
            # Vai até o próximo fechamento
            next_month = today.replace(day=28) + timedelta(days=4)
            end_date = date(next_month.year, next_month.month, c_day) - timedelta(days=1)
        else:
            first = today.replace(day=1)
            last_month = first - timedelta(days=1)
            start_date = date(last_month.year, last_month.month, c_day)
            end_date = date(today.year, today.month, c_day) - timedelta(days=1)

        trans = supabase.table('transactions').select('amount')\
            .eq('user_id', user_id).eq('card_id', card['id'])\
            .gte('transaction_date', start_date.isoformat())\
            .lte('transaction_date', end_date.isoformat()).execute().data
            
        card_total = sum(float(t['amount']) for t in trans)
        total_invoice += card_total
        details.append({'card': card['name'], 'total': card_total, 'due_day': card['due_day']})

    return total_invoice, details

# --- TRANSAÇÕES ---
def process_transaction_with_rpc(user_id, data):
    try:
        params = {
            'p_user_id': user_id,
            'p_description': data.get('description'),
            'p_amount': data.get('amount'),
            'p_type': data.get('type'),
            'p_payment_method': data.get('payment_method'),
            'p_category': data.get('category'),
            'p_card_id': data.get('card_id')
        }
        # RPC padrão (insere transação). A atualização de saldo de conta específica é feita depois via update_transaction_account
        supabase.rpc('handle_transaction_and_update_balance', params).execute()
        return True
    except Exception as e:
        print(f"Erro RPC: {e}")
        return False

def create_installments(user_id, data, installments):
    try:
        total = float(data.get('amount', 0))
        val = total / installments
        base_desc = data.get('description', 'Compra')
        base_date = datetime.now()
        for i in range(installments):
            future = base_date + relativedelta(months=i)
            payload = {
                "user_id": user_id,
                "description": f"{base_desc} ({i+1}/{installments})",
                "amount": val,
                "type": data.get('type'),
                "payment_method": data.get('payment_method'),
                "category": data.get('category'),
                "card_id": data.get('card_id'),
                "transaction_date": future.isoformat()
            }
            supabase.table('transactions').insert(payload).execute()
        return True
    except: return False

def update_transaction_method(transaction_id, method):
    try:
        supabase.table('transactions').update({'payment_method': method}).eq('id', transaction_id).execute()
        return True
    except: return False

def update_transaction_card(transaction_id, card_id):
    try:
        supabase.table('transactions').update({'card_id': card_id}).eq('id', transaction_id).execute()
        return True
    except: return False

def update_transaction_account(transaction_id, account_id):
    """Vincula a transação a uma conta e ATUALIZA O SALDO DA CONTA."""
    try:
        # 1. Atualiza o ID da conta na transação
        supabase.table('transactions').update({'account_id': account_id}).eq('id', transaction_id).execute()
        
        # 2. Pega os dados para ajustar o saldo
        trans = supabase.table('transactions').select('amount, type').eq('id', transaction_id).single().execute()
        if trans.data:
            amount = float(trans.data['amount'])
            tipo = trans.data['type']
            
            # Pega saldo atual
            acc = supabase.table('accounts').select('balance').eq('id', account_id).single().execute()
            current_bal = float(acc.data['balance'])
            
            # Calcula novo saldo (Se for Income soma, se for Expense subtrai)
            if tipo == 'income': 
                new_bal = current_bal + amount
            else: 
                new_bal = current_bal - amount
            
            # Salva
            supabase.table('accounts').update({'balance': new_bal}).eq('id', account_id).execute()
            return True
    except Exception as e:
        print(f"Erro update conta: {e}")
        return False

def get_last_transactions(user_id, limit=5):
    response = supabase.table('transactions').select('id, description, amount, type').eq('user_id', user_id).order('transaction_date', desc=True).limit(limit).execute()
    return response.data if response.data else []

def delete_transaction(transaction_id, user_id):
    try:
        supabase.rpc('delete_transaction_and_revert_balance', {'p_transaction_id': transaction_id, 'p_user_id': user_id}).execute()
        return True
    except: return False

# --- RELATÓRIOS ---
def get_date_range(time_period):
    today = date.today()
    if time_period == 'today': return datetime.combine(today, time.min), datetime.combine(today, time.max)
    if time_period == 'yesterday':
        y = today - timedelta(days=1)
        return datetime.combine(y, time.min), datetime.combine(y, time.max)
    if time_period == 'this_week':
        start = today - timedelta(days=today.weekday())
        return datetime.combine(start, time.min), datetime.combine(today, time.max)
    if time_period == 'this_month':
        start = today.replace(day=1)
        return datetime.combine(start, time.min), datetime.combine(today, time.max)
    return None, None

def get_report(user_id, description, time_period):
    start, end = get_date_range(time_period)
    if not start: return 0
    query = supabase.table('transactions').select('amount').eq('user_id', user_id).eq('type', 'expense').gte('transaction_date', start.isoformat()).lte('transaction_date', end.isoformat())
    if description: query = query.ilike('description', f'%{description}%')
    resp = query.execute()
    return sum(float(i['amount']) for i in resp.data) if resp.data else 0

def get_detailed_report(user_id, time_period):
    start, end = get_date_range(time_period)
    if not start: return []
    resp = supabase.table('transactions').select('description, amount, transaction_date, category, type').eq('user_id', user_id).gte('transaction_date', start.isoformat()).lte('transaction_date', end.isoformat()).order('transaction_date').execute()
    return resp.data if resp.data else []

def set_verification_code(user_id, code):
    try:
        supabase.table('users').update({'verification_code': code}).eq('id', user_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao salvar codigo: {e}")
        return False

def verify_code_and_set_password(user_id, code, plain_password):
    try:
        # Busca o usuário e o código
        resp = supabase.table('users').select('verification_code').eq('id', user_id).execute()
        if not resp.data: return False
        
        stored_code = resp.data[0].get('verification_code')
        
        if stored_code == code:
            # Hash da senha para segurança
            p_hash = generate_password_hash(plain_password)
            supabase.table('users').update({
                'password_hash': p_hash,
                'verification_code': None # Limpa o código usado
            }).eq('id', user_id).execute()
            return True
        return False
    except Exception as e:
        print(f"Erro ao definir senha: {e}")
        return False

def check_user_login(user_id, plain_password):
    try:
        resp = supabase.table('users').select('password_hash').eq('id', user_id).execute()
        if not resp.data: return False
        
        p_hash = resp.data[0].get('password_hash')
        if not p_hash: return False
        
        return check_password_hash(p_hash, plain_password)
    except:
        return False