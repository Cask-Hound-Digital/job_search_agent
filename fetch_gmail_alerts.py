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

STATE_FILE = "state.json"
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
        extracted_links = set()

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

                    links = re.findall(r'href=["\'](https?://[^"\']+)["\']', body)
                    for l in links:
                        clean_l = clean_url(l)
                        if any(domain in clean_l for domain in ["linkedin.com/jobs/view/", "indeed.com/viewjob", "builtin.com/job/"]):
                            extracted_links.add(clean_l)

        mail.logout()
        print(f"Extracted {len(extracted_links)} unique job links from email digests.")

    except Exception as e:
        print(f"Gmail IMAP processing error: {e}")

if __name__ == "__main__":
    fetch_gmail_alerts()
