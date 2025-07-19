import db

def handle_command(command, user_id):
    parts = command.split(' ')
    cmd = parts[0]

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

    else:
        return "Comando não reconhecido. Digite `/menu`."