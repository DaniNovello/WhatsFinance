"""
Provedores LLM plugáveis — texto estruturado (JSON) para o pipeline de intenção.

- **gemini** (padrão): Google Generative AI; camada gratuita em https://ai.google.dev
- **openai_compatible**: qualquer API estilo OpenAI (ex.: **Groq** gratuito, OpenRouter com créditos free).

Imagens: só Gemini implementa visão aqui; em `openai_compatible` a imagem é ignorada com aviso
(a menos que você estenda este módulo com multimodal no mesmo formato da API).
"""
from __future__ import annotations

import io
import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import requests

from .intent_normalize import extract_json_object, normalize_llm_dict
from .llm_prompts import ZENITH_PARSER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    name: str = "base"

    def supports_vision(self) -> bool:
        return False

    @abstractmethod
    def parse_structured(self, user_text: str, image_bytes: Optional[bytes] = None) -> Dict[str, Any]:
        ...


class GeminiProvider(BaseLLMProvider):
    name = "gemini"

    def __init__(self) -> None:
        import google.generativeai as genai
        from PIL import Image

        self._genai = genai
        self._Image = Image
        key = os.environ.get("GEMINI_API_KEY", "").strip()
        if key:
            genai.configure(api_key=key)
        self._model_name = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
        self._generation_config = {
            "temperature": 0.15,
            "response_mime_type": "application/json",
        }

    def supports_vision(self) -> bool:
        return True

    def parse_structured(self, user_text: str, image_bytes: Optional[bytes] = None) -> Dict[str, Any]:
        user_text = (user_text or "").strip()[:2000]
        prompt = f'{ZENITH_PARSER_SYSTEM_PROMPT}\n"""{user_text}"""'
        content: list = [prompt]
        if image_bytes:
            try:
                content.append(self._Image.open(io.BytesIO(image_bytes)))
            except Exception as e:
                logger.error("Erro imagem (Gemini): %s", e)

        model = self._genai.GenerativeModel(self._model_name, generation_config=self._generation_config)
        try:
            response = model.generate_content(content)
            try:
                raw_text = response.text or ""
            except ValueError:
                raw_text = str(response)
            parsed = extract_json_object(raw_text)
            if not parsed:
                parsed = {}
            return normalize_llm_dict(parsed, source="llm")
        except Exception as e:
            logger.error("Erro LLM (Gemini): %s", e)
            return normalize_llm_dict({}, source="llm")


class OpenAICompatibleProvider(BaseLLMProvider):
    """
    Chat Completions API (OpenAI format). Ex.: Groq — https://console.groq.com (tier gratuito).

    Env:
      LLM_PROVIDER=openai_compatible
      OPENAI_COMPATIBLE_BASE_URL=https://api.groq.com/openai/v1
      OPENAI_COMPATIBLE_API_KEY=...
      OPENAI_COMPATIBLE_MODEL=llama-3.1-8b-instant
    """

    name = "openai_compatible"

    def __init__(self) -> None:
        self._base = (
            os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
        )
        self._key = os.environ.get("OPENAI_COMPATIBLE_API_KEY", "").strip()
        self._model = os.environ.get("OPENAI_COMPATIBLE_MODEL", "llama-3.1-8b-instant").strip()

    def parse_structured(self, user_text: str, image_bytes: Optional[bytes] = None) -> Dict[str, Any]:
        if image_bytes:
            logger.warning(
                "[%s] Imagem recebida mas visão não implementada para este provedor — use LLM_PROVIDER=gemini para fotos.",
                self.name,
            )
        user_text = (user_text or "").strip()[:2000]
        if not self._key:
            logger.error("OPENAI_COMPATIBLE_API_KEY não definida.")
            return normalize_llm_dict({}, source="llm")

        url = f"{self._base}/chat/completions"
        payload = {
            "model": self._model,
            "temperature": 0.15,
            "messages": [
                {"role": "system", "content": ZENITH_PARSER_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f'Extraia o JSON conforme o schema. Mensagem:\n"""{user_text}"""',
                },
            ],
        }
        try:
            r = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {self._key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60,
            )
            r.raise_for_status()
            data = r.json()
            raw_text = (data.get("choices") or [{}])[0].get("message", {}).get("content") or ""
            parsed = extract_json_object(raw_text)
            if not parsed:
                parsed = {}
            return normalize_llm_dict(parsed, source="llm")
        except Exception as e:
            logger.error("Erro LLM (%s): %s", self.name, e)
            return normalize_llm_dict({}, source="llm")


def get_llm_provider() -> BaseLLMProvider:
    """Escolhe provedor por LLM_PROVIDER (default: gemini)."""
    p = os.environ.get("LLM_PROVIDER", "gemini").strip().lower()
    if p in ("openai_compatible", "groq", "openai"):
        return OpenAICompatibleProvider()
    return GeminiProvider()
