BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="pt-br" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>WhatsFinance</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #020617; color: #e2e8f0; }
        .glass { background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.05); }
        .gradient-text { background: linear-gradient(135deg, #4ade80 0%, #3b82f6 100%); -webkit-background-clip: text; color: transparent; }
        .card-hover { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
        .card-hover:hover { transform: translateY(-4px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5); border-color: rgba(255,255,255,0.1); }
        .input-dark { background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255, 255, 255, 0.05); color: white; }
        .input-dark:focus { border-color: #3b82f6; ring: 2px solid rgba(59, 130, 246, 0.2); outline: none; }
    </style>
</head>
<body class="antialiased min-h-screen flex flex-col bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-[#020617] to-[#020617]">
    
    {% with messages = get_flashed_messages() %}
    {% if messages %}
        <div id="toast" class="fixed top-6 left-1/2 transform -translate-x-1/2 z-50 animate-bounce">
            <div class="glass px-6 py-3 rounded-full shadow-2xl flex items-center gap-3 text-sm font-semibold text-white border-l-4 border-blue-500">
                <span>🔔</span>
                <span>{{ messages[0] }}</span>
            </div>
        </div>
        <script>setTimeout(() => { const t = document.getElementById('toast'); if(t) { t.style.opacity='0'; setTimeout(()=>t.remove(), 500); } }, 4000);</script>
    {% endif %}
    {% endwith %}
    
    {content_body}
</body>
</html>
"""

LOGIN_PAGE = """
<div class="flex flex-col items-center justify-center min-h-screen px-4 relative overflow-hidden">
    <div class="glass p-8 rounded-3xl shadow-2xl w-full max-w-sm">
        <div class="text-center mb-8">
            <h1 class="text-3xl font-bold mb-2 text-white">WhatsFinance</h1>
            <p class="text-slate-400 text-sm">Painel de Controle</p>
        </div>
        <form method="POST" class="space-y-5">
            <div class="space-y-1">
                <label class="text-xs font-semibold text-slate-400 ml-1 uppercase">Telegram ID</label>
                <input type="text" name="telegram_id" placeholder="Ex: 123456789" class="w-full input-dark rounded-xl px-4 py-3.5">
            </div>
            <div class="space-y-1">
                <label class="text-xs font-semibold text-slate-400 ml-1 uppercase">Senha</label>
                <input type="password" name="password" placeholder="••••••••" class="w-full input-dark rounded-xl px-4 py-3.5">
            </div>
            <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-4 rounded-xl mt-2 transition">Acessar</button>
        </form>
        <div class="mt-8 pt-6 border-t border-slate-700/50 text-center">
            <a href="/register" class="text-sm text-blue-400 hover:text-blue-300 font-semibold">Primeiro acesso? Criar Senha</a>
        </div>
    </div>
</div>
"""

REGISTER_PAGE = """
<div class="flex flex-col items-center justify-center min-h-screen px-4">
    <div class="glass p-8 rounded-3xl w-full max-w-sm relative">
        <button onclick="history.back()" class="absolute top-6 left-6 text-slate-500 hover:text-white">← Voltar</button>
        <div class="text-center mt-8 mb-8">
            <h2 class="text-2xl font-bold text-white">Autenticação</h2>
            <p class="text-slate-400 text-sm mt-2">Enviaremos um código no Telegram.</p>
        </div>
        <form method="POST" action="/send_code" class="space-y-4">
            <input type="text" name="telegram_id" placeholder="Seu Telegram ID" class="w-full input-dark rounded-xl px-4 py-3.5 text-center text-lg">
            <button class="w-full bg-slate-800 hover:bg-slate-700 text-white font-bold py-4 rounded-xl border border-slate-700 transition">Enviar Código</button>
        </form>
    </div>
</div>
"""

VERIFY_PAGE = """
<div class="flex flex-col items-center justify-center min-h-screen px-4">
    <div class="glass p-8 rounded-3xl w-full max-w-sm">
        <h2 class="text-2xl font-bold text-white text-center mb-6">Definir Senha</h2>
        <form method="POST" action="/verify_setup" class="space-y-4">
            <input type="hidden" name="telegram_id" value="{{ telegram_id }}">
            <input type="text" name="code" placeholder="000000" class="w-full bg-slate-900/80 border border-slate-700 rounded-2xl px-4 py-6 text-center text-3xl font-mono tracking-[0.5em] text-white focus:border-green-500 outline-none" maxlength="6" autofocus>
            <div>
                <label class="text-xs text-slate-400 uppercase font-semibold pl-1">Nova Senha</label>
                <input type="password" name="password" class="w-full mt-1 input-dark rounded-xl px-4 py-3.5" required>
            </div>
            <button class="w-full bg-green-600 hover:bg-green-500 text-white font-bold py-4 rounded-xl mt-4 transition">Confirmar</button>
        </form>
    </div>
</div>
"""

DASHBOARD_PAGE = """
<nav class="glass sticky top-0 z-40 border-b-0 border-b border-white/5">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-green-400 to-blue-600 flex items-center justify-center text-white font-bold">W</div>
                <span class="font-bold text-lg text-white">WhatsFinance</span>
            </div>
            <div class="flex items-center gap-4">
                <div class="hidden md:flex flex-col items-end">
                    <span class="text-sm font-bold text-white">{{ user.name }}</span>
                    <span class="text-xs text-green-400">Online</span>
                </div>
                <a href="/logout" class="text-xs bg-slate-800 text-slate-300 px-4 py-2 rounded-lg hover:bg-red-500/10 hover:text-red-400 border border-white/5 transition">Sair</a>
            </div>
        </div>
    </div>
</nav>

<main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="glass p-6 rounded-3xl card-hover relative overflow-hidden group">
            <p class="text-slate-400 text-xs font-bold uppercase tracking-wider mb-1">Saldo Total</p>
            <h3 class="text-3xl font-bold text-white mb-4">R$ {{ "%.2f"|format(total_acc) }}</h3>
            <div class="flex flex-wrap gap-2">
                {% for acc in accs %}
                <div class="flex items-center gap-2 bg-slate-800/50 px-3 py-1.5 rounded-lg border border-white/5">
                    <span class="w-2 h-2 rounded-full bg-green-500"></span>
                    <span class="text-xs text-slate-300">{{ acc.name }}: R${{ acc.balance }}</span>
                </div>
                {% endfor %}
            </div>
        </div>
        <div class="glass p-6 rounded-3xl card-hover relative overflow-hidden group">
            <p class="text-slate-400 text-xs font-bold uppercase tracking-wider mb-1">Faturas Abertas</p>
            <h3 class="text-3xl font-bold text-white mb-4">R$ {{ "%.2f"|format(total_invoice) }}</h3>
            <div class="flex flex-wrap gap-2">
                {% for inv in invoice_details %}
                <div class="flex items-center gap-2 bg-slate-800/50 px-3 py-1.5 rounded-lg border border-white/5">
                    <span class="w-2 h-2 rounded-full bg-red-500"></span>
                    <span class="text-xs text-slate-300">{{ inv.card }}</span>
                </div>
                {% endfor %}
            </div>
        </div>
        <a href="/transaction/new" class="glass p-6 rounded-3xl card-hover flex flex-col items-center justify-center text-center cursor-pointer border-dashed border-2 border-slate-700 hover:border-blue-500/50 hover:bg-blue-500/5 transition group">
            <div class="w-14 h-14 bg-blue-600 rounded-2xl flex items-center justify-center text-2xl mb-3 shadow-lg shadow-blue-600/20 group-hover:scale-110 transition">＋</div>
            <h3 class="font-bold text-white">Novo Registro</h3>
            <p class="text-slate-400 text-xs mt-1">Lançamento manual</p>
        </a>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 glass rounded-3xl p-6 md:p-8">
            <div class="flex items-center justify-between mb-8">
                <h3 class="font-bold text-xl text-white">Últimas Movimentações</h3>
                <a href="/transactions" class="text-sm text-blue-400 hover:text-blue-300 font-semibold transition">Ver Extrato Completo →</a>
            </div>
            <div class="space-y-4">
                {% for t in recent %}
                <div class="flex items-center justify-between p-4 rounded-2xl bg-slate-800/30 hover:bg-slate-800/60 border border-white/5 transition group">
                    <div class="flex items-center gap-4">
                        <div class="w-12 h-12 rounded-2xl flex items-center justify-center text-xl {{ 'bg-red-500/10 text-red-400' if t.type == 'expense' else 'bg-green-500/10 text-green-400' }}">
                            {{ '📉' if t.type == 'expense' else '📈' }}
                        </div>
                        <div>
                            <p class="font-bold text-sm text-slate-200 group-hover:text-white transition">{{ t.description }}</p>
                            <div class="flex items-center gap-2 text-xs text-slate-500 mt-0.5">
                                <span class="bg-slate-700/50 px-1.5 py-0.5 rounded">{{ t.category or 'Geral' }}</span>
                                <span class="uppercase">{{ t.payment_method or 'Outro' }}</span>
                            </div>
                        </div>
                    </div>
                    <span class="font-bold font-mono text-sm {{ 'text-red-400' if t.type == 'expense' else 'text-green-400' }}">
                        {{ '-' if t.type == 'expense' else '+' }}R$ {{ "%.2f"|format(t.amount) }}
                    </span>
                </div>
                {% endfor %}
            </div>
        </div>
        <div class="glass rounded-3xl p-6 md:p-8 flex flex-col">
            <h3 class="font-bold text-lg text-white mb-6">Fluxo</h3>
            <div class="flex-1 flex items-center justify-center relative min-h-[200px]">
                <canvas id="financeChart"></canvas>
            </div>
            <div class="mt-6 text-center text-xs text-slate-500">Entradas vs Saídas</div>
        </div>
    </div>
</main>
<script>
    const ctx = document.getElementById('financeChart').getContext('2d');
    const transactions = {{ recent_json | safe }};
    const expenses = transactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + parseFloat(t.amount), 0);
    const incomes = transactions.filter(t => t.type === 'income').reduce((sum, t) => sum + parseFloat(t.amount), 0);
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Entradas', 'Saídas'],
            datasets: [{
                data: [incomes, expenses],
                backgroundColor: ['#4ade80', '#f87171'],
                borderColor: '#1e293b',
                borderWidth: 0
            }]
        },
        options: { responsive: true, cutout: '75%', plugins: { legend: { display: false } } }
    });
