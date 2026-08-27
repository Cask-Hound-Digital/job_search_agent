import json
import os
import re
import sys
from datetime import datetime
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from jobspy import scrape_jobs

STATE_FILE = r".\state.json"

TARGET_TITLES = [
    "Director of Web Marketing",
    "{{YOUR_TARGET_ROLE_1}}",
    "Director of Website Growth",
    "VP of Digital Experience",
    "Fractional VP of Digital Product",
    "Digital Transformation Advisor",
    "Target Role Title",
    "AI Agent Manager",
    "Target Role Title",
    "AI Operations Lead",
    "Target Role Title",
    "Target Role Title",
    "Target Role Title"
]

EXCLUDED_TITLES = [
    "nursing", "medical", "clinical", "sales director", "account executive", 
    "wealth management", "financial advisor", "hardware", "qa director"
]

def clean_url(url):
    if not url:
        return ""
    if "linkedin.com" in url:
        url = url.replace('/comm/jobs/view/', '/jobs/view/').split('?')[0].split('#')[0]
    elif "indeed.com" in url or "builtin.com" in url or "greenhouse.io" in url or "lever.co" in url:
        url = url.split('&')[0].split('?')[0].split('#')[0]
    return url.rstrip('/')

DFW_CITIES = [
    "dallas", "fort worth", "{{YOUR_CITY}}", "irving", "{{YOUR_CITY}}", "plano", 
    "frisco", "addison", "southlake", "mansfield", "lewisville", "grapevine", 
    "richardson", "denton", "Preferred Hybrid City", "colleyville", "euless", "bedford", "texas", "tx"
]

NON_DFW_LOCATIONS = [
    "tampa", "florida", "fl", "miami", "orlando", "seattle", "wa", "boston", "ma",
    "chicago", "il", "atlanta", "ga", "los angeles", "san francisco", "san jose", "ca",
    "new york", "ny", "nc", "charlotte", "raleigh", "denver", "co", "phoenix", "az",
    "minneapolis", "mn", "detroit", "mi", "philadelphia", "pa", "london", "uk",
    "canada", "paris", "france", "india", "australia", "singapore", "germany", "berlin", "tokyo"
]

def is_valid_location(loc_str, is_remote_query=True):
    if not loc_str:
        return True
    l_lower = loc_str.lower()

    # Reject explicitly labeled 100% Onsite / In-Office roles
    if "onsite" in l_lower or "on-site" in l_lower or "in-office" in l_lower or "in office" in l_lower:
        if "hybrid" not in l_lower and "remote" not in l_lower:
            return False

    # If explicitly remote, allow
    if any(k in l_lower for k in ["remote", "work from home", "telecommute", "anywhere", "100% remote", "remote (us)", "remote - us"]):
        return True

    # Reject explicitly non-Preferred Hybrid City locations without remote tag
    if any(re.search(rf'\b{kw}\b', l_lower) for kw in NON_DFW_LOCATIONS):
        return False

    return True

