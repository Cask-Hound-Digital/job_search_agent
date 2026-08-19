# PROJECT GOAL & REVISION TRACKER
**Candidate**: {{YOUR_FULL_NAME}}  
**Role Scope**: {{TARGET_ROLE_SCOPE_LIST}}  
**Target Compensation**: {{TARGET_COMPENSATION_MIN}}  
**Location Preferences**: 100% Remote (Primary) | Hybrid ONLY in Preferred Target Location (Preferred Hybrid City area near {{YOUR_CITY_STATE}})  
**Search Hours Schedule**: **7:00 AM – 5:00 PM CT** (Business Hours Only | Every 4 Hours: 7am, 11am, 3pm CT)  
**Primary System Location**: `P:\Projects\job-search-consultant`  
**Local Export Storage Directory**: `P:\Projects\job-search-consultant\Job Search\`  
**Shareable Template ZIP**: `P:\Projects\job-search-consultant\Job Search\job_search_agent_template.zip`  
**Live GitHub Repository**: [github.com/Cask-Hound-Digital/job_search_agent](https://github.com/Cask-Hound-Digital/job_search_agent)  

---

## 🎯 1. Primary Objectives & Operating Rules

1. **Strict Zero Em Dash Policy (`—`, `&mdash;`)**:
   * Em dashes are STRICTLY PROHIBITED across all resumes, cover letters, and system text outputs.
   * The generator script automatically runs a text sanitizer to convert any dashes to standard hyphens (` - `), pipes (` | `), or commas.

2. **Public Repository Placeholders & Valid Mermaid Syntax**:
   * The public GitHub repository ([github.com/Cask-Hound-Digital/job_search_agent](https://github.com/Cask-Hound-Digital/job_search_agent)) contains zero personal candidate data, hardcoded emails, app passwords, target titles, target comp, or location specifics.
   * All Mermaid edge labels (`|...|`) are formatted cleanly without double curly braces (`{{...}}`) to guarantee 100% valid Mermaid rendering on GitHub.

3. **Full Engine GitHub Repository Mirroring & 0 Security Violations**:
   * The live GitHub repository contains the complete, production-ready Python automation engine (`dashboard_server.py`, `fetch_gmail_alerts.py`, `sync_dashboard_from_state.py`, `fetch_jobspy_roles.py`, `build_application_package.py`, `audit_and_fix_queue_companies.py`, `clean_non_dfw_queue_roles.py`, `agents.md`, `.env.example`, `.gitignore`, blueprint, goals, and resume templates).
   * AppSec audit scanner (`audit_repo_security.py`) confirms **0 security violations** across all committed repository files.

4. **AppSec & Secret Hygiene Policy**:
   * All API keys, passwords, and sensitive credentials MUST be loaded via environment variables (`os.environ`) or untracked local `.env` files. Hardcoded secrets in source files are strictly forbidden.
   * Local API endpoints (`dashboard_server.py`) MUST enforce origin validation to disallow wildcard (`*`) cross-site requests from untrusted external web origins.

5. **Unified Project Root (`P:\Projects\job-search-consultant`)**:
   * All codebase scripts, state trackers (`state.json`), master application exports (`Job Search/`), and HTML dashboards (`Job Search/dashboard.html`) are consolidated under `P:\Projects\job-search-consultant`.

6. **{{MOST_RECENT_COMPANY}} Date Range Requirement ({{MOST_RECENT_EMPLOYMENT_DATES}})**:
   * All future resume and cover letter packages MUST set {{YOUR_FULL_NAME}}' {{MOST_RECENT_COMPANY}} role date range to **{{MOST_RECENT_EMPLOYMENT_DATES}}** (replacing "Present").

7. **Silent Background Daemon Server Architecture**:
   * Standing local API background server ([`dashboard_server.py`](file:///P:/Projects/job-search-consultant/dashboard_server.py)) running on `http://localhost:5000`.
   * Launched silently using `subprocess.CREATE_NO_WINDOW` via `ensure_dashboard_server_running()` in [`fetch_gmail_alerts.py`](file:///P:/Projects/job-search-consultant/fetch_gmail_alerts.py) so no shell windows pop up or remain open on screen.

8. **Additive Queue Protection Rule**:
   * All search runs ([`fetch_gmail_alerts.py`](file:///P:/Projects/job-search-consultant/fetch_gmail_alerts.py) & [`fetch_jobspy_roles.py`](file:///P:/Projects/job-search-consultant/fetch_jobspy_roles.py)) MUST preserve all existing unreviewed/unapplied jobs in `state.json`.
   * Newly discovered jobs are strictly **ADDED** to the queue using URL/ID deduplication. Roles are ONLY removed when explicitly applied for or dismissed by the user.

9. **Director-Level Role Scope Negotiation Strategy**:
   * For senior manager / manager openings that match technical GEO/AEO and web strategy competencies (e.g., {{TARGET_COMPANY_4}}), the system builds a tailored package positioning candidate as a Director-level executive to negotiate scope and compensation elevation ({{TARGET_COMPENSATION_MIN}}).

10. **Open-Source Multi-Board JobSpy Integration**:
   * Integrated `python-jobspy` open-source scraper engine ([`fetch_jobspy_roles.py`](file:///P:/Projects/job-search-consultant/fetch_jobspy_roles.py)) querying **LinkedIn and Indeed** for live $0-cost job extraction.

11. **Strict Location Filtering Engine (Remote & Preferred Hybrid City Local Only)**:
   * Enforced `is_remote=True` flags and strict location validation (`is_valid_location()`) in [`fetch_jobspy_roles.py`](file:///P:/Projects/job-search-consultant/fetch_jobspy_roles.py).

12. **Candidate Baseline Career Profile Template**:
   * **{{MOST_RECENT_COMPANY}} ({{YOUR_CITY_STATE}})**: *{{YOUR_MOST_RECENT_TITLE}}* (**{{MOST_RECENT_EMPLOYMENT_DATES}}**) — Managing a **{{TEAM_SIZE_PLACEHOLDER}}** (Development, DevOps, QA, BA, SEO); owning global web operations across 34 countries; **leading discovery, ROI evaluation, and decision-making for next-gen DXP to replace {{LEGACY_PLATFORM}}**; **organizing and executing the {{KEY_PROJECT_MIGRATION}}**; integrating {{ENTERPRISE_TECH_STACK_LIST}}; driving +15% demo conversion uplift & +42% self-serve digital conversion rate.
   * **{{PREVIOUS_COMPANY_2}} ({{YOUR_CITY_STATE}})**: *{{YOUR_PREVIOUS_TITLE_1}}* (**{{EMPLOYMENT_DATES_COMPANY_2}}**) — E-commerce storefronts for mobile apps & partner channels (Sprint), boosting checkout conversion by +34%.
   * **{{PREVIOUS_COMPANY_3}} ({{YOUR_CITY_STATE}})**: *{{YOUR_PREVIOUS_TITLE_2}}* (**{{EMPLOYMENT_DATES_COMPANY_3}}**) — Sustaining 35%+ annual online sales growth via SEO/SEM/Email/Marketplaces.
   * **University of Texas at {{YOUR_CITY}} ({{YOUR_CITY_STATE}})**: *{{YOUR_DEGREE_1}}* (Degree)
   * **{{YOUR_UNIVERSITY_2}} (College Station, TX)**: *{{YOUR_COURSEWORK_2}}*

---

## 📜 2. Technical System Revision History

### **Revision 1.85** | *2026-08-19*
* **Mermaid Syntax Fix in GitHub Repository**:
  * Fixed edge label syntax in [`README.md`](file:///P:/Projects/job-search-consultant/README.md) system architecture diagram (`E -->|"Remote or Preferred Hybrid"| F[...]`), resolving the `{{YOUR_PREFERRED_HYBRID_CITY}}` double-curly-brace parser conflict in GitHub's rich markdown display engine.
  * Pushed update to GitHub repository [github.com/Cask-Hound-Digital/job_search_agent](https://github.com/Cask-Hound-Digital/job_search_agent) (Commit `fd9fc90`).

### **Revision 1.84** | *2026-08-19*
* **Public Repository Placeholder Sanitization**.

### **Revision 1.83** | *2026-08-18*
* **AppSec Repository Verification & Blueprint Sanitization**.

### **Revision 1.82** | *2026-08-18*
* **Production-Ready `README.md` & Repository Documentation Update**.

### **Revision 1.81** | *2026-08-18*
* **Full Production Engine Repository Sync**.

### **Revision 1.80** | *2026-08-18*
* **AppSec Security Hardening Patch**.

### **Revision 1.79** | *2026-08-18*
* **Full Migration to `P:\Projects\job-search-consultant`**.

### **Revision 1.78** | *2026-08-17*
* **{{MOST_RECENT_COMPANY}} End Date Updated to {{EMPLOYMENT_END_DATE}}**.

### **Revision 1.77** | *2026-08-17*
* **Silent Background Server Launch (`subprocess.CREATE_NO_WINDOW`)**.

### **Revision 1.76** | *2026-08-14*
* **Additive Review Queue Preservation Engine**.

### **Revision 1.75** | *2026-08-13*
* **{{TARGET_COMPANY_4}} Application Package & Submission Log (`JOB-19`)**.

### **Revision 1.74** | *2026-08-13*
* **Automated Cron Server Auto-Launch (`ensure_dashboard_server_running`)**.

### **Revision 1.73** | *2026-08-12*
* **1-Click "⚡ Apply & Build Package" Dashboard API Server & UI Integration**.

### **Revision 1.72** | *2026-08-12*
* **Strict Geographic & Location Safeguard Integration**.

### **Revision 1.71** | *2026-08-12*
* **{{TARGET_COMPANY_1}} Application Package & Submission Log (`JOB-18`)**.

### **Revision 1.70** | *2026-08-12*
* **{{TARGET_COMPANY_2}} / {{TARGET_COMPANY_1}} Application Package & Submission Log (`JOB-17`)**.

### **Revision 1.69** | *2026-08-12*
* **Candidate Baseline Experience Expansion (DXP Replacement & TrendAI {{MODERN_CMS}} Migration)**.

### **Revision 1.68** | *2026-08-12*
* **{{TARGET_COMPANY_3}} Application Package & Submission Log (`JOB-16`)**.

### **Revision 1.67** | *2026-08-12*
* **Candidate Career Baseline Refinement (First Horizon Excluded)**.

### **Revision 1.66** | *2026-08-12*
* **Candidate Baseline Resume Enhancement (Historical PDF Audit)**.

### **Revision 1.65** | *2026-08-12*
* **Open-Source JobSpy Multi-Board Engine Integrated**.

### **Revision 1.64** | *2026-08-12*
* **Dual-Channel Indeed Ingestion**.

### **Revision 1.63** | *2026-08-11*
* **Expanded Target Role Scope**.

### **Revision 1.61** | *2026-08-11*
* **Ground-Truth Page Metadata Auditor**.

### **Revision 1.60** | *2026-08-10*
* **Multi-Layer Cross-Digest Deduplication Engine**.

### **Revision 1.59** | *2026-08-10*
* **Automated Dashboard Sync Engine**.

### **Revision 1.0 – 1.58** | *System Foundation*
* **Core Agent Architecture**.

---

## 📂 3. Workspace File Registry

| File Name | Location | Description |
| :--- | :--- | :--- |
| **`sanitize_and_push_github.py`** | [`./sanitize_and_push_github.py`](file:///P:/Projects/job-search-consultant/sanitize_and_push_github.py) | Comprehensive placeholder sanitization & GitHub push script for public repository releases. |
| **`audit_repo_security.py`** | [`./audit_repo_security.py`](file:///P:/Projects/job-search-consultant/audit_repo_security.py) | AppSec security audit scanner verifying 0 security violations in repository. |
| **`README.md`** | [`./README.md`](file:///P:/Projects/job-search-consultant/README.md) | **[Production System Overview]** Architecture diagram, component matrix, AppSec standards & execution guides. |
| **`PROJECT_GOALS_AND_REVISIONS.md`** | [`./PROJECT_GOALS_AND_REVISIONS.md`](file:///P:/Projects/job-search-consultant/PROJECT_GOALS_AND_REVISIONS.md) | System technical revision history and candidate baseline. |
| **`fetch_gmail_alerts.py`** | [`./fetch_gmail_alerts.py`](file:///P:/Projects/job-search-consultant/fetch_gmail_alerts.py) | Email job alert parser with dynamic pathing, secret environment loading, silent server auto-launch & additive queue merging. |
| **`dashboard_server.py`** | [`./dashboard_server.py`](file:///P:/Projects/job-search-consultant/dashboard_server.py) | **[Local API Server]** Background HTTP server listening on localhost:5000 with origin-validated CORS security. |
| **`sync_dashboard_from_state.py`** | [`./sync_dashboard_from_state.py`](file:///P:/Projects/job-search-consultant/sync_dashboard_from_state.py) | Automated state-to-HTML dashboard generator with 1-click apply button UI. |
| **`fetch_jobspy_roles.py`** | [`./fetch_jobspy_roles.py`](file:///P:/Projects/job-search-consultant/fetch_jobspy_roles.py) | Open-source Python multi-board live scraper engine with strict Preferred Hybrid City/Remote location guardrails. |
| **`build_application_package.py`** | [`./build_application_package.py`](file:///P:/Projects/job-search-consultant/build_application_package.py) | **[Single Master Generator]** Unified Python engine configured with {{MOST_RECENT_COMPANY}} end date {{EMPLOYMENT_END_DATE}}. |
| **`state.json`** | [`./state.json`](file:///P:/Projects/job-search-consultant/state.json) | Central persistent state tracker for candidate profile, job listings, and active submissions. |
