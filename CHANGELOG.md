# Changelog

All notable changes to the Autonomous AI Career Advancement & Job Search System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-08-21

### Added
- **Manual Job URL Ingestion Engine**: Allows candidates to paste and parse any job posting URL (`/api/add_queue_url`) directly into the dashboard to add to the review queue.
- **Dynamic Queue Card Metadata**: Replaced static text with dynamic location (`100% Remote / Preferred Hybrid City Hybrid`), compensation scope (`{{TARGET_COMPENSATION_MIN}}`), and target capability fit details (`98% Fit`).
- **4-Week Stale Application Alert Engine**: Automatically flags applications submitted over 28 days ago (`⚠️ 4+ Weeks — Follow Up Needed`) with a dedicated KPI counter and a 1-click **"{{YOUR_NAME}} No Response"** quick-action button.
- **Application Lifecycle Tracker**: Inline status dropdown selector on each application row (`Applied`, `Interviewing`, `Negotiating`, `I Withdrew`, `Not Selected`, `No Response`, `Archived`).
- **Interactive Job Detail Modal**: Deep details view with 3 tabs: **Overview & Package**, **Applied Tab** (General notes & post-application follow-up tracker), and **Interviewing Tab** (Interview round logger with contact info, discussion notes, and post-interview follow-up tracker).
- **Queue Archiving Engine**: Replaced queue "Remove" button with "Archive" (`/api/archive_queue`), with restore (`/api/restore_queue`) and permanent deletion (`/api/delete_queue_permanent`).
- **Job Source Visual Badges**: Visual badges (`LinkedIn`, `Indeed`, `Greenhouse`, `Lever`, `Company Portal`) rendered on application rows and queue cards.

### Fixed
- **Applied Tab Status Filtering**: Normalized legacy application statuses in `state.json` to ensure all 17 applied roles display properly when clicking the **Applied** tab.

---

## [1.9.0] - 2026-08-20

### Added
- **Candidate Skill Verification Engine**: Prevents automated keyword stuffing by prompting candidate confirmation via an interactive UI modal (`P:\Job Search\dashboard.html`) before building resume packages.
- **Skills Learning Database**: Persistent skill storage (`approved_skills.json`) auto-approving candidate-verified technical skills, tools, and competencies in future builds.
- **Generic Example Template**: Public template (`approved_skills.example.json`) for open-source repository sharing.

---

## [1.8.0] - 2026-08-19

### Added
- **Multi-Board JobSpy Integration**: Scrapes LinkedIn and Indeed via open-source `python-jobspy` with strict location guardrails.
- **Ground-Truth Metadata Auditor**: HTTP title resolution script (`audit_and_fix_queue_companies.py`) ensuring accurate hiring company names.
- **Dashboard API Server**: Local background HTTP server (`dashboard_server.py`) listening on `http://localhost:5000` for 1-click apply package triggers.
- **Responsive HTML Dashboard**: Automated state-to-HTML generator (`sync_dashboard_from_state.py`) rendering live review queues and submitted applications.

### Security & Hardening
- **AppSec Environment Variables**: Extracted all credentials into untracked `.env` files loaded dynamically via `os.environ`.
- **CORS Origin Protection**: Restricted local API endpoint access (`dashboard_server.py`) to trusted local origins (`http://localhost`, `http://127.0.0.1`, `file://`, `null`).

### Fixed
- **Mermaid Syntax Rendering**: Quoted edge labels in `README.md` system architecture diagram for clean rendering on GitHub.
- **Additive Queue Preservation**: Refactored alert ingestion (`fetch_gmail_alerts.py`) to merge new roles additively via URL deduplication without deleting unreviewed roles.

---

## [1.5.0] - 2026-08-12

### Added
- **Master Document Generator**: Single Python engine (`build_application_package.py`) generating single-column ATS PDF and DOCX resumes and hybrid cover letters.
- **Strict Location Guardrails**: Geographic validation filtering non-matching onsite job listings.

---

## [1.0.0] - 2026-08-05

### Added
- Initial release of the Autonomous AI Job Search Agent architecture, state tracker (`state.json`), and document builder templates.
