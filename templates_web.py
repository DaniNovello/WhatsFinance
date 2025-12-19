BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="pt-br" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Zenith</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #0B0F19; color: #E2E8F0; }
        .font-mono { font-family: 'JetBrains Mono', monospace; }
        
        .glass { 
            background: rgba(17, 24, 39, 0.7); 
            backdrop-filter: blur(20px); 
            -webkit-backdrop-filter: blur(20px); 
            border: 1px solid rgba(255, 255, 255, 0.08); 
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        .input-dark { 
            background: #111827; 
            border: 1px solid #374151; 
            color: white; 
            transition: all 0.2s;
        }
        .input-dark:focus { 
            border-color: #3B82F6; 
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2); 
            outline: none; 
        }

        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        .toast-enter { animation: slideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
        
        /* Utilitário para esconder barra de rolagem mas permitir scroll */
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
    </style>
</head>
<body class="antialiased min-h-screen flex flex-col bg-[#0B0F19]">
    
    {% with messages = get_flashed_messages() %}
    {% if messages %}
        <div id="toast-container" class="fixed bottom-6 right-6 z-50 flex flex-col gap-2 max-w-[90vw]">
            <div class="toast-enter glass bg-[#1F2937] border-l-4 border-blue-500 text-white px-5 py-4 rounded shadow-2xl flex items-center gap-4 relative overflow-hidden">
                <div class="text-blue-400 shrink-0">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                </div>
                <div>
                    <h4 class="font-semibold text-sm">Notificação</h4>
                    <p class="text-slate-300 text-xs">{{ messages[0] }}</p>
                </div>
                <div class="absolute bottom-0 left-0 h-1 bg-blue-500/30 w-full">
                    <div class="h-full bg-blue-500 w-full animate-[shrink_4s_linear_forwards]" style="animation-name: shrinkWidth;"></div>
                </div>
            </div>
        </div>
        <script>
            const t = document.querySelector('.toast-enter');
            setTimeout(() => {
                t.style.transition = 'all 0.4s ease';
                t.style.opacity = '0';
                t.style.transform = 'translateX(20px)';
                setTimeout(() => t.remove(), 400);
            }, 4000);
            const style = document.createElement('style');
            style.innerHTML = `@keyframes shrinkWidth { from { width: 100%; } to { width: 0%; } }`;
            document.head.appendChild(style);
        </script>
    {% endif %}
    {% endwith %}
    
    {content_body}
</body>
</html>
"""

LOGIN_PAGE = """
<div class="flex flex-col items-center justify-center min-h-screen px-4 bg-gradient-to-b from-[#0B0F19] to-[#111827]">
    <div class="w-full max-w-sm">
        <div class="text-center mb-10">
            <div class="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-blue-600/10 text-blue-500 mb-4 ring-1 ring-blue-500/20">
                <span class="text-2xl font-bold">Z</span>
            </div>
            <h1 class="text-3xl font-bold text-white tracking-tight">Zenith</h1>
            <p class="text-slate-500 text-sm mt-1">Inteligência Financeira</p>
        </div>
        
        <div class="glass p-8 rounded-xl shadow-xl border border-slate-800">
            <form method="POST" class="space-y-5">
                <div class="space-y-1.5">
                    <label class="text-xs font-medium text-slate-400 uppercase tracking-wide">Telegram ID</label>
                    <input type="text" name="telegram_id" class="w-full input-dark rounded-lg px-4 py-3 text-sm focus:ring-blue-500/20 placeholder-slate-600" placeholder="Seu ID">
                </div>
                <div class="space-y-1.5">
                    <label class="text-xs font-medium text-slate-400 uppercase tracking-wide">Senha</label>
                    <input type="password" name="password" class="w-full input-dark rounded-lg px-4 py-3 text-sm focus:ring-blue-500/20 placeholder-slate-600" placeholder="••••••••">
                </div>
                
                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 rounded-lg transition-all shadow-lg shadow-blue-900/20 text-sm mt-2">
                    Acessar
                </button>
            </form>
        </div>
        
        <div class="mt-8 text-center">
            <a href="/register" class="text-sm text-slate-500 hover:text-blue-400 transition">Primeiro acesso?</a>
        </div>
    </div>
</div>
"""

REGISTER_PAGE = """
<div class="flex flex-col items-center justify-center min-h-screen px-4 bg-[#0B0F19]">
    <div class="w-full max-w-sm glass p-8 rounded-xl border border-slate-800 relative">
        <button onclick="history.back()" class="absolute top-6 left-6 text-slate-500 hover:text-white transition text-sm flex items-center gap-1">
            ← Voltar
        </button>
        <div class="text-center mt-6 mb-8">
            <h2 class="text-xl font-bold text-white">Novo Acesso Zenith</h2>
            <p class="text-slate-500 text-sm mt-2">Validação via Telegram</p>
        </div>
        <form method="POST" action="/send_code" class="space-y-4">
            <input type="text" name="telegram_id" placeholder="Seu Telegram ID" class="w-full input-dark rounded-lg px-4 py-3 text-center text-lg focus:border-blue-500 transition">
            <button class="w-full bg-slate-800 hover:bg-slate-700 text-white font-medium py-3 rounded-lg border border-slate-700 transition text-sm">Enviar Código</button>
        </form>
    </div>
</div>
"""

VERIFY_PAGE = """
<div class="flex flex-col items-center justify-center min-h-screen px-4 bg-[#0B0F19]">
    <div class="w-full max-w-sm glass p-8 rounded-xl border border-slate-800">
        <h2 class="text-xl font-bold text-white text-center mb-1">Definir Senha</h2>
        <p class="text-slate-500 text-xs text-center mb-8">Código enviado ao chat</p>
        <form method="POST" action="/verify_setup" class="space-y-5">
            <input type="hidden" name="telegram_id" value="{{ telegram_id }}">
            <input type="text" name="code" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-4 text-center text-2xl font-mono tracking-[0.5em] text-white focus:border-blue-500 outline-none" maxlength="6" autofocus placeholder="000000">
            <div>
                <label class="text-xs font-medium text-slate-400 uppercase tracking-wide">Nova Senha</label>
                <input type="password" name="password" class="w-full mt-1 input-dark rounded-lg px-4 py-3 text-sm" required>
            </div>
            <button class="w-full bg-green-600 hover:bg-green-500 text-white font-medium py-3 rounded-lg mt-2 transition text-sm shadow-lg shadow-green-900/10">Confirmar</button>
        </form>
    </div>
</div>
"""

NAVBAR = """
<nav class="sticky top-0 z-40 bg-[#0B0F19]/80 backdrop-blur-md border-b border-slate-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded bg-blue-600 flex items-center justify-center text-white font-bold text-sm">Z</div>
                <span class="font-semibold text-white tracking-tight">Zenith</span>
            </div>
            <div class="flex items-center gap-4">
                <span class="text-xs text-slate-400 hidden sm:block">{{ user.name }}</span>
                <a href="/logout" class="text-xs bg-slate-800 text-slate-300 px-3 py-1.5 rounded hover:bg-red-500/10 hover:text-red-400 transition border border-slate-700">Sair</a>
            </div>
        </div>
    </div>
</nav>
"""

DASHBOARD_PAGE = NAVBAR + """
<main class="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="glass p-5 rounded-xl border border-slate-800">
            <p class="text-slate-500 text-xs font-semibold uppercase tracking-wider mb-1">Saldo Total</p>
            <h3 class="text-2xl font-bold text-white mb-3 font-mono">R$ {{ "%.2f"|format(total_acc) }}</h3>
            <div class="flex flex-col gap-1 max-h-24 overflow-y-auto no-scrollbar">
                {% for acc in accs %}
                <div class="flex justify-between text-xs text-slate-400 border-b border-dashed border-slate-800 pb-1 last:border-0">
                    <span>{{ acc.name }}</span>
                    <span class="text-white font-mono">R$ {{ acc.balance }}</span>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="glass p-5 rounded-xl border border-slate-800">
            <p class="text-slate-500 text-xs font-semibold uppercase tracking-wider mb-1">Faturas Abertas</p>
            <h3 class="text-2xl font-bold text-white mb-3 font-mono">R$ {{ "%.2f"|format(total_invoice) }}</h3>
            <div class="flex flex-col gap-1 max-h-24 overflow-y-auto no-scrollbar">
                {% for inv in invoice_details %}
                <div class="flex justify-between text-xs text-slate-400 border-b border-dashed border-slate-800 pb-1 last:border-0">
                    <span>{{ inv.card }}</span>
                    <span class="text-white font-mono">Vence {{ inv.due_day }}</span>
                </div>
                {% endfor %}
            </div>
        </div>

        <a href="/transaction/new" class="glass p-5 rounded-xl border border-dashed border-slate-700 hover:bg-blue-500/5 transition flex items-center justify-center gap-3 group cursor-pointer h-full">
            <div class="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white shadow-lg group-hover:scale-110 transition">＋</div>
            <div class="text-left">
                <h3 class="font-semibold text-white text-sm">Novo Lançamento</h3>
                <p class="text-slate-500 text-xs">Registrar manual</p>
            </div>
        </a>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <div class="lg:col-span-2">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-md font-semibold text-white">Últimas Movimentações</h3>
                <a href="/transactions" class="text-xs text-blue-400 hover:text-blue-300 font-medium">Ver Extrato →</a>
            </div>
            
            <div class="glass rounded-xl border border-slate-800 overflow-hidden">
                <div class="block md:hidden">
                    {% for t in recent %}
                    <div class="p-4 border-b border-slate-800 last:border-0 active:bg-slate-800/50 transition">
                        <div class="flex justify-between items-start mb-1">
                            <div class="flex items-center gap-3">
                                <div class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold {{ 'bg-red-500/10 text-red-500' if t.type == 'expense' else 'bg-green-500/10 text-green-500' }}">
                                    {{ '↓' if t.type == 'expense' else '↑' }}
                                </div>
                                <div>
                                    <p class="text-white text-sm font-medium">{{ t.description }}</p>
                                    <p class="text-[10px] text-slate-500 uppercase tracking-wide">{{ t.category or 'Geral' }} • {{ t.payment_method }}</p>
                                </div>
                            </div>
                            <span class="font-mono text-sm font-medium {{ 'text-red-400' if t.type == 'expense' else 'text-green-400' }}">
                                {{ '-' if t.type == 'expense' else '+' }}{{ "%.2f"|format(t.amount) }}
                            </span>
                        </div>
                    </div>
                    {% endfor %}
                    {% if not recent %}
                    <div class="p-6 text-center text-xs text-slate-500">Sem registros recentes.</div>
                    {% endif %}
                </div>

                <div class="hidden md:block overflow-x-auto">
                    <table class="w-full text-left text-sm text-slate-400">
                        <thead class="bg-slate-900/50 text-xs uppercase font-semibold text-slate-500">
                            <tr>
                                <th class="px-6 py-3">Descrição</th>
                                <th class="px-6 py-3">Categoria</th>
                                <th class="px-6 py-3 text-right">Valor</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-800/50">
                            {% for t in recent %}
                            <tr class="hover:bg-slate-800/30 transition">
                                <td class="px-6 py-4">
                                    <div class="flex items-center gap-3">
                                        <div class="w-6 h-6 rounded flex items-center justify-center text-[10px] font-bold {{ 'bg-red-500/10 text-red-500' if t.type == 'expense' else 'bg-green-500/10 text-green-500' }}">
                                            {{ 'OUT' if t.type == 'expense' else 'IN' }}
                                        </div>
                                        <span class="text-white">{{ t.description }}</span>
                                    </div>
                                </td>
                                <td class="px-6 py-4 text-xs">{{ t.category }}</td>
                                <td class="px-6 py-4 text-right font-mono {{ 'text-red-400' if t.type == 'expense' else 'text-green-400' }}">
                                    {{ '-' if t.type == 'expense' else '+' }}{{ "%.2f"|format(t.amount) }}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div class="glass p-5 rounded-xl border border-slate-800 flex flex-col justify-center">
            <h3 class="text-xs font-semibold text-white mb-4 uppercase tracking-wider text-center">Balanço do Período</h3>
            <div class="relative h-[180px] w-full">
                <canvas id="financeChart"></canvas>
            </div>
            <div class="mt-4 flex justify-between text-xs px-4">
                <div class="text-green-400 font-mono">IN: <span id="totalIncome">0</span></div>
                <div class="text-red-400 font-mono">OUT: <span id="totalExpense">0</span></div>
            </div>
        </div>
    </div>
</main>
<script>
    const ctx = document.getElementById('financeChart').getContext('2d');
    const transactions = {{ recent_json | safe }};
    const expenses = transactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + parseFloat(t.amount), 0);
    const incomes = transactions.filter(t => t.type === 'income').reduce((sum, t) => sum + parseFloat(t.amount), 0);

    document.getElementById('totalIncome').innerText = incomes.toFixed(0);
    document.getElementById('totalExpense').innerText = expenses.toFixed(0);

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Entradas', 'Saídas'],
            datasets: [{
                data: [incomes, expenses],
                backgroundColor: ['#10B981', '#EF4444'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '85%',
            plugins: { legend: { display: false } }
        }
    });
