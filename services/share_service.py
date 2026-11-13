"""
Service to handle call sharing between registered users.
Allows users to share processed calls and their analytics with other registered accounts.
"""
from datetime import datetime, timezone
from bson import ObjectId
from services.db import get_calls_collection, get_users_collection


def share_call(
    call_id: str,
    recipient_id: str = None,
    sender_id: str = None,
    sender_username: str = None,
    customer_name: str = None,
    country_code: str = "+91",
    customer_number: str = None,
    customer_phone: str = None
):
    """
    Shares a call record with another user or customer.
    Stores customer details (name, country code, number), recipient ID,
    and sender info in the call's `shared_with` list.
    """
    import re
    calls_col = get_calls_collection()
    users_col = get_users_collection()

    try:
        call_oid = ObjectId(call_id)
    except Exception:
        return False, "Invalid call ID."

    call = calls_col.find_one({"_id": call_oid})
    if not call:
        return False, "Call record not found."

    # Check ownership (owner, admin, or user with whom call has been shared)
    sender = users_col.find_one({"_id": ObjectId(sender_id)}) if sender_id else None
    is_admin = bool(sender and sender.get("is_admin"))
    is_owner = (call.get("uploaded_by") == str(sender_id))
    is_shared_recipient = any(str(item.get("user_id")) == str(sender_id) for item in call.get("shared_with", []))

    if not (is_owner or is_admin or is_shared_recipient):
        return False, "You do not have permission to share this call."

    recipient = None
    if recipient_id:
        try:
            recipient_oid = ObjectId(recipient_id)
            if str(recipient_id) == str(sender_id):
                return False, "You cannot share a call with yourself."
            recipient = users_col.find_one({"_id": recipient_oid})
        except Exception:
            recipient = None

    # Customer name and phone number are strictly compulsory
    c_name = (customer_name or "").strip()
    if not c_name:
        return False, "Customer Name is compulsory."

    raw_num = (customer_number or customer_phone or "").strip()
    clean_digits = re.sub(r"[^\d]", "", raw_num)
    if not raw_num or len(clean_digits) < 7:
        return False, "Customer phone / mobile number is compulsory (minimum 7 digits)."

    c_code = (country_code or "+91").strip()
    if not c_code.startswith("+"):
        c_code = "+" + c_code

    if not recipient and raw_num:
        # Match exact customer_number like CUST-1002
        recipient = users_col.find_one({"customer_number": {"$regex": f"^{re.escape(raw_num)}$", "$options": "i"}})
        if not recipient:
            # Match phone number
            recipient = users_col.find_one({"phone": raw_num})

    if not recipient and c_name:
        recipient = users_col.find_one({"username": {"$regex": f"^{re.escape(c_name)}$", "$options": "i"}})

    if recipient and str(recipient["_id"]) == str(sender_id):
        return False, "You cannot share a call with yourself."

    # Determine display values
    final_name = c_name or (recipient.get("username") if recipient else "Customer")
    
    # Format customer number / phone cleanly with country code
    if raw_num.startswith("+"):
        display_num = raw_num
    else:
        display_num = f"{c_code} {raw_num}"

    sender_cnum = ""

    now_utc = datetime.now(timezone.utc)
    share_entry = {
        "user_id": str(recipient["_id"]) if recipient else None,
        "username": recipient.get("username") if recipient else final_name,
        "customer_name": final_name,
        "country_code": c_code,
        "customer_phone": raw_num,
        "customer_number": display_num,
        "email": recipient.get("email", "") if recipient else "",
        "shared_by": str(sender_id),
        "shared_by_username": sender_username or (sender.get("username") if sender else "Unknown"),
        "shared_by_customer_number": "",
        "shared_at": now_utc,
    }

    # Remove any existing share entry for this user or customer number to prevent duplicates
    pull_conditions = []
    if recipient:
        pull_conditions.append({"user_id": str(recipient["_id"])})
    if display_num:
        pull_conditions.append({"customer_number": display_num})
    if raw_num:
        pull_conditions.append({"customer_phone": raw_num})

    if pull_conditions:
        pull_filter = pull_conditions[0] if len(pull_conditions) == 1 else {"$or": pull_conditions}
        calls_col.update_one(
            {"_id": call_oid},
            {"$pull": {"shared_with": pull_filter}}
        )

    calls_col.update_one(
        {"_id": call_oid},
        {"$push": {"shared_with": share_entry}}
    )

    # Send email notification to recipient if they have an email registered
    if recipient and recipient.get("email"):
        try:
            from services import email_service
            from config import Config
            email_service.send_call_shared_email(
                to_email=recipient["email"],
                recipient_name=recipient.get("username") or final_name,
                sender_username=sender_username or (sender.get("username") if sender else "A team member"),
                call_title=call.get("filename") or "Call recording",
                call_url=f"{Config.APP_BASE_URL.rstrip('/')}/dashboard?view=shared",
                call_category=call.get("category"),
                call_language=call.get("language"),
                call_duration=call.get("audio_duration_seconds"),
                share_date=now_utc.strftime("%B %d, %Y at %I:%M %p UTC"),
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Could not send call-sharing email: {e}")

    return True, f"Successfully shared '{call.get('filename')}' with {final_name} ({display_num})."


def unshare_call(call_id: str, recipient_id: str = None, requester_id: str = None, customer_number: str = None):
    """
    Revokes sharing of a call with a recipient or customer.
    Can be performed by the call owner, admin, or the recipient themselves (to dismiss).
    Supports removal by recipient user ID or customer number.
    """
    calls_col = get_calls_collection()
    users_col = get_users_collection()

    try:
        call_oid = ObjectId(call_id)
    except Exception:
        return False, "Invalid call ID."

    call = calls_col.find_one({"_id": call_oid})
    if not call:
        return False, "Call not found."

    requester = users_col.find_one({"_id": ObjectId(requester_id)}) if requester_id else None
    is_admin = bool(requester and requester.get("is_admin"))
    is_owner = call.get("uploaded_by") == str(requester_id)
    is_recipient = bool(recipient_id and str(recipient_id) == str(requester_id))

    if not (is_owner or is_admin or is_recipient):
        return False, "You do not have permission to remove this share."

    pull_conditions = []
    if recipient_id and str(recipient_id) not in ("None", "", "undefined"):
        pull_conditions.append({"user_id": str(recipient_id)})
    if customer_number and str(customer_number).strip():
        pull_conditions.append({"customer_number": str(customer_number).strip()})

    if not pull_conditions:
        return False, "Target recipient to remove was not specified."

    pull_filter = pull_conditions[0] if len(pull_conditions) == 1 else {"$or": pull_conditions}

    calls_col.update_one(
        {"_id": call_oid},
        {"$pull": {"shared_with": pull_filter}}
    )
    return True, "Call share removed."


def get_shared_calls_for_user(user_id: str):
    """
    Retrieves all calls shared with the given user_id.
    Attaches the matching `shared_info` object to each call for easy template display,
    enriching sender customer number and recipient customer details.
    """
    calls_col = get_calls_collection()
    users_col = get_users_collection()
    raw_calls = list(
        calls_col.find({"shared_with.user_id": str(user_id)})
        .sort("created_at", -1)
    )

    enriched_calls = []
    for call in raw_calls:
        # Locate the specific share entry for this user
        shared_info = None
        for item in call.get("shared_with", []):
            if item.get("user_id") == str(user_id):
                shared_info = dict(item)
                break

        if shared_info:
            # Enrich sender username if missing
            if shared_info.get("shared_by"):
                try:
                    s_user = users_col.find_one({"_id": ObjectId(shared_info["shared_by"])})
                    if s_user and not shared_info.get("shared_by_username"):
                        shared_info["shared_by_username"] = s_user.get("username", "Unknown")
                except Exception:
                    pass

            # Enrich recipient customer name if missing
            if not shared_info.get("customer_name"):
                shared_info["customer_name"] = shared_info.get("username") or "Customer"

        call["shared_info"] = shared_info
        enriched_calls.append(call)

    return enriched_calls


def is_call_accessible(call: dict, user_id: str, is_admin: bool = False) -> bool:
    """Checks if a user has permission to view a call (owner, admin, or shared recipient)."""
    if not call or not user_id:
        return False
    if is_admin:
        return True
    if call.get("uploaded_by") == str(user_id):
        return True
    for item in call.get("shared_with", []):
        if item.get("user_id") == str(user_id):
            return True
    return False
