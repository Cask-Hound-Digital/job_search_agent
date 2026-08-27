import os
import re
import json
import urllib.request
from datetime import datetime
from config_loader import get_allowed_local_cities, get_min_salary_floor, get_excluded_titles

EXCLUDED_TITLES = get_excluded_titles()

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

ALLOWED_LOCAL_CITIES = get_allowed_local_cities()
MIN_SALARY_FLOOR = get_min_salary_floor()

NON_MATCHING_LOCATIONS = [
    "tampa", "florida", "fl", "miami", "orlando", "seattle", "wa", "boston", "ma",
    "chicago", "il", "atlanta", "ga", "los angeles", "san francisco", "san jose", "ca",
    "new york", "ny", "nc", "charlotte", "raleigh", "denver", "co", "phoenix", "az",
    "minneapolis", "mn", "detroit", "mi", "philadelphia", "pa", "london", "uk",
    "canada", "paris", "france", "india", "australia", "singapore", "germany", "berlin", "tokyo", "bethesda", "md",
    "austin", "houston", "san antonio"
]

def extract_salary_range(text_content):
    """
    Extracts max salary found in text (annualized USD).
    Returns (min_sal, max_sal, is_under_range)
    """
    if not text_content:
        return None, None, False

    found_max = 0
    found_min = 0

    # Pattern 1: $150,000 - $180,000
    m1 = re.findall(r'\$([0-9]{2,3}),?([0-9]{3})\s*(?:to|-|–)\s*\$([0-9]{2,3}),?([0-9]{3})', text_content, re.I)
    for match in m1:
        low = int(match[0] + match[1])
        high = int(match[2] + match[3])
        if high > found_max and high < 1000000:
            found_max = high
            found_min = low

    # Pattern 2: $150k - $180k
    m2 = re.findall(r'\$([0-9]{2,3})k\s*(?:to|-|–)\s*\$([0-9]{2,3})k', text_content, re.I)
    for match in m2:
        low = int(match[0]) * 1000
        high = int(match[1]) * 1000
        if high > found_max and high < 1000000:
            found_max = high
            found_min = low

    if found_max > 0:
        if found_max < MIN_SALARY_FLOOR:
            return found_min, found_max, True
        return found_min, found_max, False

    return None, None, False

def is_unwanted_workplace(combined_str, html_text=""):
    """
    Checks if job requires full Onsite work outside allowed local cities.
    """
    c_low = combined_str.lower()
    h_low = html_text.lower() if html_text else ""
    full_text = f"{c_low} {h_low}"

    is_remote = any(k in full_text for k in ["100% remote", "remote (us)", "remote - us", "work from home", "telecommute", "anywhere"])
    is_local = any(re.search(rf'\b{city}\b', full_text) for city in ALLOWED_LOCAL_CITIES)

    # If explicitly remote or local hybrid, allow
    if is_remote or is_local:
        return False

    is_onsite = any(k in full_text for k in ["onsite", "on-site", "in-office", "in office", "onsite required", "on-site required", "5 days in office"])
    is_non_matching_loc = any(re.search(rf'\b{kw}\b', full_text) for kw in NON_MATCHING_LOCATIONS)

    if is_onsite or is_non_matching_loc:
        return True

    return False

def audit_compensation_and_workplace():
    if not os.path.exists(STATE_FILE):
        return

    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)

    rq = state.get("review_queue", [])
    arch = state.get("archived_queue", [])

    clean_rq = []
    pruned_sal = 0
    pruned_workplace = 0
    pruned_ic = 0

    print(f"Starting Compensation (<${MIN_SALARY_FLOOR:,.0f}) & Workplace Audit of {len(rq)} Queue Items...")

    for idx, j in enumerate(rq):
        co = j.get("company_name", "")
        title = j.get("audited_role_title", j.get("title", ""))
        url = j.get("url", "")
        loc = j.get("location", "")

        max_amt = j.get("max_amount") or j.get("max_salary")
        combined = f"{co} | {title} | {loc} | {url}"

        # 1. Fast metadata check
        if max_amt and float(max_amt) < MIN_SALARY_FLOOR and float(max_amt) > 1000:
            j['archive_reason'] = f"Under Compensation Floor (Metadata Max: ${max_amt:,.0f})"
            j['archive_notes'] = f"Pruned low salary role (${max_amt:,.0f} < ${MIN_SALARY_FLOOR:,.0f})"
            arch.append(j)
            pruned_sal += 1
            continue

        # 2. Workplace check
        if is_unwanted_workplace(combined):
            j['archive_reason'] = f"Unwanted Workplace / Location ({loc})"
            j['archive_notes'] = f"Pruned unwanted workplace role ({co} - {title} - {loc})"
            arch.append(j)
            pruned_workplace += 1
            continue

        # 3. Excluded IC Developer Titles check (unless leadership title present)
        t_low = title.lower()
        if any(ex.lower() in t_low for ex in EXCLUDED_TITLES) and not any(k in t_low for k in ["director", "vp", "head of", "vice president", "principal"]):
            j['archive_reason'] = f"Excluded IC Developer Title ({title})"
            j['archive_notes'] = f"Pruned pure IC developer role ({co} - {title})"
            arch.append(j)
            pruned_ic += 1
            continue

        clean_rq.append(j)

    state["review_queue"] = clean_rq
    state["verified_gmail_jobs"] = clean_rq
    state["archived_queue"] = arch

    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)

    print(f"\n=========================================================")
    print(f"  Compensation & Workplace Audit Complete!")
    print(f"  Pruned Low Salary (<${MIN_SALARY_FLOOR:,.0f}) Roles: {pruned_sal}")
    print(f"  Pruned Unwanted Workplace Roles: {pruned_workplace}")
    print(f"  Remaining Clean Review Queue: {len(clean_rq)}")
    print(f"=========================================================")

if __name__ == '__main__':
    audit_compensation_and_workplace()
