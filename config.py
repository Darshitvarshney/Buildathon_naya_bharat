import os
from dotenv import load_dotenv

load_dotenv()  # load .env file if present

# ------------------ SECURITY ------------------

API_KEY = os.getenv("HONEYPOT_API_KEY", "CHANGE_ME_SECRET_KEY")

# ------------------ GUVI CALLBACK ------------------

GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

# ------------------ DATABASE ------------------

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "honeypot_db"
SESSIONS_COLLECTION = "sessions"

# ------------------ AGENT SETTINGS ------------------

MAX_MESSAGES = 15
FINALIZE_AFTER_MESSAGES = 12

# ------------------ LLM ------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "models/gemini-2.5-flash"
