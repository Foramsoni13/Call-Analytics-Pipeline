"""
Email service module for CallSense.
Handles secure delivery of transactional emails (OTP, password reset confirmation,
welcome emails, call sharing notifications) using Gmail SMTP with TLS.
"""
import os
import smtplib
import logging
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from jinja2 import Environment, FileSystemLoader, select_autoescape
from config import Config

logger = logging.getLogger(__name__)

# Set up standalone Jinja2 environment pointing to templates/emails
_template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "emails")
_jinja_env = Environment(
    loader=FileSystemLoader(_template_dir),
    autoescape=select_autoescape(["html", "xml"])
)


def _render_email_template(template_name: str, context: dict) -> str:
    """Renders an email template from the templates/emails directory."""
    try:
        tmpl = _jinja_env.get_template(template_name)
        return tmpl.render(**context)
    except Exception as e:
        logger.error(f"[EmailService] Failed to render template {template_name}: {e}")
        return ""


def _get_smtp_config() -> dict:
    """Dynamically reloads and retrieves SMTP credentials from environment."""
    from dotenv import load_dotenv
    load_dotenv(override=True)
    raw_pw = os.getenv("MAIL_PASSWORD", Config.MAIL_PASSWORD or "")
    # Clean app password: remove spaces and outer quotes if user copied 'xxxx yyyy zzzz wwww'
    cleaned_pw = raw_pw.strip().replace(" ", "").replace('"', '').replace("'", "")
    
    server = os.getenv("MAIL_SERVER", Config.MAIL_SERVER or "smtp.gmail.com").strip()
    port = int(os.getenv("MAIL_PORT", Config.MAIL_PORT or 587))
    username = os.getenv("MAIL_USERNAME", Config.MAIL_USERNAME or "foramsoni2004@gmail.com").strip()
    sender = os.getenv("MAIL_DEFAULT_SENDER", Config.MAIL_DEFAULT_SENDER or username).strip()
    use_tls = os.getenv("MAIL_USE_TLS", str(Config.MAIL_USE_TLS)).lower() == "true"
    use_ssl = os.getenv("MAIL_USE_SSL", str(Config.MAIL_USE_SSL)).lower() == "true"

    return {
        "password": cleaned_pw,
        "server": server,
        "port": port,
        "username": username,
        "sender": sender,
        "use_tls": use_tls,
        "use_ssl": use_ssl,
    }


def send_email(to_email: str, subject: str, html_content: str, text_content: str = None) -> tuple[bool, str | None]:
    """
    Sends an email using the configured SMTP server (Gmail SMTP).
    Returns (True, None) on success, or (False, error_message) on failure.
    Never raises an unhandled exception to prevent crashing callers.
    """
    if not to_email or "@" not in to_email:
        return False, "Invalid recipient email address."

    cfg = _get_smtp_config()
    mail_password = cfg["password"]
    if not mail_password or mail_password == "YOUR_GMAIL_APP_PASSWORD":
        msg = "Gmail App Password is not configured in .env (MAIL_PASSWORD is empty or placeholder)."
        logger.warning(f"[EmailService] {msg}")
        return False, msg

    mail_server = cfg["server"]
    mail_port = cfg["port"]
    sender_email = cfg["sender"]
    mail_username = cfg["username"]

    # Construct the multipart alternative email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = formataddr(("CallSense", sender_email))
    msg["To"] = to_email

    # Plain text fallback
    if not text_content:
        # Strip simple tags for fallback if no explicit text provided
        import re
        text_content = re.sub(r"<[^>]+>", " ", html_content)
        text_content = re.sub(r"\s+", " ", text_content).strip()

    part1 = MIMEText(text_content, "plain", "utf-8")
    part2 = MIMEText(html_content, "html", "utf-8")
    msg.attach(part1)
    msg.attach(part2)

    server = None
    try:
        if cfg["use_ssl"]:
            server = smtplib.SMTP_SSL(mail_server, mail_port, timeout=12)
        else:
            server = smtplib.SMTP(mail_server, mail_port, timeout=12)
            if cfg["use_tls"]:
                server.starttls()

        if mail_username and mail_password:
            server.login(mail_username, mail_password)

        server.sendmail(sender_email, [to_email], msg.as_string())
        logger.info(f"[EmailService] Successfully sent '{subject}' to {to_email}")
        return True, None

    except smtplib.SMTPAuthenticationError as e:
        err_msg = f"SMTP authentication failed. Check your Gmail address and 16-character App Password. Details: {e}"
        logger.error(f"[EmailService] {err_msg}")
        return False, err_msg
    except Exception as e:
        err_msg = f"Failed to send email to {to_email}: {str(e)}"
        logger.error(f"[EmailService] {err_msg}")
        return False, err_msg
    finally:
        if server is not None:
            try:
                server.quit()
            except Exception:
                pass


