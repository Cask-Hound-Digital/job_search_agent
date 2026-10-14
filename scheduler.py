"""
Autonomous Job Search Built-in Scheduler.
Periodically triggers run_unified_search_cycle() using APScheduler.
Configurable via config.json and dashboard API.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

_scheduler = None
_last_run = None

def get_interval_hours() -> float:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return float(cfg.get("scheduler", {}).get("interval_hours", 6))
        except Exception:
            pass
    return 6.0

def is_scheduler_enabled() -> bool:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return bool(cfg.get("scheduler", {}).get("enabled", True))
        except Exception:
            pass
    return True

def scheduled_job():
    global _last_run
    _last_run = datetime.now().isoformat()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Triggering scheduled unified search cycle...")
    try:
        from run_unified_search import run_unified_search_cycle
        run_unified_search_cycle()
    except Exception as e:
        print(f"Scheduled cycle error: {e}")

def init_scheduler(background=True):
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    scheduler_cls = BackgroundScheduler if background else BlockingScheduler
    _scheduler = scheduler_cls()
    interval = get_interval_hours()
    enabled = is_scheduler_enabled()

    if enabled:
        _scheduler.add_job(
            scheduled_job,
            "interval",
            hours=interval,
            id="unified_search_job",
            replace_existing=True
        )
    return _scheduler

def update_scheduler_interval(interval_hours: float, enabled: bool = True):
    global _scheduler
    interval_hours = max(0.0001, float(interval_hours))

    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            cfg = {}
        cfg.setdefault("scheduler", {})
        cfg["scheduler"]["interval_hours"] = interval_hours
        cfg["scheduler"]["enabled"] = enabled
        tmp = CONFIG_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        os.replace(tmp, CONFIG_PATH)

    if _scheduler is not None:
        if enabled:
            _scheduler.add_job(
                scheduled_job,
                "interval",
                hours=interval_hours,
                id="unified_search_job",
                replace_existing=True
            )
        else:
            try:
                _scheduler.remove_job("unified_search_job")
            except Exception:
                pass

def get_scheduler_status() -> dict:
    global _scheduler, _last_run
    interval = get_interval_hours()
    enabled = is_scheduler_enabled()
    next_run = None
    if _scheduler is not None and enabled:
        job = _scheduler.get_job("unified_search_job")
        if job and job.next_run_time:
            next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")

    last_run = _last_run
    if not last_run:
        state_path = os.path.join(BASE_DIR, "state.json")
        if os.path.exists(state_path):
            try:
                with open(state_path, "r", encoding="utf-8") as f:
                    last_run = json.load(f).get("last_search_cycle")
            except Exception:
                pass

    return {
        "enabled": enabled,
        "interval_hours": interval,
        "last_run": last_run,
        "next_run": next_run,
        "is_running": _scheduler is not None and _scheduler.running
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous Job Search Scheduler")
    parser.add_argument("--interval", type=float, default=None, help="Interval in hours (default 6h)")
    parser.add_argument("--daemon", action="store_true", help="Run in background daemon mode")
    args = parser.parse_args()

    if args.interval is not None:
        update_scheduler_interval(args.interval)

    sched = init_scheduler(background=args.daemon)
    print(f"Starting job search scheduler (interval: {get_interval_hours()}h)...")
    sched.start()
    if args.daemon:
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            sched.shutdown()
