import os
import secrets
from datetime import datetime, timezone
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify, send_file, send_from_directory,
    Response, abort
)
from werkzeug.utils import secure_filename

from config import Config
from services.db import get_calls_collection, get_users_collection
from services.auth_service import (
    create_user, authenticate_user, get_user_by_id,
    update_user_profile, change_user_password,
    validate_registration, validate_login,
    get_shareable_users, get_user_customer_number,
)
from services.share_service import (
    share_call, unshare_call, get_shared_calls_for_user, is_call_accessible
)
from services import otp_service
from services import google_auth_service
from services.pipeline import run_pipeline
from services import admin_service
from services.export_service import generate_calls_excel, generate_single_call_pdf

app = Flask(__name__)
app.config.from_object(Config)
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)


@app.cli.command("make-admin")
def make_admin_command():
    """Promote an existing user to admin.

    Usage:  flask --app app.py make-admin someone@example.com
    (Run this from the project folder, with your virtualenv/venv active.)
    """
    import click
    from services.db import get_users_collection

    email = click.prompt("Email of the user to promote").strip().lower()
    users = get_users_collection()
    result = users.update_one({"email": email}, {"$set": {"is_admin": True}})
    if result.matched_count == 0:
        click.echo(f"No user found with email '{email}'.")
    else:
        click.echo(f"'{email}' is now an admin. They'll see the Admin tab next time they log in.")


# ---------- helpers ----------

def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("login"))
        if not session.get("is_admin"):
            flash("Admin access required.", "error")
            return redirect(url_for("dashboard"))
        return view_func(*args, **kwargs)
    return wrapped


def allowed_file(filename):
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@app.before_request
def ensure_session_meta():
    if "customer_number" in session:
        session.pop("customer_number", None)


# ---------- splash ----------

@app.route("/")
def splash():
    return render_template("splash.html")


# ---------- auth ----------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        val_err = validate_registration(username, email, password, confirm)
        if val_err:
            flash(val_err, "error")
            return render_template("register.html", username=username, email=email)

        user, error = create_user(username, email, password)
        if error:
            flash(error, "error")
            return render_template("register.html", username=username, email=email)

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        if session.get("is_admin"):
            return redirect(url_for("admin_overview"))
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")

        val_err = validate_login(identifier, password)
        if val_err:
            flash(val_err, "error")
            return render_template("login.html", identifier=identifier)

        user, error = authenticate_user(identifier, password)
        if error:
            flash(error, "error")
            return render_template("login.html", identifier=identifier)

        session["user_id"] = str(user["_id"])
        session["username"] = user["username"]
        session["is_admin"] = bool(user.get("is_admin", False))
        flash(f"Welcome back, {user['username']}!", "success")
        if session["is_admin"]:
            return redirect(url_for("admin_overview"))
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))


def mask_email(email: str) -> str:
    """Masks an email like f***i@example.com for privacy on verification screens."""
    if not email or "@" not in email:
        return email
    user_part, domain_part = email.split("@", 1)
    if len(user_part) <= 2:
        masked_user = user_part[0] + "*"
    else:
        masked_user = user_part[0] + ("*" * (len(user_part) - 2)) + user_part[-1]
    return f"{masked_user}@{domain_part}"


# ---------- forgot password with email otp ----------

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if not email:
            flash("Please enter your registered email address.", "error")
            return render_template("forgot_password.html", email=email)

        success, message, meta = otp_service.request_password_reset_otp(email)
        if not success:
            flash(message, "error")
            return render_template("forgot_password.html", email=email)

        # Anti-enumeration response: always confirm that code has been dispatched
        session["reset_email"] = email
        flash(message, "success")
        return redirect(url_for("verify_otp", email=email))

    return render_template("forgot_password.html")


@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    email = request.args.get("email") or request.form.get("email") or session.get("reset_email")
    if not email:
        flash("Please enter your email to start the password reset process.", "error")
        return redirect(url_for("forgot_password"))

    email = email.strip().lower()
    masked = mask_email(email)

    if request.method == "POST":
        otp = request.form.get("otp", "").strip()
        ok, msg, reset_token = otp_service.verify_password_reset_otp(email, otp)
        if not ok:
            flash(msg, "error")
            return render_template(
                "verify_otp.html",
                email=email,
                masked_email=masked,
                expires_in=Config.OTP_EXPIRATION_SECONDS,
                cooldown=Config.OTP_RESEND_COOLDOWN_SECONDS
            )

        session["reset_token"] = reset_token
        session["reset_email"] = email
        flash(msg, "success")
        return redirect(url_for("reset_password", token=reset_token))

    return render_template(
        "verify_otp.html",
        email=email,
        masked_email=masked,
        expires_in=Config.OTP_EXPIRATION_SECONDS,
        cooldown=Config.OTP_RESEND_COOLDOWN_SECONDS
    )


