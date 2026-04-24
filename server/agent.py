import os
from dotenv import load_dotenv
from groq import Groq
from portfolio_data import construire_contexte_portfolio

# Charger les variables d'environnement depuis .env
load_dotenv()


# Configuration de l'agent conversationnel avec Groq


GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

# Client Groq
client = Groq(api_key=GROQ_API_KEY)

# Contexte du portfolio 
CONTEXTE_PORTFOLIO = construire_contexte_portfolio()

# Prompt système
SYSTEM_PROMPT = f"""Tu es l'assistant personnel du portfolio de Pascal Kambou.

Ton rôle est d'aider les visiteurs à mieux connaître Pascal : ses projets, compétences, formations et expériences.

Voici toutes les données du portfolio :

{CONTEXTE_PORTFOLIO}


CONSIGNES STRICTES - TRÈS IMPORTANT


1. LANGUE:
   - Si question en français → UNIQUEMENT français
   - Si question en anglais → UNIQUEMENT anglais
   - JAMAIS mélanger les langues

2. TONALITÉ: Clair, concis, professionnel, amical

3. **POUR LES DEMANDES DE CONTACT - RÈGLE ABSOLUE** :
   -  INTERDIT: créer des liens markdown [email](mailto:email)
   -  INTERDIT: utiliser les listes à puces avec des liens
   -  OBLIGATOIRE: Afficher les contacts en format simple:
   
   Email: pascalkambou200@gmail.com
   LinkedIn: Pascal Kambou
   
   -  OBLIGATOIRE: Pas de tirets longs, max 6 caractères

4. Pour les projets: détails précis (techno, fonctionnalités)

5. Si info absente du contexte: dire "Je ne dispose pas de cette info"

6. JAMAIS inventer d'infos

7. Structures tes réponses:
   - Titres: ## Titre (markdown OK sauf pour contacts)
   - Listes: • Point (bullet OK)
   - Gras: **texte** (gras OK)
   - Mais JAMAIS de [liens](url) - texte + url simplement

8. Réponds UNIQUEMENT à la question posée
"""


# API PUBLIQUE

def creer_session() -> list:
    """Crée une nouvelle session de conversation (historique vide)."""
    return []


def envoyer_message(historique: list, message_utilisateur: str) -> tuple[str, list]:
    """
    Envoie un message à Groq et retourne (réponse, historique_mis_à_jour).
    
    Args:
        historique: liste de dicts {"role": "user"|"assistant", "content": str}
        message_utilisateur: message de l'utilisateur
    
    Returns:
        (texte_reponse, nouvel_historique)
    """
    
    historique_clean = [
        {"role": m.get("role", "user"), "content": m.get("content", "")}
        for m in historique
    ]
    
    # Préparer les messages pour l'API Groq 
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ] + historique_clean + [
        {"role": "user", "content": message_utilisateur}
    ]
    
    try:
        # Appel à Groq API
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.5,
            max_tokens=580,
            top_p=0.95,
        )
        
        texte_reponse = completion.choices[0].message.content
        
    except Exception as e:
        return f" Erreur d'appel API Groq: {str(e)}", historique_clean
    
    # Mise à jour de l'historique
    nouvel_historique = historique_clean + [
        {"role": "user", "content": message_utilisateur},
        {"role": "assistant", "content": texte_reponse},
    ]
    
    return texte_reponse, nouvel_historique
