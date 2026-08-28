import imaplib
import email
from email.header import decode_header
import re
import json
import os
from datetime import datetime

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

from config_loader import get_target_titles, get_excluded_titles, get_allowed_local_cities

TARGET_TITLES = get_target_titles()
EXCLUDED_TITLES = get_excluded_titles()
DFW_LOCATIONS = get_allowed_local_cities()

REJECTION_RULES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rejection_rules.json")

def is_rejected_by_rules(title, url, location=""):
    if not os.path.exists(REJECTION_RULES_FILE):
        return False
    try:
        with open(REJECTION_RULES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        keywords = [k.lower() for k in data.get("hard_negative_keywords", [])]
        locs = [l.lower() for l in data.get("hard_excluded_locations", [])]
        
        t_lower = (title or "").lower()
        l_lower = (location or "").lower()

        for kw in keywords:
            if kw and kw in t_lower:
                return True
        for loc in locs:
            if loc and loc in l_lower:
                return True
    except Exception:
        pass
    return False

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

from config_loader import is_valid_target_title

def evaluate_job_criteria(title, context_text):
    combined_text = f"{title} {context_text}".lower()

    # 1. Strict Target Title Domain Validation
    if not is_valid_target_title(title):
        return False, f"Rejected: Title '{title}' is an excluded IC Engineer / PM / MOps role or out of target matrix"

    # 2. Exclusion Check
    for ex in EXCLUDED_TITLES:
        if ex in combined_text:
            return False, f"Rejected: Contains excluded domain/title term ({ex})"

    # 3. Location Check (Default Remote for email alerts unless non-Preferred Hybrid City hybrid explicitly stated)
    is_non_dfw_onsite = any(loc in combined_text for loc in ["onsite in california", "onsite in new york", "hybrid in lansdale"])

    if is_non_dfw_onsite:
        return False, "Rejected: Non-Preferred Hybrid City Onsite/Hybrid constraint"

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
            if is_valid and is_rejected_by_rules(j['title'], j['url']):
                is_valid = False
                reason = "Filtered out by candidate rejection rules"
            
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
                "date": j['date'],
                "date_added": datetime.now().strftime("%Y-%m-%d"),
                "time_scraped": datetime.now().isoformat()
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
                fresh_state = json.load(f)

            review_queue = fresh_state.get("review_queue", [])
            archived_queue = fresh_state.get("archived_queue", [])
            applications = fresh_state.get("applications", [])

            existing_urls = {j.get("url", "").split('?')[0].lower() for j in review_queue if j.get("url")}
            arch_urls = {j.get("url", "").split('?')[0].lower() for j in archived_queue if j.get("url")}
            app_urls = {a.get("job_url", "").split('?')[0].lower() for a in applications if a.get("job_url")}

            added_count = 0
            for v_job in valid_candidate_jobs:
                u_clean = v_job["url"].split('?')[0].lower()
                if u_clean not in existing_urls and u_clean not in arch_urls and u_clean not in app_urls:
                    review_queue.append(v_job)
                    existing_urls.add(u_clean)
                    added_count += 1

            fresh_state["review_queue"] = review_queue
            fresh_state["verified_gmail_jobs"] = review_queue
            fresh_state["rejected_gmail_jobs"] = rejected_jobs
            fresh_state["last_updated"] = datetime.now().strftime("%Y-%m-%d")

            with open(STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(fresh_state, f, indent=2)

            print(f"Updated {STATE_FILE}: Added {added_count} new unique verified roles. Total queue count: {len(review_queue)}.")

            # Automatically run JobSpy multi-board scraper, Built In & Dice scraper, audit ground-truth titles, ensure server is running, and sync live browser dashboard
            try:
                from fetch_jobspy_roles import run_jobspy_scraper
                from fetch_builtin_and_dice import run_builtin_and_dice_scraper
                from audit_and_fix_queue_companies import audit_queue
                from sync_dashboard_from_state import sync_dashboard
                from send_job_alert import notify_fresh_jobs

                run_jobspy_scraper()
                run_builtin_and_dice_scraper()
                audit_queue()

                # Run strict IC Engineer, Austin, and Compensation purges BEFORE Telegram notifications
                try:
                    import subprocess
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    purge_eng = os.path.join(script_dir, ".system_generated", "steps", "purge_eng.py")
                    # Run post-audit scripts directly
                    subprocess.run([sys.executable, "-c", "from config_loader import is_valid_target_title; import json, os; f='state.json'; state=json.load(open(f)); rq=[j for j in state.get('review_queue',[]) if is_valid_target_title(j.get('audited_role_title', j.get('title','')))]; state['review_queue']=rq; json.dump(state, open(f,'w'), indent=2)"], cwd=script_dir, check=False)
                except Exception as purge_err:
                    print(f"Warning running pre-telegram purge: {purge_err}")

                ensure_dashboard_server_running()
                sync_dashboard()

                # Trigger instant mobile push notifications for fresh jobs (<24h) AFTER all audits and purges
                with open(STATE_FILE, 'r', encoding='utf-8') as sf:
                    latest_state = json.load(sf)
                notify_fresh_jobs(latest_state.get("review_queue", []))

            except Exception as sync_err:
                print(f"Warning auditing/syncing dashboard: {sync_err}")

        return valid_candidate_jobs

    except Exception as e:
        print(f"Error in deep fetch Gmail alerts: {e}")
        return []

if __name__ == '__main__':
    fetch_and_filter_all_job_alerts()
