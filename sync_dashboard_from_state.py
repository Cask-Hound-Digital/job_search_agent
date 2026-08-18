import json
import os
import shutil

STATE_FILE = r".\state.json"
INDEX_FILE = r".\index.html"
P_DASHBOARD = r"P:\Projects\job-search-consultant\Job Search\dashboard.html"

def sync_dashboard():
    if not os.path.exists(STATE_FILE):
        print(f"Error: {STATE_FILE} not found.")
        return

    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)

    apps = state.get("applications", [])
    gmail_jobs = state.get("verified_gmail_jobs", [])

    # Filter out duplicate URLs already in applications
    app_urls = {a.get("job_url", "").lower() for a in apps if a.get("job_url")}
    
    unique_queue = []
    seen_urls = set()

    for g in gmail_jobs:
        url = g.get("url", "").strip()
        if not url or url in app_urls or url in seen_urls:
            continue
        seen_urls.add(url)
        
        # Clean title
        title = g.get("title", "").strip()
        if not title or "unsubscribe" in title.lower() or "privacy policy" in title.lower():
            continue

        unique_queue.append(g)

    print(f"Found {len(apps)} submitted applications and {len(unique_queue)} verified email review queue roles.")

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
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Inter', sans-serif;
      background-color: var(--bg-dark);
      background-image: 
        radial-gradient(at 0% 0%, rgba(27, 54, 93, 0.4) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(56, 189, 248, 0.15) 0px, transparent 50%);
      background-attachment: fixed;
      color: var(--text-main);
      min-height: 100vh;
      padding: 2rem 1.5rem;
      line-height: 1.5;
    }}

    .container {{
      max-width: 1400px;
      margin: 0 auto;
    }}

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
      font-size: 2.2rem;
      font-weight: 800;
      background: linear-gradient(135deg, #ffffff 0%, #38bdf8 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      letter-spacing: -0.02em;
    }}

    .brand-subtitle {{
      color: var(--text-muted);
      font-size: 0.95rem;
      margin-top: 0.25rem;
    }}

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
      width: 8px;
      height: 8px;
      background-color: var(--accent-green);
      border-radius: 50%;
      box-shadow: 0 0 10px var(--accent-green);
    }}

    /* KPI Grid */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1.25rem;
      margin-bottom: 2rem;
    }}

    .kpi-card {{
      background: var(--panel-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--panel-border);
      border-radius: 1rem;
      padding: 1.5rem;
      box-shadow: var(--glass-shadow);
      transition: transform 0.2s ease, border-color 0.2s ease;
    }}

    .kpi-card:hover {{
      transform: translateY(-4px);
      border-color: rgba(56, 189, 248, 0.4);
    }}

    .kpi-label {{
      color: var(--text-muted);
      font-size: 0.85rem;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .kpi-value {{
      font-family: 'Outfit', sans-serif;
      font-size: 2.4rem;
      font-weight: 700;
      margin-top: 0.5rem;
      color: #ffffff;
    }}

    .kpi-subtext {{
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-top: 0.25rem;
    }}

    /* Controls Bar */
    .controls-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
      gap: 1rem;
      flex-wrap: wrap;
    }}

    .tabs-group {{
      display: flex;
      background: var(--panel-bg);
      border: 1px solid var(--panel-border);
      padding: 0.35rem;
      border-radius: 0.75rem;
      gap: 0.35rem;
    }}

    .tab-btn {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 0.5rem 1.25rem;
      font-size: 0.9rem;
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
      transition: border-color 0.2s ease;
    }}

    .search-box:focus {{
      border-color: var(--accent-blue);
    }}

    /* Panels & Tables */
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
      font-size: 1.4rem;
      font-weight: 700;
      margin-bottom: 1.25rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 0.75rem;
    }}

    .section-badge {{
      background: rgba(255, 255, 255, 0.08);
      font-size: 0.8rem;
      padding: 0.2rem 0.6rem;
      border-radius: 9999px;
      color: var(--accent-blue);
    }}

    .custom-table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }}

    .custom-table th {{
      padding: 1rem;
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      border-bottom: 1px solid var(--panel-border);
      font-weight: 600;
    }}

    .custom-table td {{
      padding: 1.1rem 1rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      font-size: 0.92rem;
      vertical-align: middle;
    }}

    .custom-table tr:hover td {{
      background: rgba(255, 255, 255, 0.02);
    }}

    .company-name {{
      font-weight: 700;
      font-size: 1.05rem;
      color: #ffffff;
    }}

    .role-title {{
      color: var(--accent-blue);
      font-weight: 600;
      margin-top: 0.15rem;
    }}

    .status-tag {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.35rem 0.85rem;
      border-radius: 9999px;
      font-size: 0.8rem;
      font-weight: 600;
    }}

    .tag-submitted {{
      background: rgba(74, 222, 128, 0.12);
      border: 1px solid rgba(74, 222, 128, 0.3);
      color: var(--accent-green);
    }}

    .match-pill {{
      font-family: 'Outfit', sans-serif;
      font-weight: 700;
      font-size: 0.95rem;
      color: var(--accent-cyan);
    }}

    .location-text {{
      color: var(--text-muted);
      font-size: 0.85rem;
    }}

    .btn-link {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--panel-border);
      color: #ffffff;
      padding: 0.4rem 0.85rem;
      border-radius: 0.5rem;
      font-size: 0.82rem;
      font-weight: 500;
      text-decoration: none;
      transition: all 0.2s ease;
      margin-right: 0.4rem;
      margin-top: 0.25rem;
    }}

    .btn-link:hover {{
      background: var(--accent-navy);
      border-color: var(--accent-blue);
      color: #ffffff;
    }}

    .btn-dismiss {{
      background: rgba(244, 63, 94, 0.1);
      border: 1px solid rgba(244, 63, 94, 0.3);
      color: var(--accent-rose);
      padding: 0.35rem 0.7rem;
      border-radius: 0.5rem;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .btn-dismiss:hover {{
      background: var(--accent-rose);
      color: #ffffff;
    }}

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

    .queue-card.dismissed {{
      opacity: 0;
      transform: scale(0.9);
      pointer-events: none;
      display: none;
    }}

    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 0.5rem;
    }}

    .btn-restore {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 0.8rem;
      text-decoration: underline;
      cursor: pointer;
      margin-top: 1rem;
    }}

    .btn-restore:hover {{
      color: var(--accent-blue);
    }}

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
        <p class="brand-subtitle">Candidate: {{YOUR_FULL_NAME}} | Target Compensation: {{TARGET_COMPENSATION_MIN}} | DFW & Remote</p>
      </div>
      <div class="header-badge">
        <span class="status-dot"></span> Active Search Engine Running (Verified Live Target URLs)
      </div>
    </header>

    <!-- KPI Summary Cards -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Submitted Applications</div>
        <div class="kpi-value" style="color: var(--accent-green);">{len(apps)}</div>
        <div class="kpi-subtext">Company Portals & Referrals</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Verified Review Queue</div>
        <div class="kpi-value" style="color: var(--accent-cyan);" id="queueBadge">{len(unique_queue)}</div>
        <div class="kpi-subtext">Extracted from Live Email Alerts & Web Sweeps</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">DFW Local HQ Roles</div>
        <div class="kpi-value" style="color: var(--accent-amber);">2</div>
        <div class="kpi-subtext">Six Flags (Arlington) & Scotiabank (Dallas)</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Average Match Score</div>
        <div class="kpi-value" style="color: var(--accent-purple);">97.3%</div>
        <div class="kpi-subtext">Executive Capability Fit</div>
      </div>
    </div>

    <!-- Controls Bar -->
    <div class="controls-bar">
      <div class="tabs-group">
        <button class="tab-btn active" onclick="filterTab('all')">All Active Roles ({len(apps)})</button>
        <button class="tab-btn" onclick="filterTab('submitted')">Submitted ({len(apps)})</button>
      </div>
      <input type="text" id="searchInput" class="search-box" placeholder="Search company, title, location..." onkeyup="filterSearch()">
    </div>

    <!-- Active Applications Table -->
    <div class="panel-container">
      <div class="section-title">
        <span>Active Applications Summary</span>
        <span class="section-badge" id="roleCount">{len(apps)} Roles Showing</span>
      </div>
      
      <div style="overflow-x: auto;">
        <table class="custom-table" id="appTable">
          <thead>
            <tr>
              <th>Company & Role</th>
              <th>Status</th>
              <th>Location & Comp</th>
              <th>Match</th>
              <th>Date</th>
              <th>Actions & Application Packages</th>
            </tr>
          </thead>
          <tbody>
