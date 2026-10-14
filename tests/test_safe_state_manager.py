"""
Tests for Safe State Manager.
Covers: atomic file writing, backup rotation, error resilience.
"""

import os
import json
import pytest
from safe_state_manager import save_state_safe, load_state, get_next_job_id

def test_get_next_job_id():
    apps = [{"id": "JOB-01"}, {"id": "JOB-02"}, {"id": "JOB-15"}]
    assert get_next_job_id(apps) == "JOB-16"
    assert get_next_job_id([]) == "JOB-01"

def test_save_state_safe_atomicity(tmp_path, monkeypatch):
    custom_state = str(tmp_path / "state.json")
    custom_backups = str(tmp_path / "state_backups")
    monkeypatch.setattr("safe_state_manager.STATE_FILE", custom_state)
    monkeypatch.setattr("safe_state_manager.BACKUP_DIR", custom_backups)

    # First write
    payload_1 = {
        "applications": [],
        "review_queue": [{"company": "Alpha", "title": "Lead Architect"}],
        "archived_queue": []
    }
    save_state_safe(payload_1, caller="test_atomicity_1")

    assert os.path.exists(custom_state)
    with open(custom_state, "r", encoding="utf-8") as f:
        data_1 = json.load(f)
    assert len(data_1["review_queue"]) == 1
    assert data_1["review_queue"][0]["company"] == "Alpha"

    # Second write triggers backup of state 1
    payload_2 = {
        "applications": [{"company": "Alpha", "title": "Lead Architect", "id": "JOB-01"}],
        "review_queue": [],
        "archived_queue": []
    }
    save_state_safe(payload_2, caller="test_atomicity_2")

    # Verify state 2 written cleanly
    with open(custom_state, "r", encoding="utf-8") as f:
        data_2 = json.load(f)
    assert len(data_2["applications"]) == 1
    assert len(data_2["review_queue"]) == 0

    # Verify backup retained state 1
    assert os.path.exists(custom_state + ".bak")
    with open(custom_state + ".bak", "r", encoding="utf-8") as f:
        bak_data = json.load(f)
    assert len(bak_data["review_queue"]) == 1

def test_load_state_fallback(tmp_path, monkeypatch):
    missing_file = str(tmp_path / "nonexistent_state.json")
    monkeypatch.setattr("safe_state_manager.STATE_FILE", missing_file)
    monkeypatch.setattr("safe_state_manager.BASE_DIR", str(tmp_path))

    loaded = load_state()
    assert isinstance(loaded, dict)
    assert "applications" in loaded
    assert "review_queue" in loaded
    assert "archived_queue" in loaded
