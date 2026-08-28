import json
import os
import re
import sys
from datetime import datetime
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from jobspy import scrape_jobs

from config_loader import get_target_titles, get_excluded_titles, get_allowed_local_cities, get_min_salary_floor, get_primary_location

STATE_FILE = r".\state.json"

TARGET_TITLES = get_target_titles()
EXCLUDED_TITLES = get_excluded_titles()
ALLOWED_LOCAL_CITIES = get_allowed_local_cities()
MIN_SALARY_FLOOR = get_min_salary_floor()
PRIMARY_LOCATION = get_primary_location()

def clean_url(url):
    if not url:
        return ""
    if "linkedin.com" in url:
        url = url.replace('/comm/jobs/view/', '/jobs/view/').split('?')[0].split('#')[0]
    elif "indeed.com" in url or "builtin.com" in url or "greenhouse.io" in url or "lever.co" in url:
        url = url.split('&')[0].split('?')[0].split('#')[0]
    return url.rstrip('/')

NON_DFW_LOCATIONS = [
    "tampa", "florida", "fl", "miami", "orlando", "seattle", "wa", "boston", "ma",
    "chicago", "il", "atlanta", "ga", "los angeles", "san francisco", "san jose", "ca",
    "new york", "ny", "nc", "charlotte", "raleigh", "denver", "co", "phoenix", "az",
    "minneapolis", "mn", "detroit", "mi", "philadelphia", "pa", "london", "uk",
    "canada", "paris", "france", "india", "australia", "singapore", "germany", "berlin", "tokyo"
]

INTL_EXCLUDED_LOCATIONS = [
    "india", "mumbai", "bengaluru", "hyderabad", "pune", "gurgaon", "delhi", "noida",
    "hong kong", "indonesia", "jakarta", "singapore", "uk", "london", "england",
    "europe", "australia", "sydney", "melbourne", "canada", "toronto", "vancouver",
    "china", "shenzhen", "shanghai", "beijing", "japan", "tokyo", "germany", "berlin",
    "france", "paris", "philippines", "manila", "taiwan", "korea", "seoul", "vietnam",
    "brazil", "mexico", "ireland", "dublin", "poland", "warsaw", "estonia", "tallinn",
    "romania", "bucharest", "luxembourg", "switzerland", "zurich", "austria", "netherlands", "amsterdam"
]

def is_valid_location(loc_str, is_remote_query=True, title=""):
    combined = f"{loc_str} {title}".lower()

    # HARD REJECT: International non-US locations even if marked remote
    for intl in INTL_EXCLUDED_LOCATIONS:
        if re.search(rf'\b{intl}\b', combined):
            return False

    # Reject explicitly labeled 100% Onsite / In-Office roles if not Preferred Hybrid City
    if "onsite" in combined or "on-site" in combined or "in-office" in combined or "in office" in combined:
        if "hybrid" not in combined and "remote" not in combined:
            if not any(re.search(rf'\b{city}\b', combined) for city in ALLOWED_LOCAL_CITIES):
                return False

    # Check 1: Explicit remote keywords in location or title
    if any(k in combined for k in ["remote", "work from home", "telecommute", "anywhere", "100% remote", "remote (us)", "remote - us"]):
        return True

    # Check 2: Explicit Preferred Hybrid City local city match
    if any(re.search(rf'\b{city}\b', combined) for city in ALLOWED_LOCAL_CITIES):
        return True

    # Default fallback: Reject if not explicitly US Remote or Preferred Hybrid City Local
    return False

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

                        # Strict target title domain check
                        from config_loader import is_valid_target_title
                        if not is_valid_target_title(job_title):
                            print(f"  [REJECTED TITLE UNRELATED] '{job_title}' at '{company}'")
                            continue

                        # Location validation check
                        if not is_valid_location(location, is_rem_query, job_title):
                            print(f"  [REJECTED LOCATION] '{job_title}' at '{company}' in '{location}'")
                            continue

                        # Check metadata salary amounts from JobSpy
                        min_amt = row.get("min_amount") if pd.notna(row.get("min_amount")) else None
                        max_amt = row.get("max_amount") if pd.notna(row.get("max_amount")) else None
                        if max_amt and float(max_amt) < 200000 and float(max_amt) > 1000:
                            print(f"  [REJECTED SALARY METADATA] '{job_title}' at '{company}' (Max: ${max_amt:,.0f} < $200k)")
                            continue

                        dp_clean = str(date_posted).strip() if pd.notna(date_posted) else ""
                        if not dp_clean or dp_clean.lower() in ["nan", "none", "null", "undefined"]:
                            dp_clean = datetime.now().strftime("%Y-%m-%d")

                        clean_u = job_url.split('?')[0].strip()

                        all_scraped_jobs.append({
                            "title": job_title,
                            "company_name": company if company and company != "nan" else "Verified Employer",
                            "url": clean_u,
                            "source": f"JobSpy ({site})",
                            "email_subject": f"JobSpy Live Sweep: {job_title} ({location})",
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
