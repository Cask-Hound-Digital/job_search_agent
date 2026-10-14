"""
Local Web Dashboard Server.
Exposes REST API endpoints on http://localhost:5000 for interactive queue review and tracking.
"""

import os
import json
from flask import Flask, jsonify, request, send_from_directory, redirect
from safe_state_manager import save_state_safe, load_state

app = Flask(__name__, static_folder=".")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

def is_configured() -> bool:
    if not os.path.exists(CONFIG_PATH):
        return False
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            cand = cfg.get("candidate", {})
            name = cand.get("full_name", "").strip()
            if not name or "{{YOUR_FULL_NAME}}" in name or "{{" in name:
                return False
            email = cand.get("email", "").strip()
            if not email or "{{YOUR_EMAIL_ADDRESS}}" in email or "{{" in email:
                return False
            targets = cfg.get("search_matrix", {}).get("target_titles", [])
            if not targets:
                return False
            return True
    except Exception:
        return False

@app.route("/")
def index():
    if not is_configured():
        return redirect("/setup")
    index_path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(BASE_DIR, "index.html")
    return "<h1>Autonomous Job Search Agent</h1><p>Dashboard running. Place index.html in root directory to view UI.</p>"

@app.route("/setup")
def setup_page():
    setup_path = os.path.join(BASE_DIR, "setup.html")
    if os.path.exists(setup_path):
        return send_from_directory(BASE_DIR, "setup.html")
    return "<h1>Autonomous Job Search Agent - Setup Wizard</h1><p>setup.html not found.</p>"

@app.route("/api/setup", methods=["GET", "POST"])
def setup_api():
    if request.method == "GET":
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    return jsonify(json.load(f))
            except Exception:
                pass
        return jsonify({})

    payload = request.get_json() or {}
    full_name = payload.get("full_name", "").strip()
    email = payload.get("email", "").strip()
    phone = payload.get("phone", "").strip()
    primary_location = payload.get("primary_location", "").strip()
    min_salary_floor = payload.get("min_salary_floor", 0)
    target_salary_baseline = payload.get("target_salary_baseline", 0)
    workplace_preferences = payload.get("workplace_preferences", [])
    allowed_local_cities = payload.get("allowed_local_cities", [])
    target_titles = payload.get("target_titles", [])
    excluded_titles = payload.get("excluded_titles", [])

    if not full_name:
        return jsonify({"success": False, "error": "Full Name is required."}), 400
    if not email or "@" not in email or "." not in email:
        return jsonify({"success": False, "error": "A valid Email Address is required."}), 400
    if not phone:
        return jsonify({"success": False, "error": "Phone Number is required."}), 400
    if not primary_location:
        return jsonify({"success": False, "error": "Primary Location is required."}), 400
    if not isinstance(min_salary_floor, (int, float)) or min_salary_floor < 0:
        return jsonify({"success": False, "error": "Minimum Salary Floor must be a positive number."}), 400
    if not target_titles or len(target_titles) == 0:
        return jsonify({"success": False, "error": "At least one Target Job Title is required."}), 400

    existing_cfg = {}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                existing_cfg = json.load(f)
        except Exception:
            existing_cfg = {}

    cand = existing_cfg.get("candidate", {})
    cand.update({
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "min_salary_floor": int(min_salary_floor),
        "target_salary_baseline": int(target_salary_baseline) if target_salary_baseline else int(min_salary_floor) + 20000,
        "workplace_preferences": workplace_preferences if workplace_preferences else ["Remote", "Hybrid"],
        "primary_location": primary_location,
        "allowed_local_cities": [c.lower().strip() for c in allowed_local_cities if c.strip()]
    })

    cand.setdefault("professional_summary", "Accomplished technology leader with extensive experience scaling enterprise platforms, directing cross-functional engineering teams, and modernizing digital infrastructure.")
    cand.setdefault("key_skills", [
        "Technical Strategy & Enterprise Architecture",
        "Cross-Functional Engineering Leadership",
        "Cloud Infrastructure & Security Governance",
        "DevOps, CI/CD & Workflow Automation"
    ])
    cand.setdefault("experience", [])
    cand.setdefault("education", [])

    search_matrix = existing_cfg.get("search_matrix", {})
    search_matrix["target_titles"] = [t.strip() for t in target_titles if t.strip()]
    search_matrix["excluded_titles"] = [t.strip() for t in excluded_titles if t.strip()]

    new_cfg = {
        "candidate": cand,
        "search_matrix": search_matrix,
        "scoring_signals": existing_cfg.get("scoring_signals", {
            "positive_keywords": ["architecture", "scaling", "leadership"],
            "negative_keywords": ["entry level", "internship"]
        }),
        "notifications": existing_cfg.get("notifications", {
            "telegram_enabled": False,
            "alert_on_raw_ingest": False,
            "alert_only_vetted": True
        })
    }

    tmp_path = CONFIG_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(new_cfg, f, indent=2)
    os.replace(tmp_path, CONFIG_PATH)

    return jsonify({"success": True, "redirect": "/"})

