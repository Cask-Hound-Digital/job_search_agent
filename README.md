# Autonomous AI Career Advancement & Job Search Agent

A complete open-source agentic pipeline that continuously discovers target opportunities across multiple job boards, parses email alert digests, audits live page metadata, generates ATS-optimized PDF and DOCX application packages, and manages your pipeline via a local web dashboard.

---

## Architecture Overview

1. **Multi-Board Scrapers**: Automated ingestion via **BuiltIn**, **LinkedIn & Indeed** (via `python-jobspy`), **JobsPipe API** (Greenhouse, Lever, Ashby, Workday), and **Gmail IMAP** alert digests.
2. **Universal Ingest Guard**: Dynamic filtering enforcing target titles, leadership seniority, geographic guardrails (remote / local metro), and compensation floors loaded from `config.json`.
3. **Safe State Manager**: Atomic state updates with automatic rolling backups and zero silent record drops.
4. **404 Dead URL Pruning**: Multi-threaded link auditing to purge expired listings before presentation.
5. **Document Engine**: Generates single-column ATS-compliant Word (`.docx`) and PDF (`.pdf`) application packages with strict zero em-dash enforcement.
6. **Local Web Dashboard**: Lightweight Flask web interface on `http://localhost:5000` to review queued roles, dismiss irrelevant postings, and track active applications.

---

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Your Profile & Targets
Copy `config.json` and customize your target titles, salary floor, and metro locations:
```json
{
  "candidate": {
    "full_name": "Jane Doe",
    "email": "jane.doe@example.com",
    "phone": "(555) 012-3456",
    "min_salary_floor": 180000,
    "primary_location": "New York, NY",
    "workplace_preferences": ["Remote", "Hybrid"]
  },
  "search_matrix": {
    "target_titles": [
      "Director of Product Management",
      "Director of Engineering",
      "VP of Technology"
    ]
  }
}
```

### 3. Set Up Environment Variables (Optional)
Copy `.env.example` to `.env` to configure email alert ingestion and API keys:
```bash
cp .env.example .env
```

### 4. Run Unified Multi-Board Ingestion
```bash
python run_unified_search.py
```

### 5. Launch the Local Dashboard
```bash
python dashboard_server.py
```
Open `http://localhost:5000` in your browser to review discovered roles and generate tailored application packages.\n