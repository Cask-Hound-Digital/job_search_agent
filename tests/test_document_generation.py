"""
Tests for Document Generation Engine.
Covers: 6-part cover letter generation, resume section rendering, zero em-dash compliance.
"""

import os
from docx import Document
from pypdf import PdfReader
from build_documents import generate_package, sanitize_text

def test_sanitize_text_zero_em_dash():
    raw = "Leadership \u2014 Architecture & Strategy &mdash; Execution"
    cleaned = sanitize_text(raw)
    assert "\u2014" not in cleaned
    assert "&mdash;" not in cleaned
    assert " - " in cleaned

def test_generate_package_produces_four_files(tmp_path, monkeypatch):
    out_dir = str(tmp_path / "output")
    monkeypatch.setattr("build_documents.OUTPUT_DIR", out_dir)

    target_company = "CyberDefenseCorp"
    target_role = "Director of Engineering"
    comp_dir = generate_package(target_company, target_role)

    expected_files = [
        f"Resume_{target_company}.docx",
        f"Resume_{target_company}.pdf",
        f"Cover_Letter_{target_company}.docx",
        f"Cover_Letter_{target_company}.pdf"
    ]
    for f in expected_files:
        assert os.path.exists(os.path.join(comp_dir, f))

    # Verify Resume DOCX contains required ATS sections
    doc_resume = Document(os.path.join(comp_dir, f"Resume_{target_company}.docx"))
    resume_text = "\n".join([p.text for p in doc_resume.paragraphs])
    assert "PROFESSIONAL SUMMARY" in resume_text
    assert "KEY SKILLS" in resume_text
    assert "PROFESSIONAL EXPERIENCE" in resume_text
    assert "EDUCATION" in resume_text
    assert "\u2014" not in resume_text

    # Verify Cover Letter DOCX contains 6-part hybrid structure
    doc_cl = Document(os.path.join(comp_dir, f"Cover_Letter_{target_company}.docx"))
    cl_text = "\n".join([p.text for p in doc_cl.paragraphs])
    assert f"Dear {target_company} Hiring Team," in cl_text
    assert target_role in cl_text
    assert "Sincerely," in cl_text
    assert "\u2014" not in cl_text
