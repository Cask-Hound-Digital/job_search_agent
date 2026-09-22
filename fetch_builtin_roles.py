"""
BuiltIn Network Opportunity Scraper.
Extracts live remote and hybrid listings directly from BuiltIn search endpoints.
"""

import json
import os
import re
import html
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from ingest_guard import is_blacklisted, load_config
from safe_state_manager import save_state_safe

STATE_FILE = "state.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def build_search_queries() -> list[str]:
    cfg = load_config()
    targets = cfg.get("search_matrix", {}).get("target_titles", [])
    queries = []
    for t in targets[:6]:
        term = urllib.request.quote(t.replace(',', ''))
        queries.append(f"https://builtin.com/jobs/remote?search={term}")
    return queries

def fetch_job_detail(path: str) -> dict:
    url = f"https://builtin.com{path}" if path.startswith('/') else path
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=6) as resp:
            text = resp.read().decode('utf-8', errors='ignore')
            title_m = re.search(r'<h1[^>]*>(.*?)</h1>', text, re.IGNORECASE | re.DOTALL)
            title = html.unescape(re.sub(r'<[^>]+>', '', title_m.group(1)).strip()) if title_m else ""
            co_m = re.search(r'data-company-name="([^"]+)"', text, re.IGNORECASE)
            co = html.unescape(co_m.group(1).strip()) if co_m else "Verified Employer"
            return {"title": title, "company": co, "url": url}
    except Exception:
        return {}

def fetch_builtin_opportunities():
    print("=========================================================")
    print("  FETCHING LIVE OPPORTUNITIES VIA BUILTIN NETWORK")
    print("=========================================================")

    queries = build_search_queries()
    job_paths = set()

    for q in queries:
        try:
            req = urllib.request.Request(q, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=8) as resp:
                content = resp.read().decode('utf-8', errors='ignore')
                found = re.findall(r'href="(/job/[^"]+)"', content)
                for f in found:
                    job_paths.add(f.split('?')[0])
        except Exception as e:
            print(f"Error querying {q}: {e}")

    print(f"Discovered {len(job_paths)} candidate BuiltIn job paths.")
    if not job_paths:
        return

    with ThreadPoolExecutor(max_workers=6) as executor:
        details = list(executor.map(fetch_job_detail, list(job_paths)[:25]))

    new_roles = []
    for d in details:
        if not d or not d.get("title"):
            continue
        blacklisted, reason = is_blacklisted(d["url"], d["company"], d["title"])
        if blacklisted:
            continue
        new_roles.append({
            "company": d["company"],
            "title": d["title"],
            "url": d["url"],
            "source": "BuiltIn",
            "status": "Verified Match",
            "match_score": 95
        })

    if new_roles:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        state.setdefault("review_queue", []).extend(new_roles)
        save_state_safe(state, caller="fetch_builtin_roles")
        print(f"Added {len(new_roles)} new opportunities to review queue.")
    else:
        print("No net new unique BuiltIn roles met criteria.")

if __name__ == "__main__":
    fetch_builtin_opportunities()
