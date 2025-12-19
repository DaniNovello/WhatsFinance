import os
import random
import json
from datetime import datetime
import requests
from flask import Blueprint, request, render_template_string, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user, UserMixin
import db
import templates_web as tpl

web_bp = Blueprint('web', __name__)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def send_telegram_msg(chat_id, text):
    try:
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'})
    except: pass

class User(UserMixin):
    def __init__(self, id, name):
        self.id = str(id)
        self.name = name

# --- ROTAS PRINCIPAIS ---
@web_bp.route('/')
def index():
    return redirect(url_for('web.dashboard')) if current_user.is_authenticated else redirect(url_for('web.login'))

@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        t_id, pwd = request.form.get('telegram_id'), request.form.get('password')
        if db.check_user_login(t_id, pwd):
            u = db.get_user(t_id)
            login_user(User(u['id'], u['name']))
            return redirect(url_for('web.dashboard'))
        flash('❌ Login inválido.')
    return render_template_string(tpl.BASE_LAYOUT.replace('{content_body}', tpl.LOGIN_PAGE))

@web_bp.route('/register')
def register_page():
    return render_template_string(tpl.BASE_LAYOUT.replace('{content_body}', tpl.REGISTER_PAGE))

@web_bp.route('/send_code', methods=['POST'])
def send_code():
    t_id = request.form.get('telegram_id')
    if not db.get_user(t_id):
        flash("⚠️ Usuário não encontrado. Inicie o bot primeiro.")
        return redirect(url_for('web.register_page'))
    code = str(random.randint(100000, 999999))
    db.set_verification_code(t_id, code)
    send_telegram_msg(t_id, f"🔐 *Seu Código Web:*\n\n`{code}`")
    return render_template_string(tpl.BASE_LAYOUT.replace('{content_body}', tpl.VERIFY_PAGE), telegram_id=t_id)

@web_bp.route('/verify_setup', methods=['POST'])
def verify_setup():
    t_id, code, pwd = request.form.get('telegram_id'), request.form.get('code'), request.form.get('password')
    if db.verify_code_and_set_password(t_id, code, pwd):
        flash("✅ Senha criada! Faça login.")
        return redirect(url_for('web.login'))
    flash("❌ Código incorreto.")
    return redirect(url_for('web.register_page'))

@web_bp.route('/dashboard')
@login_required
def dashboard():
    uid = current_user.id
    accs, recent = db.get_user_accounts(uid), db.get_last_transactions(uid, 10)
    total_acc = sum(float(a['balance']) for a in accs)
    try: total_invoice, invoice_details = db.get_invoice_total(uid)
    except: total_invoice, invoice_details = 0.0, []
    
    recent_json = json.dumps([{'type': t['type'], 'amount': float(t['amount'])} for t in recent])
    full_html = tpl.BASE_LAYOUT.replace('{content_body}', tpl.DASHBOARD_PAGE)
    return render_template_string(full_html, user=current_user, accs=accs, total_acc=total_acc, total_invoice=total_invoice, invoice_details=invoice_details, recent=recent, recent_json=recent_json)

# --- ROTAS DE TRANSAÇÕES (CRUD) ---
@web_bp.route('/transactions')
@login_required
def list_transactions():
    transactions = db.get_all_transactions(current_user.id)
    return render_template_string(tpl.BASE_LAYOUT.replace('{content_body}', tpl.TRANSACTIONS_LIST_PAGE), transactions=transactions)

@web_bp.route('/transaction/new', methods=['GET', 'POST'])
@login_required
def new_transaction():
    if request.method == 'POST':
        data = {k: request.form.get(k) for k in ['type', 'description', 'amount', 'category', 'payment_method', 'account_id', 'card_id', 'date']}
        if db.add_transaction_manual(current_user.id, data):
            flash("✅ Transação adicionada!")
            return redirect(url_for('web.dashboard'))
        flash("❌ Erro ao adicionar.")
    
    accs, cards = db.get_user_accounts(current_user.id), db.get_user_cards(current_user.id)
    now_str = datetime.now().strftime('%Y-%m-%dT%H:%M')
    return render_template_string(tpl.BASE_LAYOUT.replace('{content_body}', tpl.TRANSACTION_FORM_PAGE), t=None, accounts=accs, cards=cards, now=now_str)

@web_bp.route('/transaction/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(id):
    if request.method == 'POST':
        data = {k: request.form.get(k) for k in ['type', 'description', 'amount', 'category', 'payment_method', 'account_id', 'card_id', 'date']}
        if db.update_transaction(current_user.id, id, data):
            flash("✅ Transação atualizada!")
            return redirect(url_for('web.list_transactions'))
        flash("❌ Erro ao atualizar.")
    
    t = db.get_transaction(id, current_user.id)
    if not t: return redirect(url_for('web.list_transactions'))
    if t.get('transaction_date'): t['transaction_date'] = t['transaction_date'][:16]
    
    accs, cards = db.get_user_accounts(current_user.id), db.get_user_cards(current_user.id)
    return render_template_string(tpl.BASE_LAYOUT.replace('{content_body}', tpl.TRANSACTION_FORM_PAGE), t=t, accounts=accs, cards=cards)

@web_bp.route('/transaction/delete/<id>')
@login_required
def delete_transaction_route(id):
    if db.delete_transaction(id, current_user.id): flash("🗑️ Excluída.")
    else: flash("❌ Erro ao excluir.")
    return redirect(url_for('web.list_transactions'))

@web_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('web.login'))