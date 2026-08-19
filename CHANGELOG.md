# Changelog

All notable changes to the Autonomous AI Career Advancement & Job Search System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
