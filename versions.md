# SpacePoint Portal - Versions Tracker

This document tracks all version releases, feature additions, layout modifications, and system updates for the **SpacePoint Instructor & Facilitator Portal**.

---

## [v1.1.0] - 2026-05-20
### Added
- **Admin Dashboard Overview Section & Charts**:
  - Integrated `Chart.js` libraries in the admin template suite.
  - Implemented a premium glassmorphic statistics overview tab featuring active users metrics, total counts per role, and high-fidelity interactive visualization charts.
  - Added a bar chart showing the distribution of applicant universities.
  - Added a doughnut chart showing the distribution of applicant cities.
  - Added a line chart tracking joined user registrations compared chronologically across months.
  - Exposed a backend `/api/admin/dashboard-analytics` endpoint to group and return clean database-agnostic analytical statistics.
- **Car & Own Transportation Selection**:
  - Added a new `has_own_transportation` boolean field to the `ApplicantProfile` database schema and model in `profile.py`.
  - Added a responsive binary radio selector switch to the `/apply` signup form to ask applicants if they have a car or own transportation.
  - Displayed the transportation option inside the **Applicant Details** drawer on the Admin Dashboard.
- **Gmail-Only Signup Restriction**:
  - Enforced that only `@gmail.com` email addresses are accepted for scholarship applications.
  - Implemented instant client-side validation in `apply.html`.
  - Implemented backend constraint check in `auth.py` registration API.
- **Humorous AI Alert on video summaries**:
  - Added a glassmorphic warning modal that appears randomly for one of the video summaries when a student clicks submit.
  - Says: *"We are sure that you are not using AI, right? 😉"* as a friendly deterrent against AI-plagiarized summaries.
- **File Upload Instructions & Size Limits**:
  - Added explicit maximum size limit warnings (`10MB`) to both Phase 2 research submissions and Phase 1 module details.
  - Instructed students to host files larger than 10MB on Google Drive and share the link in the comments/notes fields.
- **Modern Form Elements & Custom Controls**:
  - Replaced standard HTML checkboxes in `/apply` form with premium custom checkbox components featuring animated SVG checkmarks and scale transitions.
  - Styled all inputs, tel fields, password fields, and select dropdowns on the apply page with glassmorphism backgrounds (`rgba(5, 3, 10, 0.6)`), custom active borders, and neon violet box-shadow glows upon focus.

### Modified
- **Brand Aesthetic Alignment (spacepoint.ae Theme)**:
  - Migrated the base styling system from cyan (`#4FD1C5`) to the official brand violet theme (`#A77DFF`) across all Jinja2 templates (12+ files).
  - Loaded the **Outfit** Google Font to replace standard headings.
  - Replaced hardcoded shadow/border colors to match neon violet glowing parameters.
  - Added dark violet gradients, glassmorphism panel styles, and purple space nebula ambient glows to all templates.
- **Admin Users Management Section**:
  - Added dedicated CRUD API routes and dashboard UI to manage **ADMIN** and **FACILITATOR** accounts.
  - Restructured password changes to require verification of the user's existing password via hashing check.
  - Added safe cascade delete logic for removing accounts with related applicant metadata.

### Changed
- **Folder Organization & Asset Cleanup**:
  - Moved ID Card templates (`newID_Front.png`, `newID_Back.png`) and the Agreement docx template (`SPACE.-FC-AGREEMENTLETTER-EN - November.docx`) from the root directory to `backend/app/static/templates/`.
  - Cleaned up obsolete helper and scratch scripts (`check_tables.py`, `fix_tables.py`, `test_docx.py`) from the root folder.
  - Removed duplicate assets and obsolete generated test PDFs (`SpacePoint logo.png`, `Space.Terms.pdf`, `contract.pdf`, `InstructorID1.png`, etc.).
  - Re-routed templates lookups inside `card_layout.py` and `email_service.py` to point to the new centralized templates folder.

### Files Impacted
- `backend/app/models/profile.py`
- `backend/app/schemas/core.py`
- `backend/app/routers/auth.py`
- `backend/app/routers/admin.py`
- `backend/app/templates/apply.html`
- `backend/app/templates/admin_dashboard.html`
- `backend/app/templates/base_admin.html`
- `backend/app/templates/base_facilitator.html`
- `backend/app/templates/base_instructor.html`
- `backend/app/templates/base.html`
- `backend/app/templates/landing.html`
- `backend/app/templates/instructor/training_player.html`
- `backend/app/services/card_layout.py`
- `backend/app/services/email_service.py`

---

## [v1.0.0] - Base Portal Release (Existing System)
### Added
- **Gatekeeping & Access Verification**:
  - Invitation code validator to gate registration.
- **Phase 1 Application Checklist**:
  - Video summaries tracker with length validation (200+ words).
  - Learning modules step tracker with file download and review checklist items.
- **Phase 2 Presentation Pipeline**:
  - Video presentation submission gate and instruction guidelines.
- **Admin Dashboard Adjudication**:
  - Statistics overview cards for portal status tracking.
  - Review form with status updating and detailed review feedback logging.
  - Automatic upgrades of applicants to Instructors.
  - PDF Dossier Compiler tool utilizing `ReportLab` to merge applicant forms, documents, and checklists.
- **Contract & Agreement Automation**:
  - Auto-generation of personalized Docx/PDF agreement letters from templates and mail merging.
  - Automated transactional emails containing generated contracts and login credentials.
- **Instructor Portal**:
  - Forced temporary password reset on initial login.
  - Digital ID Card Generator utilizing Pillow/qrcode libraries (LinkedIn URL and profile photo rendering).
  - SatKit video training player and completion progress tracker.
  - Personal Vault folder uploads.
- **Facilitator Portal**:
  - Resource library module editor.
  - SatKit training content uploader.
