"""
Regras leves (sem API) para cumprimentos, relatórios e transações óbvias.
Retorna dict parcial + flag use_llm se precisar do modelo.
"""
from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple

from .structured_schema import empty_result


def _br_amount(text: str) -> Optional[float]:
    """Extrai primeiro valor monetário comum em PT-BR."""
    t = text.replace("R$", " ").replace("RS", " ").replace("reais", " ")
    # 10x de 100 -> skip installment for amount parent - handle separately
    patterns = [
        r"(\d{1,3}(?:\.\d{3})+,\d{2})",  # 1.234,56
        r"(\d+,\d{2})\b",  # 50,90
        r"\b(\d+(?:\.\d{2})?)\s*(?:reais|r\$)?",  # 50 or 50.5
    ]
    for pat in patterns:
        m = re.search(pat, t, re.IGNORECASE)
        if not m:
            continue
        raw = m.group(1)
        try:
            if "," in raw and "." in raw:
                raw = raw.replace(".", "").replace(",", ".")
            elif "," in raw:
                parts = raw.split(",")
                if len(parts) == 2 and len(parts[1]) <= 2:
                    raw = parts[0].replace(".", "") + "." + parts[1]
                else:
                    raw = raw.replace(",", ".")
            return float(raw)
        except ValueError:
            continue
    m2 = re.search(r"\b(\d+)\b", t)
    if m2:
        try:
            v = float(m2.group(1))
            if 1 <= v <= 999999:
                return v
        except ValueError:
            pass
    return None


def _installments(text: str) -> Optional[int]:
    m = re.search(r"(\d{1,2})\s*x\b", text, re.IGNORECASE)
    if m:
        n = int(m.group(1))
        if 2 <= n <= 48:
            return n
    return None


def _description_guess(text: str, kind: str) -> str:
    t = text.strip()
    if len(t) > 80:
        return t[:77] + "..."
    return t or ("Entrada" if kind == "income" else "Despesa")


def parse(text: str) -> Tuple[Dict[str, Any], bool]:
    """
    Retorna (partial_dict, use_llm).
    partial_dict pode ser mesclado com empty_result().
    """
    if not text or not text.strip():
        return {}, True

    raw = text.strip()
    low = raw.lower()

    # --- Saudação / ajuda ---
    if len(low) <= 2:
        r = empty_result()
        r.update(intent="greeting", confidence=0.95, source="heuristic", needs_confirmation=False)
        return r, False

    greet = re.match(
        r"^(oi|olá|ola|hey|e aí|eai|bom dia|boa tarde|boa noite|menu|ajuda|help|start)\b",
        low,
    )
    if greet and len(low) < 40:
        r = empty_result()
        r.update(intent="greeting", confidence=0.92, source="heuristic", needs_confirmation=False)
        return r, False

    # --- Relatório ---
    if re.search(r"relat[oó]rio|extrato|resumo|quanto\s+(gastei|paguei)|gastos?\s+da", low):
        period = "this_week"
        if "mês" in low or "mes" in low or "mês atual" in low:
            period = "this_month"
        elif "semana passada" in low or "última semana" in low or "ultima semana" in low:
            period = "last_week"
        elif "esta semana" in low or "essa semana" in low or "semana" in low:
            period = "this_week"
        r = empty_result()
        r.update(
            intent="query_report",
            time_period=period,
            confidence=0.88,
            source="heuristic",
            needs_confirmation=False,
        )
        return r, False

    # --- Transação: palavras-chave + valor ---
    expense_kw = r"gastei|paguei|comprei|debit(?:ei|ar)|investi|saí|said|despesa"
    income_kw = r"recebi|ganhei|entrada|sal[aá]rio|cr[eé]dito\s+recebido|pix\s+recebido|dep[oó]sito"

    is_exp = re.search(expense_kw, low)
    is_inc = re.search(income_kw, low)

    amt = _br_amount(raw)
    inst = _installments(raw)

    if (is_exp or is_inc) and amt is not None:
        kind = "expense" if is_exp and not is_inc else "income" if is_inc and not is_exp else ("expense" if is_exp else "income")
        r = empty_result()
        r.update(
            intent="register_transaction",
            transaction_type=kind,
            amount=amt,
            description=_description_guess(raw, kind),
            category="Geral",
            payment_method="",
            installment_count=inst,
            confidence=0.86 if not inst else 0.82,
            source="heuristic",
            needs_confirmation=False,
        )
        # parcela sem descrição clara: pedir confirmação leve
        if inst:
            r["needs_confirmation"] = True
            r["confidence"] = min(r["confidence"], 0.74)
        return r, False

    # Transação provável mas sem valor → LLM
    if is_exp or is_inc:
        return {"_hint_expense": bool(is_exp), "_hint_income": bool(is_inc), "source": "heuristic_partial"}, True

    # Nada claro
    return {}, True
