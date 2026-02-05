from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import time
from config import API_KEY
from config import MONGO_URI, DB_NAME, SESSIONS_COLLECTION
from scam_detector import detect_scam
from agent import generate_reply
from intelligence import extract_intelligence
from session_manager import get_session, update_session, should_finalize,update_intelligence,mark_scam_detected,mark_finalized
from callback import send_final_callback
# from mangum import Mangum
# ------------------ APP SETUP ------------------

app = FastAPI(title="Agentic Honeypot API")

@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI on Vercel"}

# handler = Mangum(app)
# ------------------ CORS ------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # restrict later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ MONGO ------------------

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
sessions_collection = db[SESSIONS_COLLECTION]

# Inject mongo into session manager
from session_manager import init_db
init_db(sessions_collection)

# ------------------ HEALTH API ------------------

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "honeypot-api"}

# ------------------ MAIN HONEYPOT API ------------------
@app.post("/honeypot")
def honeypot_endpoint(payload: dict, x_api_key: str = Header(None)):

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    session_id = payload["sessionId"]
    message_obj = payload["message"]
    text = message_obj["text"]

    # 1. Get session and history from DB
    session = get_session(session_id)
    history = session["messages"]
    update_session(session_id, message_obj)

    is_scam = detect_scam(text, history)

    if is_scam:
        mark_scam_detected(session_id)
    reply_text = generate_reply(text, history,is_scam )

    # 4. Create agent message object
    agent_message = {
        "sender": "user",
        "text": reply_text,
        "timestamp": int(time.time() * 1000)
    }

    # 5. Save agent reply
    update_session(session_id, agent_message)
    extract_intelligence(message_obj["text"], session["intelligence"])

    # 4. SAVE intelligence back to MongoDB  ❗❗❗
    update_intelligence(session_id, session["intelligence"])


    if should_finalize(session, text) or should_finalize(session, reply_text):
        send_final_callback(session_id, session)
        mark_finalized(session_id)
        
    if session["finalized"]:
        return {
            "status": "finalized"
            }
    else:
        return {
            "status": "success",
            "reply": reply_text
        }         
