import re

# Regex patterns
UPI_PATTERN = r'\b[\w.-]+@upi\b'
PHONE_PATTERN = r'(\+91\d{10}|\b\d{10}\b)'
URL_PATTERN = r'https?://\S+'

SUSPICIOUS_KEYWORDS = [
    "urgent", "verify", "account blocked", "account suspended",
    "otp", "upi", "click", "link", "bank", "kyc",
    "refund", "lottery", "prize", "congratulations"
]


def extract_intelligence(text: str, intelligence_store: dict):
    """
    Extract scam-related intelligence from text and update intelligence_store.
    intelligence_store format:
    {
        "bankAccounts": [],
        "upiIds": [],
        "phishingLinks": [],
        "phoneNumbers": [],
        "suspiciousKeywords": []
    }
    """

    lowered = text.lower()

    # 1️⃣ Extract UPI IDs
    upis = re.findall(UPI_PATTERN, text)
    for upi in upis:
        if upi not in intelligence_store["upiIds"]:
            intelligence_store["upiIds"].append(upi)

    # 2️⃣ Extract phone numbers
    phones = re.findall(PHONE_PATTERN, text)
    for phone in phones:
        if phone not in intelligence_store["phoneNumbers"]:
            intelligence_store["phoneNumbers"].append(phone)

    # 3️⃣ Extract phishing links
    links = re.findall(URL_PATTERN, text)
    for link in links:
        if link not in intelligence_store["phishingLinks"]:
            intelligence_store["phishingLinks"].append(link)

    # 4️⃣ Extract suspicious keywords
    for word in SUSPICIOUS_KEYWORDS:
        if word in lowered and word not in intelligence_store["suspiciousKeywords"]:
            intelligence_store["suspiciousKeywords"].append(word)

    return intelligence_store
