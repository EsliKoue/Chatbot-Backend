import uuid
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import creer_session, envoyer_message


# CONFIGURATION Configuration du serveur FastAPI

app = FastAPI(
    title="Portfolio Chatbot API",
    description="Backend IA pour le chatbot du portfolio",
    version="1.0.0",
)

# CORS — autorise le frontend à communiquer
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",      # Vite
        "http://localhost:8082",
        "http://localhost:8083",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5500",
        "*",  # À remplacer par le domaine réel en production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stockage en mémoire des sessions
sessions: dict[str, list] = {}



# Schemas pydantic pour les requêtes et réponses de l'API


class NouvelleSessionReponse(BaseModel):
    session_id: str
    message: str


class MessageRequete(BaseModel):
    session_id: str
    message: str


class MessageReponse(BaseModel):
    reponse: str
    session_id: str


# Routes de l'API


@app.get("/")
def accueil():
    """Route de test pour vérifier que le serveur est actif."""
    return {
        "statut": "ok",
        "message": "Portfolio Chatbot Backend actif et prêt à recevoir des messages !",
        "api": "FastAPI",
    }


@app.post("/session/nouvelle", response_model=NouvelleSessionReponse)
def nouvelle_session():
    """
    Crée une nouvelle session de conversation.
    À appeler quand un visiteur ouvre le chatbot pour la première fois.
    """
    session_id = str(uuid.uuid4())
    sessions[session_id] = creer_session()
    return {
        "session_id": session_id,
        "message": "Session créée avec succès",
    }


@app.post("/chat", response_model=MessageReponse)
def chat(requete: MessageRequete):
    """
    Envoie un message au chatbot et reçoit une réponse.
    
    Body JSON attendu :
    {
        "session_id": "uuid-...",
        "message": "Ta question ici"
    }
    """
    
    # Vérifier la session
    if requete.session_id not in sessions:
        raise HTTPException(
            status_code=404,
            detail="Session introuvable. Créez d'abord une session via /session/nouvelle"
        )
    
    # Vérifier le message
    message = requete.message.strip()
    if not message:
        raise HTTPException(
            status_code=400,
            detail="Le message ne peut pas être vide"
        )
    
    # Obtenir l'historique
    historique = sessions[requete.session_id]
    
    # Appeler l'agent
    reponse_texte, historique_mis_a_jour = envoyer_message(historique, message)
    
    # Sauvegarder
    sessions[requete.session_id] = historique_mis_a_jour
    
    return {
        "reponse": reponse_texte,
        "session_id": requete.session_id,
    }


@app.delete("/session/{session_id}")
def supprimer_session(session_id: str):
    """
    Supprime une session (libère la mémoire).
    À appeler quand le visiteur ferme le chatbot.
    """
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "Session supprimée avec succès"}
    raise HTTPException(status_code=404, detail="Session introuvable")


@app.get("/session/{session_id}/historique")
def obtenir_historique(session_id: str):
    """Retourne l'historique complet d'une session (debug)."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session introuvable")
    return {
        "session_id": session_id,
        "nb_messages": len(sessions[session_id]),
        "historique": sessions[session_id],
    }


# Démarre le serveur

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )
