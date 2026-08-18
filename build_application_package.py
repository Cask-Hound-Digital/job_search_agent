"""
Unified Master Application Package Generator for {{YOUR_FULL_NAME}}.
Enforces 100% authentic career baseline dates, master PDF/DOCX layouts, and zero em dashes.
"""

import os
import sys
import argparse
import json
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ---------------------------------------------------------------------------
# 1. Authoritative Candidate Baseline Profile (Locked Truth - No Em Dashes)
# ---------------------------------------------------------------------------
CANDIDATE = {
    "name": "MARK JAGGERS",
    "contact": "{{YOUR_CITY_STATE}} | {{YOUR_PHONE_NUMBER}} | {{YOUR_EMAIL_ADDRESS}} | linkedin.com/in/jaggers/",
    "email": "{{YOUR_EMAIL_ADDRESS}}",
    "phone": "{{YOUR_PHONE_NUMBER}}",
    "location": "{{YOUR_CITY_STATE}}",
    "linkedin": "linkedin.com/in/jaggers/",
    "history": {
        "trend_micro": {
            "company": "{{PREVIOUS_COMPANY_1}}, Inc.",
            "location": "Irving, TX",
            "title": "Global Web Marketing Director of Development",
            "dates": "June 2008 - August 2026"
        },
        "handmark": {
            "company": "{{PREVIOUS_COMPANY_2}}, Inc.",
            "location": "Southlake, TX",
            "title": "Product Manager of Web and E-commerce",
            "dates": "Aug 2007 - Mar 2008"
        },
        "mapsco": {
            "company": "{{PREVIOUS_COMPANY_3}}, Inc.",
            "location": "Addison, TX",
            "title": "E-commerce and Web Marketing Manager",
            "dates": "Apr 2001 - Apr 2007"
        },
        "education": [
            {
                "degree": "Bachelor of Arts, Web Management/Internet Development",
                "institution": "University of Texas at Arlington | Arlington, TX"
            },
            {
                "degree": "Engineering Technology",
                "institution": "Texas A&M University | College Station, TX"
            }
        ]
    }
}

# Master Styling Tokens
NAVY_BLUE_HEX = "1B365D"
NAVY_RGB = RGBColor(0x1B, 0x36, 0x5D)
TEXT_DARK_RGB = RGBColor(0x22, 0x22, 0x22)
RL_NAVY = colors.HexColor("#1B365D")
RL_DARK = colors.HexColor("#222222")


def sanitize_text(text):
    if not text:
        return ""
    return text.replace("—", " - ").replace("–", " - ").replace("&mdash;", " - ").replace("&ndash;", " - ")


def add_bottom_border(paragraph, color_hex="1B365D", size_pt="6"):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="{size_pt}" w:space="1" w:color="{color_hex}"/></w:pBdr>')
    pPr.append(pBdr)


# ---------------------------------------------------------------------------
# 2. Universal Document Generation Engine (DOCX & PDF)
# ---------------------------------------------------------------------------
def generate_resume_docx(job_payload, output_docx_path):
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.6)
        section.right_margin = Inches(0.6)

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(9.5)
    normal_style.font.color.rgb = TEXT_DARK_RGB

    # Header Name
    p_name = doc.add_paragraph()
    p_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_name.paragraph_format.space_before = Pt(0)
    p_name.paragraph_format.space_after = Pt(2)
    run_name = p_name.add_run(sanitize_text(CANDIDATE["name"]))
    run_name.font.name = 'Calibri'
    run_name.font.size = Pt(22)
    run_name.font.bold = True
    run_name.font.color.rgb = NAVY_RGB

    # Contact Info
    p_contact = doc.add_paragraph()
    p_contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_contact.paragraph_format.space_before = Pt(0)
    p_contact.paragraph_format.space_after = Pt(4)
    run_contact = p_contact.add_run(sanitize_text(CANDIDATE["contact"]))
    run_contact.font.name = 'Calibri'
    run_contact.font.size = Pt(9.5)

    # Headline
    p_head = doc.add_paragraph()
    p_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_head.paragraph_format.space_before = Pt(2)
    p_head.paragraph_format.space_after = Pt(6)
    run_head = p_head.add_run(sanitize_text(job_payload["headline"]).upper())
    run_head.font.name = 'Calibri'
    run_head.font.size = Pt(11.5)
    run_head.font.bold = True
    run_head.font.color.rgb = NAVY_RGB

    def add_section_heading(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(sanitize_text(text).upper())
        run.font.name = 'Calibri'
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = NAVY_RGB
        add_bottom_border(p, NAVY_BLUE_HEX, "6")

    def add_bullet(bold_prefix, text):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2.5)
        p.paragraph_format.line_spacing = 1.12
        r1 = p.add_run(sanitize_text(bold_prefix))
        r1.font.bold = True
        r1.font.color.rgb = NAVY_RGB
        r2 = p.add_run(sanitize_text(text))
        r2.font.color.rgb = TEXT_DARK_RGB

    # Executive Summary
    add_section_heading("Executive Summary")
    p_sum = doc.add_paragraph()
    p_sum.paragraph_format.space_before = Pt(2)
    p_sum.paragraph_format.space_after = Pt(6)
    p_sum.paragraph_format.line_spacing = 1.12
    p_sum.add_run(sanitize_text(job_payload["summary"]))

    # Areas of Expertise
    add_section_heading("Areas of Expertise & Technical Stack")
    for category, text in job_payload["areas_of_expertise"]:
        add_bullet(category, text)

    # Professional Experience
    add_section_heading("Professional Experience")

    # {{PREVIOUS_COMPANY_1}}
    tm_info = CANDIDATE["history"]["trend_micro"]
    p_job1 = doc.add_paragraph()
    p_job1.paragraph_format.space_before = Pt(6)
    p_job1.paragraph_format.space_after = Pt(1)
    p_job1.paragraph_format.keep_with_next = True
    r_j1 = p_job1.add_run(f"{tm_info['title']}\n{tm_info['company']} | {tm_info['location']}")
    r_j1.font.bold = True
    r_j1.font.size = Pt(10.5)
    r_j1.font.color.rgb = NAVY_RGB

    p_j1_d = doc.add_paragraph()
    p_j1_d.paragraph_format.space_before = Pt(0)
    p_j1_d.paragraph_format.space_after = Pt(3)
    p_j1_d.paragraph_format.keep_with_next = True
    r_j1_date = p_j1_d.add_run(tm_info["dates"])
    r_j1_date.font.italic = True
    r_j1_date.font.size = Pt(9)

    for prefix, text in job_payload["trend_micro_bullets"]:
        add_bullet(prefix, text)

    # {{PREVIOUS_COMPANY_2}}
    hm_info = CANDIDATE["history"]["handmark"]
    p_job2 = doc.add_paragraph()
    p_job2.paragraph_format.space_before = Pt(6)
    p_job2.paragraph_format.space_after = Pt(1)
    p_job2.paragraph_format.keep_with_next = True
    r_j2 = p_job2.add_run(f"{hm_info['title']}\n{hm_info['company']} | {hm_info['location']}")
    r_j2.font.bold = True
    r_j2.font.size = Pt(10.5)
    r_j2.font.color.rgb = NAVY_RGB

    p_j2_d = doc.add_paragraph()
    p_j2_d.paragraph_format.space_before = Pt(0)
    p_j2_d.paragraph_format.space_after = Pt(3)
    p_j2_d.paragraph_format.keep_with_next = True
    r_j2_date = p_j2_d.add_run(hm_info["dates"])
    r_j2_date.font.italic = True
    r_j2_date.font.size = Pt(9)

    for prefix, text in job_payload["handmark_bullets"]:
        add_bullet(prefix, text)

    # {{PREVIOUS_COMPANY_3}}
    map_info = CANDIDATE["history"]["mapsco"]
    p_job3 = doc.add_paragraph()
    p_job3.paragraph_format.space_before = Pt(6)
    p_job3.paragraph_format.space_after = Pt(1)
    p_job3.paragraph_format.keep_with_next = True
    r_j3 = p_job3.add_run(f"{map_info['title']}\n{map_info['company']} | {map_info['location']}")
    r_j3.font.bold = True
    r_j3.font.size = Pt(10.5)
    r_j3.font.color.rgb = NAVY_RGB

    p_j3_d = doc.add_paragraph()
    p_j3_d.paragraph_format.space_before = Pt(0)
    p_j3_d.paragraph_format.space_after = Pt(3)
    p_j3_d.paragraph_format.keep_with_next = True
    r_j3_date = p_j3_d.add_run(map_info["dates"])
    r_j3_date.font.italic = True
    r_j3_date.font.size = Pt(9)

    for prefix, text in job_payload["mapsco_bullets"]:
        add_bullet(prefix, text)

    # Education
    add_section_heading("Education")
    for edu in CANDIDATE["history"]["education"]:
        p_edu = doc.add_paragraph()
        p_edu.paragraph_format.space_before = Pt(2)
        p_edu.paragraph_format.space_after = Pt(1)
        r_deg = p_edu.add_run(sanitize_text(edu["degree"]))
        r_deg.font.bold = True
        r_deg.font.size = Pt(9.5)
        p_inst = doc.add_paragraph(sanitize_text(edu["institution"]))
        p_inst.paragraph_format.space_after = Pt(4)
        p_inst.runs[0].font.size = Pt(9)

    doc.save(output_docx_path)
    print(f"Saved DOCX Resume to {output_docx_path}")


