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
    response = supabase.table('accounts').select('*').eq('user_id', user_id).execute()
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
    query = supabase.table('credit_cards').select('*').eq('user_id', user_id)
    if card_id: query = query.eq('id', card_id)
    cards = query.execute().data
    
    if not cards: return 0.0, []

    total_invoice = 0.0
    details = []
    today = date.today()
    
    for card in cards:
        c_day = card.get('closing_day', 1)
        if today.day >= c_day:
            start_date = date(today.year, today.month, c_day)
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
        supabase.rpc('handle_transaction_and_update_balance', params).execute()
        return True
    except: return False

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
    try:
        supabase.table('transactions').update({'account_id': account_id}).eq('id', transaction_id).execute()
        trans = supabase.table('transactions').select('amount, type').eq('id', transaction_id).single().execute()
        if trans.data:
            amount = float(trans.data['amount'])
            tipo = trans.data['type']
            acc = supabase.table('accounts').select('balance').eq('id', account_id).single().execute()
            new_bal = float(acc.data['balance']) + amount if tipo == 'income' else float(acc.data['balance']) - amount
            supabase.table('accounts').update({'balance': new_bal}).eq('id', account_id).execute()
            return True
    except: return False

def get_last_transactions(user_id, limit=5):
    response = supabase.table('transactions').select('*').eq('user_id', user_id).order('transaction_date', desc=True).limit(limit).execute()
    return response.data if response.data else []

def delete_transaction(transaction_id, user_id):
    try:
        supabase.rpc('delete_transaction_and_revert_balance', {'p_transaction_id': int(transaction_id), 'p_user_id': user_id}).execute()
        return True
    except: return False

# --- CRUD DASHBOARD ---
def get_transaction(transaction_id, user_id):
    resp = supabase.table('transactions').select('*').eq('id', transaction_id).eq('user_id', user_id).single().execute()
    return resp.data if resp.data else None

def get_all_transactions(user_id, limit=100, filters=None):
    # filters é um dicionário: {'type': '...', 'search': '...', 'start_date': '...', 'end_date': '...'}
    query = supabase.table('transactions').select('*').eq('user_id', user_id).order('transaction_date', desc=True)
    
    if filters:
        # Filtro por Tipo (Entrada/Saída)
        if filters.get('type') and filters['type'] in ['income', 'expense']:
            query = query.eq('type', filters['type'])
        
        # Filtro por Texto (Descrição ou Categoria)
        if filters.get('search'):
            # Busca aproximada (ilike)
            term = f"%{filters['search']}%"
            # Nota: Supabase as vezes requer sintaxe específica para OR, 
            # vamos simplificar filtrando Description. Para OR complexo precisaria de .or_()
            query = query.ilike('description', term) 

        # Filtro de Data (Início e Fim)
        if filters.get('start_date'):
            query = query.gte('transaction_date', f"{filters['start_date']}T00:00:00")
        
        if filters.get('end_date'):
            query = query.lte('transaction_date', f"{filters['end_date']}T23:59:59")

    # Limite final
    query = query.limit(limit)
    
    try:
        resp = query.execute()
        return resp.data if resp.data else []
    except Exception as e:
        print(f"Erro filtro: {e}")
        return []

def update_transaction(user_id, t_id, data):
    try:
        acc_id = int(data['account_id']) if data.get('account_id') else None
        card_id = int(data['card_id']) if data.get('card_id') else None
        params = {
            'p_transaction_id': int(t_id),
            'p_user_id': user_id,
            'p_description': data['description'],
            'p_amount': float(data['amount']),
            'p_type': data['type'],
            'p_payment_method': data['payment_method'],
            'p_category': data.get('category'),
            'p_account_id': acc_id,
            'p_card_id': card_id,
            'p_date': data.get('date')
        }
        supabase.rpc('update_transaction_and_balance', params).execute()
        return True
    except: return False

def add_transaction_manual(user_id, data):
    try:
        acc_id = int(data['account_id']) if data.get('account_id') else None
        card_id = int(data['card_id']) if data.get('card_id') else None
        payload = {
            "user_id": user_id,
            "description": data['description'],
            "amount": float(data['amount']),
            "type": data['type'],
            "payment_method": data['payment_method'],
            "category": data.get('category'),
            "card_id": card_id,
            "account_id": acc_id,
            "transaction_date": data.get('date') or datetime.now().isoformat()
        }
        t = supabase.table('transactions').insert(payload).execute()
        if t.data and acc_id:
            acc = supabase.table('accounts').select('balance').eq('id', acc_id).single().execute()
            bal = float(acc.data['balance'])
            new_bal = bal + float(data['amount']) if data['type'] == 'income' else bal - float(data['amount'])
            supabase.table('accounts').update({'balance': new_bal}).eq('id', acc_id).execute()
        return True
    except: return False

# --- AUTH ---
def set_verification_code(user_id, code):
    try:
        supabase.table('users').update({'verification_code': code}).eq('id', user_id).execute()
        return True
    except: return False

def verify_code_and_set_password(user_id, code, plain_password):
    try:
        resp = supabase.table('users').select('verification_code').eq('id', user_id).execute()
        if not resp.data or resp.data[0].get('verification_code') != code: return False
        p_hash = generate_password_hash(plain_password)
        supabase.table('users').update({'password_hash': p_hash, 'verification_code': None}).eq('id', user_id).execute()
        return True
    except: return False

def check_user_login(user_id, plain_password):
    try:
        resp = supabase.table('users').select('password_hash').eq('id', user_id).execute()
        if not resp.data or not resp.data[0].get('password_hash'): return False
        return check_password_hash(resp.data[0]['password_hash'], plain_password)
    except: return False