</script>
"""

# Página de Extrato (TOTALMENTE RESPONSIVA)
TRANSACTIONS_LIST_PAGE = NAVBAR + """
<main class="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-3">
            <a href="/dashboard" class="w-8 h-8 rounded-lg border border-slate-700 flex items-center justify-center text-slate-400 hover:text-white transition">←</a>
            <h1 class="text-xl font-bold text-white">Extrato</h1>
        </div>
        <a href="/transaction/new" class="px-4 py-2 text-xs bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium shadow-lg transition">
            + Novo
        </a>
    </div>

    <div class="glass rounded-xl border border-slate-800 overflow-hidden shadow-xl">
        
        <div class="block md:hidden divide-y divide-slate-800/50">
            {% for t in transactions %}
            <div class="p-4 active:bg-slate-800/30 transition">
                <div class="flex justify-between items-start mb-2">
                    <div class="flex flex-col">
                        <span class="text-xs text-slate-500 font-mono">{{ t.transaction_date[:10] }}</span>
                        <p class="text-white font-medium text-sm mt-0.5">{{ t.description }}</p>
                    </div>
                    <div class="text-right">
                        <span class="block font-mono text-sm font-bold {{ 'text-red-400' if t.type == 'expense' else 'text-green-400' }}">
                            {{ '-' if t.type == 'expense' else '+' }}{{ "%.2f"|format(t.amount) }}
                        </span>
                    </div>
                </div>
                
                <div class="flex justify-between items-center mt-3">
                    <div class="flex gap-2">
                        <span class="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-400 border border-slate-700">{{ t.category }}</span>
                        <span class="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-400 border border-slate-700 uppercase">{{ t.payment_method }}</span>
                    </div>
                    <div class="flex gap-3">
                        <a href="/transaction/edit/{{ t.id }}" class="text-blue-400 text-xs">Editar</a>
                        <a href="/transaction/delete/{{ t.id }}" onclick="return confirm('Excluir?')" class="text-red-400 text-xs">Excluir</a>
                    </div>
                </div>
            </div>
            {% endfor %}
            
            {% if not transactions %}
            <div class="p-8 text-center text-slate-500 text-sm">Nenhum registro encontrado.</div>
            {% endif %}
        </div>

        <div class="hidden md:block overflow-x-auto">
            <table class="w-full text-left text-sm text-slate-400">
                <thead class="bg-slate-900/80 text-xs uppercase font-semibold text-slate-500 border-b border-slate-700">
                    <tr>
                        <th class="px-6 py-4">Data</th>
                        <th class="px-6 py-4">Descrição</th>
                        <th class="px-6 py-4">Método</th>
                        <th class="px-6 py-4">Valor</th>
                        <th class="px-6 py-4 text-right">Ações</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-800/50">
                    {% for t in transactions %}
                    <tr class="hover:bg-slate-800/30 transition group">
                        <td class="px-6 py-4 whitespace-nowrap font-mono text-xs">{{ t.transaction_date[:10] }}</td>
                        <td class="px-6 py-4">
                            <p class="text-white font-medium">{{ t.description }}</p>
                            <span class="text-xs text-slate-500">{{ t.category or 'Geral' }}</span>
                        </td>
                        <td class="px-6 py-4">
                            <span class="px-2 py-1 rounded text-xs bg-slate-800 border border-slate-700 uppercase">{{ t.payment_method }}</span>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap font-mono font-medium {{ 'text-red-400' if t.type == 'expense' else 'text-green-400' }}">
                            {{ '-' if t.type == 'expense' else '+' }}R$ {{ "%.2f"|format(t.amount) }}
                        </td>
                        <td class="px-6 py-4 text-right">
                            <div class="flex justify-end gap-3 opacity-50 group-hover:opacity-100 transition">
                                <a href="/transaction/edit/{{ t.id }}" class="text-blue-400 hover:underline text-xs">Editar</a>
                                <a href="/transaction/delete/{{ t.id }}" onclick="return confirm('Excluir?')" class="text-red-400 hover:underline text-xs">Excluir</a>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</main>
