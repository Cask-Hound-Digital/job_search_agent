# Security and Code Quality Rules
* You must never hardcode API keys or secrets into frontend components. Always use environment variables.
* If creating a backend database (Firebase/Supabase), you must write and verify strict Security Rules blocking unauthorized public access.
* Before marking an Artifact or Task as complete, run a self-review step to verify no OWASP Top 10 vulnerabilities (like SQL injection or XSS) were introduced.
## 🛡️ APPSEC COMPLIANCE REPORT CARD
> **Instruction to AppSec Guard:** If you detect any security bugs or guideline violations during a scan, you must format your response using the interactive report card layout below. Clear all placeholder text and output it as markdown checkboxes.

### 🛑 Security Violations Found
- [ ] **File:** `<Insert_File_Path>` — **Line:** `<Line_Number>`
  - **Severity:** `[Critical 🔴 | Warning 🟡]`
  - **Flaw Description:** <Describe the specific security vulnerability here>
  - **Required Fix:** <Provide a 1-sentence instruction on how the main builder agent should refactor this code>

### 📋 Code Health Evaluation
- [ ] **Secret Management:** `[Passed ✅ | Failed ❌ | N/A ➖]`
- [ ] **Database / Routing Rules:** `[Passed ✅ | Failed ❌ | N/A ➖]`
- [ ] **Input Validation:** `[Passed ✅ | Failed ❌ | N/A ➖]`

### 🤖 Prompt for the Primary Builder
Copy and paste the line below into the main builder chat window to initiate an automated patch:
> `Fix the security vulnerabilities flagged by AppSec Guard in <Insert_File_Path> and ensure it aligns with our agents.md standards.`
