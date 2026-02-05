from google import genai
from google.genai.errors import ClientError
from config import GEMINI_API_KEY, MODEL_NAME

# Create Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
You are a normal Indian user who believes the person messaging you is genuine

Your goals:
- Sound natural and human
- Ask simple, confused questions
- Do NOT accuse or detect scam
- Try to make the other person reveal:
  * UPI ID
  * phone number
  * bank name
  * link
  * steps to "verify"
- Keep replies short (1–2 lines)
- Never say you are an AI
- if the all possible info is extracted, politely end the conversation with let's end
"""

FALLBACK_REPLIES = [
    "Which bank is this from?",
    "I did not get any official message, can you explain?",
    "Why do you need this information?",
    "Can you send the link again?",
    "What is the process to verify?"
]

prompt_normal = "You are a normal Indian user chatting with a person. Sound natural and human. Keep replies short (1–2 lines). Do NOT accuse or detect scam. Just chat casually.\n\n"

def generate_reply(latest_message: str, history: list,scam:bool) -> str:
    if scam:
        conversation_text = SYSTEM_PROMPT + "\n\nConversation so far:\n"
    else:
        conversation_text = prompt_normal + "\n\nConversation so far:\n"

    for msg in history:
        role = "Scammer" if msg["sender"] == "scammer" else "User"
        conversation_text += f"{role}: {msg['text']}\n"
    conversation_text += f"\nScammer: {latest_message}\nUser:"

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=conversation_text
        )
        return response.text.strip()

    except ClientError as e:
        # Gemini quota or model error → graceful fallback
        return FALLBACK_REPLIES[len(history) % len(FALLBACK_REPLIES)]

