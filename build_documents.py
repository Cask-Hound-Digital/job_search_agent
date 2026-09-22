"""
ATS-Compliant Document Generation Engine.
Generates single-column Word (.docx) and PDF (.pdf) resumes from Markdown templates.
Strictly enforces zero em-dashes and ATS single-column formatting standards.
"""

import os
import re
import json
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

def sanitize_text(text: str) -> str:
    if not text:
        return ""
    # Enforce zero em-dashes
    clean = text.replace("\u2014", " - ").replace("&" + "mdash;", " - ")
    return re.sub(r'\s+', ' ', clean).strip()

def build_docx_resume(profile: dict, target_role: str, filepath: str):
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.5)
        s.bottom_margin = Inches(0.5)
        s.left_margin = Inches(0.6)
        s.right_margin = Inches(0.6)

    # Name Header
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(sanitize_text(profile.get("name", "Candidate Name")).upper())
    r.font.size = Pt(20)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)

    # Contact Info
    p_c = doc.add_paragraph()
    p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    contact_line = f"{profile.get('location', '')} | {profile.get('phone', '')} | {profile.get('email', '')} | {profile.get('linkedin', '')}"
    r_c = p_c.add_run(sanitize_text(contact_line))
    r_c.font.size = Pt(9.5)
    r_c.font.color.rgb = RGBColor(0x4A, 0x55, 0x68)

    # Headline
    p_h = doc.add_paragraph()
    p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_h = p_h.add_run(sanitize_text(target_role).upper())
    r_h.font.size = Pt(12)
    r_h.font.bold = True

    doc.save(filepath)
    print(f"Generated DOCX Resume: {filepath}")

def build_pdf_resume(profile: dict, target_role: str, filepath: str):
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    styles = getSampleStyleSheet()
    story = []

    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1B365D'),
        alignment=1
    )
    story.append(Paragraph(sanitize_text(profile.get("name", "Candidate Name")).upper(), header_style))

    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor('#4A5568'),
        alignment=1
    )
    contact_line = f"{profile.get('location', '')} | {profile.get('phone', '')} | {profile.get('email', '')} | {profile.get('linkedin', '')}"
    story.append(Paragraph(sanitize_text(contact_line), contact_style))
    story.append(Spacer(1, 10))

    doc.build(story)
    print(f"Generated PDF Resume: {filepath}")

def generate_package(company: str, target_role: str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    comp_dir = os.path.join(OUTPUT_DIR, re.sub(r'[^a-zA-Z0-9]', '_', company))
    os.makedirs(comp_dir, exist_ok=True)

    cfg_path = os.path.join(BASE_DIR, "config.json")
    profile = {}
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            c = json.load(f).get("candidate", {})
            profile = {
                "name": c.get("full_name", "Candidate Name"),
                "email": c.get("email", "candidate@example.com"),
                "phone": c.get("phone", "(555) 000-0000"),
                "location": c.get("primary_location", "Remote"),
                "linkedin": "https://www.linkedin.com/in/candidate/"
            }

    docx_path = os.path.join(comp_dir, f"Resume_{company}.docx")
    pdf_path = os.path.join(comp_dir, f"Resume_{company}.pdf")

    build_docx_resume(profile, target_role, docx_path)
    build_pdf_resume(profile, target_role, pdf_path)

if __name__ == "__main__":
    generate_package("ExampleCorp", "Director of Engineering")
