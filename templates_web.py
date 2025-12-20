# Logo SVG Zenith
LOGO_SVG = """<svg class="w-8 h-8 text-blue-500" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M13 3L19 9M19 9L13 15M19 9H5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M5 15L11 21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

# Script Universal para Modais (Essencial para os botões funcionarem)
MODAL_SCRIPT = """
<script>
    function toggleModal(modalId, show) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        const backdrop = modal.querySelector('.modal-backdrop');
        const panel = modal.querySelector('.modal-panel');
        
        if (show) {
            modal.classList.remove('hidden');
            // Pequeno delay para permitir a transição CSS
            setTimeout(() => {
                backdrop.classList.remove('opacity-0');
                panel.classList.remove('opacity-0', 'translate-y-4', 'sm:translate-y-0', 'sm:scale-95');
            }, 10);
        } else {
            backdrop.classList.add('opacity-0');
            panel.classList.add('opacity-0', 'translate-y-4', 'sm:translate-y-0', 'sm:scale-95');
            setTimeout(() => {
                modal.classList.add('hidden');
            }, 300);
        }
    }
</script>
"""

# --- MODAL DE NOVO REGISTRO ---
ADD_MODAL = """
<div id="addModal" class="fixed inset-0 z-[60] hidden" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="fixed inset-0 bg-black/70 backdrop-blur-sm transition-opacity opacity-0 modal-backdrop" onclick="toggleModal('addModal', false)"></div>
    <div class="fixed inset-0 z-10 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4 text-center sm:p-0">
            <div class="relative transform overflow-hidden rounded-2xl bg-[#0F172A] border border-slate-700 text-left shadow-2xl transition-all sm:my-8 sm:w-full sm:max-w-lg opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95 modal-panel">
                <div class="bg-[#1E293B] px-4 py-4 border-b border-slate-700 flex justify-between items-center">
                    <h3 class="text-base font-bold text-white flex items-center gap-2">
                        <div class="w-2 h-6 bg-blue-500 rounded-full"></div> Novo Lançamento
                    </h3>
                    <button type="button" onclick="toggleModal('addModal', false)" class="text-slate-400 hover:text-white transition bg-slate-800/50 p-1 rounded-full">✕</button>
                </div>
                <form action="/transaction/new" method="POST" class="p-6 space-y-5">
                    <div class="grid grid-cols-2 gap-2 p-1 bg-slate-900 rounded-lg border border-slate-800">
                        <label class="cursor-pointer"><input type="radio" name="type" value="expense" checked class="peer sr-only"><div class="text-center py-2.5 rounded-md text-slate-500 text-xs font-bold uppercase tracking-wider peer-checked:bg-red-500/10 peer-checked:text-red-500 transition">Saída</div></label>
                        <label class="cursor-pointer"><input type="radio" name="type" value="income" class="peer sr-only"><div class="text-center py-2.5 rounded-md text-slate-500 text-xs font-bold uppercase tracking-wider peer-checked:bg-green-500/10 peer-checked:text-green-500 transition">Entrada</div></label>
                    </div>
                    <div class="space-y-1"><label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Descrição</label><input type="text" name="description" required class="w-full input-dark rounded-lg px-4 py-3 text-sm" placeholder="Ex: Supermercado"></div>
                    <div class="grid grid-cols-2 gap-4">
                        <div class="space-y-1"><label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Valor (R$)</label><input type="number" step="0.01" name="amount" required class="w-full input-dark rounded-lg px-4 py-3 text-sm font-mono" placeholder="0.00"></div>
                        <div class="space-y-1"><label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Categoria</label><input type="text" name="category" class="w-full input-dark rounded-lg px-4 py-3 text-sm" placeholder="Geral"></div>
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <div class="space-y-1"><label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Método</label><select name="payment_method" class="w-full input-dark rounded-lg px-3 py-3 text-sm bg-[#111827]"><option value="debit_card">Débito</option><option value="credit_card">Crédito</option><option value="pix">Pix</option><option value="money">Dinheiro</option></select></div>
                        <div class="space-y-1"><label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Conta</label><select name="account_id" class="w-full input-dark rounded-lg px-3 py-3 text-sm bg-[#111827]"><option value="">-- Selecionar --</option>{% for acc in accounts %}<option value="{{ acc.id }}">{{ acc.name }}</option>{% endfor %}{% for acc in accs %}<option value="{{ acc.id }}">{{ acc.name }}</option>{% endfor %}</select></div>
                    </div>
                    <div class="space-y-1"><label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Cartão (Se Crédito)</label><select name="card_id" class="w-full input-dark rounded-lg px-3 py-3 text-sm bg-[#111827]"><option value="">-- Nenhum --</option>{% for c in cards %}<option value="{{ c.id }}">{{ c.name }}</option>{% endfor %}</select></div>
                    <div class="space-y-1"><label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Data</label><input type="datetime-local" name="date" value="{{ now }}" class="w-full input-dark rounded-lg px-4 py-3 text-sm"></div>
                    <div class="pt-4 border-t border-slate-800">
                        <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-blue-900/20 transition transform active:scale-[0.98] text-sm">Confirmar Lançamento</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