def send_otp_email(to_email: str, otp_code: str, minutes_valid: int = 5) -> tuple[bool, str | None]:
    """Sends a password-reset 6-digit OTP code to the recipient."""
    subject = f"{otp_code} is your CallSense verification code"
    context = {
        "otp_code": otp_code,
        "minutes_valid": minutes_valid,
        "current_year": datetime.now(timezone.utc).year,
    }
    html = _render_email_template("otp_email.html", context)
    text = (
        f"CallSense Password Reset Verification\n\n"
        f"Your one-time verification code is: {otp_code}\n"
        f"This code will expire in {minutes_valid} minutes.\n\n"
        f"If you did not request this code, please ignore this email.\n"
        f"CallSense representatives will never ask for your verification code."
    )
    return send_email(to_email, subject, html, text)


def send_password_reset_confirmation_email(to_email: str, username: str = None) -> tuple[bool, str | None]:
    """Sends a security confirmation after the user successfully resets their password."""
    subject = "CallSense Password Reset Confirmation"
    now_str = datetime.now(timezone.utc).strftime("%B %d, %Y at %I:%M %p UTC")
    login_url = f"{Config.APP_BASE_URL.rstrip('/')}/login"
    context = {
        "username": username or to_email,
        "reset_time": now_str,
        "login_url": login_url,
        "current_year": datetime.now(timezone.utc).year,
    }
    html = _render_email_template("password_reset_confirmed.html", context)
    text = (
        f"CallSense Password Reset Confirmation\n\n"
        f"Hello {username or to_email},\n\n"
        f"The password for your CallSense account was successfully changed on {now_str}.\n"
        f"You can log in now at: {login_url}\n\n"
        f"If you did not make this change, please contact support immediately."
    )
    return send_email(to_email, subject, html, text)


def send_welcome_email(to_email: str, username: str = None, is_google: bool = False) -> tuple[bool, str | None]:
    """Sends a welcome email to newly registered users."""
    subject = "Welcome to CallSense!"
    dashboard_url = f"{Config.APP_BASE_URL.rstrip('/')}/dashboard"
    context = {
        "username": username or to_email.split("@")[0],
        "user_email": to_email,
        "is_google": is_google,
        "dashboard_url": dashboard_url,
        "current_year": datetime.now(timezone.utc).year,
    }
    html = _render_email_template("welcome_email.html", context)
    text = (
        f"Welcome to CallSense, {username or to_email}!\n\n"
        f"Thank you for registering. You are now ready to unlock AI-powered speech analytics, "
        f"transcription, and insights from every call.\n\n"
        f"Access your dashboard: {dashboard_url}\n"
    )
    return send_email(to_email, subject, html, text)


def send_call_shared_email(
    to_email: str,
    recipient_name: str,
    sender_username: str,
    call_title: str,
    call_url: str = None,
    call_category: str = None,
    call_language: str = None,
    call_duration: int | float = None,
    share_date: str = None,
) -> tuple[bool, str | None]:
    """
    Sends an email notification when a call record is shared with an existing user.
    Protects privacy by never including call transcripts or customer phone numbers.
    """
    subject = f"{sender_username} shared a call with you on CallSense"
    if not share_date:
        share_date = datetime.now(timezone.utc).strftime("%B %d, %Y")
    if not call_url:
        call_url = f"{Config.APP_BASE_URL.rstrip('/')}/dashboard?view=shared"

    context = {
        "recipient_name": recipient_name or to_email.split("@")[0],
        "sender_username": sender_username or "A team member",
        "call_title": call_title or "Call recording",
        "call_url": call_url,
        "call_category": call_category,
        "call_language": call_language,
        "call_duration": round(call_duration, 1) if call_duration else None,
        "share_date": share_date,
        "current_year": datetime.now(timezone.utc).year,
    }
    html = _render_email_template("call_shared_email.html", context)
    text = (
        f"Call Shared on CallSense\n\n"
        f"Hello {recipient_name},\n\n"
        f"{sender_username} shared a call recording ('{call_title}') with you on {share_date}.\n"
        f"View the call analytics securely on CallSense: {call_url}\n\n"
        f"For privacy compliance, call audio and transcripts can only be accessed while logged into CallSense."
    )
    return send_email(to_email, subject, html, text)