"""

TRANSACTION_FORM_PAGE = """
<div class="flex flex-col items-center justify-center min-h-screen px-4 py-8 bg-[#0B0F19]">
    <div class="glass p-6 rounded-xl w-full max-w-md border border-slate-800 relative">
        <button onclick="history.back()" class="absolute top-6 left-6 text-slate-500 hover:text-white transition text-xs flex items-center gap-1">
            ← Cancelar
        </button>
        
        <h2 class="text-lg font-bold text-center mb-6 text-white">{{ 'Editar' if t else 'Novo' }} Lançamento</h2>

        <form method="POST" class="space-y-5">
            <div class="grid grid-cols-2 gap-2 p-1 bg-slate-900 rounded-lg border border-slate-800">
                <label class="cursor-pointer">
                    <input type="radio" name="type" value="expense" class="peer sr-only" {{ 'checked' if not t or t.type == 'expense' else '' }}>
                    <div class="text-center py-2 rounded-md text-slate-500 text-xs font-bold uppercase tracking-wider peer-checked:bg-red-500/10 peer-checked:text-red-500 transition">
                        Saída
                    </div>
                </label>
                <label class="cursor-pointer">
                    <input type="radio" name="type" value="income" class="peer sr-only" {{ 'checked' if t and t.type == 'income' else '' }}>
                    <div class="text-center py-2 rounded-md text-slate-500 text-xs font-bold uppercase tracking-wider peer-checked:bg-green-500/10 peer-checked:text-green-500 transition">
                        Entrada
                    </div>
                </label>
            </div>

            <div class="space-y-1">
                <label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Descrição</label>
                <input type="text" name="description" value="{{ t.description if t else '' }}" required class="w-full input-dark rounded-lg px-4 py-3 text-sm" placeholder="Ex: Almoço">
            </div>
            
            <div class="grid grid-cols-2 gap-4">
                <div class="space-y-1">
                    <label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Valor</label>
                    <input type="number" step="0.01" name="amount" value="{{ t.amount if t else '' }}" required class="w-full input-dark rounded-lg px-4 py-3 text-sm font-mono" placeholder="0.00">
                </div>
                <div class="space-y-1">
                    <label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Categoria</label>
                    <input type="text" name="category" value="{{ t.category if t else '' }}" class="w-full input-dark rounded-lg px-4 py-3 text-sm" placeholder="Geral">
                </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
                <div class="space-y-1">
                    <label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Método</label>
                    <select name="payment_method" class="w-full input-dark rounded-lg px-3 py-3 text-sm bg-[#111827]">
                        <option value="debit_card" {{ 'selected' if t and t.payment_method=='debit_card' else '' }}>Débito</option>
                        <option value="credit_card" {{ 'selected' if t and t.payment_method=='credit_card' else '' }}>Crédito</option>
                        <option value="pix" {{ 'selected' if t and t.payment_method=='pix' else '' }}>Pix</option>
                        <option value="money" {{ 'selected' if t and t.payment_method=='money' else '' }}>Dinheiro</option>
                    </select>
                </div>
                <div class="space-y-1">
                    <label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Conta</label>
                    <select name="account_id" class="w-full input-dark rounded-lg px-3 py-3 text-sm bg-[#111827]">
                        <option value="">-- Selecionar --</option>
                        {% for acc in accounts %}
                        <option value="{{ acc.id }}" {{ 'selected' if t and t.account_id == acc.id else '' }}>{{ acc.name }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            
            <div class="space-y-1">
                <label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Cartão (Se Crédito)</label>
                <select name="card_id" class="w-full input-dark rounded-lg px-3 py-3 text-sm bg-[#111827]">
                    <option value="">-- Nenhum --</option>
                    {% for c in cards %}
                    <option value="{{ c.id }}" {{ 'selected' if t and t.card_id == c.id else '' }}>{{ c.name }}</option>
                    {% endfor %}
                </select>
            </div>

            <div class="space-y-1">
                <label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Data</label>
                <input type="datetime-local" name="date" value="{{ t.transaction_date if t else now }}" class="w-full input-dark rounded-lg px-4 py-3 text-sm">
            </div>

            <button class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-lg mt-4 shadow-lg transition text-sm">
                {{ 'Salvar' if t else 'Adicionar' }}
            </button>
        </form>
    </div>
</div>
"""