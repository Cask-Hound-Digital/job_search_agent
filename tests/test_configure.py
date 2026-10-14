import pytest
import os
import json
from configure import get_nested, set_nested, validate_and_cast, CONFIG_FILE

@pytest.fixture(autouse=True)
def backup_config():
    original = None
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            original = f.read()
    yield
    if original is not None:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(original)

def test_get_nested():
    data = {
        "candidate": {
            "full_name": "Test User",
            "min_salary_floor": 180000
        },
        "scheduler": {
            "interval_hours": 6.0
        }
    }
    assert get_nested(data, "candidate.full_name") == "Test User"
    assert get_nested(data, "candidate.min_salary_floor") == 180000
    assert get_nested(data, "scheduler.interval_hours") == 6.0

    with pytest.raises(KeyError):
        get_nested(data, "candidate.non_existent")

def test_set_nested():
    data = {}
    set_nested(data, "candidate.full_name", "Jane Doe")
    set_nested(data, "scheduler.interval_hours", 4.0)
    assert data["candidate"]["full_name"] == "Jane Doe"
    assert data["scheduler"]["interval_hours"] == 4.0

def test_validate_and_cast_booleans():
    cfg = {}
    assert validate_and_cast("scheduler.enabled", "true", cfg) is True
    assert validate_and_cast("scheduler.enabled", "no", cfg) is False
    assert validate_and_cast("notifications.desktop_enabled", "yes", cfg) is True
    assert validate_and_cast("sources.builtin", "off", cfg) is False

    with pytest.raises(ValueError):
        validate_and_cast("scheduler.enabled", "not_a_bool", cfg)

def test_validate_and_cast_numeric():
    cfg = {}
    assert validate_and_cast("candidate.min_salary_floor", "185000", cfg) == 185000
    assert validate_and_cast("candidate.min_salary_floor", "$190,000", cfg) == 190000
    assert validate_and_cast("scheduler.interval_hours", "8.5", cfg) == 8.5
    assert validate_and_cast("scheduler.interval_hours", "6h", cfg) == 6.0

    with pytest.raises(ValueError):
        validate_and_cast("candidate.min_salary_floor", "-500", cfg)

    with pytest.raises(ValueError):
        validate_and_cast("scheduler.interval_hours", "-1", cfg)

def test_validate_and_cast_email():
    cfg = {}
    assert validate_and_cast("candidate.email", "jane@example.com", cfg) == "jane@example.com"
    with pytest.raises(ValueError):
        validate_and_cast("candidate.email", "invalid_email", cfg)

def test_validate_and_cast_lists():
    cfg = {}
    titles = validate_and_cast("search_matrix.target_titles", "Director of Engineering, VP of Tech", cfg)
    assert titles == ["Director of Engineering", "VP of Tech"]

    cities = validate_and_cast("candidate.allowed_local_cities", "Dallas, Plano", cfg)
    assert cities == ["dallas", "plano"]

    with pytest.raises(ValueError):
        validate_and_cast("search_matrix.target_titles", "", cfg)
