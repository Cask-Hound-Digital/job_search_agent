import json
import os
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

STATE_FILE = r".\state.json"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none'
}

def clean_company_string(co_raw):
    if not co_raw:
        return ""
    co = co_raw.strip()
    co = re.split(r'\s+[—–|-]\s+', co)[0].strip()
    co = re.sub(r'\s+in\s+.*$', '', co, flags=re.IGNORECASE).strip()
    co = re.sub(r'\s+United States$', '', co, flags=re.IGNORECASE).strip()
    if co.lower() in ["{{YOUR_NAME}}", "your job alert", "job alert", "linkedin", "verified employer", "hr", "recsolu", "target company"]:
        return ""
    return co

def extract_from_text_patterns(item):
    subj = item.get("email_subject", "")
    title = item.get("title", "")
    url = item.get("url", "")
    audited_title = item.get("audited_role_title", "")
    page_title = item.get("page_title", "")

    # 1. Check email_subject for 'at <Company>'
    m_subj = re.search(r'\sat\s+([A-Z0-9\s,&.\'-]+)$', subj, re.IGNORECASE)
    if m_subj:
        c = clean_company_string(m_subj.group(1))
        if c: return c

    # 2. Check page_title or audited_title for 'Role at Company'
    for text in [page_title, audited_title, title]:
        m_at = re.search(r'^(.*?)\s+at\s+(.*?)(?:\s+[—–|-]|\s+\|\s*LinkedIn|\s*$)', text, re.IGNORECASE)
        if m_at:
            c = clean_company_string(m_at.group(2))
            if c: return c

        m_hir = re.search(r'^(.*?)\s+hiring\s+(.*?)(?:\s+in|\s+[—–|-]|\s+\|\s*LinkedIn|\s*$)', text, re.IGNORECASE)
        if m_hir:
            c = clean_company_string(m_hir.group(1))
            if c: return c

    # 3. Check LinkedIn URL slug
    m_slug = re.search(r'-at-([a-z0-9-]+)-\d+', url, re.IGNORECASE)
    if m_slug:
        c = clean_company_string(m_slug.group(1).replace('-', ' ').title())
        if c: return c

    return ""

def fetch_and_extract_live_company(item):
    existing = item.get("company_name", "")
    if existing and existing.lower() not in ["verified employer", "{{YOUR_NAME}}", "your job alert", "job alert", "linkedin", "hr", "recsolu", "target company"]:
        return item, existing

    # Try pattern extraction first
    pat_co = extract_from_text_patterns(item)
    if pat_co:
        return item, pat_co

    url = item.get("url", "").strip()
    if not url or url == "#":
        return item, existing if existing else "Verified Employer"

    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=7) as resp:
            final_url = resp.geturl()
            html = resp.read().decode('utf-8', errors='ignore')

            # Check JSON-LD hiringOrganization
            m_org = re.search(r'"hiringOrganization"\s*:\s*\{\s*"@type"\s*:\s*"Organization"\s*,\s*"name"\s*:\s*"([^"]+)"', html, re.IGNORECASE)
            if m_org:
                c = clean_company_string(m_org.group(1))
                if c: return item, c

            # Check OG title
            og_match = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', html, re.IGNORECASE)
            if og_match:
                og_t = og_match.group(1)
                m_at = re.search(r'at\s+([A-Z0-9\s,&.\'-]+?)(?:\s+[—–|-]|\s+\|\s*LinkedIn|\s*$)', og_t, re.IGNORECASE)
                if m_at:
                    c = clean_company_string(m_at.group(1))
                    if c: return item, c

            # Check page title
            m_title = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
            pt = m_title.group(1) if m_title else ""
            
            m_at = re.search(r'at\s+([A-Z0-9\s,&.\'-]+?)(?:\s+[—–|-]|\s+\|\s*LinkedIn|\s*$)', pt, re.IGNORECASE)
            if m_at:
                c = clean_company_string(m_at.group(1))
                if c: return item, c

            m_hir = re.search(r'^(.*?)\s+hiring\s+', pt, re.IGNORECASE)
            if m_hir:
                c = clean_company_string(m_hir.group(1))
                if c: return item, c
    except Exception as e:
        pass

    # If all fails, parse title fallback cleanly instead of defaulting to Verified Employer
    title = item.get("title", "")
    if " at " in title:
        parts = title.split(" at ")
        if len(parts) >= 2:
            c = clean_company_string(parts[-1])
            if c: return item, c

    return item, existing if existing else "Verified Employer"

def run_recovery():
    if not os.path.exists(STATE_FILE):
        print("ERROR: state.json not found.")
        return

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state_data = json.load(f)

    review_queue = state_data.get("review_queue", [])
    print(f"Auditing & restoring company names across {len(review_queue)} review queue opportunities...")

    restored_count = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_and_extract_live_company, item) for item in review_queue]
        for future in as_completed(futures):
            item, co = future.result()
            if co and co != item.get("company_name") and co != "Verified Employer":
                item["company_name"] = co
                restored_count += 1

    state_data["review_queue"] = review_queue
    with open(STATE_FILE, "w", encoding="utf-8") as sf:
        json.dump(state_data, sf, indent=2)

    print(f"SUCCESS: Restored ground-truth company names for {restored_count} opportunities!")

if __name__ == '__main__':
    run_recovery()
