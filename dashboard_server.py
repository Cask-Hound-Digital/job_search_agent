"""
Local Web Dashboard Server.
Exposes REST API endpoints on http://localhost:5000 for interactive queue review and tracking.
"""

import os
import json
from flask import Flask, jsonify, request, send_from_directory
from safe_state_manager import save_state_safe, load_state

app = Flask(__name__, static_folder=".")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    index_path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(BASE_DIR, "index.html")
    return "<h1>Autonomous Job Search Agent</h1><p>Dashboard running. Place index.html in root directory to view UI.</p>"

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

if __name__ == "__main__":
    print("Starting Autonomous Job Search Dashboard on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
