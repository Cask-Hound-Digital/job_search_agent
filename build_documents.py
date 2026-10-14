"""
ATS-Compliant Document Generation Engine.
Generates single-column Word (.docx) and PDF (.pdf) resumes and 6-part hybrid cover letters.
Strictly enforces zero em-dashes and ATS single-column formatting standards.
"""

import os
import re
import json
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

DEFAULT_COVER_LETTER_BULLETS = [
    ("Technical Strategy & Enterprise Architecture", "Architected and scaled modern enterprise platforms and services, ensuring system stability, cloud efficiency, and continuous alignment with organizational milestones."),
    ("Cross-Functional Leadership", "Led and mentored multi-disciplinary engineering and operations teams, driving cross-team alignment and delivering high-impact strategic initiatives on schedule."),
    ("Operational Excellence & Automation", "Modernized continuous integration and deployment pipelines, decreasing release cycle times by over 35% while upholding strict reliability and security benchmarks."),
    ("Strategic Planning & Execution", "Partnered with executive leadership to establish technical roadmaps, budget allocation, and technical governance models that accelerated operational velocity."),
    ("Team Mentorship & Culture", "Recruited, coached, and retained top engineering talent, cultivating an engineering culture centered on accountability, technical rigor, and cross-functional collaboration.")
]

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

    navy = RGBColor(0x1B, 0x36, 0x5D)
    dark_gray = RGBColor(0x2D, 0x37, 0x48)
    muted_gray = RGBColor(0x4A, 0x55, 0x68)

    # 1. Name Header
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(sanitize_text(profile.get("name", "Candidate Name")).upper())
    r.font.size = Pt(20)
    r.font.bold = True
    r.font.color.rgb = navy

    # 2. Contact Info
    p_c = doc.add_paragraph()
    p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c.paragraph_format.space_after = Pt(4)
    contact_line = f"{profile.get('location', '')} | {profile.get('phone', '')} | {profile.get('email', '')} | {profile.get('linkedin', '')}"
    r_c = p_c.add_run(sanitize_text(contact_line))
    r_c.font.size = Pt(9.5)
    r_c.font.color.rgb = muted_gray

    # 3. Target Role Headline
    p_h = doc.add_paragraph()
    p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_h.paragraph_format.space_after = Pt(12)
    r_h = p_h.add_run(sanitize_text(target_role).upper())
    r_h.font.size = Pt(12)
    r_h.font.bold = True
    r_h.font.color.rgb = navy

    # Helper for Section Headers
    def add_section_header(title: str):
        sec_p = doc.add_paragraph()
        sec_p.paragraph_format.space_before = Pt(10)
        sec_p.paragraph_format.space_after = Pt(3)
        run = sec_p.add_run(title.upper())
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = navy

    # 4. Professional Summary
    summary = profile.get("professional_summary")
    if summary:
        add_section_header("Professional Summary")
        p_s = doc.add_paragraph()
        p_s.paragraph_format.space_after = Pt(6)
        r_s = p_s.add_run(sanitize_text(summary))
        r_s.font.size = Pt(10)
        r_s.font.color.rgb = dark_gray

    # 5. Key Skills
    skills = profile.get("key_skills", [])
    if skills:
        add_section_header("Key Skills")
        p_sk = doc.add_paragraph()
        p_sk.paragraph_format.space_after = Pt(6)
        r_sk = p_sk.add_run(" • ".join(sanitize_text(s) for s in skills))
        r_sk.font.size = Pt(9.5)
        r_sk.font.color.rgb = dark_gray

    # 6. Professional Experience
    experiences = profile.get("experience", [])
    if experiences:
        add_section_header("Professional Experience")
        for job in experiences:
            p_job = doc.add_paragraph()
            p_job.paragraph_format.space_before = Pt(6)
            p_job.paragraph_format.space_after = Pt(1)
            r_co = p_job.add_run(sanitize_text(job.get("company", "Company")))
            r_co.bold = True
            r_co.font.size = Pt(10.5)
            r_co.font.color.rgb = navy

            loc = job.get("location")
            if loc:
                r_loc = p_job.add_run(f" | {sanitize_text(loc)}")
                r_loc.font.size = Pt(9.5)
                r_loc.font.color.rgb = muted_gray

            p_title = doc.add_paragraph()
            p_title.paragraph_format.space_after = Pt(3)
            r_t = p_title.add_run(sanitize_text(job.get("title", "Role Title")))
            r_t.italic = True
            r_t.font.size = Pt(10)

            dates = f"{job.get('start_date', '')} - {job.get('end_date', '')}".strip(" -")
            if dates:
                r_d = p_title.add_run(f" | {sanitize_text(dates)}")
                r_d.font.size = Pt(9.5)
                r_d.font.color.rgb = muted_gray

            for bullet in job.get("bullets", []):
                p_b = doc.add_paragraph(style='List Bullet')
                p_b.paragraph_format.space_after = Pt(2)
                r_b = p_b.add_run(sanitize_text(bullet))
                r_b.font.size = Pt(9.5)
                r_b.font.color.rgb = dark_gray

    # 7. Education
    education = profile.get("education", [])
    if education:
        add_section_header("Education")
        for edu in education:
            p_edu = doc.add_paragraph()
            p_edu.paragraph_format.space_after = Pt(2)
            deg = sanitize_text(edu.get("degree", "Degree"))
            inst = sanitize_text(edu.get("institution", "Institution"))
            yr = sanitize_text(str(edu.get("graduation_year", "")))
            edu_text = f"{deg} | {inst}" + (f" ({yr})" if yr else "")
            r_e = p_edu.add_run(edu_text)
            r_e.font.size = Pt(9.5)
            r_e.font.color.rgb = dark_gray

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

    navy_hex = '#1B365D'
    charcoal_hex = '#2D3748'
    muted_hex = '#4A5568'

    header_style = ParagraphStyle(
        'ResumeHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor(navy_hex),
        alignment=1,
        spaceAfter=2
    )
    story.append(Paragraph(sanitize_text(profile.get("name", "Candidate Name")).upper(), header_style))

    contact_style = ParagraphStyle(
        'ResumeContact',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor(muted_hex),
        alignment=1,
        spaceAfter=4
    )
    contact_line = f"{profile.get('location', '')} | {profile.get('phone', '')} | {profile.get('email', '')} | {profile.get('linkedin', '')}"
    story.append(Paragraph(sanitize_text(contact_line), contact_style))

    headline_style = ParagraphStyle(
        'ResumeHeadline',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor(navy_hex),
        alignment=1,
        spaceAfter=10
    )
    story.append(Paragraph(sanitize_text(target_role).upper(), headline_style))

    sec_header_style = ParagraphStyle(
        'ResumeSection',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor(navy_hex),
        spaceBefore=8,
        spaceAfter=3
    )

    body_style = ParagraphStyle(
        'ResumeBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor(charcoal_hex),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'ResumeBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor(charcoal_hex),
        leftIndent=12,
        spaceAfter=3
    )

    job_title_style = ParagraphStyle(
        'ResumeJobTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor(charcoal_hex),
        spaceAfter=3
    )

    # 1. Professional Summary
    summary = profile.get("professional_summary")
    if summary:
        story.append(Paragraph("PROFESSIONAL SUMMARY", sec_header_style))
        story.append(Paragraph(sanitize_text(summary), body_style))

    # 2. Key Skills
    skills = profile.get("key_skills", [])
    if skills:
        story.append(Paragraph("KEY SKILLS", sec_header_style))
        skills_text = " • ".join(sanitize_text(s) for s in skills)
        story.append(Paragraph(skills_text, body_style))

    # 3. Professional Experience
    experiences = profile.get("experience", [])
    if experiences:
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", sec_header_style))
        for job in experiences:
            co = sanitize_text(job.get("company", "Company"))
            loc = sanitize_text(job.get("location", ""))
            t = sanitize_text(job.get("title", "Role Title"))
            dates = f"{job.get('start_date', '')} - {job.get('end_date', '')}".strip(" -")

            co_line = f"<b>{co}</b>" + (f" | {loc}" if loc else "")
            story.append(Paragraph(co_line, body_style))

            t_line = f"<i>{t}</i>" + (f" | {dates}" if dates else "")
            story.append(Paragraph(t_line, job_title_style))

            for bullet in job.get("bullets", []):
                story.append(Paragraph(f"&bull; {sanitize_text(bullet)}", bullet_style))
            story.append(Spacer(1, 4))

    # 4. Education
    education = profile.get("education", [])
    if education:
        story.append(Paragraph("EDUCATION", sec_header_style))
        for edu in education:
            deg = sanitize_text(edu.get("degree", "Degree"))
            inst = sanitize_text(edu.get("institution", "Institution"))
            yr = sanitize_text(str(edu.get("graduation_year", "")))
            edu_text = f"{deg} | {inst}" + (f" ({yr})" if yr else "")
            story.append(Paragraph(edu_text, body_style))

    doc.build(story)
    print(f"Generated PDF Resume: {filepath}")

