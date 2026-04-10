import json
import tempfile
import os
from openai import AsyncOpenAI
from src.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


# ─── Intent & entity extraction ──────────────────────

INTENT_SYSTEM = """
You are a smart parser for AgroLink, an agricultural marketplace in Cameroon.
Users write in English, French, or Cameroonian Pidgin English.
They may make spelling mistakes, use abbreviations, or write very informally.

Extract a structured JSON object from the user message.

Return ONLY valid JSON with these fields:
{
  "intent": one of ["sell", "buy", "price_check", "yes", "no", "menu", "help", "greeting", "unknown"],
  "product": string or null (normalize to English: mais/maïs → maize, tomates → tomatoes),
  "quantity": number or null,
  "unit": string or null (bags, crates, kg, etc.),
  "price": number or null,
  "location": string or null,
  "language": one of ["en", "fr", "pidgin"],
  "raw_text": the original text
}

Examples:
- "Sell maize 10 bags" → intent: sell, product: maize, quantity: 10
- "Je veux vendre 5 sacs de tomates" → intent: sell, product: tomatoes, quantity: 5, language: fr
- "I get plantain plenty, na 8 bunch" → intent: sell, product: plantain, quantity: 8, language: pidgin
- "Buy 20 bags maize" → intent: buy, product: maize, quantity: 20
- "Combien coute le mais?" → intent: price_check, product: maize, language: fr
- "yes" / "oui" / "yes na" → intent: yes
- "no" / "non" / "no be dat" → intent: no
"""


async def parse_intent(text: str) -> dict:
    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": INTENT_SYSTEM},
                {"role": "user", "content": text},
            ],
            max_tokens=300,
            temperature=0,
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception as e:
        return {"intent": "unknown", "language": "en", "raw_text": text}


# ─── Language detection ───────────────────────────────

LANG_SYSTEM = """
Detect the language of this message and return ONLY one word:
- "en" for English
- "fr" for French  
- "pidgin" for Cameroonian Pidgin English

Pidgin clues: "na", "no be", "i get", "plenty", "wetin", "how much e cost", "make i"
"""


async def detect_language(text: str) -> str:
    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": LANG_SYSTEM},
                {"role": "user", "content": text},
            ],
            max_tokens=10,
            temperature=0,
        )
        lang = response.choices[0].message.content.strip().lower()
        return lang if lang in ["en", "fr", "pidgin"] else "en"
    except Exception:
        return "en"


# ─── Voice transcription (Whisper) ───────────────────

async def transcribe_voice(file_bytes: bytes, file_ext: str = "ogg") -> str:
    try:
        with tempfile.NamedTemporaryFile(suffix=f".{file_ext}", delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        with open(tmp_path, "rb") as f:
            transcript = await client.audio.transcriptions.create(
                model=settings.OPENAI_WHISPER_MODEL,
                file=f,
                response_format="text",
            )
        os.unlink(tmp_path)
        return transcript.strip()
    except Exception as e:
        return ""


# ─── Generate warm, human-like bot reply ─────────────

AMARA_SYSTEM = """
You are Amara, a warm and friendly assistant for AgroLink, an agricultural marketplace in Cameroon.
You help farmers sell their produce and connect buyers with the best local farmers.

Personality:
- Warm, encouraging, patient
- Use the person's name when you know it
- Keep messages SHORT — max 2 sentences per message
- Respond in the same language the user used (English, French, or Pidgin)
- For Pidgin, use natural Cameroonian expressions
- Never sound robotic — always sound like a helpful friend
- Use light emoji only when it feels natural (not excessive)

Constraints:
- Never give prices unless asked
- Never promise things you can't deliver
- If confused, ask one clear question
"""


async def generate_reply(
    conversation_history: list[dict],
    user_name: str = None,
    language: str = "en",
) -> str:
    system = AMARA_SYSTEM
    if user_name:
        system += f"\nThe user's name is {user_name}."
    system += f"\nRespond in: {'English' if language == 'en' else 'French' if language == 'fr' else 'Cameroonian Pidgin English'}"

    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "system", "content": system}] + conversation_history,
            max_tokens=200,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "I'm having a little trouble right now. Please try again in a moment! 🙏"
