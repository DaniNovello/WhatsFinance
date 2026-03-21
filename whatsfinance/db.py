import os
from datetime import timedelta, date
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
            .lt('transaction_date', (end_date + timedelta(days=1)).isoformat()).execute().data
            
        card_total = sum(float(t['amount']) for t in trans)
        total_invoice += card_total
        details.append({'card': card['name'], 'total': card_total, 'due_day': card['due_day']})

    return total_invoice, details

# --- TRANSAÇÕES (BOT) — mutações via transaction_service + RPCs ---
def process_transaction_with_rpc(user_id, data):
    from whatsfinance.services import transaction_service as ts

    return ts.insert_transaction(user_id, data)


def create_installments(user_id, data, installments):
    from whatsfinance.services import transaction_service as ts

    return ts.create_installments(user_id, data, installments)

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

def update_transaction_account(transaction_id, account_id, user_id=None):
    from whatsfinance.services import transaction_service as ts

    if user_id is None:
        r = supabase.table("transactions").select("user_id").eq("id", transaction_id).limit(1).execute()
        if not r.data:
            return False
        user_id = r.data[0]["user_id"]
    return ts.attach_transaction_to_account(user_id, int(transaction_id), int(account_id))

def get_last_transactions(user_id, limit=5):
    response = supabase.table('transactions').select('*').eq('user_id', user_id).order('transaction_date', desc=True).limit(limit).execute()
    return response.data if response.data else []

def delete_transaction(transaction_id, user_id):
    from whatsfinance.services import transaction_service as ts

    return ts.delete_transaction(user_id, transaction_id)

# --- CRUD DASHBOARD (WEB) ---
def get_transaction(transaction_id, user_id):
    resp = supabase.table('transactions').select('*').eq('id', transaction_id).eq('user_id', user_id).single().execute()
    return resp.data if resp.data else None

def get_all_transactions(user_id, limit=100, filters=None):
    query = supabase.table('transactions').select('*').eq('user_id', user_id).order('transaction_date', desc=True)
    
    if filters:
        if filters.get('type') and filters['type'] in ['income', 'expense']:
            query = query.eq('type', filters['type'])
        
        if filters.get('search'):
            query = query.ilike('description', f"%{filters['search']}%") 

        if filters.get('start_date'):
            query = query.gte('transaction_date', f"{filters['start_date']}T00:00:00")
        
        if filters.get('end_date'):
            query = query.lte('transaction_date', f"{filters['end_date']}T23:59:59")

    query = query.limit(limit)
    
    try:
        resp = query.execute()
        return resp.data if resp.data else []
    except Exception as e:
        print(f"Erro filtro: {e}")
        return []

def update_transaction(user_id, t_id, data):
    from whatsfinance.services import transaction_service as ts

    return ts.update_transaction_from_form(user_id, t_id, data)


def add_transaction_manual(user_id, data):
    from whatsfinance.services import transaction_service as ts

    return ts.add_transaction_from_form(user_id, data)

# --- AUTH ---
def set_verification_code(user_id, code, expires_at_iso: str):
    try:
        supabase.table("users").update(
            {
                "verification_code": code,
                "verification_code_expires_at": expires_at_iso,
                "verification_attempts": 0,
            }
        ).eq("id", user_id).execute()
        return True
    except Exception:
        return False


def _parse_ts(val):
    if val is None:
        return None
    from datetime import datetime, timezone

    if isinstance(val, datetime):
        return val if val.tzinfo else val.replace(tzinfo=timezone.utc)
    s = str(val).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def verify_code_and_set_password(user_id, code, plain_password):
    """
    Valida código (expiração + tentativas), define senha e limpa campos de verificação.
    Retorna: 'ok' | 'wrong_code' | 'expired' | 'locked' | 'bad_password' | 'error'
    """
    from datetime import datetime, timezone

    from whatsfinance import web_security as ws

    ok_pwd, _ = ws.validate_new_password(plain_password)
    if not ok_pwd:
        return "bad_password"

    try:
        resp = (
            supabase.table("users")
            .select("verification_code, verification_code_expires_at, verification_attempts")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )
        if not resp.data:
            return "error"
        row = resp.data[0]
        stored = row.get("verification_code")
        if not stored:
            return "error"

        attempts = int(row.get("verification_attempts") or 0)
        if attempts >= ws.VERIFICATION_MAX_ATTEMPTS:
            return "locked"

        exp = _parse_ts(row.get("verification_code_expires_at"))
        now = datetime.now(timezone.utc)
        if exp is not None and now > exp:
            supabase.table("users").update(
                {
                    "verification_code": None,
                    "verification_code_expires_at": None,
                    "verification_attempts": 0,
                }
            ).eq("id", user_id).execute()
            return "expired"

        if str(code).strip() != str(stored):
            supabase.table("users").update({"verification_attempts": attempts + 1}).eq("id", user_id).execute()
            return "wrong_code"

        p_hash = generate_password_hash(plain_password)
        supabase.table("users").update(
            {
                "password_hash": p_hash,
                "verification_code": None,
                "verification_code_expires_at": None,
                "verification_attempts": 0,
            }
        ).eq("id", user_id).execute()
        return "ok"
    except Exception:
        return "error"

def check_user_login(user_id, plain_password):
    try:
        resp = supabase.table('users').select('password_hash').eq('id', user_id).execute()
        if not resp.data or not resp.data[0].get('password_hash'): return False
        return check_password_hash(resp.data[0]['password_hash'], plain_password)
    except: return False

# --- ESTADO DO BOT (Telegram) — persistido no Supabase ---
def bot_conversation_get(telegram_id):
    try:
        resp = supabase.table('bot_conversation_state').select('*').eq('telegram_id', telegram_id).limit(1).execute()
        if not resp.data:
            return None
        return resp.data[0]
    except Exception:
        return None

def bot_conversation_replace(telegram_id, current_state, pending_intent, payload_json):
    """payload_json None = sem buffer; apaga linha se tudo vazio."""
    empty_state = current_state is None or current_state == ''
    if empty_state and pending_intent is None and payload_json is None:
        bot_conversation_delete(telegram_id)
        return
    row = {
        'telegram_id': telegram_id,
        'current_state': current_state if not empty_state else None,
        'pending_intent': pending_intent,
        'payload_json': payload_json,
    }
    supabase.table('bot_conversation_state').upsert(row, on_conflict='telegram_id').execute()

def bot_conversation_delete(telegram_id):
    try:
        supabase.table('bot_conversation_state').delete().eq('telegram_id', telegram_id).execute()
    except Exception:
        pass