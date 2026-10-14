"""
Interactive Configuration CLI Wizard and Get/Set Tool for Autonomous Job Search Agent.
Allows complete setup and parameter modification without opening a web browser.
"""

import sys
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load existing config ({e}). Using defaults.")
    return {}

def save_config(cfg: dict) -> bool:
    try:
        tmp_file = CONFIG_FILE + ".tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        os.replace(tmp_file, CONFIG_FILE)
        return True
    except Exception as e:
        print(f"Error saving config.json: {e}")
        return False

def get_nested(data: dict, key_path: str):
    parts = key_path.split(".")
    curr = data
    for part in parts:
        if isinstance(curr, dict) and part in curr:
            curr = curr[part]
        else:
            raise KeyError(f"Key '{key_path}' not found at segment '{part}'")
    return curr

def set_nested(data: dict, key_path: str, value):
    parts = key_path.split(".")
    curr = data
    for part in parts[:-1]:
        if part not in curr or not isinstance(curr[part], dict):
            curr[part] = {}
        curr = curr[part]
    curr[parts[-1]] = value

def validate_and_cast(key_path: str, raw_value: str, existing_cfg: dict):
    norm_key = key_path.lower()

    # Boolean keys
    if norm_key in [
        "scheduler.enabled",
        "notifications.desktop_enabled",
        "notifications.telegram_enabled",
        "notifications.alert_on_raw_ingest",
        "notifications.alert_only_vetted",
        "sources.builtin",
        "sources.jobspy",
        "sources.jobspipe",
        "sources.gmail"
    ] or norm_key.startswith("sources."):
        val_str = raw_value.strip().lower()
        if val_str in ["true", "1", "yes", "y", "on"]:
            return True
        elif val_str in ["false", "0", "no", "n", "off"]:
            return False
        else:
            raise ValueError(f"Invalid boolean for '{key_path}': expected true/false/yes/no, got '{raw_value}'")

    # Numeric integers (salaries)
    if "salary" in norm_key or "floor" in norm_key or "baseline" in norm_key:
        try:
            cleaned = raw_value.replace("$", "").replace(",", "").strip()
            num = int(cleaned)
            if num < 0:
                raise ValueError(f"Value for '{key_path}' must be non-negative.")
            return num
        except ValueError:
            raise ValueError(f"Invalid integer for '{key_path}': got '{raw_value}'")

    # Numeric float (interval hours)
    if "interval" in norm_key:
        try:
            flt = float(raw_value.replace("h", "").strip())
            if flt <= 0:
                raise ValueError(f"Interval for '{key_path}' must be greater than 0.")
            return flt
        except ValueError:
            raise ValueError(f"Invalid number for '{key_path}': got '{raw_value}'")

    # Email
    if "email" in norm_key:
        val = raw_value.strip()
        if "@" not in val or "." not in val:
            raise ValueError(f"Invalid email address: '{raw_value}'")
        return val

    # Target titles / excluded titles / cities / workplace (list fields)
    if norm_key in [
        "search_matrix.target_titles",
        "search_matrix.excluded_titles",
        "candidate.allowed_local_cities",
        "candidate.workplace_preferences"
    ]:
        if isinstance(raw_value, list):
            items = raw_value
        elif raw_value.startswith("[") and raw_value.endswith("]"):
            try:
                items = json.loads(raw_value)
            except Exception:
                items = [s.strip() for s in raw_value[1:-1].split(",") if s.strip()]
        else:
            items = [s.strip() for s in raw_value.split(",") if s.strip()]

        if norm_key == "search_matrix.target_titles" and len(items) == 0:
            raise ValueError("Target titles cannot be empty.")
        if norm_key == "candidate.allowed_local_cities":
            return [c.lower() for c in items]
        return items

    return raw_value.strip()

