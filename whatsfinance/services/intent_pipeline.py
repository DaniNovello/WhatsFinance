"""
Orquestração: heurística primeiro, LLM só quando necessário.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Union

from . import heuristic_parser
from .intent_normalize import apply_confirmation_rules, merge_heuristic_and_llm
from .ai_service import llm_parse_structured


def understand_multimodal(
    text: str = "",
    *,
    image_bytes: Optional[bytes] = None,
    image_path: Optional[Union[str, Path]] = None,
    audio_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Mesmo pipeline que `understand_user_message`, com resolução opcional de path de áudio/imagem.

    Use quando tiver arquivos locais (ex.: voz baixada do Telegram). Mantém compatibilidade
    com o fluxo atual: texto + bytes de imagem → heurística/LLM como antes.
    """
    from .multimodal_input import (
        merge_receipt_hint_into_structured,
        receipt_hint_is_useful,
        resolve_multimodal_inputs,
    )

    t, ib, hint = resolve_multimodal_inputs(
        text,
        image_bytes=image_bytes,
        image_path=image_path,
        audio_path=audio_path,
    )
    result = understand_user_message(t, ib)
    if receipt_hint_is_useful(hint):
        merged = merge_receipt_hint_into_structured(result, hint)
        merged["had_image"] = result.get("had_image", bool(ib))
        had_img = bool(ib) or (image_path is not None)
        return apply_confirmation_rules(merged, had_image=had_img)
    return result


def understand_user_message(text: str, image_bytes: Optional[bytes] = None) -> Dict[str, Any]:
    had_image = bool(image_bytes)

    def _tag(result: Dict[str, Any]) -> Dict[str, Any]:
        result["had_image"] = had_image
        return result

    if had_image:
        raw_llm = llm_parse_structured(text or "Comprovante em imagem.", image_bytes)
        merged = dict(raw_llm)
        merged["source"] = "llm"
        return _tag(apply_confirmation_rules(merged, had_image=True))

    partial, use_llm = heuristic_parser.parse(text or "")

    if not use_llm and partial.get("intent") not in (None, "unknown"):
        base = dict(partial)
        return _tag(apply_confirmation_rules(base, had_image=False))

    llm_norm = llm_parse_structured(text, None)

    if partial.get("source") == "heuristic_partial":
        merged = merge_heuristic_and_llm(partial, llm_norm)
    elif partial:
        merged = merge_heuristic_and_llm(partial, llm_norm)
    else:
        merged = dict(llm_norm)

    return _tag(apply_confirmation_rules(merged, had_image=False))


def to_legacy_bot_format(result: Dict[str, Any]) -> Dict[str, Any]:
    """Formato esperado por fluxos antigos: intent + entities."""
    intent = result.get("intent") or "unknown"
    entities: Dict[str, Any] = {}
    if intent == "query_report":
        entities["time_period"] = result.get("time_period") or "this_week"
    elif intent == "register_transaction":
        entities = {
            "amount": result.get("amount"),
            "type": result.get("transaction_type"),
            "description": (result.get("description") or "").strip(),
            "category": result.get("category"),
            "payment_method": result.get("payment_method") or None,
            "installments": result.get("installment_count") or 1,
            "payer_name": None,
            "payee_name": None,
        }
    return {"intent": intent, "entities": entities, "_structured": result}


def should_auto_persist_transaction(result: Dict[str, Any]) -> bool:
    if result.get("intent") != "register_transaction":
        return False
    if result.get("needs_confirmation"):
        return False
    if result.get("missing_fields"):
        mf = set(result["missing_fields"])
        if mf & {"amount", "transaction_type"}:
            return False
        if "description" in mf:
            return False
    return True