"""

# --- MODAL DE FILTROS ---
FILTER_MODAL = """
<div id="filterModal" class="fixed inset-0 z-[60] hidden" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="fixed inset-0 bg-black/70 backdrop-blur-sm transition-opacity opacity-0 modal-backdrop" onclick="toggleModal('filterModal', false)"></div>
    <div class="fixed inset-0 z-10 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4 text-center sm:p-0">
            <div class="relative transform overflow-hidden rounded-2xl bg-[#0F172A] border border-slate-700 text-left shadow-2xl transition-all sm:my-8 sm:w-full sm:max-w-md opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95 modal-panel">
                <div class="bg-[#1E293B] px-4 py-4 border-b border-slate-700 flex justify-between items-center">
                    <h3 class="text-base font-bold text-white flex items-center gap-2">
                        <svg class="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path></svg> 
                        Filtrar Extrato
                    </h3>
                    <button type="button" onclick="toggleModal('filterModal', false)" class="text-slate-400 hover:text-white transition bg-slate-800/50 p-1 rounded-full">✕</button>
                </div>
                <form action="/transactions" method="GET" class="p-6 space-y-5">
                    <div class="space-y-1">
                        <label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Buscar por Nome</label>
                        <div class="relative">
                            <input type="text" name="search" value="{{ filters.search if filters.search else '' }}" class="w-full input-dark rounded-lg pl-10 pr-4 py-3 text-sm focus:ring-purple-500/20" placeholder="Ex: Mercado, Uber...">
                            <svg class="w-4 h-4 text-slate-500 absolute left-3 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                        </div>
                    </div>
                    <div class="space-y-1">
                        <label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Tipo de Transação</label>
                        <select name="type" class="w-full input-dark rounded-lg px-3 py-3 text-sm bg-[#111827]">
                            <option value="">Todas</option>
                            <option value="income" {{ 'selected' if filters.type == 'income' else '' }}>Apenas Entradas</option>
                            <option value="expense" {{ 'selected' if filters.type == 'expense' else '' }}>Apenas Saídas</option>
                        </select>
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <div class="space-y-1"><label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">De</label><input type="date" name="start_date" value="{{ filters.start_date if filters.start_date else '' }}" class="w-full input-dark rounded-lg px-3 py-3 text-sm text-slate-300"></div>
                        <div class="space-y-1"><label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Até</label><input type="date" name="end_date" value="{{ filters.end_date if filters.end_date else '' }}" class="w-full input-dark rounded-lg px-3 py-3 text-sm text-slate-300"></div>
                    </div>
                    <div class="pt-4 border-t border-slate-800 flex gap-3">
                        <a href="/transactions" class="flex-1 py-3.5 rounded-xl border border-slate-700 text-slate-400 text-sm font-bold hover:bg-slate-800 transition text-center">Limpar</a>
                        <button type="submit" class="flex-[2] bg-purple-600 hover:bg-purple-500 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-purple-900/20 transition transform active:scale-[0.98] text-sm">Aplicar Filtros</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
