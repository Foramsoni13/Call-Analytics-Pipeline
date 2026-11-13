"""
OTP and Password Reset Service for CallSense.
Manages cryptographically secure OTP generation, rate limiting, hashing,
verification, and single-use password resets with anti-enumeration protection.
"""
import re
import secrets
import logging
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

from config import Config
from services.db import get_db, get_users_collection
from services import email_service

logger = logging.getLogger(__name__)


def get_resets_collection():
    """Returns the MongoDB collection for password reset records."""
    return get_db()["password_resets"]


def generate_secure_otp() -> str:
    """Generates a cryptographically secure 6-digit OTP string."""
    # Guarantees a 6-digit number between 100000 and 999999
    code_int = secrets.randbelow(900000) + 100000
    return f"{code_int:06d}"


def request_password_reset_otp(raw_email: str) -> tuple[bool, str, dict]:
    """
    Initiates password recovery for an email address.
    To prevent user enumeration, always returns a success response to the client
    even if the email address does not exist in the database.
    """
    email = (raw_email or "").strip().lower()
    meta = {"email": email, "cooldown": Config.OTP_RESEND_COOLDOWN_SECONDS}

    if not email or "@" not in email:
        return False, "Please enter a valid email address.", meta

    users_col = get_users_collection()
    user = users_col.find_one({"email": email})

    if not user:
        # Anti-enumeration: mimic success response without sending email
        logger.info(f"[OTP] Password reset requested for non-existent email '{email}' (anti-enumeration response given)")
        return True, "If an account matches that email address, a 6-digit verification code has been sent.", meta

    now_utc = datetime.now(timezone.utc)
    resets_col = get_resets_collection()

    # Rate limiting: check if a reset was requested recently for this email
    latest = resets_col.find_one(
        {"email": email, "used": False},
        sort=[("created_at", -1)]
    )

    if latest:
        created_at = latest.get("created_at")
        if created_at:
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            elapsed = (now_utc - created_at).total_seconds()
            cooldown = Config.OTP_RESEND_COOLDOWN_SECONDS
            if elapsed < cooldown:
                wait_sec = int(cooldown - elapsed)
                return False, f"Please wait {wait_sec} seconds before requesting a new code.", {"email": email, "cooldown": wait_sec}

    # Invalidate all prior unverified OTP records for this email
    resets_col.update_many(
        {"email": email, "used": False},
        {"$set": {"used": True, "invalidated": True, "invalidated_at": now_utc}}
    )

    # Generate secure 6-digit OTP
    otp_code = generate_secure_otp()
    otp_hash = generate_password_hash(otp_code)
    expires_at = now_utc + timedelta(seconds=Config.OTP_EXPIRATION_SECONDS)

    reset_doc = {
        "email": email,
        "user_id": str(user["_id"]),
        "username": user.get("username", ""),
        "otp_hash": otp_hash,
        "created_at": now_utc,
        "expires_at": expires_at,
        "attempts": 0,
        "max_attempts": Config.OTP_MAX_VERIFY_ATTEMPTS,
        "verified": False,
        "verified_at": None,
        "reset_token": None,
        "reset_token_expires_at": None,
        "used": False,
        "used_at": None,
    }

    resets_col.insert_one(reset_doc)

    # Send OTP email via Gmail SMTP
    sent_ok, send_err = email_service.send_otp_email(
        email,
        otp_code,
        minutes_valid=int(Config.OTP_EXPIRATION_SECONDS / 60)
    )

    if not sent_ok:
        logger.warning(f"[OTP] Could not send email to {email}: {send_err}")
        return False, f"Failed to deliver verification code: {send_err}", meta

    return True, "A 6-digit verification code has been sent to your email address.", meta


