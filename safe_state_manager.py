"""
Safe State Manager for Job Search Pipeline.
Provides atomic JSON updates with automatic rotating backups.
"""

import os
import re
import json
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "state.json")
BACKUP_DIR = os.path.join(BASE_DIR, "state_backups")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

def _normalize_name(name: str) -> str:
    if not name:
        return ""
    clean = re.sub(r'\(.*?\)', '', str(name)).lower()
    clean = re.sub(r'[^\w\s]', '', clean)
    return " ".join(clean.split())

def get_next_job_id(apps: list) -> str:
    max_id = 0
    for a in apps:
        val = str(a.get("id", ""))
        m = re.search(r'JOB-(\d+)', val, re.IGNORECASE)
        if m:
            max_id = max(max_id, int(m.group(1)))
    return f"JOB-{max_id + 1:02d}"

def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        example_file = os.path.join(BASE_DIR, "state.example.json")
        if os.path.exists(example_file):
            shutil.copy(example_file, STATE_FILE)
        else:
            return {"applications": [], "review_queue": [], "archived_queue": []}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state_safe(state_data: dict, caller: str = "unknown") -> bool:
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Create timestamped backup if existing file exists
    if os.path.exists(STATE_FILE):
        bak_dest = os.path.join(BACKUP_DIR, f"state_{timestamp}.json")
        try:
            shutil.copy(STATE_FILE, bak_dest)
            shutil.copy(STATE_FILE, STATE_FILE + ".bak")
        except Exception as e:
            print(f"Warning: Failed to create state backup: {e}")

    # 2. Prune old backups, keeping newest 30
    try:
        backups = sorted([
            os.path.join(BACKUP_DIR, f)
            for f in os.listdir(BACKUP_DIR)
            if f.startswith("state_") and f.endswith(".json")
        ], key=os.path.getmtime)
        while len(backups) > 30:
            oldest = backups.pop(0)
            os.remove(oldest)
    except Exception as e:
        print(f"Warning: Error pruning backups: {e}")

    # 3. Update timestamp
    state_data["last_updated"] = datetime.now().astimezone().isoformat()

    # 4. Atomic write using temporary file
    temp_file = STATE_FILE + ".tmp"
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_file, STATE_FILE)
        return True
    except Exception as e:
        print(f"CRITICAL: Atomic state save failed for {caller}: {e}")
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass
        return False