"""

# --- PÁGINAS ---

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
        .glass { background: rgba(17, 24, 39, 0.75); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); border: 1px solid rgba(255, 255, 255, 0.06); box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
        .input-dark { background: #111827; border: 1px solid #374151; color: white; transition: all 0.2s; }
        .input-dark:focus { border-color: #3B82F6; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2); outline: none; }
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
    </style>
</head>
<body class="antialiased min-h-screen flex flex-col bg-[#0B0F19]">
    {% with messages = get_flashed_messages() %}
    {% if messages %}
        <div id="toast-container" class="fixed bottom-6 right-6 z-[80] bg-[#1F2937] border-l-4 border-blue-500 text-white px-5 py-4 rounded shadow-2xl flex items-center gap-4 animate-bounce">
            <div><h4 class="font-semibold text-sm">Notificação</h4><p class="text-slate-300 text-xs">{{ messages[0] }}</p></div>
        </div>
        <script>setTimeout(() => document.getElementById('toast-container').remove(), 4000);</script>
    {% endif %}
    {% endwith %}
    {content_body}
</body>
</html>
"""

LOGIN_PAGE = f"""
<div class="flex flex-col items-center justify-center min-h-screen w-full bg-[#0B0F19] relative overflow-hidden">
    <div class="absolute inset-0 bg-gradient-to-br from-[#0f172a] to-[#020617] -z-10"></div>
    
    <div class="w-full max-w-sm px-4">
        <div class="text-center mb-10">
            <div class="inline-flex items-center justify-center p-4 rounded-2xl bg-slate-800/50 border border-slate-700/50 shadow-2xl mb-6">
                {LOGO_SVG}
            </div>
            <h1 class="text-3xl font-bold text-white tracking-tight mb-2">Zenith</h1>
            <p class="text-slate-400 text-sm">Sistema de Inteligência Financeira</p>
        </div>
        
        <div class="glass p-8 rounded-2xl shadow-2xl border border-slate-700/50">
            <form method="POST" class="space-y-6">
                <div class="space-y-1.5">
                    <label class="text-xs font-bold text-slate-500 uppercase tracking-wider ml-1">ID de Acesso</label>
                    <input type="text" name="telegram_id" class="w-full input-dark rounded-xl px-4 py-3.5 text-sm" placeholder="Seu Telegram ID">
                </div>
                <div class="space-y-1.5">
                    <label class="text-xs font-bold text-slate-500 uppercase tracking-wider ml-1">Senha</label>
                    <input type="password" name="password" class="w-full input-dark rounded-xl px-4 py-3.5 text-sm" placeholder="••••••••">
                </div>
                
                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3.5 rounded-xl shadow-lg transition text-sm mt-2">
                    Entrar no Sistema
                </button>
            </form>
        </div>
        
        <div class="mt-8 text-center">
            <a href="/register" class="text-xs font-medium text-slate-500 hover:text-blue-400 transition">Primeiro acesso? Validar Dispositivo</a>
        </div>
    </div>
</div>
"""

REGISTER_PAGE = """
<div class="flex flex-col items-center justify-center min-h-screen w-full bg-[#0B0F19]">
    <div class="w-full max-w-sm px-4">
        <div class="glass p-8 rounded-2xl border border-slate-800 relative">
            <button onclick="history.back()" class="absolute top-6 left-6 text-slate-500 hover:text-white transition text-xs">← Voltar</button>
            <div class="text-center mt-6 mb-8"><h2 class="text-xl font-bold text-white">Novo Acesso Zenith</h2><p class="text-slate-500 text-sm mt-2">Validação via Telegram</p></div>
            <form method="POST" action="/send_code" class="space-y-4">
                <input type="text" name="telegram_id" placeholder="Seu Telegram ID" class="w-full input-dark rounded-xl px-4 py-3.5 text-center text-lg focus:border-blue-500 transition">
                <button class="w-full bg-slate-800 hover:bg-slate-700 text-white font-medium py-3.5 rounded-xl border border-slate-700 transition text-sm">Enviar Código</button>
            </form>
        </div>
    </div>
</div>
"""

