# Arquivo: commands.py (Versão Final com Relatórios Detalhados)

import db
from datetime import datetime

def format_detailed_report(transactions):
    """Formata a lista de transações em um relatório bonito e seguro."""
    if not transactions:
        return "Nenhum gasto registrado no período."

    report_lines = ["*Lista de Gastos:*"]
    category_totals = {}
    grand_total = 0

    # 1. Monta a lista de transações individuais
    for trans in transactions:
        trans_date_str = trans.get('transaction_date')
        description = trans.get('description', 'Sem descrição').capitalize()
        amount = float(trans.get('amount', 0))

        if not trans_date_str:
            continue

        trans_date = datetime.fromisoformat(trans_date_str).strftime('%d/%m/%y')
        
        report_lines.append(f"- {description}: R${amount:.2f} ({trans_date})")
        
        category_totals[description] = category_totals.get(description, 0) + amount
        grand_total += amount
    
    if not category_totals:
        return "Nenhum gasto válido encontrado no período."

    # 2. Monta o resumo por categoria
    summary_lines = ["\n-----------------------------------------\n\n*Resumo por Categoria:*"]
    for category, total in sorted(category_totals.items(), key=lambda item: item[1], reverse=True):
        summary_lines.append(f"- Você gastou R${total:.2f} com {category}")

    # 3. Junta tudo em um relatório final
    final_report = "\n".join(report_lines) + "\n".join(summary_lines)
    final_report += f"\n\n*Gasto Total no Período:* R${grand_total:.2f}"
    
    return final_report

def handle_command(command, user_id):
    parts = command.split(' ')
    cmd = parts[0].lstrip('/')

    # --- Comandos de Relatório ---
    if cmd == 'gerar_relatorio_semanal_detalhado' or cmd == 'relatorio_semana_passada':
        transactions = db.get_detailed_report(user_id, 'last_week')
        return "*--- Relatório da Semana Passada ---*\n\n" + format_detailed_report(transactions)

    elif cmd == 'gerar_relatorio_mensal_detalhado' or cmd == 'relatorio_mes_passado':
        transactions = db.get_detailed_report(user_id, 'last_month')
        return "*--- Relatório do Mês Passado ---*\n\n" + format_detailed_report(transactions)

    # --- NOVOS COMANDOS PARA TESTE ---
    elif cmd == 'relatorio_esta_semana':
        transactions = db.get_detailed_report(user_id, 'this_week')
        return "*--- Relatório desta Semana ---*\n\n" + format_detailed_report(transactions)

    elif cmd == 'relatorio_este_mes':
        transactions = db.get_detailed_report(user_id, 'this_month')
        return "*--- Relatório deste Mês ---*\n\n" + format_detailed_report(transactions)

    # --- Outros Comandos ---
    elif cmd == 'menu' or cmd == 'ajuda':
        return """
🤖 *Menu de Comandos* 🤖

*Lançamentos:*
Apenas escreva o que aconteceu.

*Contas e Cartões:*
`/cadastrar_conta [nome]`
`/cadastrar_cartao [nome]`
`/saldo`
`/fatura [nome]`

*Relatórios Detalhados:*
`/relatorio_esta_semana`
`/relatorio_este_mes`
`/relatorio_semana_passada`
`/relatorio_mes_passado`
"""
    # ... (resto do código para saldo, cadastrar_conta, etc., continua igual)
    elif cmd == 'cadastrar_conta':
        if len(parts) < 2: return "Uso: `/cadastrar_conta [nome]`"
        account_name = " ".join(parts[1:])
        db.create_account(user_id, account_name)
        return f"✅ Conta '{account_name}' criada!"
    elif cmd == 'cadastrar_cartao':
        if len(parts) < 2: return "Uso: `/cadastrar_cartao [nome]`"
        card_name = " ".join(parts[1:])
        db.create_credit_card(user_id, card_name)
        return f"✅ Cartão '{card_name}' criado!"
    elif cmd == 'saldo':
        accounts = db.get_accounts_balance(user_id)
        if not accounts:
            return "Você ainda não tem contas cadastradas."
        response_text = "* Saldos Atuais *\n\n"
        total = 0
        for acc in accounts:
            response_text += f"*{acc['name']}:* R${acc['balance']:.2f}\n"
            total += acc['balance']
        response_text += f"\n*Total:* R${total:.2f}"
        return response_text
    elif cmd == 'fatura':
        return "Função /fatura ainda em construção!"
    else:
        return "Comando não reconhecido. Digite /menu."