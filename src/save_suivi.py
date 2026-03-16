import json
from src.config import FICHIER_SAUVEGARDE
from src.logger import log_error, log_info


def sauvegarder_suivi(donnees):
    try:
        with open(FICHIER_SAUVEGARDE, "w", encoding="utf-8") as f:
            json.dump(donnees, f, indent=4, ensure_ascii=False)
        log_info(f"Suivi sauvegardé avec succès dans {FICHIER_SAUVEGARDE}")
    except Exception as e:
        log_error(f"Erreur lors de la sauvegarde du suivi dans {FICHIER_SAUVEGARDE} : {e}")