VERIFY_PAGE = """
<div class="flex flex-col items-center justify-center min-h-screen w-full bg-[#0B0F19]">
    <div class="w-full max-w-sm px-4">
        <div class="glass p-8 rounded-2xl border border-slate-800">
            <h2 class="text-xl font-bold text-white text-center mb-1">Definir Senha</h2>
            <p class="text-slate-500 text-xs text-center mb-8">Código enviado ao chat</p>
            <form method="POST" action="/verify_setup" class="space-y-5">
                <input type="hidden" name="telegram_id" value="{{ telegram_id }}">
                <input type="text" name="code" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-4 text-center text-2xl font-mono tracking-[0.5em] text-white outline-none" maxlength="6" autofocus placeholder="000000">
                <div><label class="text-xs font-medium text-slate-400 uppercase tracking-wide">Nova Senha</label><input type="password" name="password" class="w-full mt-1 input-dark rounded-xl px-4 py-3.5 text-sm" required></div>
                <button class="w-full bg-green-600 hover:bg-green-500 text-white font-medium py-3.5 rounded-xl mt-2 transition text-sm">Confirmar</button>
            </form>
        </div>
    </div>
</div>
"""

NAVBAR = f"""
<nav class="sticky top-0 z-40 bg-[#0B0F19]/80 backdrop-blur-xl border-b border-slate-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
            <div class="flex items-center gap-3">{LOGO_SVG}<span class="font-bold text-white tracking-tight text-lg">Zenith</span></div>
            <div class="flex items-center gap-4">
                <span class="text-xs font-medium text-slate-400 hidden sm:block bg-slate-800/50 px-3 py-1 rounded-full border border-slate-700">{{{{ user.name }}}}</span>
                <a href="/logout" class="text-xs bg-slate-800 text-slate-300 px-3 py-1.5 rounded-lg hover:bg-red-500/10 hover:text-red-400 transition border border-slate-700 font-medium">Sair</a>
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
                <div class="flex justify-between text-xs text-slate-400 border-b border-dashed border-slate-800 pb-1 last:border-0"><span>{{ acc.name }}</span><span class="text-white font-mono">R$ {{ acc.balance }}</span></div>
                {% endfor %}
            </div>
        </div>
        <div class="glass p-5 rounded-xl border border-slate-800">
            <p class="text-slate-500 text-xs font-semibold uppercase tracking-wider mb-1">Faturas</p>
            <h3 class="text-2xl font-bold text-white mb-3 font-mono">R$ {{ "%.2f"|format(total_invoice) }}</h3>
            <div class="flex flex-col gap-1 max-h-24 overflow-y-auto no-scrollbar">
                {% for inv in invoice_details %}
                <div class="flex justify-between text-xs text-slate-400 border-b border-dashed border-slate-800 pb-1 last:border-0"><span>{{ inv.card }}</span><span class="text-white font-mono">Vence {{ inv.due_day }}</span></div>
                {% endfor %}
            </div>
        </div>
        <div onclick="toggleModal('addModal', true)" class="glass p-5 rounded-xl border border-dashed border-slate-700 hover:bg-blue-500/5 transition flex items-center justify-center gap-3 group cursor-pointer h-full">
            <div class="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white shadow-lg group-hover:scale-110 transition">＋</div>
            <div class="text-left"><h3 class="font-semibold text-white text-sm">Novo Lançamento</h3><p class="text-slate-500 text-xs">Adicionar manual</p></div>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-md font-semibold text-white">Recentes</h3>
                <a href="/transactions" class="text-xs text-blue-400 hover:text-blue-300 font-medium">Ver Extrato →</a>
            </div>
            <div class="glass rounded-xl border border-slate-800 overflow-hidden">
                <div class="divide-y divide-slate-800/50">
                    {% for t in recent %}
                    <div class="p-4 flex justify-between items-center hover:bg-slate-800/30 transition">
                        <div class="flex items-center gap-3">
                            <div class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold {{ 'bg-red-500/10 text-red-500' if t.type == 'expense' else 'bg-green-500/10 text-green-500' }}">{{ '↓' if t.type == 'expense' else '↑' }}</div>
                            <div><p class="text-white text-sm font-medium">{{ t.description }}</p><p class="text-[10px] text-slate-500 uppercase">{{ t.category }}</p></div>
                        </div>
                        <span class="font-mono text-sm font-medium {{ 'text-red-400' if t.type == 'expense' else 'text-green-400' }}">{{ '-' if t.type == 'expense' else '+' }}{{ "%.2f"|format(t.amount) }}</span>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
        <div class="glass p-5 rounded-xl border border-slate-800 flex flex-col justify-center">
            <h3 class="text-xs font-semibold text-white mb-4 uppercase tracking-wider text-center">Balanço</h3>
            <div class="relative h-[180px] w-full"><canvas id="financeChart"></canvas></div>
        </div>
    </div>
</main>
""" + ADD_MODAL + MODAL_SCRIPT + """
<script>
    const ctx = document.getElementById('financeChart').getContext('2d');
    const transactions = {{ recent_json | safe }};
    const expenses = transactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + parseFloat(t.amount), 0);
    const incomes = transactions.filter(t => t.type === 'income').reduce((sum, t) => sum + parseFloat(t.amount), 0);
    new Chart(ctx, {
        type: 'doughnut',
        data: { labels: ['Entradas', 'Saídas'], datasets: [{ data: [incomes, expenses], backgroundColor: ['#10B981', '#EF4444'], borderWidth: 0 }] },
        options: { responsive: true, maintainAspectRatio: false, cutout: '85%', plugins: { legend: { display: false } } }
    });
</script>
"""