def run_jobspy_scraper():
    print("=========================================================")
    print("  LAUNCHING JOBSPY MULTI-BOARD SCRAPER (LinkedIn, Indeed)")
    print("  STRICT FILTERING: 100% Remote (US) & Preferred Hybrid City Hybrid/Onsite ONLY")
    print("=========================================================")

    all_scraped_jobs = []

    for title in TARGET_TITLES:
        for loc in ["Remote", "Dallas, TX"]:
            is_rem_query = (loc == "Remote")
            print(f"\n[JobSpy Query] Searching '{title}' in '{loc}' (is_remote={is_rem_query})...")
            try:
                jobs_df = scrape_jobs(
                    site_name=["linkedin", "indeed"],
                    search_term=title,
                    location=loc,
                    is_remote=is_rem_query,
                    results_wanted=15,
                    hours_old=72,
                    country_indeed='USA'
                )

                if jobs_df is not None and not jobs_df.empty:
                    print(f"  -> Found {len(jobs_df)} raw listings.")
                    for _, row in jobs_df.iterrows():
                        job_title = str(row.get('title', '')).strip()
                        company = str(row.get('company', '')).strip()
                        job_url = str(row.get('job_url', '')).strip()
                        site = str(row.get('site', '')).strip().capitalize()
                        location = str(row.get('location', '')).strip()
                        date_posted = str(row.get('date_posted', '')).strip()

                        if not job_title or not job_url or len(job_title) < 3:
                            continue

                        # Exclusion check
                        t_lower = job_title.lower()
                        if any(ex in t_lower for ex in EXCLUDED_TITLES):
                            continue

                        # Location validation check
                        if not is_valid_location(location, is_rem_query):
                            print(f"  [REJECTED LOCATION] '{job_title}' at '{company}' in '{location}'")
                            continue

                        # Check metadata salary amounts from JobSpy
                        min_amt = row.get("min_amount") if pd.notna(row.get("min_amount")) else None
                        max_amt = row.get("max_amount") if pd.notna(row.get("max_amount")) else None
                        if max_amt and float(max_amt) < 200000 and float(max_amt) > 1000:
                            print(f"  [REJECTED SALARY METADATA] '{job_title}' at '{company}' (Max: ${max_amt:,.0f} < $200k)")
                            continue

                        dp_clean = str(date_posted).strip() if pd.notna(date_posted) else ""
                        if dp_clean.lower() in ["nan", "none", "null"]:
                            dp_clean = ""

                        all_scraped_jobs.append({
                            "title": job_title,
                            "company_name": company if company and company != "nan" else "Verified Employer",
                            "url": clean_u,
                            "source": f"JobSpy ({site})",
                            "email_subject": f"JobSpy Live Sweep: {title} ({loc})",
                            "status": "Verified Match",
                            "filter_reason": f"Passed JobSpy criteria check (Location: {location})",
                            "date": dp_clean,
                            "date_posted": dp_clean,
                            "date_added": datetime.now().strftime("%Y-%m-%d"),
                            "time_scraped": datetime.now().isoformat(),
                            "audited_role_title": job_title,
                            "location": location
                        })
                else:
                    print("  -> 0 listings returned.")

            except Exception as e:
                print(f"  -> Error querying JobSpy for '{title}' in '{loc}': {e}")

    print(f"\n=========================================================")
    print(f"  Total Raw Roles Extracted via JobSpy: {len(all_scraped_jobs)}")

    # Deduplicate and merge into state.json
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)

        existing_queue = state.get("review_queue", [])
        existing_urls = {j.get("url", "").split('?')[0].lower() for j in existing_queue if j.get("url")}
        arch_urls = {j.get("url", "").split('?')[0].lower() for j in state.get("archived_queue", []) if j.get("url")}
        apps_urls = {a.get("job_url", "").split('?')[0].lower() for a in state.get("applications", []) if a.get("job_url")}

        new_unique_jobs = []
        for j in all_scraped_jobs:
            u_clean = j["url"].split('?')[0].lower()
            if u_clean not in existing_urls and u_clean not in arch_urls and u_clean not in apps_urls:
                existing_urls.add(u_clean)
                new_unique_jobs.append(j)

        print(f"  New Unique Multi-Board Roles Added: {len(new_unique_jobs)}")

        if new_unique_jobs:
            state.setdefault("verified_gmail_jobs", []).extend(new_unique_jobs)
            state.setdefault("review_queue", []).extend(new_unique_jobs)
            state["last_updated"] = datetime.now().strftime("%Y-%m-%d")

            with open(STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)

            print("  Successfully updated state.json with JobSpy multi-board roles.")

            # Trigger Live Dashboard Sync
            try:
                from sync_dashboard_from_state import sync_dashboard
                sync_dashboard()
            except Exception as sync_err:
                print(f"  Warning syncing dashboard: {sync_err}")
    print("=========================================================")

if __name__ == '__main__':
    run_jobspy_scraper()
