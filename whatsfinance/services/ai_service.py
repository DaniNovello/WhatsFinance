import logging
import os

from .llm_providers import get_llm_provider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Compat: leitura de modelo Gemini no .env (provedor Gemini usa internamente)
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")


def llm_parse_structured(user_text: str, image_bytes=None) -> dict:
    return get_llm_provider().parse_structured(user_text, image_bytes)


def get_financial_advice():
    return "💡 Dica Zenith: Revise suas faturas semanalmente para evitar surpresas!"
