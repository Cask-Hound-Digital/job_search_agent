# Autonomous AI Career Advancement Agent Template

This project provides an end-to-end autonomous job search, resume tailoring, cover letter generation, and application tracking system.

---

## 🚀 Quick Setup Instructions

### Step 1: Configure Your Profile & Preferences
Open `config.json` and replace the placeholder values with your personal details and career targets:
- `candidate_name`: Your full name.
- `target_roles`: Titles you are targeting (e.g., `["Manager of something", "Senior Developer of Stuff"]`).
- `target_compensation_min`: Minimum annual salary (e.g., `"{{TARGET_COMPENSATION_MIN}}"` -> `67676`).
- `target_locations`: Preferred locations (e.g., `["Remote", "Dallas, TX"]`).

### Step 2: Add Your Baseline Resumes
Place your recent resume versions in {{YOUR_NAME}}down format inside the `resumes/` folder:
- `resumes/resume_version_1.md`
- `resumes/resume_version_2.md`

### Step 3: Install Python Dependencies
Run the following command in your terminal to install the PDF and Word document generators:
```bash
pip install reportlab python-docx
```

### Step 4: Run Document Generation & Monitoring
Use `build_documents.py` to generate ATS-compliant **PDF** and **DOCX** application packages for approved roles:
```bash
python build_documents.py
```

---

## 📜 Key Principles & Protocols
1. **Zero Unapproved Submissions**: Applications are evaluated and presented with Live Job URLs for your review. Applications are only submitted after explicit user confirmation.
2. **Resume & Hybrid Cover Letter Strategy**: All materials use quantified 3-part bullet points (*Action Verb + Specific Detail + Measurable Result*) and ATS single-column formatting.
3. **Structured Tracking**: Application statuses and history are automatically maintained in `state.json` and `PROJECT_GOALS_AND_REVISIONS.md`.
