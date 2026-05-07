import json
from datetime import date

from google import genai

from config import Config

MODEL = "gemini-2.5-flash"

CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Other"]
PAYMENT_METHODS = ["Cash", "Transfer", "Credit Card", "Debit Card", "E-Wallet", "Other"]


def parse_expense(message: str) -> dict:
    """Send a WhatsApp message to Gemini to extract expense details.

    Returns a dict with keys:
        date         – YYYY-MM-DD
        amount       – numeric (IDR, no symbol)
        category     – one of CATEGORIES
        description  – short description
        payment_method – one of PAYMENT_METHODS
    """
    client = genai.Client(api_key=Config.GEMINI_API_KEY)
    today = date.today().isoformat()

    prompt = f"""You are an expense tracking assistant. Extract expense information from the message below.
Today's date: {today}

Return ONLY a valid JSON object (no markdown, no explanation) with these fields:
- date: YYYY-MM-DD format (use today if not specified)
- amount: numeric value in IDR without currency symbol (e.g. 50000)
- category: one of {CATEGORIES}
- description: short description of the expense
- payment_method: one of {PAYMENT_METHODS} (default to "Cash" if not mentioned)

Message: "{message}"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )

    text = response.text.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    data = json.loads(text)

    # Normalise to allowed values
    if data.get("category") not in CATEGORIES:
        data["category"] = "Other"
    if data.get("payment_method") not in PAYMENT_METHODS:
        data["payment_method"] = "Other"

    return data