@app.route("/resend-otp", methods=["POST"])
def resend_otp():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    email = (request.form.get("email") or session.get("reset_email") or "").strip().lower()
    if not email:
        flash("Email address missing. Please restart password recovery.", "error")
        return redirect(url_for("forgot_password"))

    success, message, meta = otp_service.request_password_reset_otp(email)
    if success:
        flash("A new 6-digit verification code has been dispatched to your email.", "success")
    else:
        flash(message, "error")

    return redirect(url_for("verify_otp", email=email))


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    token = request.args.get("token") or request.form.get("token") or session.get("reset_token")
    if not token:
        flash("Invalid or missing password reset token. Please request a new verification code.", "error")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        ok, msg = otp_service.complete_password_reset(token, new_password, confirm_password)
        if not ok:
            flash(msg, "error")
            return render_template("reset_password.html", token=token)

        # Clear temporary recovery session
        session.pop("reset_token", None)
        session.pop("reset_email", None)
        flash("Your password has been reset successfully! Please log in with your new password.", "success")
        return redirect(url_for("login"))

    return render_template("reset_password.html", token=token)


# ---------- google oauth 2.0 / oidc ----------

@app.route("/auth/google")
def google_auth():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if not google_auth_service.is_google_oauth_configured():
        flash("Google OAuth credentials are not configured yet. Please supply GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env.", "error")
        return redirect(url_for("login"))

    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state
    auth_url = google_auth_service.get_google_auth_url(state)
    return redirect(auth_url)


@app.route("/auth/google/callback")
def google_auth_callback():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    # Check for OAuth error returned by Google
    if request.args.get("error"):
        error_desc = request.args.get("error_description") or request.args.get("error")
        flash(f"Google sign-in was cancelled or encountered an error ({error_desc}).", "error")
        return redirect(url_for("login"))

    # State validation (CSRF protection)
    returned_state = request.args.get("state")
    expected_state = session.pop("oauth_state", None)
    if not returned_state or returned_state != expected_state:
        flash("Invalid Google OAuth session state. Please try logging in again.", "error")
        return redirect(url_for("login"))

    code = request.args.get("code")
    if not code:
        flash("Google did not return an authorization code. Please try again.", "error")
        return redirect(url_for("login"))

    # Exchange code for tokens
    token_data, token_err = google_auth_service.exchange_code_for_token(code)
    if token_err:
        flash(token_err, "error")
        return redirect(url_for("login"))

    id_token_jwt = token_data.get("id_token")
    # Verify ID token cryptographically
    id_info, verify_err = google_auth_service.verify_id_token(id_token_jwt)
    if verify_err:
        flash(verify_err, "error")
        return redirect(url_for("login"))

    # Authenticate or register user
    user, is_new, auth_err = google_auth_service.authenticate_or_register_google_user(id_info)
    if auth_err:
        flash(auth_err, "error")
        return redirect(url_for("login"))

    # Establish authenticated session
    session["user_id"] = str(user["_id"])
    session["username"] = user["username"]
    session["is_admin"] = bool(user.get("is_admin", False))

    if is_new:
        flash(f"Welcome to CallSense, {user['username']}! Your account was created with Google.", "success")
    else:
        flash(f"Welcome back, {user['username']}!", "success")

    if session["is_admin"]:
        return redirect(url_for("admin_overview"))
    return redirect(url_for("dashboard"))


# ---------- dashboard ----------

def _compute_stats(calls):
    completed = [c for c in calls if c.get("status") == "completed"]
    stats = {
        "total": len(calls),
        "completed": len(completed),
        "avg_confidence": None,
        "avg_time": None,
        "languages": [],
    }
    if completed:
        confidences = [c["confidence_percent"] for c in completed if c.get("confidence_percent") is not None]
        times = [c["total_time_seconds"] for c in completed if c.get("total_time_seconds") is not None]
        languages = sorted({c["language"] for c in completed if c.get("language")})
        stats["avg_confidence"] = round(sum(confidences) / len(confidences), 1) if confidences else None
        stats["avg_time"] = round(sum(times) / len(times), 1) if times else None
        stats["languages"] = languages
    return stats


