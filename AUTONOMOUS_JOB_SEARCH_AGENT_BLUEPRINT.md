# Autonomous AI Job Search & Application Engineering Blueprint

## System Architecture

```
                              +-----------------------------------------+
                              |         Candidate Target Profile        |
                              | (Roles, Comp, Locations, Skill Baseline)|
                              +--------------------+--------------------+
                                                   |
                                                   v
+-------------------------+         +------------------------------+         +-------------------------+
| Scheduled Search Runner |-------> | Multi-Board Ingestion Suite  | ------> | Universal Ingest Guard  |
| (Cron or Task Engine)   |         | (BuiltIn, JobSpy, Gmail IMAP)|         | (Titles, Comp, Loc, Dedu)|
+-------------------------+         +------------------------------+         +------------+------------+
                                                   |                                      |
                                                   v                                      v
+-------------------------+         +------------------------------+         +-------------------------+
| Local Output Directory  | <------ | Application Package Engine   | <------ | Central State Manager   |
| (`output/<Company>/`)   |         | (ATS DOCX / PDF Builder)     |         | (`safe_state_manager`)  |
+-------------------------+         +------------------------------+         +------------+------------+
                                                                                          |
                                                                                          v
                                                                             +-------------------------+
                                                                             | Local Web Dashboard     |
                                                                             | (Flask / `index.html`)  |
                                                                             +-------------------------+
```

## Core Operating Principles

1. **Zero Unapproved Submissions**: The agent identifies, audits, and presents opportunities with live URLs for candidate review. No materials are submitted without explicit user sign-off.
2. **ATS Single-Column Format**: All generated resumes use standardized single-column layouts with clear section headers, readable font hierarchy, and quantified accomplishment bullets.
3. **Strict Zero Em-Dash Policy**: All text sanitizers strip em-dashes and replace them with hyphens or commas to prevent layout corruption across legacy enterprise ATS parsers.
4. **Atomic State Persistence**: Pipeline records are written atomically with rolling backup files to prevent state loss during system interruptions.\n