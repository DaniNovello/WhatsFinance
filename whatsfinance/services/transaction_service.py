"""
Mutações de transação + saldo de conta: um único caminho via RPCs do Postgres.
Leituras continuam em db.py.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from whatsfinance import db


def _rpc_insert_params(
    user_id: int | str,
    data: Dict[str, Any],
    *,
    transaction_date_iso: Optional[str] = None,
) -> Dict[str, Any]:
    acc = data.get("account_id")
    acc_id = int(acc) if acc not in (None, "", "None") else None
    card = data.get("card_id")
    card_id = int(card) if card not in (None, "", "None") else None
    raw_amt = data.get("amount")
    try:
        amount = float(raw_amt) if raw_amt is not None else None
    except (TypeError, ValueError):
        amount = None
    dt = transaction_date_iso or data.get("date")
    if dt is not None and hasattr(dt, "isoformat"):
        dt = dt.isoformat()
    return {
        "p_user_id": user_id,
        "p_description": data.get("description"),
        "p_amount": amount,
        "p_type": data.get("type"),
        "p_payment_method": data.get("payment_method"),
        "p_category": data.get("category"),
        "p_card_id": card_id,
        "p_account_id": acc_id,
        "p_transaction_date": dt,
    }


def insert_transaction(user_id: int | str, data: Dict[str, Any], *, transaction_date_iso: Optional[str] = None) -> bool:
    """Cria transação e aplica saldo na conta se houver account_id (RPC única)."""
    try:
        params = _rpc_insert_params(user_id, data, transaction_date_iso=transaction_date_iso)
        db.supabase.rpc("handle_transaction_and_update_balance", params).execute()
        return True
    except Exception:
        return False


def create_installments(user_id: int | str, data: Dict[str, Any], installments: int) -> bool:
    """Parcelas: cada parcela via mesma RPC (saldo/conta quando account_id vier no payload)."""
    try:
        from dateutil.relativedelta import relativedelta

        total = float(data.get("amount", 0))
        val = total / installments
        base_desc = data.get("description", "Compra")
        base_date = datetime.now()
        for i in range(installments):
            future = base_date + relativedelta(months=i)
            payload = {
                "user_id": user_id,
                "description": f"{base_desc} ({i + 1}/{installments})",
                "amount": val,
                "type": data.get("type"),
                "payment_method": data.get("payment_method"),
                "category": data.get("category"),
                "card_id": data.get("card_id"),
                "account_id": data.get("account_id"),
            }
            if not insert_transaction(user_id, payload, transaction_date_iso=future.isoformat()):
                return False
        return True
    except Exception:
        return False


def attach_transaction_to_account(user_id: int | str, transaction_id: int, account_id: int) -> bool:
    """
    Liga transação a uma conta e ajusta saldo usando a mesma RPC de edição
    (reverte conta antiga se houver, aplica na nova).
    """
    try:
        t = db.get_transaction(transaction_id, user_id)
        if not t:
            return False
        raw_date = t.get("transaction_date")
        p_date = None
        if raw_date is not None:
            p_date = raw_date if isinstance(raw_date, str) else str(raw_date)
        params = {
            "p_transaction_id": int(transaction_id),
            "p_user_id": user_id,
            "p_description": t["description"],
            "p_amount": float(t["amount"]),
            "p_type": t["type"],
            "p_payment_method": t.get("payment_method"),
            "p_category": t.get("category"),
            "p_account_id": int(account_id),
            "p_card_id": int(t["card_id"]) if t.get("card_id") is not None else None,
            "p_date": p_date,
        }
        db.supabase.rpc("update_transaction_and_balance", params).execute()
        return True
    except Exception:
        return False


def add_transaction_from_form(user_id: int | str, data: Dict[str, Any]) -> bool:
    """Formulário web: mesmo insert RPC (sem segundo update manual de saldo)."""
    payload = {
        "description": data["description"],
        "amount": float(data["amount"]),
        "type": data["type"],
        "payment_method": data["payment_method"],
        "category": data.get("category"),
        "card_id": data.get("card_id"),
        "account_id": data.get("account_id"),
    }
    return insert_transaction(user_id, payload, transaction_date_iso=data.get("date") or datetime.now().isoformat())


def update_transaction_from_form(user_id: int | str, t_id: str | int, data: Dict[str, Any]) -> bool:
    try:
        acc_id = int(data["account_id"]) if data.get("account_id") else None
        card_id = int(data["card_id"]) if data.get("card_id") else None
        params = {
            "p_transaction_id": int(t_id),
            "p_user_id": user_id,
            "p_description": data["description"],
            "p_amount": float(data["amount"]),
            "p_type": data["type"],
            "p_payment_method": data["payment_method"],
            "p_category": data.get("category"),
            "p_account_id": acc_id,
            "p_card_id": card_id,
            "p_date": data.get("date"),
        }
        db.supabase.rpc("update_transaction_and_balance", params).execute()
        return True
    except Exception:
        return False


def delete_transaction(user_id: int | str, transaction_id: str | int) -> bool:
    try:
        db.supabase.rpc(
            "delete_transaction_and_revert_balance",
            {"p_transaction_id": int(transaction_id), "p_user_id": user_id},
        ).execute()
        return True
    except Exception:
        return False
