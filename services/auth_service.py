"""
Handles user registration and login.
Passwords are never stored in plain text - werkzeug hashes them before
saving to MongoDB.
"""
import re
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from services.db import get_users_collection
from config import Config

USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_.]{3,30}$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def validate_registration(username, email, password, confirm_password):
    """Server-side validation for registration fields."""
    if not username:
        return "Username is required."
    if len(username) < 3 or len(username) > 30:
        return "Username must be between 3 and 30 characters."
    if not USERNAME_REGEX.match(username):
        return "Username can only contain letters, numbers, underscores, and dots (no spaces)."

    if not email:
        return "Email address is required."
    if not EMAIL_REGEX.match(email):
        return "Please enter a valid email address (e.g. name@example.com)."

    if not password:
        return "Password is required."
    if len(password) < 6:
        return "Password must be at least 6 characters long."

    if password != confirm_password:
        return "Passwords do not match. Please re-enter."

    return None


def validate_login(identifier, password):
    """Server-side validation for login fields."""
    if not identifier:
        return "Please enter your username or email address."
    if not password:
        return "Please enter your password."
    return None


def get_user_customer_number(user):
    if not user:
        return ""
    return user.get("customer_number") or ""


def get_shareable_users(current_user_id: str, search_query: str = None):
    """
    Returns all registered users (excluding current_user_id) for the Share dialog.
    Supports search filtering by username, customer_number, or email.
    """
    from bson import ObjectId
    users = get_users_collection()

    query = {}
    curr_oid = None
    if current_user_id:
        try:
            curr_oid = ObjectId(current_user_id)
            query["_id"] = {"$ne": curr_oid}
        except Exception:
            pass

    if search_query:
        q = search_query.strip()
        regex_pattern = {"$regex": re.escape(q), "$options": "i"}
        or_clause = {
            "$or": [
                {"username": regex_pattern},
                {"customer_number": regex_pattern},
                {"email": regex_pattern},
            ]
        }
        if curr_oid:
            query = {"$and": [{"_id": {"$ne": curr_oid}}, or_clause]}
        else:
            query = or_clause

    user_docs = list(users.find(query).sort("username", 1))
    results = []
    for u in user_docs:
        results.append({
            "id": str(u["_id"]),
            "username": u.get("username", "Unknown"),
            "customer_number": u.get("customer_number") or "",
            "email": u.get("email", ""),
            "phone": u.get("phone", ""),
            "country_code": u.get("country_code", "+91"),
        })
    return results


def create_user(username, email, password):
    users = get_users_collection()
    username = username.strip()
    email = email.strip().lower()

    if users.find_one({"username": username}):
        return None, "This username is already taken. Please choose another username."

    if users.find_one({"email": email}):
        return None, "An account with this email is already registered. Please log in instead."

    user_doc = {
        "username": username,
        "email": email,
        "password_hash": generate_password_hash(password),
        # Only email listed in ADMIN_EMAILS (.env) gets admin access
        "is_admin": Config.is_admin_email(email),
        "created_at": datetime.now(timezone.utc),
    }
    result = users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id

    # Optional welcome email after successful registration
    try:
        from services import email_service
        email_service.send_welcome_email(email, username, is_google=False)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Could not send welcome email: {e}")

    return user_doc, None


def authenticate_user(identifier, password):
    """identifier = username OR email"""
    users = get_users_collection()
    identifier = (identifier or "").strip()
    user = users.find_one({"$or": [{"username": identifier}, {"email": identifier.lower()}]})

    if not user:
        return None, "No account found with that username or email. Please register first."

    stored_hash = user.get("password_hash")
    if not stored_hash:
        return None, "This account was registered using Google sign-in. Please click 'Continue with Google', or use 'Forgot Password?' to set a password."

    if not check_password_hash(stored_hash, password):
        return None, "Incorrect password. Please try again."

    # Keep admin role strictly synced with ADMIN_EMAILS
    is_admin = Config.is_admin_email(user.get("email", ""))
    if user.get("is_admin") != is_admin:
        users.update_one({"_id": user["_id"]}, {"$set": {"is_admin": is_admin}})
        user["is_admin"] = is_admin

    return user, None


def get_user_by_id(user_id):
    from bson import ObjectId
    users = get_users_collection()
    try:
        return users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None


def update_user_profile(user_id, username, email):
    """Updates a user's editable profile fields (username, email)."""
    from bson import ObjectId
    users = get_users_collection()

    try:
        user_oid = ObjectId(user_id)
    except Exception:
        return None, "Invalid user."

    username = (username or "").strip()
    email = (email or "").strip().lower()

    if not username or not email:
        return None, "Username and email are required."

    conflict = users.find_one({
        "_id": {"$ne": user_oid},
        "$or": [{"username": username}, {"email": email}],
    })
    if conflict:
        return None, "That username or email is already taken."

    users.update_one({"_id": user_oid}, {"$set": {"username": username, "email": email}})
    return users.find_one({"_id": user_oid}), None


def change_user_password(user_id, current_password, new_password):
    """Verifies the current password, then sets a new hashed password."""
    from bson import ObjectId
    users = get_users_collection()

    try:
        user_oid = ObjectId(user_id)
    except Exception:
        return False, "Invalid user."

    user = users.find_one({"_id": user_oid})
    if not user:
        return False, "User not found."

    if not check_password_hash(user["password_hash"], current_password):
        return False, "Current password is incorrect."

    if not new_password or len(new_password) < 6:
        return False, "New password must be at least 6 characters."

    users.update_one(
        {"_id": user_oid},
        {"$set": {"password_hash": generate_password_hash(new_password)}},
    )
    return True, None
