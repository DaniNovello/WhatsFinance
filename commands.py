# Arquivo: commands.py (substitua o conteúdo pelo abaixo)
import db

def handle_command(command, user_id):
    parts = command.split(' ')
    cmd = parts[0]

    if cmd == '/menu' or cmd == '/ajuda':
        return """
🤖 *Menu de Comandos* 🤖

*Lançamentos:*
Apenas escreva o que aconteceu.
Ex: `gastei 50 no ifood no crédito`

*Contas:*
`/cadastrar_conta [nome_da_conta]`
Ex: `/cadastrar_conta Carteira`
`/saldo` - Mostra o saldo de todas as suas contas.
"""
    elif cmd == '/cadastrar_conta':
        if len(parts) < 2:
            return "Uso incorreto. Ex: `/cadastrar_conta Carteira`"
        account_name = " ".join(parts[1:])
        db.create_account(user_id, account_name)
        return f"✅ Conta '{account_name}' criada com sucesso!"

    elif cmd == '/saldo':
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
    else:
        return "Comando não reconhecido. Digite `/menu` para ver as opções."