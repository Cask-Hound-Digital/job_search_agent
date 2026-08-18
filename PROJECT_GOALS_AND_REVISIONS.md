# PROJECT GOAL & REVISION TRACKER
**Candidate**: {{YOUR_FULL_NAME}}  
**Role Scope**: Director, Senior Director, Head of, VP, Fractional VP, Advisory, Senior Manager, and Lead roles across Web Marketing, Digital Experience, Website Growth, PLG, Web Strategy, Fractional VP of Digital Product / Web Operations, Digital Transformation Advisor, SEO, Web & AI, and Web Development  
**Target Compensation**: {{TARGET_COMPENSATION_MIN}} / Year  
**Location Preferences**: 100% Remote (Primary) | Hybrid ONLY in Dallas–Fort Worth (DFW area near {{YOUR_CITY_STATE}})  
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

2. **Unified Project Root (`P:\Projects\job-search-consultant`)**:
   * All codebase scripts, state trackers (`state.json`), master application exports (`Job Search/`), and HTML dashboards (`Job Search/dashboard.html`) are consolidated under `P:\Projects\job-search-consultant`.

3. **{{PREVIOUS_COMPANY_1}} Date Range Requirement (June 2008 - August 2026)**:
   * All future resume and cover letter packages MUST set {{YOUR_FULL_NAME}}' {{PREVIOUS_COMPANY_1}} role date range to **June 2008 - August 2026** (replacing "Present").

