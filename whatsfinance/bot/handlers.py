"""Webhook Telegram: callbacks e mensagens (texto/imagem)."""
import logging

from whatsfinance import commands, conversation_state as conv, db
from whatsfinance.services.intent_normalize import (
    apply_confirmation_rules,
    format_confirmation_summary,
    to_flow_entities,
)
from whatsfinance.services.intent_pipeline import (
    should_auto_persist_transaction,
    to_legacy_bot_format,
    understand_multimodal,
)

from . import keyboards
from .flow import ask_follow_up_questions, trigger_save_and_continue
from .telegram_client import (
    answer_callback_query,
    download_file_to_temp,
    download_photo_bytes,
    send_message,
)

logger = logging.getLogger(__name__)


def _save_entities_from_buffer(buf: dict) -> dict:
    """Remove metadados do buffer antes de gravar no banco."""
    return {k: v for k, v in buf.items() if k != "_structured"}


def _offer_confirm_or_save(chat_id, structured: dict) -> None:
    """Grava direto se política permitir; senão pede confirmação inline."""
    fe = to_flow_entities(structured)
    if should_auto_persist_transaction(structured):
        trigger_save_and_continue(chat_id, fe)
        return
    buf = dict(fe)
    buf["_structured"] = structured
    conv.replace(chat_id, "awaiting_txn_confirm", "register_transaction", buf)
    send_message(
        chat_id,
        format_confirmation_summary(structured),
        reply_markup=keyboards.get_transaction_confirm_keyboard(),
    )


def handle_telegram_update(data):
    if not data:
        return "OK", 200

    if "callback_query" in data:
        return _handle_callback(data["callback_query"])

    if "message" in data:
        return _handle_message(data["message"])

    return "OK", 200


def _handle_callback(cb):
    chat_id = cb["message"]["chat"]["id"]
    raw_data = cb["data"]
    if not db.get_user(chat_id):
        db.create_user(chat_id, cb.get("from", {}).get("first_name", "User"))
    answer_callback_query(cb["id"])

    if raw_data == "txn_confirm_yes":
        if conv.has_buffer(chat_id):
            buf = conv.get_buffer(chat_id)
            trigger_save_and_continue(chat_id, _save_entities_from_buffer(buf))
        else:
            send_message(chat_id, "⚠️ Sessão expirada.")
        return "OK", 200

    if raw_data == "txn_confirm_no":
        conv.clear_all(chat_id)
        send_message(chat_id, "Lançamento cancelado.")
        return "OK", 200

    if raw_data.startswith("set_type_"):
        new_type = "income" if "income" in raw_data else "expense"
        if conv.has_buffer(chat_id):
            ents = conv.get_buffer(chat_id)
            ents["type"] = new_type

            payer = ents.get("payer_name")
            payee = ents.get("payee_name")
            final_desc = payee if new_type == "expense" and payee else payer
            if final_desc:
                ents["description"] = final_desc

            desc = ents.get("description")
            if not desc or desc.lower() in ["none", "null"]:
                conv.replace(chat_id, "awaiting_description", "register_transaction", ents)
                send_message(
                    chat_id,
                    f"ok, é uma {('Entrada' if new_type == 'income' else 'Saída')}.\nMas qual o nome da descrição?",
                )
            else:
                struct = ents.get("_structured")
                if struct:
                    struct = dict(struct)
                    struct["transaction_type"] = new_type
                    struct["description"] = desc
                    struct = apply_confirmation_rules(
                        struct, had_image=bool(struct.get("had_image"))
                    )
                    _offer_confirm_or_save(chat_id, struct)
                else:
                    conv.put_buffer(chat_id, ents)
                    trigger_save_and_continue(chat_id, ents)
        else:
            send_message(chat_id, "⚠️ Sessão expirada.")
        return "OK", 200

    if raw_data.startswith("sel_acc_"):
        acc_id = int(raw_data.split("_")[2])
        last = db.get_last_transactions(chat_id, 1)
        if last:
            db.update_transaction_account(last[0]["id"], acc_id, chat_id)
            send_message(chat_id, "✅ Saldo atualizado!")
        return "OK", 200

    if raw_data.startswith("sel_card_"):
        card_id = int(raw_data.split("_")[2])
        last = db.get_last_transactions(chat_id, 1)
        if last:
            db.update_transaction_card(last[0]["id"], card_id)
            send_message(chat_id, "✅ Fatura atualizada!")
        return "OK", 200

    if raw_data.startswith("set_method_"):
        method = raw_data.replace("set_method_", "")
        last = db.get_last_transactions(chat_id, 1)
        if last:
            db.update_transaction_method(last[0]["id"], method)
            trans_data = last[0]
            trans_data["payment_method"] = method
            ask_follow_up_questions(chat_id, trans_data)
        return "OK", 200

    if raw_data == "/menu":
        send_message(chat_id, "🤖 *Menu Principal*", reply_markup=keyboards.get_main_menu_keyboard())
    elif raw_data == "menu_relatorios":
        send_message(chat_id, "📊 *Relatórios*", reply_markup=keyboards.get_reports_keyboard())
    elif raw_data == "menu_config":
        send_message(chat_id, "⚙️ *Configurações*", reply_markup=keyboards.get_config_keyboard())
    elif raw_data == "/saldo":
        send_message(chat_id, commands.handle_command("saldo", chat_id))
    elif raw_data == "/ultimos":
        send_message(chat_id, commands.handle_command("ultimos", chat_id))
    elif raw_data == "btn_new_account":
        conv.put_state(chat_id, "awaiting_account_name")
        send_message(chat_id, "🏦 Qual o nome do banco?")
    elif raw_data == "btn_new_card":
        conv.replace(chat_id, "awaiting_card_name", None, {})
        send_message(chat_id, "💳 Qual o nome do cartão?")
    else:
        send_message(chat_id, commands.handle_command(raw_data, chat_id))

    return "OK", 200


