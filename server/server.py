import uuid
import os
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import creer_session, envoyer_message

# =====================
# CONFIG
# =====================

app = FastAPI(
    title="AI Portfolio Chatbot",
    description="Backend IA pour chatbot intelligent",
    version="2.0.0",
)

# ⚠️ CORS sécurisé
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================
# STOCKAGE (temporaire)
# =====================

sessions = {}
last_access = {}

SESSION_TIMEOUT = 3600  # 1h

# =====================
# SCHEMAS
# =====================

class NouvelleSessionReponse(BaseModel):
    session_id: str
    message: str


class MessageRequete(BaseModel):
    session_id: str
    message: str


class MessageReponse(BaseModel):
    reponse: str
    session_id: str


# =====================
# UTILITAIRE
# =====================

def nettoyer_sessions():
    """Supprime les sessions expirées"""
    now = time.time()
    expired = [
        sid for sid, t in last_access.items()
        if now - t > SESSION_TIMEOUT
    ]
    for sid in expired:
        sessions.pop(sid, None)
        last_access.pop(sid, None)


# =====================
# ROUTES
# =====================

@app.get("/")
def accueil():
    return {"status": "ok", "message": "API Chatbot active"}


@app.post("/session/nouvelle", response_model=NouvelleSessionReponse)
def nouvelle_session():
    nettoyer_sessions()

    session_id = str(uuid.uuid4())
    sessions[session_id] = creer_session()
    last_access[session_id] = time.time()

    return {
        "session_id": session_id,
        "message": "Session créée",
    }


@app.post("/chat", response_model=MessageReponse)
def chat(req: MessageRequete, request: Request):

    nettoyer_sessions()

    if req.session_id not in sessions:
        raise HTTPException(404, "Session introuvable")

    message = req.message.strip()
    if not message:
        raise HTTPException(400, "Message vide")

    # Anti-spam simple
    if len(message) > 1000:
        raise HTTPException(400, "Message trop long")

    historique = sessions[req.session_id]

    try:
        reponse, new_hist = envoyer_message(historique, message)
    except Exception as e:
        raise HTTPException(500, "Erreur IA")

    sessions[req.session_id] = new_hist
    last_access[req.session_id] = time.time()

    return {
        "reponse": reponse,
        "session_id": req.session_id,
    }


@app.delete("/session/{session_id}")
def supprimer_session(session_id: str):
    sessions.pop(session_id, None)
    last_access.pop(session_id, None)
    return {"message": "Session supprimée"}


@app.get("/session/{session_id}/historique")
def historique(session_id: str):
    if session_id not in sessions:
        raise HTTPException(404, "Session introuvable")

    return {
        "nb_messages": len(sessions[session_id]),
        "historique": sessions[session_id],
    }


# =====================
# RUN
# =====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)