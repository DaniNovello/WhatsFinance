# Arquivo: commands.py
import db
from datetime import datetime
import ai_parser # Importamos o ai_parser para usar a nova função

def format_detailed_report(transactions):
    if not transactions:
        return "Nenhum gasto registrado no período."
    report_lines = ["*Lista de Gastos:*"]
    category_totals = {}
    grand_total = 0
    for trans in transactions:
        try:
            desc = (trans.get('description') or "Sem descrição").capitalize()
            amount = float(trans.get('amount', 0))
            trans_date = datetime.fromisoformat(trans.get('transaction_date')).strftime('%d/%m/%y')
            report_lines.append(f"- {desc}: R${amount:.2f} ({trans_date})")
            category_totals[desc] = category_totals.get(desc, 0) + amount
            grand_total += amount
        except Exception as e:
            print(f"Erro ao processar transação no relatório: {trans} | Erro: {e}")
            continue
    if not category_totals: return "Nenhum gasto válido encontrado no período."
    summary_lines = ["\n-----------------------------------------\n\n*Resumo por Categoria:*"]
    for category, total in sorted(category_totals.items(), key=lambda item: item[1], reverse=True):
        summary_lines.append(f"- Você gastou R${total:.2f} com {category}")
    final_report = "\n".join(report_lines) + "\n".join(summary_lines)
    final_report += f"\n\n*Gasto Total no Período:* R${grand_total:.2f}"
    return final_report

def handle_command(command, user_id):
    parts = command.split(' ')
    cmd = parts[0].lstrip('/')

    if cmd in ['menu', 'ajuda']:
        return """
🤖 *Menu de Comandos* 🤖

*Gestão de Lançamentos:*
`/ultimos` - Lista seus últimos 5 lançamentos.
`/apagar [ID]` - Apaga um lançamento pelo ID.

*Contas e Cartões:*
`/cadastrar_conta [nome]`
`/cadastrar_cartao [nome]`
`/saldo`
`/fatura [nome]` (Em breve)

*Relatórios Detalhados:*
`/relatorio_esta_semana`
`/relatorio_semana_passada`
"""
    # --- NOVO COMANDO "SECRETO" PARA TESTE ---
    elif cmd == 'conselho':
        return ai_parser.get_financial_advice()

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
        if not accounts: return "Você ainda não tem contas cadastradas."
        response_text = "* Saldos Atuais *\n\n"
        total = sum(acc.get('balance', 0) for acc in accounts)
        for acc in accounts:
            response_text += f"*{acc.get('name', 'N/A')}:* R${acc.get('balance', 0):.2f}\n"
        response_text += f"\n*Total:* R${total:.2f}"
        return response_text
    elif cmd == 'fatura':
        return "Função /fatura ainda em construção!"

    elif cmd == 'ultimos':
        last_trans = db.get_last_transactions(user_id)
        if not last_trans:
            return "Nenhum lançamento recente encontrado."
        response_text = "*Seus Últimos Lançamentos:*\n\n"
        for t in last_trans:
            tipo = "⬆️" if t.get('type') == 'income' else "⬇️"
            desc = (t.get('description') or "Sem descrição").capitalize()
            response_text += f"{tipo} *ID {t.get('id')}:* {desc} - R${t.get('amount', 0):.2f}\n"
        response_text += "\nPara apagar, use `/apagar [ID]`"
        return response_text
    elif cmd == 'apagar':
        if len(parts) < 2 or not parts[1].isdigit():
            return "Uso incorreto. Ex: `/apagar 123`"
        trans_id_to_delete = int(parts[1])
        success = db.delete_transaction(trans_id_to_delete, user_id)
        if success:
            return f"✅ Lançamento com ID {trans_id_to_delete} apagado com sucesso!"
        else:
            return "❌ Erro ao apagar o lançamento. Verifique se o ID está correto."

    elif cmd == 'relatorio_esta_semana':
        transactions = db.get_detailed_report(user_id, 'this_week')
        return "*--- Relatório desta Semana ---*\n\n" + format_detailed_report(transactions)
    elif cmd in ['gerar_relatorio_semanal_detalhado', 'relatorio_semana_passada']:
        transactions = db.get_detailed_report(user_id, 'last_week')
        return "*--- Relatório da Semana Passada ---*\n\n" + format_detailed_report(transactions)
    elif cmd in ['gerar_relatorio_mensal_detalhado', 'relatorio_mes_passado']:
        transactions = db.get_detailed_report(user_id, 'last_month')
        return "*--- Relatório do Mês Passado ---*\n\n" + format_detailed_report(transactions)
        
    else:
        return "Comando não reconhecido. Digite /menu."