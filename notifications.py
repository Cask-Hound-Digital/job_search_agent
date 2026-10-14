"""
System Notification Engine.
Dispatches desktop notifications via plyer when new guardrail-passing roles are ingested.
Configurable via config.json under notifications.desktop_enabled.
"""

import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

def is_desktop_notifications_enabled() -> bool:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return bool(cfg.get("notifications", {}).get("desktop_enabled", True))
        except Exception:
            pass
    return True

def notify_new_roles(count: int, top_role: str = "") -> bool:
    """
    Sends a system desktop notification naming the count of newly ingested roles.
    Returns True if notification was triggered, False otherwise.
    """
    if count <= 0:
        return False

    if not is_desktop_notifications_enabled():
        print(f"[Notifications] Desktop notifications disabled in config. Skipping alert for {count} roles.")
        return False

    title = "Autonomous Job Search Agent"
    message = f"Found {count} new vetted opportunity!" if count == 1 else f"Found {count} new vetted opportunities ready for review!"
    if top_role:
        message += f"\nTop match: {top_role}"

    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name="JobSearchAgent",
            timeout=8
        )
        print(f"[Notifications] Sent desktop notification for {count} new roles.")
        return True
    except Exception as e:
        print(f"[Notifications] Desktop notification warning: {e}")
        return False
