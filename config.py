import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    SKIP_TWILIO_VALIDATION = os.getenv("SKIP_TWILIO_VALIDATION", "false").lower() == "true"
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID")
    GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv(
        "GOOGLE_SERVICE_ACCOUNT_JSON", "service_account.json"
    )
    PORT = int(os.getenv("PORT", 3000))
