"""
System Notification Engine.
Dispatches desktop notifications via plyer when new guardrail-passing roles are ingested.
Configurable via config.json under notifications.desktop_enabled.
"""

import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

_last_notification = None

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
    global _last_notification

    if count <= 0:
        return False

    enabled = is_desktop_notifications_enabled()
    _last_notification = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "count": count,
        "top_role": top_role,
        "dispatched": enabled
    }

    if not enabled:
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

def get_notification_status() -> dict:
    return {
        "desktop_enabled": is_desktop_notifications_enabled(),
        "last_notification": _last_notification
    }

def update_notification_settings(desktop_enabled: bool) -> bool:
    if not os.path.exists(CONFIG_FILE):
        return False
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        cfg.setdefault("notifications", {})["desktop_enabled"] = bool(desktop_enabled)
        tmp = CONFIG_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        os.replace(tmp, CONFIG_FILE)
        return True
    except Exception as e:
        print(f"Error updating notification settings: {e}")
        return False