def run_interactive_wizard():
    print("=" * 65)
    print("     Autonomous Job Search Agent - Interactive Setup Wizard")
    print("=" * 65)
    print("Press Enter to accept existing/default values shown in [brackets].\n")

    cfg = load_config()
    cand = cfg.setdefault("candidate", {})
    sm = cfg.setdefault("search_matrix", {})
    sched = cfg.setdefault("scheduler", {})
    notif = cfg.setdefault("notifications", {})
    sources = cfg.setdefault("sources", {
        "builtin": True, "jobspy": True, "jobspipe": True, "gmail": True
    })

    # Helper prompt
    def ask(prompt: str, current_val="", validator=None):
        placeholder = f" [{current_val}]" if current_val else ""
        while True:
            try:
                raw = input(f"{prompt}{placeholder}: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nSetup cancelled.")
                sys.exit(0)
            val = raw if raw else current_val
            if not validator:
                if val:
                    return val
                print("This field is required. Please enter a value.")
                continue
            try:
                validated = validator(val)
                return validated
            except Exception as err:
                print(f"  Error: {err}")

    # 1. Candidate details
    print("--- 1. Candidate Profile ---")
    cand_name = cand.get("full_name", "")
    if "{{" in cand_name:
        cand_name = ""
    cand["full_name"] = ask("Full Name", cand_name)

    cand_email = cand.get("email", "")
    if "{{" in cand_email:
        cand_email = ""
    cand["email"] = ask("Email Address", cand_email, lambda v: validate_and_cast("candidate.email", v, cfg))

    cand_phone = cand.get("phone", "")
    if "{{" in cand_phone:
        cand_phone = ""
    cand["phone"] = ask("Phone Number", cand_phone)

    cand_loc = cand.get("primary_location", "Dallas, TX")
    cand["primary_location"] = ask("Primary Location", cand_loc)

    floor = str(cand.get("min_salary_floor", 180000))
    cand["min_salary_floor"] = ask("Minimum Salary Floor ($ USD)", floor, lambda v: validate_and_cast("candidate.min_salary_floor", v, cfg))

    baseline = str(cand.get("target_salary_baseline", int(cand["min_salary_floor"]) + 20000))
    cand["target_salary_baseline"] = ask("Target Salary Baseline ($ USD)", baseline, lambda v: validate_and_cast("candidate.target_salary_baseline", v, cfg))

    # 2. Preferences
    print("\n--- 2. Workplace Alignment ---")
    current_wp = ", ".join(cand.get("workplace_preferences", ["Remote", "Hybrid"]))
    cand["workplace_preferences"] = ask("Workplace Preferences (comma-separated, e.g. Remote, Hybrid)", current_wp, lambda v: validate_and_cast("candidate.workplace_preferences", v, cfg))

    current_cities = ", ".join(cand.get("allowed_local_cities", ["dallas", "fort worth", "plano"]))
    cand["allowed_local_cities"] = ask("Allowed Local Cities (comma-separated)", current_cities, lambda v: validate_and_cast("candidate.allowed_local_cities", v, cfg))

    # 3. Target Titles
    print("\n--- 3. Search Matrix ---")
    current_titles = ", ".join(sm.get("target_titles", ["Director of Engineering", "VP of Engineering"]))
    sm["target_titles"] = ask("Target Job Titles (comma-separated)", current_titles, lambda v: validate_and_cast("search_matrix.target_titles", v, cfg))

    current_ex = ", ".join(sm.get("excluded_titles", ["junior", "intern", "entry level"]))
    sm["excluded_titles"] = ask("Excluded Job Titles (comma-separated)", current_ex, lambda v: validate_and_cast("search_matrix.excluded_titles", v, cfg))

    # 4. Automation & Alerts
    print("\n--- 4. Automation & Alerts ---")
    curr_interval = str(sched.get("interval_hours", 6.0))
    sched["interval_hours"] = ask("Scheduler Interval in Hours", curr_interval, lambda v: validate_and_cast("scheduler.interval_hours", v, cfg))

    sched_en = "yes" if sched.get("enabled", True) else "no"
    sched["enabled"] = ask("Enable Background Scheduler (yes/no)", sched_en, lambda v: validate_and_cast("scheduler.enabled", v, cfg))

    notif_en = "yes" if notif.get("desktop_enabled", True) else "no"
    notif["desktop_enabled"] = ask("Enable Desktop Notifications (yes/no)", notif_en, lambda v: validate_and_cast("notifications.desktop_enabled", v, cfg))

    cand.setdefault("professional_summary", "Accomplished technology leader with extensive experience scaling enterprise platforms, directing cross-functional engineering teams, and modernizing digital infrastructure.")
    cand.setdefault("key_skills", [
        "Technical Strategy & Enterprise Architecture",
        "Cross-Functional Engineering Leadership",
        "Cloud Infrastructure & Security Governance",
        "DevOps, CI/CD & Workflow Automation"
    ])
    cand.setdefault("experience", [])
    cand.setdefault("education", [])

    print("\n" + "=" * 65)
    print("Configuration Summary:")
    print(f"  Candidate: {cand['full_name']} <{cand['email']}> ({cand['primary_location']})")
    print(f"  Comp: Floor ${cand['min_salary_floor']:,} | Target ${cand['target_salary_baseline']:,}")
    print(f"  Workplace: {', '.join(cand['workplace_preferences'])} (Local: {', '.join(cand['allowed_local_cities'])})")
    print(f"  Targets: {', '.join(sm['target_titles'])}")
    print(f"  Scheduler: {sched['interval_hours']}h (Active: {sched['enabled']})")
    print(f"  Desktop Alerts: {notif['desktop_enabled']}")
    print("=" * 65)

    save = input("Save configuration to config.json? [Y/n]: ").strip().lower()
    if save in ["", "y", "yes"]:
        if save_config(cfg):
            print("\nConfiguration saved successfully to config.json!")
            print("Run 'python start.py' to launch the agent.")
        else:
            print("\nFailed to save configuration.")
    else:
        print("\nChanges discarded.")

