"""
Script to generate CallSense_Viva_Questions_and_Answers.pdf
Comprehensive Viva Voce & Technical Defense Guide covering:
- Project Overview & Architecture
- Audio Ingestion & Noise Reduction (PyDub, NoiseReduce)
- Speech Transcription (Whisper Large V3 via Groq Cloud)
- LLM Intelligence & Classification (LLaMA / GPT-OSS)
- Database Design & PyMongo Connection (MongoDB)
- Security, Password Hashing & OTP via Gmail SMTP
- Troubleshooting & Project Defense Questions
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
            self.drawString(40, 755, "CallSense — Technical Viva Voce & Project Defense Guide")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, 747, 572, 747)

        # Running footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 25, page_str)
        self.drawString(40, 25, "CallSense Project Documentation — Viva Preparation Guide")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 36, 572, 36)
        self.restoreState()


def build_pdf(output_path="CallSense_Viva_Questions_and_Answers.pdf"):
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
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=10
    )

    category_style = ParagraphStyle(
        'CatHeading',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=16,
        textColor=colors.HexColor("#0284C7"),
        spaceBefore=11,
        spaceAfter=6,
        keepWithNext=True
    )

    q_style = ParagraphStyle(
        'Question',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=7,
        spaceAfter=2.5,
        keepWithNext=True
    )

    a_style = ParagraphStyle(
        'Answer',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'AnswerBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=12,
        textColor=colors.HexColor("#334155"),
        leftIndent=12,
        spaceAfter=2
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.2,
        leading=10,
        textColor=colors.HexColor("#0369A1"),
        spaceBefore=2,
        spaceAfter=3
    )

    story = []

    # Title Banner
    story.append(Paragraph("CallSense — Comprehensive Viva Questions & Answers", title_style))
    story.append(Paragraph("<b>Essential Questions, Model Answers, Architecture Rationale & Technical Defense</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284C7"), spaceBefore=0, spaceAfter=8))

    # =========================================================================
    # SECTION 1: PROJECT OVERVIEW & ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("Category 1: Project Overview & System Architecture", category_style))

    story.append(Paragraph("Q1: What is CallSense and what real-world problem does it solve?", q_style))
    story.append(Paragraph(
        "<b>Answer:</b> CallSense is an intelligent, full-stack call analytics pipeline designed for customer contact centers and support teams. "
        "Traditionally, quality assurance teams can only manually listen to 1–2% of recorded customer calls due to high time and labor costs. "
        "CallSense automates this by ingesting raw audio, stripping background noise, transcribing conversations across multiple Indian languages "
        "(English, Hindi, Gujarati), and utilizing LLMs to automatically extract customer sentiments, urgency levels, key issues, action items, "
        "and executive summaries in seconds.",
        a_style
    ))

    story.append(Paragraph("Q2: Explain the architectural pattern of the application.", q_style))
    story.append(Paragraph(
        "<b>Answer:</b> CallSense follows a <b>Service-Oriented Model-View-Controller (MVC)</b> architectural pattern:",
        a_style
    ))
    story.append(Paragraph("&bull; <b>Presentation Layer (Controller/View):</b> <code>app.py</code> handles HTTP routing, session management, and template rendering (HTML5/Vanilla CSS/Jinja2).", bullet_style))
    story.append(Paragraph("&bull; <b>Business Logic Layer (Services):</b> Decoupled modules under <code>services/</code> handle audio denoising (<code>audio_processing.py</code>), speech transcription (<code>transcription_service.py</code>), LLM intelligence (<code>llm_service.py</code>), pipeline orchestration (<code>pipeline.py</code>), authentication (<code>auth_service.py</code>), and email notifications (<code>email_service.py</code>).", bullet_style))
    story.append(Paragraph("&bull; <b>Persistence Layer (Model):</b> <code>services/db.py</code> manages MongoDB collections (<code>users</code>, <code>calls</code>, <code>password_resets</code>) using PyMongo with a singleton client pool.", bullet_style))

    story.append(Paragraph("Q3: Why did you choose Groq Cloud instead of running Whisper or LLaMA locally?", q_style))
    story.append(Paragraph(
        "<b>Answer:</b> Running large models like Whisper Large V3 (1.5 billion parameters) or LLaMA 70B locally requires high-end server GPUs "
        "(NVIDIA A100/H100 with 40–80GB VRAM) which are unaffordable on standard laptops or CPU servers. "
        "Groq provides custom LPU (Language Processing Unit) hardware acceleration in the cloud with near-zero latency, sub-second inference speeds, "
        "and zero CPU/RAM degradation on our web server.",
        a_style
    ))

    story.append(Paragraph("Q4: How does the Pipeline Orchestrator (services/pipeline.py) track call status?", q_style))
    story.append(Paragraph(
        "<b>Answer:</b> The orchestrator moves each uploaded call through a deterministic state machine: "
        "<code>'uploaded'</code> &rarr; <code>'preprocessing_audio'</code> &rarr; <code>'transcribing'</code> &rarr; <code>'analyzing'</code> &rarr; <code>'completed'</code> (or <code>'failed'</code>). "
        "Each stage transition is written atomically to MongoDB so the UI can accurately display processing progress.",
        a_style
    ))

    story.append(Spacer(1, 6))

    # =========================================================================
    # SECTION 2: AUDIO PROCESSING & PREPROCESSING
    # =========================================================================
    story.append(Paragraph("Category 2: Audio Ingestion & Preprocessing (PyDub, NoiseReduce)", category_style))

    story.append(Paragraph("Q5: Why is audio preprocessing necessary before sending audio to Whisper?", q_style))
    story.append(Paragraph(
        "<b>Answer:</b> Real-world call recordings often have background chatter, electrical hiss, variable sampling rates, multiple channels, "
        "and long dead-air silences. Preprocessing cleans the input so Whisper receives clear, normalized speech, directly boosting transcription "
        "accuracy and reducing transcription hallucinations.",
        a_style
    ))

    story.append(Paragraph("Q6: What specific operations are performed in services/audio_processing.py?", q_style))
    story.append(Paragraph("&bull; <b>Format Standardization:</b> <code>pydub.AudioSegment</code> converts any uploaded format (MP3, M4A, OGG, WEBM) to 16kHz, 16-bit mono WAV (the optimal format for Whisper).", bullet_style))
    story.append(Paragraph("&bull; <b>Stationary Noise Reduction:</b> <code>noisereduce.reduce_noise()</code> analyzes non-voice audio bands to eliminate steady-state hums and room echoes without distorting human vocals.", bullet_style))
    story.append(Paragraph("&bull; <b>Decibel Normalization:</b> Normalizes average loudness (target -20 dBFS) so quiet speakers become clearly audible.", bullet_style))
    story.append(Paragraph("&bull; <b>Silence Trimming:</b> Detects and trims leading and trailing dead air, leaving a 200ms natural padding to save inference compute.", bullet_style))

    story.append(Paragraph("Q7: What is the fail-safe mechanism in audio preprocessing?", q_style))
    story.append(Paragraph(
        "<b>Answer:</b> A try-except block encapsulates all preprocessing steps. If an obscure codec or corrupted audio file triggers an exception, "
        "the system catches the error, logs it, and gracefully falls back to sending the original unedited file to Whisper. This ensures the upload "
        "never crashes the application.",
        a_style
    ))

    story.append(Spacer(1, 6))

    # =========================================================================
    # SECTION 3: SPEECH TRANSCRIPTION (WHISPER LARGE V3)
    # =========================================================================
    story.append(Paragraph("Category 3: Multilingual Speech-to-Text Transcription", category_style))

    story.append(Paragraph("Q8: Which Whisper model is used and how are Indian regional languages handled?", q_style))
    story.append(Paragraph(
        "<b>Answer:</b> The project uses <b>Whisper Large V3</b> (hosted by Groq). It features state-of-the-art multilingual acoustic models capable "
        "of transcribing English, Hindi (Devanagari), Gujarati (Gujarati script), and code-mixed conversations (such as Hinglish or Gujlish). "
        "The user can either select a target language or let Whisper auto-detect the spoken language from the initial 30-second audio window.",
        a_style
    ))

    story.append(Paragraph("Q9: How is the 'Overall Accuracy' / Confidence Score calculated?", q_style))
    story.append(Paragraph(
        "<b>Answer:</b> Whisper returns log-probabilities for each token generated. In <code>services/transcription_service.py</code>, these log-probabilities "
        "are converted into a 0–100% confidence score (<code>confidence_percent</code>). The system also builds a <code>confidence_breakdown</code> "
        "identifying reasons why confidence was reduced (e.g. ambient background noise, overlapping speech, mumbling, or low volume).",
        a_style
    ))

    story.append(Paragraph("Q10: How do you achieve Speaker Diarization (Agent vs Customer separation)?", q_style))
    story.append(Paragraph(
        "<b>Answer:</b> We apply a temporal speaker-turn heuristic. Whisper returns timestamped utterance segments (start time, end time, text). "
        "The system analyzes conversational pause gaps (>= 0.5s) and phrase markers to alternate speakers sequentially between "
        "<b>Agent</b> and <b>Customer</b>, which is then refined during the LLM intelligence phase.",
        a_style
    ))

    story.append(Spacer(1, 6))

    # =========================================================================
    # SECTION 4: LLM INTELLIGENCE & INSIGHTS EXTRACTION
    # =========================================================================
    story.append(Paragraph("Category 4: Natural Language Processing & LLM Analytics", category_style))

    story.append(Paragraph("Q11: Which LLM is used for summarization and how is it called?", q_style))
    story.append(Paragraph(
        "<b>Answer:</b> It runs via the Groq Cloud API using models such as <code>openai/gpt-oss-120b</code> or Meta's <code>llama-3.3-70b-versatile</code>. "
        "The model is invoked using Groq's Python SDK (<code>client.chat.completions.create()</code>) with <code>response_format={'type': 'json_object'}</code> "
        "to guarantee structured JSON outputs.",
        a_style
    ))

    story.append(Paragraph("Q12: How do you extract structured fields from free-text transcripts without errors?", q_style))
    story.append(Paragraph(
        "<b>Answer:</b> In <code>services/llm_service.py</code>, we construct a rigorous system prompt outlining a schema with required JSON keys: "
        "<code>summary</code>, <code>motive</code>, <code>category</code>, <code>sentiment</code> (Positive/Neutral/Negative), "
        "<code>priority</code> (Low/Medium/High/Urgent), <code>resolution_status</code>, <code>key_issues</code>, and <code>action_items</code>. "
        "A robust parser strips markdown code fences and validates the parsed JSON before committing it to MongoDB.",
        a_style
    ))

    story.append(Paragraph("Q13: Why did you use regex instead of the LLM to extract phone numbers?", q_style))
    story.append(Paragraph(
        "<b>Answer:</b> Generative LLMs can occasionally hallucinate or misquote digits in long numbers. "
        "Phone numbers follow exact digit patterns (e.g. 10-digit Indian numbers: <code>(?<!\\d)(\\d{10})(?!\\d)</code>). "
        "Deterministic regular expressions guarantee 100% precision with zero hallucinations.",
        a_style
    ))

    story.append(Spacer(1, 6))

    # =========================================================================
    # SECTION 5: DATABASE & PERSISTENCE (MONGODB)
    # =========================================================================
    story.append(Paragraph("Category 5: Database Design & MongoDB Connectivity", category_style))

    story.append(Paragraph("Q14: Why did you choose MongoDB over a relational SQL database?", q_style))
    story.append(Paragraph(
        "<b>Answer:</b> Call analytics data is inherently hierarchical, semi-structured, and polymorphic. Each call record contains nested arrays "
        "(key issues, action items, phone numbers), embedded sharing objects (<code>shared_with</code> list), and variable confidence breakdown dictionaries. "
        "MongoDB stores native BSON documents without requiring complex multi-table JOINs, offering flexible schema evolution as new analytics fields are added.",
        a_style
    ))

    story.append(Paragraph("Q15: Explain the Singleton Database Pattern in services/db.py.", q_style))
    story.append(Paragraph(
        "<b>Answer:</b> Creating a new TCP connection to MongoDB on every web request causes high latency and exhausts connection sockets. "
        "<code>services/db.py</code> maintains a module-level global variable <code>_client</code>. On the first request, <code>MongoClient(Config.MONGO_URI)</code> "
        "is initialized; subsequent requests reuse the existing connection pool handle.",
        a_style
    ))

    story.append(Paragraph("Q16: What collections are maintained in the database?", q_style))
    story.append(Paragraph("&bull; <code>users</code>: Registered accounts, usernames, emails, Werkzeug password hashes, and admin privilege flags.", bullet_style))
    story.append(Paragraph("&bull; <code>calls</code>: Audio metadata, transcripts, durations, LLM insights, confidence scores, and sharing arrays.", bullet_style))
    story.append(Paragraph("&bull; <code>password_resets</code>: OTP hashes, creation timestamps, 5-minute TTL expirations, attempt counters, and single-use reset tokens.", bullet_style))

    story.append(Spacer(1, 6))

    # =========================================================================
    # SECTION 6: AUTHENTICATION, SECURITY & GMAIL SMTP
    # =========================================================================
    story.append(Paragraph("Category 6: Security, Authentication & Gmail SMTP Integration", category_style))

    story.append(Paragraph("Q17: How are passwords stored and authenticated securely?", q_style))
    story.append(Paragraph(
        "<b>Answer:</b> Passwords are never stored in plain text. We use <code>werkzeug.security.generate_password_hash()</code>, which employs "
        "salted, key-stretched hashing (Scrypt / PBKDF2 with SHA-256). During login, <code>check_password_hash()</code> re-computes the hash using "
        "the embedded salt and verifies equality in constant time to prevent timing attacks.",
        a_style
    ))

    story.append(Paragraph("Q18: What is Account Enumeration and how does CallSense prevent it?", q_style))
    story.append(Paragraph(
        "<b>Answer:</b> Account enumeration occurs when an application reveals whether an email is registered (e.g. 'Email not found' vs 'Code sent'). "
        "Attackers harvest valid emails using this feedback. CallSense returns an identical, generic message: "
        "<i>'If an account matches that email address, a 6-digit verification code has been sent'</i>, preventing attackers from probing user existence.",
        a_style
    ))

    story.append(Paragraph("Q19: How does the OTP password reset flow prevent brute-force attacks?", q_style))
    story.append(Paragraph("&bull; <b>Cryptographic Randomness:</b> Generated via <code>secrets.randbelow(900000) + 100000</code> (not pseudo-random <code>random</code>).", bullet_style))
    story.append(Paragraph("&bull; <b>Attempt Limiting:</b> Capped at a maximum of 5 attempts. Exceeding 5 attempts immediately locks and invalidates the code.", bullet_style))
    story.append(Paragraph("&bull; <b>Time-to-Live (TTL):</b> Codes expire automatically after 5 minutes (300 seconds).", bullet_style))
    story.append(Paragraph("&bull; <b>Resend Rate Limit:</b> Enforces a 60-second cooldown between resend requests.", bullet_style))
    story.append(Paragraph("&bull; <b>Single-Use Reset Token:</b> Once verified, an ephemeral 32-byte token is issued; upon password change, it is immediately marked <code>used: True</code>.", bullet_style))

    story.append(Paragraph("Q20: How does Gmail SMTP connect and why is an App Password required?", q_style))
    story.append(Paragraph(
        "<b>Answer:</b> Python's <code>smtplib</code> connects to <code>smtp.gmail.com:587</code> and executes <code>server.starttls()</code> to upgrade "
        "to TLS encryption. Google requires 2-Factor Authentication (2FA) on developer accounts; standard account passwords cannot be used directly in scripts. "
        "Instead, a 16-character dedicated <b>App Password</b> is generated in Google Security settings. CallSense automatically strips any formatting spaces.",
        a_style
    ))

    story.append(Paragraph("Q21: How is privacy protected when a call is shared with another user?", q_style))
    story.append(Paragraph(
        "<b>Answer:</b> When a call is shared, the email notification sent via SMTP contains only the call filename, sender name, and a link to view it. "
        "Private audio files, full transcripts, and customer phone numbers are strictly excluded from the email body and can only be accessed after "
        "logging into CallSense under the <code>Shared With Me</code> tab.",
        a_style
    ))

    story.append(Spacer(1, 6))

    # =========================================================================
    # SECTION 7: PROJECT DEFENSE & TECHNICAL COMMANDS
    # =========================================================================
    story.append(Paragraph("Category 7: Project Defense, Operations & Troubleshooting", category_style))

    story.append(Paragraph("Q22: Why is 'threaded=True' used in app.py?", q_style))
    story.append(Paragraph(
        "<b>Answer:</b> By default, Flask's development server is single-threaded. When a user uploads a recording and processing takes 5–8 seconds, "
        "a single-threaded server blocks all other concurrent requests (e.g. another user clicking Profile or Login). "
        "Enabling <code>app.run(debug=True, threaded=True)</code> allows Flask to spawn a new thread per request, enabling concurrent user access.",
        a_style
    ))

    story.append(Paragraph("Q23: How do you promote an existing user to Administrator?", q_style))
    story.append(Paragraph(
        "<b>Answer:</b> We built a custom Flask CLI command: <code>flask --app app.py make-admin</code>. "
        "It prompts for the user's email and executes <code>users.update_one({'email': email}, {'$set': {'is_admin': True}})</code>. "
        "Alternatively, emails listed under <code>ADMIN_EMAILS</code> in <code>.env</code> automatically receive admin privileges at signup.",
        a_style
    ))

    story.append(Paragraph("Q24: What are the key future enhancements for CallSense?", q_style))
    story.append(Paragraph("&bull; <b>Asynchronous Task Queue:</b> Integrating Celery with Redis for background audio job processing instead of blocking HTTP requests.", bullet_style))
    story.append(Paragraph("&bull; <b>Real-Time WebSockets:</b> Live audio streaming transcription directly from browser microphones.", bullet_style))
    story.append(Paragraph("&bull; <b>CRM Integration:</b> Automated webhooks pushing call summaries directly into Salesforce or HubSpot.", bullet_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated PDF successfully at: {output_path}")


if __name__ == "__main__":
    out = "CallSense_Viva_Questions_and_Answers.pdf"
    if len(sys.argv) > 1:
        out = sys.argv[1]
    build_pdf(out)
