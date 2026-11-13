"""
Script to generate CallSense_Dashboard_Analytics_and_Exports_Guide.pdf
Comprehensive technical guide answering:
1. How counts (totals) are calculated
2. How to upload work records (audio data files)
3. How to import library files and install a library by name
4. How the AI summary is generated
5. How to share call records with others
6. How to add Excel and PDF export functionality
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
            self.drawString(40, 755, "CallSense — Dashboard Analytics, Processing & Export Architecture Guide")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, 747, 572, 747)

        # Running footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 25, page_str)
        self.drawString(40, 25, "CallSense Technical Documentation — Confidential & Educational")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 36, 572, 36)
        self.restoreState()


def build_pdf(output_path="CallSense_Dashboard_Analytics_and_Exports_Guide.pdf"):
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
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0284C7"),
        spaceBefore=13,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SecH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14.5,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=8,
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
        spaceAfter=4
    )

    story = []

    # Title Banner
    story.append(Paragraph("CallSense Dashboard & Processing Guide", title_style))
    story.append(Paragraph("<b>Calculations, Upload Pipeline, Library Management, AI Summaries, Sharing & Exports</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284C7"), spaceBefore=0, spaceAfter=10))

    # =========================================================================
    # SECTION 1: HOW COUNTS ARE CALCULATED
    # =========================================================================
    story.append(Paragraph("1. How Dashboard Counts (Totals) are Calculated", h1_style))
    story.append(Paragraph(
        "CallSense computes real-time analytics from documents in MongoDB. "
        "User dashboard metrics are calculated dynamically in <code>app.py</code> via <code>_compute_stats(calls)</code>:",
        body_style
    ))

    calc_code = (
        "def _compute_stats(calls):\n"
        "    completed = [c for c in calls if c.get('status') == 'completed']\n"
        "    stats = {\n"
        "        'total': len(calls),                  # Total uploaded recordings\n"
        "        'completed': len(completed),          # Successfully transcribed & analyzed\n"
        "        'avg_confidence': None,               # Average accuracy percentage\n"
        "        'avg_time': None,                     # Average processing time (seconds)\n"
        "        'languages': [],                      # Unique detected languages list\n"
        "    }\n"
        "    if completed:\n"
        "        confidences = [c['confidence_percent'] for c in completed if c.get('confidence_percent') is not None]\n"
        "        times = [c['total_time_seconds'] for c in completed if c.get('total_time_seconds') is not None]\n"
        "        languages = sorted({c['language'] for c in completed if c.get('language')})\n"
        "        stats['avg_confidence'] = round(sum(confidences) / len(confidences), 1) if confidences else None\n"
        "        stats['avg_time'] = round(sum(times) / len(times), 1) if times else None\n"
        "        stats['languages'] = languages\n"
        "    return stats"
    )
    t_calc = Table([[Paragraph(f"<pre>{calc_code}</pre>", code_style)]], colWidths=[532])
    t_calc.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_calc)

    story.append(Spacer(1, 3))
    story.append(Paragraph("&bull; <b>Calls Processed:</b> Compares completed calls against total records: <code>stats.completed / stats.total</code>.", bullet_style))
    story.append(Paragraph("&bull; <b>Overall Accuracy (%):</b> Calculates the mathematical mean of Whisper transcription confidence scores across all completed calls.", bullet_style))
    story.append(Paragraph("&bull; <b>Average Time / Call:</b> Measures total elapsed seconds from audio upload through AI LLM analysis.", bullet_style))
    story.append(Paragraph("&bull; <b>Admin Overview Stats:</b> In <code>services/admin_service.py</code>, aggregates system-wide counts across every user (total users, category breakdown, sentiment distribution, priority levels).", bullet_style))

    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 2: HOW TO UPLOAD WORK RECORDS
    # =========================================================================
    story.append(Paragraph("2. How to Upload Work Records (Audio Data Files)", h1_style))
    story.append(Paragraph(
        "CallSense accepts audio recordings in <code>.mp3</code>, <code>.wav</code>, <code>.m4a</code>, <code>.ogg</code>, and <code>.webm</code> formats.",
        body_style
    ))

    story.append(Paragraph("A. Upload Form Interface (<code>templates/dashboard.html</code>)", h2_style))
    html_upload = (
        "&lt;form method=\"POST\" action=\"{{ url_for('upload_call') }}\" enctype=\"multipart/form-data\"&gt;\n"
        "  &lt;input type=\"file\" name=\"audio_file\" accept=\".mp3,.wav,.m4a,.ogg,.webm\" required&gt;\n"
        "  &lt;select name=\"language\"&gt;\n"
        "    &lt;option value=\"auto\" selected&gt;Auto Detect (Hindi / Gujarati / English)&lt;/option&gt;\n"
        "    &lt;option value=\"hi\"&gt;Hindi&lt;/option&gt;\n"
        "    &lt;option value=\"gu\"&gt;Gujarati&lt;/option&gt;\n"
        "    &lt;option value=\"en\"&gt;English&lt;/option&gt;\n"
        "  &lt;/select&gt;\n"
        "  &lt;button type=\"submit\"&gt;Process Call&lt;/button&gt;\n"
        "&lt;/form&gt;"
    )
    t_html = Table([[Paragraph(f"<pre>{html_upload}</pre>", code_style)]], colWidths=[532])
    t_html.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_html)

    story.append(Spacer(1, 3))
    story.append(Paragraph("B. Server-Side Handling Workflow (<code>app.py</code> & <code>services/pipeline.py</code>)", h2_style))
    story.append(Paragraph("1. <b>File Extraction & Security:</b> <code>file = request.files['audio_file']</code> &rarr; sanitized via <code>secure_filename(file.filename)</code>.", bullet_style))
    story.append(Paragraph("2. <b>Storage:</b> Written to disk in the <code>uploads/</code> directory.", bullet_style))
    story.append(Paragraph("3. <b>Database Tracking:</b> Inserts a placeholder document into MongoDB with status <code>'uploaded'</code>.", bullet_style))
    story.append(Paragraph("4. <b>Pipeline Execution:</b> <code>pipeline.run_pipeline()</code> launches noise reduction, Whisper Large V3 transcription, and LLM classification.", bullet_style))

    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 3: HOW TO INSTALL AND IMPORT LIBRARIES
    # =========================================================================
    story.append(Paragraph("3. How to Install and Import Python Libraries", h1_style))
    story.append(Paragraph(
        "Python packages are installed via <code>pip</code> within the project's virtual environment (<code>venv</code>).",
        body_style
    ))

    story.append(Paragraph("A. Terminal Commands for Installing Libraries", h2_style))
    pip_cmd = (
        "# 1. Install any library by name (e.g. openpyxl, reportlab, pandas):\n"
        "./venv/bin/pip install openpyxl reportlab\n\n"
        "# 2. Save installed packages to requirements.txt:\n"
        "./venv/bin/pip freeze > requirements.txt\n\n"
        "# 3. Install all project dependencies at once:\n"
        "./venv/bin/pip install -r requirements.txt"
    )
    t_pip = Table([[Paragraph(f"<pre>{pip_cmd}</pre>", code_style)]], colWidths=[532])
    t_pip.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_pip)

    story.append(Spacer(1, 3))
    story.append(Paragraph("B. Import Syntax in Python Source Files", h2_style))
    story.append(Paragraph("&bull; <b>Standard Library:</b> <code>import os</code>, <code>import smtplib</code>, <code>import secrets</code>, <code>import csv</code>.", bullet_style))
    story.append(Paragraph("&bull; <b>Third-Party Libraries:</b> <code>from flask import Flask, render_template</code>, <code>from pymongo import MongoClient</code>, <code>from reportlab.platypus import SimpleDocTemplate</code>.", bullet_style))
    story.append(Paragraph("&bull; <b>Internal Project Modules:</b> <code>from config import Config</code>, <code>from services.db import get_calls_collection</code>, <code>from services import email_service</code>.", bullet_style))

    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 4: HOW AI SUMMARY IS GENERATED
    # =========================================================================
    story.append(Paragraph("4. How the AI Summary is Generated", h1_style))
    story.append(Paragraph(
        "Summaries and analytics are generated in <code>services/llm_service.py</code> using Groq Cloud's ultra-fast LLM API "
        "(<code>openai/gpt-oss-120b</code> or LLaMA 3.3):",
        body_style
    ))

    llm_flow_data = [
        [Paragraph("<b>Step</b>", body_style), Paragraph("<b>Component</b>", body_style), Paragraph("<b>Operation Description</b>", body_style)],
        [Paragraph("1. Transcript Input", body_style), Paragraph("<code>services/transcription_service.py</code>", code_style), Paragraph("Whisper Large V3 outputs complete conversation transcript with timestamps.", body_style)],
        [Paragraph("2. Prompt Assembly", body_style), Paragraph("<code>services/llm_service.py</code>", code_style), Paragraph("Injects transcript into a detailed system prompt demanding structured JSON.", body_style)],
        [Paragraph("3. LLM Inference", body_style), Paragraph("Groq Cloud API", code_style), Paragraph("Analyzes conversation nuances, speaker sentiments, and key issues.", body_style)],
        [Paragraph("4. JSON Parsing", body_style), Paragraph("<code>extract_json_response()</code>", code_style), Paragraph("Extracts: <code>summary</code>, <code>category</code>, <code>sentiment</code>, <code>priority</code>, <code>action_items</code>.", body_style)],
        [Paragraph("5. Persistence", body_style), Paragraph("MongoDB <code>calls</code>", code_style), Paragraph("Updates document atomically with summary and metadata.", body_style)],
    ]
    t_llm = Table(llm_flow_data, colWidths=[90, 160, 282])
    t_llm.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_llm)

    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 5: HOW SHARING WORKS
    # =========================================================================
    story.append(Paragraph("5. How to Share Call Records with Others", h1_style))
    story.append(Paragraph(
        "CallSense allows team members to share call analytics while protecting sensitive data:",
        body_style
    ))
    story.append(Paragraph("1. User clicks <b>Share</b> on any completed call card in the dashboard.", bullet_style))
    story.append(Paragraph("2. Selects a registered user from the searchable modal (backed by <code>/api/users/shareable</code>).", bullet_style))
    story.append(Paragraph("3. <code>services/share_service.py</code> pushes a <code>ShareEntry</code> into the call's <code>shared_with</code> array in MongoDB.", bullet_style))
    story.append(Paragraph("4. Automatically dispatches a branded notification email to the recipient's registered address via <code>email_service.send_call_shared_email()</code>.", bullet_style))
    story.append(Paragraph("5. <b>Privacy Protection:</b> Private call transcripts, audio recordings, and phone numbers are strictly excluded from the notification email.", bullet_style))
    story.append(Paragraph("6. Recipient accesses the call securely from their authenticated <b>Shared With Me</b> dashboard tab.", bullet_style))

    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 6: HOW TO ADD EXCEL AND PDF EXPORTS (PRODUCTION-READY & SECURE)
    # =========================================================================
    story.append(Paragraph("6. Production-Ready Excel (.xlsx) and PDF Exports (Bugs Solved)", h1_style))
    story.append(Paragraph(
        "The initial export draft contained four critical bugs which have been completely resolved in the production codebase:",
        body_style
    ))
    story.append(Paragraph("&bull; <b>Security Bug Solved:</b> The route previously fetched any call by ID without checking user ownership or sharing. Access control now verifies that the caller is the call owner, an administrator, or an authorized shared recipient.", bullet_style))
    story.append(Paragraph("&bull; <b>Missing 404 Handling Solved:</b> Previously, an invalid ID or deleted call caused a 500 crash on <code>call.get(...)</code> because <code>call</code> was <code>None</code>. Now, <code>ObjectId</code> validation is wrapped in a try/except block, and missing records redirect gracefully with an informative error.", bullet_style))
    story.append(Paragraph("&bull; <b>Privacy Mismatch Solved:</b> CallSense sharing strictly protects customer phone numbers and audio transcripts. The export now implements role-based privacy redaction: call owners and admins receive the <b>Full Executive Audit Report</b> with complete transcripts, while shared recipients receive an <b>Analytics Summary Report</b> with raw transcripts and contact numbers redacted.", bullet_style))
    story.append(Paragraph("&bull; <b>True Excel Formatting Solved:</b> Rather than disguising CSV as Excel, the system now utilizes <code>openpyxl</code> to generate authentic, styled <code>.xlsx</code> workbooks featuring deep navy headers, auto-adjusted column dimensions, text wrapping, and alternating zebra row striping.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("A. True Excel (.xlsx) Export via <code>openpyxl</code> (in <code>services/export_service.py</code>)", h2_style))
    excel_code = (
        "import openpyxl, io\n"
        "from openpyxl.styles import Font, PatternFill, Alignment, Border, Side\n\n"
        "def generate_calls_excel(calls_list, requester_username='User'):\n"
        "    wb = openpyxl.Workbook()\n"
        "    ws = wb.active\n"
        "    ws.title = 'Call Analytics'\n"
        "    # Styled Header & Zebra Rows:\n"
        "    headers = ['File Name', 'Uploaded Date', 'Status', 'Language', 'Customer Name',\n"
        "               'Agent Name', 'Category', 'Sentiment', 'Priority', 'Resolution',\n"
        "               'Confidence (%)', 'Duration (s)', 'Summary', 'Key Issues', 'Action Items']\n"
        "    ws.append(headers)\n"
        "    for call in calls_list:\n"
        "        ws.append([call.get('filename'), str(call.get('created_at')), call.get('status'),\n"
        "                   call.get('language'), call.get('customer_name'), call.get('agent_name'),\n"
        "                   call.get('category'), call.get('sentiment'), call.get('priority'),\n"
        "                   call.get('resolution_status'), call.get('confidence_percent'),\n"
        "                   call.get('audio_duration_seconds'), call.get('summary'),\n"
        "                   '; '.join(call.get('key_issues', [])), '; '.join(call.get('action_items', []))])\n"
        "    # Auto-adjust column widths:\n"
        "    for col in ws.columns:\n"
        "        ws.column_dimensions[col[0].column_letter].width = max(len(str(cell.value or '')) for cell in col) + 4\n"
        "    buffer = io.BytesIO()\n"
        "    wb.save(buffer)\n"
        "    buffer.seek(0)\n"
        "    return buffer"
    )
    t_excel = Table([[Paragraph(f"<pre>{excel_code}</pre>", code_style)]], colWidths=[532])
    t_excel.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_excel)

    story.append(Spacer(1, 4))
    story.append(Paragraph("B. Secure PDF Export Route with 404, Security &amp; Privacy Redaction (in <code>app.py</code>)", h2_style))
    pdf_code = (
        "@app.route('/call/<call_id>/export/pdf')\n"
        "@login_required\n"
        "def export_call_pdf(call_id):\n"
        "    # 1. 404 Handling: Safe ObjectId validation\n"
        "    try:\n"
        "        call_oid = ObjectId(call_id)\n"
        "    except Exception:\n"
        "        flash('Invalid call ID specified.', 'error')\n"
        "        return redirect(url_for('dashboard'))\n\n"
        "    call = get_calls_collection().find_one({'_id': call_oid})\n"
        "    if not call:\n"
        "        flash('Call record was not found.', 'error')\n"
        "        return redirect(url_for('dashboard'))\n\n"
        "    # 2. Security Bug Check: Verify ownership, admin, or shared status\n"
        "    user_id = str(session['user_id'])\n"
        "    is_admin = (session.get('role') == 'admin')\n"
        "    is_owner = (str(call.get('uploaded_by')) == user_id)\n"
        "    is_shared = any(str(s.get('user_id')) == user_id for s in call.get('shared_with', []))\n\n"
        "    if not (is_owner or is_admin or is_shared):\n"
        "        flash('Access denied: You do not have permission to export this call.', 'error')\n"
        "        return redirect(url_for('dashboard'))\n\n"
        "    # 3. Privacy Redaction: Owner/Admin gets full transcripts; Shared gets redacted summary\n"
        "    pdf_buffer = generate_single_call_pdf(call, requester_id=user_id, is_admin=is_admin)\n"
        "    filename = f\"{call.get('filename')}_report.pdf\"\n"
        "    return Response(pdf_buffer.getvalue(), mimetype='application/pdf',\n"
        "                    headers={'Content-Disposition': f'attachment; filename=\"{filename}\"'})"
    )
    t_pdf = Table([[Paragraph(f"<pre>{pdf_code}</pre>", code_style)]], colWidths=[532])
    t_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_pdf)

    story.append(Spacer(1, 3))
    story.append(Paragraph("C. Dashboard Integration in <code>templates/dashboard.html</code>", h2_style))
    story.append(Paragraph("The dashboard features a global <b>Export Excel (.xlsx)</b> button above the call tabs, and an individual <b>PDF</b> download button on every completed call card for instant, secure reporting.", bullet_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated PDF successfully at: {output_path}")


if __name__ == "__main__":
    out = "CallSense_Dashboard_Analytics_and_Exports_Guide.pdf"
    if len(sys.argv) > 1:
        out = sys.argv[1]
    build_pdf(out)