def _handle_message(msg):
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "").strip()

    if not db.get_user(chat_id):
        db.create_user(chat_id, msg["from"].get("first_name", "User"))

    if conv.has_state(chat_id):
        state = conv.get_current_state(chat_id)
        if text == "/cancelar":
            conv.clear_all(chat_id)
            send_message(chat_id, "Cancelado.")
            return "OK", 200

        if state == "awaiting_txn_confirm":
            send_message(
                chat_id,
                "Use os botões *Confirmar* ou *Cancelar* na mensagem acima (ou envie /cancelar).",
            )
            return "OK", 200

        if state == "awaiting_description":
            if conv.has_buffer(chat_id):
                ents = conv.get_buffer(chat_id)
                ents["description"] = text.strip()
                struct = ents.get("_structured")
                if struct:
                    struct = dict(struct)
                    struct["description"] = ents["description"]
                    struct = apply_confirmation_rules(
                        struct, had_image=bool(struct.get("had_image"))
                    )
                    _offer_confirm_or_save(chat_id, struct)
                else:
                    conv.put_buffer(chat_id, ents)
                    trigger_save_and_continue(chat_id, ents)
            else:
                conv.clear_all(chat_id)
            return "OK", 200

        if state == "awaiting_account_name":
            db.create_account(chat_id, text)
            conv.clear_all(chat_id)
            send_message(
                chat_id,
                f"✅ Conta *{text}* criada!",
                reply_markup=keyboards.get_config_keyboard(),
            )
            return "OK", 200

        if state == "awaiting_card_name":
            conv.replace(chat_id, "awaiting_card_closing", None, {"name": text})
            send_message(chat_id, "📅 Fecha dia? (Digite apenas o número)")
            return "OK", 200

        if state == "awaiting_card_closing":
            if text.isdigit():
                ents = conv.get_buffer(chat_id) or {}
                ents["closing"] = int(text)
                conv.replace(chat_id, "awaiting_card_due", None, ents)
                send_message(chat_id, "📅 Vence dia? (Digite apenas o número)")
            else:
                send_message(chat_id, "⚠️ Digite um número válido.")
            return "OK", 200

        if state == "awaiting_card_due":
            if text.isdigit():
                d = conv.get_buffer(chat_id) or {}
                db.create_credit_card(chat_id, d["name"], d["closing"], int(text))
                conv.clear_all(chat_id)
                send_message(chat_id, "✅ Cartão criado!", reply_markup=keyboards.get_config_keyboard())
            else:
                send_message(chat_id, "⚠️ Digite um número válido.")
            return "OK", 200

    if text.strip() == "/menu":
        send_message(chat_id, "🤖 *Menu Principal*", reply_markup=keyboards.get_main_menu_keyboard())
        return "OK", 200

    initial_text = text
    had_voice = False
    audio_path = None
    if "voice" in msg:
        had_voice = True
        send_message(chat_id, "🎤 Processando áudio...")
        audio_path = download_file_to_temp(msg["voice"]["file_id"], suffix=".oga")
        if not audio_path:
            send_message(chat_id, "⚠️ Não consegui baixar o áudio.")

    image_bytes = None
    if "photo" in msg:
        f_id = msg["photo"][-1]["file_id"]
        image_bytes = download_photo_bytes(f_id)
        text = msg.get("caption", "")
        send_message(chat_id, "🔎 Analisando comprovante...")

    try:
        if text or image_bytes or audio_path:
            structured = understand_multimodal(
                text or "",
                image_bytes=image_bytes,
                audio_path=audio_path,
            )
            ai_data = to_legacy_bot_format(structured)
            intent = ai_data.get("intent") if ai_data else "unknown"
            entities = ai_data.get("entities", {})

            if intent == "register_transaction":
                buf = dict(entities)
                buf["_structured"] = structured

                if entities.get("amount") is None:
                    send_message(
                        chat_id,
                        "Não identifiquei o *valor*. Ex.: *gastei 45,90 no mercado* ou *recebi 200 de salário*.",
                    )
                    return "OK", 200

                if image_bytes and not entities.get("type"):
                    conv.replace(chat_id, None, "register_transaction", buf)
                    send_message(
                        chat_id,
                        f"🧾 Li um valor de R$ {entities.get('amount')}.\nIsso é *Entrada* ou *Saída*?",
                        reply_markup=keyboards.get_type_keyboard(),
                    )
                    return "OK", 200

                if not entities.get("type"):
                    conv.replace(chat_id, None, "register_transaction", buf)
                    send_message(
                        chat_id,
                        "É *Entrada* ou *Saída*?",
                        reply_markup=keyboards.get_type_keyboard(),
                    )
                    return "OK", 200

                if not entities.get("description"):
                    conv.replace(chat_id, "awaiting_description", "register_transaction", buf)
                    send_message(
                        chat_id,
                        f"💰 Valor R$ {entities.get('amount')}. Qual a *descrição* do lançamento?",
                    )
                    return "OK", 200

                _offer_confirm_or_save(chat_id, structured)

            elif intent == "query_report":
                report = commands.handle_command(
                    f"relatorio_{entities.get('time_period', 'this_week')}", chat_id
                )
                send_message(chat_id, report)

            else:
                # Só mostra mensagem de stub se a transcrição realmente
                # retornou vazio (o transcriber não está plugado de verdade).
                from whatsfinance.services.multimodal_input import transcribe_audio as _ta
                _transcriber_is_stub = (_ta.__module__ == "whatsfinance.services.multimodal_input" 
                                        and not getattr(_ta, "_is_real", False))
                if had_voice and not initial_text.strip() and not image_bytes:
                    # Verifica se o pipeline realmente não conseguiu transcrever
                    # checando se o resultado final é "unknown" sem nenhum dado útil
                    if intent in (None, "unknown") and not entities.get("amount"):
                        greeting = (
                            "Olá! 👋" if intent == "greeting"
                            else "Não entendi o que você disse no áudio. Tente novamente com mais detalhes, por exemplo: *gastei 50 reais no mercado*."
                        )
                        send_message(
                            chat_id,
                            f"{greeting}\nO que deseja fazer?",
                            reply_markup=keyboards.get_main_menu_keyboard(),
                        )
                    else:
                        greeting = (
                            "Olá! 👋" if intent == "greeting"
                            else "Não entendi como registro, mas aqui está seu menu:"
                        )
                        send_message(
                            chat_id,
                            f"{greeting}\nO que deseja fazer?",
                            reply_markup=keyboards.get_main_menu_keyboard(),
                        )
                else:
                    greeting = (
                        "Olá! 👋" if intent == "greeting" else "Não entendi como registro, mas aqui está seu menu:"
                    )
                    send_message(
                        chat_id,
                        f"{greeting}\nO que deseja fazer?",
                        reply_markup=keyboards.get_main_menu_keyboard(),
                    )

    finally:
        if audio_path is not None:
            try:
                audio_path.unlink(missing_ok=True)
            except OSError:
                pass

    return "OK", 200


def register_telegram_webhook(app):
    from flask import request

    @app.route("/webhook", methods=["POST"])
    def telegram_webhook():
        return handle_telegram_update(request.get_json())
