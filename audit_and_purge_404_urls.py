"""
404 URL Audit Engine.
Multi-threaded link validator to purge dead or expired job postings from the queue.
"""

import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from safe_state_manager import save_state_safe

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "state.json")

def check_url_status(url: str) -> tuple[int, str]:
    if not url or url == "#":
        return 404, "Invalid URL"
    try:
        proc = subprocess.run(
            ['curl', '-s', '-o', os.devnull, '-w', '%{http_code}', '-L', '-A',
             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', url],
            capture_output=True,
            timeout=5
        )
        if proc.returncode != 0:
            return -1, f"Probe Failed (curl exit code {proc.returncode})"
        code_str = proc.stdout.decode('utf-8', errors='ignore').strip()
        if code_str.isdigit():
            code = int(code_str)
            if code == 0:
                return -1, "Uncertain (HTTP 000)"
            return code, "OK" if code < 400 else f"HTTP {code}"
        return -1, f"Uncertain ({code_str})"
    except Exception as e:
        return -1, f"Uncertain ({e})"

def purge_404_and_history_duplicates():
    if not os.path.exists(STATE_FILE):
        return

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)

    queue = state.get("review_queue", [])
    archived = state.get("archived_queue", [])
    if not queue:
        return

    print(f"Auditing {len(queue)} review queue URLs for live HTTP status...")
    clean_queue = []
    purged_count = 0
    uncertain_count = 0

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(lambda item: (item, check_url_status(item.get("url", ""))), queue))

    for item, (code, reason) in results:
        if code in [404, 410, 400]:
            item["status"] = "Archived"
            item["archive_reason"] = f"Broken Link / HTTP {code}"
            archived.append(item)
            purged_count += 1
            print(f"  [PURGED 404] {item.get('company')} - {item.get('title')} ({reason})")
        elif code == -1:
            item["link_check"] = "uncertain"
            clean_queue.append(item)
            uncertain_count += 1
            print(f"  [UNCERTAIN] {item.get('company')} - {item.get('title')} ({reason})")
        else:
            item.pop("link_check", None)
            clean_queue.append(item)

    if purged_count > 0 or uncertain_count > 0:
        state["review_queue"] = clean_queue
        state["archived_queue"] = archived
        save_state_safe(state, caller="audit_and_purge_404_urls")
        print(f"Audit complete: {purged_count} dead links purged, {uncertain_count} flagged uncertain. {len(clean_queue)} active opportunities remain.")
    else:
        print(f"Audit complete: All {len(clean_queue)} URLs are live.")

STALE_JOB_PHRASES = [
    "job has expired", "job is no longer available", "position has been filled",
    "no longer accepting applications", "job is closed", "this posting has expired",
    "this job is no longer open", "listing has expired", "this role has been filled",
    "posting has ended", "job opening has been closed", "no longer active",
    "the page you are looking for no longer exists", "requisition closed",
    "job expired", "closed job", "posting is expired", "job not found"
]

def verify_posting(url: str) -> tuple[str, str]:
    """
    Fetches the posting URL and checks for active job status vs. stale/filled signals.
    Returns:
      ("verified", "Active Listing") or ("unconfirmed", reason)
    """
    if not url or url.startswith("#"):
        return "unconfirmed", "Invalid URL"

    try:
        import urllib.request
        import urllib.error
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            status_code = resp.getcode()
            if status_code >= 400:
                return "unconfirmed", f"HTTP {status_code}"

            html_content = resp.read().decode("utf-8", errors="ignore").lower()

            for phrase in STALE_JOB_PHRASES:
                if phrase in html_content:
                    return "unconfirmed", f"Detected stale signal: '{phrase}'"

            return "verified", "Active Listing"
    except Exception as e:
        return "unconfirmed", f"Verification probe failed: {e}"

def verify_active_postings(state: dict = None) -> dict:
    """
    Runs company-site verification pass across the review queue.
    Marks unverifiable roles as 'unconfirmed' and sorts them below verified ones.
    """
    save_needed = False
    if state is None:
        if not os.path.exists(STATE_FILE):
            return {}
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        save_needed = True

    queue = state.get("review_queue", [])
    if not queue:
        return state

    print(f"Running verification pass on {len(queue)} queued opportunities...")
    with ThreadPoolExecutor(max_workers=6) as executor:
        verification_results = list(executor.map(lambda item: verify_posting(item.get("url", "")), queue))

    for item, (v_status, note) in zip(queue, verification_results):
        item["verification"] = v_status
        item["verification_note"] = note

    queue.sort(key=lambda x: (
        0 if x.get("verification") == "verified" else 1,
        -x.get("match_score", 0)
    ))
    state["review_queue"] = queue

    if save_needed:
        save_state_safe(state, caller="audit_and_purge_404_urls:verify_active_postings")

    verified_count = sum(1 for q in queue if q.get("verification") == "verified")
    print(f"Verification pass complete: {verified_count}/{len(queue)} verified active.")
    return state

if __name__ == "__main__":
    purge_404_and_history_duplicates()
    verify_active_postings()

