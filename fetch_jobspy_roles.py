"""
Multi-Board Ingestion via python-jobspy.
Scrapes live job postings across LinkedIn and Indeed with salary extraction.
"""

import json
import os
from ingest_guard import is_blacklisted, load_config
from safe_state_manager import save_state_safe

STATE_FILE = "state.json"

def run_jobspy_scraper():
    try:
        from jobspy import scrape_jobs
    except ImportError:
        print("python-jobspy not installed. Run: pip install python-jobspy")
        return

    cfg = load_config()
    targets = cfg.get("search_matrix", {}).get("target_titles", ["Director of Product Management"])
    pref_remote = "remote" in [p.lower() for p in cfg.get("candidate", {}).get("workplace_preferences", ["remote"])]

    print("=========================================================")
    print("  FETCHING LIVE OPPORTUNITIES VIA JOBSPY (LinkedIn & Indeed)")
    print("=========================================================")

    all_jobs = []
    for term in targets[:3]:
        try:
            print(f"Querying JobSpy for: '{term}' (Remote: {pref_remote})")
            jobs = scrape_jobs(
                site_name=["linkedin", "indeed"],
                search_term=term,
                location="United States",
                results_wanted=10,
                is_remote=pref_remote
            )
            if jobs is not None and not jobs.empty:
                all_jobs.append(jobs)
        except Exception as e:
            print(f"JobSpy error on '{term}': {e}")

    if not all_jobs:
        print("JobSpy returned 0 raw results.")
        return

    import pandas as pd
    combined = pd.concat(all_jobs, ignore_index=True)
    new_roles = []

    for _, row in combined.iterrows():
        title = str(row.get("title", "")).strip()
        co = str(row.get("company", "")).strip()
        url = str(row.get("job_url", "")).strip()
        loc = str(row.get("location", "")).strip()
        sal = f"${int(row.get('min_amount')):,} - ${int(row.get('max_amount')):,}" if pd.notna(row.get("min_amount")) and pd.notna(row.get("max_amount")) else ""

        blacklisted, reason = is_blacklisted(url, co, title, location=loc, salary=sal)
        if blacklisted:
            continue

        new_roles.append({
            "company": co,
            "title": title,
            "url": url,
            "location": loc,
            "compensation": sal,
            "source": "JobSpy",
            "status": "Verified Match",
            "match_score": 94
        })

    if new_roles:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        state.setdefault("review_queue", []).extend(new_roles)
        save_state_safe(state, caller="fetch_jobspy_roles")
        print(f"Added {len(new_roles)} JobSpy roles to review queue.")
    else:
        print("No net new JobSpy roles passed guardrails.")

if __name__ == "__main__":
    run_jobspy_scraper()
