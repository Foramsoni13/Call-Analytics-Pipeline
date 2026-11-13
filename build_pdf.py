#!/usr/bin/env python3
"""
Builds CallSense_Research_Paper_IEEE.pdf
Zero italics anywhere. All fonts in regular Times-Roman (or bold for titles and headings).
"""

import os
import sys
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, FrameBreak,
    NextPageTemplate, Table, TableStyle, Image, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

import paper_text as pt

def sanitize_rl(text):
    if not isinstance(text, str):
        text = str(text)
    # Remove any stray italic tags
    text = text.replace('<i>', '').replace('</i>', '')
    
    tokens = {}
    valid_tags = ['<b>', '</b>', '<sup>', '</sup>', '<sub>', '</sub>', '<br/>']
    for idx, tag in enumerate(valid_tags):
        token = f"___TAG_{idx}___"
        tokens[token] = tag
        text = text.replace(tag, token)
        
    text = re.sub(r'&(?!(amp|lt|gt);)', '&amp;', text)
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    for token, tag in tokens.items():
        text = text.replace(token, tag)
    return text

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
            self.draw_header_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Times-Roman", 7.5)
        self.setFillColor(colors.HexColor("#475569"))
        
        # Header
        if self._pageNumber == 1:
            self.drawString(54, 750, "IEEE RESEARCH ARCHIVE — MASTER OF COMPUTER APPLICATIONS (MCA) PROJECT — 2026")
            self.setStrokeColor(colors.HexColor("#94A3B8"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
        else:
            self.drawString(54, 750, "CALLSENSE: MULTILINGUAL TELEPHONY CALL ANALYTICS PIPELINE")
            self.drawRightString(558, 750, f"PAGE {self._pageNumber} OF {page_count}")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)

        # Footer
        self.drawString(54, 30, "MCA ACADEMIC SUBMISSION — FORAM SONI")
        self.drawRightString(558, 30, f"{self._pageNumber}")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 38, 558, 38)
        self.restoreState()

