import os
import re
import json
import urllib.request
import urllib.parse
from datetime import datetime
from audit_and_clean_builtin_dice import parse_detail_page, is_valid_location_strict, TARGET_TITLE_KEYWORDS, EXCLUDED_TITLES

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")

def fetch_builtin_roles():
    print("\n[Built In Scraper] Scraping Built In (builtin.com) for target roles...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    scraped_jobs = []
    categories = [
        "https://builtin.com/jobs/remote",
        "https://builtin.com/jobs/dallas-fort-worth",
        "https://builtin.com/jobs/tech/ai-machine-learning"
    ]

    for cat_url in categories:
        try:
            req = urllib.request.Request(cat_url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                html = resp.read().decode("utf-8")
                
                links = set(re.findall(r'href="(/job/[^"]+)"', html))
                for link in list(links)[:15]:
                    full_url = f"https://builtin.com{link}"
                    
                    parsed = parse_detail_page(full_url, "Built In (builtin.com)")
                    if not parsed:
                        continue

                    real_title = parsed["title"]
                    real_co = parsed["company"]
                    real_loc = parsed["location"]
                    real_date = parsed["date_posted"]

                    t_low = real_title.lower()
                    if not any(kw in t_low for kw in TARGET_TITLE_KEYWORDS) or any(ex in t_low for ex in EXCLUDED_TITLES):
                        continue

                    combined_str = f"{real_co} | {real_title} | {real_loc} | {parsed['page_title']}"
                    if not is_valid_location_strict(combined_str):
                        continue

                    scraped_jobs.append({
                        "title": real_title,
                        "company_name": real_co,
                        "url": full_url,
                        "source": "Built In (builtin.com)",
                        "status": "Verified Match",
                        "date_added": datetime.now().strftime("%Y-%m-%d"),
                        "time_scraped": datetime.now().isoformat(),
                        "audited_role_title": real_title,
                        "location": real_loc,
                        "date_posted_raw": real_date
                    })
        except Exception as e:
            print(f"  [Built In Error] Failed fetching {cat_url}: {e}")

    print(f"  [Built In Result] Verified & Extracted {len(scraped_jobs)} ground-truth listings.")
    return scraped_jobs

def fetch_dice_roles():
    print("\n[Dice Scraper] Scraping Dice (dice.com) for target roles...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    scraped_jobs = []
    queries = [
        "AI Transformation",
        "Director Digital Experience",
        "Director Web Strategy",
        "VP Digital Product"
    ]

    for q in queries:
        url = f"https://www.dice.com/jobs?q={urllib.parse.quote(q)}&countryCode=US"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                html = resp.read().decode("utf-8")
                
                links = set(re.findall(r'href="(/job-detail/[^"]+)"', html))
                for link in list(links)[:15]:
                    full_url = f"https://www.dice.com{link.split('?')[0]}"
                    
                    parsed = parse_detail_page(full_url, "Dice (dice.com)")
                    if not parsed:
                        continue

                    real_title = parsed["title"]
                    real_co = parsed["company"]
                    real_loc = parsed["location"]
                    real_date = parsed["date_posted"]

                    t_low = real_title.lower()
                    if not any(kw in t_low for kw in TARGET_TITLE_KEYWORDS) or any(ex in t_low for ex in EXCLUDED_TITLES):
                        continue

                    combined_str = f"{real_co} | {real_title} | {real_loc} | {parsed['page_title']}"
                    if not is_valid_location_strict(combined_str):
                        continue

                    scraped_jobs.append({
                        "title": real_title,
                        "company_name": real_co,
                        "url": full_url,
                        "source": "Dice (dice.com)",
                        "status": "Verified Match",
                        "date_added": datetime.now().strftime("%Y-%m-%d"),
                        "time_scraped": datetime.now().isoformat(),
                        "audited_role_title": real_title,
                        "location": real_loc,
                        "date_posted_raw": real_date
                    })
        except Exception as e:
            print(f"  [Dice Error] Failed fetching {q}: {e}")

    print(f"  [Dice Result] Verified & Extracted {len(scraped_jobs)} ground-truth listings.")
    return scraped_jobs

def run_builtin_and_dice_scraper():
    b_jobs = fetch_builtin_roles()
    d_jobs = fetch_dice_roles()
    all_jobs = b_jobs + d_jobs

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)

        existing_queue = state.get("review_queue", [])
        existing_urls = {j.get("url", "").split('?')[0].lower() for j in existing_queue if j.get("url")}
        arch_urls = {j.get("url", "").split('?')[0].lower() for j in state.get("archived_queue", []) if j.get("url")}
        app_urls = {a.get("job_url", "").split('?')[0].lower() for a in state.get("applications", []) if a.get("job_url")}

        new_unique = []
        for j in all_jobs:
            u_clean = j["url"].split('?')[0].lower()
            if u_clean not in existing_urls and u_clean not in arch_urls and u_clean not in app_urls:
                existing_urls.add(u_clean)
                new_unique.append(j)

        print(f"\n=========================================================")
        print(f"  Verified Ground-Truth Built In & Dice Roles Added: {len(new_unique)}")
        print(f"=========================================================")

        if new_unique:
            state.setdefault("verified_gmail_jobs", []).extend(new_unique)
            state.setdefault("review_queue", []).extend(new_unique)
            state["last_updated"] = datetime.now().strftime("%Y-%m-%d")

            with open(STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)

            print("  Successfully updated state.json with Built In & Dice roles.")

            try:
                from sync_dashboard_from_state import sync_dashboard
                sync_dashboard()
            except Exception as sync_err:
                print(f"  Warning syncing dashboard: {sync_err}")

if __name__ == '__main__':
    run_builtin_and_dice_scraper()
