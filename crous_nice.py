from flask import Flask
import requests
from bs4 import BeautifulSoup
import json
import os

app = Flask(__name__)

# Fichier pour stocker les anciennes offres
SAVE_FILE = "offres_crous_nice.json"

# URL des offres CROUS
URL = "https://trouverunlogement.lescrous.fr/tools/41/search?bounds=7.1819535_43.7607635_7.323912_43.6454189"

# Config IFTTT
IFTTT_KEY = "TON_IFTTT_KEY"  # <-- Remplace par ta clé IFTTT
IFTTT_EVENT = "nouvelles_offres_crous"  # Nom de ton Applet IFTTT

# Fonction pour envoyer une notification via IFTTT
def notify_ifttt(message):
    try:
        requests.post(
            f"https://maker.ifttt.com/trigger/{IFTTT_EVENT}/with/key/{IFTTT_KEY}",
            json={"value1": message}
        )
    except Exception as e:
        print("Erreur notification IFTTT:", e)

# Fonction pour récupérer les offres CROUS
def get_offres():
    try:
        response = requests.get(URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        offres = []
        for bloc in soup.select("h3"):
            titre = bloc.text.strip()
            suivant = bloc.find_next_sibling("p")
            lieu = suivant.text.strip() if suivant else "Lieu non précisé"
            offres.append({"titre": titre, "lieu": lieu})
        return offres
    except Exception as e:
        print("Erreur récupération offres:", e)
        return []

# Charger les anciennes offres
def load_old_offres():
    if not os.path.exists(SAVE_FILE):
        return []
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

# Sauvegarder les nouvelles offres
def save_offres(offres):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(offres, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Erreur sauvegarde offres:", e)

# Vérifier les nouvelles offres et notifier si besoin
def check_new_offres():
    old = load_old_offres()
    new = get_offres()

    if not new:
        notify_ifttt("Aucune offre trouvée pour le moment 😢")
        return

    old_titles = {o["titre"] for o in old}
    nouv = [o for o in new if o["titre"] not in old_titles]

    if nouv:
        message = "\n".join([f"{o['titre']} ({o['lieu']})" for o in nouv])
        notify_ifttt(message)
        save_offres(new)

# Route principale déclenchée par Cronjobly
@app.route('/')
def run_script():
    try:
        check_new_offres()
        return "Script exécuté avec succès"
    except Exception as e:
        return f"Erreur: {e}"

# Pour exécuter localement (optionnel)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
