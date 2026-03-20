"""Estado conversacional do bot (Supabase: bot_conversation_state)."""
import copy

from whatsfinance import db


def _row(chat_id):
    return db.bot_conversation_get(chat_id)


def has_buffer(chat_id):
    r = _row(chat_id)
    return r is not None and r.get("payload_json") is not None


def has_state(chat_id):
    r = _row(chat_id)
    return r is not None and bool(r.get("current_state"))


def get_buffer(chat_id):
    r = _row(chat_id)
    if not r or r.get("payload_json") is None:
        return None
    return copy.deepcopy(r["payload_json"])


def get_current_state(chat_id):
    r = _row(chat_id)
    return r.get("current_state") if r else None


def get_pending_intent(chat_id):
    r = _row(chat_id)
    return r.get("pending_intent") if r else None


def put_buffer(chat_id, payload_dict):
    r = _row(chat_id) or {}
    db.bot_conversation_replace(
        chat_id,
        r.get("current_state"),
        r.get("pending_intent"),
        payload_dict,
    )


def put_state(chat_id, state):
    r = _row(chat_id) or {}
    db.bot_conversation_replace(chat_id, state, r.get("pending_intent"), r.get("payload_json"))


def put_intent(chat_id, intent):
    r = _row(chat_id) or {}
    db.bot_conversation_replace(chat_id, r.get("current_state"), intent, r.get("payload_json"))


def replace(chat_id, current_state, pending_intent, payload_json):
    """Atualiza os três campos de uma vez. payload_json None = sem buffer."""
    db.bot_conversation_replace(chat_id, current_state, pending_intent, payload_json)


def clear_all(chat_id):
    db.bot_conversation_delete(chat_id)
