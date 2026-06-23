# SpacePoint Portal - Versions Tracker

This document tracks all version releases, feature additions, layout modifications, and system updates for the **SpacePoint Instructor & Facilitator Portal**.

## [v1.5.0] - 2026-06-20
### Added
- **10 Questions Assessment Onboarding Step**:
  - Inserted a new assessment step in the onboarding flow right after the Research Modules stage and before the Video Presentation.
  - Added a dedicated database table `AssessmentSubmission` to securely store applicants' PDF answer paths, original filenames, Google Drive links, and notes/comments.
  - Automatically synchronizes the new `RESEARCH_APPROVED` state value into the PostgreSQL `applicationstatus` enum via the `ultimate_fix.py` database script.
  - Implemented `GET /api/applicant/assessment/questions` to return 10 selected questions (one from each category in the bank) and `POST /api/applicant/assessment/submit` to handle PDF/Drive link uploads.
  - Added review, download, and cascade delete functions to the admin dashboard, including merging assessment details directly into consolidated PDF exports.
  - Designed the `send_research_approval_email` template to notify applicants when their research is approved.
  - Created a dynamic assessment panel in the `/status` portal page for applicants to view their questions and upload answers, and updated the admin dashboard drawer with the answers panel.

---

## [v1.4.0] - 2026-06-10
### Added
- **Interactive FAQ Accordion**:
  - Implemented a custom JS-driven FAQ accordion section in the landing page (`landing.html`).
  - Added 6 critical questions selected from the main `FAQ.md` (covering Intern vs Instructor roles, compensation terms, onboarding roadmap, co-working locations, and required hours).
  - Built smooth max-height expansion/collapse animations and border-glow highlights.
- **Premium Branded Footer**:
  - Replaced the simple footer in the base template (`base.html`) with a modern multi-column layout.
  - Includes columns for branding description, Contact Us info (with custom SVG icons), and follow-mission links to official Instagram/TikTok/LinkedIn profiles.

### Modified
- **Landing Page Portal Theme Upgrade**:
  - Refined page layouts, updated the hero section, key highlights grid, and onboarding roadmap.
  - Enhanced responsive behavior, visual gradients, and typography for a professional space-tech portal vibe.
  - Maintained core authentication and modal inputs so user registration and login endpoints function without issues.

---

## [v1.3.1] - 2026-06-07
### Fixed
- **Instructor Payments Dashboard UI Bug Fixes**:
  - Fixed "Schedule of Workshops" and "Optional Add-ons" tables overflowing the white letter container in the Facilitator Payment Letter modal by adding width constraints and proper scroll container overflow properties.
  - Resolved status badge wrapping issue in the main Payment Letters table by setting a table minimum width and adding whitespace nowrap styling on table cells.
  - Fixed overlap between the "Save Bank Details" button and its adjacent disclaimer helper text on intermediate tablet/desktop screen widths by adjusting the responsive flex row layout breakpoint to accommodate the sidebar footprint.
- **Excel Bulk Import Template Bug Fix**:
  - Replaced usage of the non-standard `cell.column_letter` property in `openpyxl` with the official `get_column_letter` utility function from `openpyxl.utils` to prevent version mismatch crashes on deployment.
  - Corrected the `requirements.txt` installation file path in the VPS update guide from `backend/requirements.txt` to `requirements.txt`.

### Added
- **Admin Single-Letter Batch Assignment UI**:
  - Exposed a **Batch (optional)** dropdown selector inside the single letter creation modal (`openCreateLetterModal`).
  - Added a **Batch (optional)** dropdown selector in the General Information section of the inline editor modal (`openEditLetterModal`), allowing admins to dynamically move or assign individual letters to any created batch.

## [v1.3.0] - 2026-06-06
### Added
- **Instructor Payment System Backend**:
  - Designed SQLAlchemy models for automated payments workflow: `PaymentBatch`, `PaymentLetter`, `PaymentSession`, `PaymentAddon`, `InstructorBankDetails`, and `PortalSetting`.
  - Added automated ReportLab PDF generator with personalized signatory settings and digital signature embedding.
  - Developed transactional notification emails to alert instructors of ready contracts and notify administrators of signed agreements (with redirection from placeholder `admin@spacepoint.com/ae` logins to `ahmad2012yacine@gmail.com`).
  - Updated the database repair tool `backend/ultimate_fix.py` to import payment schema models, guaranteeing automated table auditing and physical table creations.

