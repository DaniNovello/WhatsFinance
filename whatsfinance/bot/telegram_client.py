"""Envio de mensagens e download de mídia via API HTTP do Telegram."""
import logging
import os
import tempfile
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        r = requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
        if r.status_code != 200:
            logger.error("Erro Telegram: %s", r.text)
    except Exception as e:
        logger.error("Erro request: %s", e)


def answer_callback_query(callback_query_id):
    try:
        requests.post(
            f"{TELEGRAM_API_URL}/answerCallbackQuery",
            json={"callback_query_id": callback_query_id},
        )
    except Exception as e:
        logger.error("answerCallbackQuery: %s", e)


def download_file_bytes(file_id: str) -> Optional[bytes]:
    """Baixa qualquer arquivo pelo file_id (foto, voz, documento). Retorna bytes ou None."""
    if not TELEGRAM_TOKEN or not file_id:
        return None
    try:
        meta = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile",
            params={"file_id": file_id},
            timeout=30,
        ).json()
        path = meta["result"]["file_path"]
        return requests.get(
            f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{path}",
            timeout=60,
        ).content
    except Exception as e:
        logger.error("Erro download arquivo: %s", e)
        return None


def download_photo_bytes(file_id):
    """Compat: foto → bytes (usa download genérico)."""
    return download_file_bytes(file_id)


def download_file_to_temp(file_id: str, suffix: str = ".bin") -> Optional[Path]:
    """
    Baixa arquivo do Telegram para um tempfile (útil para áudio antes de transcrição plugável).
    Quem chama deve apagar o path após uso.
    """
    data = download_file_bytes(file_id)
    if not data:
        return None
    fd, name = tempfile.mkstemp(suffix=suffix)
    try:
        os.write(fd, data)
        return Path(name)
    finally:
        os.close(fd)