4. **Silent Background Daemon Server Architecture**:
   * Standing local API background server ([`dashboard_server.py`](file:///P:/Projects/job-search-consultant/dashboard_server.py)) running on `http://localhost:5000`.
   * Launched silently using `subprocess.CREATE_NO_WINDOW` via `ensure_dashboard_server_running()` in [`fetch_gmail_alerts.py`](file:///P:/Projects/job-search-consultant/fetch_gmail_alerts.py) so no shell windows pop up or remain open on screen.

5. **Additive Queue Protection Rule**:
   * All search runs ([`fetch_gmail_alerts.py`](file:///P:/Projects/job-search-consultant/fetch_gmail_alerts.py) & [`fetch_jobspy_roles.py`](file:///P:/Projects/job-search-consultant/fetch_jobspy_roles.py)) MUST preserve all existing unreviewed/unapplied jobs in `state.json`.
   * Newly discovered jobs are strictly **ADDED** to the queue using URL/ID deduplication. Roles are ONLY removed when explicitly applied for or dismissed by the user.

6. **Director-Level Role Scope Negotiation Strategy**:
   * For senior manager / manager openings that match technical GEO/AEO and web strategy competencies (e.g., Sysdig), the system builds a tailored package positioning candidate as a Director-level executive to negotiate scope and compensation elevation ({{TARGET_COMPENSATION_MIN}}).

7. **Open-Source Multi-Board JobSpy Integration**:
   * Integrated `python-jobspy` open-source scraper engine ([`fetch_jobspy_roles.py`](file:///P:/Projects/job-search-consultant/fetch_jobspy_roles.py)) querying **LinkedIn and Indeed** for live $0-cost job extraction.

8. **Strict Location Filtering Engine (Remote & DFW Local Only)**:
   * Enforced `is_remote=True` flags and strict location validation (`is_valid_location()`) in [`fetch_jobspy_roles.py`](file:///P:/Projects/job-search-consultant/fetch_jobspy_roles.py).

9. **Authoritative Candidate Baseline Career Truth**:
   * **{{PREVIOUS_COMPANY_1}}, Inc. (Irving, TX)**: *Global Web Marketing Director of Development* (**June 2008 - August 2026**) — Managing a **13+ person cross-functional team** (Development, DevOps, QA, BA, SEO); owning global web operations across 34 countries; **leading discovery, ROI evaluation, and decision-making for next-gen DXP to replace legacy AEM**; **organizing and executing the TrendAI site redesign & migration to Sanity CMS**; integrating mPulse, Cludo, AEM 6.x, Marketo, Tealium, GA4; driving +15% demo conversion uplift & +42% self-serve digital conversion rate.
   * **{{PREVIOUS_COMPANY_2}}, Inc. (Southlake, TX)**: *Product Manager of Web and E-commerce* (**Aug 2007 - Mar 2008**) — E-commerce storefronts for mobile apps & partner channels (Sprint), boosting checkout conversion by +34%.
   * **{{PREVIOUS_COMPANY_3}}, Inc. (Addison, TX)**: *E-commerce and Web Marketing Manager* (**Apr 2001 - Apr 2007**) — Sustaining 35%+ annual online sales growth via SEO/SEM/Email/Marketplaces.
   * **University of Texas at Arlington (Arlington, TX)**: *Bachelor of Arts (B.A.), E-Business Management & Internet Development* (Degree)
   * **Texas A&M University (College Station, TX)**: *Engineering Technology Coursework*

---

## 📜 2. Technical System Revision History

### **Revision 1.79** | *2026-08-18*
* **Full Migration to `P:\Projects\job-search-consultant`**:
  * Consolidated all Python scripts, agent configuration, state files, active application packages, and HTML dashboards into `P:\Projects\job-search-consultant`.
  * Refactored all Python scripts to use dynamic script directory resolution (`os.path.dirname(os.path.abspath(__file__))`) and relative paths.
  * Verified live dashboard sync to [`P:\Projects\job-search-consultant\Job Search\dashboard.html`](file:///P:/Projects/job-search-consultant/Job%20Search/dashboard.html).

### **Revision 1.78** | *2026-08-17*
* **{{PREVIOUS_COMPANY_1}} End Date Updated to August 2026**.

### **Revision 1.77** | *2026-08-17*
* **Silent Background Server Launch (`subprocess.CREATE_NO_WINDOW`)**.

### **Revision 1.76** | *2026-08-14*
* **Additive Review Queue Preservation Engine**.

### **Revision 1.75** | *2026-08-13*
* **Sysdig Application Package & Submission Log (`JOB-19`)**.

### **Revision 1.74** | *2026-08-13*
* **Automated Cron Server Auto-Launch (`ensure_dashboard_server_running`)**.

### **Revision 1.73** | *2026-08-12*
* **1-Click "⚡ Apply & Build Package" Dashboard API Server & UI Integration**.

### **Revision 1.72** | *2026-08-12*
* **Strict Geographic & Location Safeguard Integration**.

### **Revision 1.71** | *2026-08-12*
* **FourLeaf Federal Credit Union Application Package & Submission Log (`JOB-18`)**.

### **Revision 1.70** | *2026-08-12*
* **Jobgether / FourLeaf Application Package & Submission Log (`JOB-17`)**.

### **Revision 1.69** | *2026-08-12*
* **Candidate Baseline Experience Expansion (DXP Replacement & TrendAI Sanity CMS Migration)**.

### **Revision 1.68** | *2026-08-12*
* **Spinutech Application Package & Submission Log (`JOB-16`)**.

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
| **`PROJECT_GOALS_AND_REVISIONS.md`** | [`./PROJECT_GOALS_AND_REVISIONS.md`](file:///P:/Projects/job-search-consultant/PROJECT_GOALS_AND_REVISIONS.md) | **[Current File]** System technical revision history and candidate baseline. |
| **`fetch_gmail_alerts.py`** | [`./fetch_gmail_alerts.py`](file:///P:/Projects/job-search-consultant/fetch_gmail_alerts.py) | Email job alert parser with dynamic pathing, silent background server auto-launch & additive queue merging. |
| **`dashboard_server.py`** | [`./dashboard_server.py`](file:///P:/Projects/job-search-consultant/dashboard_server.py) | **[Local API Server]** Background HTTP server listening silently on localhost:5000 for 1-click apply triggers. |
| **`sync_dashboard_from_state.py`** | [`./sync_dashboard_from_state.py`](file:///P:/Projects/job-search-consultant/sync_dashboard_from_state.py) | Automated state-to-HTML dashboard generator with 1-click apply button UI. |
| **`fetch_jobspy_roles.py`** | [`./fetch_jobspy_roles.py`](file:///P:/Projects/job-search-consultant/fetch_jobspy_roles.py) | Open-source Python multi-board live scraper engine with strict DFW/Remote location guardrails. |
| **`build_application_package.py`** | [`./build_application_package.py`](file:///P:/Projects/job-search-consultant/build_application_package.py) | **[Single Master Generator]** Unified Python engine configured with {{PREVIOUS_COMPANY_1}} end date August 2026. |
| **`state.json`** | [`./state.json`](file:///P:/Projects/job-search-consultant/state.json) | Central persistent state tracker for candidate profile, job listings, and active submissions. |