- **Admin Payments Dashboard & Batch Filtering**:
  - Replaced native browser `alert`, `confirm`, and `prompt` dialogs with theme-matched custom glassmorphic modals.
  - Developed a full-bleed inline editor modal to manually edit, add, or delete sessions and optional add-ons, recalculating totals instantly.
  - Replaced applicant metrics with **Payment Overview Stats** tracking total spent, pending payment, awaiting signatures, total sessions, and total duration.
  - Integrated **Batch Filtering** dropdown select element to group and analyze letters by batch, computing statistics client-side to ensure accuracy.

- **Instructor Payments Tab & Vault**:
  - Added IBAN, swift, bank name, and account holder fields under payments settings.
  - Created a signature confirmation modal with base64 digital signature canvas drawing and verified PDF generation.
  - Enhanced layout to support scrollable overlays and edge-to-edge full bleed ReportLab contract headers in brand violet color (`#231134`).

### Files Impacted
- `backend/ultimate_fix.py`
- `backend/app/models/payment.py`
- `backend/app/routers/payments_admin.py`
- `backend/app/routers/payments_instructor.py`
- `backend/app/services/payment_service.py`
- `backend/app/templates/admin_dashboard.html`
- `backend/app/templates/instructor/payments.html`

---

## [v1.2.0] - 2026-05-31
### Added
- **Instructor ID Card PDF Download**:
  - Implemented a backend route (`/api/instructor/id-card/pdf`) utilizing `ReportLab` to compile the front and back card images into a two-page PDF.
  - Tailored the PDF page canvas dimensions precisely to portrait CR80 format specifications (`2.125" x 3.375"` i.e., `153.0 x 243.0` points) to support direct physical printing.
  - Added a download action button to the frontend UI that is dynamically revealed upon successful ID card generation.

- **ID Card Portal Layout Enhancements**:
  - Optimized the ID card details page by converting the two-column grid into stacked full-width rows (Row 1: Card Details Form & Actions, Row 2: Card Preview showing Front/Back side-by-side).
  - Added a highly visible, always-accessible note banner detailing the standard landscape CR80 format dimensions (`3.375" x 2.125"` / `85.60 mm x 54.00 mm`) for workshop card holders.

- **Personal Documents Uploader UI Redesign**:
  - Redesigned the uploader layout into a 5-column split panel structure.
  - Added a **Required Documents Checklist** detailing explicit requirements for UAE Emirates IDs, Passport copies, Personal Pictures, SpacePoint Contracts, UAE Visas, and CVs.
  - Built a fully interactive drag-and-drop file uploader zone featuring hover transition styles, drag-over highlights, and dynamic filename/file size rendering.
  - Added **CV** option to the document type dropdown and checklist details.

---

## [v1.1.0] - 2026-05-20
### Fixed
- **Invitation Code Case Insensitivity**:
  - Enforced automatic conversion of typed invitation codes to uppercase on the frontend (`apply.html`). This fixes validation failures caused by inputting lowercase letters even when CSS transformation displays them as uppercase.

### Added
- **International Applicants (Outside UAE) Support**:
  - Implemented a location toggle at the top of the `/apply` form to differentiate between applicants residing **Within UAE** and **Outside UAE**.
  - Conditionally hides UAE-specific fields (City of Residence, Own Transportation/Car, and Deliver Cities checkboxes) for international applicants.
  - Implemented a **Country of Residence** dropdown select element populated dynamically with all countries, which is displayed and required for **both** domestic and international applicants.
  - Relaxed phone validation logic across the frontend form and backend schema (no longer mandates the `+971` UAE country code).
  - Added a new `country` column to the `ApplicantProfile` model, populated with the user's selected country from the countries dropdown.
  - Integrated `country` details inside the Admin Dashboard table view, stats aggregations, and applicant profile drawer.

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

---

## SpacePoint Portal - Database Schema Reference

This section outlines all database tables, columns, constraints, relationships, and data types modeled in SQLAlchemy for the portal.

