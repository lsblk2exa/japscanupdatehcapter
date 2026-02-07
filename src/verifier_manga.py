import requests
from bs4 import BeautifulSoup
from src.config import FLARESOLVERR_URL
from src.config import ROUGE, RESET

def verifier_manga(url, dernier_lu_connu):
    headers = {"Content-Type": "application/json"}
    payload = {
        "cmd": "request.get",
        "url": url,
        "maxTimeout": 60000,
    }

    try:
        response = requests.post(FLARESOLVERR_URL, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                soup = BeautifulSoup(data['solution']['response'], 'html.parser')
                
                all_divs = soup.find_all('div', class_='list_chapters')
                
                if not all_divs: return None

                chapitres_a_lire = []
                
                for div in all_divs:
                    liens = div.find_all('a', class_='text-dark')
                    
                    lien_valide = None
                    
                    for link in liens:
                        classes = link.get('class', [])
                        if 'd-none' in classes:
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

                    lien_relatif = lien_valide.get('href') or lien_valide.get('toto')
                    lien_complet = f"https://www.japscan.vip{lien_relatif}" if lien_relatif else ""
                    if dernier_lu_connu and nom_chapitre == dernier_lu_connu:
                        break
                    
                    chapitres_a_lire.append({"nom": nom_chapitre, "lien": lien_complet})
                
                return chapitres_a_lire
        return None
    except Exception as e:
        print(f"Erreur technique sur {url}: {e}")
        return None
    headers = {"Content-Type": "application/json"}
    payload = {
        "cmd": "request.get",
        "url": url,
        "maxTimeout": 60000,
    }

    try:
        response = requests.post(FLARESOLVERR_URL, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                soup = BeautifulSoup(data['solution']['response'], 'html.parser')
                all_divs = soup.find_all('div', class_='list_chapters')   
                chapitres_a_lire = []
                
                for div in all_divs:
                    link_tag = div.find('a', class_='text-dark')
                    if not link_tag:
                        continue
                        
                    nom_chapitre = link_tag.text.strip()
                    lien_relatif = link_tag.get('href') or link_tag.get('toto')
                    lien_complet = f"https://www.japscan.vip{lien_relatif}" if lien_relatif else "Lien introuvable"
                    
                    if dernier_lu_connu and nom_chapitre == dernier_lu_connu:
                        break
                    
                    chapitres_a_lire.append({
                        "nom": nom_chapitre,
                        "lien": lien_complet
                    })
                
                return chapitres_a_lire
                
        return None
    except Exception as e:
        print(f"{ROUGE}Erreur technique : {e}{RESET}")
        return None