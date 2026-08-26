import json
import os
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "state.json")

def normalize_title(t):
    if not t:
        return ""
    t_clean = re.sub(r'&amp;', '&', t, flags=re.IGNORECASE)
    t_clean = re.sub(r'[^a-z0-9\s&]', '', t_clean.lower()).strip()
    return re.sub(r'\s+', ' ', t_clean)

def normalize_company(c):
    if not c:
        return ""
    c_clean = re.sub(r'&amp;', '&', c, flags=re.IGNORECASE)
    c_clean = re.split(r'\s+[—–|-]\s+', c_clean)[0].strip()
    c_clean = re.sub(r'[^a-z0-9\s&]', '', c_clean.lower()).strip()
    return re.sub(r'\s+', ' ', c_clean)

def deduplicate_review_queue():
    if not os.path.exists(STATE_FILE):
        print("ERROR: state.json not found.")
        return

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state_data = json.load(f)

    review_queue = state_data.get("review_queue", [])
    initial_count = len(review_queue)
    print(f"Starting deduplication across {initial_count} review queue items...")

    seen_signatures = set()
    seen_urls = set()
    deduped_queue = []
    removed_count = 0

    for item in review_queue:
        url = item.get("url", "").strip()
        url_clean = url.split("?")[0].lower().rstrip("/")
        
        # Check LinkedIn Job ID
        m_id = re.search(r'/view/(\d+)', url_clean)
        job_id = m_id.group(1) if m_id else url_clean

        title_norm = normalize_title(item.get("title", ""))
        co_norm = normalize_company(item.get("company_name", ""))

        # 1. URL / Job ID Deduplication
        if job_id and job_id in seen_urls:
            removed_count += 1
            continue

        # 2. Title + Company Deduplication (Only for valid company names)
        if co_norm and co_norm != "verified employer":
            sig = f"{title_norm}:::{co_norm}"
            if sig in seen_signatures:
                removed_count += 1
                continue
            seen_signatures.add(sig)

        if job_id:
            seen_urls.add(job_id)

        deduped_queue.append(item)

    state_data["review_queue"] = deduped_queue
    with open(STATE_FILE, "w", encoding="utf-8") as sf:
        json.dump(state_data, sf, indent=2)

    print(f"SUCCESS: Removed {removed_count} duplicate postings! Queue reduced from {initial_count} to {len(deduped_queue)} clean items.")

if __name__ == '__main__':
    deduplicate_review_queue()
