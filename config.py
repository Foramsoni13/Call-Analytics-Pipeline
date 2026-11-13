import os
from dotenv import load_dotenv

# Load variables from .env into the environment
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "call_analytics")

    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

    # Comma-separated list of emails that are auto-promoted to admin the
    # moment they register (case-insensitive). e.g. ADMIN_EMAILS=you@x.com,ops@x.com
    ADMIN_EMAILS = {
        e.strip().lower()
        for e in os.getenv("ADMIN_EMAILS", "foramsoni1312@gmail.com").split(",")
        if e.strip()
    }

    @classmethod
    def is_admin_email(cls, email: str) -> bool:
        if not email:
            return False
        from dotenv import load_dotenv
        load_dotenv(override=True)
        admins = {
            e.strip().lower()
            for e in os.getenv("ADMIN_EMAILS", "foramsoni1312@gmail.com").split(",")
            if e.strip()
        }
        return email.strip().lower() in admins

    # Whisper model served by Groq (cloud, free tier, no local CPU load)
    WHISPER_MODEL = "whisper-large-v3"

    # LLM used for summarization + classification
    LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")

    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
    ALLOWED_EXTENSIONS = {"mp3", "wav", "m4a", "ogg", "webm"}

    CALL_CATEGORIES = [
        "Hardware Issue",
        "Installation",
        "Billing",
        "Network Issue",
        "General Inquiry",
        "Complaint",
        "Other",
    ]

    # Used by the classification/extraction step in services/llm_service.py
    PRIORITY_LEVELS = ["Low", "Medium", "High", "Urgent"]
    RESOLUTION_STATUSES = ["Resolved", "Unresolved", "Escalated", "Follow-up Required"]

    # ==== Gmail SMTP Configuration ====
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "foramsoni2004@gmail.com")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "foramsoni2004@gmail.com")

    # Application base URL for email links (e.g. view shared calls)
    APP_BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:5000")

    # ==== Google OAuth 2.0 ====
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://127.0.0.1:5000/auth/google/callback")

    # ==== OTP & Password Reset Security ====
    OTP_EXPIRATION_SECONDS = 300       # 5 minutes
    OTP_RESEND_COOLDOWN_SECONDS = 60   # 1 minute between resend requests
    OTP_MAX_VERIFY_ATTEMPTS = 5        # Max invalid attempts before invalidating OTP
    RESET_TOKEN_EXPIRATION_SECONDS = 600  # 10 minutes to set new password after OTP verified
