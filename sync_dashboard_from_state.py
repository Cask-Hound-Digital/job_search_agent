import json
import os
import shutil
from datetime import datetime

STATE_FILE = r".\state.json"
INDEX_FILE = r".\index.html"
PRIMARY_DASHBOARD = r"P:\Job Search\dashboard.html"
SECONDARY_DASHBOARD = r"P:\Projects\job-search-consultant\Job Search\dashboard.html"

def sync_dashboard():
    if not os.path.exists(STATE_FILE):
        print(f"Error: {STATE_FILE} not found.")
        return

    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)

    apps = state.get("applications", [])
    gmail_jobs = state.get("verified_gmail_jobs", [])
    review_queue = state.get("review_queue", [])
    archived_queue = state.get("archived_queue", [])

    # Normalize historical "Submitted" statuses to "Applied"
    for a in apps:
        if a.get("status") == "Submitted":
            a["status"] = "Applied"

    # Combine review queue sources
    queue_source_map = {}
    for r in review_queue:
        url = r.get("url", "").strip().split('?')[0].lower()
        if url:
            queue_source_map[url] = r

    for g in gmail_jobs:
        url = g.get("url", "").strip().split('?')[0].lower()
        if url and url not in queue_source_map:
            queue_source_map[url] = g

    # Filter out URLs already in applications
    app_urls = {a.get("job_url", "").strip().split('?')[0].lower() for a in apps if a.get("job_url")}
    
    unique_queue = []
    seen_urls = set()

    for url_clean, g in queue_source_map.items():
        if not url_clean or url_clean in app_urls or url_clean in seen_urls:
            continue
        seen_urls.add(url_clean)
        
        title = g.get("title", "").strip()
        if not title or "unsubscribe" in title.lower() or "privacy policy" in title.lower():
            continue

        unique_queue.append(g)

    # Compute status counts and stale applications (> 28 days)
    today = datetime.strptime("2026-08-21", "%Y-%m-%d")

    status_counts = {
        "all": len(apps),
        "Applied": 0,
        "Interviewing": 0,
        "Negotiating": 0,
        "I Withdrew": 0,
        "Not Selected": 0,
        "No Response": 0,
        "Archived": 0
    }

    stale_count = 0

    for a in apps:
        st = a.get("status", "Applied")
        if st == "Submitted": st = "Applied"
        if st in status_counts:
            status_counts[st] += 1
        else:
            status_counts["Applied"] += 1

        # Check date for 4-week alert (> 28 days)
        sub_date_str = a.get("submission_date", "2026-08-12")
        try:
            sub_date = datetime.strptime(sub_date_str, "%Y-%m-%d")
            days_elapsed = (today - sub_date).days
            if days_elapsed >= 28 and st in ["Applied", "Interviewing"]:
                stale_count += 1
                a["is_stale"] = True
                a["days_elapsed"] = days_elapsed
            else:
                a["is_stale"] = False
                a["days_elapsed"] = days_elapsed
        except Exception:
            a["is_stale"] = False
            a["days_elapsed"] = 0

    # Pass serialized JSON apps for dynamic client modal lookups
    apps_json_str = json.dumps(apps).replace("'", "&#39;")

    print(f"Found {len(apps)} applications ({status_counts['Applied']} Applied), {stale_count} 4-week stale alerts, {len(unique_queue)} review queue roles, and {len(archived_queue)} archived roles.")

    # Generate HTML content
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Executive Job Search Dashboard | {{YOUR_FULL_NAME}}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-dark: #090d16;
      --panel-bg: rgba(18, 26, 43, 0.75);
      --panel-border: rgba(255, 255, 255, 0.08);
      --accent-navy: #1b365d;
      --accent-blue: #38bdf8;
      --accent-cyan: #22d3ee;
      --accent-green: #4ade80;
      --accent-purple: #c084fc;
      --accent-amber: #fbbf24;
      --accent-rose: #f43f5e;
      --text-muted: #94a3b8;
      --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: 'Inter', sans-serif;
      background-color: var(--bg-dark);
      background-image: 
        radial-gradient(at 0% 0%, rgba(27, 54, 93, 0.3) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(56, 189, 248, 0.15) 0px, transparent 50%);
      background-attachment: fixed;
      color: #f8fafc;
      min-height: 100vh;
      padding: 2rem;
      line-height: 1.5;
    }}

    .container {{ max-width: 1440px; margin: 0 auto; }}

    header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
      padding-bottom: 1.5rem;
      border-bottom: 1px solid var(--panel-border);
      flex-wrap: wrap;
      gap: 1rem;
    }}

    .brand-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 2rem;
      font-weight: 800;
      background: linear-gradient(135deg, #ffffff 0%, #38bdf8 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      letter-spacing: -0.02em;
    }}

    .brand-subtitle {{ color: var(--text-muted); font-size: 0.95rem; margin-top: 0.25rem; }}

    .header-badge {{
      background: rgba(56, 189, 248, 0.1);
      border: 1px solid rgba(56, 189, 248, 0.3);
      color: var(--accent-blue);
      padding: 0.5rem 1rem;
      border-radius: 9999px;
      font-size: 0.85rem;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .status-dot {{
      width: 8px; height: 8px;
      background-color: var(--accent-green);
      border-radius: 50%;
      box-shadow: 0 0 10px var(--accent-green);
    }}

    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1.25rem;
      margin-bottom: 2rem;
    }}

    .kpi-card {{
      background: var(--panel-bg);
      backdrop-filter: blur(16px);
      border: 1px solid var(--panel-border);
      border-radius: 1rem;
      padding: 1.25rem;
      box-shadow: var(--glass-shadow);
    }}

    .kpi-label {{ color: var(--text-muted); font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }}
    .kpi-value {{ font-family: 'Outfit', sans-serif; font-size: 2.1rem; font-weight: 700; margin: 0.3rem 0; }}
    .kpi-subtext {{ color: var(--text-muted); font-size: 0.8rem; }}

    .controls-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
      flex-wrap: wrap;
      gap: 1rem;
    }}

    .tabs-group {{
      display: flex;
      background: var(--panel-bg);
      border: 1px solid var(--panel-border);
      padding: 0.35rem;
      border-radius: 0.85rem;
      gap: 0.35rem;
      flex-wrap: wrap;
    }}

    .tab-btn {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 0.45rem 0.9rem;
      font-size: 0.82rem;
      font-weight: 600;
      border-radius: 0.5rem;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .tab-btn.active {{
      background: var(--accent-navy);
      color: #ffffff;
      box-shadow: 0 4px 12px rgba(27, 54, 93, 0.4);
    }}

    .search-box {{
      background: var(--panel-bg);
      border: 1px solid var(--panel-border);
      border-radius: 0.75rem;
      padding: 0.5rem 1rem;
      color: #ffffff;
      font-size: 0.9rem;
      width: 280px;
      outline: none;
    }}

    .search-box:focus {{ border-color: var(--accent-blue); }}

    .panel-container {{
      background: var(--panel-bg);
      backdrop-filter: blur(16px);
      border: 1px solid var(--panel-border);
      border-radius: 1.25rem;
      padding: 1.5rem;
      box-shadow: var(--glass-shadow);
      margin-bottom: 2.5rem;
    }}

    .section-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 1.35rem;
      font-weight: 700;
      margin-bottom: 1.25rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 0.75rem;
    }}

    .section-badge {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--panel-border);
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.8rem;
      color: var(--accent-blue);
      font-weight: 600;
    }}

    .custom-table {{ width: 100%; border-collapse: collapse; margin-top: 0.5rem; }}
    .custom-table th {{ text-align: left; padding: 0.85rem 1rem; color: var(--text-muted); font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--panel-border); }}
    .custom-table td {{ padding: 1rem; border-bottom: 1px solid var(--panel-border); font-size: 0.9rem; vertical-align: middle; }}
    
    .app-row {{ cursor: pointer; transition: background 0.2s ease; }}
    .app-row:hover {{ background: rgba(255, 255, 255, 0.03); }}

    .company-name {{ font-weight: 700; font-size: 1rem; color: #ffffff; }}
    .role-title {{ color: var(--accent-cyan); font-size: 0.9rem; font-weight: 600; }}

    /* Source Badges */
    .source-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      padding: 0.25rem 0.6rem;
      border-radius: 0.35rem;
      font-size: 0.78rem;
      font-weight: 700;
    }}
    .src-linkedin {{ background: rgba(10, 102, 194, 0.2); border: 1px solid #0a66c2; color: #38bdf8; }}
    .src-indeed {{ background: rgba(33, 100, 243, 0.2); border: 1px solid #2164f3; color: #60a5fa; }}
    .src-greenhouse {{ background: rgba(36, 161, 108, 0.2); border: 1px solid #24a16c; color: #4ade80; }}
    .src-lever {{ background: rgba(255, 122, 89, 0.2); border: 1px solid #ff7a59; color: #fb923c; }}
    .src-default {{ background: rgba(148, 163, 184, 0.2); border: 1px solid #94a3b8; color: #cbd5e1; }}

    /* 4-Week Stale Alert Badge */
    .stale-alert-badge {{
      background: rgba(251, 191, 36, 0.15);
      border: 1px solid var(--accent-amber);
      color: var(--accent-amber);
      padding: 0.25rem 0.6rem;
      border-radius: 0.35rem;
      font-size: 0.75rem;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      margin-top: 0.35rem;
    }}

    /* Status Selector Dropdown */
    .status-select {{
      background: rgba(15, 23, 42, 0.9);
      border: 1px solid var(--panel-border);
      color: #ffffff;
      padding: 0.35rem 0.65rem;
      border-radius: 0.5rem;
      font-size: 0.82rem;
      font-weight: 600;
      outline: none;
      cursor: pointer;
    }}
    .status-select:focus {{ border-color: var(--accent-blue); }}

    .match-score {{ font-family: 'Outfit', sans-serif; font-weight: 700; color: var(--accent-purple); }}

    .btn-link {{
      color: var(--accent-blue);
      text-decoration: none;
      font-size: 0.82rem;
      font-weight: 600;
      margin-right: 0.5rem;
    }}
    .btn-link:hover {{ text-decoration: underline; }}

    .btn-no-response {{
      background: transparent;
      border: 1px solid var(--accent-amber);
      color: var(--accent-amber);
      padding: 0.25rem 0.5rem;
      border-radius: 0.35rem;
      font-size: 0.75rem;
      cursor: pointer;
      margin-top: 0.25rem;
    }}
    .btn-no-response:hover {{ background: rgba(251, 191, 36, 0.2); }}

    .queue-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 1.25rem;
    }}

    .queue-card {{
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--panel-border);
      border-radius: 0.85rem;
      padding: 1.25rem;
      position: relative;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .queue-card:hover {{
      border-color: var(--accent-blue);
      transform: translateY(-2px);
    }}

    .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; }}

    .btn-archive {{
      background: transparent;
      border: 1px solid var(--panel-border);
      color: var(--text-muted);
      padding: 0.3rem 0.6rem;
      border-radius: 0.4rem;
      font-size: 0.78rem;
      cursor: pointer;
      transition: all 0.2s ease;
    }}
    .btn-archive:hover {{ background: rgba(244, 63, 94, 0.15); color: var(--accent-rose); border-color: var(--accent-rose); }}

    .btn-restore {{
      background: transparent;
      border: 1px solid var(--accent-green);
      color: var(--accent-green);
      padding: 0.3rem 0.6rem;
      border-radius: 0.4rem;
      font-size: 0.78rem;
      cursor: pointer;
      margin-right: 0.5rem;
    }}
    .btn-restore:hover {{ background: rgba(74, 222, 128, 0.15); }}

    .btn-delete-perm {{
      background: transparent;
      border: 1px solid var(--accent-rose);
      color: var(--accent-rose);
      padding: 0.3rem 0.6rem;
      border-radius: 0.4rem;
      font-size: 0.78rem;
      cursor: pointer;
    }}
    .btn-delete-perm:hover {{ background: rgba(244, 63, 94, 0.2); }}

    /* Modal Backdrop & Content */
    .modal-backdrop {{
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(10, 15, 29, 0.85);
      backdrop-filter: blur(8px);
      z-index: 9999;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .modal-content {{
      background: #0f172a;
      border: 1px solid var(--panel-border);
      border-radius: 1rem;
      width: 92%;
      max-width: 800px;
      max-height: 90vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
      color: #ffffff;
    }}
    .modal-header {{
      padding: 1.25rem 1.5rem;
      border-bottom: 1px solid var(--panel-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .modal-body {{ padding: 1.5rem; overflow-y: auto; flex: 1; }}

    .modal-tabs {{
      display: flex;
      gap: 0.5rem;
      border-bottom: 1px solid var(--panel-border);
      margin-bottom: 1.25rem;
    }}
    .modal-tab-btn {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 0.5rem 1rem;
      font-size: 0.9rem;
      font-weight: 600;
      border-bottom: 2px solid transparent;
      cursor: pointer;
    }}
    .modal-tab-btn.active {{
      color: var(--accent-blue);
      border-bottom-color: var(--accent-blue);
    }}

    .form-group {{ margin-bottom: 1rem; }}
    .form-label {{ display: block; font-size: 0.82rem; font-weight: 600; color: var(--text-muted); margin-bottom: 0.35rem; }}
    .form-input, .form-select, .form-textarea {{
      width: 100%;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--panel-border);
      border-radius: 0.5rem;
      padding: 0.55rem 0.85rem;
      color: #ffffff;
      font-size: 0.88rem;
      outline: none;
    }}
    .form-input:focus, .form-select:focus, .form-textarea:focus {{ border-color: var(--accent-blue); }}
    .form-textarea {{ min-height: 90px; resize: vertical; }}

    .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }}
    .grid-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; }}

    .interview-card {{
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--panel-border);
      border-radius: 0.75rem;
      padding: 1rem;
      margin-bottom: 1rem;
    }}
    .interview-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }}

    footer {{
      text-align: center;
      color: var(--text-muted);
      font-size: 0.85rem;
      padding: 2rem 0;
      border-top: 1px solid var(--panel-border);
    }}
  </style>
</head>
<body>

  <div class="container">
    <header>
      <div>
        <h1 class="brand-title">Executive Job Search Dashboard</h1>
        <p class="brand-subtitle">Candidate: {{YOUR_FULL_NAME}} | Target Compensation: {{TARGET_COMPENSATION_MIN}} | Preferred Hybrid City & Remote</p>
      </div>
      <div class="header-badge">
        <span class="status-dot"></span> Active Search Engine Running (Verified Live Target URLs)
      </div>
    </header>

    <!-- KPI Summary Cards -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Applied Opportunities</div>
        <div class="kpi-value" style="color: var(--accent-green);">{status_counts["Applied"]}</div>
        <div class="kpi-subtext">Company Portals & 1-Click Package Builds</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Interviewing Stage</div>
        <div class="kpi-value" style="color: var(--accent-cyan);">{status_counts["Interviewing"]}</div>
        <div class="kpi-subtext">Active Recruiter & Executive Panels</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">4-Week Follow-Up Alerts</div>
        <div class="kpi-value" style="color: var(--accent-amber);">{stale_count}</div>
        <div class="kpi-subtext">Applied &gt;28 Days Ago — Action Required</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Verified Review Queue</div>
        <div class="kpi-value" style="color: var(--accent-purple);" id="queueBadge">{len(unique_queue)}</div>
        <div class="kpi-subtext">Extracted from Live Email Alerts & Sweeps</div>
      </div>
    </div>

    <!-- Controls & Status Filter Bar -->
    <div class="controls-bar">
      <div class="tabs-group">
        <button class="tab-btn active" onclick="filterTab('all', this)">All Roles ({len(apps)})</button>
        <button class="tab-btn" onclick="filterTab('applied', this)">Applied ({status_counts['Applied']})</button>
        <button class="tab-btn" onclick="filterTab('interviewing', this)">Interviewing ({status_counts['Interviewing']})</button>
        <button class="tab-btn" onclick="filterTab('negotiating', this)">Negotiating ({status_counts['Negotiating']})</button>
        <button class="tab-btn" onclick="filterTab('i withdrew', this)">Withdrew ({status_counts['I Withdrew']})</button>
        <button class="tab-btn" onclick="filterTab('not selected', this)">Not Selected ({status_counts['Not Selected']})</button>
        <button class="tab-btn" onclick="filterTab('no response', this)">No Response ({status_counts['No Response']})</button>
        <button class="tab-btn" onclick="filterTab('archived', this)">Archived ({status_counts['Archived']})</button>
      </div>
      <input type="text" id="searchInput" class="search-box" placeholder="Search company, title, source..." onkeyup="filterSearch()">
    </div>

    <!-- Active Applications Table -->
    <div class="panel-container">
      <div class="section-title">
        <span>Active Applications & Lifecycle Summary</span>
        <span class="section-badge" id="roleCount">{len(apps)} Roles Showing</span>
      </div>
      
      <div style="overflow-x: auto;">
        <table class="custom-table" id="appTable">
          <thead>
            <tr>
              <th>Company & Role</th>
              <th>Source</th>
              <th>Lifecycle Status</th>
              <th>Location & Comp</th>
              <th>Match</th>
              <th>Applied Date</th>
              <th>Actions & Details</th>
            </tr>
          </thead>
          <tbody>
"""

    for a in apps:
        app_id = a.get("id", "JOB-00")
        co = a.get("company_name", "Enterprise Leader")
        title = a.get("job_title", "Director Role")
        loc = a.get("location", "Remote")
        comp = a.get("compensation_range", "{{TARGET_COMPENSATION_MIN}}")
        match = a.get("match_score", 98)
        date = a.get("submission_date", "2026-08-12")
        url = a.get("job_url", "")
        status = a.get("status", "Applied")
        if status == "Submitted": status = "Applied"
        source = a.get("source", "LinkedIn")
        is_stale = a.get("is_stale", False)
        days_elapsed = a.get("days_elapsed", 0)
        
        folder_name = co.replace(' ', '%20').replace('.', '')
        
        # Source badge styling
        src_class = "src-default"
        if "linkedin" in source.lower(): src_class = "src-linkedin"
        elif "indeed" in source.lower(): src_class = "src-indeed"
        elif "greenhouse" in source.lower(): src_class = "src-greenhouse"
        elif "lever" in source.lower(): src_class = "src-lever"

        url_btn = f'<a href="{url}" class="btn-link" target="_blank" onclick="event.stopPropagation()">🔗 Job Posting</a>' if url else ''
        folder_btn = f'<a href="file:///P:/Job%20Search/{folder_name}/" class="btn-link" target="_blank" onclick="event.stopPropagation()">📁 Package Folder</a>'

        stale_html = ""
        if is_stale:
            stale_html = f"""
            <div class="stale-alert-badge">
              ⚠️ 4+ Weeks ({days_elapsed}d) — Follow Up Needed
            </div>
            <div>
              <button class="btn-no-response" onclick="event.stopPropagation(); updateJobStatus('{app_id}', 'No Response')">{{YOUR_NAME}} No Response</button>
            </div>
            """

        status_options = ["Applied", "Interviewing", "Negotiating", "I Withdrew", "Not Selected", "No Response", "Archived"]
        select_html = f'<select class="status-select" onclick="event.stopPropagation()" onchange="updateJobStatus(\'{app_id}\', this.value)">'
        for opt in status_options:
            sel = "selected" if opt.lower() == status.lower() else ""
            select_html += f'<option value="{opt}" {sel}>{opt}</option>'
        select_html += '</select>'

        html += f"""
            <tr data-status="{status.lower()}" class="app-row" onclick="openJobDetailModal('{app_id}')">
              <td>
                <div class="company-name">{co}</div>
                <div class="role-title">{title}</div>
                {stale_html}
              </td>
              <td><span class="source-badge {src_class}">{source}</span></td>
              <td>{select_html}</td>
              <td><div>{loc}</div><div style="font-size:0.78rem; color:var(--text-muted);">{comp}</div></td>
              <td><span class="match-score">{match}%</span></td>
              <td>{date}</td>
              <td>
                {url_btn}
                {folder_btn}
              </td>
            </tr>
"""

    html += f"""
          </tbody>
        </table>
      </div>
    </div>

    <!-- Verified Email Review Queue -->
    <div class="panel-container">
      <div class="section-title">
        <span>Verified Review Queue</span>
        <span class="section-badge" id="queueCountBadge">{len(unique_queue)} Opportunities</span>
      </div>

      <div class="queue-grid" id="queueContainer">
"""

    for idx, item in enumerate(unique_queue):
        card_id = f"card-gen-{idx}"
        co = item.get("company_name", item.get("company", "Verified Company")).strip()
        title = item.get("audited_role_title", item.get("title", "Executive Opportunity")).strip()
        url = item.get("url", "#")
        source = item.get("source", "LinkedIn")
        
        src_class = "src-default"
        if "linkedin" in source.lower(): src_class = "src-linkedin"
        elif "indeed" in source.lower(): src_class = "src-indeed"

        html += f"""
        <div class="queue-card" id="{card_id}">
          <div class="card-header">
            <div>
              <div class="company-name">{co}</div>
              <div class="role-title">{title}</div>
            </div>
            <span class="source-badge {src_class}">{source}</span>
          </div>
          <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 1rem;">Verified Executive Opportunity</div>
          <div style="display: flex; gap: 0.5rem; justify-content: space-between; align-items: center;">
            <a href="{url}" class="btn-link" target="_blank">🔗 View Posting</a>
            <div style="display: flex; gap: 0.4rem;">
              <button class="btn-archive" onclick="archiveQueueJob('{url}')">📦 Archive</button>
              <button class="btn-apply" id="btn-apply-{card_id}" onclick="triggerApply('{card_id}', '{co.replace("'", "\\'")}', '{title.replace("'", "\\'")}', '{url}')">⚡ Apply & Build Package</button>
            </div>
          </div>
        </div>
"""

    html += f"""
      </div>
    </div>

    <!-- Archived Opportunities Queue -->
    <div class="panel-container">
      <div class="section-title">
        <span>Archived Queue ({len(archived_queue)} Items)</span>
        <span class="section-badge">Archived Opportunities</span>
      </div>
      <div class="queue-grid">
"""

    for item in archived_queue:
        co = item.get("company_name", item.get("company", "Archived Company")).strip()
        title = item.get("audited_role_title", item.get("title", "Executive Role")).strip()
        url = item.get("url", "#")
        source = item.get("source", "LinkedIn")
        arch_date = item.get("archived_date", "2026-08-21")
        
        html += f"""
        <div class="queue-card">
          <div class="card-header">
            <div>
              <div class="company-name">{co}</div>
              <div class="role-title">{title}</div>
            </div>
            <span class="source-badge src-default">{source}</span>
          </div>
          <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.75rem;">Archived on {arch_date}</div>
          <div style="display: flex; gap: 0.5rem; justify-content: space-between; align-items: center;">
            <a href="{url}" class="btn-link" target="_blank">🔗 View Posting</a>
            <div style="display: flex; gap: 0.4rem;">
              <button class="btn-restore" onclick="restoreQueueJob('{url}')">↩️ Restore</button>
              <button class="btn-delete-perm" onclick="deleteQueuePermanent('{url}')">🗑️ Delete</button>
            </div>
          </div>
        </div>
"""

    html += f"""
      </div>
    </div>

    <footer>
      <p>Job Search Agent System | Candidate: {{YOUR_FULL_NAME}} | Export Storage: P:\\Job Search\\</p>
    </footer>
  </div>

  <!-- Candidate Skill Verification Modal -->
  <div id="skillVerificationModal" class="modal-backdrop" style="display: none;">
    <div class="modal-content">
      <div class="modal-header">
        <div>
          <h2 class="modal-title">🛡️ Candidate Skill Verification Required</h2>
          <p class="modal-subtitle" id="modalSubTitle">Verify targeted skills before generating resume package</p>
        </div>
        <button class="modal-close-btn" onclick="closeSkillModal()">✕</button>
      </div>
      <div class="modal-body">
        <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem;">
          To ensure your resume reflects 100% genuine candidate experience without automated keyword stuffing, please review the skills targeted for this role:
        </p>
        <div id="skillChecklist" class="skill-checklist"></div>
      </div>
      <div style="padding:1rem 1.5rem; border-top:1px solid var(--panel-border); display:flex; justify-content:flex-end; gap:0.75rem;">
        <button class="btn-secondary" onclick="closeSkillModal()">Cancel</button>
        <button class="btn-primary" id="btnConfirmBuild" onclick="confirmSkillAndBuild()">⚡ Confirm Selected & Build Package</button>
      </div>
    </div>
  </div>

  <!-- Job Detail & Interview Tracker Modal -->
  <div id="jobDetailModal" class="modal-backdrop" style="display: none;">
    <div class="modal-content" style="max-width: 840px;">
      <div class="modal-header">
        <div>
          <h2 class="modal-title" id="detailModalCompanyRole">Company — Role</h2>
          <p class="modal-subtitle" id="detailModalMeta">Location | Compensation | Match Score</p>
        </div>
        <button class="modal-close-btn" onclick="closeJobDetailModal()">✕</button>
      </div>
      <div class="modal-body">
        
        <div class="modal-tabs">
          <button class="modal-tab-btn active" id="tabBtnOverview" onclick="switchDetailTab('overview')">Overview & Package</button>
          <button class="modal-tab-btn" id="tabBtnApplied" onclick="switchDetailTab('applied')">Applied & Follow-Ups</button>
          <button class="modal-tab-btn" id="tabBtnInterviewing" onclick="switchDetailTab('interviewing')">Interviewing Schedule</button>
        </div>

        <!-- Tab 1: Overview -->
        <div id="tabContentOverview">
          <div class="grid-2" style="margin-bottom: 1rem;">
            <div>
              <span class="form-label">Job Source</span>
              <span id="detailSourceBadge" class="source-badge src-default">LinkedIn</span>
            </div>
            <div>
              <span class="form-label">Submission Date</span>
              <div id="detailSubmissionDate" style="font-weight: 600;">2026-08-12</div>
            </div>
          </div>

          <div style="margin-bottom: 1.5rem;">
            <span class="form-label">Master Application Packages (P:\\Job Search\\)</span>
            <div id="detailPackageLinks" style="margin-top: 0.5rem; display: flex; gap: 0.75rem; flex-wrap: wrap;"></div>
          </div>
        </div>

        <!-- Tab 2: Applied Tab -->
        <div id="tabContentApplied" style="display: none;">
          <div class="form-group">
            <label class="form-label">General Application Notes</label>
            <textarea id="appNotesTextarea" class="form-textarea" placeholder="Add notes about referral contact, application submission details, custom questions..."></textarea>
          </div>

          <div style="margin-top: 1.5rem;">
            <h4 style="font-size: 1rem; font-weight: 700; margin-bottom: 0.75rem;">Post-Application Follow-Up Tracker</h4>
            <div class="grid-2" style="margin-bottom: 0.75rem;">
              <div>
                <label class="form-label">Next Follow-Up Date</label>
                <input type="date" id="appFollowupDate" class="form-input" />
              </div>
              <div>
                <label class="form-label">Follow-Up Action / Notes</label>
                <input type="text" id="appFollowupNotes" class="form-input" placeholder="e.g. Sent check-in email to hiring manager / Recruiter ping" />
              </div>
            </div>
            <button class="btn-primary" style="font-size: 0.85rem; padding: 0.4rem 0.85rem;" onclick="saveAppliedTabDetails()">💾 Save Applied Notes & Follow-Up</button>
          </div>
        </div>

        <!-- Tab 3: Interviewing Tab -->
        <div id="tabContentInterviewing" style="display: none;">
          <div id="interviewRoundsList"></div>

          <div style="border-top: 1px solid var(--panel-border); padding-top: 1.25rem; margin-top: 1.25rem;">
            <h4 style="font-size: 1rem; font-weight: 700; margin-bottom: 0.85rem;" id="interviewFormTitle">➕ Add Interview Round</h4>
            
            <input type="hidden" id="editingInterviewId" value="" />

            <div class="grid-3" style="margin-bottom: 0.75rem;">
              <div>
                <label class="form-label">Interview Date</label>
                <input type="date" id="intDate" class="form-input" />
              </div>
              <div>
                <label class="form-label">Type</label>
                <select id="intType" class="form-select">
                  <option value="Initial Screen">Initial Screen</option>
                  <option value="Technical">Technical</option>
                  <option value="Work Culture">Work Culture</option>
                  <option value="Panel">Panel</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div>
                <label class="form-label">Format</label>
                <select id="intFormat" class="form-select">
                  <option value="Video">Video</option>
                  <option value="Phone">Phone</option>
                  <option value="In Person">In Person</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>

            <div class="grid-2" style="margin-bottom: 0.75rem;">
              <div>
                <label class="form-label">Interviewer Name</label>
                <input type="text" id="intName" class="form-input" placeholder="e.g. Jane Doe" />
              </div>
              <div>
                <label class="form-label">Interviewer Title</label>
                <input type="text" id="intTitle" class="form-input" placeholder="e.g. VP of Engineering" />
              </div>
            </div>

            <div class="grid-2" style="margin-bottom: 0.75rem;">
              <div>
                <label class="form-label">Interviewer Email</label>
                <input type="email" id="intEmail" class="form-input" placeholder="e.g. jane@company.com" />
              </div>
              <div>
                <label class="form-label">Interviewer Phone</label>
                <input type="tel" id="intPhone" class="form-input" placeholder="e.g. (555) 123-4567" />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Interview Discussion Notes</label>
              <textarea id="intNotes" class="form-textarea" placeholder="Key topics covered, questions asked, technical takeaways..."></textarea>
            </div>

            <div class="grid-2" style="margin-bottom: 1rem;">
              <div>
                <label class="form-label">Post-Interview Follow-Up Date</label>
                <input type="date" id="intFollowupDate" class="form-input" />
              </div>
              <div>
                <label class="form-label">Post-Interview Follow-Up Notes</label>
                <input type="text" id="intFollowupNotes" class="form-input" placeholder="e.g. Sent thank-you email / Recruiter status check date" />
              </div>
            </div>

            <button class="btn-primary" onclick="saveInterviewRound()">💾 Save Interview Round</button>
          </div>
        </div>

      </div>
    </div>
  </div>

  <script>
    const APPS_DATA = {apps_json_str};
    let currentFilter = 'all';
    let currentAppDetailId = null;

    function filterTab(status, btnElement) {{
      currentFilter = status.toLowerCase();
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
      if (btnElement) btnElement.classList.add('active');
      filterSearch();
    }}

    function filterSearch() {{
      const query = document.getElementById('searchInput').value.toLowerCase();
      const rows = document.querySelectorAll('.app-row');
      let visibleCount = 0;

      rows.forEach(row => {{
        let rowStatus = (row.getAttribute('data-status') || '').toLowerCase().trim();
        if (rowStatus === 'submitted') rowStatus = 'applied';
        const text = row.innerText.toLowerCase();

        const matchesTab = (currentFilter === 'all') || (rowStatus === currentFilter);
        const matchesSearch = text.includes(query);

        if (matchesTab && matchesSearch) {{
          row.style.display = '';
          visibleCount++;
        }} else {{
          row.style.display = 'none';
        }}
      }});

      document.getElementById('roleCount').innerText = `${{visibleCount}} Roles Showing`;
    }}

    async function updateJobStatus(appId, newStatus) {{
      try {{
        const res = await fetch('http://localhost:5000/api/update_status', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ id: appId, status: newStatus }})
        }});
        const data = await res.json();
        if (data.status === 'success') {{
          showToast(`✅ Status updated to <strong>${{newStatus}}</strong>`);
          setTimeout(() => window.location.reload(), 1000);
        }}
      }} catch (err) {{
        showToast('❌ Failed to update status.');
      }}
    }}

    async function archiveQueueJob(jobUrl) {{
      try {{
        const res = await fetch('http://localhost:5000/api/archive_queue', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ url: jobUrl }})
        }});
        const data = await res.json();
        if (data.status === 'success') {{
          showToast('📦 Opportunity archived.');
          setTimeout(() => window.location.reload(), 1000);
        }}
      }} catch (err) {{
        showToast('❌ Error archiving job.');
      }}
    }}

    async function restoreQueueJob(jobUrl) {{
      try {{
        const res = await fetch('http://localhost:5000/api/restore_queue', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ url: jobUrl }})
        }});
        const data = await res.json();
        if (data.status === 'success') {{
          showToast('↩️ Restored to active queue.');
          setTimeout(() => window.location.reload(), 1000);
        }}
      }} catch (err) {{
        showToast('❌ Error restoring job.');
      }}
    }}

    async function deleteQueuePermanent(jobUrl) {{
      if (!confirm('Are you sure you want to permanently delete this job from the archive?')) return;
      try {{
        const res = await fetch('http://localhost:5000/api/delete_queue_permanent', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ url: jobUrl }})
        }});
        const data = await res.json();
        if (data.status === 'success') {{
          showToast('🗑️ Job permanently deleted.');
          setTimeout(() => window.location.reload(), 1000);
        }}
      }} catch (err) {{
        showToast('❌ Error deleting job.');
      }}
    }}

    function openJobDetailModal(appId) {{
      const app = APPS_DATA.find(a => a.id === appId);
      if (!app) return;
      currentAppDetailId = appId;

      document.getElementById('detailModalCompanyRole').innerText = `${{app.company_name}} — ${{app.job_title}}`;
      document.getElementById('detailModalMeta').innerText = `${{app.location}} | ${{app.compensation_range}} | Match: ${{app.match_score}}%`;
      document.getElementById('detailSourceBadge').innerText = app.source || 'LinkedIn';
      document.getElementById('detailSubmissionDate').innerText = app.submission_date || '2026-08-12';

      const folderName = app.company_name.replace(/ /g, '%20').replace(/\\./g, '');
      const linksContainer = document.getElementById('detailPackageLinks');
      linksContainer.innerHTML = `
        <a href="file:///P:/Job%20Search/${{folderName}}/" class="btn-link" target="_blank">📁 Open Package Folder</a>
        <a href="${{app.job_url}}" class="btn-link" target="_blank">🔗 Original Job Posting</a>
      `;

      // Fill Applied tab
      document.getElementById('appNotesTextarea').value = app.application_notes || '';
      const followups = app.application_followups || [];
      if (followups.length > 0) {{
        document.getElementById('appFollowupDate').value = followups[0].date || '';
        document.getElementById('appFollowupNotes').value = followups[0].notes || '';
      }} else {{
        document.getElementById('appFollowupDate').value = '';
        document.getElementById('appFollowupNotes').value = '';
      }}

      // Fill Interviewing tab
      renderInterviewRoundsList(app.interviews || []);
      resetInterviewForm();

      switchDetailTab('overview');
      document.getElementById('jobDetailModal').style.display = 'flex';
    }}

    function closeJobDetailModal() {{
      document.getElementById('jobDetailModal').style.display = 'none';
      currentAppDetailId = null;
    }}

    function switchDetailTab(tabName) {{
      document.querySelectorAll('.modal-tab-btn').forEach(btn => btn.classList.remove('active'));
      document.getElementById('tabContentOverview').style.display = 'none';
      document.getElementById('tabContentApplied').style.display = 'none';
      document.getElementById('tabContentInterviewing').style.display = 'none';

      if (tabName === 'overview') {{
        document.getElementById('tabBtnOverview').classList.add('active');
        document.getElementById('tabContentOverview').style.display = 'block';
      }} else if (tabName === 'applied') {{
        document.getElementById('tabBtnApplied').classList.add('active');
        document.getElementById('tabContentApplied').style.display = 'block';
      }} else if (tabName === 'interviewing') {{
        document.getElementById('tabBtnInterviewing').classList.add('active');
        document.getElementById('tabContentInterviewing').style.display = 'block';
      }}
    }}

    async function saveAppliedTabDetails() {{
      if (!currentAppDetailId) return;
      const notes = document.getElementById('appNotesTextarea').value;
      const fDate = document.getElementById('appFollowupDate').value;
      const fNotes = document.getElementById('appFollowupNotes').value;

      const followups = fDate ? [{{ id: 'FUP-01', date: fDate, notes: fNotes }}] : [];

      try {{
        const res = await fetch('http://localhost:5000/api/save_application_details', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ id: currentAppDetailId, application_notes: notes, application_followups: followups }})
        }});
        const data = await res.json();
        if (data.status === 'success') {{
          showToast('💾 Application notes & follow-up saved.');
        }}
      }} catch (err) {{
        showToast('❌ Error saving application details.');
      }}
    }}

    function renderInterviewRoundsList(interviews) {{
      const container = document.getElementById('interviewRoundsList');
      container.innerHTML = '';
      if (interviews.length === 0) {{
        container.innerHTML = '<p style="color:var(--text-muted); font-size:0.9rem; margin-bottom:1rem;">No interview rounds scheduled yet.</p>';
        return;
      }}

      interviews.forEach((item, idx) => {{
        const card = document.createElement('div');
        card.className = 'interview-card';
        card.innerHTML = `
          <div class="interview-header">
            <div>
              <strong style="color:var(--accent-cyan); font-size:0.95rem;">Round ${{idx + 1}}: ${{item.type}} (${{item.format}})</strong>
              <div style="font-size:0.8rem; color:var(--text-muted);">Date: ${{item.date || 'TBD'}}</div>
            </div>
            <div>
              <button class="btn-secondary" style="font-size:0.75rem; padding:0.2rem 0.5rem;" onclick="editInterviewRound('${{item.id}}')">✏️ Edit</button>
              <button class="btn-delete-perm" style="font-size:0.75rem; padding:0.2rem 0.5rem;" onclick="deleteInterviewRound('${{item.id}}')">✕</button>
            </div>
          </div>
          <div style="font-size:0.85rem; margin-bottom:0.4rem;">
            <strong>Interviewer:</strong> ${{item.interviewer_name || 'N/A'}} (${{item.interviewer_title || 'N/A'}}) | ${{item.interviewer_email || ''}} ${{item.interviewer_phone || ''}}
          </div>
          ${{item.interview_notes ? `<div style="font-size:0.83rem; color:#cbd5e1; margin-bottom:0.4rem;"><strong>Notes:</strong> ${{item.interview_notes}}</div>` : ''}}
          ${{item.followup_date ? `<div style="font-size:0.8rem; color:var(--accent-amber);"><strong>Post-Interview Follow-Up (${{item.followup_date}}):</strong> ${{item.followup_notes || 'Pending'}}</div>` : ''}}
        `;
        container.appendChild(card);
      }});
    }}

    function resetInterviewForm() {{
      document.getElementById('editingInterviewId').value = '';
      document.getElementById('interviewFormTitle').innerText = '➕ Add Interview Round';
      document.getElementById('intDate').value = '';
      document.getElementById('intType').value = 'Initial Screen';
      document.getElementById('intFormat').value = 'Video';
      document.getElementById('intName').value = '';
      document.getElementById('intTitle').value = '';
      document.getElementById('intEmail').value = '';
      document.getElementById('intPhone').value = '';
      document.getElementById('intNotes').value = '';
      document.getElementById('intFollowupDate').value = '';
      document.getElementById('intFollowupNotes').value = '';
    }}

    function editInterviewRound(intId) {{
      const app = APPS_DATA.find(a => a.id === currentAppDetailId);
      if (!app) return;
      const target = (app.interviews || []).find(i => i.id === intId);
      if (!target) return;

      document.getElementById('editingInterviewId').value = target.id;
      document.getElementById('interviewFormTitle').innerText = '✏️ Edit Interview Round';
      document.getElementById('intDate').value = target.date || '';
      document.getElementById('intType').value = target.type || 'Initial Screen';
      document.getElementById('intFormat').value = target.format || 'Video';
      document.getElementById('intName').value = target.interviewer_name || '';
      document.getElementById('intTitle').value = target.interviewer_title || '';
      document.getElementById('intEmail').value = target.interviewer_email || '';
      document.getElementById('intPhone').value = target.interviewer_phone || '';
      document.getElementById('intNotes').value = target.interview_notes || '';
      document.getElementById('intFollowupDate').value = target.followup_date || '';
      document.getElementById('intFollowupNotes').value = target.followup_notes || '';
    }}

    async function deleteInterviewRound(intId) {{
      if (!confirm('Delete this interview round?')) return;
      try {{
        const res = await fetch('http://localhost:5000/api/delete_interview', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ app_id: currentAppDetailId, interview_id: intId }})
        }});
        const data = await res.json();
        if (data.status === 'success') {{
          showToast('Interview round deleted.');
          setTimeout(() => window.location.reload(), 1000);
        }}
      }} catch (err) {{
        showToast('❌ Error deleting interview.');
      }}
    }}

    async function saveInterviewRound() {{
      if (!currentAppDetailId) return;
      const editingId = document.getElementById('editingInterviewId').value;
      const intObj = {{
        id: editingId || null,
        date: document.getElementById('intDate').value,
        type: document.getElementById('intType').value,
        format: document.getElementById('intFormat').value,
        interviewer_name: document.getElementById('intName').value,
        interviewer_title: document.getElementById('intTitle').value,
        interviewer_email: document.getElementById('intEmail').value,
        interviewer_phone: document.getElementById('intPhone').value,
        interview_notes: document.getElementById('intNotes').value,
        followup_date: document.getElementById('intFollowupDate').value,
        followup_notes: document.getElementById('intFollowupNotes').value
      }};

      try {{
        const res = await fetch('http://localhost:5000/api/save_interview', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ app_id: currentAppDetailId, interview: intObj }})
        }});
        const data = await res.json();
        if (data.status === 'success') {{
          showToast('💾 Interview round saved.');
          setTimeout(() => window.location.reload(), 1000);
        }}
      }} catch (err) {{
        showToast('❌ Error saving interview round.');
      }}
    }}

    function showToast(htmlMsg) {{
      const toast = document.getElementById('toastNotification');
      const msg = document.getElementById('toastMessage');
      if (toast && msg) {{
        msg.innerHTML = htmlMsg;
        toast.style.display = 'block';
        setTimeout(() => {{ toast.style.display = 'none'; }}, 4000);
      }}
    }}
  </script>

  <div id="toastNotification" style="display:none; position:fixed; bottom:2rem; right:2rem; background:#0f172a; border:1px solid var(--accent-blue); padding:1rem 1.5rem; border-radius:0.75rem; color:#fff; box-shadow:0 10px 30px rgba(0,0,0,0.5); z-index:10000;">
    <div id="toastMessage"></div>
  </div>
</body>
</html>
"""

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Saved updated dashboard HTML to {INDEX_FILE}.")

    os.makedirs(os.path.dirname(PRIMARY_DASHBOARD), exist_ok=True)
    shutil.copy(INDEX_FILE, PRIMARY_DASHBOARD)
    print(f"Copied live dashboard to {PRIMARY_DASHBOARD}.")

    if os.path.exists(os.path.dirname(SECONDARY_DASHBOARD)):
        shutil.copy(INDEX_FILE, SECONDARY_DASHBOARD)
        print(f"Copied live dashboard mirror to {SECONDARY_DASHBOARD}.")

if __name__ == '__main__':
    sync_dashboard()
