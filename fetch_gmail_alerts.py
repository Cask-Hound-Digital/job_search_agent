import imaplib
import email
from email.header import decode_header
import re
import json
import os

def _load_env_file():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")

_load_env_file()

GMAIL_USER = os.environ.get("GMAIL_USER", "{{YOUR_GMAIL_ADDRESS}}")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
IMAP_SERVER = "imap.gmail.com"

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")

# Candidate Expanded Target Title & Keyword Matrix
TARGET_TITLES = [
    "head of web", "head of digital", "head of web operations", "head of web marketing", "head of web development", "head of website growth", "head of growth",
    "founding web", "founding growth", "founding marketer",
    "director, web", "director of web", "director, digital", "director of digital", "e-commerce director", "director, ecommerce", "director of ecommerce",
    "director of website growth", "director, website growth", "director of growth marketing", "director, growth marketing", "director, growth", "director of growth",
    "director, ai", "director of ai", "director, analytics & web", "director of plg", "director, plg", "director, geo", "director of geo", "director, seo", "director of seo",
    "engineering director, web", "director, web operations", "director of web strategy", "director, experience", "director of experience",
    "senior director, web", "senior director of web", "senior director, digital", "senior director of digital",
    "senior director, growth", "senior director of growth", "senior director, global marketing",
    "vp, digital", "vp of digital", "vp, experience", "vp of experience", "vp - seo", "vp of seo", "vp, web", "vp of web", "vice president, digital", "vice president, ecommerce", "vp, product and ux",
    "fractional vp", "fractional vp of digital", "fractional vp, digital product", "digital product", "web operations",
    "digital transformation advisor", "transformation advisor", "digital transformation",
    "sr. web", "senior web", "senior manager, web", "senior manager of web", "senior manager, digital", "senior manager of digital",
    "web & ai", "web and ai"
]

EXCLUDED_TITLES = [
    "software architecture", "enterprise architect", "cloud architect",
    "infrastructure director", "qa director", "devops director",
    "hardware director", "sales director", "account executive", "financial advisor",
    "nursing director", "medical director", "clinical director", "wealth management", "rewards business partner"
]

DFW_LOCATIONS = [
    "dallas", "fort worth", "{{YOUR_PREFERRED_HYBRID_CITY}}", "{{YOUR_CITY}}", "irving", "plano",
    "frisco", "richardson", "arlington", "texas", "tx"
]

def clean_url(url):
    if "linkedin.com" in url:
        url = url.replace('/comm/jobs/view/', '/jobs/view/').split('?')[0].split('#')[0]
    elif "indeed.com" in url or "builtin.com" in url or "greenhouse.io" in url or "lever.co" in url:
        url = url.split('&')[0].split('?')[0].split('#')[0]
    return url.rstrip('/')

def get_job_dedup_key(title, url, company=""):
    # 1. Extract canonical Job ID if available
    clean_u = clean_url(url)
    match_li = re.search(r'linkedin\.com/jobs/view/(\d+)', clean_u)
    if match_li:
        return f"li_id_{match_li.group(1)}"
    
    match_gh = re.search(r'greenhouse\.io/[^/]+/jobs/(\d+)', clean_u)
    if match_gh:
        return f"gh_id_{match_gh.group(1)}"

    # 2. Fallback to normalized Title + Company
    norm_title = re.sub(r'[^a-z0-9]', '', title.lower())
    norm_co = re.sub(r'[^a-z0-9]', '', company.lower())
    if norm_title and norm_co:
        return f"tc_{norm_title}_{norm_co}"

    # 3. Fallback to clean URL
    return f"url_{clean_u}"

def evaluate_job_criteria(title, context_text):
    combined_text = f"{title} {context_text}".lower()

    # 1. Exclusion Check
    for ex in EXCLUDED_TITLES:
        if ex in combined_text:
            return False, f"Rejected: Contains excluded domain/title term ({ex})"

    # 2. Expanded Target Title Match Check
    has_target_title = any(t in combined_text for t in TARGET_TITLES)
    if not has_target_title:
        return False, "Rejected: Title does not match candidate's expanded target title matrix"

    # 3. Location Check (Default Remote for email alerts unless non-{{YOUR_PREFERRED_HYBRID_CITY}} hybrid explicitly stated)
    is_dfw = any(loc in combined_text for loc in DFW_LOCATIONS)
    is_non_dfw_onsite = any(loc in combined_text for loc in ["onsite in california", "onsite in new york", "hybrid in lansdale"])

    if is_non_dfw_onsite:
        return False, "Rejected: Non-{{YOUR_PREFERRED_HYBRID_CITY}} Onsite/Hybrid constraint"

    return True, "Passed candidate criteria check"

