"""
One-Command Launcher for Autonomous Job Search Agent (YACareerOps).
Verifies Python version, verifies/installs dependencies, starts dashboard + scheduler,
and launches the browser to setup wizard or main dashboard.
"""

import sys
import os
import subprocess
import threading
import time
import webbrowser

MIN_PYTHON = (3, 10)

def check_python_version():
    if sys.version_info < MIN_PYTHON:
        print(f"Error: Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} or higher is required.")
        print(f"Current version detected: {sys.version.split()[0]}")
        print("Please upgrade Python from https://www.python.org/downloads/ and try again.")
        sys.exit(1)

def verify_dependencies():
    required_modules = [
        ("flask", "Flask"),
        ("pypdf", "pypdf"),
        ("docx", "python-docx"),
        ("plyer", "plyer"),
        ("apscheduler", "APScheduler"),
        ("google_auth_oauthlib", "google-auth-oauthlib"),
        ("google.oauth2", "google-auth"),
    ]

    missing = []
    for mod_name, pkg_name in required_modules:
        try:
            __import__(mod_name)
        except ImportError:
            missing.append(pkg_name)

    if missing:
        print(f"[Launcher] Missing required packages: {', '.join(missing)}")
        req_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
        if os.path.exists(req_file):
            print("[Launcher] Auto-installing dependencies from requirements.txt...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
                print("[Launcher] Dependencies installed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"[Launcher] Dependency installation failed: {e}")
                print("Please run: pip install -r requirements.txt manually.")
                sys.exit(1)
        else:
            print(f"[Launcher] Error: requirements.txt not found at {req_file}")
            sys.exit(1)

def main():
    check_python_version()
    verify_dependencies()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, base_dir)

    from dashboard_server import app, is_configured
    from scheduler import init_scheduler

    # Determine initial target URL
    configured = is_configured()
    port = 5000
    target_url = f"http://localhost:{port}" if configured else f"http://localhost:{port}/setup"

    print("=" * 65)
    print("       Autonomous Job Search Agent (YACareerOps)")
    print("=" * 65)
    if not configured:
        print("[Launcher] First-time setup detected.")
        print(f"[Launcher] Opening setup wizard at: {target_url}")
    else:
        print(f"[Launcher] Dashboard configured. Launching: {target_url}")

    # Launch browser in a background timer
    def open_browser():
        time.sleep(1.2)
        try:
            webbrowser.open(target_url)
        except Exception:
            pass

    threading.Thread(target=open_browser, daemon=True).start()

    # Start background scheduler
    print("[Launcher] Activating autonomous background search scheduler...")
    sched = init_scheduler(background=True)
    sched.start()

    # Run Dashboard Flask server
    print(f"[Launcher] Server active on http://localhost:{port} (Press Ctrl+C to stop)")
    try:
        app.run(host="0.0.0.0", port=port, debug=False)
    except (KeyboardInterrupt, SystemExit):
        print("\n[Launcher] Shutting down agent and scheduler. Goodbye!")
        try:
            sched.shutdown(wait=False)
        except Exception:
            pass

if __name__ == "__main__":
    main()
