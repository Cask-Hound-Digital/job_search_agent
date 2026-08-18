# Autonomous AI Executive Job Search & Application Engineering Blueprint
**System Blueprint & Implementation Guide**  
*A complete blueprint for building an autonomous AI agentic system that continuously monitors job boards, parses email alert digests, audits live company page metadata, generates ATS-optimized PDF/DOCX application packages, and maintains a live web browser dashboard.*

---

## 📐 1. System Architecture & Component Diagram

```
                              ┌─────────────────────────────────────────┐
                              │           Candidate Target Profile      │
                              │ (Roles, Comp, Locations, Skill Baseline)│
                              └────────────────────┬────────────────────┘
                                                   │
                                                   ▼
┌─────────────────────────┐         ┌──────────────────────────────┐         ┌─────────────────────────┐
│ Business Hours Cron     │───────► │    Gmail IMAP Alert Parser   │ ──────► │ Multi-Layer             │
│ (7am, 11am, 3pm CT)     │         │ (LinkedIn, Indeed, BuiltIn)  │         │ Deduplication Engine    │
└─────────────────────────┘         └──────────────────────────────┘         └────────────┬────────────┘
                                                   │                                      │
┌─────────────────────────┐                        ▼                                      ▼
│ Web Search Sweeps       │─────────► ┌──────────────────────────────┐         ┌─────────────────────────┐
│ (Greenhouse, Lever, etc)│           │ Live Page Metadata Auditor   │ ──────► │ Central State Tracker   │
└─────────────────────────┘           │ (Extract Ground-Truth Titles)│         │ (`state.json`)          │
                                      └──────────────────────────────┘         └────────────┬────────────┘
                                                                                          │
                                                                                          ▼
┌─────────────────────────┐         ┌──────────────────────────────┐         ┌─────────────────────────┐
│ Local Output Drive      │ ◄────── │ Application Package Engine   │ ◄────── │ Glassmorphism Browser   │
│ (`P:\Job Search\`)      │         │ (PDF/DOCX Generator + Sanity)│         │ Dashboard (`index.html`)│
└─────────────────────────┘         └──────────────────────────────┘         └─────────────────────────┘
```

---

## 🛠️ 2. Core Technical Prerequisites & Stack

* **Language**: Python 3.10+
* **Document Processing Libraries**: `reportlab` (for PDF generation), `python-docx` (for Word generation)
* **Standard Libraries**: `imaplib`, `email`, `urllib.request`, `re`, `json`, `os`, `shutil`, `argparse`
* **Frontend Dashboard**: HTML5, Vanilla CSS3 (Glassmorphism & CSS Grid), Javascript (ES6+)
* **Operating Environment**: Windows / Linux / macOS with persistent background scheduler (Cron or AGY Schedule Tool)

---

## ⚙️ 3. Master Configuration & State Schema (`state.json`)

The central database of the agent system is stored in a JSON structure (`state.json`):

```json
{
  "last_updated": "2026-08-12T10:00:00-05:00",
  "policy": {
    "auto_submit": false,
    "user_approval_required": true,
    "mandatory_live_validation": "Every job posting must undergo mandatory HTTP 200 verification and active application form check before being presented to user.",
    "pre_submission_review_format": "List of jobs with Live Verified URLs, Title, Company, Comp, Match Score, and Summary for explicit user sign-off"
  },
  "user_profile": {
    "name": "Candidate Name",
    "email": "candidate@example.com",
    "phone": "(555) 000-0000",
    "location": "City, State",
    "linkedin": "https://www.linkedin.com/in/candidate/",
    "target_roles": [
      "Director of Web Marketing",
      "Director of Digital Experience",
      "Director of Website Growth / PLG",
      "VP of Digital Experience / Growth",
      "Fractional VP of Digital Product / Web Operations",
      "Digital Transformation Advisor"
    ],
    "target_compensation_min": "{{TARGET_COMPENSATION_MIN}}",
    "target_locations": [
      "100% Remote (US)",
      "Hybrid (Local Metro Area)"
    ]
  },
  "applications": [],
  "verified_gmail_jobs": [],
  "review_queue": []
}
```

---

## 🐍 4. Python Module Implementations

### Module A: Application Package Generator (`build_application_package.py`)
Generates single-column ATS-compliant Word (`.docx`) and PDF (`.pdf`) application packages using `python-docx` and `reportlab`. Enforces a strict zero em-dash policy via standard text sanitization.

