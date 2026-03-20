"""Normaliza saída heurística/LLM, regras de missing_fields e confirmação."""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from .structured_schema import (
    AUTO_SAVE_MIN_CONFIDENCE,
    CONFIRM_THRESHOLD,
    CRITICAL_TXN_FIELDS,
    empty_result,
)

VALID_INTENTS = frozenset({"register_transaction", "query_report", "greeting", "unknown"})
VALID_TYPES = frozenset({"expense", "income", ""})
VALID_PAYMENT = frozenset({"", "debit_card", "credit_card", "pix", "money"})
VALID_PERIODS = frozenset({"", "this_week", "last_week", "this_month"})


def _clamp_confidence(v: Any) -> float:
    try:
        x = float(v)
        return max(0.0, min(1.0, x))
    except (TypeError, ValueError):
        return 0.0


def _coerce_amount(v: Any) -> Optional[float]:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v) if v >= 0 else None
    if isinstance(v, str):
        s = v.strip().replace("R$", "").replace(" ", "")
        if not s:
            return None
        try:
            if "," in s and "." in s:
                s = s.replace(".", "").replace(",", ".")
            elif "," in s:
                parts = s.split(",")
                if len(parts) == 2 and len(parts[1]) <= 2:
                    s = parts[0].replace(".", "") + "." + parts[1]
                else:
                    s = s.replace(",", ".")
            return float(s)
        except ValueError:
            return None
    return None


def _coerce_installments(v: Any) -> Optional[int]:
    if v is None:
        return None
    try:
        n = int(v)
        if 2 <= n <= 48:
            return n
    except (TypeError, ValueError):
        pass
    return None


def normalize_llm_dict(raw: Dict[str, Any], source: str = "llm") -> Dict[str, Any]:
    """Garante chaves do schema e tipos seguros."""
    out = empty_result()
    if not isinstance(raw, dict):
        out["source"] = source
        return out

    intent = str(raw.get("intent", "unknown")).strip()
    out["intent"] = intent if intent in VALID_INTENTS else "unknown"

    tt = str(raw.get("transaction_type", "")).strip()
    out["transaction_type"] = tt if tt in VALID_TYPES else ""

    out["amount"] = _coerce_amount(raw.get("amount"))
    out["description"] = str(raw.get("description", "") or "").strip()[:500]
    out["category"] = str(raw.get("category", "") or "").strip()[:120]
    pm = str(raw.get("payment_method", "") or "").strip()
    out["payment_method"] = pm if pm in VALID_PAYMENT else ""
    out["account_name"] = str(raw.get("account_name", "") or "").strip()[:120]
    out["card_name"] = str(raw.get("card_name", "") or "").strip()[:120]
    out["installment_count"] = _coerce_installments(
        raw.get("installment_count", raw.get("installments"))
    )
    out["date"] = str(raw.get("date", "") or "").strip()[:32]
    tp = str(raw.get("time_period", "") or "").strip()
    out["time_period"] = tp if tp in VALID_PERIODS else ("this_week" if out["intent"] == "query_report" else "")

    out["confidence"] = _clamp_confidence(raw.get("confidence", 0.7))
    mf = raw.get("missing_fields")
    if isinstance(mf, list):
        out["missing_fields"] = [str(x) for x in mf if isinstance(x, str)][:20]
    out["needs_confirmation"] = bool(raw.get("needs_confirmation", False))
    out["source"] = source
    return out


def merge_heuristic_and_llm(h_partial: Dict[str, Any], llm_norm: Dict[str, Any]) -> Dict[str, Any]:
    """Combina dicas da heurística com o JSON do LLM."""
    out = dict(llm_norm)

    if h_partial.get("source") == "heuristic_partial":
        if h_partial.get("_hint_expense"):
            out["transaction_type"] = out.get("transaction_type") or "expense"
        elif h_partial.get("_hint_income"):
            out["transaction_type"] = out.get("transaction_type") or "income"
        if out.get("intent") == "unknown" and (out.get("amount") is not None or out.get("transaction_type")):
            out["intent"] = "register_transaction"
        out["source"] = "merged"
        out["confidence"] = max(out.get("confidence", 0), 0.55)
        return out

    if h_partial.get("source") == "heuristic" and h_partial.get("intent") == "register_transaction":
        if h_partial.get("amount") is not None:
            out["amount"] = h_partial["amount"]
        if h_partial.get("transaction_type"):
            out["transaction_type"] = h_partial["transaction_type"]
        if h_partial.get("installment_count") and not out.get("installment_count"):
            out["installment_count"] = h_partial["installment_count"]
        if h_partial.get("description") and not out.get("description"):
            out["description"] = h_partial["description"]
        out["source"] = "merged"
        out["confidence"] = max(out.get("confidence", 0), h_partial.get("confidence", 0) * 0.95)
    return out


def apply_confirmation_rules(result: Dict[str, Any], *, had_image: bool) -> Dict[str, Any]:
    """Ajusta missing_fields, needs_confirmation e confidence após normalizar."""
    intent = result.get("intent")
    missing: List[str] = list(result.get("missing_fields") or [])

    if intent == "register_transaction":
        if result.get("amount") is None:
            missing.append("amount")
        if not result.get("transaction_type"):
            missing.append("transaction_type")
        if not result.get("description"):
            missing.append("description")  # informativo; fluxo do bot pede texto em outro passo

    seen = set()
    result["missing_fields"] = [x for x in missing if x not in seen and not seen.add(x)]

    crit = [f for f in CRITICAL_TXN_FIELDS if f in result["missing_fields"]]
    if crit:
        result["needs_confirmation"] = True
        result["confidence"] = min(result.get("confidence", 0), 0.55)

    thr = AUTO_SAVE_MIN_CONFIDENCE if had_image else CONFIRM_THRESHOLD
    if intent == "register_transaction" and not crit:
        if result.get("confidence", 0) < thr:
            result["needs_confirmation"] = True
        if result.get("installment_count") and result.get("installment_count", 0) > 1:
            result["needs_confirmation"] = True

    return result


def to_flow_entities(result: Dict[str, Any]) -> Dict[str, Any]:
    """Formato esperado por trigger_save_and_continue / db."""
    inst = result.get("installment_count")
    installments = inst if isinstance(inst, int) and inst > 1 else 1
    desc = result.get("description") or "Lançamento"
    return {
        "type": result.get("transaction_type") or "expense",
        "amount": result.get("amount"),
        "description": desc,
        "payment_method": result.get("payment_method") or None,
        "category": result.get("category") or "Geral",
        "card_id": None,
        "installments": installments,
        "payer_name": None,
        "payee_name": None,
    }


def format_confirmation_summary(result: Dict[str, Any]) -> str:
    t = result.get("transaction_type") or "?"
    amt = result.get("amount")
    d = result.get("description") or "—"
    cat = result.get("category") or "Geral"
    inst = result.get("installment_count")
    extra = f"\n📎 {inst}x parcelas" if inst and inst > 1 else ""
    tipo = "Saída" if t == "expense" else "Entrada" if t == "income" else t
    return (
        f"📋 *Confirma este lançamento?*\n\n"
        f"*{tipo}* — {d}\n"
        f"💰 R$ {amt}\n"
        f"🏷 {cat}{extra}\n\n"
        f"_Confiança: {result.get('confidence', 0):.0%}_"
    )


def extract_json_object(text: str) -> Optional[dict]:
    """Extrai JSON de resposta que às vezes vem com markdown."""
    if not text:
        return None
    t = text.strip()
    m = re.search(r"\{[\s\S]*\}", t)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