def handle_get(key_path: str):
    cfg = load_config()
    try:
        val = get_nested(cfg, key_path)
        if isinstance(val, (dict, list)):
            print(json.dumps(val, indent=2))
        else:
            print(val)
    except KeyError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def handle_set(key_path: str, raw_value: str):
    cfg = load_config()
    try:
        val = validate_and_cast(key_path, raw_value, cfg)
        set_nested(cfg, key_path, val)
        if save_config(cfg):
            print(f"[Config] Set '{key_path}' = {json.dumps(val)}")
        else:
            print(f"[Config] Failed to save '{key_path}'", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Validation Error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    args = sys.argv[1:]
    if len(args) == 0:
        run_interactive_wizard()
    elif args[0] == "get":
        if len(args) < 2:
            print("Usage: python configure.py get <key_path>", file=sys.stderr)
            print("Example: python configure.py get candidate.min_salary_floor", file=sys.stderr)
            sys.exit(1)
        handle_get(args[1])
    elif args[0] == "set":
        if len(args) < 3:
            print("Usage: python configure.py set <key_path> <value>", file=sys.stderr)
            print("Example: python configure.py set candidate.min_salary_floor 190000", file=sys.stderr)
            sys.exit(1)
        key_path = args[1]
        val = " ".join(args[2:])
        handle_set(key_path, val)
    elif args[0] in ["--help", "-h", "help"]:
        print("Autonomous Job Search Agent - Configuration CLI")
        print("\nCommands:")
        print("  python configure.py                      Interactive step-by-step wizard")
        print("  python configure.py get <key_path>       Read a configuration value (e.g. scheduler.interval_hours)")
        print("  python configure.py set <key_path> <val> Update a configuration value with validation")
    else:
        print(f"Unknown command: '{args[0]}'. Use 'python configure.py --help' for usage.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
