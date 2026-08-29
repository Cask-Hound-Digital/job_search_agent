import os
import json
import re

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

def get_excluded_locations():
    return get_search_matrix().get("excluded_locations", [])

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

# Exclude IC Software Engineers and Project Managers strictly
PURE_IC_ENGINEER_EXCLUSIONS = [
    "software engineer", "sr. software engineer", "sr software engineer", "senior software engineer",
    "staff software engineer", "principal software engineer", "full stack engineer", "frontend engineer",
    "backend engineer", "qa engineer", "developer", "programmer", "coder", "architect",
    "project manager", "project management", "pmo manager", "scrum master", "agile coach",
    "marketing operations", "marketing ops"
]

# Expressly allowed leadership & management categories
LEADERSHIP_ROLE_KEYWORDS = [
    "manager", "director", "head", "vp", "vice president", "lead", "principal", "chief", "advisor", "consultant"
]

def is_valid_target_title(title_str):
    if not title_str:
        return False
    t_low = title_str.lower()

    # 1. HARD REJECT: Project Managers & PMO
    if any(pm in t_low for pm in ["project manager", "project management", "pmo manager", "scrum master", "agile coach"]):
        return False

    # 2. ALWAYS ALLOW Product Management roles
    if "product manager" in t_low or "product management" in t_low or "product strategy" in t_low or "product lead" in t_low or "product director" in t_low or "product owner" in t_low:
        return True

    # 3. ALLOW Engineering Management & AI Engineering Leadership (e.g. Manager Software Engineering, Director AI Engineering)
    if any(lk in t_low for lk in ["manager", "director", "head", "vp", "vice president", "lead", "principal", "chief"]):
        if any(ek in t_low for ek in ["engineering", "ai", "gen ai", "genai", "agentic", "sre", "technical services", "digital", "data"]):
            return True

    # 4. HARD REJECT: Pure IC software engineers & developers
    for ic_ex in PURE_IC_ENGINEER_EXCLUSIONS:
        if re.search(rf'\b{re.escape(ic_ex)}\b', t_low):
            return False

    # 5. Reject explicit excluded titles from candidate config.json
    for ex in get_excluded_titles():
        if re.search(rf'\b{re.escape(ex.lower())}\b', t_low):
            return False

    # 6. Check target domain phrases or target titles
    for phrase in TARGET_DOMAIN_PHRASES:
        if phrase in t_low:
            return True

    for target in get_target_titles():
        if target.lower() in t_low:
            return True

    return False