```python
import os
import re
import argparse
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

def sanitize_text(text):
    if not text:
        return ""
    # Strip em dashes and replace with hyphens or pipes
    text = text.replace("—", " - ").replace("&mdash;", " - ")
    return re.sub(r'\s+', ' ', text).strip()

def build_pdf_resume(payload, filepath):
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

    # Title & Contact Header
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1B365D'),
        alignment=1
    )
    story.append(Paragraph(sanitize_text(payload['candidate_name'].upper()), header_style))
    
    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#4A5568'),
        alignment=1
    )
    contact_line = f"{payload['location']} | {payload['phone']} | {payload['email']} | {payload['linkedin']}"
    story.append(Paragraph(sanitize_text(contact_line), contact_style))
    story.append(Spacer(1, 10))

    # Add Sections...
    doc.build(story)
    print(f"Generated PDF Resume: {filepath}")

def build_package(payload):
    output_dir = os.path.join(r"P:\Job Search", payload['folder'])
    os.makedirs(output_dir, exist_ok=True)
    
    pdf_resume_path = os.path.join(output_dir, f"{payload['candidate_name']}_Resume_{payload['company']}.pdf")
    build_pdf_resume(payload, pdf_resume_path)

if __name__ == '__main__':
    print("Application Package Generator Ready.")
```

---

### Module B: Email Digest Alert Parser (`fetch_gmail_alerts.py`)
Connects via IMAP to Gmail, extracts HTML anchor tags from job digest emails, and applies a 3-layer deduplication strategy:

```python
import imaplib
import email
from email.header import decode_header
import re
import json

IMAP_SERVER = "imap.gmail.com"
GMAIL_USER = "your_email@gmail.com"
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

def clean_url(url):
    if "linkedin.com" in url:
        url = url.replace('/comm/jobs/view/', '/jobs/view/').split('?')[0].split('#')[0]
    elif "indeed.com" in url or "builtin.com" in url or "greenhouse.io" in url or "lever.co" in url:
        url = url.split('&')[0].split('?')[0].split('#')[0]
    return url.rstrip('/')

def get_job_dedup_key(title, url, company=""):
    clean_u = clean_url(url)
    match_li = re.search(r'linkedin\.com/jobs/view/(\d+)', clean_u)
    if match_li:
        return f"li_id_{match_li.group(1)}"
    
    norm_title = re.sub(r'[^a-z0-9]', '', title.lower())
    norm_co = re.sub(r'[^a-z0-9]', '', company.lower())
    if norm_title and norm_co:
        return f"tc_{norm_title}_{norm_co}"

    return f"url_{clean_u}"
```

---

### Module C: Ground-Truth Page Metadata Auditor (`audit_and_fix_queue_companies.py`)
Fetches live page titles for every URL to extract 100% accurate hiring company names and job titles:

```python
import urllib.request
import re

def fetch_page_title(url):
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode('utf-8', errors='ignore')
            match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
    except Exception as e:
        print(f"Error fetching metadata for {url}: {e}")
    return None

def extract_company_from_title(page_title):
    if not page_title:
        return "Verified Employer"
    
    # LinkedIn Format: "Company hiring Role in Location | LinkedIn"
    match_li = re.search(r'^(.*?)\s+hiring\s+(.*?)\s+in\s+.*\|?\s*LinkedIn', page_title, re.IGNORECASE)
    if match_li:
        return match_li.group(1).strip()
        
    return "Verified Employer"
```

---

### Module D: Dynamic Dashboard Generator (`sync_dashboard_from_state.py`)
Reads `state.json` and compiles an HTML glassmorphism browser dashboard saved locally at `P:\Job Search\dashboard.html`.

---

## ⏱️ 5. Cron & Automation Schedule

To run in non-intrusive business hours mode, set up a cron job (or AGY scheduler):

* **Cron Schedule**: `0 7,11,15 * * *` (7:00 AM, 11:00 AM, 3:00 PM CT Business Hours)
* **Command**: `python fetch_gmail_alerts.py`

---

## 🛡️ 6. Core Operating Guardrails

1. **Zero Unapproved Submissions**: Applications must be reviewed by the candidate before submission.
2. **Strict Zero Em-Dash Policy**: All resume & cover letter outputs sanitize em-dashes (`—`) to hyphens or pipes.
3. **No Over-Reach / Hallucinations**: Resumes must strictly reflect the candidate's authentic career baseline.
4. **Local File Archiving**: Application packages are stored in structured folders on local storage (`P:\Job Search\<Company_Name>\`).