@app.route("/dashboard")
@login_required
def dashboard():
    calls_collection = get_calls_collection()
    my_calls = list(
        calls_collection.find({"uploaded_by": session["user_id"]})
        .sort("created_at", -1)
    )
    shared_calls = get_shared_calls_for_user(session["user_id"])

    view = request.args.get("view", "my_calls")
    if view not in {"my_calls", "shared"}:
        view = "my_calls"

    stats = _compute_stats(my_calls)
    return render_template(
        "dashboard.html",
        calls=my_calls,
        shared_calls=shared_calls,
        active_view=view,
        categories=Config.CALL_CATEGORIES,
        stats=stats
    )


@app.route("/shared-with-me")
@login_required
def shared_with_me():
    return redirect(url_for("dashboard", view="shared"))


@app.route("/profile")
@login_required
def profile():
    user = get_user_by_id(session["user_id"])
    if not user:
        flash("Could not load your profile.", "error")
        return redirect(url_for("dashboard"))

    calls_collection = get_calls_collection()
    calls = list(
        calls_collection.find({"uploaded_by": session["user_id"]})
        .sort("created_at", -1)
    )
    stats = _compute_stats(calls)

    category_counts = {}
    for c in calls:
        if c.get("status") == "completed" and c.get("category"):
            category_counts[c["category"]] = category_counts.get(c["category"], 0) + 1

    return render_template(
        "profile.html",
        user=user,
        calls=calls,
        stats=stats,
        category_counts=category_counts,
    )


@app.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    username = request.form.get("username", "")
    email = request.form.get("email", "")

    updated_user, error = update_user_profile(session["user_id"], username, email)
    if error:
        flash(error, "error")
        return redirect(url_for("profile"))

    session["username"] = updated_user["username"]
    flash("Profile updated successfully.", "success")
    return redirect(url_for("profile"))


@app.route("/profile/change-password", methods=["POST"])
@login_required
def update_password():
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_new_password", "")

    if new_password != confirm_password:
        flash("New password and confirmation do not match.", "error")
        return redirect(url_for("profile"))

    ok, error = change_user_password(session["user_id"], current_password, new_password)
    if error:
        flash(error, "error")
    else:
        flash("Password updated successfully.", "success")
    return redirect(url_for("profile"))


@app.route("/upload", methods=["POST"])
@login_required
def upload_call():
    if "audio_file" not in request.files:
        flash("No file selected.", "error")
        return redirect(url_for("dashboard"))

    file = request.files["audio_file"]

    if file.filename == "" or not allowed_file(file.filename):
        flash("Please choose a valid audio file (mp3, wav, m4a, ogg).", "error")
        return redirect(url_for("dashboard"))

    filename = secure_filename(file.filename)
    save_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(save_path)

    calls_collection = get_calls_collection()

    # Insert an "uploaded" placeholder immediately so the UI can show status.
    # The pipeline (services/pipeline.py) will move this through
    # preprocessing_audio -> transcribing -> analyzing -> completed/failed,
    # updating this same document at every stage.
    target_lang = request.form.get("language", "auto")
    if target_lang not in {"auto", "hi", "gu", "en"}:
        target_lang = "auto"

    call_doc = {
        "filename": filename,
        "uploaded_by": session["user_id"],
        "uploaded_by_username": session.get("username"),
        "status": "uploaded",
        "target_language": target_lang,
        "transcript": None,
        "transcript_gujarati": None,
        "transcript_hindi": None,
        "transcript_english": None,
        "summary": None,
        "motive": None,
        "category": None,
        "language": None,
        "sentiment": None,
        "priority": None,
        "resolution_status": None,
        "customer_name": None,
        "agent_name": None,
        "key_issues": [],
        "action_items": [],
        "follow_up_required": False,
        "phone_numbers_mentioned": [],
        "confidence_percent": None,
        "confidence_breakdown": None,
        "audio_duration_seconds": None,
        "transcription_time_seconds": None,
        "llm_time_seconds": None,
        "total_time_seconds": None,
        "created_at": datetime.now(timezone.utc),
    }
    inserted = calls_collection.insert_one(call_doc)

    success, error = run_pipeline(
        calls_collection,
        inserted.inserted_id,
        save_path,
        filename,
        target_language=target_lang
    )

    if success:
        flash(f"'{filename}' processed successfully!", "success")
    else:
        flash(f"Processing failed: {error}", "error")

    return redirect(url_for("dashboard"))