### 1. Table: `users`
Tracks core administrative and authentication credentials.
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `name`: `String` | Not Null
  * `email`: `String` | Unique, Indexed, Not Null
  * `phone`: `String` | Nullable
  * `password_hash`: `String` | Not Null
  * `role`: `Enum(UserRole)` (`ADMIN`, `APPLICANT`, `INSTRUCTOR`, `FACILITATOR`) | Not Null
  * `invitation_code_used`: `String` | Nullable
  * `created_at`: `DateTime(timezone=True)` | Server Default (`func.now()`)
  * `last_login_at`: `DateTime(timezone=True)` | Nullable
  * `must_change_password`: `Integer` (1/0) | Not Null, Default `0`
  * `temp_password_last_set_at`: `DateTime(timezone=True)` | Nullable

### 2. Table: `applicant_profiles`
Holds additional application details for applicants.
* **Columns:**
  * `user_id`: `Integer` | Foreign Key (`users.id`), Primary Key
  * `university`: `String` | Not Null
  * `highest_degree`: `String` | Not Null
  * `highest_degree_other`: `String` | Nullable
  * `city_of_residence`: `String` | Nullable
  * `deliver_cities_json`: `String` | Nullable (stores stringified JSON list of cities)
  * `background_areas_json`: `String` | Not Null (stores stringified JSON list of areas)
  * `background_other`: `String` | Nullable
  * `has_own_transportation`: `Boolean` | Nullable, Default `False`
  * `country`: `String` | Nullable, Default `"United Arab Emirates"`

### 3. Table: `instructor_profiles`
Tracks generated assets, contract paths, and digital ID card credentials for instructors.
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `user_id`: `Integer` | Foreign Key (`users.id`), Unique, Not Null
  * `linkedin_url`: `String` | Nullable
  * `profile_photo_path`: `String` | Nullable
  * `instructor_id`: `String` | Unique, Nullable (e.g. `SP-0012-UAE`)
  * `issue_date`: `DateTime(timezone=True)` | Nullable
  * `front_card_path`: `String` | Nullable
  * `back_card_path`: `String` | Nullable
  * `contract_path`: `String` | Nullable
  * `signed_contract_path`: `String` | Nullable
  * `created_at`: `DateTime(timezone=True)` | Server Default (`func.now()`)
  * `updated_at`: `DateTime(timezone=True)` | On Update (`func.now()`)

### 4. Table: `video_submissions`
Tracks Phase 1 applicant video summaries.
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `user_id`: `Integer` | Foreign Key (`users.id`), Not Null
  * `video_no`: `Integer` (1, 2, or 3) | Not Null
  * `youtube_url`: `String` | Not Null
  * `summary_text`: `String` | Nullable
  * `word_count`: `Integer` | Default `0`
  * `status`: `Enum(SubmissionStatus)` (`DRAFT`, `SUBMITTED`) | Not Null, Default `DRAFT`
  * `submitted_at`: `DateTime(timezone=True)` | Nullable

### 5. Table: `research_submissions`
Tracks Phase 2 applicant research uploader submissions.
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `user_id`: `Integer` | Foreign Key (`users.id`), Not Null
  * `file_path`: `String` | Not Null
  * `original_filename`: `String` | Not Null
  * `content_text`: `String` | Nullable
  * `submitted_at`: `DateTime(timezone=True)` | Server Default (`func.now()`)

### 6. Table: `presentation_submissions`
Tracks final Phase 2 video link submissions.
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `user_id`: `Integer` | Foreign Key (`users.id`), Unique, Not Null
  * `video_link`: `String` | Not Null
  * `submitted_at`: `DateTime(timezone=True)` | Server Default (`func.now()`)

### 7. Table: `application_reviews`
Tracks overall admin adjudication workflow status.
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `user_id`: `Integer` | Foreign Key (`users.id`), Unique, Not Null
  * `status`: `Enum(ApplicationStatus)` (`IN_PROGRESS`, `UNDER_REVIEW`, `PHASE_1_APPROVED`, `APPROVED`, `REJECTED`) | Not Null, Default `IN_PROGRESS`
  * `admin_id`: `Integer` | Foreign Key (`users.id`), Nullable
  * `feedback`: `String` | Nullable
  * `reviewed_at`: `DateTime(timezone=True)` | Nullable

### 8. Table: `modules`
Curriculum module nodes for checklist items.
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `title`: `String` | Not Null
  * `sort_order`: `Integer` | Not Null, Default `1`

