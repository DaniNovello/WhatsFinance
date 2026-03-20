"""Schema único de entendimento de mensagens (Zenith)."""

CONFIRM_THRESHOLD = 0.78  # abaixo: pedir confirmação antes de gravar (se demais campos ok)
AUTO_SAVE_MIN_CONFIDENCE = 0.88  # comprovante/imagem: exige mais certeza para pular confirmação

CRITICAL_TXN_FIELDS = ("amount", "transaction_type")


def empty_result() -> dict:
    return {
        "intent": "unknown",
        "transaction_type": "",
        "amount": None,
        "description": "",
        "category": "",
        "payment_method": "",
        "account_name": "",
        "card_name": "",
        "installment_count": None,
        "date": "",
        "time_period": "",
        "confidence": 0.0,
        "missing_fields": [],
        "needs_confirmation": False,
        "source": "none",  # heuristic | llm | merged
    }
