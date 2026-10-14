"""
Gmail Job Alert Digest Parser.
Connects via IMAP to extract and validate job listings from email alert digests.
"""

import imaplib
import email
from email.header import decode_header
import re
import os
import json
from ingest_guard import is_blacklisted
from safe_state_manager import save_state_safe

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "state.json")
GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
IMAP_SERVER = "imap.gmail.com"

def clean_url(url: str) -> str:
    if not url:
        return ""
    if "linkedin.com" in url:
        url = url.replace('/comm/jobs/view/', '/jobs/view/').split('?')[0].split('#')[0]
    elif "indeed.com" in url or "builtin.com" in url:
        url = url.split('&')[0].split('?')[0].split('#')[0]
    return url.rstrip('/')

def fetch_gmail_alerts():
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("GMAIL_USER or GMAIL_APP_PASSWORD not set in environment. Skipping email alert check.")
        return

    print("=========================================================")
    print(f"  CONNECTING TO GMAIL IMAP ({GMAIL_USER})")
    print("=========================================================")

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        mail.select("INBOX")

        status, messages = mail.search(None, '(OR FROM "linkedin" (OR FROM "indeed" FROM "googlealerts-noreply"))')
        if status != "OK" or not messages[0]:
            print("No new job alert emails found.")
            mail.logout()
            return

        msg_ids = messages[0].split()[-10:]  # Process latest 10 alert emails
        extracted_roles = {}

        for mid in msg_ids:
            res, msg_data = mail.fetch(mid, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/html":
                                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                break
                    else:
                        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

                    # 1. Parse HTML for <a> tags to extract link and context
                    try:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(body, 'html.parser')
                        for a_tag in soup.find_all('a', href=True):
                            clean_l = clean_url(a_tag['href'])
                            if any(domain in clean_l for domain in ["linkedin.com/jobs/view/", "indeed.com/viewjob", "builtin.com/job/"]):
                                if clean_l not in extracted_roles:
                                    anchor_text = a_tag.get_text(" ", strip=True)
                                    company, title = "Unknown", "Unknown"
                                    if " at " in anchor_text:
                                        parts = anchor_text.split(" at ")
                                        title, company = parts[0].strip(), parts[1].strip()
                                    elif " - " in anchor_text:
                                        parts = anchor_text.split(" - ")
                                        title, company = parts[0].strip(), parts[1].strip()
                                    elif anchor_text and len(anchor_text) < 100 and not any(k in anchor_text.lower() for k in ["view", "apply", "see job", "click", "http"]):
                                        title = anchor_text
                                    extracted_roles[clean_l] = {
                                        "url": clean_l,
                                        "company": company,
                                        "title": title
                                    }
                    except Exception:
                        pass

                    # 2. Regex fallback for any links missed by HTML parser
                    links = re.findall(r'href=["\'](https?://[^"\']+)["\']', body)
                    for l in links:
                        clean_l = clean_url(l)
                        if any(domain in clean_l for domain in ["linkedin.com/jobs/view/", "indeed.com/viewjob", "builtin.com/job/"]):
                            if clean_l not in extracted_roles:
                                extracted_roles[clean_l] = {
                                    "url": clean_l,
                                    "company": "Unknown",
                                    "title": "Unknown"
                                }

        mail.logout()
        print(f"Extracted {len(extracted_roles)} unique job links from email digests.")

        new_roles = []
        for r_url, r_data in extracted_roles.items():
            co = r_data.get("company") or "Unknown"
            title = r_data.get("title") or "Unknown"

            blacklisted, reason = is_blacklisted(r_url, company=co, title=title)
            if blacklisted:
                continue

            new_roles.append({
                "company": co,
                "title": title,
                "url": r_url,
                "source": "Gmail Alerts",
                "status": "Verified Match",
                "match_score": 90
            })

        if new_roles:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    state = json.load(f)
            else:
                state = {"applications": [], "review_queue": [], "archived_queue": []}
            state.setdefault("review_queue", []).extend(new_roles)
            save_state_safe(state, caller="fetch_gmail_alerts")
            print(f"Added {len(new_roles)} Gmail alert roles to review queue.")
        else:
            print("No net new Gmail alert roles passed guardrails.")

    except Exception as e:
        print(f"Gmail IMAP processing error: {e}")

if __name__ == "__main__":
    fetch_gmail_alerts()
