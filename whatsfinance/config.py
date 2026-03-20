"""Carregamento de ambiente (centralizado)."""
from pathlib import Path

from dotenv import load_dotenv

# Raiz do repositório (pai de `whatsfinance/`)
REPO_ROOT = Path(__file__).resolve().parent.parent

# .env na raiz do projeto
load_dotenv(REPO_ROOT / ".env")
