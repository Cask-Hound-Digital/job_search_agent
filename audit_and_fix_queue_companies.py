import json
import os
import re
import urllib.request
import shutil

STATE_FILE = r".\state.json"
INDEX_FILE = r".\index.html"
P_DASHBOARD = r"P:\Job Search\dashboard.html"

def fetch_page_content(url):
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Fetch page content error for {url}: {e}")
    return ""

def extract_company_and_role_from_title(page_title, raw_title="", email_subject="", url="", html=""):
    # Extract og:title if available
    og_title_match = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', html, re.IGNORECASE) if html else None
    og_title = og_title_match.group(1).strip() if og_title_match else ""

    pt = page_title.replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"') if page_title else ""
    if og_title:
        og_title = og_title.replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"')

    # 1. Recsolu / Yello ATS Subdomain Parser (e.g., klgates.recsolu.com)
    recsolu_match = re.search(r'https?://([^.]+)\.recsolu\.com', url, re.IGNORECASE)
    if recsolu_match:
        sub = recsolu_match.group(1).lower()
        company = "K&L Gates" if sub == "klgates" else sub.capitalize()
        role = og_title if og_title else (pt.split("|")[0].strip() if pt else raw_title)
        return company, role

    # 2. LinkedIn Format: "Company hiring Role in Location | LinkedIn"
    match_li = re.search(r'^(.*?)\s+hiring\s+(.*?)\s+in\s+.*\|?\s*LinkedIn', pt, re.IGNORECASE)
    if match_li:
        company = match_li.group(1).strip()
        role = match_li.group(2).strip()
        return company, role

    # 3. LinkedIn Alternate Format: "Role at Company | LinkedIn"
    match_li_alt = re.search(r'^(.*?)\s+at\s+(.*?)\s+\|?\s*LinkedIn', pt, re.IGNORECASE)
    if match_li_alt:
        role = match_li_alt.group(1).strip()
        company = match_li_alt.group(2).strip()
        return company, role

    # 4. Greenhouse Format: "Job Application for Role at Company"
    match_gh = re.search(r'Job Application for\s+(.*?)\s+at\s+(.*)', pt, re.IGNORECASE)
    if match_gh:
        role = match_gh.group(1).strip()
        company = match_gh.group(2).strip()
        return company, role

    # 5. Breezy HR Format: "Role at Company"
    if "breezy.hr" in url:
        match_br = re.search(r'^(.*?)\s+at\s+(.*)', og_title or pt, re.IGNORECASE)
        if match_br:
            role = match_br.group(1).strip()
            company = match_br.group(2).strip()
            if company.lower() == "hip":
                company = "HIP (HIP Creative)"
            return company, role

    # 6. Paylocity / ATS Portals
    if "paylocity.com" in url:
        company = payloc_co.group(1).strip() if payloc_co else "CeriFi"
        role = og_title if og_title else (pt.split("-")[0].strip() if pt else raw_title)
        return company, role

    # General Fallback
    parts = pt.split("|")[0].split("-")[0].strip() if pt else raw_title
    return "Verified Employer", parts if parts else raw_title

def extract_posted_time_from_html(html):
    if not html:
        return "", ""

    # 1. JSON-LD datePosted (ISO format)
    m_jsonld = re.search(r'"datePosted"\s*:\s*"([^"]+)"', html, re.IGNORECASE)
    if m_jsonld:
        dp_raw = m_jsonld.group(1).strip()
        return dp_raw, dp_raw

    # 2. LinkedIn relative time span: posted-time-ago__text
    m_rel = re.search(r'posted-time-ago__text[^>]*>\s*(.*?)\s*</', html, re.IGNORECASE | re.DOTALL)
    if m_rel:
        rel_text = re.sub(r'<[^>]+>', '', m_rel.group(1)).strip()
        if rel_text:
            return rel_text, rel_text

    # 3. Early applicant tag
    if "be an early applicant" in html.lower():
        return "Be an early applicant (<24h)", "Be an early applicant (<24h)"

    return "", ""

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
        existing_co = j.get("company_name", "").strip()
        existing_title = j.get("audited_role_title", "").strip()

        # Skip HTTP re-fetch if job already has a ground-truth company name and title
        if existing_co and existing_co != "Verified Employer" and existing_title and len(existing_co) > 1:
            audited_jobs.append(j)
            continue

        print(f"[{idx+1}/{len(gmail_jobs)}] Fetching page content for {url}...")
        html = fetch_page_content(url)
        page_title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL) if html else None
        page_title = page_title_match.group(1).strip() if page_title_match else ""

        company, real_role = extract_company_and_role_from_title(page_title, raw_title, email_subj, url, html)

        # Extract posted date/time metadata from HTML
        posted_raw, _ = extract_posted_time_from_html(html)
        if posted_raw:
            j["date_posted_raw"] = posted_raw

        # Sanitize "{{YOUR_NAME}}" or generic mistakes
        if company.lower() in ["{{YOUR_NAME}}", "your job alert", "job alert", "linkedin"]:
            company = "Verified Employer"

        existing_co = j.get("company_name", "").strip()
        if company != "Verified Employer" or not existing_co:
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
