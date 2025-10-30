from flask import Flask
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

# Fichier pour stocker les anciennes offres
SAVE_FILE = "offres_crous_nice.json"

# URL des offres CROUS
URL = "https://trouverunlogement.lescrous.fr/tools/41/search?bounds=7.1819535_43.7607635_7.323912_43.6454189"

# Config IFTTT
IFTTT_KEY = "TON_IFTTT_KEY"  # <-- Remplace par ta clé IFTTT
IFTTT_EVENT = "nouvelles_offres_crous"

# Fonction pour envoyer une notification via IFTTT
def notify_ifttt(nouvelles):
    titres = "\n".join([f"{o['titre']} ({o['lieu']})" for o in nouvelles])
    requests.post(
        f"https://maker.ifttt.com/trigger/{IFTTT_EVENT}/with/key/{IFTTT_KEY}",
        json={"value1": titres}
    )

# Fonction pour récupérer les offres CROUS
def get_offres():
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

# Charger les anciennes offres
def load_old_offres():
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Sauvegarder les nouvelles offres
def save_offres(offres):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(offres, f, ensure_ascii=False, indent=2)

# Vérifier les nouvelles offres et notifier si besoin
def check_new_offres():
    old = load_old_offres()
    new = get_offres()
    old_titles = {o["titre"] for o in old}
    nouv = [o for o in new if o["titre"] not in old_titles]
    if nouv:
        notify_ifttt(nouv)
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
    app.run()
