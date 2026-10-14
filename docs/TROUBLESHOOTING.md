# 🔧 Troubleshooting Guide

This guide addresses common setup, runtime, and configuration issues with concrete root causes and step-by-step fixes.

---

## 1. Port 5000 Already in Use

### Symptom
When running `python start.py` or `python dashboard_server.py`, you receive an error:
```
OSError: [Errno 98] Address already in use
```
or
```
OSError: [WinError 10048] Only one usage of each socket address (protocol/network address/port) is normally permitted
```

### Cause
Another service on your computer is already listening on port 5000. Common culprits include:
- A previously running instance of `dashboard_server.py` that was not terminated.
- On macOS Monterey/Ventura/Sonoma: the built-in **AirPlay Receiver** defaults to port 5000.
- Another local web service or development container.

### Concrete Fix
**Option A: Terminate the conflicting process**
- **Windows**:
  ```cmd
  netstat -ano | findstr :5000
  taskkill /PID <PID_FROM_OUTPUT> /F
  ```
- **macOS / Linux**:
  ```bash
  lsof -i :5000
  kill -9 <PID_FROM_OUTPUT>
  ```
  *(On macOS, you can also disable AirPlay Receiver in **System Settings &rarr; General &rarr; AirDrop & Handoff &rarr; AirPlay Receiver**)*.

**Option B: Run the dashboard on an alternate port**
```bash
python dashboard_server.py --port 5050 --daemon
```
Then open `http://localhost:5050` in your browser.

---

## 2. Gmail OAuth2 Authentication Failures

### Symptom
- Error `Client credentials file not found at credentials.json`
- Error `redirect_uri_mismatch` or `invalid_client` during browser consent.
- Authorization screen says "This app is blocked" or "Access blocked: Authorization Error".

### Cause
- `credentials.json` is missing from the root directory.
- The OAuth client credentials were created as a "Web application" instead of a "Desktop app".
- Your Google Cloud OAuth Consent Screen is in "Testing" mode and your personal Gmail account has not been added as an authorized Test User.

### Concrete Fix
1. Open the [Google Cloud Console](https://console.cloud.google.com).
2. Go to **APIs & Services &rarr; Enabled APIs & Services** and ensure **Gmail API** is enabled.
3. Go to **APIs & Services &rarr; OAuth consent screen**:
   - If User Type is **External** and Publishing status is **Testing**, scroll to **Test users** and click **+ Add Users**. Add your personal Gmail address.
4. Go to **APIs & Services &rarr; Credentials**:
   - Click **+ Create Credentials &rarr; OAuth client ID**.
   - Under **Application type**, select **Desktop app**.
   - Click **Create**, then click **Download JSON**.
5. Save the downloaded file as `credentials.json` in the root of `job_search_agent` (or upload it via the browser setup wizard / dashboard Settings).
6. Run the authentication flow:
   ```bash
   python auth_gmail.py
   ```
   Or click **Authorize with Google** in the dashboard / setup wizard. Once approved, `token.json` is generated locally and stored securely on your machine.

---

## 3. No Roles Ingested (Empty Review Queue)

### Symptom
After running a search cycle, the review queue displays `0` opportunities and the empty state message.

### Cause
1. Ingestion filters are too restrictive (salary floor set above market postings, or target titles do not match listings).
2. Sources are toggled off in `config.json` or the Source Status Panel.
3. Scraper rate limits or temporary network blocks by target job boards.

### Concrete Fix
1. **Check Source Status**:
   - In the dashboard, verify the **Ingestion Sources** panel. Ensure `BuiltIn`, `JobSpy`, and `JobsPipe` are toggled **Active**.
2. **Review Target Titles and Salary Floor**:
   - In Dashboard Settings (or CLI: `python configure.py get candidate.min_salary_floor`), check your floor.
   - If set to $250,000+, lower to $180,000 to test broader candidate matching.
   - Verify `search_matrix.target_titles` includes standard seniority titles (e.g. `Director of Engineering`, `VP of Engineering`, `Head of Technology`).
3. **Run a Manual Cycle and Inspect Logs**:
   ```bash
   python run_unified_search.py
   ```
   Inspect terminal output. The ingestion guard prints any disqualified opportunities along with the disqualification reason (e.g. `[DISQUALIFIED] Sub-floor compensation`, `[DISQUALIFIED] Geographic mismatch`).

---

## 4. Desktop Notifications Not Appearing

### Symptom
Roles are ingested into the queue, but no system desktop toast notification is shown.

### Cause
- Desktop notifications are disabled in `config.json` (`notifications.desktop_enabled: false`).
- Operating system notification banners or Focus Assist / Do Not Disturb are suppressing alerts.
- Headless server environment without a graphical desktop notification daemon.

### Concrete Fix
1. **Enable Desktop Alerts in Dashboard**:
   - Click the **Desktop Alerts: ON** badge in the dashboard header or set via CLI:
     ```bash
     python configure.py set notifications.desktop_enabled true
     ```
2. **Check OS Notification Settings**:
   - **Windows 10/11**: Go to **Settings &rarr; System &rarr; Notifications**. Ensure notifications are enabled and check that **Focus assist** (Do Not Disturb) is turned off.
   - **macOS**: Go to **System Settings &rarr; Notifications &rarr; Terminal / Python** and verify alerts are permitted.
   - **Linux**: Ensure a notification daemon (e.g. `dunst`, `mako`, `notify-osd`, or GNOME notification daemon) is active and `libnotify-bin` is installed.
3. Notifications are always printed to the terminal console output as a reliable fallback.

---

## 5. Background Scheduler Not Firing

### Symptom
Opportunities are not ingested automatically every X hours.

### Cause
- The dashboard was started without the `--daemon` flag.
- The scheduler toggle in the dashboard header is set to `OFF`.
- The host computer went into sleep or hibernation mode.

### Concrete Fix
1. **Use the One-Command Launcher**:
   - Always launch using `python start.py`, `start.bat` (Windows), or `./start.sh` (macOS/Linux). The launcher starts the scheduler in daemon mode automatically.
2. **Verify Daemon Mode**:
   - If running `dashboard_server.py` directly, ensure you supply `--daemon`:
     ```bash
     python dashboard_server.py --daemon
     ```
3. **Check Dashboard Scheduler Badge**:
   - In the dashboard header, verify the scheduler badge shows `Scheduler: [ON] 6h`. If it displays `OFF`, click the button to re-activate it.
4. **Trigger On-Demand Ingestion**:
   - Click the **⚡ Run search now** button in the dashboard header at any time to run an immediate search cycle without waiting for the scheduler interval.
