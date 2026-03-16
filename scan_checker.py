import os
from src.config import FICHIER_LISTE
from src.config import VERT, JAUNE, ROUGE, BLEU, RESET
from src.charger_suivi import charger_suivi
from src.save_suivi import sauvegarder_suivi
from src.verifier_manga import verifier_manga
from src.logger import log_error, log_info


def main():
    print(f"{BLEU}--- Vérification des mises à jour ---{RESET}")

    if not os.path.exists(FICHIER_LISTE):
        message = f"Fichier liste introuvable : {FICHIER_LISTE}"
        log_error(message)
        print(f"{ROUGE}{message}{RESET}")
        return

    with open(FICHIER_LISTE, "r") as f:
        mangas = [line.strip() for line in f if line.strip()]

    suivi = charger_suivi()
    total_new = 0

    for url in mangas:
        nom_manga = url.strip("/").split("/")[-1]
        print(f"Analyse : {nom_manga}...", end="\r")

        dernier_lu = suivi.get(url)
        nouveautes = verifier_manga(url, dernier_lu)
        print(" " * 50, end="\r")

        if nouveautes and len(nouveautes) > 0:
            print(
                f"{VERT}{nom_manga}{RESET} : {len(nouveautes)} chapitre(s) de retard !"
            )
            for chap in reversed(nouveautes):
                print(f"    {chap['nom']}")
            suivi[url] = nouveautes[0]["nom"]
            total_new += 1
            log_info(
                f"{len(nouveautes)} nouveau(x) chapitre(s) trouvé(s) pour {nom_manga} ({url})"
            )
            print("-" * 30)

        elif nouveautes is not None:
            if dernier_lu:
                print(f" {JAUNE}{nom_manga}{RESET} est à jour ({dernier_lu}).")
            else:
                print(
                    f" {BLEU}{nom_manga}{RESET} ajouté au suivi (Dernier : {nouveautes[0]['nom']})"
                )
                suivi[url] = nouveautes[0]["nom"]
                total_new += 1
                log_info(f"{nom_manga} ({url}) ajouté au suivi")
        else:
            log_error(f"Impossible d'analyser {nom_manga} ({url})")
            print(f"{ROUGE}{nom_manga}{RESET} : Impossible d'analyser.")

    if total_new > 0:
        sauvegarder_suivi(suivi)
        print(f"\nSauvegarde mise à jour.")
    else:
        print("\nRien à lire pour le moment.")


if __name__ == "__main__":
    main()