@app.route("/call/<call_id>/delete", methods=["POST"])
@login_required
def delete_call(call_id):
    from bson import ObjectId
    calls_collection = get_calls_collection()
    calls_collection.delete_one({"_id": ObjectId(call_id), "uploaded_by": session["user_id"]})
    flash("Call record deleted successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/call/<call_id>/reprocess", methods=["POST"])
@login_required
def reprocess_call(call_id):
    from bson import ObjectId
    calls_collection = get_calls_collection()
    call = calls_collection.find_one({"_id": ObjectId(call_id)})
    if not call:
        flash("Call record not found.", "error")
        return redirect(url_for("dashboard"))

    user = get_user_by_id(session["user_id"])
    is_admin = user and user.get("role") == "admin"
    if str(call.get("uploaded_by")) != str(session["user_id"]) and not is_admin:
        flash("You do not have permission to reprocess this call.", "error")
        return redirect(url_for("dashboard"))

    file_path = os.path.join(Config.UPLOAD_FOLDER, call["filename"])
    if not os.path.exists(file_path):
        flash("Audio file was not found on the server.", "error")
        return redirect(url_for("dashboard"))

    target_lang = request.form.get("language") or call.get("target_language") or "auto"
    success, error = run_pipeline(
        calls_collection,
        call["_id"],
        file_path,
        call["filename"],
        target_language=target_lang,
    )
    if success:
        flash(f"'{call['filename']}' reprocessed successfully with updated pipeline!", "success")
    else:
        flash(f"Reprocessing failed: {error}", "error")
    return redirect(url_for("dashboard"))


# ---------- sharing & audio ----------

@app.route("/api/users/shareable")
@login_required
def api_shareable_users():
    search_q = request.args.get("q", "").strip()
    users_list = get_shareable_users(session["user_id"], search_q)
    return jsonify({"success": True, "users": users_list})


@app.route("/call/<call_id>/share", methods=["POST"])
@login_required
def share_call_route(call_id):
    if request.is_json:
        data = request.get_json() or {}
        recipient_id = data.get("recipient_id", "").strip()
        customer_name = data.get("customer_name", "").strip()
        country_code = data.get("country_code", "+91").strip()
        customer_number = data.get("customer_number", "").strip() or data.get("customer_phone", "").strip()
    else:
        recipient_id = request.form.get("recipient_id", "").strip()
        customer_name = request.form.get("customer_name", "").strip()
        country_code = request.form.get("country_code", "+91").strip()
        customer_number = request.form.get("customer_number", "").strip() or request.form.get("customer_phone", "").strip()

    if not customer_name:
        err = "Customer Name is compulsory. Please enter customer name."
        if request.is_json:
            return jsonify({"success": False, "error": err}), 400
        flash(err, "error")
        return redirect(url_for("dashboard"))

    clean_digits = "".join(filter(str.isdigit, customer_number))
    if not customer_number or len(clean_digits) < 7:
        err = "Customer Phone / Mobile number is compulsory (minimum 7 digits)."
        if request.is_json:
            return jsonify({"success": False, "error": err}), 400
        flash(err, "error")
        return redirect(url_for("dashboard"))

    if not recipient_id:
        err = "Please select a registered user to receive this call."
        if request.is_json:
            return jsonify({"success": False, "error": err}), 400
        flash(err, "error")
        return redirect(url_for("dashboard"))

    success, message = share_call(
        call_id=call_id,
        recipient_id=recipient_id or None,
        sender_id=session["user_id"],
        sender_username=session.get("username", "Unknown"),
        customer_name=customer_name or None,
        country_code=country_code,
        customer_number=customer_number or None,
        customer_phone=customer_number or None
    )

    if request.is_json:
        if success:
            return jsonify({"success": True, "message": message})
        return jsonify({"success": False, "error": message}), 400

    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    return redirect(url_for("dashboard"))


@app.route("/call/<call_id>/unshare", methods=["POST"])
@login_required
def unshare_call_route(call_id):
    if request.is_json:
        data = request.get_json() or {}
        recipient_id = data.get("recipient_id")
        customer_number = data.get("customer_number")
    else:
        recipient_id = request.form.get("recipient_id")
        customer_number = request.form.get("customer_number")

    # If neither target was provided, default to current user (self-dismissal from Shared With Me)
    if not recipient_id and not customer_number:
        recipient_id = session.get("user_id")

    success, message = unshare_call(
        call_id=call_id,
        recipient_id=recipient_id,
        requester_id=session["user_id"],
        customer_number=customer_number
    )

    if request.is_json:
        if success:
            return jsonify({"success": True, "message": message})
        return jsonify({"success": False, "error": message}), 400

    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    return redirect(request.referrer or url_for("dashboard"))