# Extrato (Listagem) com Botão de Filtro e Modal Injetado
TRANSACTIONS_LIST_PAGE = NAVBAR + """
<main class="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <div class="flex items-center gap-4">
            <a href="/dashboard" class="w-10 h-10 rounded-xl border border-slate-700 flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-800 transition bg-slate-800/30">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
            </a>
            <div>
                <h1 class="text-2xl font-bold text-white tracking-tight">Extrato</h1>
                <p class="text-xs text-slate-500">Histórico completo de transações</p>
            </div>
        </div>
        
        <div class="flex gap-3 w-full md:w-auto">
            <button onclick="toggleModal('filterModal', true)" class="flex-1 md:flex-none px-4 py-2.5 text-xs font-bold text-slate-300 bg-slate-800 border border-slate-700 rounded-xl hover:bg-slate-700 hover:text-white transition flex items-center justify-center gap-2">
                <svg class="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path></svg>
                Filtros Avançados
            </button>
            
            <button onclick="toggleModal('addModal', true)" class="flex-1 md:flex-none px-5 py-2.5 text-xs bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold shadow-lg shadow-blue-900/20 transition flex items-center justify-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg> Novo
            </button>
        </div>
    </div>

    {% if filters.type or filters.search or filters.start_date %}
    <div class="mb-6 flex flex-wrap gap-2">
        {% if filters.search %}<span class="px-3 py-1 rounded-full bg-purple-500/10 text-purple-400 text-xs border border-purple-500/20">Busca: {{ filters.search }}</span>{% endif %}
        {% if filters.type %}<span class="px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 text-xs border border-blue-500/20">Tipo: {{ filters.type }}</span>{% endif %}
        {% if filters.start_date %}<span class="px-3 py-1 rounded-full bg-slate-800 text-slate-400 text-xs border border-slate-700">Data: {{ filters.start_date }} → {{ filters.end_date }}</span>{% endif %}
        <a href="/transactions" class="px-3 py-1 rounded-full bg-red-500/10 text-red-400 text-xs border border-red-500/20 hover:bg-red-500/20">Limpar X</a>
    </div>
    {% endif %}

    <div class="glass rounded-2xl border border-slate-800 overflow-hidden shadow-xl">
        <div class="block md:hidden divide-y divide-slate-800/50">
            {% for t in transactions %}
            <div class="p-5 active:bg-slate-800/30 transition">
                <div class="flex justify-between items-start mb-2">
                    <div class="flex flex-col gap-1">
                        <span class="text-[10px] text-slate-500 font-mono flex items-center gap-1">
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                            {{ t.transaction_date[:10] }}
                        </span>
                        <p class="text-white font-bold text-sm">{{ t.description }}</p>
                    </div>
                    <div class="text-right">
                        <span class="block font-mono text-sm font-bold {{ 'text-red-400' if t.type == 'expense' else 'text-green-400' }}">
                            {{ '-' if t.type == 'expense' else '+' }}{{ "%.2f"|format(t.amount) }}
                        </span>
                    </div>
                </div>
                <div class="flex justify-between items-center mt-3">
                    <div class="flex gap-2">
                        <span class="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-slate-400 border border-slate-700">{{ t.category }}</span>
                        <span class="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-slate-400 border border-slate-700 uppercase">{{ t.payment_method }}</span>
                    </div>
                    <div class="flex gap-3 opacity-80">
                        <a href="/transaction/edit/{{ t.id }}" class="text-blue-400 text-[10px] font-bold uppercase tracking-wider">Editar</a>
                        <a href="/transaction/delete/{{ t.id }}" onclick="return confirm('Excluir?')" class="text-red-400 text-[10px] font-bold uppercase tracking-wider">Excluir</a>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="hidden md:block overflow-x-auto">
            <table class="w-full text-left text-sm text-slate-400">
                <thead class="bg-slate-900/80 text-xs uppercase font-bold text-slate-500 border-b border-slate-700">
                    <tr><th class="px-6 py-4">Data</th><th class="px-6 py-4">Descrição</th><th class="px-6 py-4">Método</th><th class="px-6 py-4">Valor</th><th class="px-6 py-4 text-right">Ações</th></tr>
                </thead>
                <tbody class="divide-y divide-slate-800/50">
                    {% for t in transactions %}
                    <tr class="hover:bg-slate-800/30 transition group">
                        <td class="px-6 py-4 whitespace-nowrap font-mono text-xs">{{ t.transaction_date[:10] }}</td>
                        <td class="px-6 py-4"><p class="text-white font-medium">{{ t.description }}</p><span class="text-xs text-slate-500">{{ t.category or 'Geral' }}</span></td>
                        <td class="px-6 py-4"><span class="px-2 py-1 rounded text-xs bg-slate-800 border border-slate-700 uppercase font-medium">{{ t.payment_method }}</span></td>
                        <td class="px-6 py-4 whitespace-nowrap font-mono font-bold {{ 'text-red-400' if t.type == 'expense' else 'text-green-400' }}">{{ '-' if t.type == 'expense' else '+' }}R$ {{ "%.2f"|format(t.amount) }}</td>
                        <td class="px-6 py-4 text-right"><div class="flex justify-end gap-3 opacity-0 group-hover:opacity-100 transition"><a href="/transaction/edit/{{ t.id }}" class="text-blue-400 text-xs font-bold border border-blue-500/20 px-2 py-1 rounded hover:bg-blue-500/10">EDITAR</a><a href="/transaction/delete/{{ t.id }}" class="text-red-400 text-xs font-bold border border-red-500/20 px-2 py-1 rounded hover:bg-red-500/10">EXCLUIR</a></div></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        {% if not transactions %}
        <div class="p-16 text-center">
            <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-800/50 mb-4">
                <svg class="w-8 h-8 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
            </div>
            <h3 class="text-lg font-medium text-white">Nenhum registro encontrado</h3>
            <p class="text-slate-500 text-sm mt-1">Tente ajustar seus filtros ou adicione uma nova transação.</p>
        </div>
        {% endif %}
    </div>
</main>
""" + ADD_MODAL + FILTER_MODAL + MODAL_SCRIPT