def build_docx_cover_letter(profile: dict, company: str, target_role: str, filepath: str):
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.5)
        s.bottom_margin = Inches(0.5)
        s.left_margin = Inches(0.6)
        s.right_margin = Inches(0.6)

    navy = RGBColor(0x1B, 0x36, 0x5D)
    dark_gray = RGBColor(0x2D, 0x37, 0x48)
    muted_gray = RGBColor(0x4A, 0x55, 0x68)

    # 1. Branding Header (Matches Resume Design)
    p_name = doc.add_paragraph()
    p_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_name.paragraph_format.space_after = Pt(2)
    r_n = p_name.add_run(sanitize_text(profile.get("name", "Candidate Name")).upper())
    r_n.font.size = Pt(18)
    r_n.font.bold = True
    r_n.font.color.rgb = navy

    p_contact = doc.add_paragraph()
    p_contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_contact.paragraph_format.space_after = Pt(14)
    contact_line = f"{profile.get('location', '')} | {profile.get('phone', '')} | {profile.get('email', '')} | {profile.get('linkedin', '')}"
    r_c = p_contact.add_run(sanitize_text(contact_line))
    r_c.font.size = Pt(9.5)
    r_c.font.color.rgb = muted_gray

    # 2. Address & Salutation
    p_date = doc.add_paragraph()
    p_date.paragraph_format.space_after = Pt(2)
    r_d = p_date.add_run(datetime.now().strftime("%B %d, %Y"))
    r_d.font.size = Pt(10)
    r_d.font.color.rgb = dark_gray

    p_co = doc.add_paragraph()
    p_co.paragraph_format.space_after = Pt(10)
    r_co = p_co.add_run(sanitize_text(company))
    r_co.font.size = Pt(10)
    r_co.font.color.rgb = dark_gray

    p_sal = doc.add_paragraph()
    p_sal.paragraph_format.space_after = Pt(10)
    r_sal = p_sal.add_run(f"Dear {sanitize_text(company)} Hiring Team,")
    r_sal.font.size = Pt(10.5)
    r_sal.font.color.rgb = dark_gray

    # 3. Introductory Paragraph (3-5 sentences)
    p_intro = doc.add_paragraph()
    p_intro.paragraph_format.space_after = Pt(10)
    intro_text = (
        f"I am writing to formally submit my application for the {target_role} position at {company}. "
        f"With a proven background directing enterprise digital platforms, streamlining cross-functional engineering operations, and driving technical excellence, "
        f"I have developed the strategic vision and practical execution skills required to thrive in this role. "
        f"Enclosed is my resume, and below I have summarized several key competencies that directly map to {company}'s priorities."
    )
    r_in = p_intro.add_run(sanitize_text(intro_text))
    r_in.font.size = Pt(10)
    r_in.font.color.rgb = dark_gray

    # 4. Body Bullet Points (Hybrid Bullet Layout: Bold Headline + Narrative)
    bullets = profile.get("cover_letter_bullets") or DEFAULT_COVER_LETTER_BULLETS
    for headline, narrative in bullets:
        p_b = doc.add_paragraph(style='List Bullet')
        p_b.paragraph_format.space_after = Pt(4)
        r_head = p_b.add_run(f"{sanitize_text(headline)}: ")
        r_head.bold = True
        r_head.font.size = Pt(9.5)
        r_head.font.color.rgb = navy
        r_nar = p_b.add_run(sanitize_text(narrative))
        r_nar.font.size = Pt(9.5)
        r_nar.font.color.rgb = dark_gray

    # 5. Closing Paragraph
    p_close = doc.add_paragraph()
    p_close.paragraph_format.space_before = Pt(6)
    p_close.paragraph_format.space_after = Pt(12)
    close_text = (
        f"Finally, I want to express my enthusiasm for {company} and the impactful work being built by your team. "
        f"I would welcome the opportunity to discuss how my background and operational execution model can accelerate your strategic goals. "
        f"Thank you for your time and consideration of my application, and I look forward to speaking with you regarding next steps."
    )
    r_cl = p_close.add_run(sanitize_text(close_text))
    r_cl.font.size = Pt(10)
    r_cl.font.color.rgb = dark_gray

    # 6. Sign Off & Name
    p_sign = doc.add_paragraph()
    p_sign.paragraph_format.space_after = Pt(16)
    r_sg = p_sign.add_run("Sincerely,")
    r_sg.font.size = Pt(10)
    r_sg.font.color.rgb = dark_gray

    p_name_sign = doc.add_paragraph()
    r_ns = p_name_sign.add_run(sanitize_text(profile.get("name", "Candidate Name")))
    r_ns.bold = True
    r_ns.font.size = Pt(10.5)
    r_ns.font.color.rgb = navy

    doc.save(filepath)
    print(f"Generated DOCX Cover Letter: {filepath}")

