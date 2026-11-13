"""
Script to generate CallSense_Auth_SMTP_MongoDB_Guide.pdf
Comprehensive technical guide covering:
1. Application Architecture (Layered MVC / Service-Oriented Architecture & Pipeline Lifecycle)
2. Classes, Data Models & Document Schemas (Config, NumberedCanvas, User, Call, PasswordReset, ShareEntry)
3. User Authentication Flow (Registration, Password Hashing, Login, Sessions, Admin Roles)
4. Gmail SMTP Integration (Port 587, TLS, App Passwords, Reusable Service, Templates)
5. MongoDB Database Connectivity (Singleton Connection, Collections, Queries, Indexing)
6. macOS Command Cheatsheet & Troubleshooting
"""
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8.5)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running header on pages > 1
        if self._pageNumber > 1:
            self.drawString(40, 755, "CallSense — Application Architecture, Classes, Auth, SMTP & MongoDB Guide")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, 747, 572, 747)

        # Running footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 25, page_str)
        self.drawString(40, 25, "CallSense Technical Documentation — Complete System Reference")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 36, 572, 36)
        self.restoreState()


def build_pdf(output_path="CallSense_Auth_SMTP_MongoDB_Guide.pdf"):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=21,
        leading=25,
        textColor=colors.HexColor("#0369A1"),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'SecH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13.5,
        leading=17,
        textColor=colors.HexColor("#0284C7"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SecH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=9,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'SecBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'SecBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=13,
        textColor=colors.HexColor("#334155"),
        leftIndent=14,
        spaceAfter=2.5
    )

    code_style = ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=3,
        spaceAfter=5
    )

    story = []

    # Title Banner
    story.append(Paragraph("CallSense — Complete Technical Architecture & Guide", title_style))
    story.append(Paragraph("<b>Application Architecture, Python Classes, Auth Pipeline, Gmail SMTP & MongoDB Database</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284C7"), spaceBefore=0, spaceAfter=10))

    # =========================================================================
    # SECTION 1: APPLICATION ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("1. High-Level Application Architecture", h1_style))
    story.append(Paragraph(
        "CallSense is built upon a <b>Service-Oriented Model-View-Controller (MVC)</b> architectural pattern. "
        "The web layer handles HTTP routing, request validation, and session management, while business logic "
        "is strictly decoupled into standalone, testable services under <code>services/</code>.",
        body_style
    ))

    arch_layers_data = [
        [Paragraph("<b>Architectural Layer</b>", body_style), Paragraph("<b>Key Modules / Technologies</b>", body_style), Paragraph("<b>Responsibilities & Flow</b>", body_style)],
        [
            Paragraph("<b>Presentation & Routing</b>", body_style),
            Paragraph("<code>app.py</code><br/>Flask 3.0.3, Jinja2, Vanilla CSS", code_style),
            Paragraph("HTTP request dispatching, session cookies, route authorization guards (<code>@login_required</code>, <code>@admin_required</code>), flash notifications, and template rendering.", body_style)
        ],
        [
            Paragraph("<b>Business Logic & Services</b>", body_style),
            Paragraph("<code>services/audio_processing.py</code><br/><code>services/transcription_service.py</code><br/><code>services/llm_service.py</code><br/><code>services/pipeline.py</code><br/><code>services/auth_service.py</code><br/><code>services/otp_service.py</code><br/><code>services/email_service.py</code><br/><code>services/share_service.py</code><br/><code>services/admin_service.py</code>", code_style),
            Paragraph("Decoupled service modules handling audio denoising, Whisper speech-to-text, LLaMA JSON insights extraction, OTP generation, SMTP notifications, and call sharing.", body_style)
        ],
        [
            Paragraph("<b>Data Persistence Layer</b>", body_style),
            Paragraph("<code>services/db.py</code><br/>MongoDB Community 8.x, PyMongo", code_style),
            Paragraph("Singleton connection pool managing documents across <code>users</code>, <code>calls</code>, and <code>password_resets</code> collections.", body_style)
        ],
        [
            Paragraph("<b>External Services & APIs</b>", body_style),
            Paragraph("Groq Cloud (Whisper Large V3, LLaMA)<br/>Google SMTP (Port 587, TLS)<br/>Google Cloud OAuth 2.0", code_style),
            Paragraph("Cloud AI inference for audio transcription and analytics, transactional email relay via Gmail, and OpenID Connect identity federation.", body_style)
        ],
    ]
    t_arch = Table(arch_layers_data, colWidths=[120, 150, 262])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_arch)

    story.append(Spacer(1, 4))
    story.append(Paragraph("End-to-End Call Analytics Pipeline Lifecycle:", h2_style))
    story.append(Paragraph("&bull; <b>Stage 1 (Upload):</b> Audio file received at <code>/upload</code>, sanitized with <code>secure_filename()</code>, saved to <code>uploads/</code>, and a tracking document initialized in MongoDB with status <code>'uploaded'</code>.", bullet_style))
    story.append(Paragraph("&bull; <b>Stage 2 (Preprocessing):</b> <code>audio_processing.py</code> converts audio to standard WAV (16kHz mono), reduces ambient background noise using <code>noisereduce</code>, trims silences, and normalizes decibels.", bullet_style))
    story.append(Paragraph("&bull; <b>Stage 3 (Transcription):</b> <code>transcription_service.py</code> streams the cleaned audio to Groq Whisper Large V3. Detects language (English, Hindi, Gujarati), computes confidence scores, and applies speaker diarization heuristics.", bullet_style))
    story.append(Paragraph("&bull; <b>Stage 4 (LLM Intelligence):</b> <code>llm_service.py</code> prompts Groq LLaMA models for structured JSON: customer sentiment, issue category, urgency priority, resolution status, agent/customer names, key bullet points, and action items.", bullet_style))
    story.append(Paragraph("&bull; <b>Stage 5 (Completion):</b> All extracted metadata and confidence metrics are atomically saved to MongoDB, and status transitions to <code>'completed'</code>.", bullet_style))

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 2: PYTHON CLASSES & DATA SCHEMAS
    # =========================================================================
    story.append(Paragraph("2. Python Classes and Data Models", h1_style))
    story.append(Paragraph(
        "CallSense uses Python object-oriented patterns for configuration and PDF rendering, and structured BSON "
        "document models in MongoDB.",
        body_style
    ))

    story.append(Paragraph("A. Python Classes Defined in Codebase", h2_style))
    
    classes_data = [
        [Paragraph("<b>Class Name</b>", body_style), Paragraph("<b>File Location</b>", body_style), Paragraph("<b>Properties & Methods</b>", body_style)],
        [
            Paragraph("<code>Config</code>", code_style),
            Paragraph("<code>config.py</code>", code_style),
            Paragraph("Encapsulates all environment settings.<br/>"
                      "<b>Key Attributes:</b> <code>SECRET_KEY</code>, <code>MONGO_URI</code>, <code>MONGO_DB_NAME</code>, <code>GROQ_API_KEY</code>, <code>ADMIN_EMAILS</code>, <code>MAIL_SERVER</code>, <code>MAIL_PORT</code>, <code>MAIL_PASSWORD</code>, <code>OTP_EXPIRATION_SECONDS</code>.<br/>"
                      "<b>Class Method:</b> <code>is_admin_email(email)</code> &rarr; Dynamic reload checking if email has admin rights.", body_style)
        ],
        [
            Paragraph("<code>NumberedCanvas</code>", code_style),
            Paragraph("<code>scripts/generate_project_pdf.py</code><br/><code>scripts/generate_auth_smtp_mongodb_pdf.py</code>", code_style),
            Paragraph("Inherits from ReportLab's <code>canvas.Canvas</code>.<br/>"
                      "Implements two-pass page rendering to calculate total dynamic page count (<code>showPage()</code> and <code>save()</code>) and paints running headers, footers, and rule lines.", body_style)
        ],
    ]
    t_classes = Table(classes_data, colWidths=[110, 140, 282])
    t_classes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_classes)

    story.append(Spacer(1, 4))
    story.append(Paragraph("B. Database Document Schemas (BSON Models)", h2_style))

    schemas_data = [
        [Paragraph("<b>Document Schema</b>", body_style), Paragraph("<b>MongoDB Collection</b>", body_style), Paragraph("<b>Schema Attributes & Data Types</b>", body_style)],
        [
            Paragraph("<b>UserDocument</b>", body_style),
            Paragraph("<code>users</code>", code_style),
            Paragraph("<code>_id</code> (ObjectId), <code>username</code> (string, unique), <code>email</code> (string, unique, lowercase), <code>password_hash</code> (string, Werkzeug hash), <code>google_id</code> (string or None), <code>auth_provider</code> (string), <code>is_admin</code> (boolean), <code>created_at</code> (UTC datetime).", body_style)
        ],
        [
            Paragraph("<b>CallDocument</b>", body_style),
            Paragraph("<code>calls</code>", code_style),
            Paragraph("<code>_id</code> (ObjectId), <code>filename</code> (string), <code>uploaded_by</code> (string user ID), <code>uploaded_by_username</code> (string), <code>status</code> (uploaded | preprocessing_audio | transcribing | analyzing | completed | failed), <code>transcript</code> (string), <code>summary</code> (string), <code>motive</code> (string), <code>category</code> (string), <code>sentiment</code> (Positive | Neutral | Negative), <code>priority</code> (Low | Medium | High | Urgent), <code>confidence_percent</code> (float), <code>confidence_breakdown</code> (dict), <code>audio_duration_seconds</code> (float), <code>shared_with</code> (list of ShareEntry), <code>created_at</code> (UTC datetime).", body_style)
        ],
        [
            Paragraph("<b>PasswordReset</b>", body_style),
            Paragraph("<code>password_resets</code>", code_style),
            Paragraph("<code>_id</code> (ObjectId), <code>email</code> (string), <code>user_id</code> (string), <code>otp_hash</code> (string, hashed 6-digit code), <code>created_at</code> (datetime), <code>expires_at</code> (datetime, 5-min TTL), <code>attempts</code> (int, max 5), <code>verified</code> (bool), <code>reset_token</code> (string, single-use 32-byte URL-safe token), <code>used</code> (bool).", body_style)
        ],
        [
            Paragraph("<b>ShareEntry (Embedded)</b>", body_style),
            Paragraph("Subdocument in <code>calls.shared_with</code>", code_style),
            Paragraph("<code>user_id</code> (string recipient ID), <code>username</code> (string), <code>customer_name</code> (string), <code>email</code> (string), <code>shared_by</code> (string sender ID), <code>shared_by_username</code> (string), <code>shared_at</code> (UTC datetime).", body_style)
        ],
    ]
    t_schemas = Table(schemas_data, colWidths=[110, 130, 292])
    t_schemas.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_schemas)

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 3: AUTHENTICATION FLOW
    # =========================================================================
    story.append(Paragraph("3. How User Registration and Login Work", h1_style))
    story.append(Paragraph(
        "CallSense enforces strict authentication validation, preventing unauthorized access to audio files and analytics.",
        body_style
    ))

    story.append(Paragraph("Registration Flow:", h2_style))
    story.append(Paragraph("&bull; User fills in Username, Email, Password, and Confirm Password at <code>/register</code>.", bullet_style))
    story.append(Paragraph("&bull; <code>validate_registration()</code> verifies regex matching and character length.", bullet_style))
    story.append(Paragraph("&bull; System verifies neither username nor email exists in MongoDB.", bullet_style))
    story.append(Paragraph("&bull; Password is hashed using <code>generate_password_hash(password)</code> (never stored plaintext).", bullet_style))
    story.append(Paragraph("&bull; System evaluates <code>Config.is_admin_email(email)</code> &rarr; Sets <code>is_admin</code> accordingly.", bullet_style))
    story.append(Paragraph("&bull; Dispatches a branded welcome email to the user's inbox via <code>email_service.send_welcome_email()</code>.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Login Flow:", h2_style))
    story.append(Paragraph("&bull; User submits username/email and password at <code>/login</code>.", bullet_style))
    story.append(Paragraph("&bull; Queries MongoDB: <code>users.find_one({'$or': [{'username': id}, {'email': id.lower()}]})</code>.", bullet_style))
    story.append(Paragraph("&bull; Compares candidate password against the stored salt & hash using <code>check_password_hash()</code>.", bullet_style))
    story.append(Paragraph("&bull; Encrypts session cookies with <code>session['user_id']</code>, <code>session['username']</code>, <code>session['is_admin']</code>.", bullet_style))
    story.append(Paragraph("&bull; Role-based redirect: Admins redirect to <code>/admin</code>; standard users redirect to <code>/dashboard</code>.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Forgot Password & OTP Flow:", h2_style))
    story.append(Paragraph("&bull; User clicks 'Forgot Password?' on login page &rarr; Enters email at <code>/forgot-password</code>.", bullet_style))
    story.append(Paragraph("&bull; <b>Anti-Enumeration:</b> Generic confirmation shown even if email does not exist.", bullet_style))
    story.append(Paragraph("&bull; Generates 6-digit cryptographic OTP (<code>secrets.randbelow(900000) + 100000</code>).", bullet_style))
    story.append(Paragraph("&bull; Sends OTP via Gmail SMTP with 5-minute expiry and 60-second resend cooldown.", bullet_style))
    story.append(Paragraph("&bull; User verifies 6 digits at <code>/verify-otp</code> &rarr; Sets new password at <code>/reset-password</code>.", bullet_style))

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 4: GMAIL SMTP
    # =========================================================================
    story.append(Paragraph("4. How Gmail SMTP Works & How It Connects", h1_style))
    story.append(Paragraph(
        "CallSense connects to Google's official SMTP server (<code>smtp.gmail.com</code>) on <b>Port 587</b> using <b>TLS (STARTTLS)</b>. "
        "Python's standard library modules <code>smtplib</code> and <code>email.mime</code> are utilized directly, ensuring rock-solid stability.",
        body_style
    ))

    story.append(Paragraph("A. Connection Workflow in CallSense", h2_style))
    story.append(Paragraph("1. <code>email_service.send_email()</code> calls <code>_get_smtp_config()</code> which reloads <code>.env</code> dynamically using <code>load_dotenv(override=True)</code>.", bullet_style))
    story.append(Paragraph("2. Automatically strips spaces and quotes from <code>MAIL_PASSWORD</code> (handles <code>abcd efgh ijkl mnop</code> seamlessly).", bullet_style))
    story.append(Paragraph("3. Opens TCP socket connection: <code>server = smtplib.SMTP('smtp.gmail.com', 587, timeout=12)</code>.", bullet_style))
    story.append(Paragraph("4. Upgrades socket to encrypted TLS tunnel: <code>server.starttls()</code>.", bullet_style))
    story.append(Paragraph("5. Authenticates: <code>server.login('foramsoni2004@gmail.com', password)</code>.", bullet_style))
    story.append(Paragraph("6. Transmits multipart MIME message containing responsive HTML and plain-text fallback.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("B. Required Environment Variables (in <code>.env</code>)", h2_style))
    env_code = (
        "MAIL_SERVER=smtp.gmail.com\n"
        "MAIL_PORT=587\n"
        "MAIL_USE_TLS=True\n"
        "MAIL_USE_SSL=False\n"
        "MAIL_USERNAME=foramsoni2004@gmail.com\n"
        "MAIL_PASSWORD=your_16_character_app_password\n"
        "MAIL_DEFAULT_SENDER=foramsoni2004@gmail.com\n"
        "APP_BASE_URL=http://127.0.0.1:5000"
    )
    t_env = Table([[Paragraph(f"<pre>{env_code}</pre>", code_style)]], colWidths=[532])
    t_env.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_env)

    story.append(Spacer(1, 4))
    story.append(Paragraph("C. Email Templates in CallSense", h2_style))
    smtp_data = [
        [Paragraph("<b>Template</b>", body_style), Paragraph("<b>Trigger Event</b>", body_style), Paragraph("<b>Content Delivered</b>", body_style)],
        [Paragraph("<code>templates/emails/otp_email.html</code>", code_style), Paragraph("Password Reset Request", body_style), Paragraph("6-digit OTP, 5-minute countdown warning, security disclaimer.", body_style)],
        [Paragraph("<code>templates/emails/password_reset_confirmed.html</code>", code_style), Paragraph("Password Reset Success", body_style), Paragraph("Security confirmation that password was updated with login button.", body_style)],
        [Paragraph("<code>templates/emails/welcome_email.html</code>", code_style), Paragraph("New User Registration", body_style), Paragraph("Welcome message outlining audio transcription and AI features.", body_style)],
        [Paragraph("<code>templates/emails/call_shared_email.html</code>", code_style), Paragraph("Call Record Shared", body_style), Paragraph("Notifies recipient of shared call details (audio & transcript kept private).", body_style)],
    ]
    t_smtp = Table(smtp_data, colWidths=[150, 120, 262])
    t_smtp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_smtp)

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 5: MONGODB
    # =========================================================================
    story.append(Paragraph("5. How MongoDB Works & How It Connects", h1_style))
    story.append(Paragraph(
        "CallSense uses <b>MongoDB</b> as its document store via the official <b>PyMongo</b> driver. "
        "A singleton client pattern in <code>services/db.py</code> avoids connection overhead by maintaining a single database handle.",
        body_style
    ))

    db_code = (
        "from pymongo import MongoClient\n"
        "from config import Config\n\n"
        "_client = None\n"
        "_db = None\n\n"
        "def get_db():\n"
        "    global _client, _db\n"
        "    if _db is None:\n"
        "        _client = MongoClient(Config.MONGO_URI)  # default: mongodb://localhost:27017\n"
        "        _db = _client[Config.MONGO_DB_NAME]      # default: call_analytics\n"
        "    return _db\n\n"
        "def get_users_collection():\n"
        "    return get_db()['users']\n\n"
        "def get_calls_collection():\n"
        "    return get_db()['calls']"
    )
    t_db = Table([[Paragraph(f"<pre>{db_code}</pre>", code_style)]], colWidths=[532])
    t_db.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_db)

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 6: COMMAND CHEATSHEET
    # =========================================================================
    story.append(Paragraph("6. macOS Command Cheatsheet", h1_style))
    story.append(Paragraph("Execute these commands from your project root folder with your virtual environment active:", body_style))

    cmd_data = [
        [Paragraph("<b>Task</b>", body_style), Paragraph("<b>Command Line</b>", body_style)],
        [Paragraph("Start MongoDB service", body_style), Paragraph("<code>brew services start mongodb-community</code>", code_style)],
        [Paragraph("Stop MongoDB service", body_style), Paragraph("<code>brew services stop mongodb-community</code>", code_style)],
        [Paragraph("Check MongoDB data", body_style), Paragraph("<code>./venv/bin/python -c \"from services.db import get_users_collection, get_calls_collection; print('Users:', get_users_collection().count_documents({}), '| Calls:', get_calls_collection().count_documents({}))\"</code>", code_style)],
        [Paragraph("Test Gmail SMTP delivery", body_style), Paragraph("<code>./venv/bin/python -c \"from services import email_service; ok, err = email_service.send_otp_email('foramsoni2004@gmail.com', '123456'); print('Sent:', ok, '| Error:', err)\"</code>", code_style)],
        [Paragraph("Promote an existing user to Admin", body_style), Paragraph("<code>./venv/bin/flask --app app.py make-admin</code>", code_style)],
        [Paragraph("Re-generate this PDF guide", body_style), Paragraph("<code>./venv/bin/python scripts/generate_auth_smtp_mongodb_pdf.py CallSense_Auth_SMTP_MongoDB_Guide.pdf</code>", code_style)],
        [Paragraph("Launch CallSense dev server", body_style), Paragraph("<code>./venv/bin/python app.py</code>", code_style)],
    ]
    t_cmd = Table(cmd_data, colWidths=[160, 372])
    t_cmd.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_cmd)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated PDF successfully at: {output_path}")


if __name__ == "__main__":
    out = "CallSense_Auth_SMTP_MongoDB_Guide.pdf"
    if len(sys.argv) > 1:
        out = sys.argv[1]
    build_pdf(out)