def generate_ieee_pdf(output_path="CallSense_Research_Paper_IEEE.pdf"):
    print("Generating non-italic simple PDF document...")
    doc = BaseDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    # Printable width: 504 pt. Printable height: 684 pt.
    # Column width: (504 - 18) / 2 = 243 pt. Col 1 x=54, Col 2 x=315.
    frame_top = Frame(54, 598, 504, 140, id='F_top', topPadding=0, bottomPadding=0, leftPadding=0, rightPadding=0)
    frame_p1_l = Frame(54, 54, 243, 534, id='F_p1_left', topPadding=0, bottomPadding=0, leftPadding=0, rightPadding=0)
    frame_p1_r = Frame(315, 54, 243, 534, id='F_p1_right', topPadding=0, bottomPadding=0, leftPadding=0, rightPadding=0)

    frame_l = Frame(54, 54, 243, 678, id='F_left', topPadding=0, bottomPadding=0, leftPadding=0, rightPadding=0)
    frame_r = Frame(315, 54, 243, 678, id='F_right', topPadding=0, bottomPadding=0, leftPadding=0, rightPadding=0)

    first_page = PageTemplate(id='FirstPage', frames=[frame_top, frame_p1_l, frame_p1_r])
    later_pages = PageTemplate(id='LaterPages', frames=[frame_l, frame_r])
    doc.addPageTemplates([first_page, later_pages])

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        fontName='Times-Bold',
        fontSize=16,
        leading=19,
        alignment=1, # Centered
        spaceAfter=6
    )
    
    author_style = ParagraphStyle(
        'DocAuthor',
        fontName='Times-Roman',
        fontSize=9,
        leading=11.5,
        alignment=1 # Centered
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        fontName='Times-Roman', # NO ITALICS
        fontSize=8.2,
        leading=10.2,
        alignment=4, # Justified
        spaceAfter=4
    )
    
    sec_head_style = ParagraphStyle(
        'DocSecHead',
        fontName='Times-Bold',
        fontSize=9,
        leading=11,
        alignment=1, # Centered
        spaceBefore=8,
        spaceAfter=3
    )
    
    subsec_head_style = ParagraphStyle(
        'DocSubSecHead',
        fontName='Times-Bold', # NO ITALICS
        fontSize=8.5,
        leading=10.5,
        alignment=0, # Left
        spaceBefore=6,
        spaceAfter=2
    )

    abs_style = ParagraphStyle(
        'DocAbstract',
        fontName='Times-Roman', # NO ITALICS
        fontSize=8,
        leading=9.8,
        alignment=4, # Justified
        spaceAfter=4
    )
    
    eq_style = ParagraphStyle(
        'DocEquation',
        fontName='Times-Roman', # NO ITALICS
        fontSize=8,
        leading=10,
        alignment=1 # Centered
    )

    code_style = ParagraphStyle(
        'DocCode',
        fontName='Courier',
        fontSize=6.5,
        leading=8,
        alignment=0
    )

    ref_style = ParagraphStyle(
        'DocRef',
        fontName='Times-Roman', # NO ITALICS
        fontSize=7,
        leading=8.5,
        alignment=4,
        leftIndent=12,
        firstLineIndent=-12,
        spaceAfter=2.5
    )

    caption_style = ParagraphStyle(
        'DocCaption',
        fontName='Times-Roman', # NO ITALICS
        fontSize=7.5,
        leading=9,
        alignment=1,
        spaceBefore=2,
        spaceAfter=4
    )

    story = []

    # 1. Title Block (in F_top)
    story.append(Paragraph(sanitize_rl(pt.TITLE), title_style))
    story.append(Spacer(1, 4))
    
    auth_html = (
        f"<b>{pt.AUTHOR_NAME}</b><br/>"
        "Department of Computer Applications, Faculty of Technology &amp; Computer Applications<br/>"
        "Master of Computer Applications (MCA)<br/>"
        "Email: foramsoni2004@gmail.com"
    )
    story.append(Paragraph(auth_html, author_style))
    story.append(FrameBreak()) # Move to Left Column of Page 1
    story.append(NextPageTemplate('LaterPages'))

    # Abstract & Index Terms in Column 1 (Plain Regular Font, NO ITALICS)
    story.append(Paragraph(f"<b>Abstract—</b>{sanitize_rl(pt.ABSTRACT)}", abs_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph(f"<b>Index Terms—</b>{sanitize_rl(', '.join(pt.KEYWORDS))}", abs_style))
    story.append(Spacer(1, 4))

    # SECTION I: INTRODUCTION
    story.append(Paragraph(sanitize_rl(pt.SEC_I_TITLE), sec_head_style))
    for p_text in pt.SEC_I_BODY:
        story.append(Paragraph(sanitize_rl(p_text), body_style))

    # SECTION II: BACKGROUND AND MOTIVATION
    story.append(Paragraph(sanitize_rl(pt.SEC_II_TITLE), sec_head_style))
    for sub_title, sub_paras in pt.SEC_II_BODY:
        story.append(Paragraph(sanitize_rl(sub_title), subsec_head_style))
        for p_text in sub_paras:
            story.append(Paragraph(sanitize_rl(p_text), body_style))

    # SECTION III: LITERATURE REVIEW
    story.append(Paragraph(sanitize_rl(pt.SEC_III_TITLE), sec_head_style))
    for sub_title, sub_paras in pt.SEC_III_BODY:
        story.append(Paragraph(sanitize_rl(sub_title), subsec_head_style))
        for p_text in sub_paras:
            story.append(Paragraph(sanitize_rl(p_text), body_style))

    # SECTION IV: RESEARCH GAP
    story.append(Paragraph(sanitize_rl(pt.SEC_IV_TITLE), sec_head_style))
    for p_text in pt.SEC_IV_BODY:
        story.append(Paragraph(sanitize_rl(p_text), body_style))

    # SECTION V: PROBLEM STATEMENT
    story.append(Paragraph(sanitize_rl(pt.SEC_V_TITLE), sec_head_style))
    story.append(Paragraph(sanitize_rl(pt.SEC_V_BODY[0]), body_style))
    
    # Equation 1 (NO ITALICS)
    eq1_data = [[Paragraph("y(t) = [x(t) * h(t)] + η(t)", eq_style), Paragraph("(1)", eq_style)]]
    t_eq1 = Table(eq1_data, colWidths=[200, 35])
    t_eq1.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(t_eq1)
    
    story.append(Paragraph(sanitize_rl(pt.SEC_V_BODY[2]), body_style))
    story.append(Paragraph(sanitize_rl(pt.SEC_V_BODY[3]), body_style))
    
    # Equation 2 (NO ITALICS)
    eq2_data = [[Paragraph("M = ⟨Language, Transcript, Sentiment, Category, Priority, Resolution, Phone_Numbers, Action_Items, Translations⟩", eq_style), Paragraph("(2)", eq_style)]]
    t_eq2 = Table(eq2_data, colWidths=[205, 30])
    t_eq2.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(t_eq2)
    
    for p_text in pt.SEC_V_BODY[5:]:
        story.append(Paragraph(sanitize_rl(p_text), body_style))

    # SECTION VI: RESEARCH OBJECTIVES
    story.append(Paragraph(sanitize_rl(pt.SEC_VI_TITLE), sec_head_style))
    for p_text in pt.SEC_VI_BODY:
        story.append(Paragraph(sanitize_rl(p_text), body_style))

    # Helper for adding tables in PDF
    def format_pdf_table(tbl_dict, col_w=None):
        cap = Paragraph(sanitize_rl(f"<b>{tbl_dict['caption']}</b>"), caption_style)
        headers = [Paragraph(sanitize_rl(f"<b>{h}</b>"), ParagraphStyle('TH', fontName='Times-Bold', fontSize=6.5, leading=7.5, alignment=1)) for h in tbl_dict['headers']]
        data = [headers]
        for row in tbl_dict['rows']:
            r_data = []
            for j, val in enumerate(row):
                align = 0 if j <= 1 else 1
                p_val = Paragraph(sanitize_rl(str(val)), ParagraphStyle('TD', fontName='Times-Roman', fontSize=6.5, leading=7.5, alignment=align))
                r_data.append(p_val)
            data.append(r_data)
        
        if not col_w:
            w_each = 235 / len(headers)
            col_w = [w_each] * len(headers)
            
        t = Table(data, colWidths=col_w)
        t_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('LINEABOVE', (0, 0), (-1, 0), 1.0, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 0.7, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 1.0, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#CBD5E1')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]
        t.setStyle(TableStyle(t_style))
        return KeepTogether([cap, t, Spacer(1, 4)])

    def format_pdf_algo(algo_dict):
        title_p = Paragraph(sanitize_rl(f"<b>Algorithm {algo_dict['num']}: {algo_dict['title']}</b>"), ParagraphStyle('AT', fontName='Times-Bold', fontSize=7.5, leading=9))
        rows = []
        for step in algo_dict['steps']:
            rows.append([Paragraph(sanitize_rl(step), code_style)])
        t = Table(rows, colWidths=[235])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#475569')),
            ('TOPPADDING', (0,0), (-1,-1), 1),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ]))
        return KeepTogether([title_p, Spacer(1, 2), t, Spacer(1, 4)])

    # SECTION VII: PROPOSED METHODOLOGY
    story.append(Paragraph(sanitize_rl(pt.SEC_VII_TITLE), sec_head_style))
    for sub_title, sub_paras in pt.SEC_VII_BODY:
        story.append(Paragraph(sanitize_rl(sub_title), subsec_head_style))
        for p_text in sub_paras:
            if "H(z) =" in p_text:
                story.append(Paragraph("The high-pass filter equation is written as:", body_style))
                t_eq = Table([[Paragraph("H(z) = (1 - z<sup>-1</sup>) / (1 - α·z<sup>-1</sup>)", eq_style), Paragraph("(3)", eq_style)]], colWidths=[200, 35])
                t_eq.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
                story.append(t_eq)
            elif "E_dBFS(m) =" in p_text:
                story.append(Paragraph("The sound energy in decibels is calculated as:", body_style))
                t_eq = Table([[Paragraph("E<sub>dBFS</sub>(m) = 10·log<sub>10</sub>[ (1/N · Σ x<sup>2</sup>) / X<sub>max</sub><sup>2</sup> ]", eq_style), Paragraph("(4)", eq_style)]], colWidths=[200, 35])
                t_eq.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
                story.append(t_eq)
            elif "C_ASR =" in p_text:
                story.append(Paragraph("The confidence percentage score is defined as:", body_style))
                t_eq = Table([[Paragraph("C<sub>ASR</sub> = exp( 1/|S| · Σ l̄<sub>s</sub> ) × 100%", eq_style), Paragraph("(5)", eq_style)]], colWidths=[200, 35])
                t_eq.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
                story.append(t_eq)
            elif "P_regex =" in p_text:
                story.append(Paragraph("The regular expression pattern for phone numbers is:", body_style))
                t_eq = Table([[Paragraph("P<sub>regex</sub> = (?&lt;!\\d)(\\d{10})(?!\\d)", eq_style), Paragraph("(6)", eq_style)]], colWidths=[200, 35])
                t_eq.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
                story.append(t_eq)
            else:
                story.append(Paragraph(sanitize_rl(p_text), body_style))

    # SECTION VIII: SYSTEM ARCHITECTURE AND WORKFLOW
    story.append(Paragraph(sanitize_rl(pt.SEC_VIII_TITLE), sec_head_style))
    if os.path.exists("paper_assets/fig_architecture.png"):
        img = Image("paper_assets/fig_architecture.png", width=235, height=130)
        cap = Paragraph("<b>Fig. 1. CallSense end-to-end system architecture and dataflow pipeline.</b>", caption_style)
        story.append(KeepTogether([img, cap]))
    for p_text in pt.SEC_VIII_BODY:
        story.append(Paragraph(sanitize_rl(p_text), body_style))

    # SECTION IX: TECHNOLOGIES USED
    story.append(Paragraph(sanitize_rl(pt.SEC_IX_TITLE), sec_head_style))
    story.append(format_pdf_table(pt.TABLE_I, col_w=[50, 55, 45, 85]))
    for p_text in pt.SEC_IX_BODY:
        story.append(Paragraph(sanitize_rl(p_text), body_style))

    # SECTION X: IMPLEMENTATION DETAILS
    story.append(Paragraph(sanitize_rl(pt.SEC_X_TITLE), sec_head_style))
    for sub_title, sub_paras in pt.SEC_X_BODY:
        story.append(Paragraph(sanitize_rl(sub_title), subsec_head_style))
        for p_text in sub_paras:
            story.append(Paragraph(sanitize_rl(p_text), body_style))
            if "Algorithm 1" in p_text:
                story.append(format_pdf_algo(pt.ALGORITHM_1))
            elif "Algorithm 2" in p_text:
                story.append(format_pdf_algo(pt.ALGORITHM_2))

    # SECTION XI: EXPERIMENTAL RESULTS AND ANALYSIS
    story.append(Paragraph(sanitize_rl(pt.SEC_XI_TITLE), sec_head_style))
    for sub_title, sub_paras in pt.SEC_XI_BODY:
        story.append(Paragraph(sanitize_rl(sub_title), subsec_head_style))
        for p_text in sub_paras:
            if "WER =" in p_text:
                t_eq = Table([[Paragraph("WER = [ (Substitutions + Deletions + Insertions) / Total_Words ] × 100%", eq_style), Paragraph("(7)", eq_style)]], colWidths=[200, 35])
                t_eq.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
                story.append(t_eq)
            elif "RTF =" in p_text:
                t_eq = Table([[Paragraph("RTF = Total_Processing_Time / Audio_Duration", eq_style), Paragraph("(8)", eq_style)]], colWidths=[200, 35])
                t_eq.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
                story.append(t_eq)
            else:
                story.append(Paragraph(sanitize_rl(p_text), body_style))

        if "B. Speech Recognition Accuracy" in sub_title:
            story.append(format_pdf_table(pt.TABLE_II, col_w=[55, 45, 50, 45, 40]))
            if os.path.exists("paper_assets/fig_wer_comparison.png"):
                img = Image("paper_assets/fig_wer_comparison.png", width=235, height=115)
                cap = Paragraph("<b>Fig. 2. Audio cleaning impact on Whisper Word Error Rate (WER) across languages.</b>", caption_style)
                story.append(KeepTogether([img, cap]))
        elif "D. Processing Speed" in sub_title:
            story.append(format_pdf_table(pt.TABLE_IV, col_w=[60, 35, 35, 35, 35, 35]))
            if os.path.exists("paper_assets/fig_latency_rtf.png"):
                img = Image("paper_assets/fig_latency_rtf.png", width=235, height=105)
                cap = Paragraph("<b>Fig. 3. Processing time per stage (a) and Real-Time Factor (RTF) comparison (b).</b>", caption_style)
                story.append(KeepTogether([img, cap]))
        elif "E. Accuracy of Categorization" in sub_title:
            story.append(format_pdf_table(pt.TABLE_III, col_w=[65, 60, 35, 35, 40]))
            if os.path.exists("paper_assets/fig_classification_metrics.png"):
                img = Image("paper_assets/fig_classification_metrics.png", width=235, height=115)
                cap = Paragraph("<b>Fig. 4. Accuracy scores across different customer support categories.</b>", caption_style)
                story.append(KeepTogether([img, cap]))

    # SECTION XII: DISCUSSION
    story.append(Paragraph(sanitize_rl(pt.SEC_XII_TITLE), sec_head_style))
    for p_text in pt.SEC_XII_BODY:
        story.append(Paragraph(sanitize_rl(p_text), body_style))

    # SECTION XIII: ADVANTAGES AND LIMITATIONS
    story.append(Paragraph(sanitize_rl(pt.SEC_XIII_TITLE), sec_head_style))
    story.append(format_pdf_table(pt.TABLE_V, col_w=[50, 40, 45, 45, 55]))
    for sub_title, sub_paras in pt.SEC_XIII_BODY:
        story.append(Paragraph(sanitize_rl(sub_title), subsec_head_style))
        for p_text in sub_paras:
            story.append(Paragraph(sanitize_rl(p_text), body_style))

    # SECTION XIV: CONCLUSION
    story.append(Paragraph(sanitize_rl(pt.SEC_XIV_TITLE), sec_head_style))
    for p_text in pt.SEC_XIV_BODY:
        story.append(Paragraph(sanitize_rl(p_text), body_style))

    # SECTION XV: FUTURE SCOPE
    story.append(Paragraph(sanitize_rl(pt.SEC_XV_TITLE), sec_head_style))
    for p_text in pt.SEC_XV_BODY:
        story.append(Paragraph(sanitize_rl(p_text), body_style))

    # SECTION XVI: REFERENCES
    story.append(Paragraph("XVI. REFERENCES", sec_head_style))
    for ref in pt.REFERENCES:
        story.append(Paragraph(sanitize_rl(ref), ref_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated non-italic simple PDF: {output_path}")

if __name__ == "__main__":
    generate_ieee_pdf()
