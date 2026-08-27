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