### 9. Table: `module_sections`
Checklist sections grouped under modules.
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `module_id`: `Integer` | Foreign Key (`modules.id` ON DELETE `CASCADE`), Not Null
  * `title`: `String` | Not Null
  * `sort_order`: `Integer` | Not Null, Default `1`

### 10. Table: `checklist_items`
Individual checklist items in modules/sections.
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `module_id`: `Integer` | Foreign Key (`modules.id` ON DELETE `CASCADE`), Not Null
  * `section_id`: `Integer` | Foreign Key (`module_sections.id` ON DELETE `CASCADE`), Nullable
  * `item_code`: `String` | Not Null
  * `title`: `String` | Not Null
  * `description`: `Text` | Not Null
  * `sort_order`: `Integer` | Not Null, Default `1`
  * `is_required`: `Boolean` | Not Null, Default `True`

### 11. Table: `user_checklist_progress`
Tracks student checkmarks on checklist items.
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `user_id`: `Integer` | Foreign Key (`users.id` ON DELETE `CASCADE`), Indexed, Not Null
  * `checklist_item_id`: `Integer` | Foreign Key (`checklist_items.id` ON DELETE `CASCADE`), Not Null
  * `is_completed`: `Boolean` | Not Null, Default `False`
  * `updated_at`: `DateTime(timezone=True)` | Server Default / On Update (`func.now()`)

### 12. Table: `module_submissions`
Files uploaded by applicants to pass checklist modules.
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `user_id`: `Integer` | Foreign Key (`users.id` ON DELETE `CASCADE`), Indexed, Not Null
  * `module_id`: `Integer` | Foreign Key (`modules.id` ON DELETE `CASCADE`), Not Null
  * `file_path`: `String` | Not Null
  * `original_filename`: `String` | Not Null
  * `notes_text`: `Text` | Nullable
  * `status`: `String` (`SUBMITTED`, `APPROVED`, `REJECTED`) | Not Null, Default `"SUBMITTED"`
  * `feedback`: `Text` | Nullable
  * `submitted_at`: `DateTime(timezone=True)` | Server Default (`func.now()`)
  * `reviewed_at`: `DateTime(timezone=True)` | Nullable
  * `reviewer_admin_id`: `Integer` | Foreign Key (`users.id` ON DELETE `SET NULL`), Nullable

### 13. Table: `invitation_codes`
Tracks unique verification codes for user registrations.
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `code`: `String` | Unique, Indexed, Not Null
  * `is_active`: `Boolean` | Not Null, Default `True`
  * `expires_at`: `DateTime(timezone=True)` | Nullable
  * `max_uses`: `Integer` | Not Null, Default `20`
  * `used_count`: `Integer` | Not Null, Default `0`
  * `source_type`: `String` | Nullable
  * `source_id`: `String` | Nullable
  * `created_at`: `DateTime(timezone=True)` | Server Default (`func.now()`)

### 14. Table: `instructor_documents`
Personal vault uploads by instructors (Emirates ID, Passports, Visas, Contracts, CVs, etc.).
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `user_id`: `Integer` | Foreign Key (`users.id`), Indexed, Not Null
  * `document_type`: `String` | Not Null (e.g. `"ID Card"`, `"Passport"`, `"Visa"`, `"CV"`)
  * `file_path`: `String` | Not Null
  * `uploaded_at`: `DateTime(timezone=True)` | Server Default (`func.now()`)

### 15. Table: `library_modules`
Folder categories inside resources library vault.
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `name`: `String` | Unique, Not Null
  * `description`: `Text` | Nullable
  * `created_at`: `DateTime(timezone=True)` | Server Default (`func.now()`)

### 16. Table: `library_resources`
Actual document resources uploaded for instructors inside vault folders.
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `title`: `String` | Not Null
  * `description`: `Text` | Nullable
  * `format`: `String` | Not Null (e.g. `"PDF"`, `"PPTX"`)
  * `file_path`: `String` | Not Null
  * `uploader_id`: `Integer` | Foreign Key (`users.id`)
  * `module_id`: `Integer` | Foreign Key (`library_modules.id` ON DELETE `CASCADE`), Not Null
  * `created_at`: `DateTime(timezone=True)` | Server Default (`func.now()`)

### 17. Table: `training_modules`
Curriculum modules for instructor SatKit training.
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `title`: `String` | Unique, Not Null
  * `description`: `Text` | Nullable
  * `sort_order`: `Integer` | Not Null, Default `1`
  * `created_at`: `DateTime(timezone=True)` | Server Default (`func.now()`)

