# Arquivo: commands.py
import db
from datetime import datetime
import ai_parser

def format_detailed_report(transactions):
    if not transactions:
        return "Nenhum gasto registrado no período."
    
    report_lines = ["*📝 Extrato do Período:*"]
    category_totals = {}
    grand_total = 0
    
    for trans in transactions:
        try:
            desc = (trans.get('description') or "Sem descrição").capitalize()
            amount = float(trans.get('amount', 0))
            # Tratamento de data seguro
            t_date = trans.get('transaction_date')
            if t_date:
                data_fmt = datetime.fromisoformat(t_date).strftime('%d/%m')
            else:
                data_fmt = "--/--"
            
            report_lines.append(f"▫️ {desc}: R${amount:.2f} ({data_fmt})")
            
            # Agrupa categorias
            cat = trans.get('category') or desc # Usa descrição se não tiver categoria
            category_totals[cat] = category_totals.get(cat, 0) + amount
            grand_total += amount
        except Exception as e:
            continue

    summary_lines = ["\n*📂 Por Categoria:*"]
    for category, total in sorted(category_totals.items(), key=lambda item: item[1], reverse=True):
        summary_lines.append(f"▪️ {category}: R${total:.2f}")
    
    final_report = "\n".join(report_lines) + "\n------------------\n" + "\n".join(summary_lines)
    final_report += f"\n\n💰 *Total:* R${grand_total:.2f}"
    return final_report

def handle_command(command, user_id):
    parts = command.split(' ')
    cmd = parts[0].lstrip('/')

    
    # --- TEXTO DE AJUDA NOVO ---
    if cmd in ['ajuda', 'start']:
        return """
🤖 *Bem-vindo ao WhatsFinance!*

Eu sou seu assistente financeiro pessoal.
Você não precisa decorar comandos. Basta navegar pelos botões abaixo ou conversar comigo.

*Como usar:*
1. *Registrar gastos:* Apenas escreva.
   Ex: _"Gastei 50 no mercado no débito"_
   Ex: _"Pix de 100 reais recebido do João"_

2. *Navegar:* Use o botão */menu* para ver seus relatórios, saldos e cadastrar contas.

Vamos começar? 👇
"""
    
    # --- Lógica de Comandos ---
    elif cmd == 'conselho':
        return ai_parser.get_financial_advice()

    # Cadastros (Mantemos a lógica textual caso o usuário queira digitar, 
    # mas vamos acionar via botão que pede input depois)
    elif cmd == 'cadastrar_conta':
        if len(parts) < 2: return "⚠️ Para cadastrar, digite: `/cadastrar_conta NomeDoBanco`"
        account_name = " ".join(parts[1:])
        db.create_account(user_id, account_name)
        return f"✅ Conta *{account_name}* criada com sucesso!"

    elif cmd == 'cadastrar_cartao':
        if len(parts) < 2: return "⚠️ Para cadastrar, digite: `/cadastrar_cartao NomeDoCartao`"
        card_name = " ".join(parts[1:])
        db.create_credit_card(user_id, card_name)
        return f"✅ Cartão *{card_name}* criado com sucesso!"

    # --- NOVO CADASTRO DE CARTÃO ---
    elif cmd == 'cadastrar_cartao':
        # Formato: /cadastrar_cartao Nome DiaFecha DiaVence
        if len(parts) < 4: 
            return "⚠️ Use: `/cadastrar_cartao Nome DiaFechamento DiaVencimento`\nEx: `/cadastrar_cartao Nubank 04 11`"
        
        card_name = parts[1]
        try:
            closing = int(parts[2])
            due = int(parts[3])
            db.create_credit_card(user_id, card_name, closing, due)
            return f"✅ Cartão *{card_name}* cadastrado!\n📅 Fecha dia {closing}\n📅 Vence dia {due}"
        except:
            return "⚠️ Os dias precisam ser números."

    # --- NOVA FUNÇÃO FATURA ---
    elif cmd == 'fatura':
        total, details = db.get_invoice_total(user_id)
        if total == 0: return "💳 Nenhuma fatura em aberto encontrada."
        
        msg = f"💳 *Faturas Abertas (Estimativa):*\n"
        for d in details:
            msg += f"▫️ *{d['card']}*: R${d['total']:.2f} (Vence dia {d['due_day']})\n"
        
        msg += f"\n💰 *Total:* R${total:.2f}"
        return msg

    elif cmd == 'saldo':
        accounts = db.get_accounts_balance(user_id)
        if not accounts: return "Você ainda não tem contas cadastradas. Vá em Configurações para adicionar."
        response_text = "💰 *Seus Saldos:*\n\n"
        total = sum(acc.get('balance', 0) for acc in accounts)
        for acc in accounts:
            response_text += f"🏦 *{acc.get('name')}:* R${acc.get('balance', 0):.2f}\n"
        response_text += f"\n*Patrimônio Total:* R${total:.2f}"
        return response_text

    elif cmd == 'ultimos':
        last_trans = db.get_last_transactions(user_id)
        if not last_trans: return "📭 Nenhum lançamento recente."
        
        response_text = "*📝 Últimos 5 Lançamentos:*\n\n"
        for t in last_trans:
            tipo = "🟢" if t.get('type') == 'income' else "🔴"
            desc = t.get('description') or "S/D"
            val = t.get('amount', 0)
            tid = t.get('id')
            response_text += f"{tipo} *R${val:.2f}* - {desc} (ID: {tid})\n"
        
        response_text += "\n_Para apagar, digite /apagar ID_"
        return response_text

    elif cmd == 'apagar':
        if len(parts) < 2: return "Para apagar, preciso do ID. Ex: `/apagar 55`"
        if not parts[1].isdigit(): return "O ID precisa ser um número."
        
        tid = int(parts[1])
        if db.delete_transaction(tid, user_id):
            return f"🗑️ Lançamento {tid} apagado!"
        else:
            return "❌ Erro: ID não encontrado ou falha no sistema."

    # Relatórios (Centralizados)
    elif cmd == 'relatorio_esta_semana':
        return format_detailed_report(db.get_detailed_report(user_id, 'this_week'))
    elif cmd == 'relatorio_semana_passada':
        return format_detailed_report(db.get_detailed_report(user_id, 'last_week'))
    elif cmd == 'relatorio_mes_atual': # Adicionado
        return format_detailed_report(db.get_detailed_report(user_id, 'this_month'))
        
    return "Comando não entendido."