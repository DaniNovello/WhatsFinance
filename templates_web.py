# Layout Base com CSS refinado para visual "Enterprise"
BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="pt-br" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>WhatsFinance Pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #0B0F19; color: #E2E8F0; }
        .font-mono { font-family: 'JetBrains Mono', monospace; }
        
        /* Glass Effect mais "Fosco/Profissional" */
        .glass { 
            background: rgba(17, 24, 39, 0.7); 
            backdrop-filter: blur(20px); 
            -webkit-backdrop-filter: blur(20px); 
            border: 1px solid rgba(255, 255, 255, 0.08); 
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
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

        /* Animação do Toast Profissional */
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        .toast-enter { animation: slideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
        
        /* Tabela Profissional */
        .table-row-hover:hover td { background-color: rgba(59, 130, 246, 0.05); }
    </style>
</head>
<body class="antialiased min-h-screen flex flex-col bg-[#0B0F19]">
    
    {% with messages = get_flashed_messages() %}
    {% if messages %}
        <div id="toast-container" class="fixed bottom-6 right-6 z-50 flex flex-col gap-2">
            <div class="toast-enter glass bg-[#1F2937] border-l-4 border-blue-500 text-white px-6 py-4 rounded shadow-2xl flex items-center gap-4 min-w-[320px] relative overflow-hidden">
                <div class="text-blue-400">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                </div>
                <div>
                    <h4 class="font-semibold text-sm">Notificação</h4>
                    <p class="text-slate-300 text-sm">{{ messages[0] }}</p>
                </div>
                <div class="absolute bottom-0 left-0 h-1 bg-blue-500/30 w-full">
                    <div class="h-full bg-blue-500 w-full animate-[shrink_4s_linear_forwards]" style="animation-name: shrinkWidth;"></div>
                </div>
            </div>
        </div>
        <script>
            // Auto-dismiss suave
            const t = document.querySelector('.toast-enter');
            t.style.animation = 'slideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards';
            setTimeout(() => {
                t.style.transition = 'all 0.4s ease';
                t.style.opacity = '0';
                t.style.transform = 'translateX(20px)';
                setTimeout(() => t.remove(), 400);
            }, 4000);
            
            // CSS keyframe para barra de progresso injetado via JS para simplicidade
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
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            </div>
            <h1 class="text-2xl font-bold text-white tracking-tight">WhatsFinance</h1>
            <p class="text-slate-500 text-sm mt-1">Gestão Financeira Inteligente</p>
        </div>
        
        <div class="glass p-8 rounded-xl shadow-xl border border-slate-800">
            <form method="POST" class="space-y-5">
                <div class="space-y-1.5">
                    <label class="text-xs font-medium text-slate-400 uppercase tracking-wide">Telegram ID</label>
                    <input type="text" name="telegram_id" class="w-full input-dark rounded-lg px-4 py-3 text-sm focus:ring-blue-500/20 placeholder-slate-600" placeholder="Digite seu ID">
                </div>
                <div class="space-y-1.5">
                    <label class="text-xs font-medium text-slate-400 uppercase tracking-wide">Senha</label>
                    <input type="password" name="password" class="w-full input-dark rounded-lg px-4 py-3 text-sm focus:ring-blue-500/20 placeholder-slate-600" placeholder="••••••••">
                </div>
                
                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 rounded-lg transition-all shadow-lg shadow-blue-900/20 text-sm mt-2">
                    Entrar
                </button>
            </form>
        </div>
        
        <div class="mt-8 text-center">
            <a href="/register" class="text-sm text-slate-500 hover:text-blue-400 transition">Não tem senha? Validar Acesso</a>
        </div>
    </div>
</div>
"""

REGISTER_PAGE = """
<div class="flex flex-col items-center justify-center min-h-screen px-4 bg-[#0B0F19]">
    <div class="w-full max-w-sm glass p-8 rounded-xl border border-slate-800 relative">
        <button onclick="history.back()" class="absolute top-6 left-6 text-slate-500 hover:text-white transition text-sm flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg> Voltar
        </button>
        
        <div class="text-center mt-6 mb-8">
            <h2 class="text-xl font-bold text-white">Validação de Segurança</h2>
            <p class="text-slate-500 text-sm mt-2">Enviaremos um código único para o seu Telegram.</p>
        </div>

        <form method="POST" action="/send_code" class="space-y-4">
            <div class="space-y-1.5">
                <label class="text-xs font-medium text-slate-400 uppercase tracking-wide">Seu ID Telegram</label>
                <input type="text" name="telegram_id" class="w-full input-dark rounded-lg px-4 py-3 text-center text-lg tracking-wide focus:border-blue-500 transition">
            </div>
            <button class="w-full bg-slate-800 hover:bg-slate-700 text-white font-medium py-3 rounded-lg border border-slate-700 transition text-sm">Solicitar Código</button>
        </form>
    </div>
</div>
"""

VERIFY_PAGE = """
<div class="flex flex-col items-center justify-center min-h-screen px-4 bg-[#0B0F19]">
    <div class="w-full max-w-sm glass p-8 rounded-xl border border-slate-800">
        <h2 class="text-xl font-bold text-white text-center mb-1">Definir Senha</h2>
        <p class="text-slate-500 text-xs text-center mb-8">Digite o código recebido e sua nova senha.</p>
        
        <form method="POST" action="/verify_setup" class="space-y-5">
            <input type="hidden" name="telegram_id" value="{{ telegram_id }}">
            
            <div class="space-y-1.5">
                <label class="text-xs font-medium text-slate-400 uppercase tracking-wide text-center block">Código de Verificação</label>
                <input type="text" name="code" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-4 text-center text-2xl font-mono tracking-[0.5em] text-white focus:border-blue-500 outline-none transition" maxlength="6" autofocus placeholder="000000">
            </div>
            
            <div class="space-y-1.5">
                <label class="text-xs font-medium text-slate-400 uppercase tracking-wide">Nova Senha</label>
                <input type="password" name="password" class="w-full input-dark rounded-lg px-4 py-3 text-sm" required placeholder="Crie uma senha forte">
            </div>
            
            <button class="w-full bg-green-600 hover:bg-green-500 text-white font-medium py-3 rounded-lg mt-2 transition text-sm shadow-lg shadow-green-900/10">Confirmar Acesso</button>
        </form>
    </div>
</div>
"""

# Navbar componente para reutilizar
NAVBAR = """
<nav class="sticky top-0 z-40 bg-[#0B0F19]/80 backdrop-blur-md border-b border-slate-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded bg-blue-600 flex items-center justify-center text-white font-bold text-sm">WF</div>
                <span class="font-semibold text-white tracking-tight">WhatsFinance</span>
            </div>
            <div class="flex items-center gap-6">
                <div class="hidden md:block text-right">
                    <p class="text-sm font-medium text-white">{{ user.name }}</p>
                    <p class="text-[10px] text-green-500 uppercase font-bold tracking-wider">Pro Plan</p>
                </div>
                <a href="/logout" class="text-sm text-slate-400 hover:text-white transition">Sair</a>
            </div>
        </div>
    </div>
</nav>
"""

DASHBOARD_PAGE = NAVBAR + """
<main class="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="glass p-6 rounded-xl border border-slate-800 hover:border-slate-700 transition duration-300">
            <div class="flex justify-between items-start mb-4">
                <div>
                    <p class="text-slate-500 text-xs font-semibold uppercase tracking-wider">Saldo em Contas</p>
                    <h3 class="text-3xl font-bold text-white mt-1 font-mono tracking-tight">R$ {{ "%.2f"|format(total_acc) }}</h3>
                </div>
                <span class="p-2 bg-green-500/10 rounded-lg text-green-500">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                </span>
            </div>
            <div class="flex flex-col gap-1">
                {% for acc in accs %}
                <div class="flex justify-between text-xs text-slate-400 border-b border-dashed border-slate-800 pb-1 last:border-0 last:pb-0">
                    <span>{{ acc.name }}</span>
                    <span class="text-white font-mono">R$ {{ acc.balance }}</span>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="glass p-6 rounded-xl border border-slate-800 hover:border-slate-700 transition duration-300">
            <div class="flex justify-between items-start mb-4">
                <div>
                    <p class="text-slate-500 text-xs font-semibold uppercase tracking-wider">Faturas Abertas</p>
                    <h3 class="text-3xl font-bold text-white mt-1 font-mono tracking-tight">R$ {{ "%.2f"|format(total_invoice) }}</h3>
                </div>
                <span class="p-2 bg-red-500/10 rounded-lg text-red-500">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"></path></svg>
                </span>
            </div>
            <div class="flex flex-col gap-1">
                {% for inv in invoice_details %}
                <div class="flex justify-between text-xs text-slate-400 border-b border-dashed border-slate-800 pb-1 last:border-0 last:pb-0">
                    <span>{{ inv.card }}</span>
                    <span class="text-white font-mono">Vence: {{ inv.due_day }}</span>
                </div>
                {% endfor %}
            </div>
        </div>

        <a href="/transaction/new" class="glass p-6 rounded-xl border border-dashed border-slate-700 hover:border-blue-500/50 hover:bg-blue-500/5 transition duration-300 flex flex-col items-center justify-center text-center cursor-pointer group h-full">
            <div class="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white shadow-lg shadow-blue-600/20 mb-3 group-hover:scale-110 transition duration-300">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
            </div>
            <h3 class="font-semibold text-white">Novo Lançamento</h3>
            <p class="text-slate-500 text-xs mt-1">Adicionar manualmente</p>
        </a>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <div class="lg:col-span-2">
            <div class="flex items-center justify-between mb-6">
                <h3 class="text-lg font-semibold text-white">Últimas Movimentações</h3>
                <a href="/transactions" class="text-sm text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1 transition">
                    Extrato Completo <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
                </a>
            </div>
            
            <div class="glass rounded-xl border border-slate-800 overflow-hidden">
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-sm text-slate-400">
                        <thead class="bg-slate-900/50 text-xs uppercase font-semibold text-slate-500 border-b border-slate-800">
                            <tr>
                                <th class="px-6 py-3 font-medium">Descrição</th>
                                <th class="px-6 py-3 font-medium">Categoria</th>
                                <th class="px-6 py-3 font-medium text-right">Valor</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-800/50">
                            {% for t in recent %}
                            <tr class="table-row-hover transition duration-150">
                                <td class="px-6 py-4">
                                    <div class="flex items-center gap-3">
                                        <div class="w-8 h-8 rounded flex items-center justify-center text-xs font-bold {{ 'bg-red-500/10 text-red-500' if t.type == 'expense' else 'bg-green-500/10 text-green-500' }}">
                                            {{ 'OUT' if t.type == 'expense' else 'IN' }}
                                        </div>
                                        <div>
                                            <p class="text-white font-medium truncate max-w-[180px]">{{ t.description }}</p>
                                            <p class="text-xs text-slate-500">{{ t.payment_method or 'N/A' }}</p>
                                        </div>
                                    </div>
                                </td>
                                <td class="px-6 py-4">
                                    <span class="px-2 py-1 bg-slate-800 rounded text-xs border border-slate-700">{{ t.category or 'Geral' }}</span>
                                </td>
                                <td class="px-6 py-4 text-right">
                                    <span class="font-mono font-medium {{ 'text-red-400' if t.type == 'expense' else 'text-green-400' }}">
                                        {{ '-' if t.type == 'expense' else '+' }}{{ "%.2f"|format(t.amount) }}
                                    </span>
                                </td>
                            </tr>
                            {% endfor %}
                            
                            {% if not recent %}
                            <tr>
                                <td colspan="3" class="px-6 py-8 text-center text-slate-500">Nenhuma movimentação recente.</td>
                            </tr>
                            {% endif %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div class="flex flex-col gap-6">
            <div class="glass p-6 rounded-xl border border-slate-800">
                <h3 class="text-sm font-semibold text-white mb-6 uppercase tracking-wider">Resumo do Período</h3>
                <div class="relative h-[220px] w-full">
                    <canvas id="financeChart"></canvas>
                    <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
                        <div class="text-center">
                            <span class="text-xs text-slate-500 block">Balanço</span>
                            <span class="text-xl font-bold text-white block">100%</span>
                        </div>
                    </div>
                </div>
                <div class="mt-6 space-y-3">
                    <div class="flex justify-between items-center text-sm border-b border-slate-800 pb-2">
                        <span class="flex items-center gap-2 text-slate-400"><span class="w-2 h-2 rounded-full bg-green-500"></span> Entradas</span>
                        <span class="text-white font-mono" id="totalIncome">R$ 0.00</span>
                    </div>
                    <div class="flex justify-between items-center text-sm border-b border-slate-800 pb-2">
                        <span class="flex items-center gap-2 text-slate-400"><span class="w-2 h-2 rounded-full bg-red-500"></span> Saídas</span>
                        <span class="text-white font-mono" id="totalExpense">R$ 0.00</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</main>
<script>
    const ctx = document.getElementById('financeChart').getContext('2d');
    const transactions = {{ recent_json | safe }};
    const expenses = transactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + parseFloat(t.amount), 0);
    const incomes = transactions.filter(t => t.type === 'income').reduce((sum, t) => sum + parseFloat(t.amount), 0);

    document.getElementById('totalIncome').innerText = 'R$ ' + incomes.toFixed(2);
    document.getElementById('totalExpense').innerText = 'R$ ' + expenses.toFixed(2);

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Entradas', 'Saídas'],
            datasets: [{
                data: [incomes, expenses],
                backgroundColor: ['#10B981', '#EF4444'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '80%',
            plugins: { legend: { display: false }, tooltip: { backgroundColor: '#1F2937', titleColor: '#fff', bodyColor: '#ccc', borderColor: '#374151', borderWidth: 1 } }
        }
    });
</script>
"""

# Extrato Completo com Layout UNIFICADO (max-w-7xl)
TRANSACTIONS_LIST_PAGE = NAVBAR + """
<main class="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex flex-col sm:flex-row items-center justify-between mb-8 gap-4">
        <div class="flex items-center gap-4">
            <a href="/dashboard" class="w-10 h-10 rounded-lg border border-slate-700 flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-800 transition">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
            </a>
            <h1 class="text-2xl font-bold text-white tracking-tight">Extrato Completo</h1>
        </div>
        
        <div class="flex gap-3">
            <button class="px-4 py-2 text-sm text-slate-400 bg-slate-800 rounded-lg border border-slate-700 hover:text-white transition">Filtrar</button>
            <a href="/transaction/new" class="px-4 py-2 text-sm bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium shadow-lg shadow-blue-900/20 transition flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg> Novo Registro
            </a>
        </div>
    </div>

    <div class="glass rounded-xl border border-slate-800 overflow-hidden shadow-xl">
        <div class="overflow-x-auto">
            <table class="w-full text-left text-sm text-slate-400">
                <thead class="bg-slate-900/80 text-xs uppercase font-semibold text-slate-500 border-b border-slate-700">
                    <tr>
                        <th class="px-6 py-4 font-medium">Data</th>
                        <th class="px-6 py-4 font-medium">Descrição</th>
                        <th class="px-6 py-4 font-medium">Método</th>
                        <th class="px-6 py-4 font-medium">Valor</th>
                        <th class="px-6 py-4 font-medium text-right">Ações</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-800/50">
                    {% for t in transactions %}
                    <tr class="table-row-hover transition duration-150 group">
                        <td class="px-6 py-4 whitespace-nowrap font-mono text-xs text-slate-500">
                            {{ t.transaction_date[:10] }} <span class="text-slate-600">{{ t.transaction_date[11:16] }}</span>
                        </td>
                        <td class="px-6 py-4">
                            <p class="text-white font-medium group-hover:text-blue-400 transition">{{ t.description }}</p>
                            <span class="text-xs text-slate-500 block mt-0.5">{{ t.category or 'Geral' }}</span>
                        </td>
                        <td class="px-6 py-4">
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-800 border border-slate-700 text-slate-300">
                                {{ t.payment_method or 'Manual' }}
                            </span>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <span class="font-mono font-medium {{ 'text-red-400' if t.type == 'expense' else 'text-green-400' }}">
                                {{ '-' if t.type == 'expense' else '+' }}R$ {{ "%.2f"|format(t.amount) }}
                            </span>
                        </td>
                        <td class="px-6 py-4 text-right whitespace-nowrap">
                            <div class="flex justify-end gap-3 opacity-60 group-hover:opacity-100 transition">
                                <a href="/transaction/edit/{{ t.id }}" class="text-blue-400 hover:text-blue-300 font-medium text-xs border border-blue-500/30 px-3 py-1 rounded hover:bg-blue-500/10 transition">Editar</a>
                                <a href="/transaction/delete/{{ t.id }}" onclick="return confirm('Confirmar exclusão?')" class="text-red-400 hover:text-red-300 font-medium text-xs border border-red-500/30 px-3 py-1 rounded hover:bg-red-500/10 transition">Excluir</a>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                    
                    {% if not transactions %}
                    <tr>
                        <td colspan="5" class="px-6 py-12 text-center">
                            <div class="flex flex-col items-center justify-center text-slate-500">
                                <svg class="w-12 h-12 mb-4 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>
                                <p>Nenhum registro encontrado no histórico.</p>
                            </div>
                        </td>
                    </tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
    </div>
</main>
"""

TRANSACTION_FORM_PAGE = """
<div class="flex flex-col items-center justify-center min-h-screen px-4 py-8 bg-[#0B0F19]">
    <div class="glass p-8 rounded-xl w-full max-w-lg border border-slate-800 shadow-2xl relative">
        <button onclick="history.back()" class="absolute top-6 left-6 text-slate-500 hover:text-white transition text-sm flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg> Cancelar
        </button>
        
        <h2 class="text-xl font-bold text-center mb-8 text-white">{{ 'Editar Lançamento' if t else 'Novo Lançamento' }}</h2>

        <form method="POST" class="space-y-6">
            <div class="grid grid-cols-2 gap-2 p-1 bg-slate-900 rounded-lg border border-slate-800">
                <label class="cursor-pointer">
                    <input type="radio" name="type" value="expense" class="peer sr-only" {{ 'checked' if not t or t.type == 'expense' else '' }}>
                    <div class="text-center py-2.5 rounded-md text-slate-500 text-sm font-medium peer-checked:bg-red-500/10 peer-checked:text-red-500 peer-checked:shadow-sm transition-all hover:text-slate-300">
                        Saída
                    </div>
                </label>
                <label class="cursor-pointer">
                    <input type="radio" name="type" value="income" class="peer sr-only" {{ 'checked' if t and t.type == 'income' else '' }}>
                    <div class="text-center py-2.5 rounded-md text-slate-500 text-sm font-medium peer-checked:bg-green-500/10 peer-checked:text-green-500 peer-checked:shadow-sm transition-all hover:text-slate-300">
                        Entrada
                    </div>
                </label>
            </div>

            <div class="space-y-1.5">
                <label class="text-xs font-semibold text-slate-400 uppercase tracking-wide">Descrição</label>
                <input type="text" name="description" value="{{ t.description if t else '' }}" required class="w-full input-dark rounded-lg px-4 py-3 text-sm focus:ring-blue-500/20" placeholder="Ex: Supermercado, Salário">
            </div>
            
            <div class="grid grid-cols-2 gap-4">
                <div class="space-y-1.5">
                    <label class="text-xs font-semibold text-slate-400 uppercase tracking-wide">Valor (R$)</label>
                    <input type="number" step="0.01" name="amount" value="{{ t.amount if t else '' }}" required class="w-full input-dark rounded-lg px-4 py-3 text-sm focus:ring-blue-500/20 font-mono" placeholder="0.00">
                </div>
                <div class="space-y-1.5">
                    <label class="text-xs font-semibold text-slate-400 uppercase tracking-wide">Categoria</label>
                    <input type="text" name="category" value="{{ t.category if t else '' }}" class="w-full input-dark rounded-lg px-4 py-3 text-sm focus:ring-blue-500/20" placeholder="Geral">
                </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
                <div class="space-y-1.5">
                    <label class="text-xs font-semibold text-slate-400 uppercase tracking-wide">Método</label>
                    <select name="payment_method" class="w-full input-dark rounded-lg px-4 py-3 text-sm bg-[#111827]">
                        <option value="debit_card" {{ 'selected' if t and t.payment_method=='debit_card' else '' }}>Débito</option>
                        <option value="credit_card" {{ 'selected' if t and t.payment_method=='credit_card' else '' }}>Crédito</option>
                        <option value="pix" {{ 'selected' if t and t.payment_method=='pix' else '' }}>Pix</option>
                        <option value="money" {{ 'selected' if t and t.payment_method=='money' else '' }}>Dinheiro</option>
                    </select>
                </div>
                <div class="space-y-1.5">
                    <label class="text-xs font-semibold text-slate-400 uppercase tracking-wide">Conta</label>
                    <select name="account_id" class="w-full input-dark rounded-lg px-4 py-3 text-sm bg-[#111827]">
                        <option value="">-- Selecionar --</option>
                        {% for acc in accounts %}
                        <option value="{{ acc.id }}" {{ 'selected' if t and t.account_id == acc.id else '' }}>{{ acc.name }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            
            <div class="space-y-1.5">
                <label class="text-xs font-semibold text-slate-400 uppercase tracking-wide">Cartão (Se Crédito)</label>
                <select name="card_id" class="w-full input-dark rounded-lg px-4 py-3 text-sm bg-[#111827]">
                    <option value="">-- Selecionar --</option>
                    {% for c in cards %}
                    <option value="{{ c.id }}" {{ 'selected' if t and t.card_id == c.id else '' }}>{{ c.name }}</option>
                    {% endfor %}
                </select>
            </div>

            <div class="space-y-1.5">
                <label class="text-xs font-semibold text-slate-400 uppercase tracking-wide">Data & Hora</label>
                <input type="datetime-local" name="date" value="{{ t.transaction_date if t else now }}" class="w-full input-dark rounded-lg px-4 py-3 text-sm focus:ring-blue-500/20">
            </div>

            <button class="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 rounded-lg mt-4 shadow-lg shadow-blue-900/20 transition transform active:scale-[0.99]">
                {{ 'Salvar Alterações' if t else 'Adicionar Lançamento' }}
            </button>
        </form>
    </div>
</div>
"""