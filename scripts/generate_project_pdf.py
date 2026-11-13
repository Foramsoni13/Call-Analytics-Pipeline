import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
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
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8.5)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(40, 755, "CallSense — Customer Call Analytics Pipeline Architecture & Project Guide")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, 747, 572, 747)

        # Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 25, page_str)
        self.drawString(40, 25, "Confidential & Proprietary — CallSense Project Documentation")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 36, 572, 36)
        self.restoreState()


def create_project_pdf(output_path="CallSense_Project_Guide.pdf"):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    # Custom palette
    PRIMARY = colors.HexColor("#0F172A")    # Slate 900
    SECONDARY = colors.HexColor("#1E293B")  # Slate 800
    ACCENT = colors.HexColor("#0284C7")     # Sky 600
    ACCENT_PURPLE = colors.HexColor("#6366F1") # Indigo 500
    TEXT_DARK = colors.HexColor("#334155")  # Slate 700
    BG_LIGHT = colors.HexColor("#F8FAFC")   # Slate 50
    BORDER_LIGHT = colors.HexColor("#E2E8F0") # Slate 200

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=PRIMARY,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=ACCENT,
        spaceAfter=12,
    )
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=PRIMARY,
        spaceBefore=12,
        spaceAfter=6,
    )
    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=SECONDARY,
        spaceBefore=8,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=TEXT_DARK,
        spaceAfter=6,
    )
    body_bold = ParagraphStyle(
        "BodyBold_Custom",
        parent=body_style,
        fontName="Helvetica-Bold",
    )
    badge_style = ParagraphStyle(
        "Badge",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
    )
    callout_style = ParagraphStyle(
        "Callout",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12.5,
        textColor=SECONDARY,
    )
    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=TEXT_DARK,
    )
    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=table_cell,
        fontName="Helvetica-Bold",
        textColor=PRIMARY,
    )
    table_header = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.white,
    )

    story = []

    # ==========================
    # HEADER BANNER
    # ==========================
    banner_data = [
        [
            Paragraph("<b>CallSense</b> — Intelligent Call Analytics Pipeline", title_style),
            Paragraph("<font color='#0284C7'><b>VERSION 2.0</b></font><br/><font color='#64748B'>Full Architecture &amp; User Manual</font>", ParagraphStyle("RightH", parent=body_style, alignment=2))
        ],
        [
            Paragraph("An end-to-end, multi-lingual audio intelligence web application that transforms raw customer service phone calls into actionable insights, accurate transcripts, sentiment analysis, and translations.", subtitle_style),
            ""
        ]
    ]
    banner_table = Table(banner_data, colWidths=[400, 132])
    banner_table.setStyle(TableStyle([
        ('SPAN', (0, 1), (1, 1)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(banner_table)
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceBefore=4, spaceAfter=10))

    # ==========================
    # 1. WHAT IS CALLSENSE (EASY EXPLANATION)
    # ==========================
    story.append(Paragraph("1. Executive Summary: What is CallSense &amp; What Problem Does it Solve?", h1_style))
    summary_text = (
        "In modern customer support centers, thousands of customer calls are handled daily across multiple languages "
        "(primarily <b>Hindi, Gujarati, and English</b> in India). Quality analysts and managers cannot manually listen "
        "to every phone call. <b>CallSense</b> solves this by automatically analyzing call recordings within seconds: "
        "it cleans up audio noise, transcribes speech accurately in its native alphabet, extracts customer and agent details, "
        "classifies call intent, measures customer sentiment, assigns priority, and provides full <b>Gujarati and English translations</b>."
    )
    story.append(Paragraph(summary_text, body_style))

    # Core value proposition callout box
    value_data = [[
        Paragraph(
            "<b>Key Advantage:</b> Unlike traditional systems requiring heavy GPUs or slow local setups, CallSense "
            "uses high-speed cloud inference via Groq. It delivers near-instant transcription and analysis with "
            "<b>0% local CPU/RAM bottleneck</b>, runs completely on free-tier APIs, and saves all structured analytics into MongoDB.",
            callout_style
        )
    ]]
    value_table = Table(value_data, colWidths=[532])
    value_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F0F9FF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#BAE6FD")),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(value_table)
    story.append(Spacer(1, 8))

    # ==========================
    # 2. HOW THE SYSTEM WORKS (THE 4-STAGE PIPELINE)
    # ==========================
    story.append(Paragraph("2. How It Works: The 4-Stage Processing Pipeline", h1_style))
    story.append(Paragraph(
        "Every audio call uploaded or recorded live passes through a strictly orchestrated pipeline (managed in "
        "<code>services/pipeline.py</code>) that reports real-time progress to MongoDB and the web dashboard:",
        body_style
    ))

    pipeline_data = [
        [
            Paragraph("Stage", table_header),
            Paragraph("Component &amp; Technology", table_header),
            Paragraph("What Happens Behind the Scenes", table_header),
            Paragraph("Output Produced", table_header)
        ],
        [
            Paragraph("<b>Stage 1: Preprocess</b>", table_cell_bold),
            Paragraph("<b>FFmpeg + PyDub + NoiseReduce</b>", table_cell),
            Paragraph("Converts audio to 16kHz mono, applies band-pass filter (80Hz–3800Hz voice band), reduces ambient background hum, and normalizes volume.", table_cell),
            Paragraph("Optimized, crystal-clear 16kHz WAV audio", table_cell)
        ],
        [
            Paragraph("<b>Stage 2: Transcribe</b>", table_cell_bold),
            Paragraph("<b>Groq Whisper large-v3</b>", table_cell),
            Paragraph("Performs acoustic language detection (Hindi, Gujarati, English). Eliminates false transliteration so Hindi words stay in Devanagari and Gujarati words stay in Gujarati.", table_cell),
            Paragraph("Clean verbatim transcript + language name + confidence %", table_cell)
        ],
        [
            Paragraph("<b>Stage 3: AI Intelligence</b>", table_cell_bold),
            Paragraph("<b>Groq LLM (GPT-OSS / LLaMA)</b>", table_cell),
            Paragraph("Single-pass structured extraction: classifies Category, Sentiment, Priority, Resolution; extracts Names, Key Issues, Action Items, and generates Gujarati &amp; English translations.", table_cell),
            Paragraph("Structured JSON with 12 analytic fields + translations", table_cell)
        ],
        [
            Paragraph("<b>Stage 4: Storage &amp; UI</b>", table_cell_bold),
            Paragraph("<b>MongoDB + Flask Web UI</b>", table_cell),
            Paragraph("Saves document to MongoDB. Dashboard updates live with interactive transcript tabs (Original, Gujarati, English), audio player, badges, and analytics.", table_cell),
            Paragraph("Interactive Dashboard Card &amp; Admin Metrics", table_cell)
        ]
    ]
    pipeline_table = Table(pipeline_data, colWidths=[80, 115, 205, 132])
    pipeline_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SECONDARY),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(pipeline_table)
    story.append(Spacer(1, 10))

    # ==========================
    # 3. TECHNOLOGIES & TOOLS USED ("THINGS USE")
    # ==========================
    story.append(Paragraph("3. Technologies &amp; Tools Used ('Things Used')", h1_style))
    story.append(Paragraph(
        "CallSense is engineered with modern, production-grade tools chosen for performance, reliability, and cost-efficiency:",
        body_style
    ))

    tech_data = [
        [
            Paragraph("Category", table_header),
            Paragraph("Technology / Library", table_header),
            Paragraph("Role &amp; Why It Was Selected", table_header)
        ],
        [
            Paragraph("<b>Web Framework</b>", table_cell_bold),
            Paragraph("<b>Python 3.10+ &amp; Flask 3.0</b>", table_cell),
            Paragraph("Lightweight, robust Python WSGI web framework. Provides clean REST routing, modular blueprints, session management, and Jinja2 templating.", table_cell)
        ],
        [
            Paragraph("<b>Database</b>", table_cell_bold),
            Paragraph("<b>MongoDB Community / Compass (PyMongo)</b>", table_cell),
            Paragraph("NoSQL document database perfect for variable-length transcripts, nested confidence breakdown arrays, and flexible call metadata schemas.", table_cell)
        ],
        [
            Paragraph("<b>Speech-to-Text</b>", table_cell_bold),
            Paragraph("<b>Whisper large-v3 via Groq Cloud API</b>", table_cell),
            Paragraph("State-of-the-art multilingual speech model running on Groq LPU chips. Delivers speech transcription up to 10x faster than local CPU inference with zero hardware cost.", table_cell)
        ],
        [
            Paragraph("<b>LLM &amp; Reasoning</b>", table_cell_bold),
            Paragraph("<b>OpenAI GPT-OSS / LLaMA (Groq Cloud)</b>", table_cell),
            Paragraph("High-speed conversational LLM for instant classification, structured JSON extraction, motive summarization, and natural Gujarati/English translation.", table_cell)
        ],
        [
            Paragraph("<b>Audio Processing</b>", table_cell_bold),
            Paragraph("<b>FFmpeg, PyDub, NoiseReduce, NumPy</b>", table_cell),
            Paragraph("Professional acoustic DSP tools for noise suppression, voice band-pass filtering, loudness normalization, and WebM/WAV/MP3 format conversions.", table_cell)
        ],
        [
            Paragraph("<b>Frontend &amp; UI</b>", table_cell_bold),
            Paragraph("<b>Vanilla CSS3, HTML5, Web Audio API</b>", table_cell),
            Paragraph("Glassmorphic, responsive design with zero heavy frontend dependencies. Uses browser <code>MediaRecorder</code> for live microphone recording directly in the browser.", table_cell)
        ],
        [
            Paragraph("<b>Security &amp; Auth</b>", table_cell_bold),
            Paragraph("<b>Werkzeug Security &amp; Python-Dotenv</b>", table_cell),
            Paragraph("Secure PBKDF2/SHA256 password hashing, user session authorization, role-based admin controls, and isolated environment variables in <code>.env</code>.", table_cell)
        ]
    ]
    tech_table = Table(tech_data, colWidths=[100, 140, 292])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(tech_table)
    story.append(Spacer(1, 10))

    # ==========================
    # 4. KEY FEATURES & CAPABILITIES
    # ==========================
    story.append(Paragraph("4. Key Features &amp; Capabilities", h1_style))

    features_data = [
        [
            Paragraph("<b>Multi-Lingual Accuracy (Hindi / Gujarati / English)</b><br/>"
                      "Prevents incorrect script transliteration. Hindi speech is recorded in clean Devanagari script, Gujarati in Gujarati script, and English in Latin script. Code-mixed calls (Hinglish/Gujlish) are handled seamlessly.", body_style),
            Paragraph("<b>Instant Gujarati &amp; English Translations</b><br/>"
                      "Every non-Gujarati call gets a fluent, grammatically correct <b>Gujarati Translation (ગુજરાતી અનુવાદ)</b>, and non-English calls get an <b>English Translation</b> accessible via simple tabs.", body_style)
        ],
        [
            Paragraph("<b>Live Call Recording via Microphone</b><br/>"
                      "Agents or testers can put any customer call on speaker, click 'Start Recording' in the browser, listen back to the preview, and process it immediately without uploading pre-recorded files.", body_style),
            Paragraph("<b>Explainable Confidence Breakdown</b><br/>"
                      "Rather than showing an arbitrary percentage, the system analyzes segments and pinpoints missing confidence: Background Noise, Unclear Speech, Garbled Audio, or Language Ambiguity.", body_style)
        ],
        [
            Paragraph("<b>Comprehensive Call Extraction</b><br/>"
                      "Extracts Customer Name, Support Agent Name, 10-digit Phone Numbers (via deterministic regex), Key Issues Raised, Action Items committed, and whether Follow-up is required.", body_style),
            Paragraph("<b>Admin Control &amp; System-Wide Analytics</b><br/>"
                      "Admins have dedicated panels to view system-wide charts, category/sentiment distributions, user management (promote/demote admin, delete users), and global inspection of all calls.", body_style)
        ]
    ]
    features_table = Table(features_data, colWidths=[260, 260])
    features_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FAF5FF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#E9D5FF")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#F3E8FF")),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(features_table)
    story.append(Spacer(1, 10))

    # ==========================
    # 5. PROJECT STRUCTURE & HOW TO RUN
    # ==========================
    story.append(Paragraph("5. Project Directory Structure &amp; Quick Start Guide", h1_style))

    struct_text = (
        "<b>Folder Organization:</b><br/>"
        "• <code>app.py</code>: Main Flask application, authentication, web routes, and session handlers.<br/>"
        "• <code>config.py</code>: Central configuration loading environment variables from <code>.env</code>.<br/>"
        "• <code>services/pipeline.py</code>: Master orchestrator coordinating stages 1 through 4.<br/>"
        "• <code>services/transcription_service.py</code>: Whisper client with auto-detection and confidence scoring.<br/>"
        "• <code>services/llm_service.py</code>: LLM classification, data extraction, and dual translations.<br/>"
        "• <code>services/audio_processing.py</code>: Noise reduction and bandpass filter DSP helpers.<br/>"
        "• <code>services/db.py &amp; auth_service.py</code>: MongoDB collections and password hashing logic.<br/>"
        "• <code>templates/ &amp; static/</code>: Responsive UI templates (Dashboard, Admin, Auth) and CSS styling."
    )
    story.append(Paragraph(struct_text, body_style))

    setup_data = [
        [
            Paragraph("<b>Step 1: Install Requirements</b><br/><code>source venv/bin/activate<br/>pip install -r requirements.txt</code>", table_cell),
            Paragraph("<b>Step 2: Configure Environment (.env)</b><br/><code>GROQ_API_KEY=your_key_here<br/>MONGO_URI=mongodb://localhost:27017</code>", table_cell),
            Paragraph("<b>Step 3: Launch Application</b><br/><code>python app.py<br/>Open: http://127.0.0.1:5000</code>", table_cell)
        ]
    ]
    setup_table = Table(setup_data, colWidths=[174, 184, 174])
    setup_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_LIGHT),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(setup_table)
    story.append(Spacer(1, 10))

    # Summary footer note
    story.append(Paragraph(
        "<b>Summary:</b> CallSense provides a complete, modern, and production-ready solution for customer speech analytics, "
        "bridging the gap between multi-lingual audio and business intelligence with zero expensive infrastructure.",
        callout_style
    ))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    return output_path

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "CallSense_Project_Guide.pdf"
    res = create_project_pdf(out_file)
    print(f"PDF successfully generated at: {os.path.abspath(res)}")
