"""Executar o app Flask (mesmo comportamento que `python app.py`)."""
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from whatsfinance.app import app

if __name__ == "__main__":
    app.run(port=5000, debug=True)
