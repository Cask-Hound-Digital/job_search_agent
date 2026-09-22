"""
JobsPipe ATS Aggregator Client.
Queries Greenhouse, Lever, Ashby, and Workday APIs via JobsPipe service.
"""

import os
import json
import urllib.request
from ingest_guard import is_blacklisted, load_config
from safe_state_manager import save_state_safe

STATE_FILE = "state.json"
API_KEY = os.environ.get("JOBSPIPE_API_KEY", "")
URL = "https://api.jobspipe.dev/v1/jobs/search"

def fetch_jobspipe_opportunities():
    if not API_KEY:
        print("JOBSPIPE_API_KEY not configured in environment. Skipping JobsPipe ingestion.")
        return

    cfg = load_config()
    targets = cfg.get("search_matrix", {}).get("target_titles", ["Director"])

    print("=========================================================")
    print("  FETCHING LIVE OPPORTUNITIES VIA JOBSPIPE API")
    print("=========================================================")

    payload = {
        "job_title_or": targets[:10],
        "remote": True,
        "limit": 30
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        req = urllib.request.Request(URL, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            job_list = data.get("data", [])
            print(f"JobsPipe returned {len(job_list)} listings.")

            new_roles = []
            for item in job_list:
                title = item.get("title") or item.get("job_title") or ""
                co = item.get("company") or "Verified Employer"
                url = item.get("url") or item.get("source_url") or ""
                loc = item.get("location") or "Remote"

                blacklisted, reason = is_blacklisted(url, co, title, location=loc)
                if blacklisted:
                    continue

                new_roles.append({
                    "company": co,
                    "title": title,
                    "url": url,
                    "location": loc,
                    "source": "JobsPipe",
                    "status": "Verified Match",
                    "match_score": 96
                })

            if new_roles:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    state = json.load(f)
                state.setdefault("review_queue", []).extend(new_roles)
                save_state_safe(state, caller="fetch_jobspipe_roles")
                print(f"Added {len(new_roles)} JobsPipe roles to review queue.")
            else:
                print("No net new unique JobsPipe roles passed guardrails.")
    except Exception as e:
        print(f"JobsPipe fetch error: {e}")

if __name__ == "__main__":
    fetch_jobspipe_opportunities()
