from flask import Flask, jsonify
import openai
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# --- CONFIGURATION ---

# Clé API OpenAI (mets la tienne)
openai.api_key = "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
"

# Infos WordPress
WORDPRESS_URL = "https://jebricol.com/wp-json/wp/v2/posts"
USERNAME = "Bricoleur"
APP_PASSWORD = "Mgbk JrPy JD1H PIIR gFai 2cD1"

# ID de la catégorie dans laquelle tu veux publier (optionnel)
CATEGORIE_ID = 5

# --- FONCTION POUR GENERER L'ARTICLE AVEC OPENAI ---

def generer_article():
    prompt = (
        "Rédige un article SEO d'au moins 3000 mots sur le bricolage, "
        "avec un style clair et engageant."
    )
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=3000,
        temperature=0.7
    )
    texte = response.choices[0].text.strip()
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
    app.run(host="0.0.0.0", port=5000)