@app.route("/audio/<filename>")
@login_required
def serve_audio(filename):
    safe_name = secure_filename(filename)
    calls_col = get_calls_collection()
    call = calls_col.find_one({"filename": safe_name})
    if call and not is_call_accessible(call, session["user_id"], session.get("is_admin", False)):
        flash("You do not have permission to access this audio file.", "error")
        return redirect(url_for("dashboard"))
    return send_from_directory(Config.UPLOAD_FOLDER, safe_name)


@app.route("/project-guide.pdf")
def download_project_guide():
    pdf_path = os.path.join(os.path.dirname(__file__), "CallSense_Project_Guide.pdf")
    if not os.path.exists(pdf_path):
        from scripts.generate_project_pdf import create_project_pdf
        create_project_pdf(pdf_path)
    return send_file(pdf_path, as_attachment=False, mimetype="application/pdf")


# ---------- admin panel ----------
# What the admin side handles:
#   1. Overview  - system-wide numbers (all users, all calls combined):
#      total users/calls, completed vs failed vs in-progress, overall
#      confidence, category/sentiment/priority/language distribution, and
#      the aggregated "why confidence isn't 100%" reasons across every call
#      (so an admin can spot systemic issues, e.g. most calls losing
#      confidence to background noise - not just one call at a time).
#   2. Users     - see every registered user with their call count,
#      promote/demote admin access, delete a user (cascades to their calls).
#   3. Calls     - browse/filter every call uploaded by anyone (not just
#      your own), inspect it, and delete any call record.
# Only accounts with is_admin=True (see Config.ADMIN_EMAILS in .env, or
# promoted by another admin from the Users tab) can reach any /admin/* route.

@app.route("/admin")
@admin_required
def admin_overview():
    calls_collection = get_calls_collection()
    users_collection = get_users_collection()
    stats = admin_service.get_global_stats(calls_collection, users_collection)
    return render_template("admin_overview.html", stats=stats, active_tab="overview")


@app.route("/admin/users")
@admin_required
def admin_users():
    calls_collection = get_calls_collection()
    users_collection = get_users_collection()
    users = admin_service.list_users(users_collection, calls_collection)
    return render_template("admin_users.html", users=users, active_tab="users")


@app.route("/admin/users/<user_id>/toggle-admin", methods=["POST"])
@admin_required
def admin_toggle_user_admin(user_id):
    users_collection = get_users_collection()
    make_admin = request.form.get("make_admin") == "1"
    ok, error = admin_service.set_admin_status(users_collection, user_id, make_admin, session["user_id"])
    if error:
        flash(error, "error")
    else:
        flash("Admin access updated.", "success")
    return redirect(url_for("admin_users"))


@app.route("/admin/users/<user_id>/delete", methods=["POST"])
@admin_required
def admin_delete_user(user_id):
    users_collection = get_users_collection()
    calls_collection = get_calls_collection()
    ok, error = admin_service.delete_user_cascade(users_collection, calls_collection, user_id, session["user_id"])
    if error:
        flash(error, "error")
    else:
        flash("User and their calls were deleted.", "success")
    return redirect(url_for("admin_users"))


@app.route("/admin/calls")
@admin_required
def admin_calls():
    calls_collection = get_calls_collection()
    status = request.args.get("status") or None
    category = request.args.get("category") or None
    calls = admin_service.list_all_calls(calls_collection, status=status, category=category)
    return render_template(
        "admin_calls.html",
        calls=calls,
        categories=Config.CALL_CATEGORIES,
        selected_status=status,
        selected_category=category,
        active_tab="calls",
    )


@app.route("/admin/calls/<call_id>/delete", methods=["POST"])
@admin_required
def admin_delete_call(call_id):
    calls_collection = get_calls_collection()
    if admin_service.delete_any_call(calls_collection, call_id):
        flash("Call record deleted.", "success")
    else:
        flash("Could not find that call.", "error")
    return redirect(url_for("admin_calls"))


# ---------- export routes (Excel .xlsx & PDF) ----------