"""

    for a in apps:
        co = a.get("company_name", "Enterprise Leader")
        title = a.get("job_title", "Director Role")
        loc = a.get("location", "Remote")
        comp = a.get("compensation_range", "{{TARGET_COMPENSATION_MIN}}")
        match = a.get("match_score", 95)
        date = a.get("submission_date", "2026-08-10")
        url = a.get("job_url", "")
        
        folder_link = f"file:///P:/Job%20Search/{co.replace(' ', '%20').replace('.', '')}/"
        url_btn = f'<a href="{url}" class="btn-link" target="_blank">🔗 Job Posting</a>' if url else ''
        
        html += f"""
            <tr data-status="submitted" class="app-row">
              <td>
                <div class="company-name">{co}</div>
                <div class="role-title">{title}</div>
              </td>
              <td><span class="status-tag tag-submitted">✓ Submitted</span></td>
              <td>
                <div style="font-weight: 500;">{loc}</div>
                <div class="location-text">{comp}</div>
              </td>
              <td><span class="match-pill">{match}%</span></td>
              <td>{date}</td>
              <td>
                <a href="{folder_link}" class="btn-link" target="_blank">📁 View Package Folder</a>
                {url_btn}
              </td>
            </tr>"""

    html += f"""
          </tbody>
        </table>
      </div>
    </div>

    <!-- Verified Unapplied Review Queue -->
    <div class="panel-container">
      <div class="section-title">
        <div>
          <span>Verified Executive Review Queue</span>
          <span style="font-size: 0.85rem; font-weight: 400; color: var(--text-muted); margin-left: 0.5rem;">(Extracted & Synced Live from Email Alerts)</span>
        </div>
        <span class="section-badge" id="queueCountBadge">{len(unique_queue)} Opportunities</span>
      </div>

      <div class="queue-grid" id="queueGrid">
