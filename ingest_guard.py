"""
Universal Ingestion Guard.
Filters incoming job opportunities against target titles, excluded titles,
location preferences, compensation floors, and past application history.
"""

import os
import re
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
STATE_FILE = os.path.join(BASE_DIR, "state.json")

COMMON_SPAM_AGENCIES = [
    'bairesdev', 'cybercoders', 'robert half', 'teksystems', 'aerotek',
    'apex systems', 'randstad', 'adecco', 'kelly services', 'beacon hill',
    'toptal', 'turing', 'crossover', 'jobot', 'dice', 'motion recruitment',
    'kforce', 'insight global', 'judge group', 'modis'
]

INTERNATIONAL_KEYWORDS = [
    'emea', 'apac', 'latam', 'europe', 'asia', 'uk', 'united kingdom',
    'germany', 'france', 'spain', 'italy', 'netherlands', 'poland',
    'india', 'bangalore', 'mumbai', 'singapore', 'australia', 'canada',
    'brazil', 'latin america', 'mexico'
]

def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config.json: {e}")
    return {}

def normalize_text(text: str) -> str:
    if not text:
        return ""
    clean = re.sub(r'[^a-zA-Z0-9]', ' ', str(text)).lower()
    return re.sub(r'\s+', ' ', clean).strip()

def extract_job_identifier(url: str) -> str:
    if not url:
        return ""
    clean_u = url.split("?")[0].rstrip("/")
    m_li = re.search(r'linkedin\.com/jobs/view/(\d+)', clean_u)
    if m_li:
        return f"li_{m_li.group(1)}"
    m_builtin = re.search(r'builtin\.com/job/[^/]+/(\d+)', clean_u)
    if m_builtin:
        return f"builtin_{m_builtin.group(1)}"
    return clean_u.lower()

def is_domain_aligned(title: str, company: str = "", location: str = "", salary: str = "", description: str = "") -> tuple[bool, str]:
    cfg = load_config()
    targets = cfg.get("search_matrix", {}).get("target_titles", [])
    excluded = cfg.get("search_matrix", {}).get("excluded_titles", [])
    candidate_cfg = cfg.get("candidate", {})
    min_floor = candidate_cfg.get("min_salary_floor", 0)
    allowed_cities = [c.lower().strip() for c in candidate_cfg.get("allowed_local_cities", [])]
    workplace_prefs = [p.lower() for p in candidate_cfg.get("workplace_preferences", ["remote", "hybrid"])]

    t = str(title or "").strip()
    co = str(company or "").strip()
    loc = str(location or "").strip().lower()
    full_text = f"{co} {t} {loc}".lower()

    # 1. Spam Agencies
    if any(sp in co.lower() for sp in COMMON_SPAM_AGENCIES):
        return False, f"Recruitment Agency / Staffing Firm: {co}"

    # 2. International Filter
    if any(ik in full_text for ik in INTERNATIONAL_KEYWORDS):
        return False, f"International Location Outside Preference: {loc or t}"

    # 3. Excluded Titles
    t_lower = t.lower()
    for ex in excluded:
        if ex and ex.lower() in t_lower:
            return False, f"Excluded Title Match ({ex}): {t}"

    # 4. Location Check
    is_remote = any(r in loc for r in ["remote", "work from home", "telecommute"])
    is_hybrid = "hybrid" in loc
    is_onsite = any(o in loc for o in ["onsite", "on-site", "in-office"])

    if is_remote:
        if "remote" not in workplace_prefs:
            return False, f"Remote role outside preference: {loc}"
    elif is_hybrid or is_onsite:
        matched_city = any(city in loc for city in allowed_cities)
        if not matched_city:
            return False, f"Onsite/Hybrid location outside target metro: {location}"

    # 5. Target Seniority / Title Alignment
    if targets:
        matched_target = any(tgt.lower() in t_lower for tgt in targets)
        if not matched_target:
            # Fallback leadership check
            has_leadership = any(term in t_lower for term in ["director", "vp", "vice president", "head", "lead", "principal", "chief"])
            if not has_leadership:
                return False, f"Role does not match target titles or leadership level: {t}"

    # 6. Salary Floor Check
    if salary and min_floor > 0:
        found_amounts = []
        for m in re.finditer(r'\$(\d{1,3}(?:,\d{3})+|\d+k?|\d{5,7})', str(salary), re.IGNORECASE):
            raw = m.group(1).replace(',', '').lower()
            try:
                val = int(float(raw.replace('k', '')) * 1000) if 'k' in raw else int(float(raw))
                if 30000 <= val <= 2000000:
                    found_amounts.append(val)
            except (ValueError, TypeError):
                continue
        if found_amounts:
            max_stated = max(found_amounts)
            if max_stated < min_floor:
                return False, f"Compensation below configured floor (${min_floor:,}): {salary}"

    return True, "Aligned"

def is_blacklisted(url: str, company: str = "", title: str = "", location: str = "", salary: str = "", description: str = "") -> tuple[bool, str]:
    aligned, reason = is_domain_aligned(title, company, location, salary, description)
    if not aligned:
        return True, reason

    if not os.path.exists(STATE_FILE):
        return False, "New Opportunity"

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        return False, "New Opportunity"

    clean_u = url.split("?")[0].lower().rstrip("/") if url else ""
    target_id = extract_job_identifier(url)
    co_norm = normalize_text(company)
    title_norm = normalize_text(title)
    target_key = f"{co_norm}_{title_norm}" if co_norm and title_norm else ""

    # Check against active applications
    for a in state.get("applications", []):
        app_url = (a.get("job_url") or a.get("url") or "").split("?")[0].lower().rstrip("/")
        if clean_u and app_url == clean_u:
            return True, "Already applied (URL match)"
        if target_id and extract_job_identifier(app_url) == target_id:
            return True, "Already applied (Job ID match)"
        app_key = f"{normalize_text(a.get('company_name') or a.get('company'))}_{normalize_text(a.get('title'))}"
        if target_key and app_key == target_key:
            return True, "Already applied (Role & Company match)"

    # Check against archived items
    for arch in state.get("archived_queue", []):
        arch_url = (arch.get("job_url") or arch.get("url") or "").split("?")[0].lower().rstrip("/")
        if clean_u and arch_url == clean_u:
            return True, "Already archived (URL match)"
        if target_id and extract_job_identifier(arch_url) == target_id:
            return True, "Already archived (Job ID match)"
        arch_key = f"{normalize_text(arch.get('company_name') or arch.get('company'))}_{normalize_text(arch.get('title'))}"
        if target_key and arch_key == target_key:
            return True, "Already archived (Role & Company match)"

    return False, "Verified New Opportunity"
