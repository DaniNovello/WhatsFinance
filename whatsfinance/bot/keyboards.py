"""Teclados inline do Telegram (estrutura JSON da API)."""


def get_main_menu_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "💰 Saldo & Faturas", "callback_data": "/saldo"},
                {"text": "📝 Últimos", "callback_data": "/ultimos"},
            ],
            [
                {"text": "📊 Relatórios", "callback_data": "menu_relatorios"},
                {"text": "⚙️ Contas e Cartões", "callback_data": "menu_config"},
            ],
        ]
    }


def get_reports_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "📅 Semana", "callback_data": "/relatorio_esta_semana"},
                {"text": "📆 Mês", "callback_data": "/relatorio_mes_atual"},
            ],
            [{"text": "🔙 Voltar", "callback_data": "/menu"}],
        ]
    }


def get_config_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "➕ Nova Conta", "callback_data": "btn_new_account"},
                {"text": "💳 Novo Cartão", "callback_data": "btn_new_card"},
            ],
            [{"text": "🔙 Voltar", "callback_data": "/menu"}],
        ]
    }


def get_type_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "🔴 Gastei (Saída)", "callback_data": "set_type_expense"},
                {"text": "🟢 Ganhei (Entrada)", "callback_data": "set_type_income"},
            ]
        ]
    }


def get_transaction_confirm_keyboard():
    """Confirmação antes de gravar lançamento (callback_data curtos < 64 bytes)."""
    return {
        "inline_keyboard": [
            [
                {"text": "✅ Confirmar", "callback_data": "txn_confirm_yes"},
                {"text": "❌ Cancelar", "callback_data": "txn_confirm_no"},
            ]
        ]
    }


def get_method_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "💳 Crédito", "callback_data": "set_method_credit_card"},
                {"text": "🏧 Débito", "callback_data": "set_method_debit_card"},
            ],
            [
                {"text": "💠 Pix", "callback_data": "set_method_pix"},
                {"text": "💵 Dinheiro", "callback_data": "set_method_money"},
            ],
        ]
    }