def verify_password_reset_otp(raw_email: str, entered_otp: str) -> tuple[bool, str, str | None]:
    """
    Verifies the 6-digit OTP for the given email.
    Enforces maximum attempts and expiration.
    Returns (True, message, reset_token) on success, or (False, error_message, None) on failure.
    """
    email = (raw_email or "").strip().lower()
    otp_str = (entered_otp or "").strip()

    if not email:
        return False, "Email address is required.", None

    if len(otp_str) != 6 or not otp_str.isdigit():
        return False, "Please enter a valid 6-digit verification code.", None

    now_utc = datetime.now(timezone.utc)
    resets_col = get_resets_collection()

    doc = resets_col.find_one(
        {"email": email, "verified": False, "used": False},
        sort=[("created_at", -1)]
    )

    if not doc:
        return False, "No active verification code found for this email. Please request a new code.", None

    # Check expiration
    expires_at = doc.get("expires_at")
    if expires_at:
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if now_utc > expires_at:
            resets_col.update_one({"_id": doc["_id"]}, {"$set": {"used": True, "expired": True}})
            return False, "This verification code has expired. Please request a new code.", None

    # Check attempt limit
    attempts = doc.get("attempts", 0)
    max_attempts = doc.get("max_attempts", Config.OTP_MAX_VERIFY_ATTEMPTS)

    if attempts >= max_attempts:
        resets_col.update_one({"_id": doc["_id"]}, {"$set": {"used": True, "locked": True}})
        return False, "Too many incorrect attempts. This code has been invalidated. Please request a new code.", None

    # Validate OTP hash
    if not check_password_hash(doc["otp_hash"], otp_str):
        new_attempts = attempts + 1
        remaining = max(0, max_attempts - new_attempts)
        resets_col.update_one({"_id": doc["_id"]}, {"$set": {"attempts": new_attempts}})

        if remaining == 0:
            resets_col.update_one({"_id": doc["_id"]}, {"$set": {"used": True, "locked": True}})
            return False, "Too many incorrect attempts. This code has been invalidated. Please request a new code.", None

        return False, f"Incorrect verification code. {remaining} attempt{'s' if remaining != 1 else ''} remaining.", None

    # OTP is valid! Mark verified and issue a temporary single-use reset token
    reset_token = secrets.token_urlsafe(32)
    token_expires_at = now_utc + timedelta(seconds=Config.RESET_TOKEN_EXPIRATION_SECONDS)

    resets_col.update_one(
        {"_id": doc["_id"]},
        {
            "$set": {
                "verified": True,
                "verified_at": now_utc,
                "reset_token": reset_token,
                "reset_token_expires_at": token_expires_at,
            }
        }
    )

    return True, "Verification successful. You can now set a new password.", reset_token


def validate_new_password_strength(password: str) -> str | None:
    """Validates the strength requirements for a new password."""
    if not password:
        return "Password is required."
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Za-z]", password):
        return "Password must contain at least one letter."
    if not re.search(r"[0-9]", password):
        return "Password must contain at least one number."
    return None


def complete_password_reset(reset_token: str, new_password: str, confirm_password: str) -> tuple[bool, str]:
    """
    Completes password reset using a verified reset token.
    Enforces token validity, expiration, password match, and strength.
    Hashes the new password and triggers a confirmation email.
    """
    token = (reset_token or "").strip()
    if not token:
        return False, "Invalid or missing reset token. Please request a new password reset."

    if new_password != confirm_password:
        return False, "Passwords do not match. Please re-enter."

    strength_err = validate_new_password_strength(new_password)
    if strength_err:
        return False, strength_err

    now_utc = datetime.now(timezone.utc)
    resets_col = get_resets_collection()

    doc = resets_col.find_one({"reset_token": token, "verified": True, "used": False})
    if not doc:
        return False, "Reset session is invalid or has already been used. Please start over."

    token_expires = doc.get("reset_token_expires_at")
    if token_expires:
        if token_expires.tzinfo is None:
            token_expires = token_expires.replace(tzinfo=timezone.utc)
        if now_utc > token_expires:
            resets_col.update_one({"_id": doc["_id"]}, {"$set": {"used": True, "expired": True}})
            return False, "Your password reset session has expired. Please request a new code."

    # Update user password securely in MongoDB
    users_col = get_users_collection()
    user_id = doc.get("user_id")

    try:
        user_oid = ObjectId(user_id)
        user = users_col.find_one({"_id": user_oid})
    except Exception:
        user = None

    if not user:
        return False, "User account not found."

    new_hash = generate_password_hash(new_password)
    users_col.update_one(
        {"_id": user["_id"]},
        {"$set": {"password_hash": new_hash}}
    )

    # Invalidate reset record (single-use)
    resets_col.update_one(
        {"_id": doc["_id"]},
        {"$set": {"used": True, "used_at": now_utc}}
    )

    # Invalidate any other active reset tokens for this user
    resets_col.update_many(
        {"user_id": str(user["_id"]), "used": False},
        {"$set": {"used": True, "invalidated": True, "invalidated_at": now_utc}}
    )

    # Send confirmation email
    email_service.send_password_reset_confirmation_email(user["email"], user.get("username"))

    return True, "Your password has been reset successfully. Please log in with your new password."
