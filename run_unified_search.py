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

    # 1. BuiltIn Scraper
    try:
        import fetch_builtin_roles
        fetch_builtin_roles.fetch_builtin_opportunities()
    except Exception as e:
        print(f"BuiltIn error: {e}")

    # 2. JobSpy (LinkedIn & Indeed)
    try:
        import fetch_jobspy_roles
        fetch_jobspy_roles.run_jobspy_scraper()
    except Exception as e:
        print(f"JobSpy error: {e}")

    # 3. JobsPipe ATS API
    try:
        import fetch_jobspipe_roles
        fetch_jobspipe_roles.fetch_jobspipe_opportunities()
    except Exception as e:
        print(f"JobsPipe error: {e}")

    # 4. Gmail IMAP Alerts
    try:
        import fetch_gmail_alerts
        fetch_gmail_alerts.fetch_gmail_alerts()
    except Exception as e:
        print(f"Gmail error: {e}")

    # 5. 404 Dead URL Pruning
    try:
        import audit_and_purge_404_urls
        audit_and_purge_404_urls.purge_404_and_history_duplicates()
    except Exception as e:
        print(f"URL Audit error: {e}")

    print("================================================================================")
    print("  UNIFIED MULTI-BOARD SEARCH COMPLETED")
    print("================================================================================")

if __name__ == "__main__":
    run_unified_search_cycle()
