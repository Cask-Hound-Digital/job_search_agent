# PROJECT GOAL & REVISION TRACKER
**Candidate**: {{YOUR_FULL_NAME}}  
**Role Scope**: Director, Senior Director, Head of, VP, Senior Manager, and Lead roles across Web {{YOUR_NAME}}eting, Digital Experience, Website Growth, PLG, Web Strategy, SEO, Web & AI, and Web Development  
**Target Compensation**: $225,000+ USD / Year  
**Location Preferences**: 100% Remote (Primary) | Hybrid ONLY in Dallas–Fort Worth (DFW area near Grand Prairie, TX)  
**Search Hours Schedule**: **7:00 AM – 5:00 PM CT** (Business Hours Only | Every 4 Hours: 7am, 11am, 3pm CT)  
**System Location**: [`c:\Users\mark\.gemini\antigravity\scratch\job-search-consultant`](file:///c:/Users/mark\.gemini\antigravity\scratch\job-search-consultant)  
**Local Export Storage Directory**: `P:\Job Search\`  
**Shareable Template ZIP**: [`P:\Job Search\job_search_agent_template.zip`](file:///P:/Job%20Search/job_search_agent_template.zip)  
**Live GitHub Repository**: [github.com/RoadRashTX/job_search_agent](https://github.com/RoadRashTX/job_search_agent)  

---

## 🎯 1. Primary Objectives & Operating Rules

1. **Automated Job Board & 4-Channel Gmail Alert Monitoring**:
   * Run search cycles **strictly between 7:00 AM and 5:00 PM Central Time** (7:00 AM, 11:00 AM, 3:00 PM CT).
   * Automatically connect to `{{YOUR_GMAIL_ADDRESS}}` via IMAP script [`fetch_gmail_alerts.py`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/fetch_gmail_alerts.py) across **LinkedIn, Indeed, Lensa, and BuiltIn**.

2. **Expanded Target Title Matrix**:
   * **Head Level**: *Head of Web*, *Head of Digital*, *Head of Web Operations*, *Head of Web {{YOUR_NAME}}eting*, *Head of Web Development*, *Head of Website Growth*.
   * **Founding Level**: *Founding Web Director*, *Founding Growth Leader*, *Founding {{YOUR_NAME}}eter*.
   * **Director / Sr. Director**: *Director/Sr. Director of Web {{YOUR_NAME}}eting*, *Digital Experience*, *Website Growth*, *Growth {{YOUR_NAME}}eting*, *Web Strategy*, *Web Development*, *PLG*, *AI & Web*, *Analytics & Web*, *Web Operations*.
   * **VP Level**: *VP of Digital Experience*, *VP of SEO & Web Strategy*, *VP of Web*.
   * **Sr. Manager & Lead**: *Sr. Web {{YOUR_NAME}}eting Manager*, *Sr. Manager Web Development*, *Web & AI Lead/Director*.

3. **Strict Candidate Criteria Verification Engine**:
   * **Location Check**: Must be **100% Remote (US)** or **Hybrid in DFW Metroplex** (Grand Prairie/Dallas/Fort Worth area). Automatically discards non-DFW hybrid/onsite roles (e.g. CA, PA, NY hybrid).
   * **Compensation Floor**: Minimum $225,000+ USD target band.

4. **Tailored Application Materials**:
   * **Resumes**: Single-column, ATS-optimized layout with quantified 3-part bullet points (*Action Verb + Specific/Quantifiable Detail + Measurable Result*).
   * **Cover Letters**: Scannable hybrid 6-part layout (*Branding Header + Salutation + Intro + Bold Scannable Narrative Bullets + Value Closing + Sign-off*).
   * **Formats**: Output in both **PDF (`.pdf`)** and **Microsoft Word (`.docx`)** for every approved role.

5. **Strict User Approval Protocol (Zero Unapproved Submissions)**:
   * **Mandatory Review**: Present a structured job list containing **Live Posting URLs**, Company Name, Compensation, Match Score, and Tailoring Highlights for explicit user sign-off.
   * **No Automatic Submissions**: Applications are executed **only** after explicit user approval of specific URLs.

6. **Dedicated Local File Storage (`P:\Job Search\`)**:
   * Automatically organize all submitted application materials into separate company subfolders under `P:\Job Search\<Company Name>\`.

---

## 📜 2. Full Revision & Changelog History

### **Revision 1.26** | *2026-08-06 15:27:00*
* **Changelog**:
  * **Pushed Template Updates to GitHub Repository**: Committed and pushed latest template updates to [github.com/RoadRashTX/job_search_agent](https://github.com/RoadRashTX/job_search_agent) (`b250ba8`).
  * **Updated Shareable ZIP**: Re-packaged [`P:\Job Search\job_search_agent_template.zip`](file:///P:/Job%20Search/job_search_agent_template.zip).

### **Revision 1.25** | *2026-08-06 15:25:00*
* **Changelog**:
  * **Expanded Target Title Matrix**: Parsed candidate's spreadsheet image and updated [`fetch_gmail_alerts.py`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/fetch_gmail_alerts.py), [`state.json`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/state.json), and system rules with 26 exact title variations:
    * *Head of Web / Digital / Web Ops / Web {{YOUR_NAME}}eting / Web Dev / Website Growth*
    * *Founding Web / Founding Growth / Founding {{YOUR_NAME}}eter*
    * *Director / Sr. Director (Web {{YOUR_NAME}}eting, Digital Experience, Website Growth, PLG, AI & Web, Web Operations, Web Strategy, Analytics & Web)*
    * *VP (Digital Experience, SEO & Web Strategy, Web)*
    * *Sr. Web Manager / Sr. Manager Web Dev / Web & AI Lead*

### **Revision 1.24** | *2026-08-06 15:00:30*
* **Changelog**:
  * **3:00 PM CT Business Hours Search Cycle Completed**: Executed scheduled afternoon monitoring (`task-204`).
  * **Automated Audit Results**: Scanned `{{YOUR_GMAIL_ADDRESS}}` across LinkedIn, Indeed, Lensa, and BuiltIn emails.
  * **Enforced Architecture Filter**: Automatically detected and rejected 10 non-matching software architecture links (*Sr. Director, Architecture and AI*).

### **Revision 1.23** | *2026-08-06 14:13:00*
* **Changelog**:
  * **Added Lensa (`jobalert@lensa.com`) & BuiltIn (`@builtin.com`) Support**: Extended [`fetch_gmail_alerts.py`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/fetch_gmail_alerts.py) to monitor 4 major job alert channels simultaneously.

### **Revision 1.22** | *2026-08-06 14:06:10*
* **Changelog**:
  * **Added Indeed Alert Support (`@match.indeed.com`)**: Extended [`fetch_gmail_alerts.py`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/fetch_gmail_alerts.py) to monitor Indeed job alert emails.

### **Revision 1.21** | *2026-08-06 14:04:00*
* **Changelog**:
  * **Implemented Strict Candidate Criteria Filtering Engine**: Updated [`fetch_gmail_alerts.py`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/fetch_gmail_alerts.py) to audit incoming Gmail/LinkedIn job alerts against 3 strict rules (Title/Level, 100% Remote vs DFW Hybrid, $225k+ floor).

### **Revision 1.20** | *2026-08-06 12:47:00*
* **Changelog**:
  * **Gmail IMAP Connection Verified & Functional**: Authenticated with `{{YOUR_GMAIL_ADDRESS}}` via App Password and extracted direct LinkedIn job URLs from incoming job alert emails.

### **Revision 1.19** | *2026-08-06 11:24:30*
* **Changelog**:
  * **Added Gmail IMAP Integration Script**: Built [`fetch_gmail_alerts.py`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/fetch_gmail_alerts.py).

### **Revision 1.18** | *2026-08-06 11:18:55*
* **Changelog**:
  * **Enforced Mandatory Real-Time Live Validation Policy**: Mandated HTTP live verification for all search results and cleared stale aggregator listings from queue.

### **Revision 1.17** | *2026-08-06 11:00:15*
* **Changelog**:
  * **11:00 AM CT Business Hours Search Cycle Completed**: Executed scheduled midday monitoring (`task-204`).

### **Revision 1.16** | *2026-08-06 07:00:20*
* **Changelog**:
  * **7:00 AM CT Business Hours Search Cycle Completed**: Executed scheduled morning job board monitoring (`task-204`).

### **Revision 1.15** | *2026-08-05 17:22:10*
* **Changelog**:
  * **GitHub Repository Push Complete**: Successfully published template repository to [github.com/RoadRashTX/job_search_agent](https://github.com/RoadRashTX/job_search_agent).

### **Revision 1.14** | *2026-08-05 17:15:09*
* **Changelog**:
  * **Removed Name Attributions**: Completely scrubbed all references to external names/attributions across all project files.

### **Revision 1.13** | *2026-08-05 17:08:07*
* **Changelog**:
  * **Updated Template README Examples**: Updated `README.md` inside `job_search_agent_template.zip`.

### **Revision 1.12** | *2026-08-05 17:02:35*
* **Changelog**:
  * **Updated Template Placeholders**: Updated `config.json` inside `job_search_agent_template.zip`.

### **Revision 1.11** | *2026-08-05 17:01:00*
* **Changelog**:
  * **Created Generic Portable Template ZIP**: Built `create_template_zip.py` and packaged `job_search_agent_template.zip`.

### **Revision 1.10** | *2026-08-05 16:58:05*
* **Changelog**:
  * **Cron Schedule Modified to Business Hours (7am-5pm CT)**: Registered new cron task `task-204` (7am, 11am, 3pm CT).

### **Revision 1.9** | *2026-08-05 16:56:52*
* **Changelog**:
  * **Organized Local Drive Storage (`P:\Job Search\`)**: Created script `copy_to_p_drive.py` and structured dedicated company folders under `P:\Job Search\`.

### **Revision 1.8** | *2026-08-05 16:55:30*
* **Changelog**:
  * **Strict Location Policy Enforcement**: Removed `JOB-04` (Keystone Technologies) due to non-DFW hybrid attendance.

### **Revision 1.7** | *2026-08-05 16:52:30*
* **Changelog**:
  * **Application Submission Logged**: Logged candidate's submission to **Uniphore** (*Director of Digital Experience & Discoverability*).

### **Revision 1.6** | *2026-08-05 16:38:15*
* **Changelog**:
  * **Application Submission Logged**: Logged candidate's submission to **Rubrik** (*Director, Web & Digital {{YOUR_NAME}}eting*).

### **Revision 1.5** | *2026-08-05 16:30:55*
* **Changelog**:
  * **Application Submission Logged**: Logged candidate's application to **Hyland Software** (*Director, Web & Digital Experience*).

### **Revision 1.4** | *2026-08-05 16:29:48*
* **Changelog**:
  * **Strict Location Policy Enforcement**: Replaced `JOB-01` (Microsoft) with **Hyland Software**.

### **Revision 1.3** | *2026-08-05 16:20:25*
* **Changelog**:
  * **User Approval Execution**: Received explicit approval from {{YOUR_FULL_NAME}} to generate tailored application packages.

### **Revision 1.2** | *2026-08-05 16:04:35*
* **Changelog**:
  * **Enforced Pre-Submission Approval Policy**: Updated system protocol and [`state.json`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/state.json).

### **Revision 1.1** | *2026-08-05 15:42:07*
* **Changelog**:
  * **Digested Resume Portfolio**: Digitized and cataloged {{YOUR_FULL_NAME}}' 4 recent resume versions into markdown reference files in `resumes/`.

### **Revision 1.0** | *2026-08-05 15:33:28*
* **Changelog**:
  * **System Initialization**: Created project workspace and initialized persistent state tracker [`state.json`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/state.json).

---

## 📂 3. Workspace File Registry

| File Name | Location | Description |
| :--- | :--- | :--- |
| **`PROJECT_GOALS_AND_REVISIONS.md`** | [`./PROJECT_GOALS_AND_REVISIONS.md`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/PROJECT_GOALS_AND_REVISIONS.md) | **[Current File]** Project objectives, complete revision log, and system rules. |
| **`fetch_gmail_alerts.py`** | [`./fetch_gmail_alerts.py`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/fetch_gmail_alerts.py) | Python script with expanded 26-title target matrix across 4 channels. |
| **`state.json`** | [`./state.json`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/state.json) | Central persistent state tracker for candidate profile, job listings, and application statuses. |
| **`job_search_agent_template.zip`** | [`P:\Job Search\job_search_agent_template.zip`](file:///P:/Job%20Search/job_search_agent_template.zip) | Portable template package with clean placeholders for sharing. |
| **Resume Registry** | [`./resumes/`](file:///c:/Users/mark/.gemini/antigravity/scratch/job-search-consultant/resumes/) | Directory containing baseline resume versions in {{YOUR_NAME}}down format. |
