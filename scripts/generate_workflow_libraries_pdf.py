"""
Script to generate CallSense_Project_Workflow_and_Libraries_Guide.pdf
Comprehensive technical guide covering the entire CallSense project workflow,
specifying for EVERY phase and page:
- Workflow description & steps
- Exact libraries to install (pip install command)
- Exact libraries to import (Python import statements)
- Files involved in that phase
- Execution logic & architecture
"""
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
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
            self.drawString(40, 755, "CallSense — Project Workflow, Installation & Library Import Guide")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, 747, 572, 747)

        # Running footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 25, page_str)
        self.drawString(40, 25, "CallSense System Reference — Project Workflow & Library Architecture")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 36, 572, 36)
        self.restoreState()


def build_pdf(output_path="CallSense_Project_Workflow_and_Libraries_Guide.pdf"):
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
        fontSize=20,
        leading=24,
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

    h1_style = ParagraphStyle(
        'SecH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=16,
        textColor=colors.HexColor("#0284C7"),
        spaceBefore=11,
        spaceAfter=5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SecH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'SecBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'SecBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=12.5,
        textColor=colors.HexColor("#334155"),
        leftIndent=14,
        spaceAfter=2
    )

    code_style = ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.2,
        leading=10,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=2,
        spaceAfter=3
    )

    story = []

    # Title Banner
    story.append(Paragraph("CallSense — Complete Project Workflow Guide", title_style))
    story.append(Paragraph("<b>End-to-End Execution Pipeline, Required Libraries, Installation Commands & Python Imports</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284C7"), spaceBefore=0, spaceAfter=8))

    # =========================================================================
    # PHASE 1: SYSTEM SETUP & MONGODB CONNECTIVITY
    # =========================================================================
    story.append(Paragraph("Phase 1: Environment Setup & MongoDB Database Connectivity", h1_style))
    story.append(Paragraph(
        "<b>Workflow Description:</b> When CallSense boots, it loads environment variables (Groq keys, MongoDB URI, SMTP credentials) "
        "and establishes a persistent, high-performance singleton connection to MongoDB.",
        body_style
    ))

    p1_box = [
        [
            Paragraph("<b>📦 Libraries to Install (Terminal):</b>", body_style),
            Paragraph("<code>./venv/bin/pip install pymongo python-dotenv</code>", code_style)
        ],
        [
            Paragraph("<b>📥 Libraries to Import in Code:</b>", body_style),
            Paragraph("<code>from pymongo import MongoClient<br/>from dotenv import load_dotenv<br/>import os</code>", code_style)
        ],
        [
            Paragraph("<b>📂 Files Involved:</b>", body_style),
            Paragraph("<code>config.py</code>, <code>services/db.py</code>, <code>.env</code>", code_style)
        ],
    ]
    t_p1 = Table(p1_box, colWidths=[150, 382])
    t_p1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_p1)

    story.append(Paragraph("Step-by-Step Execution Flow:", h2_style))
    story.append(Paragraph("&bull; <b>Step 1:</b> <code>config.py</code> invokes <code>load_dotenv()</code> to read credentials from <code>.env</code> into <code>os.environ</code>.", bullet_style))
    story.append(Paragraph("&bull; <b>Step 2:</b> <code>services/db.py</code> checks if the global <code>_client</code> is initialized. If None, it instantiates <code>MongoClient('mongodb://localhost:27017')</code>.", bullet_style))
    story.append(Paragraph("&bull; <b>Step 3:</b> Exposes collection handles: <code>get_users_collection()</code>, <code>get_calls_collection()</code>, and <code>get_db()['password_resets']</code>.", bullet_style))

    story.append(Spacer(1, 6))

    # =========================================================================
    # PHASE 2: USER REGISTRATION & AUTHENTICATION
    # =========================================================================
    story.append(Paragraph("Phase 2: User Registration, Login & Session Management", h1_style))
    story.append(Paragraph(
        "<b>Workflow Description:</b> Manages new user signups, cryptographic password hashing, login authentication, "
        "and role-based authorization for standard users vs administrators.",
        body_style
    ))

    p2_box = [
        [
            Paragraph("<b>📦 Libraries to Install (Terminal):</b>", body_style),
            Paragraph("<code>./venv/bin/pip install Flask Werkzeug</code>", code_style)
        ],
        [
            Paragraph("<b>📥 Libraries to Import in Code:</b>", body_style),
            Paragraph("<code>from flask import Flask, render_template, request, redirect, url_for, session, flash<br/>from werkzeug.security import generate_password_hash, check_password_hash<br/>from functools import wraps<br/>import re, secrets</code>", code_style)
        ],
        [
            Paragraph("<b>📂 Files Involved:</b>", body_style),
            Paragraph("<code>app.py</code>, <code>services/auth_service.py</code>, <code>templates/register.html</code>, <code>templates/login.html</code>", code_style)
        ],
    ]
    t_p2 = Table(p2_box, colWidths=[150, 382])
    t_p2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_p2)

    story.append(Paragraph("Step-by-Step Execution Flow:", h2_style))
    story.append(Paragraph("&bull; <b>Registration:</b> <code>validate_registration()</code> verifies fields &rarr; <code>generate_password_hash()</code> salts and hashes password &rarr; Checks <code>ADMIN_EMAILS</code> for admin role &rarr; Saves to <code>users</code>.", bullet_style))
    story.append(Paragraph("&bull; <b>Login:</b> User enters username/email &rarr; <code>authenticate_user()</code> fetches record from MongoDB &rarr; <code>check_password_hash()</code> verifies password &rarr; Session cookies initialized.", bullet_style))
    story.append(Paragraph("&bull; <b>Route Protection:</b> <code>@login_required</code> decorator protects private routes; <code>@admin_required</code> guards <code>/admin/*</code>.", bullet_style))

    story.append(Spacer(1, 6))

    # =========================================================================
    # PHASE 3: FORGOT PASSWORD & GMAIL SMTP
    # =========================================================================
    story.append(Paragraph("Phase 3: Forgot Password, OTP Verification & Gmail SMTP", h1_style))
    story.append(Paragraph(
        "<b>Workflow Description:</b> Secure password recovery generating cryptographically random 6-digit OTPs, "
        "relayed through Gmail SMTP over Port 587 using TLS encryption.",
        body_style
    ))

    p3_box = [
        [
            Paragraph("<b>📦 Libraries to Install (Terminal):</b>", body_style),
            Paragraph("<code>./venv/bin/pip install jinja2 python-dotenv</code><br/><i>(Note: <code>smtplib</code> and <code>email</code> are built into Python standard library)</i>", code_style)
        ],
        [
            Paragraph("<b>📥 Libraries to Import in Code:</b>", body_style),
            Paragraph("<code>import smtplib<br/>from email.mime.multipart import MIMEMultipart<br/>from email.mime.text import MIMEText<br/>from email.utils import formataddr<br/>import secrets, logging<br/>from jinja2 import Environment, FileSystemLoader</code>", code_style)
        ],
        [
            Paragraph("<b>📂 Files Involved:</b>", body_style),
            Paragraph("<code>services/email_service.py</code>, <code>services/otp_service.py</code>, <code>templates/forgot_password.html</code>, <code>templates/verify_otp.html</code>, <code>templates/reset_password.html</code>, <code>templates/emails/*.html</code>", code_style)
        ],
    ]
    t_p3 = Table(p3_box, colWidths=[150, 382])
    t_p3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_p3)

    story.append(Paragraph("Step-by-Step Execution Flow:", h2_style))
    story.append(Paragraph("&bull; <b>1. Request OTP:</b> User inputs email at <code>/forgot-password</code> &rarr; Anti-enumeration protects non-existent emails &rarr; Generates 6 digits via <code>secrets.randbelow(900000) + 100000</code>.", bullet_style))
    story.append(Paragraph("&bull; <b>2. SMTP Dispatch:</b> <code>email_service.send_email()</code> connects to <code>smtp.gmail.com:587</code>, starts TLS, logs in with 16-char App Password (spaces stripped), and delivers branded HTML email.", bullet_style))
    story.append(Paragraph("&bull; <b>3. Verify Code:</b> User enters code at <code>/verify-otp</code> (5-min expiry, max 5 attempts) &rarr; Success grants single-use <code>reset_token</code>.", bullet_style))
    story.append(Paragraph("&bull; <b>4. Reset Password:</b> New password hashed with Werkzeug at <code>/reset-password</code> &rarr; Confirmation email sent.", bullet_style))

    story.append(Spacer(1, 6))

    # =========================================================================
    # PHASE 4: AUDIO UPLOAD & PREPROCESSING
    # =========================================================================
    story.append(Paragraph("Phase 4: Audio File Upload & Denoising Preprocessing", h1_style))
    story.append(Paragraph(
        "<b>Workflow Description:</b> Audio recordings are uploaded, validated, converted to standardized mono WAV format, "
        "and cleaned of stationary background noise and electrical hums prior to transcription.",
        body_style
    ))

    p4_box = [
        [
            Paragraph("<b>📦 Libraries to Install (Terminal):</b>", body_style),
            Paragraph("<code>./venv/bin/pip install pydub noisereduce numpy Werkzeug</code><br/><i>(macOS FFmpeg tool: <code>brew install ffmpeg</code>)</i>", code_style)
        ],
        [
            Paragraph("<b>📥 Libraries to Import in Code:</b>", body_style),
            Paragraph("<code>from pydub import AudioSegment<br/>import noisereduce as nr<br/>import numpy as np<br/>from werkzeug.utils import secure_filename<br/>import os, tempfile</code>", code_style)
        ],
        [
            Paragraph("<b>📂 Files Involved:</b>", body_style),
            Paragraph("<code>app.py</code>, <code>services/audio_processing.py</code>, <code>services/pipeline.py</code>, <code>templates/dashboard.html</code>", code_style)
        ],
    ]
    t_p4 = Table(p4_box, colWidths=[150, 382])
    t_p4.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_p4)

    story.append(Paragraph("Step-by-Step Execution Flow:", h2_style))
    story.append(Paragraph("&bull; <b>1. Ingestion:</b> Audio received at <code>/upload</code> &rarr; Validates extension (<code>mp3, wav, m4a, ogg, webm</code>) &rarr; Saved to <code>uploads/</code> &rarr; DB status set to <code>'uploaded'</code>.", bullet_style))
    story.append(Paragraph("&bull; <b>2. Normalization:</b> <code>services/audio_processing.py</code> converts audio to 16kHz mono WAV using <code>pydub.AudioSegment</code>.", bullet_style))
    story.append(Paragraph("&bull; <b>3. Noise Reduction:</b> Extracts raw audio samples as NumPy array &rarr; <code>nr.reduce_noise(y=samples, sr=16000)</code> removes room hums.", bullet_style))
    story.append(Paragraph("&bull; <b>4. Volume Leveling:</b> Trims leading/trailing silence and normalizes decibels so faint speech is audible.", bullet_style))

    story.append(Spacer(1, 6))

    # =========================================================================
    # PHASE 5: SPEECH TRANSCRIPTION VIA WHISPER LARGE V3
    # =========================================================================
    story.append(Paragraph("Phase 5: Speech-to-Text Transcription via Groq Whisper Large V3", h1_style))
    story.append(Paragraph(
        "<b>Workflow Description:</b> Audio is streamed to Groq Cloud's ultra-fast Whisper Large V3 hardware inference engine, "
        "recognizing multilingual speech, computing confidence scores, and separating speakers.",
        body_style
    ))

    p5_box = [
        [
            Paragraph("<b>📦 Libraries to Install (Terminal):</b>", body_style),
            Paragraph("<code>./venv/bin/pip install groq httpx</code>", code_style)
        ],
        [
            Paragraph("<b>📥 Libraries to Import in Code:</b>", body_style),
            Paragraph("<code>from groq import Groq<br/>import httpx<br/>import time, os</code>", code_style)
        ],
        [
            Paragraph("<b>📂 Files Involved:</b>", body_style),
            Paragraph("<code>services/transcription_service.py</code>, <code>services/pipeline.py</code>, <code>config.py</code>", code_style)
        ],
    ]
    t_p5 = Table(p5_box, colWidths=[150, 382])
    t_p5.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_p5)

    story.append(Paragraph("Step-by-Step Execution Flow:", h2_style))
    story.append(Paragraph("&bull; <b>1. API Invocation:</b> <code>groq_client.audio.transcriptions.create()</code> sends audio file with model <code>'whisper-large-v3'</code>.", bullet_style))
    story.append(Paragraph("&bull; <b>2. Language Detection:</b> Detects spoken language (English, Hindi, Gujarati, or code-mixed Hinglish/Gujlish).", bullet_style))
    story.append(Paragraph("&bull; <b>3. Confidence Score:</b> Calculates <code>confidence_percent</code> (e.g. 91.5%) and breaks down deductions (background noise, speed).", bullet_style))
    story.append(Paragraph("&bull; <b>4. Diarization Heuristic:</b> Parses speech segments to alternate dialogue between <b>Agent</b> and <b>Customer</b>.", bullet_style))

    story.append(Spacer(1, 6))

    # =========================================================================
    # PHASE 6: LLM INTELLIGENCE & INSIGHTS EXTRACTION
    # =========================================================================
    story.append(Paragraph("Phase 6: LLM Intelligence, Summarization & Analytics Extraction", h1_style))
    story.append(Paragraph(
        "<b>Workflow Description:</b> Passes transcript to Groq Cloud LLM (<code>openai/gpt-oss-120b</code> or LLaMA 3.3) "
        "to extract structured JSON containing summaries, sentiment, priority, categories, and action items.",
        body_style
    ))

    p6_box = [
        [
            Paragraph("<b>📦 Libraries to Install (Terminal):</b>", body_style),
            Paragraph("<code>./venv/bin/pip install groq</code><br/><i>(Note: <code>json</code> and <code>re</code> are built into Python standard library)</i>", code_style)
        ],
        [
            Paragraph("<b>📥 Libraries to Import in Code:</b>", body_style),
            Paragraph("<code>from groq import Groq<br/>import json, re, logging</code>", code_style)
        ],
        [
            Paragraph("<b>📂 Files Involved:</b>", body_style),
            Paragraph("<code>services/llm_service.py</code>, <code>services/pipeline.py</code>", code_style)
        ],
    ]
    t_p6 = Table(p6_box, colWidths=[150, 382])
    t_p6.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_p6)

    story.append(Paragraph("Step-by-Step Execution Flow:", h2_style))
    story.append(Paragraph("&bull; <b>1. Prompt Assembly:</b> Injects transcript into system prompt enforcing a strict JSON schema.", bullet_style))
    story.append(Paragraph("&bull; <b>2. Structured Output:</b> Model extracts: <code>summary</code>, <code>motive</code>, <code>category</code>, <code>sentiment</code> (Positive/Neutral/Negative), <code>priority</code> (Low/Medium/High/Urgent), <code>resolution_status</code>, <code>key_issues</code>, and <code>action_items</code>.", bullet_style))
    story.append(Paragraph("&bull; <b>3. Database Persistence:</b> MongoDB atomically updates the call document and sets status to <code>'completed'</code>.", bullet_style))

    story.append(Spacer(1, 6))

    # =========================================================================
    # PHASE 7: DASHBOARD, SHARING & EXPORTS
    # =========================================================================
    story.append(Paragraph("Phase 7: Dashboard Display, Call Sharing & Report Exports", h1_style))
    story.append(Paragraph(
        "<b>Workflow Description:</b> Renders interactive call cards on user and admin dashboards, enables secure "
        "inter-user call sharing with email alerts, and produces downloadable Excel (CSV) and PDF reports.",
        body_style
    ))

    p7_box = [
        [
            Paragraph("<b>📦 Libraries to Install (Terminal):</b>", body_style),
            Paragraph("<code>./venv/bin/pip install reportlab</code><br/><i>(Note: <code>csv</code> and <code>io</code> are built into Python standard library)</i>", code_style)
        ],
        [
            Paragraph("<b>📥 Libraries to Import in Code:</b>", body_style),
            Paragraph("<code>import csv, io<br/>from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer<br/>from reportlab.lib.pagesizes import letter<br/>from reportlab.lib import colors<br/>from bson import ObjectId</code>", code_style)
        ],
        [
            Paragraph("<b>📂 Files Involved:</b>", body_style),
            Paragraph("<code>app.py</code>, <code>services/share_service.py</code>, <code>services/admin_service.py</code>, <code>templates/dashboard.html</code>", code_style)
        ],
    ]
    t_p7 = Table(p7_box, colWidths=[150, 382])
    t_p7.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_p7)

    story.append(Paragraph("Step-by-Step Execution Flow:", h2_style))
    story.append(Paragraph("&bull; <b>Dashboard Render:</b> <code>_compute_stats()</code> calculates completed counts, accuracy averages, and processing durations.", bullet_style))
    story.append(Paragraph("&bull; <b>Call Sharing:</b> User clicks 'Share' &rarr; Selects recipient from <code>/api/users/shareable</code> &rarr; Updates <code>shared_with</code> array in MongoDB &rarr; Dispatches email notification via Gmail SMTP (private transcripts/audio are not emailed).", bullet_style))
    story.append(Paragraph("&bull; <b>Excel / CSV Export:</b> <code>csv.writer()</code> streams structured calls data directly into a spreadsheet.", bullet_style))
    story.append(Paragraph("&bull; <b>PDF Export:</b> ReportLab compiles executive summary, metadata table, and speech transcript into a PDF report.", bullet_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated PDF successfully at: {output_path}")


if __name__ == "__main__":
    out = "CallSense_Project_Workflow_and_Libraries_Guide.pdf"
    if len(sys.argv) > 1:
        out = sys.argv[1]
    build_pdf(out)
