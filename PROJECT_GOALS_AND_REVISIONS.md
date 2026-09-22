# Autonomous Job Search Agent - Architecture Goals & Revision History

## Core System Architecture Goals

1. **Continuous Multi-Source Ingestion**: Automatically sweep job boards (BuiltIn, LinkedIn, Indeed), ATS APIs (Greenhouse, Lever, Ashby, Workday), and email alert digests.
2. **Universal Ingest Guard**: Enforce strict alignment on target leadership titles, compensation floors, and location preferences before any role enters the review queue.
3. **Zero Data Loss & Safe State Management**: All pipeline mutations are written atomically with automatic rolling backups.
4. **Automated 404 URL Auditing**: Multi-threaded link testing purges filled or expired postings.
5. **ATS-Compliant Document Generation**: Single-column Word and PDF document generation with strict zero em-dash enforcement.

---

## Technical Milestone History

### Version 2.0.0
- **BuiltIn Network Scraper**: Direct scraping of high-signal remote and hybrid opportunities from BuiltIn.
- **Universal Ingestion Guard**: Multi-factor filtering engine enforcing title patterns, company spam filters, regional boundaries, and salary floors.
- **Safe State Manager**: Atomic file writes, automatic timestamped backup rotation, and crash-safe persistence.
- **404 URL Audit Engine**: Multi-threaded HTTP status verification to prune broken job links.
- **Local Web Dashboard & REST API**: Flask backend on port 5000 providing split-pane review queue management and 1-click package building.

### Version 1.5.0
- **Multi-Board JobSpy Integration**: Open-source scraper querying LinkedIn and Indeed for live job listings.
- **JobsPipe ATS Aggregator**: Ingestion client for Greenhouse, Lever, Ashby, and Workday postings.
- **IMAP Digest Alert Parser**: Automated email extraction from LinkedIn and Indeed job alert notifications.

### Version 1.0.0
- **Initial Prototype**: Basic document builder (`build_documents.py`) generating DOCX and PDF resumes from Markdown templates.\n