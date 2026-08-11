# PROJECT GOAL & REVISION TRACKER
**Candidate**: Mark Jaggers  
**Role Scope**: Director, Senior Director, Head of, VP, Senior Manager, and Lead roles across Web Marketing, Digital Experience, Website Growth, PLG, Web Strategy, SEO, Web & AI, and Web Development  
**Target Compensation**: $225,000+ USD / Year  
**Location Preferences**: 100% Remote (Primary) | Hybrid ONLY in Dallas–Fort Worth (DFW area near Grand Prairie, TX)  
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

2. **Strict Candidate Integrity — Zero Over-Reach Policy**:
   * Resumes MUST NEVER contain company-specific names or specialized domain terms the candidate has not worked on.
   * The resume must strictly describe the candidate's authentic executive capabilities: Enterprise B2B & B2C Web Platforms, Mobile App Storefronts, User Portals, Checkout CRO, GA4/AEM/WordPress/Sanity, and Cross-Functional Leadership.

3. **Multi-Layer Cross-Email Strict Deduplication**:
   * All email digest parsing enforces a 3-layer deduplication engine across inbox notifications:
     1. Canonical Job ID extraction (`linkedin.com/jobs/view/<job_id>`, `greenhouse.io/.../jobs/<job_id>`).
     2. Clean URL parameter stripping (`?refId=`, `?trackingId=`, `#fragment`).
     3. Normalized Title + Company unique hash keys to guarantee zero duplicate listings across overlapping email alerts.

4. **Unified Master Application Package Generator**:
   * All PDF and Word application packages MUST be built using the single master engine script: [`build_application_package.py`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/build_application_package.py).

5. **Automated Build Execution Policy**:
   * When new job parameters or choices are added to `build_application_package.py`, automatically execute the script immediately without pausing or asking for permission.

6. **Authoritative Candidate Baseline Career Truth**:
   * **Trend Micro, Inc. (Irving, TX)**: *Global Web Marketing Director of Development* (**June 2008 - Present**)
   * **Handmark, Inc. (Southlake, TX)**: *Product Manager of Web and E-commerce* (**Aug 2007 - Mar 2008**)
   * **Mapsco, Inc. (Addison, TX)**: *E-commerce and Web Marketing Manager* (**Apr 2001 - Apr 2007**)
   * **University of Texas at Arlington (Arlington, TX)**: *Bachelor of Arts (B.A.), Web Management / Internet Development* (Degree)
   * **Texas A&M University (College Station, TX)**: *Engineering Technology Coursework*

---

## 📜 2. Full Revision & Changelog History

### **Revision 1.60** | *2026-08-10 20:53:00*
* **Changelog**:
  * **Multi-Layer Cross-Email Deduplication Implemented**:
    * Built `get_job_dedup_key()` in [`fetch_gmail_alerts.py`](file:///c:/Users/mark\.gemini\antigravity\scratch\job-search-consultant\fetch_gmail_alerts.py) enforcing canonical job IDs, clean URL parameters, and normalized Title+Company hashes.
    * Re-parsed inbox alerts, eliminating duplicate cross-digest entries. Live browser dashboard [`P:\Job Search\dashboard.html`](file:///P:/Job%20Search/dashboard.html) updated automatically.

### **Revision 1.59** | *2026-08-10 20:50:00*
* **Changelog**:
  * **Automated Dashboard Sync Engine Implemented**.

---

## 📂 3. Workspace File Registry

| File Name | Location | Description |
| :--- | :--- | :--- |
| **`PROJECT_GOALS_AND_REVISIONS.md`** | [`./PROJECT_GOALS_AND_REVISIONS.md`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/PROJECT_GOALS_AND_REVISIONS.md) | **[Current File]** Project objectives, complete revision log, and multi-layer deduplication update. |
| **`fetch_gmail_alerts.py`** | [`./fetch_gmail_alerts.py`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/fetch_gmail_alerts.py) | Email job alert parser with 3-layer cross-digest deduplication engine. |
| **`sync_dashboard_from_state.py`** | [`./sync_dashboard_from_state.py`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/sync_dashboard_from_state.py) | Automated state-to-HTML dashboard generator. |
| **`build_application_package.py`** | [`./build_application_package.py`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/build_application_package.py) | **[Single Master Generator]** Unified Python engine with automatic em-dash sanitizer. |
| **`state.json`** | [`./state.json`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/state.json) | Central persistent state tracker for candidate profile, job listings, and active submissions. |
