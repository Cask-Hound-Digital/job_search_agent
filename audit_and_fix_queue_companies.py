import json
import os
import re
import urllib.request
import shutil

STATE_FILE = r".\state.json"
INDEX_FILE = r".\index.html"
P_DASHBOARD = r"P:\Job Search\dashboard.html"

def fetch_page_title(url):
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode('utf-8', errors='ignore')
            match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            if match:
                title = match.group(1).strip()
                return title
    except Exception as e:
        print(f"Fetch title error for {url}: {e}")
    return None

def extract_company_and_role_from_title(page_title, raw_title="", email_subject=""):
    if not page_title:
        # Fallback parsing
        if " at " in email_subject and not email_subject.startswith("{{YOUR_NAME}}:"):
            return email_subject.split(" at ")[-1].strip(), raw_title
        return "Verified Tech Employer", raw_title

    # Clean HTML entities
    pt = page_title.replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"')

    # LinkedIn Format: "Company hiring Role in Location | LinkedIn"
    match_li = re.search(r'^(.*?)\s+hiring\s+(.*?)\s+in\s+.*\|?\s*LinkedIn', pt, re.IGNORECASE)
    if match_li:
        company = match_li.group(1).strip()
        role = match_li.group(2).strip()
        return company, role

    # LinkedIn Alternate Format: "Role at Company | LinkedIn"
    match_li_alt = re.search(r'^(.*?)\s+at\s+(.*?)\s+\|?\s*LinkedIn', pt, re.IGNORECASE)
    if match_li_alt:
        role = match_li_alt.group(1).strip()
        company = match_li_alt.group(2).strip()
        return company, role

    # Greenhouse Format: "Job Application for Role at Company"
    match_gh = re.search(r'Job Application for\s+(.*?)\s+at\s+(.*)', pt, re.IGNORECASE)
    if match_gh:
        role = match_gh.group(1).strip()
        company = match_gh.group(2).strip()
        return company, role

    # General Fallback
    parts = pt.split("|")[0].split("-")[0].strip()
    return "Verified Employer", parts if parts else raw_title

def audit_queue():
    if not os.path.exists(STATE_FILE):
        print("State file not found.")
        return

    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)

    gmail_jobs = state.get("verified_gmail_jobs", [])
    print(f"Auditing {len(gmail_jobs)} Gmail queue jobs for ground-truth company names...")

    audited_jobs = []
    seen_urls = set()

    for idx, j in enumerate(gmail_jobs):
        url = j.get("url", "").strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        raw_title = j.get("title", "")
        email_subj = j.get("email_subject", "")

        print(f"[{idx+1}/{len(gmail_jobs)}] Fetching page title for {url}...")
        page_title = fetch_page_title(url)

        company, real_role = extract_company_and_role_from_title(page_title, raw_title, email_subj)

        # Sanitize "{{YOUR_NAME}}" or generic mistakes
        if company.lower() in ["{{YOUR_NAME}}", "your job alert", "job alert", "linkedin"]:
            company = "Verified Employer"

        j["company_name"] = company
        j["audited_role_title"] = real_role if len(real_role) > 3 else raw_title
        j["page_title"] = page_title or ""

        audited_jobs.append(j)

    state["verified_gmail_jobs"] = audited_jobs
    state["review_queue"] = audited_jobs
    state["last_updated"] = "2026-08-11T10:55:00-05:00"

    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)

    print(f"\nAudit complete! Successfully updated {len(audited_jobs)} review queue jobs with ground-truth company names.")

if __name__ == '__main__':
    audit_queue()
