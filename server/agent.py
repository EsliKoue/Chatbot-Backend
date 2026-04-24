import os
from dotenv import load_dotenv
from portfolio_data import construire_contexte_portfolio

# Chargement variables
load_dotenv()

# CONFIG
USE_OLLAMA = os.getenv("USE_OLLAMA", "false").lower() == "true"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

MAX_HISTORY = 10  # limite mémoire

# Import conditionnel
if not USE_OLLAMA:
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
else:
    import requests

# Contexte
CONTEXTE_PORTFOLIO = construire_contexte_portfolio()

SYSTEM_PROMPT = f"""
Tu es l'assistant du portfolio de Koue Obed Esli.

{CONTEXTE_PORTFOLIO}

Règles:
- Réponds uniquement avec les infos du contexte
- Pas d'invention
- Réponses claires, structurées
"""

# ======================
# SESSION
# ======================

def creer_session():
    return []


def nettoyer_historique(historique):
    """Limite la taille de l'historique"""
    return historique[-MAX_HISTORY:]


# ======================
# APPEL MODELE
# ======================

def appeler_groq(messages):
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.5,
        max_tokens=500,
    )
    return completion.choices[0].message.content


def appeler_ollama(messages):
    url = "http://localhost:11434/api/chat"

    response = requests.post(url, json={
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False
    })

    if response.status_code != 200:
        raise Exception("Erreur Ollama")

    return response.json()["message"]["content"]


# ======================
# MAIN FUNCTION
# ======================

def envoyer_message(historique, message_utilisateur):

    historique = nettoyer_historique(historique)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ] + historique + [
        {"role": "user", "content": message_utilisateur}
    ]

    try:
        if USE_OLLAMA:
            texte_reponse = appeler_ollama(messages)
        else:
            texte_reponse = appeler_groq(messages)

    except Exception as e:
        texte_reponse = "Une erreur technique est survenue. Réessaie plus tard."

    nouvel_historique = historique + [
        {"role": "user", "content": message_utilisateur},
        {"role": "assistant", "content": texte_reponse},
    ]

    return texte_reponse, nouvel_historique