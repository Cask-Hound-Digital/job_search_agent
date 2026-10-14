"""
Gmail Job Alert Digest Parser.
Connects via Gmail API OAuth2 (token.json) to extract and validate job listings from email alert digests.
"""

import os
import re
import json
import base64
from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from ingest_guard import is_blacklisted, score_role
from safe_state_manager import save_state_safe

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "state.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def clean_url(url: str) -> str:
    if not url:
        return ""
    if "linkedin.com" in url:
        url = url.replace('/comm/jobs/view/', '/jobs/view/').split('?')[0].split('#')[0]
    elif "indeed.com" in url or "builtin.com" in url:
        url = url.split('&')[0].split('?')[0].split('#')[0]
    return url.rstrip('/')

def get_gmail_service():
    """
    Returns an authorized Gmail API service instance using token.json.
    Refreshes the token if expired.
    """
    if not os.path.exists(TOKEN_FILE):
        return None

    creds = None
    try:
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    except Exception as e:
        print(f"Error loading token.json: {e}")
        return None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                    f.write(creds.to_json())
            except Exception as e:
                print(f"Error refreshing token.json: {e}")
                return None
        else:
            return None

    try:
        return build("gmail", "v1", credentials=creds)
    except Exception as e:
        print(f"Error initializing Gmail API service: {e}")
        return None

def extract_email_body(payload: dict) -> str:
    """Recursively extracts HTML or text body from a Gmail message payload."""
    if not payload:
        return ""

    if "parts" in payload:
        for part in payload["parts"]:
            mime = part.get("mimeType", "")
            if mime == "text/html":
                data = part.get("body", {}).get("data", "")
                if data:
                    return base64.urlsafe_b64decode(data.encode("ASCII")).decode("utf-8", errors="ignore")
            elif "parts" in part:
                sub = extract_email_body(part)
                if sub:
                    return sub

    data = payload.get("body", {}).get("data", "")
    if data:
        return base64.urlsafe_b64decode(data.encode("ASCII")).decode("utf-8", errors="ignore")
    return ""

def fetch_gmail_alerts():
    service = get_gmail_service()
    if not service:
        print("Gmail OAuth2 token (token.json) not found or invalid. Run 'python auth_gmail.py' to authenticate.")
        return

    print("=========================================================")
    print("  FETCHING JOB ALERTS VIA GMAIL API (OAuth2)")
    print("=========================================================")

    try:
        query = 'from:linkedin OR from:indeed OR from:googlealerts-noreply'
        results = service.users().messages().list(userId='me', q=query, maxResults=10).execute()
        messages = results.get('messages', [])

        if not messages:
            print("No job alert messages found in Gmail.")
            return

        print(f"Processing {len(messages)} recent alert messages...")
        extracted_roles = {}

        for m_meta in messages:
            msg = service.users().messages().get(userId='me', id=m_meta['id'], format='full').execute()
            body = extract_email_body(msg.get("payload", {}))
            if not body:
                continue

            try:
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

        print(f"Extracted {len(extracted_roles)} unique job links from Gmail alerts.")
        new_roles = []
        for r_url, r_data in extracted_roles.items():
            co = r_data.get("company") or "Unknown"
            title = r_data.get("title") or "Unknown"

            blacklisted, reason = is_blacklisted(r_url, company=co, title=title)
            if blacklisted:
                continue

            score = score_role(title=title, company=co)
            new_roles.append({
                "company": co,
                "title": title,
                "url": r_url,
                "source": "Gmail Alerts",
                "status": "Verified Match",
                "match_score": score
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
        print(f"Gmail API processing error: {e}")

if __name__ == "__main__":
    fetch_gmail_alerts()
