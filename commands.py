# Arquivo: commands.py
import db # Importa nosso módulo de banco de dados

def handle_command(command, user_id):
    """Mapeia comandos para funções específicas."""
    if command == '/menu' or command == '/ajuda':
        return """
🤖 *Menu de Comandos* 🤖

*Lançamentos:*
Para registrar, apenas escreva o que aconteceu.
Ex: `gastei 50 no ifood no crédito`
Ex: `recebi 1000 de salário na conta nubank`

*Consultas Rápidas:*
`/saldo` - Mostra o saldo de todas as suas contas.
`/fatura [nome_cartao]` - Mostra o valor atual da fatura. Ex: `/fatura nubank`
"""
    elif command == '/saldo':
        # Implementar a lógica para buscar o saldo total das contas do usuário no db.py
        return "Função /saldo ainda em construção!"

    elif command.startswith('/fatura'):
        return "Função /fatura ainda em construção!"

    else:
        return "Comando não reconhecido. Digite `/menu` para ver todas as opções."