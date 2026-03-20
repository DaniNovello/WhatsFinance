"""
Entrada multimodal: interfaces plugáveis para áudio e imagem.

- Sem filas, sem microserviços, sem dependências novas obrigatórias.
- Por padrão: stubs (transcrição vazia, comprovante vazio).
- Expansão: registrar callables via set_transcriber / set_receipt_parser.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple, Union

logger = logging.getLogger(__name__)

PathLike = Union[str, Path]

# --- Hooks opcionais (testes ou integração futura: Whisper, OCR barato, etc.) ---
_Transcriber: Optional[Callable[[Path], str]] = None
_ReceiptParser: Optional[Callable[[Path], Dict[str, Any]]] = None


def set_transcriber(fn: Optional[Callable[[Path], str]]) -> None:
    """Define função que transcreve arquivo de áudio local. None = voltar ao stub."""
    global _Transcriber
    _Transcriber = fn


def set_receipt_parser(fn: Optional[Callable[[Path], Dict[str, Any]]]) -> None:
    """Define extrator de comprovante a partir de arquivo de imagem. None = stub."""
    global _ReceiptParser
    _ReceiptParser = fn


def transcribe_audio(file_path: PathLike) -> str:
    """
    Transcreve áudio em arquivo local → texto (PT-BR esperado).

    Stub: retorna string vazia até `set_transcriber` ou implementação futura.
    """
    p = Path(file_path)
    if not p.is_file():
        logger.warning("transcribe_audio: arquivo inexistente: %s", p)
        return ""
    if _Transcriber is not None:
        try:
            out = _Transcriber(p)
            return (out or "").strip()
        except Exception as e:
            logger.exception("transcribe_audio hook falhou: %s", e)
            return ""
    logger.debug("transcribe_audio (stub): %s", p)
    return ""


def parse_receipt_image(file_path: PathLike) -> Dict[str, Any]:
    """
    Extrai dados estruturados de comprovante/imagem (schema Zenith).

    Stub: retorna dict vazio normalizado até `set_receipt_parser` ou OCR dedicado.
    Quando implementado, o retorno deve ser compatível com `intent_normalize.normalize_llm_dict`.
    """
    p = Path(file_path)
    if not p.is_file():
        from .structured_schema import empty_result

        return empty_result()
    if _ReceiptParser is not None:
        try:
            raw = _ReceiptParser(p)
            if isinstance(raw, dict):
                from .intent_normalize import normalize_llm_dict

                return normalize_llm_dict(raw, source="receipt_hook")
        except Exception as e:
            logger.exception("parse_receipt_image hook falhou: %s", e)
    from .structured_schema import empty_result

    logger.debug("parse_receipt_image (stub): %s", p)
    return empty_result()


def resolve_multimodal_inputs(
    text: str = "",
    *,
    image_bytes: Optional[bytes] = None,
    image_path: Optional[PathLike] = None,
    audio_path: Optional[PathLike] = None,
) -> Tuple[str, Optional[bytes], Dict[str, Any]]:
    """
    Normaliza entradas opcionais para o pipeline textual existente.

    Retorna:
        (texto_combinado, bytes_da_imagem_ou_none, hint_comprovante)

    - Áudio: concatena transcrição ao texto (se houver).
    - Imagem: se não vier bytes mas vier path, lê bytes do disco.
    - hint_comprovante: resultado de `parse_receipt_image` quando há path;
      hoje é vazio (stub); no futuro pode ser mesclado ao resultado do LLM.
    """
    t = (text or "").strip()
    hint: Dict[str, Any] = {}

    if audio_path:
        ap = Path(audio_path)
        spoken = transcribe_audio(ap)
        if spoken:
            t = f"{t}\n{spoken}".strip() if t else spoken

    ib = image_bytes
    if image_path:
        ip = Path(image_path)
        if ip.is_file():
            hint = parse_receipt_image(ip)
            if ib is None:
                try:
                    ib = ip.read_bytes()
                except OSError as e:
                    logger.error("Falha ao ler imagem %s: %s", ip, e)

    return t, ib, hint


def receipt_hint_is_useful(hint: Dict[str, Any]) -> bool:
    """True se o hook de comprovante devolveu algo aplicável (stub retorna False)."""
    if not isinstance(hint, dict) or not hint:
        return False
    if hint.get("amount") is not None:
        return True
    if str(hint.get("description") or "").strip():
        return True
    if hint.get("intent") == "register_transaction" and hint.get("transaction_type"):
        return True
    return False


def merge_receipt_hint_into_structured(
    structured: Dict[str, Any], hint: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Mescla campos do hint OCR/comprovante quando o pipeline ainda não os preencheu.
    Só atua se o hint trouxer dados úteis (ex.: amount ou description).
    """
    if not hint:
        return structured
    amt = hint.get("amount")
    desc = (hint.get("description") or "").strip()
    if amt is None and not desc:
        return structured
    out = dict(structured)
    if amt is not None and out.get("amount") is None:
        out["amount"] = amt
    if desc and not (out.get("description") or "").strip():
        out["description"] = desc
    tt = hint.get("transaction_type")
    if tt and not out.get("transaction_type"):
        out["transaction_type"] = tt
    return out
