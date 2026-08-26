import os
import sys
import json
import urllib.request
import urllib.parse

def _load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")

_load_env()

def send_telegram_alert(company, title, url, location="100% Remote / Preferred Hybrid City Hybrid", posted_time="Just now"):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

    if not bot_token or not chat_id:
        print("[NOTIFY CONFIG] Telegram BOT_TOKEN or CHAT_ID not set in .env")
        return False

    message = (
        f"🔥 <b>FRESH JOB ALERT (&lt;24H)</b>\n\n"
        f"🏢 <b>Company:</b> {company}\n"
        f"💼 <b>Role:</b> {title}\n"
        f"📍 <b>Location:</b> {location}\n"
        f"⏰ <b>Posted:</b> {posted_time}\n\n"
        f"🔗 <a href='{url}'>View Posting on Job Board</a>\n"
        f"⚡ Open Dashboard on your PC to 1-Click Apply!"
    )

    tg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    try:
        req = urllib.request.Request(
            tg_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"[NOTIFY SUCCESS] Telegram alert sent for {company} — {title}")
            return True
    except Exception as e:
        print(f"[NOTIFY ERROR] Telegram send failed: {e}")
        return False

def notify_fresh_jobs(jobs_list):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not bot_token:
        return 0

    sent_count = 0
    for job in jobs_list:
        p_raw = str(job.get("date_posted_raw", job.get("date_posted", ""))).lower()
        if any(k in p_raw for k in ["minute", "hour", "just now", "early applicant", "today", "1h", "2h", "3h", "4h", "5h"]):
            co = job.get("company_name", job.get("company", "Employer"))
            title = job.get("audited_role_title", job.get("title", "Role"))
            url = job.get("url", "#")
            loc = job.get("location", "Remote / Preferred Hybrid City Hybrid")
            
            if send_telegram_alert(co, title, url, loc, p_raw):
                sent_count += 1

    return sent_count

if __name__ == '__main__':
    # Test notification helper
    test_co = "GitLab"
    test_title = "AI Transformation Owner, Product & Design"
    test_url = "https://job-boards.greenhouse.io/gitlab/jobs/8716179002"
    send_telegram_alert(test_co, test_title, test_url, "100% Remote (US)", "23 minutes ago")
