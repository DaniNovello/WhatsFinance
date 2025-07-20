import db

def format_detailed_report(transactions):
    """Formata a lista de transações em um relatório bonito."""
    if not transactions:
        return "Nenhum gasto registrado no período."

    report_lines = []
    category_totals = {}
    grand_total = 0

    # Lista de transações
    for trans in transactions:
        trans_date = datetime.fromisoformat(trans['transaction_date']).strftime('%d/%m/%y')
        description = trans['description']
        amount = float(trans['amount'])
        
        report_lines.append(f"- {description.capitalize()}: R${amount:.2f} ({trans_date})")
        
        category_totals[description] = category_totals.get(description, 0) + amount
        grand_total += amount
    
    # Resumo por categoria
    summary_lines = ["\n*Resumo por Categoria:*"]
    for category, total in sorted(category_totals.items(), key=lambda item: item[1], reverse=True):
        summary_lines.append(f"- {category.capitalize()}: R${total:.2f}")

    # Total geral
    final_report = "\n".join(report_lines) + "\n" + "\n".join(summary_lines)
    final_report += f"\n\n*Gasto Total:* R${grand_total:.2f}"
    
    return final_report

def handle_command(command, user_id):
    parts = command.split(' ')
    cmd = parts[0].lstrip('/')

    if cmd == '/menu' or cmd == '/ajuda':
        return """
🤖 *Menu de Comandos* 🤖

*Lançamentos:*
Apenas escreva o que aconteceu.
Ex: `gastei 50 no ifood no crédito nubank`

*Contas:*
`/cadastrar_conta [nome]`
`/saldo`

*Cartões:*
`/cadastrar_cartao [nome]`
Ex: `/cadastrar_cartao Nubank`
`/fatura [nome]`
"""
    elif cmd == '/cadastrar_conta':
        if len(parts) < 2: return "Uso: `/cadastrar_conta [nome]`"
        account_name = " ".join(parts[1:])
        db.create_account(user_id, account_name)
        return f"✅ Conta '{account_name}' criada!"

    elif cmd == '/cadastrar_cartao':
        if len(parts) < 2: return "Uso: `/cadastrar_cartao [nome]`"
        card_name = " ".join(parts[1:])
        db.create_credit_card(user_id, card_name)
        return f"✅ Cartão '{card_name}' criado!"

    elif cmd == '/saldo':
        # ... (código do /saldo que já existe) ...
        accounts = db.get_accounts_balance(user_id)
        if not accounts:
            return "Você ainda não tem contas cadastradas. Use `/cadastrar_conta [nome]`."
        
        response_text = "* Saldos Atuais *\n\n"
        total = 0
        for acc in accounts:
            response_text += f"*{acc['name']}:* R${acc['balance']:.2f}\n"
            total += acc['balance']
        response_text += f"\n*Total:* R${total:.2f}"
        return response_text

    elif cmd == '/fatura':
        # Esta é a função que vamos implementar
        return "Função /fatura ainda em construção!"
    if cmd == '/gerar_relatorio_semanal_detalhado':
        transactions = db.get_detailed_report(user_id, 'last_week')
        return "*Relatório Semanal de Gastos*\n" + format_detailed_report(transactions)

    elif cmd == '/gerar_relatorio_mensal_detalhado':
        transactions = db.get_detailed_report(user_id, 'last_month')
        return "*Relatório Mensal de Gastos*\n" + format_detailed_report(transactions)

    else:
        return "Comando não reconhecido. Digite `/menu`."