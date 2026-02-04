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


def should_finalize(session: dict) -> bool:
    """
    Decide when to end conversation & send callback.
    """
    if session["finalized"]:
        return False

    # Heuristics: finalize if enough messages or enough intelligence
    if session["totalMessages"] >= 12:
        return True

    intel = session["intelligence"]

    if intel["upiIds"] or intel["phishingLinks"] or intel["phoneNumbers"]:
        return True

    return False


def mark_finalized(session_id: str):
    sessions_collection.update_one(
        {"sessionId": session_id},
        {"$set": {"finalized": True}}
    )
