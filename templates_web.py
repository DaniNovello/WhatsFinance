# HTML e Estilos separados para organização

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

# Conteúdo da Página de Login
LOGIN_PAGE = """
<div class="flex flex-col items-center justify-center min-h-screen px-4 relative overflow-hidden">
    <div class="absolute top-0 left-0 w-full h-full overflow-hidden -z-10">
        <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>
        <div class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-green-500/10 rounded-full blur-3xl"></div>
    </div>

    <div class="glass p-8 md:p-10 rounded-3xl shadow-2xl w-full max-w-sm relative group">
        <div class="text-center mb-8">
            <div class="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-green-400 to-blue-600 mb-4 shadow-lg shadow-green-500/20">
                <span class="text-2xl">⚡</span>
            </div>
            <h1 class="text-3xl font-bold mb-2 text-white tracking-tight">WhatsFinance</h1>
            <p class="text-slate-400 text-sm">Painel de Controle Financeiro</p>
        </div>
        
        <form method="POST" class="space-y-5">
            <div class="space-y-1">
                <label class="text-xs font-semibold text-slate-400 ml-1 uppercase tracking-wider">Telegram ID</label>
                <input type="text" name="telegram_id" placeholder="Ex: 123456789" class="w-full input-dark rounded-xl px-4 py-3.5 transition placeholder-slate-600">
            </div>
            <div class="space-y-1">
                <label class="text-xs font-semibold text-slate-400 ml-1 uppercase tracking-wider">Senha de Acesso</label>
                <input type="password" name="password" placeholder="••••••••" class="w-full input-dark rounded-xl px-4 py-3.5 transition placeholder-slate-600">
            </div>
            
            <button type="submit" class="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white font-bold py-4 rounded-xl shadow-lg shadow-blue-900/20 transition-all transform active:scale-[0.98] mt-2">
                Acessar Painel
            </button>
        </form>
        
        <div class="mt-8 pt-6 border-t border-slate-700/50 text-center">
            <a href="/register" class="text-sm text-slate-400 hover:text-white transition flex items-center justify-center gap-2 group-hover:text-blue-400">
                <span>Primeiro acesso?</span>
                <span class="font-semibold underline decoration-transparent hover:decoration-blue-400 transition-all">Criar Senha</span>
            </a>
        </div>
    </div>
</div>
"""

# Conteúdo da Página de Registro (Solicitar Código)
REGISTER_PAGE = """
<div class="flex flex-col items-center justify-center min-h-screen px-4">
    <div class="glass p-8 rounded-3xl w-full max-w-sm relative">
        <button onclick="history.back()" class="absolute top-6 left-6 text-slate-500 hover:text-white transition">← Voltar</button>
        
        <div class="text-center mt-8 mb-8">
            <h2 class="text-2xl font-bold text-white">Autenticação</h2>
            <p class="text-slate-400 text-sm mt-2 px-4">Digite seu ID do Telegram. Enviaremos um código de verificação no seu chat.</p>
        </div>

        <form method="POST" action="/send_code" class="space-y-4">
            <input type="text" name="telegram_id" placeholder="Seu Telegram ID" class="w-full input-dark rounded-xl px-4 py-3.5 text-center text-lg tracking-wide focus:border-blue-500 transition">
            <button class="w-full bg-slate-800 hover:bg-slate-700 text-white font-bold py-4 rounded-xl transition border border-slate-700">Enviar Código</button>
        </form>
    </div>
</div>
"""

