import requests
from datetime import datetime
from src.config import DISCORD_WEBHOOK_URL
from src.logger import log_error, log_info


def envoyer_discord(manga_nom, chapitres):
    if not chapitres:
        return

    if len(chapitres) == 1:
        desc = f"Le **{chapitres[0]['nom']}** est disponible !"
        lien = chapitres[0]["lien"]
    else:
        desc = f" **{len(chapitres)} chapitres sortis !**\n"
        for chap in reversed(chapitres):
            desc += f"- {chap['nom']}\n"
        lien = chapitres[0]["lien"]

    footer_text = "Japscan Bot • " + datetime.now().strftime("%H:%M")

    embed = {
        "title": f"Nouveau sur {manga_nom} !",
        "description": desc,
        "url": lien,
        "color": 5814783,
        "footer": {"text": footer_text},
        "thumbnail": {"url": "https://www.japscan.vip/imgs/japscan_logo_new.png"},
    }

    data = {
        "username": "Japscan Bot",
        "content": "@everyone",
        "embeds": [embed],
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        if response.status_code >= 400:
            log_error(
                f"Echec de l'envoi Discord pour {manga_nom} (status={response.status_code})"
            )
        else:
            log_info(f"Notification Discord envoyée pour {manga_nom}")
    except Exception as e:
        log_error(f"Exception lors de l'envoi Discord pour {manga_nom} : {e}")
        print(f"Erreur envoi Discord : {e}")


def envoyer_alerte_discord(titre, message):
    embed = {
        "title": f"⚠️ {titre}",
        "description": message,
        "color": 15548997,
        "footer": {"text": "Japscan Bot • " + datetime.now().strftime("%d/%m %H:%M")},
    }
    data = {
        "username": "Japscan Bot",
        "content": "@here",
        "embeds": [embed],
    }
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        if response.status_code >= 400:
            log_error(f"Echec de l'envoi de l'alerte Discord (status={response.status_code})")
        else:
            log_info(f"Alerte Discord envoyée : {titre}")
    except Exception as e:
        log_error(f"Exception lors de l'envoi de l'alerte Discord : {e}")
        print(f"Erreur envoi alerte Discord : {e}")