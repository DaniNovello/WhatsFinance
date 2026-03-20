"""
Segurança mínima: CSRF por sessão, validação de inputs, constantes de auth.
"""
from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple

from flask import abort, session

CSRF_SESSION_KEY = "_csrf_token"

VERIFICATION_CODE_TTL_MINUTES = 15
VERIFICATION_MAX_ATTEMPTS = 5
MIN_PASSWORD_LENGTH = 8
MAX_TELEGRAM_ID_LEN = 16
MIN_TELEGRAM_ID_LEN = 5
MAX_DESCRIPTION_LEN = 500
MAX_AMOUNT = 1_000_000_000.0  # limite pragmático
MAX_SEARCH_LEN = 200


def get_csrf_token() -> str:
    import secrets

    if CSRF_SESSION_KEY not in session:
        session[CSRF_SESSION_KEY] = secrets.token_hex(16)
    return session[CSRF_SESSION_KEY]


def validate_csrf() -> None:
    from flask import request

    sent = request.form.get("csrf_token")
    if not sent or sent != session.get(CSRF_SESSION_KEY):
        abort(400)


def normalize_telegram_id(raw: Any) -> Optional[str]:
    if raw is None:
        return None
    s = str(raw).strip()
    if not s.isdigit():
        return None
    if not (MIN_TELEGRAM_ID_LEN <= len(s) <= MAX_TELEGRAM_ID_LEN):
        return None
    return s


def validate_new_password(pwd: Any) -> Tuple[bool, str]:
    if pwd is None or not isinstance(pwd, str):
        return False, "Senha inválida."
    if len(pwd) < MIN_PASSWORD_LENGTH:
        return False, f"Senha deve ter pelo menos {MIN_PASSWORD_LENGTH} caracteres."
    if len(pwd) > 256:
        return False, "Senha muito longa."
    return True, ""


def validate_transaction_form(data: Dict[str, Any]) -> Tuple[bool, str]:
    t = data.get("type")
    if t not in ("income", "expense"):
        return False, "Tipo de lançamento inválido."
    desc = (data.get("description") or "").strip()
    if not desc or len(desc) > MAX_DESCRIPTION_LEN:
        return False, "Descrição inválida."
    try:
        amt = float(data.get("amount"))
    except (TypeError, ValueError):
        return False, "Valor inválido."
    if amt <= 0 or amt > MAX_AMOUNT:
        return False, "Valor fora do intervalo permitido."
    pm = data.get("payment_method")
    if pm not in ("debit_card", "credit_card", "pix", "money"):
        return False, "Método de pagamento inválido."
    return True, ""


def sanitize_search_filter(filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not filters:
        return {}
    out = dict(filters)
    s = out.get("search")
    if s and isinstance(s, str) and len(s) > MAX_SEARCH_LEN:
        out["search"] = s[:MAX_SEARCH_LEN]
    return out