@app.route("/api/status", methods=["GET"])
def get_status():
    state = load_state()
    return jsonify({
        "status": "online",
        "applications_count": len(state.get("applications", [])),
        "review_queue_count": len(state.get("review_queue", [])),
        "archived_queue_count": len(state.get("archived_queue", [])),
        "last_updated": state.get("last_updated", "N/A")
    })

@app.route("/api/queue", methods=["GET"])
def get_queue():
    state = load_state()
    return jsonify(state.get("review_queue", []))

@app.route("/api/applications", methods=["GET"])
def get_applications():
    state = load_state()
    return jsonify(state.get("applications", []))

@app.route("/api/archive", methods=["POST"])
def archive_item():
    payload = request.get_json() or {}
    url = payload.get("url")
    reason = payload.get("reason", "User Dismissed")

    state = load_state()
    queue = state.get("review_queue", [])
    archived = state.get("archived_queue", [])

    new_q = []
    found = None
    for item in queue:
        if item.get("url") == url:
            found = item
            found["archive_reason"] = reason
            archived.append(found)
        else:
            new_q.append(item)

    if found:
        state["review_queue"] = new_q
        state["archived_queue"] = archived
        save_state_safe(state, caller="dashboard_archive")
        return jsonify({"success": True, "archived": found})
    return jsonify({"success": False, "error": "Item not found"}), 404

@app.route("/api/apply", methods=["POST"])
def apply_item():
    payload = request.get_json() or {}
    url = payload.get("url")
    company = payload.get("company", "Unknown")
    title = payload.get("title", "Unknown")

    if not url:
        return jsonify({"success": False, "error": "Missing URL"}), 400

    from build_documents import generate_package
    from safe_state_manager import get_next_job_id
    from datetime import datetime

    output_dir = generate_package(company, title)

    state = load_state()
    queue = state.get("review_queue", [])
    applications = state.get("applications", [])

    new_q = []
    found = None
    for item in queue:
        item_url = item.get("url") or item.get("job_url")
        if item_url == url:
            found = item
        else:
            new_q.append(item)

    if not found:
        found = {
            "company": company,
            "title": title,
            "url": url,
            "source": "Manual Apply"
        }

    app_entry = {
        **found,
        "id": get_next_job_id(applications),
        "status": "Applied",
        "date_applied": datetime.now().strftime("%Y-%m-%d"),
        "package_dir": output_dir
    }
    applications.append(app_entry)

    state["review_queue"] = new_q
    state["applications"] = applications
    save_state_safe(state, caller="dashboard_apply")

    return jsonify({
        "success": True,
        "output_folder": output_dir,
        "application": app_entry
    })

@app.route("/api/scheduler", methods=["GET", "POST"])
def scheduler_api():
    from scheduler import get_scheduler_status, update_scheduler_interval
    if request.method == "POST":
        payload = request.get_json() or {}
        interval = payload.get("interval_hours")
        enabled = payload.get("enabled", True)
        if interval is not None:
            try:
                update_scheduler_interval(float(interval), enabled=bool(enabled))
            except ValueError:
                return jsonify({"success": False, "error": "Invalid interval_hours"}), 400
        return jsonify({"success": True, "scheduler": get_scheduler_status()})
    return jsonify(get_scheduler_status())

@app.route("/api/scheduler/run", methods=["POST"])
def scheduler_run_now():
    import threading
    from run_unified_search import run_unified_search_cycle
    thread = threading.Thread(target=run_unified_search_cycle, daemon=True)
    thread.start()
    return jsonify({"success": True, "message": "Search cycle initiated in background."})

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Autonomous Job Search Dashboard Server")
    parser.add_argument("--daemon", action="store_true", help="Enable built-in background scheduler")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on (default 5000)")
    args = parser.parse_args()

    if args.daemon:
        from scheduler import init_scheduler
        sched = init_scheduler(background=True)
        sched.start()
        print("Built-in background scheduler activated with daemon mode.")

    print(f"Starting Autonomous Job Search Dashboard on http://localhost:{args.port}")
    app.run(host="0.0.0.0", port=args.port, debug=False)

