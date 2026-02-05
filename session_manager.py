from datetime import datetime

# Mongo collection will be injected from main.py
sessions_collection = None


def init_db(collection):
    """
    Initialize MongoDB collection from main.py
    """
    global sessions_collection
    sessions_collection = collection


def create_new_session(session_id: str):
    session = {
        "sessionId": session_id,
        "messages": [],
        "intelligence": {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        },
        "totalMessages": 0,
        "scamDetected": False,
        "finalized": False,
        "createdAt": datetime.utcnow()
    }
    sessions_collection.insert_one(session)
    return session


def get_session(session_id: str):
    """
    Fetch session from DB or create new one.
    """
    session = sessions_collection.find_one({"sessionId": session_id})

    if not session:
        session = create_new_session(session_id)

    return session


def update_session(session_id: str, message_obj: dict):
    """
    Add message to session history.
    """
    sessions_collection.update_one(
        {"sessionId": session_id},
        {
            "$push": {"messages": message_obj},
            "$inc": {"totalMessages": 1}
        }
    )

def update_intelligence(session_id: str, intelligence: dict):
    """
    Persist extracted intelligence to MongoDB for a session.
    This should be called AFTER extract_intelligence().
    """

    sessions_collection.update_one(
        {"sessionId": session_id},
        {
            "$set": {
                "intelligence": intelligence
            }
        }
    )

def mark_scam_detected(session_id: str):
    sessions_collection.update_one(
        {"sessionId": session_id},
        {"$set": {"scamDetected": True}}
    )


def update_intelligence(session_id: str, intelligence: dict):
    """
    Save extracted intelligence.
    """
    sessions_collection.update_one(
        {"sessionId": session_id},
        {"$set": {"intelligence": intelligence}}
    )



def should_finalize(session: dict, latest_text: str) -> bool:
    """
    Finalize only when conversation explicitly signals completion.
    """

    if session["finalized"]:
        return False

    return detect_finalization(latest_text)



def mark_finalized(session_id: str):
    sessions_collection.update_one(
        {"sessionId": session_id},
        {"$set": {"finalized": True}}
    )

FINALIZE_KEYWORDS = [
    # completion
    "done",
    "completed",
    "finished",
    "all set",
    "successfully",
    "process complete",

    # thanks / exit
    "thank you",
    "thanks",
    "bye",
    "goodbye",

    # explicit termination
    "end this conversation",
    "end the conversation",
    "let's end",
    "let us end",
    "stop chatting",
    "no need to continue",
    "close this",
    "close the chat"
]


def detect_finalization(text: str) -> bool:
    text = text.lower()

    termination_verbs = ["end", "stop", "close", "finish"]
    conversation_words = ["chat", "conversation", "talk", "session"]

    # Direct phrase match
    if any(k in text for k in FINALIZE_KEYWORDS):
        return True

    # Intent-based match
    if any(v in text for v in termination_verbs) and any(c in text for c in conversation_words):
        return True

    return False
