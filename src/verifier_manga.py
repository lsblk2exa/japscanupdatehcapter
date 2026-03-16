import requests
from bs4 import BeautifulSoup
import os
from src.config import FLARESOLVERR_URL, BASE_DIR
from src.config import ROUGE, RESET
from src.logger import log_error, log_warning, log_info


def verifier_manga(url, dernier_lu_connu):
    # Japscan a déménagé de .vip vers .foo
    real_url = url.replace("www.japscan.vip", "www.japscan.foo")

    headers = {"Content-Type": "application/json"}
    payload = {
        "cmd": "request.get",
        "url": real_url,
        "maxTimeout": 60000,
    }

    try:
        response = requests.post(FLARESOLVERR_URL, json=payload, headers=headers)

        if response.status_code != 200:
            log_error(
                f"Requête FlareSolverr échouée pour {real_url} (status={response.status_code})"
            )
            print(f"{ROUGE}Erreur HTTP {response.status_code} pour {real_url}{RESET}")
            return None

        data = response.json()
        if data.get("status") != "ok":
            log_error(f"Réponse FlareSolverr invalide pour {real_url} (status={data.get('status')})")
            print(f"{ROUGE}Réponse invalide pour {real_url}{RESET}")
            return None

        html = data["solution"]["response"]
        soup = BeautifulSoup(html, "html.parser")

        all_divs = soup.find_all("div", class_="list_chapters")

        if not all_divs:
            # Sauvegarde de la page pour analyse si la structure a changé
            debug_dir = os.path.join(BASE_DIR, "logs", "html_debug")
            os.makedirs(debug_dir, exist_ok=True)
            safe_name = url.strip("/").replace("https://", "").replace("http://", "").replace("/", "_")
            debug_path = os.path.join(debug_dir, f"{safe_name}.html")
            try:
                with open(debug_path, "w", encoding="utf-8") as f:
                    f.write(html)
            except Exception as e:
                log_error(f"Impossible d'écrire le HTML debug pour {url} : {e}")

            log_warning(f"Aucun bloc de chapitres trouvé pour {real_url} (HTML sauvegardé dans {debug_path})")
            return None

        chapitres_a_lire = []

        for div in all_divs:
            liens = div.find_all("a", class_="text-dark")

            lien_valide = None

            for link in liens:
                classes = link.get("class", [])
                if "d-none" in classes:
                    continue
                texte_chapitre = link.text.strip()
                if "MikeZeDev" in texte_chapitre:
                    continue
                lien_valide = link
                break

            if not lien_valide:
                continue
            nom_chapitre = lien_valide.text.strip()
            if nom_chapitre.startswith("."):
                nom_chapitre = nom_chapitre[1:].strip()

            lien_relatif = lien_valide.get("href") or lien_valide.get("toto")
            lien_complet = (
                f"https://www.japscan.foo{lien_relatif}" if lien_relatif else ""
            )
            if not lien_complet:
                log_warning(f"Lien de chapitre manquant pour {url} ({nom_chapitre})")

            if dernier_lu_connu and nom_chapitre == dernier_lu_connu:
                break

            chapitres_a_lire.append({"nom": nom_chapitre, "lien": lien_complet})

        if not chapitres_a_lire:
            log_info(f"Aucun nouveau chapitre trouvé pour {real_url}")

        return chapitres_a_lire

    except Exception as e:
        log_error(f"Exception lors de la vérification de {real_url} : {e}")
        print(f"{ROUGE}Erreur technique sur {real_url}: {e}{RESET}")
        return None