</script>
"""

TRANSACTIONS_LIST_PAGE = """
<div class="max-w-5xl mx-auto px-4 py-8">
    <div class="flex items-center justify-between mb-8">
        <a href="/dashboard" class="text-slate-400 hover:text-white flex items-center gap-2 transition font-medium">← Voltar</a>
        <h1 class="text-2xl font-bold text-white">Extrato Completo</h1>
        <a href="/transaction/new" class="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2.5 rounded-xl text-sm font-bold shadow-lg shadow-blue-900/20 transition">+ Novo</a>
    </div>
    <div class="glass rounded-3xl overflow-hidden">
        <div class="overflow-x-auto">
            <table class="w-full text-left text-sm text-slate-400">
                <thead class="bg-slate-900/50 text-xs uppercase font-semibold text-slate-300 border-b border-white/5">
                    <tr>
                        <th class="px-6 py-4">Data/Descrição</th>
                        <th class="px-6 py-4">Valor</th>
                        <th class="px-6 py-4">Método</th>
                        <th class="px-6 py-4 text-right">Ações</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-800/50">
                    {% for t in transactions %}
                    <tr class="hover:bg-slate-800/30 transition group">
                        <td class="px-6 py-4">
                            <p class="text-white font-medium group-hover:text-blue-400 transition">{{ t.description }}</p>
                            <span class="text-xs text-slate-500">{{ t.transaction_date[:10] }} • {{ t.category or 'Geral' }}</span>
                        </td>
                        <td class="px-6 py-4 font-mono font-bold {{ 'text-red-400' if t.type == 'expense' else 'text-green-400' }}">
                            {{ '-' if t.type == 'expense' else '+' }}R$ {{ "%.2f"|format(t.amount) }}
                        </td>
                        <td class="px-6 py-4">
                            <span class="bg-slate-800 px-2 py-1 rounded text-xs uppercase">{{ t.payment_method or 'OUTRO' }}</span>
                        </td>
                        <td class="px-6 py-4 text-right space-x-3">
                            <a href="/transaction/edit/{{ t.id }}" class="text-blue-400 hover:text-blue-300 font-medium">Editar</a>
                            <a href="/transaction/delete/{{ t.id }}" onclick="return confirm('Tem certeza?')" class="text-red-400 hover:text-red-300 font-medium">Excluir</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
