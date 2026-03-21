import os
import random
import json
from datetime import datetime, timedelta, timezone

import requests
from flask import Blueprint, request, render_template_string, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user, UserMixin

from whatsfinance import db, templates_web as tpl, web_security as ws

web_bp = Blueprint("web", __name__)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


def send_telegram_msg(chat_id, text):
    try:
        requests.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
        )
    except Exception:
        pass


class User(UserMixin):
    def __init__(self, id, name):
        self.id = str(id)
        self.name = name


# --- ROTAS PRINCIPAIS ---
@web_bp.route("/")
def index():
    return (
        redirect(url_for("web.dashboard"))
        if current_user.is_authenticated
        else redirect(url_for("web.login"))
    )


@web_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ws.validate_csrf()
        raw_id = request.form.get("telegram_id")
        t_id = ws.normalize_telegram_id(raw_id)
        pwd = request.form.get("password")
        if not t_id:
            flash("ID de acesso inválido.")
        elif pwd and db.check_user_login(t_id, pwd):
            u = db.get_user(t_id)
            login_user(User(u["id"], u["name"]))
            return redirect(url_for("web.dashboard"))
        else:
            flash("Credenciais inválidas.")
    return render_template_string(tpl.BASE_LAYOUT.replace("{content_body}", tpl.LOGIN_PAGE))


@web_bp.route("/register")
def register_page():
    return render_template_string(tpl.BASE_LAYOUT.replace("{content_body}", tpl.REGISTER_PAGE))


@web_bp.route("/send_code", methods=["POST"])
def send_code():
    ws.validate_csrf()
    raw = request.form.get("telegram_id")
    t_id = ws.normalize_telegram_id(raw)
    if not t_id:
        flash("ID inválido.")
        return redirect(url_for("web.register_page"))
    if not db.get_user(t_id):
        flash("ID não encontrado.")
        return redirect(url_for("web.register_page"))
    code = str(random.randint(100000, 999999))
    expires = datetime.now(timezone.utc) + timedelta(minutes=ws.VERIFICATION_CODE_TTL_MINUTES)
    db.set_verification_code(t_id, code, expires.isoformat())
    send_telegram_msg(t_id, f"🔐 *Código Zenit:*\n\n`{code}`\n\nVálido por {ws.VERIFICATION_CODE_TTL_MINUTES} min.")
    return render_template_string(
        tpl.BASE_LAYOUT.replace("{content_body}", tpl.VERIFY_PAGE), telegram_id=t_id
    )


@web_bp.route("/verify_setup", methods=["POST"])
def verify_setup():
    ws.validate_csrf()
    raw = request.form.get("telegram_id")
    t_id = ws.normalize_telegram_id(raw)
    code = (request.form.get("code") or "").strip()
    pwd = request.form.get("password")
    if not t_id:
        flash("Sessão inválida. Solicite o código novamente.")
        return redirect(url_for("web.register_page"))

    result = db.verify_code_and_set_password(t_id, code, pwd)
    if result == "ok":
        flash("Senha criada. Bem-vindo.")
        return redirect(url_for("web.login"))
    if result == "bad_password":
        flash(f"Senha deve ter pelo menos {ws.MIN_PASSWORD_LENGTH} caracteres.")
    elif result == "expired":
        flash("Código expirado. Solicite um novo.")
    elif result == "locked":
        flash("Muitas tentativas. Solicite um novo código.")
    elif result == "wrong_code":
        flash("Código incorreto.")
    else:
        flash("Não foi possível concluir. Tente novamente.")
    return render_template_string(
        tpl.BASE_LAYOUT.replace("{content_body}", tpl.VERIFY_PAGE), telegram_id=t_id
    )


