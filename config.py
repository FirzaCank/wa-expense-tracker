import os
import base64
import json
import tempfile
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
    GOOGLE_SERVICE_ACCOUNT_B64 = os.getenv("SERVICE_ACCOUNT_JSON_B64", "") or os.getenv("GOOGLE_SERVICE_ACCOUNT_B64", "")
    PORT = int(os.getenv("PORT", 3000))
    
    @classmethod
    def get_service_account_path(cls) -> str:
        """Return path to service account JSON.
        
        If GOOGLE_SERVICE_ACCOUNT_B64 is set, decode and write to temp file.
        Otherwise, use GOOGLE_SERVICE_ACCOUNT_JSON path.
        """
        if cls.GOOGLE_SERVICE_ACCOUNT_B64:
            decoded = base64.b64decode(cls.GOOGLE_SERVICE_ACCOUNT_B64).decode()
            fd, path = tempfile.mkstemp(suffix=".json")
            os.write(fd, decoded.encode())
            os.close(fd)
            return path
        return cls.GOOGLE_SERVICE_ACCOUNT_JSON
