import os
from datetime import datetime
from src.charger_suivi import charger_suivi
from src.sauvegarde_suivi_discord import sauvegarder_suivi
from src.verifier_manga import verifier_manga
from src.config import FICHIER_LISTE
from src.envoyer_discord import envoyer_discord
from src.logger import log_error, log_info


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

    for url in mangas:
        nom_manga = url.strip("/").split("/")[-1].replace("-", " ").title()
        dernier_lu = suivi.get(url)

        nouveautes = verifier_manga(url, dernier_lu)

        if nouveautes:
            print(f"--> Nouveautés pour {nom_manga} ({len(nouveautes)})")

            envoyer_discord(nom_manga, nouveautes)

            suivi[url] = nouveautes[0]["nom"]
            sauvegarde_necessaire = True
            log_info(
                f"{len(nouveautes)} nouveau(x) chapitre(s) trouvé(s) pour {nom_manga} ({url})"
            )
        else:
            if url not in suivi:
                init = verifier_manga(url, "FORCE_INIT")
                if init:
                    suivi[url] = init[0]["nom"]
                    sauvegarde_necessaire = True
                    print(f"--> {nom_manga} ajouté à la base de données.")
                    log_info(f"{nom_manga} ({url}) ajouté à la base de données")
                else:
                    log_error(
                        f"Echec de l'initialisation du suivi pour {nom_manga} ({url})"
                    )

    if sauvegarde_necessaire:
        sauvegarder_suivi(suivi)
        print("Base de données mise à jour.")
    else:
        print("Rien de nouveau.")


if __name__ == "__main__":
    main()