# Conteúdo da Página de Verificação (Digitar Código)
VERIFY_PAGE = """
<div class="flex flex-col items-center justify-center min-h-screen px-4">
    <div class="glass p-8 rounded-3xl w-full max-w-sm">
        <div class="text-center mb-6">
            <h2 class="text-2xl font-bold text-white">Definir Senha</h2>
            <p class="text-slate-400 text-xs">Código enviado para o Telegram</p>
        </div>

        <form method="POST" action="/verify_setup" class="space-y-4">
            <input type="hidden" name="telegram_id" value="{{ telegram_id }}">
            
            <div class="relative">
                <input type="text" name="code" placeholder="000000" class="w-full bg-slate-900/80 border border-slate-700 rounded-2xl px-4 py-6 text-center text-3xl font-mono tracking-[0.5em] text-white focus:border-green-500 focus:ring-1 focus:ring-green-500 outline-none transition" maxlength="6" autofocus>
            </div>
            
            <div class="pt-2">
                <label class="text-xs text-slate-400 uppercase font-semibold pl-1">Nova Senha</label>
                <input type="password" name="password" class="w-full mt-1 input-dark rounded-xl px-4 py-3.5 transition" required>
            </div>
            
            <button class="w-full bg-green-600 hover:bg-green-500 text-white font-bold py-4 rounded-xl mt-4 transition shadow-lg shadow-green-900/20">Confirmar</button>
        </form>
    </div>
</div>
"""

