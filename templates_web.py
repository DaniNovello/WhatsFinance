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
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #0f172a; color: #e2e8f0; }
        .glass { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .gradient-text { background: linear-gradient(to right, #4ade80, #3b82f6); -webkit-background-clip: text; color: transparent; }
        .card-hover { transition: all 0.3s ease; }
        .card-hover:hover { transform: translateY(-2px); box-shadow: 0 10px 20px -10px rgba(0,0,0,0.5); }
    </style>
</head>
<body class="antialiased min-h-screen flex flex-col bg-[url('https://tailwindcss.com/_next/static/media/hero-dark.9a75e549.png')] bg-cover bg-fixed">
    
    {% with messages = get_flashed_messages() %}
    {% if messages %}
        <div id="toast" class="fixed top-5 left-1/2 transform -translate-x-1/2 z-50 bg-blue-600/90 backdrop-blur text-white px-6 py-3 rounded-full shadow-2xl animate-bounce text-sm font-semibold">
            {{ messages[0] }}
        </div>
        <script>setTimeout(() => document.getElementById('toast').remove(), 4000);</script>
    {% endif %}
    {% endwith %}
    
    {% block content %}{% endblock %}
</body>
</html>
"""

LOGIN_PAGE = """
{% extends "base" %}
{% block content %}
<div class="flex flex-col items-center justify-center min-h-screen px-4 py-12">
    <div class="glass p-8 rounded-3xl shadow-2xl w-full max-w-md relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-green-400 to-blue-500"></div>
        
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold mb-2 gradient-text tracking-tight">WhatsFinance</h1>
            <p class="text-slate-400 text-sm">Controle financeiro inteligente via Chat.</p>
        </div>
        
        <form method="POST" class="space-y-5">
            <div>
                <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Telegram ID</label>
                <input type="text" name="telegram_id" placeholder="Ex: 123456789" class="w-full bg-slate-900/50 border border-slate-700 rounded-xl px-4 py-3.5 focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500 transition text-white placeholder-slate-600">
            </div>
            <div>
                <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Senha</label>
                <input type="password" name="password" placeholder="••••••••" class="w-full bg-slate-900/50 border border-slate-700 rounded-xl px-4 py-3.5 focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500 transition text-white placeholder-slate-600">
            </div>
            
            <button type="submit" class="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-400 hover:to-emerald-500 text-white font-bold py-4 rounded-xl shadow-lg shadow-green-500/20 transition transform active:scale-[0.98]">
                Entrar no Painel
            </button>
        </form>
        
        <div class="mt-8 pt-6 border-t border-slate-700/50 text-center">
            <a href="/register" class="text-sm text-blue-400 hover:text-blue-300 transition font-medium">Primeiro acesso? Criar senha</a>
        </div>
    </div>
</div>
{% endblock %}
"""

REGISTER_PAGE = """
{% extends "base" %}
{% block content %}
<div class="flex flex-col items-center justify-center min-h-screen px-4">
    <div class="glass p-8 rounded-3xl w-full max-w-md relative">
        <button onclick="history.back()" class="absolute top-6 left-6 text-slate-400 hover:text-white">← Voltar</button>
        
        <div class="text-center mt-6 mb-8">
            <div class="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl">🔐</div>
            <h2 class="text-2xl font-bold">Autenticação Segura</h2>
            <p class="text-slate-400 text-sm mt-2">Digite seu ID. Enviaremos um código no seu Telegram para validar que é você.</p>
        </div>

        <form method="POST" action="/send_code">
            <input type="text" name="telegram_id" placeholder="Seu Telegram ID" class="w-full bg-slate-900/50 border border-slate-700 rounded-xl px-4 py-3.5 mb-4 text-white focus:border-blue-500 transition">
            <button class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-4 rounded-xl transition shadow-lg shadow-blue-600/20">Enviar Código</button>
        </form>
    </div>
</div>
{% endblock %}
"""

VERIFY_PAGE = """
{% extends "base" %}
{% block content %}
<div class="flex flex-col items-center justify-center min-h-screen px-4">
    <div class="glass p-8 rounded-3xl w-full max-w-md">
        <h2 class="text-2xl font-bold mb-6 text-center">Definir Senha</h2>
        <form method="POST" action="/verify_setup" class="space-y-4">
            <input type="hidden" name="telegram_id" value="{{ telegram_id }}">
            
            <div class="bg-slate-800/50 p-4 rounded-xl border border-slate-700 text-center mb-4">
                <p class="text-xs text-slate-400 uppercase tracking-widest mb-2">Código enviado ao Bot</p>
                <input type="text" name="code" placeholder="000000" class="w-full bg-transparent text-center text-3xl font-mono tracking-[0.5em] focus:outline-none text-white font-bold" maxlength="6" autofocus>
            </div>
            
            <div>
                <label class="text-xs text-slate-400 uppercase font-semibold pl-1">Nova Senha Web</label>
                <input type="password" name="password" class="w-full mt-1 bg-slate-900/50 border border-slate-700 rounded-xl px-4 py-3.5 text-white focus:border-green-500 transition">
            </div>
            
            <button class="w-full bg-green-600 hover:bg-green-500 text-white font-bold py-4 rounded-xl mt-4 transition">Confirmar e Entrar</button>
        </form>
    </div>
</div>
{% endblock %}
"""

DASHBOARD_PAGE = """
{% extends "base" %}
{% block content %}
<nav class="glass sticky top-0 z-40 border-b border-white/5">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-green-400 to-blue-600 flex items-center justify-center text-white font-bold">W</div>
                <span class="font-bold text-lg tracking-tight hidden sm:block">WhatsFinance</span>
            </div>
            <div class="flex items-center gap-4">
                <span class="text-xs sm:text-sm text-slate-400">Olá, <strong class="text-white">{{ user.name }}</strong></span>
                <a href="/logout" class="text-xs bg-red-500/10 text-red-400 px-3 py-1.5 rounded-lg hover:bg-red-500/20 border border-red-500/20 transition">Sair</a>
            </div>
        </div>
    </div>
</nav>

<main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="glass p-6 rounded-3xl card-hover relative overflow-hidden group">
            <div class="absolute -right-6 -top-6 w-32 h-32 bg-green-500/20 rounded-full blur-2xl group-hover:bg-green-500/30 transition"></div>
            <p class="text-slate-400 text-xs font-bold uppercase tracking-wider">Saldo Total</p>
            <h3 class="text-3xl font-bold text-white mt-1">R$ {{ "%.2f"|format(total_acc) }}</h3>
            <div class="mt-4 flex flex-wrap gap-2">
                {% for acc in accs %}
                <span class="bg-slate-800/80 border border-slate-700 px-2.5 py-1 rounded-md text-xs text-slate-300">{{ acc.name }}: <span class="text-green-400">R$ {{ acc.balance }}</span></span>
                {% endfor %}
            </div>
        </div>

        <div class="glass p-6 rounded-3xl card-hover relative overflow-hidden group">
            <div class="absolute -right-6 -top-6 w-32 h-32 bg-red-500/20 rounded-full blur-2xl group-hover:bg-red-500/30 transition"></div>
            <p class="text-slate-400 text-xs font-bold uppercase tracking-wider">Faturas Abertas</p>
            <h3 class="text-3xl font-bold text-white mt-1">R$ {{ "%.2f"|format(total_invoice) }}</h3>
            <div class="mt-4 flex flex-wrap gap-2">
                {% for inv in invoice_details %}
                <span class="bg-slate-800/80 border border-slate-700 px-2.5 py-1 rounded-md text-xs text-slate-300">{{ inv.card }} <span class="text-slate-500">vence {{ inv.due_day }}</span></span>
                {% endfor %}
            </div>
        </div>

        <a href="https://t.me/{{ bot_username }}" target="_blank" class="glass p-6 rounded-3xl card-hover flex flex-col items-center justify-center text-center group cursor-pointer border border-blue-500/30 hover:border-blue-500/60 bg-blue-600/5">
            <div class="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center text-2xl mb-3 shadow-lg shadow-blue-500/30 group-hover:scale-110 transition">💬</div>
            <h3 class="font-bold text-white">Novo Lançamento</h3>
            <p class="text-blue-200/60 text-xs mt-1">Abrir Chat no Telegram</p>
        </a>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <div class="lg:col-span-2 glass rounded-3xl p-6">
            <div class="flex items-center justify-between mb-6">
                <h3 class="font-bold text-lg flex items-center gap-2">
                    <span class="w-2 h-6 bg-blue-500 rounded-full"></span> Últimas Movimentações
                </h3>
                <span class="text-xs text-slate-500 bg-slate-800 px-2 py-1 rounded">Hoje</span>
            </div>
            
            <div class="space-y-3">
                {% for t in recent %}
                <div class="flex items-center justify-between p-4 rounded-2xl bg-slate-800/40 hover:bg-slate-800/60 transition border border-white/5 group">
                    <div class="flex items-center gap-4">
                        <div class="w-10 h-10 rounded-full flex items-center justify-center text-lg {{ 'bg-red-500/10 text-red-400' if t.type == 'expense' else 'bg-green-500/10 text-green-400' }}">
                            {{ '🏷️' if t.type == 'expense' else '💰' }}
                        </div>
                        <div>
                            <p class="font-bold text-sm text-white group-hover:text-blue-400 transition">{{ t.description }}</p>
                            <div class="flex items-center gap-2 text-xs text-slate-500">
                                <span>{{ t.category or 'Geral' }}</span>
                                <span class="w-1 h-1 bg-slate-600 rounded-full"></span>
                                <span class="uppercase">{{ t.payment_method or 'Outro' }}</span>
                            </div>
                        </div>
                    </div>
                    <span class="font-bold font-mono {{ 'text-red-400' if t.type == 'expense' else 'text-green-400' }}">
                        {{ '-' if t.type == 'expense' else '+' }}R$ {{ "%.2f"|format(t.amount) }}
                    </span>
                </div>
                {% endfor %}
                
                {% if not recent %}
                <div class="text-center py-10 text-slate-500">Nenhuma transação recente.</div>
                {% endif %}
            </div>
        </div>

        <div class="glass rounded-3xl p-6 flex flex-col">
            <h3 class="font-bold text-lg mb-4">Resumo Visual</h3>
            <div class="flex-1 flex items-center justify-center relative">
                <canvas id="financeChart"></canvas>
            </div>
            <div class="mt-4 text-center">
                 <p class="text-xs text-slate-500">Entradas vs Saídas (Últimos 5)</p>
            </div>
        </div>
    </div>
</main>

<script>
    // Dados simples para o gráfico baseados nas ultimas transações
    const ctx = document.getElementById('financeChart').getContext('2d');
    
    // Processando dados do backend injetados pelo Jinja
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
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            cutout: '70%',
            plugins: {
                legend: { position: 'bottom', labels: { color: '#94a3b8', usePointStyle: true } }
            }
        }
    });
</script>
{% endblock %}
"""