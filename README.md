# Autonomous AI Career Advancement Agent & Job Search System

An enterprise-grade autonomous AI job search, multi-board scraping, resume tailoring, cover letter generation, and application tracking system built for executive career advancement ({{TARGET_COMPENSATION_MIN}} target compensation).

---

## 🏗️ System Architecture & Workflow

```mermaid
flowchart TD
    A[Gmail Email Alerts] -->|IMAP Ingestion| B[fetch_gmail_alerts.py]
    C[LinkedIn & Indeed Boards] -->|JobSpy Scraper| D[fetch_jobspy_roles.py]
    B --> E[Location & Role Filter Engine]
    D --> E
    E -->|Remote or {{YOUR_PREFERRED_HYBRID_CITY}} Local| F[audit_and_fix_queue_companies.py]
    F -->|Ground-Truth Verification| G[state.json - Central Tracker]
    G --> H[sync_dashboard_from_state.py]
    H --> I[dashboard.html - Live UI]
    I -->|1-Click Apply Button| J[dashboard_server.py - API Server]
    J --> K[build_application_package.py]
    K --> L[PDF & DOCX Master Packages]
```

---

## ⚡ Core Engine Components

| Component | Script Name | Description |
| :--- | :--- | :--- |
| **Alert Ingestion** | [`fetch_gmail_alerts.py`](file:///P:/Projects/job-search-consultant/fetch_gmail_alerts.py) | Connects to Gmail via IMAP, parses incoming job alerts (LinkedIn, Indeed, BuiltIn), filters non-{{YOUR_PREFERRED_HYBRID_CITY}} onsite roles, and merges new matches additively into `state.json`. |
| **Multi-Board Scraper** | [`fetch_jobspy_roles.py`](file:///P:/Projects/job-search-consultant/fetch_jobspy_roles.py) | Scrapes LinkedIn and Indeed via open-source `python-jobspy` with strict 100% Remote / {{YOUR_PREFERRED_HYBRID_CITY}} hybrid location validation. |
| **Metadata Auditor** | [`audit_and_fix_queue_companies.py`](file:///P:/Projects/job-search-consultant/audit_and_fix_queue_companies.py) | Performs HTTP head/title requests to extract 100% accurate ground-truth hiring company titles for review queue listings. |
| **Dashboard API Server** | [`dashboard_server.py`](file:///P:/Projects/job-search-consultant/dashboard_server.py) | Local background HTTP server listening on `http://localhost:5000` to process 1-click **"⚡ Apply & Build Package"** triggers from `dashboard.html`. |
| **Dashboard Generator** | [`sync_dashboard_from_state.py`](file:///P:/Projects/job-search-consultant/sync_dashboard_from_state.py) | Renders `state.json` applications and review queue roles into a modern, responsive HTML dashboard (`dashboard.html`). |
| **Master Generator** | [`build_application_package.py`](file:///P:/Projects/job-search-consultant/build_application_package.py) | Generates ATS-optimized PDF and DOCX resumes and tailored hybrid cover letters formatted with single-column layouts and quantified 3-part bullet points. |

---

## 🔒 Security & AppSec Compliance (`agents.md`)

* **Secrets Management**: All sensitive credentials (`GMAIL_USER`, `GMAIL_APP_PASSWORD`) are loaded dynamically from environment variables or a local untracked `.env` file. Plaintext secrets are strictly excluded from version control via `.gitignore`.
* **CORS Security**: `dashboard_server.py` enforces origin validation (`Access-Control-Allow-Origin`), restricting cross-site requests to trusted local origins (`http://localhost`, `http://127.0.0.1`, `file://`, `null`).

---

## 🎯 Candidate Profile & System Guardrails

* **Target Roles**: Director, Senior Director, Head of, VP, Fractional VP, Advisory, Senior Manager, and Lead roles across Web Marketing, Digital Experience, Website Growth, PLG, Web Strategy, Fractional VP of Digital Product / Web Operations, Digital Transformation Advisor, SEO, Web & AI, and Web Development.
* **Target Compensation**: {{TARGET_COMPENSATION_MIN}}.
* **Location Preferences**: 100% Remote (Primary) | Hybrid ONLY in {{YOUR_TARGET_LOCATION}} ({{YOUR_PREFERRED_HYBRID_CITY}} area near {{YOUR_CITY_STATE}}).
* **Strict Zero Em Dash Policy**: Em dashes (`—`) are strictly prohibited and auto-sanitized into standard hyphens (` - `) or pipes (` | `).
* **Additive Queue Protection**: New search sweeps strictly **ADD** new unique roles to `state.json`. Unreviewed jobs are never automatically deleted.
* **{{PREVIOUS_COMPANY_1}} Date Range**: All generated application packages set {{PREVIOUS_COMPANY_1}} experience to **June 2008 - August 2026**.

---

## 🚀 Quick Setup & Execution

### 1. Environment Setup
Create a `.env` file in the root directory:
```env
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password
```

### 2. Install Dependencies
```bash
pip install reportlab python-docx python-jobspy
```

### 3. Run Search & Ingestion Cycle
```bash
python fetch_gmail_alerts.py
```

### 4. Build Application Package Manually
```bash
python build_application_package.py
```

### 5. Start Local Dashboard API Server
```bash
python dashboard_server.py
```

---

## 📜 System Documentation

* **[`PROJECT_GOALS_AND_REVISIONS.md`](file:///P:/Projects/job-search-consultant/PROJECT_GOALS_AND_REVISIONS.md)**: Full system technical revision history, candidate baseline, and workspace registry.
* **[`AUTONOMOUS_JOB_SEARCH_AGENT_BLUEPRINT.md`](file:///P:/Projects/job-search-consultant/AUTONOMOUS_JOB_SEARCH_AGENT_BLUEPRINT.md)**: End-to-end architectural blueprint and design specifications.
* **[`agents.md`](file:///P:/Projects/job-search-consultant/agents.md)**: AppSec code quality and security compliance rules.
