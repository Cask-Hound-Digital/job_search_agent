import json
import os

STATE_FILE = r"c:\Users\{{YOUR_NAME}}\.gemini\antigravity\scratch\job-search-consultant\state.json"

DFW_CITIES = [
    "dallas", "fort worth", "arlington", "irving", "{{YOUR_CITY}}", "plano", 
    "frisco", "addison", "southlake", "mansfield", "lewisville", "grapevine", 
    "richardson", "denton", "Preferred Hybrid City", "colleyville", "euless", "bedford"
]

NON_DFW_CITIES = [
    "austin", "houston", "san antonio", "san francisco", "san jose", "los angeles", 
    "new york", "boston", "chicago", "seattle", "atlanta", "denver", "miami", 
    "philadelphia", "phoenix", "san diego", "charlotte", "tampa", "orlando"
]

def clean_queue():
    if not os.path.exists(STATE_FILE):
        return

    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)

    queue = state.get("verified_gmail_jobs", [])
    initial_count = len(queue)
    valid_queue = []
    purged_count = 0

    for job in queue:
        title = job.get("title", "")
        company = job.get("company_name", "")
        email_sub = job.get("email_subject", "").lower()
        filter_reason = job.get("filter_reason", "").lower()
        loc_str = job.get("location", "").lower()

        combined_text = f"{title} {company} {email_sub} {filter_reason} {loc_str}".lower()

        # Check if explicitly non-Preferred Hybrid City onsite/hybrid
        is_remote = "remote" in combined_text or "work from home" in combined_text or "telecommute" in combined_text
        is_dfw = any(Preferred Hybrid City in combined_text for Preferred Hybrid City in DFW_CITIES)
        has_non_dfw_city = any(city in combined_text for city in NON_DFW_CITIES)

        if not is_remote and has_non_dfw_city and not is_dfw:
            print(f"[PURGED NON-Preferred Hybrid City ONSITE/HYBRID] {title} at {company} (Text: '{loc_str}')")
            purged_count += 1
            continue

        valid_queue.append(job)

    print(f"\nQueue Audit Complete:")
    print(f"  Initial Review Queue Roles: {initial_count}")
    print(f"  Purged Non-Preferred Hybrid City Onsite/Hybrid Roles: {purged_count}")
    print(f"  Remaining Verified Roles: {len(valid_queue)}")

    state["verified_gmail_jobs"] = valid_queue
    state["review_queue"] = valid_queue

    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)

    # Sync live dashboard
    try:
        from sync_dashboard_from_state import sync_dashboard
        sync_dashboard()
    except Exception as e:
        print(f"Warning syncing dashboard: {e}")

if __name__ == '__main__':
    clean_queue()
