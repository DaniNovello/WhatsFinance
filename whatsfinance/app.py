import logging
import os
import secrets

from flask import Flask
from flask_login import LoginManager

import whatsfinance.config  # noqa: F401 — carrega .env na importação

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

from whatsfinance import db
from whatsfinance.bot.handlers import register_telegram_webhook
from whatsfinance.routes.web_routes import User, web_bp

app = Flask(__name__)

_is_prod = os.environ.get("FLASK_ENV", "").lower() == "production" or os.environ.get("ENV", "").lower() == "production"
_secret = (os.environ.get("SECRET_KEY") or "").strip()
if not _secret:
    if _is_prod:
        raise RuntimeError("Defina SECRET_KEY no ambiente em produção.")
    _secret = secrets.token_hex(32)
    logging.getLogger(__name__).warning(
        "SECRET_KEY não definida: usando valor aleatório só para esta execução. Configure SECRET_KEY no .env."
    )
app.secret_key = _secret

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
if os.environ.get("SESSION_COOKIE_SECURE", "").strip() in ("1", "true", "yes"):
    app.config["SESSION_COOKIE_SECURE"] = True


@app.context_processor
def _inject_csrf():
    from whatsfinance import web_security

    return dict(csrf_token=web_security.get_csrf_token)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "web.login"
login_manager.session_protection = "strong"


@login_manager.user_loader
def load_user(user_id):
    u = db.get_user(user_id)
    if u:
        return User(u["id"], u["name"])
    return None


app.register_blueprint(web_bp)
register_telegram_webhook(app)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
