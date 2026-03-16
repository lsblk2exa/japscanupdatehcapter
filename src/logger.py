import os
from datetime import datetime
from src.config import BASE_DIR


LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "japscan.log")


def _ecrire_log(niveau: str, message: str) -> None:
    os.makedirs(LOG_DIR, exist_ok=True)
    horodatage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ligne = f"[{horodatage}] {niveau.upper()} - {message}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(ligne)
    except Exception:
        # On évite de faire planter le script si le log échoue
        pass


def log_info(message: str) -> None:
    _ecrire_log("INFO", message)


def log_warning(message: str) -> None:
    _ecrire_log("WARNING", message)


def log_error(message: str) -> None:
    _ecrire_log("ERROR", message)

