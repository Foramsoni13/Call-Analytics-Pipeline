#!/usr/bin/env python3
"""
CallSense IEEE Academic Research Paper Generator
Generates:
  1. CallSense_Research_Paper_IEEE.docx (Editable IEEE-formatted Word Document)
  2. CallSense_Research_Paper_IEEE.pdf (Camera-Ready IEEE-formatted PDF)
Suitable for Master of Computer Applications (MCA) Academic Submission.
"""

import os
import sys
import math
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
from docx.enum.section import WD_SECTION_START

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, FrameBreak,
    NextPageTemplate, Table, TableStyle, Image, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

print("Generator script initialized.")
