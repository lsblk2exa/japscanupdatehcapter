import os
import time
from datetime import datetime
from src.charger_suivi import charger_suivi
from src.sauvegarde_suivi_discord import sauvegarder_suivi
from src.verifier_manga import verifier_manga, Http500Error
from src.config import FICHIER_LISTE
from src.envoyer_discord import envoyer_discord
from src.logger import log_error, log_info


def _traiter_manga(url, nom_manga, suivi, sauvegarde_necessaire):
    """Traite un manga (vérif + notif + suivi). Retourne (sauvegarde_necessaire, True si 500)."""
    dernier_lu = suivi.get(url)
    try:
        nouveautes = verifier_manga(url, dernier_lu)
    except Http500Error:
        return sauvegarde_necessaire, True

    if nouveautes:
        print(f"--> Nouveautés pour {nom_manga} ({len(nouveautes)})")
        envoyer_discord(nom_manga, nouveautes)
        suivi[url] = nouveautes[0]["nom"]
        log_info(
            f"{len(nouveautes)} nouveau(x) chapitre(s) trouvé(s) pour {nom_manga} ({url})"
        )
        return True, False
    if url not in suivi:
        try:
            init = verifier_manga(url, "FORCE_INIT")
        except Http500Error:
            return sauvegarde_necessaire, True
        if init:
            suivi[url] = init[0]["nom"]
            print(f"--> {nom_manga} ajouté à la base de données.")
            log_info(f"{nom_manga} ({url}) ajouté à la base de données")
            return True, False
        log_error(f"Echec de l'initialisation du suivi pour {nom_manga} ({url})")
    return sauvegarde_necessaire, False


def main():
    print(f"[{datetime.now().strftime('%d/%m %H:%M')}] Lancement du scan...")

    if not os.path.exists(FICHIER_LISTE):
        message = f"Fichier de liste introuvable : {FICHIER_LISTE}"
        log_error(message)
        print(message)
        return

    with open(FICHIER_LISTE, "r") as f:
        mangas = [line.strip() for line in f if line.strip()]

    suivi = charger_suivi()
    sauvegarde_necessaire = False
    urls_500 = []

    for url in mangas:
        nom_manga = url.strip("/").split("/")[-1].replace("-", " ").title()
        sn, is_500 = _traiter_manga(url, nom_manga, suivi, sauvegarde_necessaire)
        sauvegarde_necessaire = sn
        if is_500:
            urls_500.append((url, nom_manga))

    if urls_500:
        print(f"\nRelance des {len(urls_500)} page(s) en erreur 500 dans 10 s...")
        time.sleep(10)
        for url, nom_manga in urls_500:
            sn, _ = _traiter_manga(url, nom_manga, suivi, sauvegarde_necessaire)
            sauvegarde_necessaire = sauvegarde_necessaire or sn

    if sauvegarde_necessaire:
        sauvegarder_suivi(suivi)
        print("Base de données mise à jour.")
    else:
        print("Rien de nouveau.")


if __name__ == "__main__":
    main()