TRANSACTION_FORM_PAGE = """
<div class="flex flex-col items-center justify-center min-h-screen px-4 py-8 bg-[#0B0F19]">
    <div class="glass p-6 rounded-xl w-full max-w-md border border-slate-800 relative">
        <button onclick="history.back()" class="absolute top-6 left-6 text-slate-500 hover:text-white transition text-xs flex items-center gap-1">← Cancelar</button>
        <h2 class="text-lg font-bold text-center mb-6 text-white">{{ 'Editar' if t else 'Novo' }} Lançamento</h2>
        <form method="POST" class="space-y-5">
            <div class="grid grid-cols-2 gap-2 p-1 bg-slate-900 rounded-lg border border-slate-800">
                <label class="cursor-pointer"><input type="radio" name="type" value="expense" class="peer sr-only" {{ 'checked' if not t or t.type == 'expense' else '' }}><div class="text-center py-2 rounded-md text-slate-500 text-xs font-bold uppercase tracking-wider peer-checked:bg-red-500/10 peer-checked:text-red-500 transition">Saída</div></label>
                <label class="cursor-pointer"><input type="radio" name="type" value="income" class="peer sr-only" {{ 'checked' if t and t.type == 'income' else '' }}><div class="text-center py-2 rounded-md text-slate-500 text-xs font-bold uppercase tracking-wider peer-checked:bg-green-500/10 peer-checked:text-green-500 transition">Entrada</div></label>
            </div>
            <div class="space-y-1"><label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Descrição</label><input type="text" name="description" value="{{ t.description if t else '' }}" required class="w-full input-dark rounded-lg px-4 py-3 text-sm" placeholder="Ex: Almoço"></div>
            <div class="grid grid-cols-2 gap-4">
                <div class="space-y-1"><label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Valor</label><input type="number" step="0.01" name="amount" value="{{ t.amount if t else '' }}" required class="w-full input-dark rounded-lg px-4 py-3 text-sm font-mono" placeholder="0.00"></div>
                <div class="space-y-1"><label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Categoria</label><input type="text" name="category" value="{{ t.category if t else '' }}" class="w-full input-dark rounded-lg px-4 py-3 text-sm" placeholder="Geral"></div>
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div class="space-y-1"><label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Método</label><select name="payment_method" class="w-full input-dark rounded-lg px-3 py-3 text-sm bg-[#111827]"><option value="debit_card" {{ 'selected' if t and t.payment_method=='debit_card' else '' }}>Débito</option><option value="credit_card" {{ 'selected' if t and t.payment_method=='credit_card' else '' }}>Crédito</option><option value="pix" {{ 'selected' if t and t.payment_method=='pix' else '' }}>Pix</option><option value="money" {{ 'selected' if t and t.payment_method=='money' else '' }}>Dinheiro</option></select></div>
                <div class="space-y-1"><label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Conta</label><select name="account_id" class="w-full input-dark rounded-lg px-3 py-3 text-sm bg-[#111827]"><option value="">-- Selecionar --</option>{% for acc in accounts %}<option value="{{ acc.id }}" {{ 'selected' if t and t.account_id == acc.id else '' }}>{{ acc.name }}</option>{% endfor %}</select></div>
            </div>
            <div class="space-y-1"><label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Cartão (Se Crédito)</label><select name="card_id" class="w-full input-dark rounded-lg px-3 py-3 text-sm bg-[#111827]"><option value="">-- Nenhum --</option>{% for c in cards %}<option value="{{ c.id }}" {{ 'selected' if t and t.card_id == c.id else '' }}>{{ c.name }}</option>{% endfor %}</select></div>
            <div class="space-y-1"><label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Data</label><input type="datetime-local" name="date" value="{{ t.transaction_date if t else now }}" class="w-full input-dark rounded-lg px-4 py-3 text-sm"></div>
            <button class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-lg mt-4 shadow-lg transition text-sm">{{ 'Salvar' if t else 'Adicionar' }}</button>
        </form>
    </div>
</div>
"""