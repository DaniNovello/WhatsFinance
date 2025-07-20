# Arquivo: commands.py (Versão Corrigida e Mais Robusta)

import db
from datetime import datetime

def format_detailed_report(transactions):
    """Formata a lista de transações em um relatório bonito e seguro."""
    if not transactions:
        return "Nenhum gasto registrado no período."

    report_lines = []
    category_totals = {}
    grand_total = 0

    # Lista de transações
    for trans in transactions:
        # LÓGICA DE SEGURANÇA: Garante que os campos existem e não são nulos
        trans_date_str = trans.get('transaction_date')
        description = trans.get('description', 'Sem descrição') # Usa um valor padrão se for nulo
        amount = float(trans.get('amount', 0))

        if not trans_date_str:
            continue # Pula esta transação se a data for nula

        trans_date = datetime.fromisoformat(trans_date_str).strftime('%d/%m/%y')
        
        report_lines.append(f"- {description.capitalize()}: R${amount:.2f} ({trans_date})")
        
        category_totals[description] = category_totals.get(description, 0) + amount
        grand_total += amount
    
    if not report_lines:
        return "Nenhum gasto válido encontrado no período."

    # Resumo por categoria
    summary_lines = ["\n*Resumo por Categoria:*"]
    for category, total in sorted(category_totals.items(), key=lambda item: item[1], reverse=True):
        summary_lines.append(f"- {category.capitalize()}: R${total:.2f}")

    # Total geral
    final_report = "\n".join(report_lines) + "\n\n" + "\n".join(summary_lines)
    final_report += f"\n\n*Gasto Total:* R${grand_total:.2f}"
    
    return final_report

def handle_command(command, user_id):
    parts = command.split(' ')
    cmd = parts[0].lstrip('/') # Remove a barra '/' do início, se ela existir

    # -- Comandos de Cadastro --
    if cmd == 'menu' or cmd == 'ajuda':
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
`/fatura [nome]`

*Relatórios:*
`/gerar_relatorio_semanal_detalhado`
`/gerar_relatorio_mensal_detalhado`
"""
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

    # -- Comandos de Consulta --
    elif cmd == 'saldo':
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
    
    # -- Comandos de Relatório --
    # CORREÇÃO AQUI: removi a barra '/' da comparação
    elif cmd == 'gerar_relatorio_semanal_detalhado':
        transactions = db.get_detailed_report(user_id, 'last_week')
        return "*--- Relatório Semanal de Gastos ---*\n\n" + format_detailed_report(transactions)

    # CORREÇÃO AQUI: removi a barra '/' da comparação
    elif cmd == 'gerar_relatorio_mensal_detalhado':
        transactions = db.get_detailed_report(user_id, 'last_month')
        return "*--- Relatório Mensal de Gastos ---*\n\n" + format_detailed_report(transactions)

    elif cmd == 'fatura':
        return "Função /fatura ainda em construção!"

    else:
        return "Comando não reconhecido. Digite /menu."