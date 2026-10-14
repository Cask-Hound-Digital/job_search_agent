import json
import os
import pytest
from dashboard_server import app, CONFIG_PATH

@pytest.fixture
def client():
    app.config["TESTING"] = True
    original_cfg = None
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            original_cfg = f.read()

    with app.test_client() as client:
        yield client

    if original_cfg is not None:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(original_cfg)

def test_api_status(client):
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.get_json()
    assert "status" in data
    assert "review_queue_count" in data
    assert "applications_count" in data
    assert "scheduler" in data
    assert "notifications" in data
    assert "sources" in data

def test_api_sources_get_and_post(client):
    res = client.get("/api/sources")
    assert res.status_code == 200
    data = res.get_json()
    assert "sources" in data
    assert "builtin" in data["sources"]
    assert "details" in data

    # Toggle builtin source
    post_res = client.post("/api/sources", json={"builtin": False})
    assert post_res.status_code == 200
    assert post_res.get_json()["sources"]["builtin"] is False

    # Restore builtin source
    post_res2 = client.post("/api/sources", json={"builtin": True})
    assert post_res2.status_code == 200
    assert post_res2.get_json()["sources"]["builtin"] is True

def test_api_notifications_get_and_post(client):
    res = client.get("/api/notifications")
    assert res.status_code == 200
    data = res.get_json()
    assert "desktop_enabled" in data

    post_res = client.post("/api/notifications", json={"desktop_enabled": False})
    assert post_res.status_code == 200
    assert post_res.get_json()["notifications"]["desktop_enabled"] is False

    post_res2 = client.post("/api/notifications", json={"desktop_enabled": True})
    assert post_res2.status_code == 200
    assert post_res2.get_json()["notifications"]["desktop_enabled"] is True

def test_api_scheduler_toggle(client):
    res = client.get("/api/scheduler")
    assert res.status_code == 200
    curr = res.get_json()

    post_res = client.post("/api/scheduler", json={"enabled": False})
    assert post_res.status_code == 200
    assert post_res.get_json()["scheduler"]["enabled"] is False

    post_res2 = client.post("/api/scheduler", json={"enabled": True})
    assert post_res2.status_code == 200
    assert post_res2.get_json()["scheduler"]["enabled"] is True

def test_api_settings_get_and_post(client):
    res = client.get("/api/settings")
    assert res.status_code == 200
    cfg = res.get_json()
    assert "candidate" in cfg

    # Test validation failure with empty name
    bad_res = client.post("/api/settings", json={"full_name": ""})
    assert bad_res.status_code == 400

    # Test valid update
    good_payload = {
        "full_name": "Test Leader",
        "email": "test.leader@example.com",
        "phone": "555-123-4567",
        "primary_location": "Dallas, TX",
        "min_salary_floor": 180000,
        "target_salary_baseline": 200000,
        "workplace_preferences": ["Remote"],
        "allowed_local_cities": ["dallas"],
        "target_titles": ["Director of Engineering"],
        "excluded_titles": ["Junior"],
        "notifications": {"desktop_enabled": True},
        "scheduler": {"interval_hours": 6.0, "enabled": True}
    }
    good_res = client.post("/api/settings", json=good_payload)
    assert good_res.status_code == 200
    assert good_res.get_json()["success"] is True
