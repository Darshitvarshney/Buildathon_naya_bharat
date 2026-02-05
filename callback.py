import os
import requests
from config import GUVI_CALLBACK_URL

# Enable / disable real callback (VERY IMPORTANT)
ENABLE_GUVI_CALLBACK = os.getenv("ENABLE_GUVI_CALLBACK", "false").lower() == "true"


def send_final_callback(session_id: str, session: dict):
    """
    Sends final extracted intelligence to GUVI evaluation endpoint.
    This should be called ONLY once per session.
    """

    intelligence = session.get("intelligence", {})

    payload = {
        "sessionId": session_id,
        "scamDetected": session.get("scamDetected", False),
        "totalMessagesExchanged": session.get("totalMessages", 0),
        "extractedIntelligence": {
            "bankAccounts": intelligence.get("bankAccounts", []),
            "upiIds": intelligence.get("upiIds", []),
            "phishingLinks": intelligence.get("phishingLinks", []),
            "phoneNumbers": intelligence.get("phoneNumbers", []),
            "suspiciousKeywords": intelligence.get("suspiciousKeywords", [])
        },
        "agentNotes": generate_agent_notes(intelligence)
    }

    # 🧪 DEV MODE (testing)
    if not ENABLE_GUVI_CALLBACK:
        print("[DEV MODE] GUVI callback disabled")
        print(payload)
        return

    # 🚀 PRODUCTION MODE (final evaluation)
    try:
        response = requests.post(
            GUVI_CALLBACK_URL,
            json=payload,
            timeout=5
        )
        response.raise_for_status()
        print(f"[✓] Callback sent successfully for session {session_id}")

    except Exception as e:
        print(f"[X] Callback error: {e}")


def generate_agent_notes(intelligence: dict) -> str:
    """
    Generate short summary of scammer behavior.
    """

    notes = []

    if intelligence.get("upiIds"):
        notes.append("Requested UPI payment")
    if intelligence.get("phishingLinks"):
        notes.append("Shared phishing link")
    if intelligence.get("phoneNumbers"):
        notes.append("Provided phone number")
    if intelligence.get("suspiciousKeywords"):
        notes.append("Used urgency or verification tactics")

    if not notes:
        return "Scam behavior detected without direct payment details."

    return "; ".join(notes)