@web_bp.route("/dashboard")
@login_required
def dashboard():
    uid = current_user.id
    accs, cards = db.get_user_accounts(uid), db.get_user_cards(uid)
    recent = db.get_last_transactions(uid, 5)
    total_acc = sum(float(a["balance"]) for a in accs)
    try:
        total_invoice, invoice_details = db.get_invoice_total(uid)
    except Exception:
        total_invoice, invoice_details = 0.0, []

    recent_json = json.dumps([{"type": t["type"], "amount": float(t["amount"])} for t in recent])
    now_str = datetime.now().strftime("%Y-%m-%dT%H:%M")

    full_html = tpl.BASE_LAYOUT.replace("{content_body}", tpl.DASHBOARD_PAGE)
    return render_template_string(
        full_html,
        user=current_user,
        accs=accs,
        cards=cards,
        total_acc=total_acc,
        total_invoice=total_invoice,
        invoice_details=invoice_details,
        recent=recent,
        recent_json=recent_json,
        now=now_str,
    )


@web_bp.route("/transactions")
@login_required
def list_transactions():
    uid = current_user.id
    filters = {
        "type": request.args.get("type"),
        "search": request.args.get("search"),
        "start_date": request.args.get("start_date"),
        "end_date": request.args.get("end_date"),
    }
    filters = ws.sanitize_search_filter(filters)

    transactions = db.get_all_transactions(uid, filters=filters)
    accs, cards = db.get_user_accounts(uid), db.get_user_cards(uid)
    now_str = datetime.now().strftime("%Y-%m-%dT%H:%M")

    full_html = tpl.BASE_LAYOUT.replace("{content_body}", tpl.TRANSACTIONS_LIST_PAGE)
    return render_template_string(
        full_html,
        transactions=transactions,
        user=current_user,
        accounts=accs,
        cards=cards,
        now=now_str,
        filters=filters,
    )


@web_bp.route("/transaction/new", methods=["POST"])
@login_required
def new_transaction():
    ws.validate_csrf()
    data = {
        k: request.form.get(k)
        for k in [
            "type",
            "description",
            "amount",
            "category",
            "payment_method",
            "account_id",
            "card_id",
            "date",
        ]
    }
    ok, err = ws.validate_transaction_form(data)
    if not ok:
        flash(err)
        return redirect(request.referrer or url_for("web.dashboard"))
    if db.add_transaction_manual(current_user.id, data):
        flash("Registro salvo.")
    else:
        flash("Erro ao salvar.")
    return redirect(request.referrer or url_for("web.dashboard"))


@web_bp.route("/transaction/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_transaction(id):
    if request.method == "POST":
        ws.validate_csrf()
        data = {
            k: request.form.get(k)
            for k in [
                "type",
                "description",
                "amount",
                "category",
                "payment_method",
                "account_id",
                "card_id",
                "date",
            ]
        }
        ok, err = ws.validate_transaction_form(data)
        if not ok:
            flash(err)
            return redirect(url_for("web.edit_transaction", id=id))
        if db.update_transaction(current_user.id, id, data):
            flash("Atualizado com sucesso.")
            return redirect(url_for("web.list_transactions"))
        flash("Erro ao atualizar.")

    t = db.get_transaction(id, current_user.id)
    if not t:
        return redirect(url_for("web.list_transactions"))
    if t.get("transaction_date"):
        t["transaction_date"] = t["transaction_date"][:16]

    accs, cards = db.get_user_accounts(current_user.id), db.get_user_cards(current_user.id)
    return render_template_string(
        tpl.BASE_LAYOUT.replace("{content_body}", tpl.TRANSACTION_FORM_PAGE),
        t=t,
        accounts=accs,
        cards=cards,
        now=datetime.now().strftime("%Y-%m-%dT%H:%M"),
    )


@web_bp.route("/transaction/delete/<id>", methods=["POST"])
@login_required
def delete_transaction_route(id):
    ws.validate_csrf()
    if db.delete_transaction(id, current_user.id):
        flash("Removido.")
    else:
        flash("Erro.")
    return redirect(url_for("web.list_transactions"))


@web_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    ws.validate_csrf()
    logout_user()
    return redirect(url_for("web.login"))
