import os
import random
import json
import requests
from flask import Blueprint, request, render_template_string, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user, UserMixin
import db
import templates_web as tpl

# Criamos o "Blueprint"
web_bp = Blueprint('web', __name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def send_telegram_msg(chat_id, text):
    try:
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'
        })
    except: pass

class User(UserMixin):
    def __init__(self, id, name):
        self.id = str(id)
        self.name = name

# --- ROTAS ---

@web_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('web.dashboard'))
    return redirect(url_for('web.login'))

@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        t_id = request.form.get('telegram_id')
        pwd = request.form.get('password')
        
        if db.check_user_login(t_id, pwd):
            u = db.get_user(t_id)
            login_user(User(u['id'], u['name']))
            return redirect(url_for('web.dashboard'))
        
        flash('❌ Login inválido. Verifique ID e senha.')
    
    # Injeção manual do HTML para evitar conflito de Jinja
    full_html = tpl.BASE_LAYOUT.replace('{content_body}', tpl.LOGIN_PAGE)
    return render_template_string(full_html)

@web_bp.route('/register', methods=['GET'])
def register_page():
    full_html = tpl.BASE_LAYOUT.replace('{content_body}', tpl.REGISTER_PAGE)
    return render_template_string(full_html)

@web_bp.route('/send_code', methods=['POST'])
def send_code():
    t_id = request.form.get('telegram_id')
    user = db.get_user(t_id)
    
    if not user:
        flash("⚠️ Usuário não encontrado! Mande um 'Oi' no Bot do Telegram primeiro.")
        return redirect(url_for('web.register_page'))
    
    code = str(random.randint(100000, 999999))
    db.set_verification_code(t_id, code)
    
    send_telegram_msg(t_id, f"🔐 *Seu Código Web:*\n\n`{code}`\n\nUse para criar sua senha.")
    
    # Injeta a página de verificação
    full_html = tpl.BASE_LAYOUT.replace('{content_body}', tpl.VERIFY_PAGE)
    return render_template_string(full_html, telegram_id=t_id)

@web_bp.route('/verify_setup', methods=['POST'])
def verify_setup():
    t_id = request.form.get('telegram_id')
    code = request.form.get('code')
    pwd = request.form.get('password')
    
    if db.verify_code_and_set_password(t_id, code, pwd):
        flash("✅ Senha criada com sucesso! Faça login.")
        return redirect(url_for('web.login'))
    else:
        flash("❌ Código incorreto ou expirado.")
        return redirect(url_for('web.register_page'))

@web_bp.route('/dashboard')
@login_required
def dashboard():
    uid = current_user.id
    
    accs = db.get_user_accounts(uid)
    cards = db.get_user_cards(uid) # Adicionei aqui pois estava faltando
    recent = db.get_last_transactions(uid, 10)
    
    total_acc = sum(float(a['balance']) for a in accs)
    
    # Função segura para pegar faturas (caso db.py não tenha atualizado)
    try:
        total_invoice, invoice_details = db.get_invoice_total(uid)
    except:
        total_invoice, invoice_details = 0.0, []

    bot_user = "SeuBotFinanceiroBot" 
    
    # Prepara JSON seguro para o gráfico
    recent_json = json.dumps([{'type': t['type'], 'amount': float(t['amount'])} for t in recent])

    # Monta a página final
    full_html = tpl.BASE_LAYOUT.replace('{content_body}', tpl.DASHBOARD_PAGE)

    return render_template_string(full_html, 
        user=current_user,
        accs=accs,
        total_acc=total_acc,
        total_invoice=total_invoice,
        invoice_details=invoice_details,
        recent=recent,
        recent_json=recent_json,
        bot_username=bot_user
    )

@web_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('web.login'))