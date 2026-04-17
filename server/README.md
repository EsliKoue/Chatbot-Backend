# Portfolio Chatbot 

Backend FastAPI avec intégration Groq pour répondre aux questions sur le portfolio.

## Configuration requise

- Python 3.9+
- Clé API Groq 
## Installation locale

```bash
# Environnement virtuel
cd server
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Dépendances
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Éditer .env et ajouter votre GROQ_API_KEY

# Lancer
python -m uvicorn server:app --port 8000
```

Accès: http://localhost:8000/docs

2. Installer les dépendances:
```bash
pip install -r requirements.txt
```

3. Configurer les variables d'environnement:
```bash
# Créer le fichier .env avec:
GROQ_API_KEY=votre_clé_api_groq
GROQ_MODEL=llama-3.3-70b-versatile
PORT=8001
```

Obtenez votre clé gratuite sur: https://console.groq.com/keys

4. Lancer le serveur:
```bash
python -m uvicorn server:app --port 8001
```


---

## API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | /session/nouvelle | Créer une nouvelle session |
| POST | /chat | Envoyer un message |
| DELETE | /session/{session_id} | Supprimer une session |
| GET | /session/{session_id}/historique | Consulter l'historique |

## Exemple d'utilisation

Créer une session:
```bash
curl -X POST http://localhost:8001/session/nouvelle
```

Envoyer un message:
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc-123",
    "message": "Quels sont tes projets?"
  }'
```

---

## Architecture des fichiers

- **server.py** - Routes FastAPI et gestion des sessions
- **agent.py** - Intégration Groq et logique conversationnelle  
- **portfolio_data.py** - Données du portfolio 
- **requirements.txt** - Dépendances Python

## Modèle LLM

- Fournisseur: Groq
- Modèle: llama-3.3-70b-versatile
- Latence: 2-5 secondes par réponse

## Production

Pour le déploiement en production:
1. Remplacer l'origine CORS par votre domaine
2. Utiliser Redis pour le stockage des sessions
3. Ajouter authentification si nécessaire
4. Configurer HTTPS
