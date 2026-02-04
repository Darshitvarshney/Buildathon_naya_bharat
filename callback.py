import requests
from config import GUVI_CALLBACK_URL
from session_manager import mark_finalized


def send_final_callback(session_id: str, session: dict):
    """
    Sends final extracted intelligence to GUVI evaluation endpoint.
    This should be called ONLY once per session.
    """

    intelligence = session["intelligence"]

    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": session["totalMessages"],
        "extractedIntelligence": {
            "bankAccounts": intelligence.get("bankAccounts", []),
            "upiIds": intelligence.get("upiIds", []),
            "phishingLinks": intelligence.get("phishingLinks", []),
            "phoneNumbers": intelligence.get("phoneNumbers", []),
            "suspiciousKeywords": intelligence.get("suspiciousKeywords", [])
        },
        "agentNotes": generate_agent_notes(intelligence)
    }

    try:
        response = requests.post(
            GUVI_CALLBACK_URL,
            json=payload,
            timeout=5
        )

        if response.status_code == 200:
            mark_finalized(session_id)
            print(f"[✓] Callback sent successfully for session {session_id}")
        else:
            print(f"[!] Callback failed ({response.status_code}): {response.text}")

    except Exception as e:
        print(f"[X] Callback error: {e}")


def generate_agent_notes(intelligence: dict) -> str:
    """
    Generate short summary of scammer behavior.
    """

    notes = []

    if intelligence["upiIds"]:
        notes.append("Requested UPI payment")
    if intelligence["phishingLinks"]:
        notes.append("Shared phishing link")
    if intelligence["phoneNumbers"]:
        notes.append("Provided phone number")
    if intelligence["suspiciousKeywords"]:
        notes.append("Used urgency and verification tactics")

    if not notes:
        return "Scam pattern detected with no direct payment info shared yet."

    return "; ".join(notes)
