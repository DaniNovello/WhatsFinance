# WhatsFinance

Bot Telegram + dashboard web para finanças pessoais, usando **Supabase** (Postgres).

## Estrutura do repositório

```
WhatsFinance/
├── whatsfinance/           # Pacote principal da aplicação
│   ├── app.py              # Flask + Login + webhook Telegram
│   ├── config.py           # Carrega .env (raiz do repo)
│   ├── db.py               # Cliente Supabase + helpers
│   ├── commands.py         # Comandos do bot (/saldo, relatórios…)
│   ├── ai_parser.py        # Compat: pipeline de intenção
│   ├── conversation_state.py
│   ├── web_security.py
│   ├── templates_web.py
│   ├── bot/                # Telegram (handlers, flow, keyboards, client)
│   ├── routes/             # Blueprint web
│   └── services/           # Domínio: IA, transações, intent, multimodal…
├── supabase/migrations/    # SQL versionado
├── app.py / run.py         # Entrada na raiz (ajustam sys.path)
├── conversation_state.py   # Shims opcionais p/ imports antigos
├── ai_parser.py
├── db.py
├── pyproject.toml          # pip install -e .
└── requirements.txt
```

| Área | Onde |
|------|------|
| App Flask, sessão, CSRF | `whatsfinance/app.py` |
| Rotas web | `whatsfinance/routes/web_routes.py` |
| Webhook + fluxo do bot | `whatsfinance/bot/` |
| Parser + LLM plugável | `whatsfinance/services/llm_providers.py`, `ai_service.py`, `intent_pipeline.py` |
| Transações + RPC | `whatsfinance/services/transaction_service.py` |
| Estado conversa | `whatsfinance/services/conversation_service.py` |
| Dados | `whatsfinance/db.py` |

### Provedores LLM (incl. opções gratuitas)

- **`LLM_PROVIDER=gemini`** (padrão): [Google AI Studio](https://ai.google.dev) — camada gratuita; suporta **imagem** (comprovantes).
- **`LLM_PROVIDER=openai_compatible`**: API tipo OpenAI — ex. **[Groq](https://console.groq.com)** (tier gratuito), ótimo para **texto**; imagens são ignoradas com aviso no log (use Gemini para fotos).

Variáveis: ver `.env.example`.

## 1. Projeto no Supabase

1. Crie um projeto em [supabase.com](https://supabase.com).
2. Em **Project Settings → API**, copie:
   - **Project URL** → `SUPABASE_URL`
   - **service_role** `secret` → `SUPABASE_KEY` (use só no servidor; nunca no frontend).

## 2. Banco de dados

1. No Supabase, abra **SQL Editor** → **New query**.
2. Execute as migrações em `supabase/migrations/` em ordem cronológica.

## 3. Variáveis de ambiente

```bash
copy .env.example .env
```

Edite `.env` na **raiz** do repositório.

## 4. MCP no Cursor (opcional)

No `.cursor/mcp.json`, escopo read-only do Supabase, etc.

## 5. Rodar local

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# opcional: pip install -e .
python run.py
# ou: python app.py
```

Produção (exemplo):

```bash
gunicorn whatsfinance.app:app
```

## 6. Segurança mínima (web)

- **`SECRET_KEY`**: obrigatória se `FLASK_ENV=production` ou `ENV=production`.
- **`SESSION_COOKIE_SECURE=1`**: recomendado atrás de HTTPS.
- **CSRF**, **POST** para delete/logout, expiração de código Telegram — ver `whatsfinance/web_security.py`.
