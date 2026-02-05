from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import time

# ------------------ APP SETUP ------------------

app = FastAPI(title="Agentic Honeypot API")

@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI on Vercel"}

# ------------------ CORS ------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ LAZY DB INIT ------------------

def init_mongo():
    from pymongo import MongoClient
    from config import MONGO_URI, DB_NAME, SESSIONS_COLLECTION
    from session_manager import init_db

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    sessions_collection = db[SESSIONS_COLLECTION]
    init_db(sessions_collection)

# ------------------ HEALTH API ------------------

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "honeypot-api"}

# ------------------ MAIN HONEYPOT API ------------------

@app.post("/honeypot")
def honeypot_endpoint(payload: dict, x_api_key: str = Header(None)):

    # 🔹 Lazy imports (CRITICAL for Vercel)
    from config import API_KEY
    from scam_detector import detect_scam
    from agent import generate_reply
    from intelligence import extract_intelligence
    from session_manager import (
        get_session,
        update_session,
        should_finalize,
        update_intelligence,
        mark_scam_detected,
        mark_finalized,
    )
    from callback import send_final_callback

    # 🔹 Init DB only when first request hits
    init_mongo()

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    session_id = payload["sessionId"]
    message_obj = payload["message"]
    text = message_obj["text"]

    # 1. Get session and history
    session = get_session(session_id)
    history = session["messages"]

    update_session(session_id, message_obj)

    # 2. Scam detection
    is_scam = detect_scam(text, history)

    if is_scam:
        mark_scam_detected(session_id)

    # 3. Agent reply
    reply_text = generate_reply(text, history, is_scam)

    agent_message = {
        "sender": "user",
        "text": reply_text,
        "timestamp": int(time.time() * 1000),
    }

    update_session(session_id, agent_message)

    # 4. Intelligence extraction
    extract_intelligence(text, session["intelligence"])
    update_intelligence(session_id, session["intelligence"])

    # 5. Finalization
    if should_finalize(session, text) or should_finalize(session, reply_text):
        send_final_callback(session_id, session)
        mark_finalized(session_id)

    if session["finalized"]:
        return {"status": "finalized"}

    return {
        "status": "success",
        "reply": reply_text,
    }

# ------------------ VERCEL HANDLER ------------------

handler = Mangum(app)
