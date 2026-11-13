#!/usr/bin/env python3
"""
Builds CallSense_Research_Paper_IEEE.docx
Zero italics anywhere. All fonts in regular Times New Roman (or bold for titles).
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
from docx.enum.section import WD_SECTION_START

import paper_text as pt

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        r'<w:tblBorders %s>'
        r'  <w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
        r'  <w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
        r'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="D1D5DB"/>'
        r'  <w:insideV w:val="none"/>'
        r'  <w:left w:val="none"/>'
        r'  <w:right w:val="none"/>'
        r'</w:tblBorders>' % nsdecls('w')
    )
    tblPr.append(borders)

def add_p(doc, text="", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=4, line_spacing=1.05, bold=False, font_size=10, font_name="Times New Roman", font_color=RGBColor(0,0,0)):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if text:
        run = p.add_run(text)
        run.bold = bold
        run.italic = False  # NEVER ITALIC
        run.font.name = font_name
        run.font.size = Pt(font_size)
        run.font.color.rgb = font_color
    return p

def add_sec_heading(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    run.bold = True
    run.italic = False  # NEVER ITALIC
    run.font.name = "Times New Roman"
    run.font.size = Pt(10)
    return p

def add_subsec_heading(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    run.bold = True
    run.italic = False  # NEVER ITALIC
    run.font.name = "Times New Roman"
    run.font.size = Pt(10)
    return p

def add_subsubsec_heading(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    run.bold = True
    run.italic = False  # NEVER ITALIC
    run.font.name = "Times New Roman"
    run.font.size = Pt(9.5)
    return p

def add_equation(doc, eq_text, eq_num):
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(2.85)
    table.columns[1].width = Inches(0.45)
    
    cell_l = table.cell(0, 0)
    p_l = cell_l.paragraphs[0]
    p_l.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_l.paragraph_format.space_before = Pt(2)
    p_l.paragraph_format.space_after = Pt(2)
    r_l = p_l.add_run(eq_text)
    r_l.font.name = "Times New Roman"
    r_l.font.size = Pt(9.5)
    r_l.italic = False  # NEVER ITALIC
    
    cell_r = table.cell(0, 1)
    p_r = cell_r.paragraphs[0]
    p_r.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_r.paragraph_format.space_before = Pt(2)
    p_r.paragraph_format.space_after = Pt(2)
    r_r = p_r.add_run(f"({eq_num})")
    r_r.font.name = "Times New Roman"
    r_r.font.size = Pt(9.5)
    r_r.italic = False  # NEVER ITALIC

def add_table_data(doc, table_dict):
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(8)
    p_cap.paragraph_format.space_after = Pt(3)
    r_cap = p_cap.add_run(table_dict["caption"])
    r_cap.bold = True
    r_cap.italic = False  # NEVER ITALIC
    r_cap.font.name = "Times New Roman"
    r_cap.font.size = Pt(8.5)
    
    headers = table_dict["headers"]
    rows = table_dict["rows"]
    table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)
    
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        set_cell_background(cell, "F1F5F9")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(h)
        r.bold = True
        r.italic = False  # NEVER ITALIC
        r.font.name = "Times New Roman"
        r.font.size = Pt(8)
        
    for i, row in enumerate(rows):
        bg = "FFFFFF" if i % 2 == 0 else "F8FAFC"
        for j, val in enumerate(row):
            cell = table.cell(i + 1, j)
            set_cell_background(cell, bg)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j <= 1 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(1.5)
            p.paragraph_format.space_after = Pt(1.5)
            r = p.add_run(str(val))
            r.italic = False  # NEVER ITALIC
            r.font.name = "Times New Roman"
            r.font.size = Pt(8)

def add_algorithm(doc, algo_dict):
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_title.paragraph_format.space_before = Pt(8)
    p_title.paragraph_format.space_after = Pt(2)
    r_t = p_title.add_run(f"Algorithm {algo_dict['num']}: {algo_dict['title']}")
    r_t.bold = True
    r_t.italic = False  # NEVER ITALIC
    r_t.font.name = "Times New Roman"
    r_t.font.size = Pt(8.5)
    
    steps = algo_dict["steps"]
    table = doc.add_table(rows=len(steps), cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(3.35)
    
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        r'<w:tblBorders %s>'
        r'  <w:top w:val="single" w:sz="6" w:space="0" w:color="475569"/>'
        r'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="475569"/>'
        r'  <w:left w:val="single" w:sz="6" w:space="0" w:color="475569"/>'
        r'  <w:right w:val="single" w:sz="6" w:space="0" w:color="475569"/>'
        r'  <w:insideH w:val="none"/>'
        r'  <w:insideV w:val="none"/>'
        r'</w:tblBorders>' % nsdecls('w')
    )
    tblPr.append(borders)
    
    for i, step in enumerate(steps):
        cell = table.cell(i, 0)
        set_cell_background(cell, "F8FAFC")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(step)
        r.italic = False  # NEVER ITALIC
        r.font.name = "Courier New"
        r.font.size = Pt(7)

def add_figure(doc, img_path, caption):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(2)
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=Inches(3.3))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(6)
        r_cap = p_cap.add_run(caption)
        r_cap.font.name = "Times New Roman"
        r_cap.font.size = Pt(8.5)
        r_cap.italic = False  # NEVER ITALIC
        r_cap.bold = True

def generate_ieee_docx(output_path="CallSense_Research_Paper_IEEE.docx"):
    print("Generating non-italic simple DOCX document...")
    doc = docx.Document()
    
    # Configure Section 1: Title & Author (Single Column)
    sec1 = doc.sections[0]
    sec1.top_margin = Inches(0.75)
    sec1.bottom_margin = Inches(0.75)
    sec1.left_margin = Inches(0.75)
    sec1.right_margin = Inches(0.75)
    
    # Title (Bold, Non-Italic)
    add_p(doc, pt.TITLE, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=12, line_spacing=1.1, bold=True, font_size=20)
    
    # Author Block (Non-Italic)
    p_auth = doc.add_paragraph()
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auth.paragraph_format.space_before = Pt(0)
    p_auth.paragraph_format.space_after = Pt(16)
    
    r_name = p_auth.add_run(f"{pt.AUTHOR_NAME}\n")
    r_name.bold = True
    r_name.italic = False
    r_name.font.name = "Times New Roman"
    r_name.font.size = Pt(11)
    
    r_aff = p_auth.add_run(f"{pt.AUTHOR_AFFILIATION}\n")
    r_aff.italic = False
    r_aff.font.name = "Times New Roman"
    r_aff.font.size = Pt(9.5)
    
    # Continuous Section Break into Two Columns
    sec2 = doc.add_section(WD_SECTION_START.CONTINUOUS)
    sec2.top_margin = Inches(0.75)
    sec2.bottom_margin = Inches(0.75)
    sec2.left_margin = Inches(0.75)
    sec2.right_margin = Inches(0.75)
    
    sectPr = sec2._sectPr
    cols = OxmlElement('w:cols')
    cols.set(qn('w:num'), '2')
    cols.set(qn('w:space'), '360') # 0.25 in spacing
    sectPr.append(cols)
    
    # Abstract & Keywords in column 1 (Regular font, NO ITALICS)
    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_abs.paragraph_format.space_before = Pt(0)
    p_abs.paragraph_format.space_after = Pt(4)
    p_abs.paragraph_format.line_spacing = 1.05
    r_absh = p_abs.add_run("Abstract—")
    r_absh.bold = True
    r_absh.italic = False
    r_absh.font.name = "Times New Roman"
    r_absh.font.size = Pt(9)
    r_abst = p_abs.add_run(pt.ABSTRACT)
    r_abst.italic = False  # NEVER ITALIC
    r_abst.font.name = "Times New Roman"
    r_abst.font.size = Pt(9)
    
    p_kw = doc.add_paragraph()
    p_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_kw.paragraph_format.space_before = Pt(2)
    p_kw.paragraph_format.space_after = Pt(8)
    p_kw.paragraph_format.line_spacing = 1.05
    r_kwh = p_kw.add_run("Index Terms—")
    r_kwh.bold = True
    r_kwh.italic = False
    r_kwh.font.name = "Times New Roman"
    r_kwh.font.size = Pt(9)
    r_kwt = p_kw.add_run(", ".join(pt.KEYWORDS))
    r_kwt.italic = False  # NEVER ITALIC
    r_kwt.font.name = "Times New Roman"
    r_kwt.font.size = Pt(9)
    
    # SECTION I: INTRODUCTION
    add_sec_heading(doc, pt.SEC_I_TITLE)
    for p_text in pt.SEC_I_BODY:
        add_p(doc, p_text)
        
    # SECTION II: BACKGROUND AND MOTIVATION
    add_sec_heading(doc, pt.SEC_II_TITLE)
    for sub_title, sub_paras in pt.SEC_II_BODY:
        add_subsec_heading(doc, sub_title)
        for p_text in sub_paras:
            add_p(doc, p_text)
            
    # SECTION III: LITERATURE REVIEW
    add_sec_heading(doc, pt.SEC_III_TITLE)
    for sub_title, sub_paras in pt.SEC_III_BODY:
        add_subsec_heading(doc, sub_title)
        for p_text in sub_paras:
            add_p(doc, p_text)
            
    # SECTION IV: RESEARCH GAP
    add_sec_heading(doc, pt.SEC_IV_TITLE)
    for p_text in pt.SEC_IV_BODY:
        add_p(doc, p_text)
        
    # SECTION V: PROBLEM STATEMENT
    add_sec_heading(doc, pt.SEC_V_TITLE)
    add_p(doc, pt.SEC_V_BODY[0])
    add_equation(doc, "y(t) = [x(t) * h(t)] + η(t)", "1")
    add_p(doc, pt.SEC_V_BODY[2])
    add_p(doc, pt.SEC_V_BODY[3])
    add_equation(doc, "M = ⟨Language, Transcript, Sentiment, Category, Priority, Resolution, Phone_Numbers, Action_Items, Translations⟩", "2")
    for p_text in pt.SEC_V_BODY[5:]:
        add_p(doc, p_text)
        
    # SECTION VI: RESEARCH OBJECTIVES
    add_sec_heading(doc, pt.SEC_VI_TITLE)
    for p_text in pt.SEC_VI_BODY:
        add_p(doc, p_text)
        
    # SECTION VII: PROPOSED METHODOLOGY
    add_sec_heading(doc, pt.SEC_VII_TITLE)
    for sub_title, sub_paras in pt.SEC_VII_BODY:
        add_subsec_heading(doc, sub_title)
        for p_text in sub_paras:
            if "H(z) =" in p_text:
                add_p(doc, "The high-pass filter equation is written as:")
                add_equation(doc, "H(z) = (1 - z^-1) / (1 - α·z^-1),  α = 1 / (1 + 2π·fc / fs)", "3")
            elif "E_dBFS(m) =" in p_text:
                add_p(doc, "The sound energy in decibels is calculated as:")
                add_equation(doc, "E_dBFS(m) = 10·log10[ (1/N · Σ x^2) / X_max^2 ]", "4")
            elif "C_ASR =" in p_text:
                add_p(doc, "The confidence percentage score is defined as:")
                add_equation(doc, "C_ASR = exp( 1/|S| · Σ l̄_s ) × 100%", "5")
            elif "P_regex =" in p_text:
                add_p(doc, "The regular expression pattern for phone numbers is:")
                add_equation(doc, r"P_regex = (?<!\d)(\d{10})(?!\d)", "6")
            else:
                add_p(doc, p_text)
                
    # SECTION VIII: SYSTEM ARCHITECTURE AND WORKFLOW
    add_sec_heading(doc, pt.SEC_VIII_TITLE)
    add_figure(doc, "paper_assets/fig_architecture.png", "Fig. 1. CallSense end-to-end system architecture and dataflow pipeline.")
    for p_text in pt.SEC_VIII_BODY:
        add_p(doc, p_text)
        
    # SECTION IX: TECHNOLOGIES USED
    add_sec_heading(doc, pt.SEC_IX_TITLE)
    add_table_data(doc, pt.TABLE_I)
    for p_text in pt.SEC_IX_BODY:
        add_p(doc, p_text)
        
    # SECTION X: IMPLEMENTATION DETAILS
    add_sec_heading(doc, pt.SEC_X_TITLE)
    for sub_title, sub_paras in pt.SEC_X_BODY:
        add_subsec_heading(doc, sub_title)
        for p_text in sub_paras:
            add_p(doc, p_text)
            if "Algorithm 1" in p_text:
                add_algorithm(doc, pt.ALGORITHM_1)
            elif "Algorithm 2" in p_text:
                add_algorithm(doc, pt.ALGORITHM_2)
                
    # SECTION XI: EXPERIMENTAL RESULTS AND ANALYSIS
    add_sec_heading(doc, pt.SEC_XI_TITLE)
    for sub_title, sub_paras in pt.SEC_XI_BODY:
        add_subsec_heading(doc, sub_title)
        for p_text in sub_paras:
            if "WER =" in p_text:
                add_equation(doc, "WER = [ (Substitutions + Deletions + Insertions) / Total_Words ] × 100%", "7")
            elif "RTF =" in p_text:
                add_equation(doc, "RTF = Total_Processing_Time / Audio_Duration", "8")
            else:
                add_p(doc, p_text)
                
        if "B. Speech Recognition Accuracy" in sub_title:
            add_table_data(doc, pt.TABLE_II)
            add_figure(doc, "paper_assets/fig_wer_comparison.png", "Fig. 2. Audio cleaning impact on Whisper Word Error Rate (WER) across languages.")
        elif "D. Processing Speed" in sub_title:
            add_table_data(doc, pt.TABLE_IV)
            add_figure(doc, "paper_assets/fig_latency_rtf.png", "Fig. 3. Processing time per stage (a) and Real-Time Factor (RTF) comparison (b).")
        elif "E. Accuracy of Categorization" in sub_title:
            add_table_data(doc, pt.TABLE_III)
            add_figure(doc, "paper_assets/fig_classification_metrics.png", "Fig. 4. Accuracy scores across different customer support categories.")
            
    # SECTION XII: DISCUSSION
    add_sec_heading(doc, pt.SEC_XII_TITLE)
    for p_text in pt.SEC_XII_BODY:
        add_p(doc, p_text)
        
    # SECTION XIII: ADVANTAGES AND LIMITATIONS
    add_sec_heading(doc, pt.SEC_XIII_TITLE)
    add_table_data(doc, pt.TABLE_V)
    for sub_title, sub_paras in pt.SEC_XIII_BODY:
        add_subsec_heading(doc, sub_title)
        for p_text in sub_paras:
            add_p(doc, p_text)
            
    # SECTION XIV: CONCLUSION
    add_sec_heading(doc, pt.SEC_XIV_TITLE)
    for p_text in pt.SEC_XIV_BODY:
        add_p(doc, p_text)
        
    # SECTION XV: FUTURE SCOPE
    add_sec_heading(doc, pt.SEC_XV_TITLE)
    for p_text in pt.SEC_XV_BODY:
        add_p(doc, p_text)
        
    # SECTION XVI: REFERENCES
    add_sec_heading(doc, "XVI. REFERENCES")
    for ref in pt.REFERENCES:
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.space_before = Pt(1)
        p_ref.paragraph_format.space_after = Pt(2)
        p_ref.paragraph_format.left_indent = Inches(0.2)
        p_ref.paragraph_format.first_line_indent = Inches(-0.2)
        r_ref = p_ref.add_run(ref)
        r_ref.font.name = "Times New Roman"
        r_ref.font.size = Pt(8)
        r_ref.italic = False  # NEVER ITALIC
        
    doc.save(output_path)
    print(f"Successfully generated non-italic simple DOCX: {output_path}")

if __name__ == "__main__":
    generate_ieee_docx()
