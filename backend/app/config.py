import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.getenv("CHATBOT_DATA_DIR", str(BASE_DIR / "backend" / "data")))
DATA_DIR.mkdir(parents=True, exist_ok=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

_raw_origins = os.getenv("ALLOWED_ORIGINS", "*").strip()
ALLOWED_ORIGINS = ["*"] if _raw_origins == "*" else [x.strip() for x in _raw_origins.split(",") if x.strip()]

WIDGET_CONFIGS = {
    "COLLEGE_ABC_001": {
        "widget_id": "COLLEGE_ABC_001",
        "name": "College Assistant",
        "college_name": "ABC College",
        "logo_url": "",
        "primary_color": "#4B52F5",
        "welcome_message": "Hello! How can I help you today?",
        "language": "en",
        "position": "bottom-right",
        "show_sources": True,
        "show_feedback": True,
        "suggested_questions": [
            "What courses are available?",
            "What are the admission requirements?",
            "What is the fee structure?",
            "Is hostel accommodation available?"
        ]
    }
}
