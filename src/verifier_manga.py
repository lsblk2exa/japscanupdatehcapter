import os
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from src.config import FLARESOLVERR_URL, BASE_DIR
from src.config import ROUGE, RESET
from src.logger import log_error, log_warning, log_info


class Http500Error(Exception):
    """Levée quand la page Japscan renvoie une erreur 5xx (à relancer plus tard)."""
    pass


class ParseError(Exception):
    """Levée quand la structure HTML semble avoir changé (aucun chapitre parseable)."""
    pass


def _manga_slug(url):
    path = urlparse(url).path.strip("/")
    parts = [p for p in path.split("/") if p]
    return parts[-1] if parts else ""


def _sauver_debug(html, url):
    debug_dir = os.path.join(BASE_DIR, "logs", "html_debug")
    os.makedirs(debug_dir, exist_ok=True)
    safe_name = url.strip("/").replace("https://", "").replace("http://", "").replace("/", "_")
    debug_path = os.path.join(debug_dir, f"{safe_name}.html")
    try:
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(html)
    except Exception as e:
        log_error(f"Impossible d'écrire le HTML debug pour {url} : {e}")
        return None
    return debug_path


CHAPITRE_TEXTE_RE = re.compile(r"Chapitre\s+[\d\.]+", re.IGNORECASE)


def _est_cache(el):
    # Le site truffe la page de leurres hors-écran ou d-none.
    classes = el.get("class") or []
    if "d-none" in classes:
        return True
    style = (el.get("style") or "").replace(" ", "").lower()
    if "-9999px" in style or "display:none" in style or "opacity:0" in style:
        return True
    return False


def _extraire_chapitres(html, slug):
    """Trouve les chapitres par pattern d'URL + texte de chapitre visible.

    Japscan cache le vrai lien dans un attribut au nom changeant (xwtc, tuec,
    ...) et ajoute des leurres (faux href, éléments hors-écran avec un texte
    piégé). On retient uniquement les éléments qui portent à la fois :
      - un attribut dont la valeur matche `/manga/<slug>/<digits>/`
      - un texte visible matchant `Chapitre <nombre>`
      - pas de marqueur d'élément caché.
    """
    soup = BeautifulSoup(html, "html.parser")
    url_pattern = re.compile(rf'/(?:manga|manhwa|manhua)/{re.escape(slug)}/\d+/?')

    per_url = {}
    ordre = []

    for el in soup.find_all(True):
        if _est_cache(el):
            continue

        texte = el.get_text(" ", strip=True).replace("\u200b", "").strip()
        if texte.startswith("."):
            texte = texte[1:].strip()
        if not texte or len(texte) > 300:
            continue
        if not CHAPITRE_TEXTE_RE.search(texte):
            continue

        url_trouvee = None
        for v in el.attrs.values():
            valeurs = v if isinstance(v, list) else [v]
            for s in valeurs:
                if not isinstance(s, str):
                    continue
                m = url_pattern.search(s)
                if m:
                    url_trouvee = m.group(0)
                    if not url_trouvee.endswith("/"):
                        url_trouvee += "/"
                    break
            if url_trouvee:
                break
        if not url_trouvee:
            continue

        if url_trouvee not in per_url:
            per_url[url_trouvee] = (el, texte)
            ordre.append(url_trouvee)
        else:
            _, ancien_texte = per_url[url_trouvee]
            if len(texte) < len(ancien_texte):
                per_url[url_trouvee] = (el, texte)

    chapitres = []
    for url_rel in ordre:
        _, nom = per_url[url_rel]
        chapitres.append({
            "nom": nom,
            "lien": f"https://www.japscan.foo{url_rel}",
        })

    return chapitres


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

        if 500 <= response.status_code < 600:
            log_error(
                f"Requête FlareSolverr échouée pour {real_url} (status={response.status_code})"
            )
            print(f"{ROUGE}Erreur HTTP {response.status_code} pour {real_url}{RESET}")
            raise Http500Error(real_url)

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
        slug = _manga_slug(real_url)
        if not slug:
            log_error(f"Slug introuvable dans l'URL {real_url}")
            return None

        tous_chapitres = _extraire_chapitres(html, slug)

        if not tous_chapitres:
            debug_path = _sauver_debug(html, url)
            log_error(
                f"Aucun chapitre extrait pour {real_url} (slug={slug} ; HTML sauvegardé dans {debug_path})"
            )
            raise ParseError(real_url)

        chapitres_a_lire = []
        for chap in tous_chapitres:
            if dernier_lu_connu and chap["nom"] == dernier_lu_connu:
                break
            chapitres_a_lire.append(chap)

        if not chapitres_a_lire:
            log_info(f"Aucun nouveau chapitre trouvé pour {real_url}")

        return chapitres_a_lire

    except (Http500Error, ParseError):
        raise
    except Exception as e:
        log_error(f"Exception lors de la vérification de {real_url} : {e}")
        print(f"{ROUGE}Erreur technique sur {real_url}: {e}{RESET}")
        return None