### 18. Table: `training_videos`
MP4 video resources under SatKit modules.
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `module_id`: `Integer` | Foreign Key (`training_modules.id` ON DELETE `CASCADE`), Not Null
  * `title`: `String` | Not Null
  * `description`: `Text` | Nullable
  * `notes`: `Text` | Nullable
  * `video_path`: `String` | Not Null
  * `sort_order`: `Integer` | Not Null, Default `1`
  * `created_at`: `DateTime(timezone=True)` | Server Default (`func.now()`)

### 19. Table: `user_training_progress`
Tracks instructor video completion progress.
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `user_id`: `Integer` | Foreign Key (`users.id` ON DELETE `CASCADE`), Indexed, Not Null
  * `video_id`: `Integer` | Foreign Key (`training_videos.id` ON DELETE `CASCADE`), Indexed, Not Null
  * `is_completed`: `Boolean` | Not Null, Default `False`
  * `completed_at`: `DateTime(timezone=True)` | Nullable

### 20. Table: `payment_batches`
Admin groupings to categorize instructor payment cohorts.
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `name`: `String` | Not Null
  * `description`: `Text` | Nullable
  * `created_by_admin_id`: `Integer` | Foreign Key (`users.id`), Nullable
  * `created_at`: `DateTime(timezone=True)` | Server Default (`func.now()`)

### 21. Table: `payment_letters`
Generates one contract sheet/record per instructor under a batch.
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `batch_id`: `Integer` | Foreign Key (`payment_batches.id`), Nullable
  * `instructor_user_id`: `Integer` | Foreign Key (`users.id`), Not Null
  * `letter_date`: `String` | Nullable
  * `reference`: `String` | Default `"Facilitator Agreement"`
  * `status`: `Enum(PaymentLetterStatus)` (`DRAFT`, `PUBLISHED`, `SIGNED`, `PAID`) | Not Null, Default `DRAFT`
  * `is_published`: `Boolean` | Not Null, Default `False`
  * `pdf_path`: `String` | Nullable
  * `signed_pdf_path`: `String` | Nullable
  * `instructor_signature_data`: `Text` | Nullable
  * `signed_at`: `DateTime(timezone=True)` | Nullable
  * `admin_notes`: `Text` | Nullable
  * `created_at`: `DateTime(timezone=True)` | Server Default (`func.now()`)

### 22. Table: `payment_sessions`
Workshop items scheduled inside a payment letter.
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `payment_letter_id`: `Integer` | Foreign Key (`payment_letters.id`), Not Null
  * `session_date`: `String` | Not Null
  * `workshop_description`: `String` | Not Null
  * `role`: `Enum(SessionRole)` (`Lead Facilitator`, `Facilitator`, `Assistant Facilitator`) | Not Null
  * `location`: `String` | Not Null
  * `duration_hours`: `Float` | Not Null, Default `0`
  * `compensation_aed`: `Float` | Not Null, Default `0`
  * `sort_order`: `Integer` | Not Null, Default `1`

### 23. Table: `payment_addons`
Optional compensation allowances linked to a payment letter.
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `payment_letter_id`: `Integer` | Foreign Key (`payment_letters.id`), Not Null
  * `description`: `String` | Not Null
  * `amount_aed`: `Float` | Not Null, Default `0`
  * `notes`: `String` | Nullable
  * `sort_order`: `Integer` | Not Null, Default `1`

### 24. Table: `instructor_bank_details`
Secure account credentials filled by instructors for payouts.
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `user_id`: `Integer` | Foreign Key (`users.id`), Unique, Not Null
  * `account_holder_name`: `String` | Nullable
  * `bank_name`: `String` | Nullable
  * `iban`: `String` | Nullable
  * `swift_bic`: `String` | Nullable
  * `updated_at`: `DateTime(timezone=True)` | Server Default / On Update (`func.now()`)

### 25. Table: `portal_settings`
Global system settings key/value registry (e.g., admin signature paths).
* **Columns:**
  * `id`: `Integer` | Primary Key, Indexed
  * `key`: `String` | Unique, Indexed, Not Null
  * `value`: `Text` | Nullable
  * `updated_at`: `DateTime(timezone=True)` | Server Default / On Update (`func.now()`)
