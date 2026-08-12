# PROJECT GOAL & REVISION TRACKER
**Candidate**: {{YOUR_FULL_NAME}}  
**Role Scope**: Director, Senior Director, Head of, VP, Fractional VP, Advisory, Senior Manager, and Lead roles across Web Marketing, Digital Experience, Website Growth, PLG, Web Strategy, Fractional VP of Digital Product / Web Operations, Digital Transformation Advisor, SEO, Web & AI, and Web Development  
**Target Compensation**: {{TARGET_COMPENSATION_MIN}} / Year  
**Location Preferences**: 100% Remote (Primary) | Hybrid ONLY in Dallas–Fort Worth (DFW area near {{YOUR_CITY_STATE}})  
**Search Hours Schedule**: **7:00 AM – 5:00 PM CT** (Business Hours Only | Every 4 Hours: 7am, 11am, 3pm CT)  
**System Location**: [`c:\Users\mark\.gemini\antigravity\scratch\job-search-consultant`](file:///c:/Users/mark\.gemini\antigravity\scratch\job-search-consultant)  
**Local Export Storage Directory**: `P:\Job Search\`  
**Shareable Template ZIP**: [`P:\Job Search\job_search_agent_template.zip`](file:///P:/Job%20Search/job_search_agent_template.zip)  
**Live GitHub Repository**: [github.com/RoadRashTX/job_search_agent](https://github.com/RoadRashTX/job_search_agent)  

---

## 🎯 1. Primary Objectives & Operating Rules

1. **Strict Zero Em Dash Policy (`—`, `&mdash;`)**:
   * Em dashes are STRICTLY PROHIBITED across all resumes, cover letters, and system text outputs.
   * The generator script automatically runs a text sanitizer to convert any dashes to standard hyphens (` - `), pipes (` | `), or commas.

2. **Open-Source Multi-Board JobSpy Integration**:
   * Integrated `python-jobspy` open-source scraper engine ([`fetch_jobspy_roles.py`](file:///c:/Users/mark\.gemini\antigravity\scratch\job-search-consultant\fetch_jobspy_roles.py)) querying **LinkedIn and Indeed** for live $0-cost job extraction.

3. **Ground-Truth Page Title Audit Engine**:
   * All job alerts automatically fetch the live page title of each destination URL (`audit_and_fix_queue_companies.py`) to extract the 100% accurate hiring company name and job title.

4. **Authoritative Candidate Baseline Career Truth**:
   * **{{PREVIOUS_COMPANY_1}}, Inc. (Irving, TX)**: *Global Web Marketing Director of Development* (**June 2008 - Present**)
   * **{{PREVIOUS_COMPANY_2}}, Inc. (Southlake, TX)**: *Product Manager of Web and E-commerce* (**Aug 2007 - Mar 2008**)
   * **{{PREVIOUS_COMPANY_3}}, Inc. (Addison, TX)**: *E-commerce and Web Marketing Manager* (**Apr 2001 - Apr 2007**)
   * **University of Texas at Arlington (Arlington, TX)**: *Bachelor of Arts (B.A.), Web Management / Internet Development* (Degree)
   * **Texas A&M University (College Station, TX)**: *Engineering Technology Coursework*

---

## 📜 2. Complete Revision & Changelog History (v1.0 – v1.65)

### **Revision 1.65** | *2026-08-12 15:30:00*
* **Changelog**:
  * **Open-Source JobSpy Multi-Board Engine Integrated**:
    * Created [`fetch_jobspy_roles.py`](file:///c:/Users/mark\.gemini\antigravity\scratch\job-search-consultant\fetch_jobspy_roles.py) using `python-jobspy`.
    * Extracted **306 raw live roles** across LinkedIn & Indeed, adding **145 new unique verified opportunities** to the review queue.
    * Integrated `run_jobspy_scraper()` directly into [`fetch_gmail_alerts.py`](file:///c:/Users/mark\.gemini\antigravity\scratch\job-search-consultant\fetch_gmail_alerts.py) for perpetual $0-cost live multi-board scraping during every search cycle.

### **Revision 1.64** | *2026-08-12 15:19:00*
* **Changelog**:
  * **Dual-Channel Indeed Integration Executed**:
    * Enabled explicit `site:indeed.com/viewjob` web sweeps during standing search cycles alongside IMAP email digest parsing (`fetch_gmail_alerts.py`).
    * Updated standing cron schedule (`task-1468`).

### **Revision 1.63** | *2026-08-11 15:50:00*
* **Changelog**:
  * **Added Target Roles**:
    * **Fractional VP of Digital Product / Web Operations** (Global website overhauls, compliance, multi-region localization).
    * **Digital Transformation Advisor** (Legacy tech stack sync, marketing automation integration).

### **Revision 1.62** | *2026-08-11 11:48:00*
* **Changelog**:
  * **Mouser Electronics Application Package & Submission Log (`JOB-15`)**:
    * Created tailored master application package for **Mouser Electronics** (*Web Software Development Director* - Mansfield, TX DFW Local HQ, Req #30834).
    * Generated PDF/DOCX resume & cover letter in [`P:\Job Search\Mouser Electronics\`](file:///P:/Job%20Search/Mouser%20Electronics/).
    * Updated application count to **12 Active Submissions** in [`state.json`](file:///c:/Users/mark\.gemini\antigravity\scratch\job-search-consultant\state.json) and live browser dashboard [`P:\Job Search\dashboard.html`](file:///P:/Job%20Search/dashboard.html).

### **Revision 1.61** | *2026-08-11 10:55:00*
* **Changelog**:
  * **Ground-Truth Company Name Audit Executed**: Created [`audit_and_fix_queue_companies.py`](file:///c:/Users/mark\.gemini\antigravity\scratch\job-search-consultant\audit_and_fix_queue_companies.py). Fetched live page titles for all review queue URLs to extract exact hiring companies, eliminating "{{YOUR_NAME}}" and digest-header misattributions.
  * Integrated `audit_queue()` directly into [`fetch_gmail_alerts.py`](file:///c:/Users/mark\.gemini\antigravity\scratch\job-search-consultant\fetch_gmail_alerts.py) for perpetual accuracy.

### **Revision 1.60** | *2026-08-10 20:53:00*
* **Changelog**:
  * **Multi-Layer Cross-Email Deduplication Implemented**: Built `get_job_dedup_key()` in [`fetch_gmail_alerts.py`](file:///c:/Users/mark\.gemini\antigravity\scratch\job-search-consultant\fetch_gmail_alerts.py) enforcing canonical job IDs, clean URL parameters, and normalized Title+Company hashes.

### **Revision 1.59** | *2026-08-10 20:50:00*
* **Changelog**:
  * **Automated Dashboard Sync Engine Implemented**: Created [`sync_dashboard_from_state.py`](file:///c:/Users/mark\.gemini\antigravity\scratch\job-search-consultant\sync_dashboard_from_state.py) and integrated it directly into [`fetch_gmail_alerts.py`](file:///c:/Users/mark\.gemini\antigravity\scratch\job-search-consultant\fetch_gmail_alerts.py).

### **Revision 1.58** | *2026-08-10 10:13:00*
* **Changelog**:
  * **Neo Security Inc. Application Package & Submission Log (`JOB-14`)**: Tailored master package for *Director, Web & Digital / AEO*. Generated PDF/DOCX package in `P:\Job Search\Neo Security\`.

### **Revision 1.57** | *2026-08-10 10:11:00*
* **Changelog**:
  * **100% Live URL Company Name Audit**: Re-aligned company names for ServiceNow, Outreach, Scotiabank, Legacybox, and Jobgether.

### **Revision 1.56** | *2026-08-10 09:30:00*
* **Changelog**:
  * **Lensa Domain Exclusion**: Removed `@lensa.com` from email alert parser and purged low-quality Lensa listings.

### **Revision 1.54 – 1.55** | *2026-08-07*
* **Changelog**:
  * Generated master application packages for **Databricks** (`JOB-11`), **Six Flags** (`JOB-12`), **GitLab Growth EM** (`JOB-10a`), and **GitLab AI CRO** (`JOB-10b`).

### **Revision 1.50 – 1.53** | *2026-08-05 – 2026-08-06*
* **Changelog**:
  * Built tailored packages for **Life360** (`JOB-09`), **Palo Alto Networks** (`JOB-08`), **Uniphore** (`JOB-03`), **Rubrik** (`JOB-02`), and **Hyland Software** (`JOB-01`).

### **Revision 1.0 – 1.49** | *Initial Foundation*
* **Changelog**:
  * Established single-column ATS formatting, baseline career truth at {{PREVIOUS_COMPANY_1}} (June 2008 - Present), zero em-dash text sanitizer, ReportLab PDF / Word docx generator engine, local `P:\Job Search\` drive sync, and GitHub open-source template repository.

---

## 📂 3. Workspace File Registry

| File Name | Location | Description |
| :--- | :--- | :--- |
| **`PROJECT_GOALS_AND_REVISIONS.md`** | [`./PROJECT_GOALS_AND_REVISIONS.md`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/PROJECT_GOALS_AND_REVISIONS.md) | **[Current File]** Complete revision history (v1.0 – v1.65) and system goals. |
| **`fetch_jobspy_roles.py`** | [`./fetch_jobspy_roles.py`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/fetch_jobspy_roles.py) | Open-source Python multi-board live scraper engine. |
| **`fetch_gmail_alerts.py`** | [`./fetch_gmail_alerts.py`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/fetch_gmail_alerts.py) | Email job alert parser with auto JobSpy scraper execution & dashboard sync. |
| **`audit_and_fix_queue_companies.py`** | [`./audit_and_fix_queue_companies.py`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/audit_and_fix_queue_companies.py) | Live page title metadata scraper for 100% ground-truth company titles. |
| **`sync_dashboard_from_state.py`** | [`./sync_dashboard_from_state.py`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/sync_dashboard_from_state.py) | Automated state-to-HTML dashboard generator. |
| **`build_application_package.py`** | [`./build_application_package.py`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/build_application_package.py) | **[Single Master Generator]** Unified Python engine. |
| **`state.json`** | [`./state.json`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/state.json) | Central persistent state tracker for candidate profile, job listings, and active submissions. |
