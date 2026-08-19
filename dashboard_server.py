import json
import os
import subprocess
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

PORT = 5000
BASE_DIR = r"."
STATE_FILE = os.path.join(BASE_DIR, "state.json")
PAYLOAD_FILE = os.path.join(BASE_DIR, "current_payload.json")
PYTHON_EXE = r"C:\Users\{{YOUR_NAME}}\AppData\Local\Python\pythoncore-3.14-64\python.exe"

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

                print(f"\n[SERVER API APPLY TRIGGERED] Company: '{company}' | Title: '{title}' | URL: '{job_url}'")

                # Clean company folder name
                folder_name = re.sub(r'[\\/*?:"<>|]', '', company).strip()
                if not folder_name:
                    folder_name = "Target Company"

                # Construct dynamic application payload
                payload = {
                    "company": company,
                    "folder": folder_name,
                    "role": title,
                    "headline": f"{title.upper()} | GLOBAL DIGITAL EXPERIENCE & AI LEADER",
                    "summary": f"Executive web technology and digital experience leader with 18+ years leading enterprise web strategy, digital product operations, and cross-functional teams. Proven track record turning corporate web channels into high-velocity demand generation and revenue engines. Expert in evaluating emerging AI technologies (Claude Code, ChatGPT, CoPilot, GEO/AEO), modernizing legacy digital architectures, and managing strategic vendor/partner relationships for {company}.",
                    "areas_of_expertise": [
                        ["Enterprise Web Strategy & Architecture: ", "Global Web Operations, CMS Governance ({{HEADLESS_CMS}}, {{ENTERPRISE_CMS}}, WordPress, Drupal), Next-Gen DXP Modernization, Multi-National Site Performance."],
                        ["AI Activation & Digital Innovation: ", "Generative Engine Optimization (GEO/AEO), AI-Assisted Workflows (Claude, ChatGPT, CoPilot), Automated Personalization & Analytics."],
                        ["Conversion Rate Optimization (CRO): ", "High-Velocity A/B Testing Roadmaps, Customer Experience (CX) Architecture, Multi-Site Funnel Velocity, {{ANALYTICS_PLATFORM}} / GTM Data Governance."],
                        ["Executive Leadership & Governance: ", "Cross-Disciplinary Team Management (13+ Dev, DevOps, QA, BA, SEO), ROI & Business Case Governance, Strategic Partner Management."]
                    ],
                    "trend_micro_bullets": [
                        ["Global Web Strategy & Operations Leadership: ", f"Led global web marketing and digital operations for {{MOST_RECENT_COMPANY}}'s enterprise B2B and B2C portfolios, managing a {{TEAM_SIZE_PLACEHOLDER}} (Development, DevOps, QA, BA, SEO) to own the corporate web channel as the primary demand generation and pipeline engine."],
                        ["Next-Gen DXP Discovery & Decision-Making: ", "Led discovery, architectural evaluation, ROI analysis, and executive vendor decision-making for a next-generation Digital Experience Platform (DXP) to replace legacy Adobe Experience Manager ({{ENTERPRISE_CMS}}), aligning C-suite stakeholders around modern API architecture and TCO optimization."],
                        ["TrendAI Redesign & {{HEADLESS_CMS}} CMS Platform Migration: ", "Organized and executed the end-to-end redesign and platform migration of the TrendAI website onto {{HEADLESS_CMS}} CMS, establishing structured content models, modern headless workflows, and rapid publishing cadences."],
                        ["AI-First Innovation & GEO/AEO Integration: ", "Championed AI technologies (Claude, ChatGPT, CoPilot, LLMs) and Generative Engine Optimization (GEO/AEO), driving a 40% increase in brand search presence and a +15% uplift in organic demo/trial conversions."],
                        ["Multi-National Platform Modernization & Performance: ", "Directed enterprise web platform migration across 34 countries and 14 languages, integrating {{MARKETING_AUTOMATION_TOOL}}, {{TAG_MANAGEMENT_TOOL}}, GTM, {{PERFORMANCE_TOOL}}, {{SEARCH_TOOL}}, and {{ANALYTICS_PLATFORM}} to reduce page load times by 40%, boost organic sessions by 10%, and drive 15% pipeline growth."]
                    ],
                    "{{PREVIOUS_COMPANY_2}}_bullets": [
                        ["Digital Product Strategy & Storefront Management: ", "Oversaw end-to-end business management and product lifecycle for mobile app software distributor in {{YOUR_CITY_STATE}}, designing web architecture and checkout funnels for mobile app stores (Sprint) that increased e-commerce checkout conversion rate by +34%."],
                        ["Go-To-Market & Executive Alignment: ", "Executed product strategy across online and on-device stores, defining functional requirements, wireframes, and customer use cases to drive a 30% increase in product-led engagement."]
                    ],
                    "{{PREVIOUS_COMPANY_3}}_bullets": [
                        ["Digital Marketing & Revenue Optimization: ", "Directed corporate e-commerce and web marketing (SEO, SEM, email, marketplaces) at {{PREVIOUS_COMPANY_3}} in {{YOUR_CITY_STATE}}, testing offers and UX flows to sustain 35%+ annual online sales growth."]
                    ],
                    "cover_letter": {
                        "date": "August 12, 2026",
                        "recipient": f"Executive Selection Committee & Leadership Team\n{company}\nCorporate Office / Remote Executive Team",
                        "salutation": f"Dear {company} Selection Committee,",
                        "paragraphs": [
                            f"I am writing to express my strong enthusiasm for the {title} position at {company}. With over 18 years of experience leading enterprise digital strategy, digital transformation roadmaps, technology modernization, and cross-functional technology teams, I connect directly with your mission to build and scale high-performing digital channels.",
                            "Throughout my 18-year tenure as {{YOUR_MOST_RECENT_TITLE}} at {{MOST_RECENT_COMPANY}} ({{MOST_RECENT_EMPLOYMENT_DATES}}), I built a high-performing global organization of 13+ cross-functional specialists (development, DevOps, QA, BA, SEO). I owned our corporate web channel as the primary demand generation engine, directing a 34-country {{ENTERPRISE_CMS}} 6.x migration that reduced page load times by 40% while leading the discovery, ROI evaluation, and decision-making for a next-gen DXP platform to replace legacy {{ENTERPRISE_CMS}}. Additionally, I organized and executed the TrendAI site redesign and migration to {{HEADLESS_CMS}} CMS, while pioneering Generative Engine Optimization (GEO/AEO) strategies that increased search visibility by 40% and lifted organic demo conversions by +15%.",
                            "Prior to {{MOST_RECENT_COMPANY}}, I served as {{YOUR_PREVIOUS_TITLE_1}} at {{PREVIOUS_COMPANY_2}} in {{YOUR_CITY_STATE}}, where I managed digital storefront software development across web and mobile partner channels (Sprint), boosting checkout conversion rates by +34%. My background combines executive digital consulting, deep technical fluency across enterprise MarTech ecosystems, and a proven track record leading cross-disciplinary teams through organizational change.",
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
                        "status": "Submitted",
                        "submission_date": "2026-08-12",
                        "submission_channel": "Direct 1-Click Dashboard Apply",
                        "notes": f"Applied via 1-click dashboard trigger. Master application package generated in P:\\Job Search\\{folder_name}\\"
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
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    import re
    print(f"Starting Job Search Dashboard API Server on http://localhost:{PORT}...")
    server = ThreadedHTTPServer(('localhost', PORT), DashboardRequestHandler)
    server.serve_forever()