# Conteúdo do Dashboard
DASHBOARD_PAGE = """
<nav class="glass sticky top-0 z-40 border-b-0 border-b border-white/5">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-green-400 to-blue-600 flex items-center justify-center text-white font-bold shadow-lg shadow-blue-500/20">W</div>
                <span class="font-bold text-lg tracking-tight hidden sm:block text-white">WhatsFinance</span>
            </div>
            <div class="flex items-center gap-4">
                <div class="hidden md:flex flex-col items-end">
                    <span class="text-sm font-bold text-white">{{ user.name }}</span>
                    <span class="text-xs text-green-400">Online</span>
                </div>
                <a href="/logout" class="text-xs bg-slate-800 text-slate-300 px-4 py-2 rounded-lg hover:bg-red-500/10 hover:text-red-400 transition border border-white/5">Sair</a>
            </div>
        </div>
    </div>
</nav>

<main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="glass p-6 rounded-3xl card-hover relative overflow-hidden group">
            <div class="absolute top-0 right-0 p-6 opacity-50 group-hover:opacity-100 transition duration-500">
                <div class="w-12 h-12 bg-green-500/10 rounded-full flex items-center justify-center text-green-400 text-xl">💰</div>
            </div>
            <p class="text-slate-400 text-xs font-bold uppercase tracking-wider mb-1">Saldo Total</p>
            <h3 class="text-3xl font-bold text-white mb-4">R$ {{ "%.2f"|format(total_acc) }}</h3>
            
            <div class="flex flex-wrap gap-2">
                {% for acc in accs %}
                <div class="flex items-center gap-2 bg-slate-800/50 px-3 py-1.5 rounded-lg border border-white/5">
                    <span class="w-2 h-2 rounded-full bg-green-500"></span>
                    <span class="text-xs text-slate-300">{{ acc.name }}</span>
                    <span class="text-xs font-mono text-green-400">R${{ acc.balance }}</span>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="glass p-6 rounded-3xl card-hover relative overflow-hidden group">
            <div class="absolute top-0 right-0 p-6 opacity-50 group-hover:opacity-100 transition duration-500">
                <div class="w-12 h-12 bg-red-500/10 rounded-full flex items-center justify-center text-red-400 text-xl">💳</div>
            </div>
            <p class="text-slate-400 text-xs font-bold uppercase tracking-wider mb-1">Faturas Abertas</p>
            <h3 class="text-3xl font-bold text-white mb-4">R$ {{ "%.2f"|format(total_invoice) }}</h3>
            
            <div class="flex flex-wrap gap-2">
                {% for inv in invoice_details %}
                <div class="flex items-center gap-2 bg-slate-800/50 px-3 py-1.5 rounded-lg border border-white/5">
                    <span class="w-2 h-2 rounded-full bg-red-500"></span>
                    <span class="text-xs text-slate-300">{{ inv.card }}</span>
                    <span class="text-xs text-slate-500">dia {{ inv.due_day }}</span>
                </div>
                {% endfor %}
            </div>
        </div>

        <a href="https://t.me/{{ bot_username }}" target="_blank" class="glass p-6 rounded-3xl card-hover flex flex-col items-center justify-center text-center cursor-pointer border-dashed border-2 border-slate-700 hover:border-blue-500/50 hover:bg-blue-500/5 transition group">
            <div class="w-14 h-14 bg-blue-600 rounded-2xl flex items-center justify-center text-2xl mb-3 shadow-lg shadow-blue-600/20 group-hover:scale-110 transition">💬</div>
            <h3 class="font-bold text-white">Novo Lançamento</h3>
            <p class="text-slate-400 text-xs mt-1">Abrir chat no Telegram</p>
        </a>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 glass rounded-3xl p-6 md:p-8">
            <div class="flex items-center justify-between mb-8">
                <h3 class="font-bold text-xl text-white flex items-center gap-3">
                    <span class="w-1.5 h-6 bg-blue-500 rounded-full"></span> 
                    Últimas Movimentações
                </h3>
            </div>
            
            <div class="space-y-4">
                {% for t in recent %}
                <div class="flex items-center justify-between p-4 rounded-2xl bg-slate-800/30 hover:bg-slate-800/60 border border-white/5 transition group">
                    <div class="flex items-center gap-4">
                        <div class="w-12 h-12 rounded-2xl flex items-center justify-center text-xl transition-colors {{ 'bg-red-500/10 text-red-400 group-hover:bg-red-500/20' if t.type == 'expense' else 'bg-green-500/10 text-green-400 group-hover:bg-green-500/20' }}">
                            {{ '📉' if t.type == 'expense' else '📈' }}
                        </div>
                        <div>
                            <p class="font-bold text-sm text-slate-200 group-hover:text-white transition">{{ t.description }}</p>
                            <div class="flex items-center gap-2 text-xs text-slate-500 mt-0.5">
                                <span class="bg-slate-700/50 px-1.5 py-0.5 rounded">{{ t.category or 'Geral' }}</span>
                                <span>•</span>
                                <span class="uppercase tracking-wide">{{ t.payment_method or 'Outro' }}</span>
                            </div>
                        </div>
                    </div>
                    <span class="font-bold font-mono text-sm sm:text-base {{ 'text-red-400' if t.type == 'expense' else 'text-green-400' }}">
                        {{ '-' if t.type == 'expense' else '+' }}R$ {{ "%.2f"|format(t.amount) }}
                    </span>
                </div>
                {% endfor %}
                
                {% if not recent %}
                <div class="text-center py-12">
                    <div class="text-4xl mb-3">📭</div>
                    <p class="text-slate-500">Nenhuma transação recente.</p>
                </div>
                {% endif %}
            </div>
        </div>

        <div class="glass rounded-3xl p-6 md:p-8 flex flex-col">
            <h3 class="font-bold text-lg text-white mb-6">Fluxo Financeiro</h3>
            <div class="flex-1 flex items-center justify-center relative min-h-[250px]">
                <canvas id="financeChart"></canvas>
            </div>
            <div class="mt-6 grid grid-cols-2 gap-4 text-center">
                <div class="bg-green-500/5 rounded-xl p-3 border border-green-500/10">
                    <p class="text-xs text-green-400 uppercase font-bold">Entradas</p>
                    <p class="text-lg font-bold text-white mt-1" id="totalIncome">R$ 0.00</p>
                </div>
                <div class="bg-red-500/5 rounded-xl p-3 border border-red-500/10">
                    <p class="text-xs text-red-400 uppercase font-bold">Saídas</p>
                    <p class="text-lg font-bold text-white mt-1" id="totalExpense">R$ 0.00</p>
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

    // Atualiza os totais visuais
    document.getElementById('totalIncome').innerText = 'R$ ' + incomes.toFixed(2);
    document.getElementById('totalExpense').innerText = 'R$ ' + expenses.toFixed(2);

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Entradas', 'Saídas'],
            datasets: [{
                data: [incomes, expenses],
                backgroundColor: ['#4ade80', '#f87171'],
                borderColor: '#1e293b',
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '75%',
            plugins: {
                legend: { display: false }
            }
        }
    });
</script>
"""