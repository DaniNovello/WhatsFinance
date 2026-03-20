"""Compat: IA e pipeline de intenção."""
from whatsfinance.services.ai_service import get_financial_advice
from whatsfinance.services.intent_pipeline import (
    to_legacy_bot_format,
    understand_multimodal,
    understand_user_message,
)


def get_ai_response(message_text, image_bytes=None):
    """Formato legado intent + entities (+ _structured com schema completo)."""
    r = understand_user_message(message_text or "", image_bytes)
    return to_legacy_bot_format(r)


__all__ = ["get_ai_response", "get_financial_advice", "understand_multimodal", "understand_user_message"]