"""

TRANSACTION_FORM_PAGE = """
<div class="flex flex-col items-center justify-center min-h-screen px-4 py-8">
    <div class="glass p-8 rounded-3xl w-full max-w-lg relative">
        <button onclick="history.back()" class="absolute top-6 left-6 text-slate-500 hover:text-white transition">← Cancelar</button>
        <h2 class="text-2xl font-bold text-center mb-8 text-white">{{ 'Editar' if t else 'Nova' }} Transação</h2>
        <form method="POST" class="space-y-5">
            <div class="grid grid-cols-2 gap-4 p-1 bg-slate-900/50 rounded-xl">
                <label class="cursor-pointer">
                    <input type="radio" name="type" value="expense" class="peer sr-only" {{ 'checked' if not t or t.type == 'expense' else '' }}>
                    <div class="text-center py-3 rounded-lg text-slate-400 peer-checked:bg-red-500/20 peer-checked:text-red-400 peer-checked:font-bold transition">Saída</div>
                </label>
                <label class="cursor-pointer">
                    <input type="radio" name="type" value="income" class="peer sr-only" {{ 'checked' if t and t.type == 'income' else '' }}>
                    <div class="text-center py-3 rounded-lg text-slate-400 peer-checked:bg-green-500/20 peer-checked:text-green-400 peer-checked:font-bold transition">Entrada</div>
                </label>
            </div>
            <div>
                <label class="text-xs font-semibold text-slate-400 ml-1 uppercase">Descrição</label>
                <input type="text" name="description" value="{{ t.description if t else '' }}" required class="w-full input-dark rounded-xl px-4 py-3 mt-1" placeholder="Ex: Mercado, Salário">
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="text-xs font-semibold text-slate-400 ml-1 uppercase">Valor (R$)</label>
                    <input type="number" step="0.01" name="amount" value="{{ t.amount if t else '' }}" required class="w-full input-dark rounded-xl px-4 py-3 mt-1" placeholder="0.00">
                </div>
                <div>
                    <label class="text-xs font-semibold text-slate-400 ml-1 uppercase">Categoria</label>
                    <input type="text" name="category" value="{{ t.category if t else '' }}" class="w-full input-dark rounded-xl px-4 py-3 mt-1">
                </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="text-xs font-semibold text-slate-400 ml-1 uppercase">Método</label>
                    <select name="payment_method" class="w-full input-dark rounded-xl px-4 py-3 mt-1 bg-slate-900/80">
                        <option value="debit_card" {{ 'selected' if t and t.payment_method=='debit_card' else '' }}>Débito</option>
                        <option value="credit_card" {{ 'selected' if t and t.payment_method=='credit_card' else '' }}>Crédito</option>
                        <option value="pix" {{ 'selected' if t and t.payment_method=='pix' else '' }}>Pix</option>
                        <option value="money" {{ 'selected' if t and t.payment_method=='money' else '' }}>Dinheiro</option>
                    </select>
                </div>
                <div>
                    <label class="text-xs font-semibold text-slate-400 ml-1 uppercase">Conta</label>
                    <select name="account_id" class="w-full input-dark rounded-xl px-4 py-3 mt-1 bg-slate-900/80">
                        <option value="">-- Nenhuma --</option>
                        {% for acc in accounts %}
                        <option value="{{ acc.id }}" {{ 'selected' if t and t.account_id == acc.id else '' }}>{{ acc.name }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            <div>
                <label class="text-xs font-semibold text-slate-400 ml-1 uppercase">Cartão (Opcional)</label>
                <select name="card_id" class="w-full input-dark rounded-xl px-4 py-3 mt-1 bg-slate-900/80">
                    <option value="">-- Nenhum --</option>
                    {% for c in cards %}
                    <option value="{{ c.id }}" {{ 'selected' if t and t.card_id == c.id else '' }}>{{ c.name }}</option>
                    {% endfor %}
                </select>
            </div>
            <div>
                <label class="text-xs font-semibold text-slate-400 ml-1 uppercase">Data</label>
                <input type="datetime-local" name="date" value="{{ t.transaction_date if t else now }}" class="w-full input-dark rounded-xl px-4 py-3 mt-1">
            </div>
            <button class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-4 rounded-xl mt-4 transition shadow-lg shadow-blue-900/20">
                {{ 'Salvar Alterações' if t else 'Adicionar' }}
            </button>
        </form>
    </div>
</div>
"""