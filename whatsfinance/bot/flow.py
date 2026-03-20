"""Fluxo pós-registro de transação (follow-up: método, cartão, conta)."""
from whatsfinance import conversation_state as conv, db

from . import keyboards
from .telegram_client import send_message


def trigger_save_and_continue(chat_id, entities):
    inst = entities.get("installments", 1)
    if isinstance(inst, int) and inst > 1:
        success = db.create_installments(chat_id, entities, inst)
    else:
        success = db.process_transaction_with_rpc(chat_id, entities)

    if not success:
        send_message(chat_id, "❌ Erro ao salvar no banco.")
        return

    conv.clear_all(chat_id)
    ask_follow_up_questions(chat_id, entities)


def ask_follow_up_questions(chat_id, transaction_data):
    tipo = transaction_data.get("type")
    pay = transaction_data.get("payment_method")
    val = transaction_data.get("amount")
    desc = transaction_data.get("description")

    if tipo == "expense" and not pay:
        send_message(
            chat_id,
            f"📝 Registrei *{desc}* (R${val}).\nQual foi a forma de pagamento?",
            reply_markup=keyboards.get_method_keyboard(),
        )
        return

    if pay == "credit_card":
        cards = db.get_user_cards(chat_id)
        if cards:
            kb = {
                "inline_keyboard": [
                    [{"text": f"💳 {c['name']}", "callback_data": f"sel_card_{c['id']}"}]
                    for c in cards
                ]
            }
            send_message(chat_id, "💳 Gasto no crédito. Em qual cartão?", reply_markup=kb)
        else:
            send_message(chat_id, "⚠️ Registrado (sem cartão cadastrado).")
        return

    if tipo == "income" or pay in ["debit_card", "pix", "money"]:
        accs = db.get_user_accounts(chat_id)
        if accs:
            action_text = "Entrou em" if tipo == "income" else "Saiu de"
            kb = {
                "inline_keyboard": [
                    [{"text": f"🏦 {a['name']}", "callback_data": f"sel_acc_{a['id']}"}]
                    for a in accs
                ]
            }
            send_message(chat_id, f"💰 {action_text} qual conta?", reply_markup=kb)
        else:
            send_message(chat_id, "✅ Registrado!")
        return

    send_message(chat_id, f"✅ *{desc}* (R${val}) registrado!")
