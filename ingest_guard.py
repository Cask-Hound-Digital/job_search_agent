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
    m_builtin = re.search(r'builtin\.com/job/(?:.+/)?(\d+)', clean_u)
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
    if targets and t and t.lower() != "unknown":
        matched_target = any(tgt.lower() in t_lower for tgt in targets)
        if not matched_target:
            # Fallback leadership check
            has_leadership = any(term in t_lower for term in ["director", "vp", "vice president", "head", "lead", "principal", "chief"])
            if not has_leadership:
                return False, f"Role does not match target titles or leadership level: {t}"

    # 6. Salary Floor Check
    if salary and min_floor > 0:
        found_amounts = []
        for m in re.finditer(r'(?:\$|\b)(\d{1,3}(?:,\d{3})+|\d{2,3}k|\d{5,7})\b', str(salary), re.IGNORECASE):
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
    target_key = f"{co_norm}_{title_norm}" if co_norm and title_norm and co_norm != "unknown" and title_norm != "unknown" else ""

    # Check against review queue
    for q in state.get("review_queue", []):
        q_url = (q.get("job_url") or q.get("url") or "").split("?")[0].lower().rstrip("/")
        if clean_u and q_url == clean_u:
            return True, "Already in review queue (URL match)"
        if target_id and extract_job_identifier(q_url) == target_id:
            return True, "Already in review queue (Job ID match)"
        q_key = f"{normalize_text(q.get('company_name') or q.get('company'))}_{normalize_text(q.get('title'))}"
        if target_key and q_key == target_key:
            return True, "Already in review queue (Role & Company match)"

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

def score_role(title: str, company: str = "", salary: str = "", date_posted: str = "", description: str = "") -> int:
    """
    Computes a composite match score (0-100) based on:
      1. Title-to-target similarity (0-35 points)
      2. Seniority signal presence (0-25 points)
      3. Compensation vs. floor headroom (0-25 points)
      4. Recency (0-15 points)
    """
    cfg = load_config()
    candidate_cfg = cfg.get("candidate", {})
    matrix_cfg = cfg.get("search_matrix", {})

    target_titles = matrix_cfg.get("target_titles", [])
    if not target_titles:
        target_titles = [
            "Director of Product Management", "Director of Engineering",
            "VP of Engineering", "Head of Digital Strategy", "Chief of Staff"
        ]

    min_floor = candidate_cfg.get("min_salary_floor", 180000)
    baseline = candidate_cfg.get("target_salary_baseline", 200000)
    if baseline <= min_floor:
        baseline = min_floor + 20000

    t_str = str(title or "").strip()
    t_lower = t_str.lower()
    t_clean = normalize_text(t_str)

    # 1. Title-to-Target Similarity (0-35 points)
    stopwords = {"of", "the", "and", "in", "for", "to", "a", "an", "at", "by", "with"}
    t_tokens = set(w for w in t_clean.split() if w not in stopwords)

    best_title_score = 5
    for target in target_titles:
        tgt_clean = normalize_text(target)
        tgt_tokens = set(w for w in tgt_clean.split() if w not in stopwords)

        if not tgt_tokens:
            continue

        if t_clean == tgt_clean:
            similarity = 35
        elif tgt_clean in t_clean or t_clean in tgt_clean:
            similarity = 32
        elif tgt_tokens.issubset(t_tokens):
            similarity = 30
        else:
            intersection = len(t_tokens & tgt_tokens)
            union = len(t_tokens | tgt_tokens)
            jaccard = intersection / union if union else 0.0
            similarity = int(round(jaccard * 35))

        if similarity > best_title_score:
            best_title_score = similarity

    title_score = min(35, max(5, best_title_score)) if t_str and t_lower != "unknown" else 5

    # 2. Seniority Signal Presence (0-25 points)
    if any(k in t_lower for k in ["chief", "vp", "vice president", "head of", "head", "cxo", "c-level"]):
        seniority_score = 25
    elif any(k in t_lower for k in ["director", "senior director", "sr. director", "sr director", "group director"]):
        seniority_score = 22
    elif any(k in t_lower for k in ["principal", "staff", "architect"]):
        seniority_score = 18
    elif any(k in t_lower for k in ["lead", "lead strategist", "lead architect"]):
        seniority_score = 14
    elif any(k in t_lower for k in ["senior", "sr", "manager"]):
        seniority_score = 10
    else:
        seniority_score = 5

    # 3. Compensation vs Floor Headroom (0-25 points)
    comp_score = 15  # Neutral default when compensation is unstated
    if salary:
        found_amounts = []
        for m in re.finditer(r'(?:\$|\b)(\d{1,3}(?:,\d{3})+|\d{2,3}k|\d{5,7})\b', str(salary), re.IGNORECASE):
            raw = m.group(1).replace(',', '').lower()
            try:
                val = int(float(raw.replace('k', '')) * 1000) if 'k' in raw else int(float(raw))
                if 30000 <= val <= 2000000:
                    found_amounts.append(val)
            except (ValueError, TypeError):
                continue

        if found_amounts:
            max_comp = max(found_amounts)
            if max_comp >= baseline * 1.25:
                comp_score = 25
            elif max_comp >= baseline:
                fraction = (max_comp - baseline) / max(1, (baseline * 0.25))
                comp_score = 20 + int(round(fraction * 4))
            elif max_comp >= min_floor:
                fraction = (max_comp - min_floor) / max(1, (baseline - min_floor))
                comp_score = 15 + int(round(fraction * 4))
            else:
                comp_score = max(0, int(round(15 * (max_comp / max(1, min_floor)))))

    # 4. Recency (0-15 points)
    recency_score = 10  # Neutral default
    if date_posted:
        dp_str = str(date_posted).strip().lower()
        if any(w in dp_str for w in ["today", "just", "hour", "minute", "moment"]):
            recency_score = 15
        elif any(w in dp_str for w in ["yesterday", "1 day", "24 hour"]):
            recency_score = 14
        elif any(w in dp_str for w in ["2 day", "3 day"]):
            recency_score = 12
        elif any(w in dp_str for w in ["4 day", "5 day", "6 day", "7 day", "1 week"]):
            recency_score = 9
        elif any(w in dp_str for w in ["2 week", "10 day", "14 day"]):
            recency_score = 6
        elif any(w in dp_str for w in ["3 week", "4 week", "month", "30+"]):
            recency_score = 3
        else:
            m_date = re.search(r'(\d{4})-(\d{2})-(\d{2})', dp_str)
            if m_date:
                try:
                    posted_dt = datetime.strptime(m_date.group(0), "%Y-%m-%d").date()
                    days = (datetime.now().date() - posted_dt).days
                    if days <= 0:
                        recency_score = 15
                    elif days == 1:
                        recency_score = 14
                    elif days <= 3:
                        recency_score = 12
                    elif days <= 7:
                        recency_score = 9
                    elif days <= 14:
                        recency_score = 6
                    else:
                        recency_score = 3
                except Exception:
                    recency_score = 10

    total_score = title_score + seniority_score + comp_score + recency_score
    return max(0, min(100, int(round(total_score))))

