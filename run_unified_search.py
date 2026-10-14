"""
Unified Multi-Board Search Runner.
Executes all scrapers, runs 404 URL pruning, and updates state cycle metadata.
"""

import os
import sys
import json
from datetime import datetime
from safe_state_manager import save_state_safe

def run_unified_search_cycle():
    print("================================================================================")
    print("  EXECUTING UNIFIED MULTI-BOARD JOB SEARCH CYCLE")
    print("================================================================================")

    state_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")
    initial_urls = set()
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                s = json.load(f)
                initial_urls = set((item.get("url") or item.get("job_url") or "") for item in s.get("review_queue", []))
        except Exception:
            pass

    cfg_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    sources = {}
    if os.path.exists(cfg_file):
        try:
            with open(cfg_file, "r", encoding="utf-8") as f:
                sources = json.load(f).get("sources", {})
        except Exception:
            pass

    def is_source_enabled(src: str) -> bool:
        return bool(sources.get(src, True))

    # 1. BuiltIn Scraper
    if is_source_enabled("builtin"):
        try:
            import fetch_builtin_roles
            fetch_builtin_roles.fetch_builtin_opportunities()
        except Exception as e:
            print(f"BuiltIn error: {e}")
    else:
        print("[Search] BuiltIn source disabled in config. Skipping.")

    # 2. JobSpy (LinkedIn & Indeed)
    if is_source_enabled("jobspy"):
        try:
            import fetch_jobspy_roles
            fetch_jobspy_roles.run_jobspy_scraper()
        except Exception as e:
            print(f"JobSpy error: {e}")
    else:
        print("[Search] JobSpy source disabled in config. Skipping.")

    # 3. JobsPipe ATS API
    if is_source_enabled("jobspipe"):
        try:
            import fetch_jobspipe_roles
            fetch_jobspipe_roles.fetch_jobspipe_opportunities()
        except Exception as e:
            print(f"JobsPipe error: {e}")
    else:
        print("[Search] JobsPipe source disabled in config. Skipping.")

    # 4. Gmail Alerts (OAuth2)
    if is_source_enabled("gmail"):
        try:
            import fetch_gmail_alerts
            fetch_gmail_alerts.fetch_gmail_alerts()
        except Exception as e:
            print(f"Gmail error: {e}")
    else:
        print("[Search] Gmail source disabled in config. Skipping.")

    # 5. 404 Dead URL Pruning & Verification Pass
    try:
        import audit_and_purge_404_urls
        audit_and_purge_404_urls.purge_404_and_history_duplicates()
        audit_and_purge_404_urls.verify_active_postings()
    except Exception as e:
        print(f"URL Audit/Verification error: {e}")

    # 6. Desktop Notification Dispatch & Last Cycle Timestamp
    try:
        if os.path.exists(state_file):
            with open(state_file, "r", encoding="utf-8") as f:
                s = json.load(f)
            final_queue = s.get("review_queue", [])
            new_items = [item for item in final_queue if (item.get("url") or item.get("job_url") or "") not in initial_urls]
            s["last_search_cycle"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_state_safe(s, caller="run_unified_search_cycle")

            if new_items:
                from notifications import notify_new_roles
                top_match = f"{new_items[0].get('title')} at {new_items[0].get('company')}"
                notify_new_roles(len(new_items), top_role=top_match)
    except Exception as e:
        print(f"Notification error: {e}")

    print("================================================================================")
    print("  UNIFIED MULTI-BOARD SEARCH COMPLETED")
    print("================================================================================")

if __name__ == "__main__":
    run_unified_search_cycle()
