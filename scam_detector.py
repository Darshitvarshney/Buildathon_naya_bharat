import re

# High-risk keywords commonly used in scams
SCAM_KEYWORDS = [
    "account blocked",
    "account suspended",
    "verify immediately",
    "verify now",
    "urgent",
    "bank",
    "upi",
    "otp",
    "click link",
    "payment failed",
    "kyc",
    "dear customer",
    "limited time",
    "refund",
    "prize",
    "lottery",
    "congratulations"
]

# Patterns that indicate scam intent
UPI_PATTERN = r'\b[\w.-]+@upi\b'
PHONE_PATTERN = r'\+91\d{10}|\b\d{10}\b'
URL_PATTERN = r'https?://\S+'


def detect_scam(message_text: str, history: list) -> bool:
    """
    Returns True if scam intent is detected, else False.
    """

    text = message_text.lower()

    # 1️⃣ Keyword-based detection
    keyword_hits = sum(1 for word in SCAM_KEYWORDS if word in text)

    # 2️⃣ Pattern-based detection
    upi_found = re.search(UPI_PATTERN, text)
    phone_found = re.search(PHONE_PATTERN, text)
    link_found = re.search(URL_PATTERN, text)

    # 3️⃣ Context-based detection (from conversation history)
    history_text = " ".join([msg["text"].lower() for msg in history]) if history else ""

    history_hits = sum(1 for word in SCAM_KEYWORDS if word in history_text)

    # 4️⃣ Scoring logic (simple heuristic)
    score = 0
    score += keyword_hits * 2
    score += history_hits

    if upi_found:
        score += 3
    if phone_found:
        score += 2
    if link_found:
        score += 3

    # 5️⃣ Threshold decision
    if score >= 3:
        return True

    return False

