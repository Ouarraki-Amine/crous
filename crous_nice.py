import requests
from bs4 import BeautifulSoup
import json

URL = "https://trouverunlogement.lescrous.fr/tools/41/search?bounds=7.1819535_43.7607635_7.323912_43.6454189"
SAVE_FILE = "offres_crous_nice.json"

def get_offres():
    response = requests.get(URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    offres = []
    # Chaque logement semble listé avec un bloc — exemple : <### Résidence La Bastide Rouge>
    for bloc in soup.select("h3"):
        titre = bloc.text.strip()
        # on essaye de trouver la ligne de l’adresse juste après
        suivant = bloc.find_next_sibling("p")
        lieu = suivant.text.strip() if suivant else "Lieu non précisé"
        offres.append({"titre": titre, "lieu": lieu})
    return offres

def load_old_offres():
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_offres(offres):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(offres, f, ensure_ascii=False, indent=2)

def check_new_offres():
    old = load_old_offres()
    new = get_offres()
    old_titles = {o["titre"] for o in old}
    nouv = [o for o in new if o["titre"] not in old_titles]
    if nouv:
        print("🆕 Nouvelles offres :")
        for o in nouv:
            print(f"- {o['titre']} ({o['lieu']})")
        save_offres(new)
    else:
        print("Aucune nouvelle offre pour le moment.")

if __name__ == "__main__":
    try:
        check_new_offres()
    except Exception as e:
        print("Erreur :", e)