def build_pdf_cover_letter(profile: dict, company: str, target_role: str, filepath: str):
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

    navy_hex = '#1B365D'
    charcoal_hex = '#2D3748'
    muted_hex = '#4A5568'

    # 1. Branding Header
    header_style = ParagraphStyle(
        'CLHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor(navy_hex),
        alignment=1,
        spaceAfter=2
    )
    story.append(Paragraph(sanitize_text(profile.get("name", "Candidate Name")).upper(), header_style))

    contact_style = ParagraphStyle(
        'CLContact',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor(muted_hex),
        alignment=1,
        spaceAfter=14
    )
    contact_line = f"{profile.get('location', '')} | {profile.get('phone', '')} | {profile.get('email', '')} | {profile.get('linkedin', '')}"
    story.append(Paragraph(sanitize_text(contact_line), contact_style))

    body_style = ParagraphStyle(
        'CLBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor(charcoal_hex),
        spaceAfter=8
    )

    # 2. Address & Salutation
    date_str = datetime.now().strftime("%B %d, %Y")
    story.append(Paragraph(f"{date_str}<br/><b>{sanitize_text(company)}</b>", body_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph(f"Dear {sanitize_text(company)} Hiring Team,", body_style))
    story.append(Spacer(1, 4))

    # 3. Introductory Paragraph
    intro_text = (
        f"I am writing to formally submit my application for the {target_role} position at {company}. "
        f"With a proven background directing enterprise digital platforms, streamlining cross-functional engineering operations, and driving technical excellence, "
        f"I have developed the strategic vision and practical execution skills required to thrive in this role. "
        f"Enclosed is my resume, and below I have summarized several key competencies that directly map to {company}'s priorities."
    )
    story.append(Paragraph(sanitize_text(intro_text), body_style))
    story.append(Spacer(1, 4))

    # 4. Body Bullet Points (Hybrid Bullet Layout)
    bullet_style = ParagraphStyle(
        'CLBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor(charcoal_hex),
        leftIndent=12,
        spaceAfter=4
    )
    bullets = profile.get("cover_letter_bullets") or DEFAULT_COVER_LETTER_BULLETS
    for headline, narrative in bullets:
        bullet_html = f"&bull; <b>{sanitize_text(headline)}:</b> {sanitize_text(narrative)}"
        story.append(Paragraph(bullet_html, bullet_style))

    story.append(Spacer(1, 4))

    # 5. Closing Paragraph
    close_text = (
        f"Finally, I want to express my enthusiasm for {company} and the impactful work being built by your team. "
        f"I would welcome the opportunity to discuss how my background and operational execution model can accelerate your strategic goals. "
        f"Thank you for your time and consideration of my application, and I look forward to speaking with you regarding next steps."
    )
    story.append(Paragraph(sanitize_text(close_text), body_style))
    story.append(Spacer(1, 6))

    # 6. Sign Off & Name
    sign_html = f"Sincerely,<br/><br/><b>{sanitize_text(profile.get('name', 'Candidate Name'))}</b>"
    story.append(Paragraph(sign_html, body_style))

    doc.build(story)
    print(f"Generated PDF Cover Letter: {filepath}")

def build_cover_letter(profile: dict, company: str, target_role: str, docx_path: str, pdf_path: str = None):
    if pdf_path is None and os.path.isdir(docx_path):
        folder = docx_path
        d_path = os.path.join(folder, f"Cover_Letter_{company}.docx")
        p_path = os.path.join(folder, f"Cover_Letter_{company}.pdf")
    else:
        d_path = docx_path
        p_path = pdf_path

    if d_path:
        build_docx_cover_letter(profile, company, target_role, d_path)
    if p_path:
        build_pdf_cover_letter(profile, company, target_role, p_path)

def generate_package(company: str, target_role: str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    comp_dir = os.path.join(OUTPUT_DIR, re.sub(r'[^a-zA-Z0-9]', '_', company))
    os.makedirs(comp_dir, exist_ok=True)

    cfg_path = os.path.join(BASE_DIR, "config.json")
    profile = {}
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                c = json.load(f).get("candidate", {})
                profile = {
                    "name": c.get("full_name", "Candidate Name"),
                    "email": c.get("email", "candidate@example.com"),
                    "phone": c.get("phone", "(555) 000-0000"),
                    "location": c.get("primary_location", "Remote"),
                    "linkedin": c.get("linkedin", "https://www.linkedin.com/in/candidate/"),
                    "professional_summary": c.get("professional_summary", ""),
                    "key_skills": c.get("key_skills", []),
                    "experience": c.get("experience", []),
                    "education": c.get("education", [])
                }
        except Exception as e:
            print(f"Warning: Failed to load config.json in build_documents: {e}")

    # Build Resumes
    docx_path = os.path.join(comp_dir, f"Resume_{company}.docx")
    pdf_path = os.path.join(comp_dir, f"Resume_{company}.pdf")
    build_docx_resume(profile, target_role, docx_path)
    build_pdf_resume(profile, target_role, pdf_path)

    # Build Cover Letters (6-part hybrid)
    cl_docx_path = os.path.join(comp_dir, f"Cover_Letter_{company}.docx")
    cl_pdf_path = os.path.join(comp_dir, f"Cover_Letter_{company}.pdf")
    build_cover_letter(profile, company, target_role, cl_docx_path, cl_pdf_path)

    return comp_dir

if __name__ == "__main__":
    generate_package("ExampleCorp", "Director of Engineering")