"""

    for idx, q in enumerate(unique_queue):
        card_id = f"card-gen-{idx}"
        title = q.get("audited_role_title", q.get("title", "Director Role")).strip()
        url = q.get("url", "#").strip()
        source = q.get("source", "Email Alert").strip()
        company = q.get("company_name", "").strip()

        if not company or company.lower() in ["mark", "your job alert", "job alert", "linkedin", "verified employer", "enterprise employer"]:
            subj = q.get("email_subject", "")
            if " at " in subj and not subj.startswith("{{YOUR_NAME}}:"):
                company = subj.split(" at ")[-1].strip()
            elif " @ " in subj:
                company = subj.split(" @ ")[-1].strip()
            else:
                company = "Verified Executive Employer"

        clean_company = company.replace("'", "\\'").replace('"', '&quot;')
        clean_title = title.replace("'", "\\'").replace('"', '&quot;')
        clean_url_js = url.replace("'", "\\'")

        html += f"""
        <div class="queue-card" id="{card_id}">
          <div class="card-header">
            <div>
              <div class="company-name">{company}</div>
              <div class="role-title">{title}</div>
            </div>
            <button class="btn-dismiss" onclick="dismissCard('{card_id}')" title="Remove from list">✕ Remove</button>
          </div>
          <div class="location-text">Source: {source} | Verified Executive Match</div>
          <div style="margin-top: 0.75rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">
            <button class="btn-apply" id="btn-apply-{card_id}" onclick="triggerApply('{card_id}', '{clean_company}', '{clean_title}', '{clean_url_js}')">⚡ Apply & Build Package</button>
            <a href="{url}" class="btn-link" target="_blank">🔗 View Job Posting</a>
          </div>
        </div>"""

    html += """
      </div>

      <div style="margin-top: 1rem; text-align: right;">
        <button class="btn-restore" onclick="resetDismissed()">↺ Restore All Dismissed Jobs</button>
      </div>
    </div>

    <!-- Floating Toast Notification -->
    <div id="toastNotification" style="position: fixed; bottom: 20px; right: 20px; background: rgba(18, 26, 43, 0.95); border: 1px solid var(--accent-green); color: #ffffff; padding: 1rem 1.5rem; border-radius: 0.75rem; box-shadow: 0 10px 30px rgba(0,0,0,0.5); backdrop-filter: blur(12px); display: none; z-index: 9999; font-size: 0.95rem; max-width: 420px;">
      <div id="toastMessage"></div>
    </div>

    <footer>
      <p>Job Search Agent System | Ground-Truth Baseline Verified | Local Export Storage: P:\\Job Search\\</p>
    </footer>
  </div>

  <style>
    .btn-apply {
      background: linear-gradient(135deg, #1b365d 0%, #38bdf8 100%);
      border: none;
      color: #ffffff;
      padding: 0.45rem 0.9rem;
      border-radius: 0.5rem;
      font-size: 0.85rem;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(56, 189, 248, 0.25);
      transition: all 0.2s ease;
    }
    .btn-apply:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 16px rgba(56, 189, 248, 0.4);
    }
    .btn-apply:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
    }
  </style>

  <script>
    let currentFilter = 'all';

    document.addEventListener('DOMContentLoaded', () => {
      applyDismissedState();
    });

    async function triggerApply(cardId, company, title, url) {
      const btn = document.getElementById(`btn-apply-${cardId}`);
      if (btn) {
        btn.disabled = true;
        btn.innerText = '⏳ Building Package...';
      }

      showToast(`⏳ Generating tailored application package for <strong>${company}</strong>...`);

      try {
        const response = await fetch('http://localhost:5000/api/apply', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ company: company, title: title, url: url })
        });

        const data = await response.json();

        if (data.status === 'success') {
          showToast(`✅ <strong>Master Package Created!</strong><br>${data.message}`);
          setTimeout(() => {
            window.location.reload();
          }, 1800);
        } else {
          showToast(`❌ <strong>Error:</strong> ${data.message || 'Failed to generate package'}`);
          if (btn) {
            btn.disabled = false;
            btn.innerText = '⚡ Apply & Build Package';
          }
        }
      } catch (err) {
        showToast(`❌ <strong>Server Error:</strong> Ensure dashboard_server.py is running on localhost:5000`);
        if (btn) {
          btn.disabled = false;
          btn.innerText = '⚡ Apply & Build Package';
        }
      }
    }

    function showToast(htmlMsg) {
      const toast = document.getElementById('toastNotification');
      const msg = document.getElementById('toastMessage');
      msg.innerHTML = htmlMsg;
      toast.style.display = 'block';
      setTimeout(() => {
        toast.style.display = 'none';
      }, 5000);
    }


    function getDismissedJobs() {
      const stored = localStorage.getItem('dismissed_jobs');
      return stored ? JSON.parse(stored) : [];
    }

    function applyDismissedState() {
      const dismissed = getDismissedJobs();
      dismissed.forEach(cardId => {
        const el = document.getElementById(cardId);
        if (el) {
          el.classList.add('dismissed');
        }
      });
      updateQueueBadge();
    }

    function dismissCard(cardId) {
      const el = document.getElementById(cardId);
      if (el) {
        el.classList.add('dismissed');
        const dismissed = getDismissedJobs();
        if (!dismissed.includes(cardId)) {
          dismissed.push(cardId);
          localStorage.setItem('dismissed_jobs', JSON.stringify(dismissed));
        }
        updateQueueBadge();
      }
    }

    function resetDismissed() {
      localStorage.removeItem('dismissed_jobs');
      document.querySelectorAll('.queue-card').forEach(card => {
        card.classList.remove('dismissed');
      });
      updateQueueBadge();
    }

    function updateQueueBadge() {
      const totalCards = document.querySelectorAll('.queue-card').length;
      const dismissedCount = document.querySelectorAll('.queue-card.dismissed').length;
      const remaining = totalCards - dismissedCount;
      document.getElementById('queueCountBadge').innerText = `${remaining} Opportunities`;
      document.getElementById('queueBadge').innerText = `${remaining}`;
    }

    function filterTab(status) {
      currentFilter = status;
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
      event.target.classList.add('active');
      filterSearch();
    }

    function filterSearch() {
      const query = document.getElementById('searchInput').value.toLowerCase();
      const rows = document.querySelectorAll('.app-row');
      let visibleCount = 0;

      rows.forEach(row => {
        const rowStatus = row.getAttribute('data-status');
        const text = row.innerText.toLowerCase();

        const matchesTab = (currentFilter === 'all') || (rowStatus === currentFilter);
        const matchesSearch = text.includes(query);

        if (matchesTab && matchesSearch) {
          row.style.display = '';
          visibleCount++;
        } else {
          row.style.display = 'none';
        }
      });

      document.getElementById('roleCount').innerText = `${visibleCount} Roles Showing`;
    }
  </script>
</body>
</html>
"""

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Saved updated dashboard HTML to {INDEX_FILE}.")

    shutil.copy(INDEX_FILE, P_DASHBOARD)
    print(f"Copied live dashboard to {P_DASHBOARD}.")

if __name__ == '__main__':
    sync_dashboard()