@app.route("/calls/export/excel")
@login_required
def export_calls_excel():
    """
    Exports calls to a true Microsoft Excel (.xlsx) file using openpyxl.
    Exports the user's uploaded calls and any calls shared with them.
    If an admin requests ?view=system_all, exports all calls in the system.
    """
    import re
    calls_col = get_calls_collection()
    user_id = str(session["user_id"])
    user = get_user_by_id(user_id)
    is_admin = bool(user and user.get("role") == "admin")

    view_filter = request.args.get("view", "all")
    export_calls = []

    if is_admin and view_filter == "system_all":
        raw_calls = list(calls_col.find().sort("created_at", -1))
        for c in raw_calls:
            c["export_access_type"] = "System Record"
            export_calls.append(c)
    else:
        # User's uploaded calls
        my_calls = list(calls_col.find({"uploaded_by": user_id}).sort("created_at", -1))
        for c in my_calls:
            c["export_access_type"] = "My Call"
            export_calls.append(c)

        # Calls shared with the user
        shared_calls = get_shared_calls_for_user(user_id)
        for c in shared_calls:
            sender_name = c.get("shared_info", {}).get("shared_by_username") or "Team Member"
            c["export_access_type"] = f"Shared by {sender_name}"
            export_calls.append(c)

    username = session.get("username") or (user.get("username") if user else "User")
    excel_buffer = generate_calls_excel(export_calls, requester_username=username)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    filename = f"CallSense_Analytics_Report_{timestamp}.xlsx"

    return Response(
        excel_buffer.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.route("/call/<call_id>/export/pdf")
@login_required
def export_call_pdf(call_id):
    """
    Secure PDF export for a single call record.
    Fixes addressed:
    1. Security bug: Validates call access (must be owner, admin, or shared recipient).
    2. Missing 404 handling: Safely validates ObjectId; if call is None, returns 404 cleanly.
    3. Privacy mismatch:
       - Owner / Admin: Full Executive Report with complete transcripts (Original, Gujarati, Hindi, English).
       - Shared Recipient: Analytics Summary Report (Category, Motive, Summary, Action items) with
         transcripts and phone numbers redacted in accordance with sharing privacy rules.
    """
    import re
    from bson import ObjectId
    from bson.errors import InvalidId

    # 1. 404 handling for invalid call_id format
    try:
        call_oid = ObjectId(call_id)
    except (InvalidId, TypeError, Exception):
        flash("Invalid call ID specified.", "error")
        return redirect(url_for("dashboard"))

    # 2. 404 handling for missing record
    calls_col = get_calls_collection()
    call = calls_col.find_one({"_id": call_oid})
    if not call:
        flash("Call record was not found.", "error")
        return redirect(url_for("dashboard"))

    # 3. Security & Ownership check
    user_id = str(session["user_id"])
    user = get_user_by_id(user_id)
    is_admin = bool(user and user.get("role") == "admin")
    is_owner = (str(call.get("uploaded_by")) == user_id)
    is_shared = any(str(s.get("user_id")) == user_id for s in call.get("shared_with", []))

    if not (is_owner or is_admin or is_shared):
        flash("Access denied: You do not have permission to export this call report.", "error")
        return redirect(url_for("dashboard"))

    # 4. Generate PDF with role-based privacy protection
    try:
        pdf_buffer = generate_single_call_pdf(call, requester_id=user_id, is_admin=is_admin)
    except Exception as e:
        flash(f"Failed to generate PDF report: {str(e)}", "error")
        return redirect(url_for("dashboard"))

    clean_name = re.sub(r"[^\w\-_\.]", "_", call.get("filename", "call_report")).rsplit(".", 1)[0]
    report_tag = "full_report" if (is_owner or is_admin) else "summary_report"
    pdf_filename = f"{clean_name}_{report_tag}.pdf"

    return Response(
        pdf_buffer.getvalue(),
        mimetype="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{pdf_filename}"'}
    )


if __name__ == "__main__":
    # threaded=True is the actual fix for "have to refresh the page before
    # Profile/Logout work": Flask's dev server is single-threaded by
    # default, so while an upload is being transcribed + analyzed (which
    # can take several seconds), that ONE request blocks the entire
    # server. Any other click (Profile, Logout, even another tab) just
    # sits there waiting in line until the upload's request finishes -
    # which looks exactly like "nothing happens until I refresh".
    # threaded=True lets the dev server handle each request on its own
    # thread instead of one at a time.
    app.run(debug=Config.DEBUG, port=5000, threaded=True)
