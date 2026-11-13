"""
Google OAuth 2.0 / OpenID Connect (OIDC) service for CallSense.
Handles secure authorization flow, token exchange, cryptographic ID token verification,
and safe account association.
"""
import re
import urllib.parse
import logging
from datetime import datetime, timezone
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from config import Config
from services.db import get_users_collection
from services import email_service

logger = logging.getLogger(__name__)

GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"


def is_google_oauth_configured() -> bool:
    """Checks whether valid Google OAuth credentials have been set in the environment."""
    client_id = (Config.GOOGLE_CLIENT_ID or "").strip()
    client_secret = (Config.GOOGLE_CLIENT_SECRET or "").strip()
    if not client_id or not client_secret:
        return False
    if "your_google_client_id" in client_id.lower() or "your_google_client_secret" in client_secret.lower():
        return False
    return True


def get_google_auth_url(state: str) -> str:
    """Constructs the Google OAuth 2.0 authorization URL."""
    params = {
        "client_id": Config.GOOGLE_CLIENT_ID,
        "redirect_uri": Config.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    }
    return f"{GOOGLE_AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}"


def exchange_code_for_token(code: str) -> tuple[dict | None, str | None]:
    """Exchanges an authorization code for Google access and ID tokens."""
    payload = {
        "code": code,
        "client_id": Config.GOOGLE_CLIENT_ID,
        "client_secret": Config.GOOGLE_CLIENT_SECRET,
        "redirect_uri": Config.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(GOOGLE_TOKEN_ENDPOINT, data=payload, headers=headers, timeout=12)
        if response.status_code != 200:
            err_json = {}
            try:
                err_json = response.json()
            except Exception:
                pass
            err_desc = err_json.get("error_description") or err_json.get("error") or response.text
            logger.error(f"[GoogleOAuth] Token exchange failed ({response.status_code}): {err_desc}")
            return None, f"Google token exchange failed: {err_desc}"

        return response.json(), None
    except Exception as e:
        logger.error(f"[GoogleOAuth] Network exception during token exchange: {e}")
        return None, f"Failed to connect to Google OAuth service: {str(e)}"


def verify_id_token(id_token_jwt: str) -> tuple[dict | None, str | None]:
    """
    Validates Google ID token cryptographically:
    - Verifies RSA signature against Google's public keys
    - Verifies issuer is accounts.google.com or https://accounts.google.com
    - Verifies audience matches Config.GOOGLE_CLIENT_ID
    - Verifies token expiration
    """
    if not id_token_jwt:
        return None, "Missing Google ID token."

    try:
        request_adapter = google_requests.Request()
        payload = id_token.verify_oauth2_token(
            id_token_jwt,
            request_adapter,
            audience=Config.GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10
        )

        issuer = payload.get("iss", "")
        if issuer not in ("accounts.google.com", "https://accounts.google.com"):
            return None, f"Invalid ID token issuer: {issuer}"

        return payload, None
    except ValueError as e:
        logger.error(f"[GoogleOAuth] ID token validation error: {e}")
        return None, f"Google ID token validation failed: {str(e)}"
    except Exception as e:
        logger.error(f"[GoogleOAuth] Unexpected error verifying ID token: {e}")
        return None, f"Failed to verify Google token: {str(e)}"


def _generate_unique_username(base_name: str, email: str, users_col) -> str:
    """Generates an alphanumeric username conforming to USERNAME_REGEX (3-30 chars)."""
    clean = re.sub(r"[^a-zA-Z0-9_.]", "", base_name or "")
    if len(clean) < 3:
        email_prefix = email.split("@")[0]
        clean = re.sub(r"[^a-zA-Z0-9_.]", "", email_prefix)

    if len(clean) < 3:
        clean = f"user_{clean}"

    candidate = clean[:24]
    if not users_col.find_one({"username": candidate}):
        return candidate

    import secrets
    for _ in range(50):
        suffix = str(secrets.randbelow(9000) + 1000)
        candidate = f"{clean[:20]}_{suffix}"
        if not users_col.find_one({"username": candidate}):
            return candidate

    return f"user_{secrets.token_hex(4)}"


def authenticate_or_register_google_user(id_info: dict) -> tuple[dict | None, bool, str | None]:
    """
    Safely finds or creates a user account based on verified Google ID token payload.
    - Prevents account enumeration and duplicates.
    - Safe account linking: Only links to existing account if email is verified.
    - Never elevates a user to admin automatically unless listed in ADMIN_EMAILS.
    Returns: (user_doc, is_new_user, error_message)
    """
    google_id = id_info.get("sub")
    email = (id_info.get("email") or "").strip().lower()
    email_verified = id_info.get("email_verified", False)
    display_name = id_info.get("name", "")

    if not google_id or not email:
        return None, False, "Google account did not return a valid subject ID or email address."

    if not email_verified:
        return None, False, "Your Google email address has not been verified by Google. Please verify it first."

    users_col = get_users_collection()
    now_utc = datetime.now(timezone.utc)

    # 1. Check if user with this google_id already exists
    user = users_col.find_one({"google_id": google_id})
    if user:
        # Sync admin privileges strictly based on ADMIN_EMAILS
        is_admin = Config.is_admin_email(user.get("email", ""))
        if user.get("is_admin") != is_admin:
            users_col.update_one({"_id": user["_id"]}, {"$set": {"is_admin": is_admin}})
            user["is_admin"] = is_admin
        return user, False, None

    # 2. Check if user with this verified email exists (safe linking)
    existing_by_email = users_col.find_one({"email": email})
    if existing_by_email:
        # Safe linking because Google verified this email address belongs to this identity
        users_col.update_one(
            {"_id": existing_by_email["_id"]},
            {
                "$set": {
                    "google_id": google_id,
                    "auth_provider": existing_by_email.get("auth_provider") or "google_and_password",
                    "google_linked_at": now_utc,
                }
            }
        )
        existing_by_email = users_col.find_one({"_id": existing_by_email["_id"]})
        # Check admin role
        is_admin = Config.is_admin_email(email)
        if existing_by_email.get("is_admin") != is_admin:
            users_col.update_one({"_id": existing_by_email["_id"]}, {"$set": {"is_admin": is_admin}})
            existing_by_email["is_admin"] = is_admin
        logger.info(f"[GoogleOAuth] Safely linked Google identity {google_id} to existing user '{existing_by_email['username']}'")
        return existing_by_email, False, None

    # 3. New user registration via Google
    unique_username = _generate_unique_username(display_name, email, users_col)
    is_admin = Config.is_admin_email(email)  # Never admin unless in ADMIN_EMAILS

    new_user_doc = {
        "username": unique_username,
        "email": email,
        "google_id": google_id,
        "auth_provider": "google",
        "password_hash": None,  # No local password by default; can set later via Forgot Password
        "is_admin": is_admin,
        "created_at": now_utc,
    }

    result = users_col.insert_one(new_user_doc)
    new_user_doc["_id"] = result.inserted_id

    # Send welcome email for Google sign-in
    try:
        email_service.send_welcome_email(email, unique_username, is_google=True)
    except Exception as e:
        logger.warning(f"[GoogleOAuth] Failed to send welcome email to {email}: {e}")

    logger.info(f"[GoogleOAuth] Created new user '{unique_username}' via Google OAuth (admin={is_admin})")
    return new_user_doc, True, None
