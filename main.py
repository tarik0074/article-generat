from flask import Flask, jsonify
import openai
import requests
from requests.auth import HTTPBasicAuth
import os

app = Flask(__name__)

# --- CONFIGURATION ---

# Récupération de la clé API OpenAI depuis la variable d'environnement
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("La variable d'environnement OPENAI_API_KEY n'est pas définie.")

# Infos WordPress
WORDPRESS_URL = "https://jebricol.com/wp-json/wp/v2/posts"  # L'API REST WordPress (changer si besoin)
USERNAME = "Bricoleur"
APP_PASSWORD = "Mgbk JrPy JD1H PIIR gFai 2cD1"

# ID de la catégorie (optionnel)
CATEGORIE_ID = 5

# --- FONCTION POUR GENERER L'ARTICLE AVEC OPENAI ---

def generer_article():
    messages = [
        {"role": "system", "content": "Tu es un assistant qui écrit des articles de bricolage."},
        {"role": "user", "content": "Rédige un article SEO d'au moins 3000 mots sur le bricolage, avec un style clair et engageant."}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=3000,
        temperature=0.7,
    )
    texte = response.choices[0].message.content.strip()
    return texte

# --- FONCTION POUR PUBLIER L'ARTICLE SUR WORDPRESS ---

def publier_article(titre, contenu, categorie_id=None):
    data = {
        "title": titre,
        "content": contenu,
        "status": "publish",
    }
    if categorie_id:
        data["categories"] = [categorie_id]

    auth = HTTPBasicAuth(USERNAME, APP_PASSWORD)
    response = requests.post(WORDPRESS_URL, json=data, auth=auth)

    if response.status_code == 201:
        return {"success": True, "link": response.json().get("link")}
    else:
        return {"success": False, "error": response.text, "status_code": response.status_code}

# --- ROUTE FLASK POUR LANCER LA GENERATION ET PUBLICATION ---

@app.route('/generer-et-publier')
def generer_et_publier():
    try:
        article = generer_article()
        titre = "Article automatique sur le bricolage"
        resultat = publier_article(titre, article, CATEGORIE_ID)

        if resultat["success"]:
            return jsonify({"message": "Article publié avec succès", "lien": resultat["link"]})
        else:
            return jsonify({"message": "Erreur publication", "details": resultat}), 500

    except Exception as e:
        return jsonify({"message": "Erreur serveur", "details": str(e)}), 500

# --- Lancer le serveur Flask ---

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