def ensure_dashboard_server_running():
    import urllib.request
    import subprocess

    try:
        req = urllib.request.urlopen("http://localhost:5000/api/status", timeout=2)
        if req.status == 200:
            print("  [SERVER] Dashboard API Server (localhost:5000) is ALREADY running.")
            return
    except Exception:
        pass

    print("  [SERVER] Launching Dashboard API Server (localhost:5000) for 1-click apply...")
    python_exe = r"C:\Users\{{YOUR_NAME}}\AppData\Local\Python\pythoncore-3.14-64\python.exe"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    subprocess.Popen(
        [python_exe, "dashboard_server.py"],
        cwd=base_dir,
        creationflags=subprocess.CREATE_NO_WINDOW,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def fetch_and_filter_all_job_alerts():
    print(f"Connecting to Gmail ({GMAIL_USER}) via IMAP for Deep Multi-Job Parsing...")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        mail.select("inbox")

        status, msg_data = mail.search(None, 'ALL')
        email_ids = msg_data[0].split()

        print(f"Deep parsing recent {min(len(email_ids), 40)} emails in inbox across all individual job links...")

        all_individual_jobs = []

        for e_id in email_ids[-40:]:
            _, data = mail.fetch(e_id, "(RFC822)")
            for response_part in data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    sender = msg.get("From", "").lower()
                    # Filter out Lensa - only parse LinkedIn, Indeed, BuiltIn
                    if not any(domain in sender for domain in ["linkedin", "indeed", "builtin"]):
                        continue

                    subj = msg["Subject"]
                    subj_text = ""
                    if subj:
                        for part, encoding in decode_header(subj):
                            if isinstance(part, bytes):
                                subj_text += part.decode(encoding or "utf-8", errors="ignore")
                            else:
                                subj_text += str(part)

                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            b_bytes = part.get_payload(decode=True)
                            if b_bytes:
                                body += b_bytes.decode('utf-8', errors='ignore')
                    else:
                        b_bytes = msg.get_payload(decode=True)
                        if b_bytes:
                            body += b_bytes.decode('utf-8', errors='ignore')

                    # Deep parse HTML anchor tags
                    matches = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', body, re.IGNORECASE | re.DOTALL)
                    for href, text_content in matches:
                        if any(domain in href for domain in ["linkedin.com/jobs/view", "linkedin.com/comm/jobs/view", "indeed.com", "builtin.com"]):
                            clean_href = clean_url(href)
                            clean_title = re.sub(r'<[^>]+>', ' ', text_content).strip()
                            clean_title = re.sub(r'\s+', ' ', clean_title)

                            if len(clean_title) > 3 and not any(skip in clean_title.lower() for skip in ["unsubscribe", "view all", "privacy policy", "settings", "job alert"]):
                                all_individual_jobs.append({
                                    "email_subject": subj_text.strip(),
                                    "title": clean_title,
                                    "url": clean_href,
                                    "date": msg.get("Date", "")
                                })

        mail.logout()

        # Multi-Layer Strict Deduplication
        valid_candidate_jobs = []
        rejected_jobs = []
        seen_keys = set()

        for j in all_individual_jobs:
            co = ""
            subj = j['email_subject']
            if " at " in subj: co = subj.split(" at ")[-1].strip()
            elif " @ " in subj: co = subj.split(" @ ")[-1].strip()

            dedup_key = get_job_dedup_key(j['title'], j['url'], co)
            if dedup_key in seen_keys:
                continue
            seen_keys.add(dedup_key)

            is_valid, reason = evaluate_job_criteria(j['title'], j['email_subject'])
            
            source = "LinkedIn"
            if "indeed.com" in j['url']: source = "Indeed"
            elif "builtin.com" in j['url']: source = "BuiltIn"

            job_entry = {
                "title": j['title'],
                "url": j['url'],
                "source": source,
                "email_subject": j['email_subject'],
                "status": "Verified Match" if is_valid else "Rejected",
                "filter_reason": reason,
                "date": j['date']
            }

            if is_valid:
                valid_candidate_jobs.append(job_entry)
            else:
                rejected_jobs.append(job_entry)

        print(f"\nExtracted {len(all_individual_jobs)} Total Individual Job Links Across All Email Digests.")
        print(f"Strict Deduplicated: {len(valid_candidate_jobs)} Unique Verified Matching Roles.")
        print(f"Filtered out {len(rejected_jobs)} Non-matching or Duplicate Roles.")

        # Save to state.json with Additive Queue Merging
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state_data = json.load(f)

            existing_queue = state_data.get("verified_gmail_jobs", [])
            existing_urls = {j.get("url", "").split('?')[0].lower() for j in existing_queue if j.get("url")}
            app_urls = {a.get("job_url", "").split('?')[0].lower() for a in state_data.get("applications", []) if a.get("job_url")}

            added_count = 0
            for v_job in valid_candidate_jobs:
                u_clean = v_job["url"].split('?')[0].lower()
                if u_clean not in existing_urls and u_clean not in app_urls:
                    existing_queue.append(v_job)
                    existing_urls.add(u_clean)
                    added_count += 1

            state_data["verified_gmail_jobs"] = existing_queue
            state_data["review_queue"] = existing_queue
            state_data["rejected_gmail_jobs"] = rejected_jobs
            state_data["last_updated"] = "2026-08-14T12:00:00-05:00"

            with open(STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2)

            print(f"Updated {STATE_FILE}: Added {added_count} new unique verified roles. Total queue count: {len(existing_queue)}.")

            # Automatically run JobSpy multi-board scraper, audit ground-truth titles, ensure server is running, and sync live browser dashboard
            try:
                from fetch_jobspy_roles import run_jobspy_scraper
                from audit_and_fix_queue_companies import audit_queue
                from sync_dashboard_from_state import sync_dashboard
                run_jobspy_scraper()
                audit_queue()
                ensure_dashboard_server_running()
                sync_dashboard()
            except Exception as sync_err:
                print(f"Warning auditing/syncing dashboard: {sync_err}")

        return valid_candidate_jobs

    except Exception as e:
        print(f"Error in deep fetch Gmail alerts: {e}")
        return []

if __name__ == '__main__':
    fetch_and_filter_all_job_alerts()
