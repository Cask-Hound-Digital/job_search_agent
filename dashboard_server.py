import sys
import json
import os
import re
import subprocess
import urllib.parse
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

PORT = 5000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "state.json")
PAYLOAD_FILE = os.path.join(BASE_DIR, "current_payload.json")
APPROVED_SKILLS_FILE = os.path.join(BASE_DIR, "approved_skills.json")
PYTHON_EXE = sys.executable

def get_approved_skills_data():
    if os.path.exists(APPROVED_SKILLS_FILE):
        try:
            with open(APPROVED_SKILLS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"approved_skills": [], "approved_categories": []}

def save_new_approved_skills(new_skills_list):
    data = get_approved_skills_data()
    existing = set(s.lower() for s in data.get("approved_skills", []))
    added = False
    for s in new_skills_list:
        s_clean = s.strip()
        if s_clean and s_clean.lower() not in existing:
            data.setdefault("approved_skills", []).append(s_clean)
            existing.add(s_clean.lower())
            added = True
    if added:
        try:
            with open(APPROVED_SKILLS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print(f"[SKILL LEARNING ENGINE] Learned and saved {len(new_skills_list)} candidate-approved skills into approved_skills.json.")
        except Exception as e:
            print(f"Error saving approved skills: {e}")

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads."""
    daemon_threads = True

class DashboardRequestHandler(BaseHTTPRequestHandler):

    def _set_cors_headers(self):
        origin = self.headers.get('Origin', '')
        allowed_prefixes = ('http://localhost', 'http://127.0.0.1', 'file://', 'null')
        if origin and (origin.startswith(allowed_prefixes) or origin in allowed_prefixes):
            self.send_header('Access-Control-Allow-Origin', origin)
        else:
            self.send_header('Access-Control-Allow-Origin', 'http://localhost:5000')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            response = {"status": "running", "server": "Job Search Dashboard Server v1.0"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        elif self.path == '/api/approved_skills':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(get_approved_skills_data()).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/apply':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                job_url = data.get('url', '').strip()
                company = data.get('company', 'Target Company').strip()
                title = data.get('title', 'Executive Role').strip()
                user_confirmed = data.get('user_confirmed', False)
                confirmed_skills = data.get('confirmed_skills', [])

                print(f"\n[SERVER API APPLY TRIGGERED] Company: '{company}' | Title: '{title}' | Confirmed: {user_confirmed}")

                # Clean company folder name
                folder_name = re.sub(r'[\\/*?:"<>|]', '', company).strip()
                if not folder_name:
                    folder_name = "Target Company"

                # Define proposed skills for this application
                proposed_skills_list = [
                    "Enterprise Web Strategy & Architecture",
                    "Global Web Operations",
                    "CMS Governance ({{HEADLESS_CMS}}, {{ENTERPRISE_CMS}}, WordPress, Drupal)",
                    "Next-Gen DXP Modernization",
                    "Multi-National Site Performance",
                    "Generative Engine Optimization (GEO/AEO)",
                    "AI-Assisted Workflows (Claude, ChatGPT, CoPilot)",
                    "Automated Personalization & Analytics",
                    "High-Velocity A/B Testing Roadmaps",
                    "Customer Experience (CX) Architecture",
                    "Multi-Site Funnel Velocity",
                    "{{ANALYTICS_PLATFORM}} / GTM Data Governance",
                    "Cross-Disciplinary Team Management (13+ Dev, DevOps, QA, BA, SEO)",
                    "ROI & Business Case Governance",
                    "Strategic Partner Management"
                ]

                # Check against approved skills database
                skills_data = get_approved_skills_data()
                approved_set = set(s.lower() for s in skills_data.get("approved_skills", []))
                
                # Check for unverified skills if not explicitly user_confirmed
                unverified = []
                for sk in proposed_skills_list:
                    # Check if skill substring is in approved set
                    if not any(app_s in sk.lower() or sk.lower() in app_s for app_s in approved_set):
                        unverified.append(sk)

                if not user_confirmed and unverified:
                    print(f"[SKILL VERIFICATION REQUIRED] {len(unverified)} unverified skills detected for {company} ({title}). Prompting candidate...")
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self._set_cors_headers()
                    self.end_headers()
                    res = {
                        "status": "needs_confirmation",
                        "company": company,
                        "title": title,
                        "url": job_url,
                        "proposed_skills": proposed_skills_list,
                        "unverified_skills": unverified,
                        "message": "Candidate confirmation required for unverified skills before generating package."
                    }
                    self.wfile.write(json.dumps(res).encode('utf-8'))
                    return

                # If confirmed or no unverified skills, learn newly confirmed skills
                if confirmed_skills:
                    save_new_approved_skills(confirmed_skills)

                # Determine role family to dynamically tailor resume content
                t_low = title.lower()
                
                if "product manager" in t_low or "talent technology" in t_low or "product management" in t_low:
                    role_headline = f"{title.upper()} | HR TECH, INTERNAL PLATFORMS & PRODUCT LEADER"
                    role_summary = f"Accomplished Product & Technology Leader with 18+ years directing enterprise web platforms, internal talent systems, digital workflow modernization, and cross-functional technology teams. Proven track record managing complex software roadmaps, user experience (UX) architectures, and data-driven platform operations. Expert in stakeholder alignment, Agile delivery cadences, AI technology integration (Claude, ChatGPT, CoPilot), and scaling product capabilities."
                    role_expertise = [
                        ["Digital Product & HR Technology Strategy: ", "Internal Platform Roadmaps, Talent Systems Modernization, Product Lifecycle Management, Agile / Scrum Frameworks."],
                        ["User Experience & Workflow Engineering: ", "Employee & Candidate UX Design, Automated Workflow Engineering, Intranet / Enterprise Portal Architecture, System Usability."],
                        ["AI Activation & Product Innovation: ", "AI Assistant Integration (Claude, ChatGPT, CoPilot), Automated Operations, Data & Analytics Governance."],
                        ["Cross-Functional Stakeholder Governance: ", "Engineering & Product Alignment, Executive Steering Committees, Strategic Vendor Management, Team Coaching."]
                    ]
                    role_tm_bullets = [
                        ["Enterprise Web & Internal Platform Leadership: ", f"Led global web marketing and platform product management for {{MOST_RECENT_COMPANY}}'s enterprise operations, directing a 13+ person team (Product, Development, DevOps, QA, BA) to own core digital systems."],
                        ["Digital Workflow Modernization & Automation: ", "Directed the end-to-end modernization of internal product intake and content publishing workflows onto {{HEADLESS_CMS}} CMS, establishing automated governance and accelerating delivery cadences by 30%."],
                        ["User Experience (UX) & Conversion Optimization: ", "Owned product analytics and UX experimentation roadmaps, executing 40+ annual testing cycles across self-serve portals to increase user engagement and workflow completion rates by 42%."],
                        ["AI Technology Integration & Engineering Velocity: ", "Championed AI tools (Claude, ChatGPT, CoPilot) across product planning and development, streamlining requirement definitions and reducing operational cycle times."],
                        ["Multi-National System Architecture & Integration: ", "Directed enterprise platform integrations across 34 countries, unifying analytics ({{ANALYTICS_PLATFORM}}, GTM) and marketing systems ({{MARKETING_AUTOMATION_TOOL}}, {{TAG_MANAGEMENT_TOOL}}) to ensure high-availability performance."]
                    ]
                elif "digital marketing" in t_low or "growth" in t_low or "marketing director" in t_low:
                    role_headline = f"{title.upper()} | GLOBAL DEMAND GEN, CRO & PERFORMANCE MARKETING LEADER"
                    role_summary = f"Executive Digital Marketing & Growth Leader with 18+ years driving multi-channel demand generation, enterprise web strategy, conversion rate optimization (CRO), and AI-first marketing transformation. Proven track record turning corporate digital properties into high-velocity customer acquisition engines. Expert in performance analytics ({{ANALYTICS_PLATFORM}}, GTM), generative engine optimization (GEO/AEO), paid media strategy, and cross-functional team leadership."
                    role_expertise = [
                        ["Global Digital Marketing & Demand Generation: ", "Multi-Channel Customer Acquisition, Full-Funnel Growth Strategy, Brand & Content Operations, Campaign Execution."],
                        ["Conversion Rate Optimization (CRO) & CX: ", "High-Velocity A/B & Multivariate Testing, Checkout & Landing Page Funnel Velocity, {{ANALYTICS_PLATFORM}} / GTM Data Attribution."],
                        ["AI-First Marketing & GEO/AEO Dominance: ", "Generative Engine Optimization (GEO/AEO), AI Content Operations (Claude, ChatGPT), Personalization Engines."],
                        ["Executive Leadership & Revenue Growth: ", "Cross-Disciplinary Team Management (13+ Dev, Marketing, SEO), Budget Management ($1M+), Commercial Pipeline Growth."]
                    ]
                    role_tm_bullets = [
                        ["Global Demand Generation & Web Marketing Leadership: ", f"Directed global digital marketing and web operations for {{MOST_RECENT_COMPANY}}'s B2B and B2C enterprise portfolios, managing a 13+ person team to own the corporate web channel as the primary demand generation and revenue engine."],
                        ["High-Velocity CRO & Funnel Optimization: ", "Owned global CRO testing roadmap, executing 40+ annual A/B and multivariate tests across pricing and campaign landing pages, increasing digital trial signups by 42% and web-sourced pipeline contribution by 35%."],
                        ["AI-First Marketing Transformation & GEO Dominance: ", "Pioneered Generative Engine Optimization (GEO/AEO) strategies to structure brand content for AI assistants, increasing search visibility by 40% and driving a +15% uplift in organic demo conversions."],
                        ["Multi-National Platform & Analytics Operations: ", "Directed enterprise platform migration across 34 countries and 14 languages, integrating {{MARKETING_AUTOMATION_TOOL}}, {{TAG_MANAGEMENT_TOOL}}, GTM, and {{ANALYTICS_PLATFORM}} to reduce page load times by 40% and boost organic sessions by 10%."],
                        ["Cross-Functional Governance & Growth Execution: ", "Established a unified collaboration model for marketing, SEO, design, and engineering teams, streamlining campaign launches and elevating ROI across all digital channels."]
                    ]
                else:
                    role_headline = f"{title.upper()} | GLOBAL DIGITAL EXPERIENCE & AI LEADER"
                    role_summary = f"Executive web technology and digital experience leader with 18+ years leading enterprise web strategy, digital product operations, and cross-functional teams. Proven track record turning corporate web channels into high-velocity demand generation and revenue engines. Expert in evaluating emerging AI technologies (Claude Code, ChatGPT, CoPilot, GEO/AEO), modernizing legacy digital architectures, and managing strategic vendor/partner relationships."
                    role_expertise = [
                        ["Enterprise Web Strategy & Architecture: ", "Global Web Operations, CMS Governance ({{HEADLESS_CMS}}, {{ENTERPRISE_CMS}}, WordPress, Drupal), Next-Gen DXP Modernization, Multi-National Site Performance."],
                        ["AI Activation & Digital Innovation: ", "Generative Engine Optimization (GEO/AEO), AI-Assisted Workflows (Claude, ChatGPT, CoPilot), Automated Personalization & Analytics."],
                        ["Conversion Rate Optimization (CRO): ", "High-Velocity A/B Testing Roadmaps, Customer Experience (CX) Architecture, Multi-Site Funnel Velocity, {{ANALYTICS_PLATFORM}} / GTM Data Governance."],
                        ["Executive Leadership & Governance: ", "Cross-Disciplinary Team Management (13+ Dev, DevOps, QA, BA, SEO), ROI & Business Case Governance, Strategic Partner Management."]
                    ]
                    role_tm_bullets = [
                        ["Global Web Strategy & Operations Leadership: ", f"Led global web marketing and digital operations for {{MOST_RECENT_COMPANY}}'s enterprise B2B and B2C portfolios, managing a {{TEAM_SIZE_PLACEHOLDER}} (Development, DevOps, QA, BA, SEO) to own the corporate web channel as the primary demand generation and pipeline engine."],
                        ["Next-Gen DXP Discovery & Decision-Making: ", "Led discovery, architectural evaluation, ROI analysis, and executive vendor decision-making for a next-generation Digital Experience Platform (DXP) to replace legacy Adobe Experience Manager ({{ENTERPRISE_CMS}}), aligning C-suite stakeholders around modern API architecture and TCO optimization."],
                        ["TrendAI Redesign & {{HEADLESS_CMS}} CMS Platform Migration: ", "Organized and executed the end-to-end redesign and platform migration of the TrendAI website onto {{HEADLESS_CMS}} CMS, establishing structured content models, modern headless workflows, and rapid publishing cadences."],
                        ["AI-First Innovation & GEO/AEO Integration: ", "Championed AI technologies (Claude, ChatGPT, CoPilot, LLMs) and Generative Engine Optimization (GEO/AEO), driving a 40% increase in brand search presence and a +15% uplift in organic demo/trial conversions."],
                        ["Multi-National Platform Modernization & Performance: ", "Directed enterprise web platform migration across 34 countries and 14 languages, integrating {{MARKETING_AUTOMATION_TOOL}}, {{TAG_MANAGEMENT_TOOL}}, GTM, {{PERFORMANCE_TOOL}}, {{SEARCH_TOOL}}, and {{ANALYTICS_PLATFORM}} to reduce page load times by 40%, boost organic sessions by 10%, and drive 15% pipeline growth."]
                    ]

                # Construct dynamic application payload
                payload = {
                    "company": company,
                    "folder": folder_name,
                    "role": title,
                    "headline": role_headline,
                    "summary": role_summary,
                    "areas_of_expertise": role_expertise,
                    "trend_micro_bullets": role_tm_bullets,
                    "{{PREVIOUS_COMPANY_2}}_bullets": [
                        ["Digital Product Strategy & Storefront Management: ", "Oversaw end-to-end business management and product lifecycle for mobile app software distributor in {{YOUR_CITY_STATE}}, designing web architecture and checkout funnels for mobile app stores (Sprint) that increased e-commerce checkout conversion rate by +34%."],
                        ["Go-To-Market & Executive Alignment: ", "Executed product strategy across online and on-device stores, defining functional requirements, wireframes, and customer use cases to drive a 30% increase in product-led engagement."]
                    ],
                    "{{PREVIOUS_COMPANY_3}}_bullets": [
                        ["Digital Marketing & Revenue Optimization: ", "Directed corporate e-commerce and web marketing (SEO, SEM, email, marketplaces) at {{PREVIOUS_COMPANY_3}} in {{YOUR_CITY_STATE}}, testing offers and UX flows to sustain 35%+ annual online sales growth."]
                    ],
                    "cover_letter": {
                        "date": datetime.now().strftime("%B %d, %Y"),
                        "recipient": f"Executive Selection Committee & Leadership Team\n{company}\nCorporate Office / Remote Executive Team",
                        "salutation": f"Dear {company} Selection Committee,",
                        "paragraphs": [
                            f"I am writing to express my strong enthusiasm for the {title} position at {company}. With over 18 years of experience leading enterprise digital strategy, digital product operations, technology modernization, and cross-functional technology teams, I connect directly with your mission to build and scale high-performing digital capabilities.",
                            "Throughout my tenure as {{YOUR_MOST_RECENT_TITLE}} at {{MOST_RECENT_COMPANY}} ({{MOST_RECENT_EMPLOYMENT_DATES}}), I built a high-performing global organization of 13+ cross-functional specialists (development, DevOps, QA, BA, SEO). I owned our corporate web channel as the primary demand generation engine, directing a 34-country {{ENTERPRISE_CMS}} 6.x migration that reduced page load times by 40% while leading the discovery, ROI evaluation, and decision-making for a next-gen DXP platform to replace legacy {{ENTERPRISE_CMS}}. Additionally, I organized and executed the TrendAI site redesign and migration to {{HEADLESS_CMS}} CMS, while pioneering Generative Engine Optimization (GEO/AEO) strategies that increased search visibility by 40% and lifted organic demo conversions by +15%.",
                            "Prior to {{MOST_RECENT_COMPANY}}, I served as {{YOUR_PREVIOUS_TITLE_1}} at {{PREVIOUS_COMPANY_2}} in {{YOUR_CITY_STATE}}, where I managed digital storefront software development across web and mobile partner channels (Sprint), boosting checkout conversion rates by +34%. My background combines executive digital consulting, deep technical fluency across enterprise MarTech/Tech ecosystems, and a proven track record leading cross-disciplinary teams through organizational change.",
                            f"Thank you for your time and consideration. I welcome the opportunity to discuss how my background in digital strategy, AI innovation, and executive leadership will drive immediate value for {company}."
                        ]
                    }
                }

                # Write payload file
                with open(PAYLOAD_FILE, 'w', encoding='utf-8') as pf:
                    json.dump(payload, pf, indent=2)

                # Run build_application_package.py
                build_proc = subprocess.run(
                    [PYTHON_EXE, "build_application_package.py"],
                    cwd=BASE_DIR,
                    capture_output=True,
                    text=True
                )

                if build_proc.returncode != 0:
                    print(f"Error building package: {build_proc.stderr}")
                    self.send_response(500)
                    self._set_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": build_proc.stderr}).encode('utf-8'))
                    return

                # Update state.json: move role to applications
                if os.path.exists(STATE_FILE):
                    with open(STATE_FILE, 'r', encoding='utf-8') as sf:
                        state_data = json.load(sf)

                    apps = state_data.get("applications", [])
                    job_id = f"JOB-{len(apps) + 1:02d}"

                    new_app = {
                        "id": job_id,
                        "job_title": title,
                        "company_name": company,
                        "job_url": job_url,
                        "location": "Remote / Hybrid",
                        "compensation_range": "Executive Leadership Level",
                        "match_score": 98,
                        "status": "Applied",
                        "source": "LinkedIn" if "linkedin" in job_url.lower() else ("Greenhouse" if "greenhouse" in job_url.lower() else ("Lever" if "lever" in job_url.lower() else "Company Portal")),
                        "submission_date": datetime.now().strftime("%Y-%m-%d"),
                        "submission_channel": "Direct 1-Click Dashboard Apply",
                        "notes": f"Applied via 1-click dashboard trigger. Master application package generated in P:\\Job Search\\{folder_name}\\",
                        "application_notes": "",
                        "application_followups": [],
                        "interviews": []
                    }

                    apps.append(new_app)
                    state_data["applications"] = apps

                    # Remove from review_queue & verified_gmail_jobs
                    u_clean = job_url.split('?')[0].lower() if job_url else ""
                    if u_clean:
                        state_data["verified_gmail_jobs"] = [j for j in state_data.get("verified_gmail_jobs", []) if j.get("url", "").split('?')[0].lower() != u_clean]
                        state_data["review_queue"] = [j for j in state_data.get("review_queue", []) if j.get("url", "").split('?')[0].lower() != u_clean]

                    with open(STATE_FILE, 'w', encoding='utf-8') as sf:
                        json.dump(state_data, sf, indent=2)

                # Sync live dashboard
                subprocess.run([PYTHON_EXE, "sync_dashboard_from_state.py"], cwd=BASE_DIR)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                res = {
                    "status": "success",
                    "company": company,
                    "title": title,
                    "folder": folder_name,
                    "message": f"Master package generated in P:\\Job Search\\{folder_name}\\"
                }
                self.wfile.write(json.dumps(res).encode('utf-8'))

            except Exception as e:
                print(f"Exception handling /api/apply: {e}")
                self.send_response(500)
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))

        elif self.path == '/api/update_status':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                app_id = data.get('id')
                new_status = data.get('status')
                if os.path.exists(STATE_FILE):
                    with open(STATE_FILE, 'r', encoding='utf-8') as sf:
                        state_data = json.load(sf)
                    for app in state_data.get("applications", []):
                        if app.get("id") == app_id:
                            app["status"] = new_status
                            break
                    with open(STATE_FILE, 'w', encoding='utf-8') as sf:
                        json.dump(state_data, sf, indent=2)
                subprocess.run([PYTHON_EXE, "sync_dashboard_from_state.py"], cwd=BASE_DIR)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))

        elif self.path == '/api/save_application_details':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                app_id = data.get('id')
                notes = data.get('application_notes', '')
                followups = data.get('application_followups', [])
                if os.path.exists(STATE_FILE):
                    with open(STATE_FILE, 'r', encoding='utf-8') as sf:
                        state_data = json.load(sf)
                    for app in state_data.get("applications", []):
                        if app.get("id") == app_id:
                            app["application_notes"] = notes
                            app["application_followups"] = followups
                            break
                    with open(STATE_FILE, 'w', encoding='utf-8') as sf:
                        json.dump(state_data, sf, indent=2)
                subprocess.run([PYTHON_EXE, "sync_dashboard_from_state.py"], cwd=BASE_DIR)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))

        elif self.path == '/api/save_interview':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                app_id = data.get('app_id')
                interview_data = data.get('interview', {})
                if os.path.exists(STATE_FILE):
                    with open(STATE_FILE, 'r', encoding='utf-8') as sf:
                        state_data = json.load(sf)
                    for app in state_data.get("applications", []):
                        if app.get("id") == app_id:
                            interviews = app.setdefault("interviews", [])
                            # Check if updating existing or adding new
                            int_id = interview_data.get("id")
                            found = False
                            if int_id:
                                for idx, existing_int in enumerate(interviews):
                                    if existing_int.get("id") == int_id:
                                        interviews[idx] = interview_data
                                        found = True
                                        break
                            if not found:
                                interview_data["id"] = f"INT-{len(interviews) + 1:02d}"
                                interviews.append(interview_data)
                            break
                    with open(STATE_FILE, 'w', encoding='utf-8') as sf:
                        json.dump(state_data, sf, indent=2)
                subprocess.run([PYTHON_EXE, "sync_dashboard_from_state.py"], cwd=BASE_DIR)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))

        elif self.path == '/api/delete_interview':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                app_id = data.get('app_id')
                int_id = data.get('interview_id')
                if os.path.exists(STATE_FILE):
                    with open(STATE_FILE, 'r', encoding='utf-8') as sf:
                        state_data = json.load(sf)
                    for app in state_data.get("applications", []):
                        if app.get("id") == app_id:
                            app["interviews"] = [i for i in app.get("interviews", []) if i.get("id") != int_id]
                            break
                    with open(STATE_FILE, 'w', encoding='utf-8') as sf:
                        json.dump(state_data, sf, indent=2)
                subprocess.run([PYTHON_EXE, "sync_dashboard_from_state.py"], cwd=BASE_DIR)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))

        elif self.path == '/api/archive_queue':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                job_url = data.get('url', '').strip()
                reason_category = data.get('reason_category', 'General Removal').strip()
                custom_notes = data.get('custom_notes', '').strip()

                u_clean = job_url.split('?')[0].lower() if job_url else ""
                to_archive = []

                if os.path.exists(STATE_FILE):
                    with open(STATE_FILE, 'r', encoding='utf-8') as sf:
                        state_data = json.load(sf)
                    rq = state_data.get("review_queue", [])
                    gmail_jobs = state_data.get("verified_gmail_jobs", [])
                    archived = state_data.setdefault("archived_queue", [])
                    
                    # Find matching items across review_queue and verified_gmail_jobs
                    to_archive = [j for j in rq + gmail_jobs if j.get("url", "").split('?')[0].lower() == u_clean]
                    
                    state_data["review_queue"] = [j for j in rq if j.get("url", "").split('?')[0].lower() != u_clean]
                    state_data["verified_gmail_jobs"] = [j for j in gmail_jobs if j.get("url", "").split('?')[0].lower() != u_clean]
                    
                    for item in to_archive:
                        item["archived_date"] = datetime.now().strftime("%Y-%m-%d")
                        item["archive_reason"] = reason_category
                        item["archive_notes"] = custom_notes
                        archived.append(item)
                        
                    with open(STATE_FILE, 'w', encoding='utf-8') as sf:
                        json.dump(state_data, sf, indent=2)

                # Save reason entry into rejection_rules.json learning database
                REJECTION_RULES_FILE = os.path.join(BASE_DIR, "rejection_rules.json")
                try:
                    if os.path.exists(REJECTION_RULES_FILE):
                        with open(REJECTION_RULES_FILE, 'r', encoding='utf-8') as rf:
                            rr_data = json.load(rf)
                    else:
                        rr_data = {"last_updated": datetime.now().strftime("%Y-%m-%d"), "rejection_reasons": [], "hard_negative_keywords": [], "hard_excluded_locations": []}
                    
                    rr_reasons = rr_data.setdefault("rejection_reasons", [])
                    for item in to_archive:
                        rr_reasons.append({
                            "id": f"REJ-{len(rr_reasons) + 1:03d}",
                            "company": item.get("company_name", item.get("company", "")),
                            "title": item.get("audited_role_title", item.get("title", "")),
                            "url": item.get("url", ""),
                            "reason_category": reason_category,
                            "custom_notes": custom_notes,
                            "timestamp": datetime.now().strftime("%Y-%m-%d")
                        })
                    rr_data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
                    with open(REJECTION_RULES_FILE, 'w', encoding='utf-8') as rf:
                        json.dump(rr_data, rf, indent=2)
                except Exception as rr_err:
                    print(f"[REJECTION RULES SAVE WARNING] {rr_err}")

                subprocess.run([PYTHON_EXE, "sync_dashboard_from_state.py"], cwd=BASE_DIR)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))

        elif self.path == '/api/restore_queue':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                job_url = data.get('url', '').strip()
                u_clean = job_url.split('?')[0].lower() if job_url else ""
                if os.path.exists(STATE_FILE):
                    with open(STATE_FILE, 'r', encoding='utf-8') as sf:
                        state_data = json.load(sf)
                    archived = state_data.get("archived_queue", [])
                    rq = state_data.setdefault("review_queue", [])
                    to_restore = [j for j in archived if j.get("url", "").split('?')[0].lower() == u_clean]
                    state_data["archived_queue"] = [j for j in archived if j.get("url", "").split('?')[0].lower() != u_clean]
                    for item in to_restore:
                        rq.append(item)
                    with open(STATE_FILE, 'w', encoding='utf-8') as sf:
                        json.dump(state_data, sf, indent=2)
                subprocess.run([PYTHON_EXE, "sync_dashboard_from_state.py"], cwd=BASE_DIR)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))

        elif self.path == '/api/delete_queue_permanent':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                job_url = data.get('url', '').strip()
                u_clean = job_url.split('?')[0].lower() if job_url else ""
                if os.path.exists(STATE_FILE):
                    with open(STATE_FILE, 'r', encoding='utf-8') as sf:
                        state_data = json.load(sf)
                    state_data["archived_queue"] = [j for j in state_data.get("archived_queue", []) if j.get("url", "").split('?')[0].lower() != u_clean]
                    state_data["review_queue"] = [j for j in state_data.get("review_queue", []) if j.get("url", "").split('?')[0].lower() != u_clean]
                    with open(STATE_FILE, 'w', encoding='utf-8') as sf:
                        json.dump(state_data, sf, indent=2)
                subprocess.run([PYTHON_EXE, "sync_dashboard_from_state.py"], cwd=BASE_DIR)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))

        elif self.path == '/api/audit_closed_queue':
            try:
                subprocess.run([PYTHON_EXE, "audit_closed_queue_roles.py"], cwd=BASE_DIR)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "message": "Closed queue audit completed successfully."}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))

        elif self.path == '/api/add_queue_url':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                raw_url = data.get('url', '').strip()
                clean_url = raw_url.split('?')[0].strip()

                # Domain fallback guess
                try:
                    domain = urllib.parse.urlparse(clean_url).netloc
                    d_parts = domain.replace('www.', '').split('.')
                    company_name = [p for p in d_parts if p.lower() not in ['jobs','careers','com','net','org','explore','boards','www','hc','sites']][-1].capitalize()
                except Exception:
                    company_name = "Target Company"

                role_title = "Executive Opportunity"
                location_str = "100% Remote / Preferred Hybrid City Hybrid"
                source = "Company Portal"

                if "linkedin.com" in clean_url.lower():
                    source = "LinkedIn"
                elif "indeed.com" in clean_url.lower():
                    source = "Indeed"
                elif "greenhouse.io" in clean_url.lower():
                    source = "Greenhouse"
                elif "lever.co" in clean_url.lower():
                    source = "Lever"
                elif "builtin.com" in clean_url.lower():
                    source = "BuiltIn"

                # Attempt to fetch title via urllib
                try:
                    req = urllib.request.Request(clean_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
                    html_content = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
                    m_title = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
                    if m_title:
                        page_title = m_title.group(1).strip()
                        page_title = re.sub(r'\s+', ' ', page_title)
                        
                        if " hiring " in page_title:
                            parts = page_title.split(" hiring ")
                            company_name = parts[0].strip()
                            rest = parts[1]
                            role_title = rest.split(" in ")[0].split(" | ")[0].strip()
                        elif " | " in page_title:
                            parts = [p.strip() for p in page_title.split("|")]
                            role_title = parts[0]
                            if len(parts) >= 3:
                                location_str = parts[1]
                                company_name = parts[2]
                            elif len(parts) >= 2:
                                company_name = parts[1]
                        elif " - " in page_title:
                            parts = [p.strip() for p in page_title.split("-")]
                            role_title = parts[0]
                            if len(parts) >= 2:
                                company_name = parts[1].split("|")[0].strip()
                        else:
                            role_title = page_title[:60]
                except Exception as fetch_err:
                    print(f"[MANUAL URL FETCH WARNING] {fetch_err}")

                # Build new queue entry
                new_entry = {
                    "company_name": company_name,
                    "audited_role_title": role_title,
                    "title": role_title,
                    "url": clean_url,
                    "source": source,
                    "location": location_str,
                    "added_via": "Manual Candidate Ingestion",
                    "date_added": "2026-08-21"
                }

                if os.path.exists(STATE_FILE):
                    with open(STATE_FILE, 'r', encoding='utf-8') as sf:
                        state_data = json.load(sf)
                    rq = state_data.setdefault("review_queue", [])
                    u_lower = clean_url.lower()
                    if not any(j.get("url", "").split('?')[0].lower() == u_lower for j in rq):
                        rq.insert(0, new_entry)
                        with open(STATE_FILE, 'w', encoding='utf-8') as sf:
                            json.dump(state_data, sf, indent=2)

                subprocess.run([PYTHON_EXE, "sync_dashboard_from_state.py"], cwd=BASE_DIR)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "company": company_name, "title": role_title}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    print(f"Starting Job Search Dashboard API Server on http://localhost:{PORT}...")
    server = ThreadedHTTPServer(('localhost', PORT), DashboardRequestHandler)
    server.serve_forever()