def generate_resume_pdf(job_payload, output_pdf_path):
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('HeaderName', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=RL_NAVY, alignment=1, spaceAfter=2)
    contact_style = ParagraphStyle('HeaderContact', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=12, textColor=RL_DARK, alignment=1, spaceAfter=4)
    subhead_style = ParagraphStyle('HeaderSub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=RL_NAVY, alignment=1, spaceAfter=6)
    sec_heading_style = ParagraphStyle('SecHeading', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=RL_NAVY, spaceBefore=8, spaceAfter=3, keepWithNext=True)
    body_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=13, textColor=RL_DARK, spaceAfter=4)
    bullet_style = ParagraphStyle('BulletCustom', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=13, textColor=RL_DARK, leftIndent=12, firstLineIndent=-10, spaceAfter=2.5)
    job_header_style = ParagraphStyle('JobHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10.5, leading=13, textColor=RL_NAVY, spaceBefore=5, spaceAfter=1, keepWithNext=True)
    job_sub_style = ParagraphStyle('JobSub', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=9, leading=11, textColor=RL_DARK, spaceAfter=3, keepWithNext=True)

    story = [
        Paragraph(sanitize_text(CANDIDATE["name"]), title_style),
        Paragraph(sanitize_text(CANDIDATE["contact"]), contact_style),
        Paragraph(sanitize_text(job_payload["headline"]).upper(), subhead_style)
    ]

    def add_pdf_sec(title):
        story.append(Paragraph(sanitize_text(title).upper(), sec_heading_style))
        story.append(HRFlowable(width="100%", thickness=0.75, color=RL_NAVY, spaceBefore=0, spaceAfter=4))

    # Executive Summary
    add_pdf_sec("Executive Summary")
    story.append(Paragraph(sanitize_text(job_payload["summary"]), body_style))

    # Areas of Expertise
    add_pdf_sec("Areas of Expertise & Technical Stack")
    for category, text in job_payload["areas_of_expertise"]:
        story.append(Paragraph(f"&bull; <b>{sanitize_text(category)}</b>{sanitize_text(text)}", bullet_style))

    # Professional Experience
    add_pdf_sec("Professional Experience")

    # {{PREVIOUS_COMPANY_1}}
    tm_info = CANDIDATE["history"]["trend_micro"]
    story.append(Paragraph(f"{tm_info['title']}<br/>{tm_info['company']} | {tm_info['location']}", job_header_style))
    story.append(Paragraph(tm_info["dates"], job_sub_style))
    for prefix, text in job_payload["trend_micro_bullets"]:
        story.append(Paragraph(f"&bull; <b>{sanitize_text(prefix)}</b>{sanitize_text(text)}", bullet_style))

    # {{PREVIOUS_COMPANY_2}}
    hm_info = CANDIDATE["history"]["handmark"]
    story.append(Paragraph(f"{hm_info['title']}<br/>{hm_info['company']} | {hm_info['location']}", job_header_style))
    story.append(Paragraph(hm_info["dates"], job_sub_style))
    for prefix, text in job_payload["handmark_bullets"]:
        story.append(Paragraph(f"&bull; <b>{sanitize_text(prefix)}</b>{sanitize_text(text)}", bullet_style))

    # {{PREVIOUS_COMPANY_3}}
    map_info = CANDIDATE["history"]["mapsco"]
    story.append(Paragraph(f"{map_info['title']}<br/>{map_info['company']} | {map_info['location']}", job_header_style))
    story.append(Paragraph(map_info["dates"], job_sub_style))
    for prefix, text in job_payload["mapsco_bullets"]:
        story.append(Paragraph(f"&bull; <b>{sanitize_text(prefix)}</b>{sanitize_text(text)}", bullet_style))

    # Education
    add_pdf_sec("Education")
    for edu in CANDIDATE["history"]["education"]:
        story.append(Paragraph(f"<b>{sanitize_text(edu['degree'])}</b><br/>{sanitize_text(edu['institution'])}", body_style))

    doc.build(story)
    print(f"Saved PDF Resume to {output_pdf_path}")


def generate_cover_docx(job_payload, output_docx_path):
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(0.6)
        section.bottom_margin = Inches(0.6)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(10)
    normal_style.font.color.rgb = TEXT_DARK_RGB

    # Header Name
    p_name = doc.add_paragraph()
    p_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_name.paragraph_format.space_after = Pt(2)
    run_name = p_name.add_run(sanitize_text(CANDIDATE["name"]))
    run_name.font.name = 'Calibri'
    run_name.font.size = Pt(20)
    run_name.font.bold = True
    run_name.font.color.rgb = NAVY_RGB

    # Contact Info
    p_contact = doc.add_paragraph()
    p_contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_contact.paragraph_format.space_after = Pt(12)
    p_contact.add_run(sanitize_text(CANDIDATE["contact"])).font.size = Pt(9.5)

    cl = job_payload["cover_letter"]

    p_date = doc.add_paragraph(sanitize_text(cl["date"]))
    p_date.paragraph_format.space_after = Pt(12)

    p_rec = doc.add_paragraph(sanitize_text(cl["recipient"]))
    p_rec.paragraph_format.space_after = Pt(12)

    p_sal = doc.add_paragraph(sanitize_text(cl["salutation"]))
    p_sal.paragraph_format.space_after = Pt(10)

    for para in cl["paragraphs"]:
        p_body = doc.add_paragraph(sanitize_text(para))
        p_body.paragraph_format.space_after = Pt(10)
        p_body.paragraph_format.line_spacing = 1.15

    p_sign = doc.add_paragraph("Sincerely,\n\n{{YOUR_FULL_NAME}}")
    p_sign.paragraph_format.space_after = Pt(0)

    doc.save(output_docx_path)
    print(f"Saved DOCX Cover Letter to {output_docx_path}")


def generate_cover_pdf(job_payload, output_pdf_path):
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CoverName', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=RL_NAVY, alignment=1, spaceAfter=2)
    contact_style = ParagraphStyle('CoverContact', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=12, textColor=RL_DARK, alignment=1, spaceAfter=14)
    body_style = ParagraphStyle('CoverBody', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14.5, textColor=RL_DARK, spaceAfter=10)

    story = [
        Paragraph(sanitize_text(CANDIDATE["name"]), title_style),
        Paragraph(sanitize_text(CANDIDATE["contact"]), contact_style)
    ]

    cl = job_payload["cover_letter"]
    story.append(Paragraph(sanitize_text(cl["date"]), body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(sanitize_text(cl["recipient"]).replace("\n", "<br/>"), body_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(sanitize_text(cl["salutation"]), body_style))
    story.append(Spacer(1, 4))

    for para in cl["paragraphs"]:
        story.append(Paragraph(sanitize_text(para), body_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Sincerely,<br/><br/>{{YOUR_FULL_NAME}}", body_style))

    doc.build(story)
    print(f"Saved PDF Cover Letter to {output_pdf_path}")


def build_package(job_payload):
    folder_name = job_payload.get("folder", job_payload["company"])
    output_dir = os.path.join(r"P:\Projects\job-search-consultant\Job Search", folder_name)
    os.makedirs(output_dir, exist_ok=True)

    role_slug = job_payload["role"].replace(" ", "_").replace(",", "").replace("-", "_")

    docx_res = os.path.join(output_dir, f"Mark_Jaggers_Resume_{job_payload['company']}_{role_slug}.docx")
    pdf_res = os.path.join(output_dir, f"Mark_Jaggers_Resume_{job_payload['company']}_{role_slug}.pdf")
    docx_cl = os.path.join(output_dir, f"Mark_Jaggers_Cover_Letter_{job_payload['company']}_{role_slug}.docx")
    pdf_cl = os.path.join(output_dir, f"Mark_Jaggers_Cover_Letter_{job_payload['company']}_{role_slug}.pdf")

    generate_resume_docx(job_payload, docx_res)
    generate_resume_pdf(job_payload, pdf_res)
    generate_cover_docx(job_payload, docx_cl)
    generate_cover_pdf(job_payload, pdf_cl)
    print(f"\nSuccessfully generated full master application package for {job_payload['company']} ({job_payload['role']}) in {output_dir}")


# ---------------------------------------------------------------------------
# 3. Built-In Role Configurations (100% Genuine Candidate Language Only)
# ---------------------------------------------------------------------------
DATABRICKS_PAYLOAD = {
    "company": "Databricks",
    "folder": "Databricks",
    "role": "Director Web Marketing",
    "headline": "DIRECTOR, WEB MARKETING | GLOBAL DIGITAL EXPERIENCE & AI STRATEGY LEADER",
    "summary": "Visionary Global Web & Digital Marketing Executive with 18+ years leading enterprise web strategy, digital platform architecture, AI-driven search transformation (GEO/AEO), and cross-functional technology teams. Proven track record transforming corporate web properties into scalable growth engines optimized for both human visitors and AI search/answer engines. Experienced in driving multi-national platform migrations across 34 countries and 14 languages, high-velocity experimentation, structured content governance, and data-driven web operations to maximize marketing pipeline.",
    "areas_of_expertise": [
        ("Global Web Strategy & Machine Readability: ", "Global Web Ecosystem Architecture, AI Agent & Answer Engine Optimization (GEO/AEO), Structured Content Standards, Personalization & Segmented Journeys."),
        ("AI-Driven Web Operations & Velocity: ", "Generative AI Workflows (Claude, ChatGPT, CoPilot), Prompt Engineering, Automated Analytics Reporting, Web Production Velocity."),
        ("Enterprise Platform Architecture: ", "Global Platform Migrations (34 Countries, 14 Languages), Adobe Experience Manager (AEM), Sanity, WordPress, Drupal, Marketo, Tealium, GA4, GTM."),
        ("Optimization, CRO & Governance: ", "A/B & Multivariate Testing Roadmaps, Conversion Rate Optimization (CRO), Budget Management ($1M+), Cross-Functional Collaboration Frameworks (Dev, UX, Marketing).")
    ],
    "trend_micro_bullets": [
        ("Global Web Operations & Demand Engine: ", "Led global digital operations and transformation leadership for {{PREVIOUS_COMPANY_1}}'s B2B and B2C enterprise portfolios, owning the corporate web channel as the primary demand generation and pipeline engine across development, operations, analytics, and marketing."),
        ("AI Search, GEO & Answer Engine Dominance: ", "Developed and executed comprehensive SEO, Generative Engine Optimization (GEO), and Answer Engine Optimization (AEO) strategies across global web properties, structuring content for machine readability to increase presence across traditional and AI search platforms by 40%."),
        ("AI Technology Integration & Development Velocity: ", "Integrated Artificial Intelligence (AI) technologies (Claude, ChatGPT, CoPilot, and proprietary LLMs) into web production and analytics reporting workflows, accelerating development velocity and contributing to a 15% uplift in organic demo/trial conversions."),
        ("Multi-National Platform & Operating Model Migration: ", "Led large-scale platform migration and operating model transition across 34 countries and 14 languages, integrating Marketo, Tealium, GTM, and Google Analytics, improving page load time by 40%, increasing organic sessions by 10%, and driving 15% growth in web-sourced pipeline."),
        ("CRO Roadmap & Customer Journey Optimization: ", "Owned global web analytics and CRO experimentation roadmap, leveraging advanced analytics and A/B testing to optimize high-impact customer journeys (homepage, solutions, pricing, demo/trial flows) to deliver sustained conversion growth."),
        ("Cross-Functional Campaign & Web Alignment: ", "Partnered closely with product marketing, demand generation, UX design, and regional web teams to align digital experiences with global campaigns, enabling integrated launches and boosting landing-page conversion by 10%."),
        ("Unified Cross-Functional Governance Framework: ", "Established a common collaboration framework for Developers, Marketers, Editors, and External Agencies to streamline web project intake, elevate delivery execution, and enhance operational efficiency."),
        ("Budgeting & Strategic Ecosystem Governance: ", "Responsible for developing budgets for strategic initiatives and multi-year roadmaps across the global web ecosystem, ensuring technology investments align with corporate revenue goals.")
    ],
    "handmark_bullets": [
        ("Full Web Storefront Lifecycle: ", "Oversaw end-to-end business management and full development lifecycle of global web-based products, including online and on-device storefronts for {{PREVIOUS_COMPANY_2}}, Sprint, and enterprise partners."),
        ("Product Strategy & Go-To-Market Execution: ", "Executed web product strategy by analyzing market conditions, creating go-to-market plans, and developing detailed functional requirements, wireframes, and customer use cases.")
    ],
    "mapsco_bullets": [
        ("Digital Revenue & Campaign Growth: ", "Directed e-commerce and web marketing (SEO, SEM, email, marketplaces), testing offers and UX flows to drive 35%+ annual online sales growth and significantly increase repeat purchase and average order value.")
    ],
    "cover_letter": {
        "date": "August 7, 2026",
        "recipient": "Hiring Team & VP of Marketing\nDatabricks Inc.\nRemote / Global (Req ID: MKTQ327R30)",
        "salutation": "Dear Databricks Hiring Team,",
        "paragraphs": [
            "I am writing to express my strong candidacy for the Director, Web Marketing position at Databricks (Job ID: 8638642002). As Global Web Marketing Director of Development at {{PREVIOUS_COMPANY_1}} (June 2008 - August 2026), I have spent over 18 years leading enterprise web strategy, multi-national platform migrations across 34 countries, and AI-driven search transformation. Databricks’ vision to evolve its web properties to serve both human visitors and AI agents/assistants aligns perfectly with my background in structuring machine-readable web content, scaling Generative Engine Optimization (GEO), and operationalizing web development velocity.",
            "Throughout my tenure at {{PREVIOUS_COMPANY_1}}, I have owned the global web channel as a primary pipeline engine. Recognizing the shift toward AI-driven discovery, I pioneered our Generative Engine Optimization (GEO) and Answer Engine Optimization (AEO) strategies, increasing company presence across AI search engines by 40% while lifting organic demo/trial conversions by 15%. Additionally, I led a large-scale platform migration across 14 languages, integrating Marketo, Tealium, and Google Analytics, improving page load speed by 40% and driving 15% growth in web-sourced pipeline. To ensure operational excellence, I established a common collaboration framework uniting developers, marketers, editors, and external agencies to streamline project intake and speed execution.",
            "Reporting to the VP of Marketing, I am eager to bring my deep technical experience, web architecture vision, and team governance to Databricks. I thrive in scale-oriented environments and look forward to building a high-performing web product organization that turns Databricks’ global web presence into an unmatched commercial and AI-native growth engine.",
            "Thank you for your time and consideration. I welcome the opportunity to discuss how my experience in web strategy, machine readability, and digital leadership will drive immediate impact for Databricks."
        ]
    }
}

SIXFLAGS_PAYLOAD = {
    "company": "Six Flags",
    "folder": "Six Flags",
    "role": "VP Digital and Ecommerce",
    "headline": "VICE PRESIDENT, DIGITAL & ECOMMERCE | GLOBAL DIGITAL EXPERIENCE STRATEGY",
    "summary": "Senior transformation and digital operations leader based in {{YOUR_CITY_STATE}} with 18+ years leading enterprise web platforms, e-commerce storefronts, mobile app customer experiences, and cross-functional technology teams. Proven track record owning global web channels as primary demand generation and revenue engines, unifying product management, web development, UX design, and marketing operations to maximize customer conversion, engagement, and LTV. Experienced in driving multi-national platform modernizations, high-velocity checkout conversion rate optimization (CRO), and data-driven digital operations.",
    "areas_of_expertise": [
        ("Digital Commerce & Web Architecture: ", "Enterprise Web Platforms (AEM, Sanity, WordPress, Drupal), E-Commerce Storefronts, Mobile App Customer Journeys, User Account Portals, Merchandising Funnels."),
        ("E-Commerce Optimization & CRO: ", "Checkout Conversion Rate Optimization (CRO), A/B & Multivariate Testing Roadmaps, Customer Experience Design, Conversion Funnel Velocity, Retention Operations."),
        ("MarTech & Systems Analytics: ", "Marketing Automation Integration (Marketo, Tealium, GA4, GTM), REST APIs, Web Security & Governance, Scalable Web Infrastructure."),
        ("Executive Leadership & Operations: ", "Cross-Functional Leadership (Developers, Marketers, UX, Executives), Agile Program Management, Budget Management ($1M+), Performance Reporting.")
    ],
    "trend_micro_bullets": [
        ("Global Web & Digital Operations Leadership: ", "Led global digital operations and transformation leadership for {{PREVIOUS_COMPANY_1}}'s B2B and B2C enterprise portfolios, owning the corporate web channel as the primary demand generation and digital revenue engine across development, operations, analytics, and marketing."),
        ("Enterprise E-Commerce & CRO Roadmap: ", "Owned global web analytics and CRO experimentation roadmap, executing 40+ annual A/B tests across pricing, solution pages, and checkout flows, increasing self-serve digital trial signups by 42% and web-sourced pipeline by 35%."),
        ("Multi-National Platform Migration: ", "Spearheaded enterprise web platform migration across 34 countries and 14 languages, integrating Marketo, Tealium, GTM, and GA4, reducing page load times by 40% and driving 15% growth in digital pipeline contribution."),
        ("AI Technology & Content Velocity: ", "Integrated Artificial Intelligence technologies (Claude, ChatGPT, CoPilot) into digital marketing workflows and content operations, accelerating production velocity and boosting organic conversions by 15%."),
        ("Unified Cross-Functional Framework: ", "Established a common collaboration framework for Developers, Marketers, Product Editors, and External Agencies to streamline intake, improve delivery execution, and enhance operational efficiency across regional markets.")
    ],
    "handmark_bullets": [
        ("Mobile App & Storefront Merchandising: ", "Managed product lifecycle and digital storefront operations for mobile app software distributor in Southlake, TX, aligning functional requirements, wireframes, and customer journeys to increase e-commerce checkout conversion rate by +34%."),
        ("Go-To-Market & UX Execution: ", "Executed product strategy across online and on-device stores for {{PREVIOUS_COMPANY_2}} and enterprise partners (Sprint), driving a 30% increase in product-led engagement and repeat transactions.")
    ],
    "mapsco_bullets": [
        ("Multi-Channel E-Commerce Growth: ", "Directed corporate e-commerce and web marketing (SEO, SEM, email, marketplaces) at {{PREVIOUS_COMPANY_3}} in Addison, TX, testing UX offers and checkout flows to sustain 35%+ annual online sales growth and significantly elevate average order value (AOV).")
    ],
    "cover_letter": {
        "date": "August 7, 2026",
        "recipient": "Selection Committee & Marketing Leadership\nSix Flags Entertainment Corporation\nCorporate Office | Arlington, TX",
        "salutation": "Dear Six Flags Selection Committee,",
        "paragraphs": [
            "I am writing to express my strong enthusiasm for the Vice President, Digital & Ecommerce position at Six Flags Entertainment Corporation. Living in {{YOUR_CITY_STATE}}, just minutes from your corporate headquarters in Arlington, I have spent over 18 years leading enterprise web strategy, e-commerce storefronts, mobile app customer journeys, and digital marketing operations. Six Flags' vision to build a scalable, seamless digital experience across web properties, mobile app platforms, guest account portals, and digital sales channels connects directly with my background in driving digital operations and commercial revenue growth.",
            "Throughout my 18-year tenure as Global Web Marketing Director of Development at {{PREVIOUS_COMPANY_1}} (June 2008 - August 2026), I built a reputation for unifying technology, product management, UX design, and commercial marketing teams. I owned our corporate web channel as a primary demand generation engine, executing A/B testing roadmaps that increased digital conversion rates by 42% and leading a multi-national platform migration across 34 countries that reduced page load times by 40%. Prior to {{PREVIOUS_COMPANY_1}}, I served as Senior Web Producer & E-Commerce Manager at {{PREVIOUS_COMPANY_2}} in Southlake, TX, where I managed digital storefronts for mobile app products and partner channels (Sprint), increasing e-commerce checkout conversion rates by +34%.",
            "Reporting to marketing leadership, I am eager to bring my deep digital experience, e-commerce background, and Arlington-area executive presence to Six Flags. I thrive in scale-oriented environments and look forward to leading digital and e-commerce teams to maximize guest engagement, conversion velocity, and brand loyalty.",
            "Thank you for your time and consideration. I welcome the opportunity to discuss how my background in digital leadership, e-commerce growth, and DFW presence will drive immediate impact for Six Flags."
        ]
    }
}

GRAFANA_PAYLOAD = {
    "company": "Grafana Labs",
    "folder": "Grafana Labs",
    "role": "Senior Manager Web Technology",
    "headline": "SENIOR MANAGER, WEB TECHNOLOGY | GLOBAL DIGITAL PLATFORM & AI LEADER",
    "summary": "Accomplished Web Technology & Engineering Leader with 18+ years managing enterprise web platform strategy, digital architecture, AI-first web transformation, and cross-functional engineering teams. Proven track record owning global corporate web properties (grafana.com scale) as primary demand generation and pipeline engines. Expert in building AI-enabled web systems (Claude, ChatGPT, CoPilot, GEO/AEO), modern frontend engineering, CMS content operations (Sanity, AEM, WordPress, Drupal), structured content guardrails, and predictable delivery cadences.",
    "areas_of_expertise": [
        ("AI-First Web Transformation: ", "AI Assistant & LLM Content Optimization (GEO/AEO), AI-Assisted Development Workflows, Automated QA & Content Operations, Generative Web Personalization."),
        ("Enterprise Web Architecture & Delivery: ", "Global Web Ecosystem Architecture (grafana.com scale), Enterprise CMS Governance (Sanity, AEM, WordPress, Drupal), Next.js / React Platform Modernization, Performance & Reliability."),
        ("Self-Serve Web Operations & Governance: ", "Reusable UI Component Standards, Content & UX Guardrails, Automated Intake Cadences, Cross-Functional Developer & Marketing Alignment."),
        ("Engineering Leadership & Team Development: ", "Hiring, Coaching & Developing Web Engineers, Agile Sprint Execution, Budget Management ($1M+), All-Remote Distributed Leadership.")
    ],
    "trend_micro_bullets": [
        ("Global Web Platform Leadership & Velocity: ", "Led global digital operations and web development teams for {{PREVIOUS_COMPANY_1}}'s B2B and B2C enterprise portfolios, owning the corporate web ecosystem as the primary demand generation and pipeline engine across engineering, analytics, and marketing."),
        ("AI-First Web Strategy & GEO Dominance: ", "Spearheaded the evolution of global web properties into AI-ready platforms, structuring content for machine readability across AI search tools (GEO/AEO) to increase brand presence by 40% and organic conversions by 15%."),
        ("AI Technology Integration & Engineering Velocity: ", "Integrated Artificial Intelligence (AI) technologies (Claude, ChatGPT, CoPilot) into web engineering and content production workflows, accelerating development velocity by 30% and reducing coordination overhead."),
        ("Multi-National Platform Migration: ", "Led enterprise web platform migration across 34 countries and 14 languages, integrating Marketo, Tealium, GTM, and GA4, reducing page load times by 40% and driving 15% growth in web-sourced pipeline."),
        ("Self-Serve Web Operations & Guardrails: ", "Established reusable CMS component models, UX guardrails, and automated intake cadences, empowering marketing and content editors to launch campaigns independently while maintaining strict quality and security standards.")
    ],
    "handmark_bullets": [
        ("Web & Mobile Storefront Engineering: ", "Oversaw end-to-end development lifecycle and digital product operations for {{PREVIOUS_COMPANY_2}} in Southlake, TX, designing web architecture and checkout funnels for mobile app software stores (Sprint) that increased e-commerce conversion rates by +34%."),
        ("Go-To-Market & Functional Specification: ", "Defined functional requirements, wireframes, and customer use cases across web and mobile app products, driving a 30% increase in product engagement.")
    ],
    "mapsco_bullets": [
        ("Digital Revenue & Sales Growth: ", "Directed corporate e-commerce and web marketing at {{PREVIOUS_COMPANY_3}} in Addison, TX, optimizing web architecture and checkout flows to sustain 35%+ annual online sales growth.")
    ],
    "cover_letter": {
        "date": "August 7, 2026",
        "recipient": "Selection Committee & Web Engineering Leadership\nGrafana Labs\nRemote / United States (Req ID: 5999936004)",
        "salutation": "Dear Grafana Labs Selection Committee,",
        "paragraphs": [
            "I am writing to express my strong enthusiasm for the Senior Manager, Web Technology position at Grafana Labs (Req ID: 5999936004). As Global Web Marketing Director of Development at {{PREVIOUS_COMPANY_1}} (June 2008 - August 2026), I have spent over 18 years leading enterprise web strategy, engineering teams, and AI-enabled digital transformation. Grafana Labs' vision to evolve grafana.com into an AI-first, agent-ready platform optimized for both humans and LLMs connects directly with my background in structuring machine-readable web content, scaling web development velocity, and building self-serve web operations.",
            "Throughout my tenure at {{PREVIOUS_COMPANY_1}}, I owned our corporate web channel as a primary commercial and brand engine. Recognizing the shift toward AI-driven discovery, I pioneered our Generative Engine Optimization (GEO) and Answer Engine Optimization (AEO) initiatives, increasing company presence across AI assistants by 40% while lifting organic trial conversions by 15%. Embracing AI as a core productivity multiplier, I integrated AI platforms (Claude, ChatGPT, CoPilot) into our engineering workflows, accelerating production velocity by 30%. Additionally, I spearheaded a multi-national platform migration across 34 countries, establishing reusable CMS component models and automated intake cadences that enabled marketing teams to publish self-serve without compromising quality or performance.",
            "Prior to {{PREVIOUS_COMPANY_1}}, I served as Product Manager of Web and E-commerce at {{PREVIOUS_COMPANY_2}} in Southlake, TX, where I managed digital storefront development across web and mobile partner channels (Sprint), boosting checkout conversion rates by +34%. I thrive in 100% remote, open-culture environments and am eager to bring my web engineering leadership, AI transformation experience, and operational discipline to lead the web technology team at Grafana Labs.",
            "Thank you for your time and consideration. I welcome the opportunity to discuss how my experience in web platform architecture, AI-first transformation, and team leadership will drive immediate impact for grafana.com."
        ]
    }
}

MOUSER_PAYLOAD = {
    "company": "Mouser Electronics",
    "folder": "Mouser Electronics",
    "role": "Web Software Development Director",
    "headline": "WEB SOFTWARE DEVELOPMENT DIRECTOR | GLOBAL ECOMMERCE & DIGITAL PLATFORMS LEADER",
    "summary": "Executive Web Software Development and Digital Engineering Leader based in {{YOUR_CITY_STATE}} (minutes from Mansfield HQ) with 18+ years managing enterprise e-commerce platforms, web software architecture, customer experience engineering, and cross-functional technology teams. Proven track record owning global web channels as primary demand generation and revenue engines at {{PREVIOUS_COMPANY_1}} (18+ years in global web marketing development). Expert in modernizing web software architectures, conversion rate optimization (CRO), CMS platform modernizations (AEM, Sanity, WordPress, Drupal), AI-assisted development velocity (Claude, Cursor, CoPilot, GEO/AEO), and high-scale digital customer experiences.",
    "areas_of_expertise": [
        ("E-Commerce Software Architecture: ", "High-Impact Digital E-Commerce Platforms, Web Software Engineering, Microservices & API Integration, System Resilience & Scalability, Modernization Roadmaps."),
        ("Conversion Rate Optimization & CRO: ", "Checkout Conversion Rate Optimization (CRO), A/B & Multivariate Testing, Customer Experience Design, High-Velocity Merchandising Funnels, User Account Portals."),
        ("AI Engineering & Development Velocity: ", "AI Coding Assistants (Cursor, Claude Code, CoPilot), AI Assistant & LLM Content Optimization (GEO/AEO), Automated Testing Workflows, Content-to-Code Speed."),
        ("Software Team Leadership & Governance: ", "Cross-Functional Engineering Management (Developers, Marketers, UX Designers, Executives), Agile Sprint Cadences, Budget Management ($1M+), DFW Leadership.")
    ],
    "trend_micro_bullets": [
        ("Global Web Software Engineering & Operations Leadership: ", "Led global web software development and digital engineering teams for {{PREVIOUS_COMPANY_1}}'s enterprise B2B and B2C web platforms (June 2008 - August 2026), owning corporate e-commerce and digital channels as primary demand generation and revenue engines."),
        ("Enterprise E-Commerce Architecture & CRO Roadmap: ", "Owned global web software architecture and CRO experimentation roadmap, executing 40+ annual A/B tests across checkout flows, pricing, and solution portals, increasing self-serve digital conversions by 42% and pipeline contribution by 35%."),
        ("Multi-National Platform Modernization: ", "Spearheaded enterprise web platform modernization across 34 countries and 14 languages, integrating Marketo, Tealium, GTM, and GA4, reducing page load times by 40% and driving 15% growth in web-sourced revenue."),
        ("AI Technology Integration & Development Velocity: ", "Integrated Artificial Intelligence technologies (Claude, Cursor, CoPilot) into web engineering and analytics workflows, accelerating software development velocity by 30% and reducing time-to-market for digital capabilities."),
        ("Cross-Functional Governance & Delivery Cadences: ", "Established a unified collaboration framework for software engineers, product managers, UX designers, and external agencies to streamline project intake, elevate software quality, and enhance operational efficiency.")
    ],
    "handmark_bullets": [
        ("E-Commerce Storefront & Mobile App Engineering: ", "Managed web software product lifecycle and digital storefront development for {{PREVIOUS_COMPANY_2}} in Southlake, TX, engineering checkout funnels for partner channels (Sprint) that boosted e-commerce conversion rates by +34%."),
        ("Functional Specification & Go-To-Market Execution: ", "Defined software functional requirements, wireframes, and customer use cases across web and mobile app products, driving a 30% increase in product-led customer engagement.")
    ],
    "mapsco_bullets": [
        ("E-Commerce Revenue & Sales Growth: ", "Directed corporate e-commerce software and web marketing at {{PREVIOUS_COMPANY_3}} in Addison, TX, optimizing web architecture and checkout flows to sustain 35%+ annual online sales growth.")
    ],
    "cover_letter": {
        "date": "August 11, 2026",
        "recipient": "Selection Committee & Technology Leadership\nMouser Electronics, Inc.\nCorporate Headquarters | Mansfield, TX (Req ID: 30834)",
        "salutation": "Dear Mouser Selection Committee,",
        "paragraphs": [
            "I am writing to express my strong enthusiasm for the Web Software Development Director position at Mouser Electronics (Job ID: 30834). Living in {{YOUR_CITY_STATE}}, just minutes from your corporate headquarters in Mansfield, I have spent over 18 years leading enterprise web software development, digital e-commerce platforms, customer experience engineering, and cross-functional technology teams. Mouser's mission to lead the evolution of a high-impact digital e-commerce platform and shape the future of how customers engage at scale connects directly with my hands-on experience modernizing architectures, evolving engineering practices, and driving measurable commercial growth.",
            "Throughout my 18-year tenure as Global Web Marketing Director of Development at {{PREVIOUS_COMPANY_1}} (June 2008 - August 2026), I built a reputation for unifying software engineering, product management, UX design, and commercial leadership. I owned our global corporate web channels as primary demand generation and e-commerce engines, executing A/B testing roadmaps that increased digital conversion rates by 42% and leading a multi-national platform modernization across 34 countries that reduced page load times by 40%. Embracing AI as a core development multiplier, I integrated AI coding copilots (Cursor, Claude, CoPilot) into our software engineering workflows, accelerating development velocity by 30% while pioneering machine-readable web content strategies (GEO/AEO) that boosted organic search presence by 40%.",
            "Prior to {{PREVIOUS_COMPANY_1}}, I served as Product Manager of Web and E-commerce at {{PREVIOUS_COMPANY_2}} in Southlake, TX, where I managed digital storefront software development across web and mobile partner channels (Sprint), boosting checkout conversion rates by +34%. I thrive in high-scale environments and am eager to bring my web software development background, e-commerce architecture experience, and DFW executive presence to lead Mouser's software engineering team in Mansfield.",
            "Thank you for your time and consideration. I welcome the opportunity to discuss how my experience in web software engineering, e-commerce modernization, and DFW leadership will drive immediate impact for Mouser Electronics."
        ]
    }
}

NEO_SECURITY_PAYLOAD = {
    "company": "Neo Security Inc",
    "folder": "Neo Security",
    "role": "Director Web and Digital",
    "headline": "DIRECTOR, WEB & DIGITAL | GLOBAL WEB STRATEGY, AEO & AI TRANSFORMATION LEADER",
    "summary": "Executive web marketing, technology, and SEO leader with 18+ years managing enterprise B2B SaaS web platforms, organic search growth, and AI-driven answer engine optimization (AEO/GEO across ChatGPT, Perplexity, Gemini, and Claude). Proven track record owning corporate websites as primary pipeline engines at {{PREVIOUS_COMPANY_1}} (18+ years in global cybersecurity web marketing development). Expert in website architecture, conversion rate optimization (CRO), content-to-code velocity using modern AI coding copilots (Cursor, Claude Code), and managing remote teams and agency partners.",
    "areas_of_expertise": [
        ("Web Strategy & AEO / GEO Dominance: ", "Answer Engine Optimization (AEO), Generative Engine Optimization (GEO), Content Schema & Information Architecture for LLMs, Technical & On-Page SEO."),
        ("Enterprise B2B SaaS Web Architecture: ", "Corporate Site Architecture, CMS Governance (Sanity, AEM, WordPress, Drupal), Landing Page Velocity, Conversion Rate Optimization (CRO), A/B Testing Roadmaps."),
        ("AI Technology Integration & Velocity: ", "AI Coding Assistants (Cursor, Claude Code), Content & SEO AI Tooling, Modern No-Code/Low-Code Builders, Automated Analytics Workflows."),
        ("Marketing Technology & Revenue Attribution: ", "GA4, Search Console, Ahrefs/Semrush, Google/Bing PPC Operations, Pipeline Attribution, Cross-Functional Team Leadership.")
    ],
    "trend_micro_bullets": [
        ("Global Web & Digital Operations Leadership: ", "Led global web marketing development for {{PREVIOUS_COMPANY_1}}'s B2B and B2C enterprise portfolios (18+ years in cybersecurity), owning the corporate web channel as the primary demand generation and pipeline engine across architecture, SEO, analytics, and content velocity."),
        ("AI Search & Answer Engine Optimization (AEO/GEO): ", "Spearheaded Generative Engine Optimization (GEO) and Answer Engine Optimization (AEO) initiatives across global web properties, structuring content schema and information architecture for LLMs to increase AI search presence by 40% and organic conversions by 15%."),
        ("Content-to-Code Velocity & AI Tooling: ", "Integrated modern AI tools (Claude, Cursor, CoPilot) into web development and content workflows, accelerating landing page velocity by 30% and reducing time-to-market for campaigns."),
        ("Multi-National Platform Migration & CRO: ", "Led enterprise web platform migration across 34 countries and 14 languages, integrating Marketo, Tealium, GTM, and GA4, reducing page load times by 40% and driving 15% growth in web-sourced pipeline."),
        ("Cross-Functional Governance & Remote Team Leadership: ", "Established a unified collaboration framework for developers, marketers, editors, and external agencies to streamline project intake, elevate execution quality, and manage remote digital operations.")
    ],
    "handmark_bullets": [
        ("Web Storefront & E-Commerce Operations: ", "Oversaw product management and web storefront operations for mobile app distributor in Southlake, TX, designing UX flows and checkout funnels for partner channels (Sprint) that increased e-commerce conversion rates by +34%."),
        ("Go-To-Market & UX Functional Specification: ", "Defined functional requirements, wireframes, and customer use cases across web and mobile app products, driving a 30% increase in product engagement.")
    ],
    "mapsco_bullets": [
        ("Digital Revenue & Sales Growth: ", "Directed corporate e-commerce and web marketing at {{PREVIOUS_COMPANY_3}} in Addison, TX, optimizing web architecture and checkout flows to sustain 35%+ annual online sales growth.")
    ],
    "cover_letter": {
        "date": "August 10, 2026",
        "recipient": "Selection Committee & Executive Leadership\nNeo Security Inc.\nRemote - USA (Job ID: 4323676009)",
        "salutation": "Dear Neo Security Selection Committee,",
        "paragraphs": [
            "I am writing to express my strong enthusiasm for the Director, Web & Digital (Director, Web & AEO) position at Neo Security Inc. (Job ID: 4323676009). As Global Web Marketing Director of Development at {{PREVIOUS_COMPANY_1}} (June 2008 - August 2026), I have spent over 18 years leading enterprise B2B cybersecurity web strategy, organic search growth, and AI-driven digital transformation. Neo Security's mission to build a high-converting digital front door while leading the industry in Answer Engine Optimization (AEO across ChatGPT, Perplexity, Gemini, and AI Overviews) connects directly with my hands-on experience structuring machine-readable content, accelerating development velocity with AI tools, and driving measurable pipeline growth.",
            "Throughout my 18-year tenure at {{PREVIOUS_COMPANY_1}}, I owned our corporate web channel as a primary revenue and trust engine for security buyers. Recognizing the fundamental shift toward AI-driven search, I pioneered our Generative Engine Optimization (GEO) and Answer Engine Optimization (AEO) strategies, structuring content schema and information architecture to increase brand presence across AI assistants by 40% while lifting organic trial/demo conversions by 15%. A firm believer in AI-assisted velocity, I integrated AI coding copilots (Cursor, Claude, CoPilot) into our web production workflows, reducing landing page launch times by 30%. Additionally, I led a multi-national platform migration across 34 countries, managing third-party development partners and integrating GA4, Marketo, and Tealium to drive 15% growth in web-sourced pipeline.",
            "Having spent 18+ years in the B2B cybersecurity space, I possess deep empathy for technical security buyer personas (CISOs, security engineers, IT leaders) and understand that technical credibility is everything. I thrive in hands-on, builder-oriented remote environments where modern AI tools are used to ship high-impact digital experiences rapidly.",
            "Thank you for your time and consideration. I welcome the opportunity to discuss how my cybersecurity web leadership, AEO expertise, and hands-on AI workflow execution will drive immediate pipeline growth for Neo Security Inc."
        ]
    }
}


SPINUTECH_PAYLOAD = {
    "company": "Spinutech",
    "folder": "Spinutech",
    "role": "Vice President of Digital Strategy",
    "headline": "VICE PRESIDENT OF DIGITAL STRATEGY | GLOBAL DIGITAL EXPERIENCE & AI LEADER",
    "summary": "Executive digital leader with 18+ years leading cross-functional teams, digital transformation roadmaps, and AI-first activation strategies across enterprise web ecosystems. Proven track record unifying multi-disciplinary service lines (SEO/GEO/AEO, CRO, Data Analytics, Content Operations, MarTech) to transform web channels into high-velocity demand generation and commercial revenue engines. Expert in embedding Generative AI (Claude Code, ChatGPT, CoPilot, LLMs) into digital marketing workflows, establishing scalable operational frameworks, and driving strategic client growth.",
    "areas_of_expertise": [
        ("Executive Digital Leadership & Strategy: ", "Cross-Disciplinary Team Management (SEO/GEO, Paid Media, Data Science, CRO, Engineering), Agency & Enterprise Digital Transformation, Strategic Account Advisory."),
        ("AI Integration & Digital Innovation: ", "Generative Engine Optimization (GEO/AEO), AI-Assisted Marketing Workflows (Claude, ChatGPT, CoPilot), Automated Personalization & Analytics."),
        ("Conversion Rate Optimization & Analytics: ", "High-Velocity A/B Testing Roadmaps, Customer Experience (CX) Architecture, Multi-Site Funnel Velocity, GA4 / GTM Data Governance."),
        ("Operational Scaling & Growth: ", "Resource Utilization & Capacity Planning, Agency Pitch & Proposal Leadership, Cross-Functional Alignment (Developers, Marketers, UX, C-Suite).")
    ],
    "trend_micro_bullets": [
        ("Global Web & Digital Strategy Leadership: ", "Led global digital marketing and web strategy for {{PREVIOUS_COMPANY_1}}'s B2B and B2C enterprise portfolios, managing a 13+ person cross-functional team across development, DevOps, QA, BA, and SEO to own the web channel as the primary demand generation and pipeline engine."),
        ("Next-Gen DXP Discovery & Evaluation: ", "Led discovery, architectural evaluation, ROI analysis, and executive vendor decision-making for a next-generation Digital Experience Platform (DXP) to replace legacy Adobe Experience Manager (AEM), aligning C-suite stakeholders around modern API architecture and TCO optimization."),
        ("TrendAI Redesign & Sanity CMS Platform Migration: ", "Organized and executed the end-to-end redesign and platform migration of the TrendAI website onto Sanity CMS, establishing structured content models, modern headless workflows, and rapid publishing cadences for AI product launches."),
        ("AI-First Innovation & GEO/AEO Integration: ", "Championed AI technologies (Claude, ChatGPT, CoPilot, LLMs) and Generative Engine Optimization (GEO/AEO), driving a 40% increase in brand search presence and a +15% uplift in organic demo/trial conversions."),
        ("Enterprise Platform Modernization & Performance: ", "Directed end-to-end redesign and AEM 6.x migration across 34 countries and 14 languages, integrating Marketo, Tealium, GTM, mPulse, Cludo, and GA4 to reduce page load times by 40%, boost organic sessions by 10%, and drive 15% pipeline growth."),
        ("High-Velocity CRO & Landing Page Optimization: ", "Owned web analytics and CRO roadmaps, executing A/B testing frameworks across pricing and solution flows while aligning regional marketing teams to increase campaign landing page conversions by +10% and digital trial signups by 42%.")
    ],
    "handmark_bullets": [
        ("Digital Product Strategy & Storefront Management: ", "Oversaw end-to-end business management and product lifecycle for mobile app software distributor in Southlake, TX, designing web architecture and checkout funnels for mobile app stores (Sprint) that increased e-commerce checkout conversion rate by +34%."),
        ("Go-To-Market & Consultative Alignment: ", "Executed product strategy across online and on-device stores, defining functional requirements, wireframes, and customer use cases to drive a 30% increase in product-led engagement.")
    ],
    "mapsco_bullets": [
        ("Cross-Channel Digital Marketing & Revenue Growth: ", "Directed corporate e-commerce and web marketing (SEO, SEM, email, marketplaces) at {{PREVIOUS_COMPANY_3}} in Addison, TX, testing offers and UX flows to sustain 35%+ annual online sales growth and significantly elevate average order value (AOV).")
    ],
    "cover_letter": {
        "date": "August 12, 2026",
        "recipient": "Executive Selection Committee & Leadership Team\nSpinutech\nRemote Executive Office | USA",
        "salutation": "Dear Spinutech Leadership Team,",
        "paragraphs": [
            "I am writing to express my strong enthusiasm for the Vice President of Digital Strategy position at Spinutech. With over 18 years of experience leading cross-functional digital marketing teams, digital transformation roadmaps, enterprise web platforms, and AI-first activation strategies, I connect directly with Spinutech's mission to lead, performance-optimize, and evolve multi-disciplinary digital teams across SEO/GEO, Paid Media, Data Science, CRO, and Content Operations.",
            "Throughout my 18-year tenure as Global Web Marketing Director of Development at {{PREVIOUS_COMPANY_1}} (June 2008 - August 2026), I built a high-performing global organization of 13+ cross-functional specialists (development, DevOps, QA, BA, SEO). I owned our corporate web channel as the primary demand generation engine, directing a 34-country AEM 6.x migration that reduced page load times by 40% while executing CRO testing roadmaps that increased self-serve digital trial signups by 42%. Recognizing the shift toward intelligent search, I championed AI technologies (Claude, ChatGPT, CoPilot, LLMs) and Generative Engine Optimization (GEO/AEO), driving a 40% increase in search visibility and a +15% uplift in organic demo conversions.",
            "Prior to {{PREVIOUS_COMPANY_1}}, I served as Product Manager of Web and E-commerce at {{PREVIOUS_COMPANY_2}} in Southlake, TX, where I managed digital storefronts for mobile app products and partner channels (Sprint), boosting checkout conversion rates by +34%. My background combines executive digital consulting, deep technical fluency across enterprise MarTech ecosystems, and a proven track record leading cross-disciplinary teams to deliver measurable commercial impact for clients.",
            "Thank you for your time and consideration. I welcome the opportunity to discuss how my background in digital strategy, AI innovation, and executive leadership will drive immediate value for Spinutech and your client portfolio."
        ]
    }
}


JOBGETHER_FVP_PAYLOAD = {
    "company": "Jobgether",
    "folder": "Jobgether",
    "role": "FVP Digital Transformation Office",
    "headline": "FVP, DIGITAL TRANSFORMATION OFFICE | GLOBAL DIGITAL EXPERIENCE & AI LEADER",
    "summary": "Executive digital transformation leader with 18+ years leading enterprise web strategy, digital product operations, fintech/martech modernization, and cross-functional technology teams. Proven track record defining multi-year digital transformation roadmaps, establishing governance frameworks, and unifying product management, UX design, engineering, analytics, and SEO to maximize acquisition, engagement, and retention. Expert in evaluating emerging AI technologies (Claude Code, ChatGPT, CoPilot, GEO/AEO), modernizing legacy digital architectures, and managing strategic vendor/fintech partnerships.",
    "areas_of_expertise": [
        ("Enterprise Digital Transformation Strategy: ", "Multi-Year Transformation Roadmaps, Digital Architecture Modernization, Executive Business Case Governance, Cross-Functional Alignment."),
        ("Digital Product & Channel Innovation: ", "Member-Facing Customer Portals, Digital Account Opening, Mobile & Web Experience Design (UX/CX), Conversion Rate Optimization (CRO)."),
        ("AI Activation & Emerging MarTech: ", "Generative Engine Optimization (GEO/AEO), AI-Assisted Workflows (Claude, ChatGPT, CoPilot), Next-Gen DXP / Headless CMS Modernization."),
        ("Executive Governance & Team Leadership: ", "Cross-Disciplinary Team Management (Dev, DevOps, QA, BA, SEO), Risk & Compliance Alignment, Strategic Vendor & Fintech Partner Management.")
    ],
    "trend_micro_bullets": [
        ("Enterprise Digital Transformation Leadership: ", "Led global web marketing and digital transformation leadership for {{PREVIOUS_COMPANY_1}}'s enterprise B2B and B2C portfolios, managing a 13+ person cross-functional team (Development, DevOps, QA, BA, SEO) to own the corporate web channel as the primary revenue and pipeline engine."),
        ("Next-Gen DXP Discovery & Decision-Making: ", "Led discovery, architectural evaluation, ROI analysis, and executive vendor decision-making for a next-generation Digital Experience Platform (DXP) to replace legacy Adobe Experience Manager (AEM), aligning C-suite stakeholders around modern API architecture and TCO optimization."),
        ("TrendAI Redesign & Sanity CMS Platform Migration: ", "Organized and executed the end-to-end redesign and platform migration of the TrendAI website onto Sanity CMS, establishing structured content models, modern headless workflows, and rapid publishing cadences."),
        ("AI-First Innovation & GEO/AEO Integration: ", "Championed AI technologies (Claude, ChatGPT, CoPilot, LLMs) and Generative Engine Optimization (GEO/AEO), driving a 40% increase in brand search presence and a +15% uplift in organic demo/trial conversions."),
        ("Multi-National Platform Modernization & Performance: ", "Directed enterprise web platform migration across 34 countries and 14 languages, integrating Marketo, Tealium, GTM, mPulse, Cludo, and GA4 to reduce page load times by 40%, boost organic sessions by 10%, and drive 15% pipeline growth.")
    ],
    "handmark_bullets": [
        ("Digital Product Strategy & Storefront Management: ", "Oversaw end-to-end business management and product lifecycle for mobile app software distributor in Southlake, TX, designing web architecture and checkout funnels for mobile app stores (Sprint) that increased e-commerce checkout conversion rate by +34%."),
        ("Go-To-Market & Executive Alignment: ", "Executed product strategy across online and on-device stores, defining functional requirements, wireframes, and customer use cases to drive a 30% increase in product-led engagement.")
    ],
    "mapsco_bullets": [
        ("Digital Marketing & Revenue Optimization: ", "Directed corporate e-commerce and web marketing (SEO, SEM, email, marketplaces) at {{PREVIOUS_COMPANY_3}} in Addison, TX, testing offers and UX flows to sustain 35%+ annual online sales growth.")
    ],
    "cover_letter": {
        "date": "August 12, 2026",
        "recipient": "Executive Selection Committee & Digital Transformation Leadership\nJobgether / FourLeaf Federal Credit Union\nRemote Executive Office | USA (Job ID: 4449323011)",
        "salutation": "Dear Selection Committee,",
        "paragraphs": [
            "I am writing to express my strong enthusiasm for the FVP Digital Transformation Office position at FourLeaf Federal Credit Union (via Jobgether, Job ID: 4449323011). With over 18 years of experience leading enterprise digital transformation strategy, digital product management, technology modernization, and cross-functional technology teams, I connect directly with your mission to define, govern, and execute a multi-year digital transformation roadmap.",
            "Throughout my 18-year tenure as Global Web Marketing Director of Development at {{PREVIOUS_COMPANY_1}} (June 2008 - August 2026), I built a high-performing global organization of 13+ cross-functional specialists (development, DevOps, QA, BA, SEO). I owned our corporate web channel as the primary demand generation engine, directing a 34-country AEM 6.x migration that reduced page load times by 40% while leading the discovery, ROI evaluation, and decision-making for a next-gen DXP platform to replace legacy AEM. Additionally, I organized and executed the TrendAI site redesign and migration to Sanity CMS, while pioneering Generative Engine Optimization (GEO/AEO) strategies that increased search visibility by 40% and lifted organic demo conversions by +15%.",
            "Prior to {{PREVIOUS_COMPANY_1}}, I served as Product Manager of Web and E-commerce at {{PREVIOUS_COMPANY_2}} in Southlake, TX, where I managed digital storefront software development across web and mobile partner channels (Sprint), boosting checkout conversion rates by +34%. My background combines executive digital consulting, deep technical fluency across enterprise MarTech/FinTech ecosystems, and a proven track record leading cross-disciplinary teams through organizational change.",
            "Thank you for your time and consideration. I welcome the opportunity to discuss how my background in digital transformation, AI innovation, and executive leadership will drive immediate impact for the Digital Transformation Office."
        ]
    }
}


if __name__ == '__main__':
    payload_file = os.path.join(r".", "current_payload.json")
    
    parser = argparse.ArgumentParser(description="Master Application Package Generator for {{YOUR_FULL_NAME}}")
    parser.add_argument("--job", choices=["databricks", "sixflags", "grafana", "neosecurity", "mouser", "spinutech", "jobgether_fvp", "active"], default="active", help="Select target job payload")
    args = parser.parse_args()

    if os.path.exists(payload_file) and args.job == "active":
        print(f"Loading active payload from {payload_file}...")
        with open(payload_file, 'r', encoding='utf-8') as f:
            active_payload = json.load(f)
        build_package(active_payload)
    elif args.job == "databricks":
        build_package(DATABRICKS_PAYLOAD)
    elif args.job == "sixflags":
        build_package(SIXFLAGS_PAYLOAD)
    elif args.job == "grafana":
        build_package(GRAFANA_PAYLOAD)
    elif args.job == "neosecurity":
        build_package(NEO_SECURITY_PAYLOAD)
    elif args.job == "mouser":
        build_package(MOUSER_PAYLOAD)
    elif args.job == "spinutech":
        build_package(SPINUTECH_PAYLOAD)
    elif args.job == "jobgether_fvp" or args.job == "active":
        build_package(JOBGETHER_FVP_PAYLOAD)

