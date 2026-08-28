import os
import json

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
EXAMPLE_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.example.json")

def load_config():
    """
    Loads configuration settings from config.json.
    Falls back to config.example.json if config.json does not exist.
    """
    target = CONFIG_FILE if os.path.exists(CONFIG_FILE) else EXAMPLE_CONFIG_FILE
    if not os.path.exists(target):
        raise FileNotFoundError("Configuration file not found. Please create config.json.")
        
    with open(target, 'r', encoding='utf-8') as f:
        return json.load(f)

# Global Configuration Instance
CONFIG = load_config()

def get_candidate_config():
    return CONFIG.get("candidate", {})

def get_search_matrix():
    return CONFIG.get("search_matrix", {})

def get_notifications_config():
    return CONFIG.get("notifications", {})

def get_target_titles():
    return get_search_matrix().get("target_titles", [])

def get_excluded_titles():
    return get_search_matrix().get("excluded_titles", [])

def get_allowed_local_cities():
    return get_candidate_config().get("allowed_local_cities", [])

def get_min_salary_floor():
    return get_candidate_config().get("min_salary_floor", 150000)

def get_primary_location():
    return get_candidate_config().get("primary_location", "Remote")

def get_scoring_signals():
    return CONFIG.get("scoring_signals", {})

def get_positive_keywords():
    return get_scoring_signals().get("positive_keywords", [])

def get_negative_keywords():
    return get_scoring_signals().get("negative_keywords", [])

TARGET_DOMAIN_PHRASES = [
    "digital experience",
    "web marketing",
    "web strategy",
    "web operations",
    "website growth",
    "digital product",
    "digital strategy",
    "digital transformation",
    "ai transformation",
    "ai agent",
    "ai operations",
    "ai automation",
    "agentic",
    "ai solutions",
    "product strategy",
    "0-to-1",
    "product innovation",
    "chief of staff",
    "digital marketing",
    "web technology",
    "growth marketing",
    "growth operations",
    "marketing technology",
    "product & ai",
    "product enablement",
    "incubation"
]

HARD_ENGINEER_EXCLUSIONS = [
    "engineer", "engineering", "developer", "architect", "programmer", "coder",
    "project manager", "project management", "pmo manager", "marketing operations", "marketing ops"
]

def is_valid_target_title(title_str):
    if not title_str:
        return False
    t_low = title_str.lower()

    # HARD REJECT: Engineer, Developer, Architect, PM, MOPs titles
    for h_ex in HARD_ENGINEER_EXCLUSIONS:
        if h_ex in t_low:
            return False

    # Reject hard excluded keywords
    for ex in get_excluded_titles():
        if ex.lower() in t_low:
            return False

    # Check if title matches target domain phrases or target titles
    for phrase in TARGET_DOMAIN_PHRASES:
        if phrase in t_low:
            return True

    for target in get_target_titles():
        if target.lower() in t_low:
            return True

    return False
