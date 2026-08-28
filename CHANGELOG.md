# 📜 Changelog

All notable changes to the **YACareerOps / job_search_agent** platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.2.0] - 2026-08-28

### Added
- **🤝 LinkedIn 1st-Degree Connections Engine**: Parses exported `Connections.csv` files, matches network connections to target companies in the review queue and applications list, and displays green network badges.
- **💬 3TC Outreach Template Modal**: Integrated 1-click warm outreach copy templates pre-populated with candidate background and target company details.
- **📤 CSV Connections Import Portal**: Built dashboard button and `/api/upload_connections` REST endpoint for drag-and-drop CSV importing directly from the browser UI.

### Fixed & Hardened
- **🛡️ Configurable Role & Title Exclusion Engine (`excluded_titles`)**: Dynamic multi-keyword pre-filtering engine that hard-rejects non-target role categories before phrase matching.
- **📍 Dynamic Metropolitan Location & Region Blacklist (`excluded_locations`)**: Candidate-configured location boundary filter allowing precise exclusion of non-target cities and international regions.
- **📱 Post-Audit Notification Pipeline**: Refactored push notification pipeline to trigger strictly AFTER all pre-screening, title validation, and location purges complete.

---

## [v1.1.0] - 2026-08-27

### Added
- **🌐 Remote Access & Tailscale Support**: Dynamic `window.location.origin` API origin binding allowing remote monitoring over Tailscale (`http://<your-tailscale-ip>:5000`) from mobile and external laptops.
- **🧠 Candidate Skill Learning & Anti-Hallucination Engine**: Persistent `approved_skills.json` and `rejected_skills.json` rule registries enforcing 100% candidate baseline verification.
- **🤖 BuiltIn & Dice Scraper Modules**: Added automated ground-truth extraction for BuiltIn and Dice job boards.

---

## [v1.0.0] - 2026-08-26

### Added
- Initial public release of YACareerOps autonomous job search agent, multi-board JobSpy scraper, local HTTP API server, and 1-click ATS application package builder.
