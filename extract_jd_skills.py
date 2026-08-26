import re
import json
import os
import urllib.parse
from audit_and_fix_queue_companies import fetch_page_content

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APPROVED_SKILLS_FILE = os.path.join(BASE_DIR, "approved_skills.example.json")
REJECTED_SKILLS_FILE = os.path.join(BASE_DIR, "rejected_skills.json")

COMMON_TECH_PATTERNS = [
    r'\b({{ENTERPRISE_CMS}}|Adobe Experience Manager|{{HEADLESS_CMS}}|Contentful|WordPress|Drupal|Strapi|Webflow|Sitecore|HubSpot|{{MARKETING_AUTOMATION_TOOL}})\b',
    r'\b(React|Next\.js|Vue|Angular|Node\.js|TypeScript|JavaScript|HTML5|CSS3|GraphQL|REST API|Tailwind)\b',
    r'\b({{ANALYTICS_PLATFORM}}|Google Analytics|Google Tag Manager|GTM|{{TAG_MANAGEMENT_TOOL}}|Segment|Adobe Analytics|Mixpanel|Amplitude|Optimizely|VWO)\b',
    r'\b(SEO|GEO|AEO|Generative Engine Optimization|CRO|A/B Testing|Multivariate Testing|UX/UI|Design System|Figma)\b',
    r'\b(AWS|Cloudflare|Vercel|Docker|Kubernetes|CI/CD|DevOps|Microservices|Headless Architecture|DXP)\b',
    r'\b(Jira|Confluence|Asana|Trello|Agile|Scrum|Kanban|P&L|Vendor Management|SLA Management)\b'
]

def load_approved_skills():
    if os.path.exists(APPROVED_SKILLS_FILE):
        try:
            with open(APPROVED_SKILLS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [s.strip() for s in data.get("approved_skills", [])]
        except Exception:
            pass
    return [
        "Executive Web Strategy & Architecture", "Global Web Operations", "CMS Governance ({{HEADLESS_CMS}}, {{ENTERPRISE_CMS}}, WordPress, Drupal)",
        "Next-Gen DXP Modernization", "Generative Engine Optimization (GEO/AEO)", "Conversion Rate Optimization (CRO)",
        "{{ANALYTICS_PLATFORM}} / GTM Data Governance", "Cross-Disciplinary Team Management (13+ Dev, DevOps, QA, BA, SEO)"
    ]

def load_rejected_skills():
    if os.path.exists(REJECTED_SKILLS_FILE):
        try:
            with open(REJECTED_SKILLS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [s.strip().lower() for s in data.get("rejected_skills", [])]
        except Exception:
            pass
    return ["amazon seller central", "amazon vendor central", "fba logistics", "brick-and-mortar retail operations"]

def save_approved_skills(skills_list):
    skills = load_approved_skills()
    updated = False
    for s in skills_list:
        if s and s not in skills:
            skills.append(s)
            updated = True
    if updated:
        with open(APPROVED_SKILLS_FILE, "w", encoding="utf-8") as f:
            json.dump({"last_updated": "2026-08-22", "approved_skills": skills}, f, indent=2)

def save_rejected_skills(skills_list):
    rejected = load_rejected_skills()
    raw_rejected = []
    if os.path.exists(REJECTED_SKILLS_FILE):
        try:
            with open(REJECTED_SKILLS_FILE, "r", encoding="utf-8") as f:
                raw_rejected = json.load(f).get("rejected_skills", [])
        except Exception:
            pass
    
    updated = False
    for s in skills_list:
        if s and s.lower() not in rejected:
            raw_rejected.append(s)
            rejected.append(s.lower())
            updated = True
    if updated:
        with open(REJECTED_SKILLS_FILE, "w", encoding="utf-8") as f:
            json.dump({"last_updated": "2026-08-22", "rejected_skills": raw_rejected}, f, indent=2)

def filter_relevant_approved_skills(html_text, approved_skills):
    if not html_text:
        return approved_skills[:6]
    
    text_lower = html_text.lower()
    scored_skills = []

    for s in approved_skills:
        score = 0
        s_lower = s.lower()
        # Split skill into core key terms
        words = [w for w in re.split(r'[^a-z0-9]', s_lower) if len(w) > 3 and w not in ['management', 'leadership', 'strategy', 'global', 'next', 'multi']]
        
        for w in words:
            if w in text_lower:
                score += text_lower.count(w)
        
        # Bonus for exact phrases
        if s_lower in text_lower:
            score += 10
            
        scored_skills.append((score, s))

    # Sort by relevance score descending
    scored_skills.sort(key=lambda x: x[0], reverse=True)
    
    # Filter to top relevant skills (minimum score > 0 if available, capped at 6)
    relevant = [s for score, s in scored_skills if score > 0]
    if len(relevant) < 4:
        relevant = [s for score, s in scored_skills[:6]]
        
    return relevant[:6]

def extract_skills_from_url_or_text(url="", html_text=""):
    if url and not html_text:
        html_text = fetch_page_content(url)
    
    approved = load_approved_skills()
    if not html_text:
        return approved[:6], []

    # Score and filter approved skills for maximum JD relevance
    relevant_approved = filter_relevant_approved_skills(html_text, approved)
    
    approved_lower = [a.lower() for a in approved]
    rejected_lower = load_rejected_skills()

    found_jd_skills_dict = {}
    for pattern in COMMON_TECH_PATTERNS:
        matches = re.findall(pattern, html_text, re.IGNORECASE)
        for m in matches:
            m_clean = m.strip()
            if len(m_clean) > 2:
                key = m_clean.lower()
                # Prefer title case (e.g. DevOps) over ALL CAPS (e.g. DEVOPS)
                if key not in found_jd_skills_dict:
                    found_jd_skills_dict[key] = m_clean
                else:
                    existing = found_jd_skills_dict[key]
                    if existing.isupper() and not m_clean.isupper():
                        found_jd_skills_dict[key] = m_clean

    # Filter out skills already approved or previously rejected
    unverified_skills = []
    seen_unverified_keys = set()
    for s_low in sorted(found_jd_skills_dict.keys()):
        s_display = found_jd_skills_dict[s_low]
        if s_low in rejected_lower or s_low in seen_unverified_keys:
            continue
        if any(s_low == a or s_low in a for a in approved_lower):
            continue
        seen_unverified_keys.add(s_low)
        unverified_skills.append(s_display)

    return relevant_approved, unverified_skills

if __name__ == '__main__':
    app, unv = extract_skills_from_url_or_text('https://www.linkedin.com/jobs/view/4456390472/')
    print('Approved Skills Count:', len(app))
    print('Unverified JD Skills Found:', unv)
