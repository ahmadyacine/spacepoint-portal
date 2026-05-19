# SpacePoint Instructor & Facilitator Portal (Portal V2)

Welcome to **Portal V2**, the fully-featured, production-ready, multi-role portal for the **SpacePoint Instructor Scholarship Programme**. This platform handles the complete pipeline: from initial applicant gatekeeping and multi-phase scholarship tasks to advanced admin/facilitator adjudication, contract generation, instructor training, and digital ID card generation.

---

## 🌟 Key Product Features

### 1. Gatekeeping & Signup Flow
* **Invitation Code Gate:** Access to registration is strictly restricted using unique invitation codes, controlled by the Admin.
* **Dynamic Registration:** Collects applicant details, contact info, city of residence, and initial onboarding metadata.

### 2. Applicant Pipeline (Phase 1 & Phase 2)
* **Phase 1 Video Summaries:** Applicants watch three required embedded space/cubesat videos and submit summaries (validated at 200+ words each).
* **Interactive Module Checklists:** Applicants step through learning modules, download reference guidelines, toggle required checklist items, and upload completed PDF submissions.
* **Status Tracking:** A real-time status page shows progress, reviewer notes, and feedback.
* **Phase 2 Presentation Submission:** Once Phase 1 is approved, applicants submit a Google Drive/YouTube video link explaining Cubesat concepts (subsystems, memory, communication) within strict layout guidelines (10-15 mins, max 10 slides).

### 3. Comprehensive Adjudication (Admin Dashboard)
* **System Stats:** Live counters for total applicants, draft status, approvals, rejections, and the most active invitation codes.
* **Granular Reviews:** Admins can view individual checklist items, review uploads, and approve/reject module submissions with detailed feedback.
* **Automated Document & Email Automation:**
  * **Phase 1 Approval:** Sends an automated congratulatory email with Phase 2 instructions.
  * **Final Approval:** Automatically upgrades the applicant to an **Instructor**, generates a personalized SpacePoint Agreement Letter (`.docx` and `.pdf`) with variables in **BOLD**, registers the contract in the DB, and emails the login credentials and signed contract to the instructor.
* **Dossier PDF Compilation:** Instantly export an applicant's entire file package as a single master PDF, complete with a generated cover sheet, module separation divider sheets, and merged applicant PDF attachments.
* **Admin Control Center:** Easily manage invitation codes, register and manage Facilitators, and search the Instructor Directory.

### 4. Instructor Portal
* **Forced Password Reset:** Instructors logging in for the first time with a temporary password are automatically redirected to reset their password.
* **Digital ID Card Generation:** Instructors input their LinkedIn URL and upload a profile photo. The system uses Pillow to composite their photo, name, unique sequential ID (`SP-XXXX-UAE`), and a QR code of their LinkedIn profile onto premium front/back card templates.
* **SatKit Training Modules:** View organized modules, stream training MP4 videos directly in an inline player, read notes, and track completion progress.
* **Resource Library:** Search, preview, and download facilitator-uploaded PDF/PPTX resources.
* **Personal Documents Vault:** Upload, view, download, and delete personal files (visas, ID cards, external certifications).

### 5. Facilitator Portal
* **Library Management:** Create and delete resource modules, and upload/remove PDF and PPTX resource materials.
* **Training Management:** Setup SatKit training modules, and upload/delete training MP4 videos.

---

## 🛠️ Technology Stack

* **Backend:** FastAPI (Python 3.9+), SQLAlchemy ORM, Alembic Migrations, SQLite / PostgreSQL, JWT Authentication
* **Frontend:** Vanilla HTML5, TailwindCSS (CDN), Vanilla JS, Jinja2 Templates (Interactive dashboard UI with responsive components)
* **Document Processing:**
  * **Pillow & qrcode:** Digital ID Card creation (photo cropping, text rendering, QR code generation).
  * **python-docx & docx2pdf:** Custom Word document templating and conversion to PDF.
  * **ReportLab & PyPDF:** Compiled PDF Dossier generation and merging.

---

## 🚀 Local Run & Setup Instructions

### Prerequisites
* **Python 3.9+**
* **PostgreSQL** server active locally (or configure SQLite in `.env`).
* **LibreOffice** (optional: required for Word-to-PDF conversion on Linux, `docx2pdf` uses Word on Windows).

### Setup Steps

1. **Create the Database:**
   Ensure your local PostgreSQL server contains a database named `portal`.
   *Default config user:* `postgres` | *Default password:* `Ahmad213#`

2. **Environment Variables:**
   Create a `.env` file in the project root with the following variables:
   ```env
   DATABASE_URL=postgresql://postgres:Ahmad213%23@localhost:5432/portal
   SECRET_KEY=your-jwt-secret-key-here
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-smtp-email@gmail.com
   SMTP_PASSWORD=your-smtp-app-password
   BASE_URL=http://localhost:8000
   ADMIN_EMAIL=admin@spacepoint.com
   ADMIN_PASSWORD=admin
   ```

3. **Virtual Environment & Dependencies:**
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On Linux/macOS:
   source venv/bin/activate

   # Install requirements
   pip install -r requirements.txt
   ```

4. **Initialize Database Tables:**
   First run migrations, then ensure all tables and role types match using the repair script:
   ```bash
   alembic upgrade head
   python backend/ultimate_fix.py
   ```

5. **Seed the Database:**
   Pre-seed default admin credentials, five invitation codes, and checklist modules:
   ```bash
   python seed.py
   ```

6. **Run the Server:**
   ```bash
   cd backend
   ..\venv\Scripts\python.exe -m uvicorn app.main:app --reload --env-file ..\.env
   ```

7. **Access the Portals:**
   * **Applicant Pipeline:** [http://localhost:8000](http://localhost:8000)
   * **Admin Login:** [http://localhost:8000/admin/login](http://localhost:8000/admin/login)
     * *Default Admin User:* `admin@spacepoint.com` | *Password:* `admin`

---

## 🔧 Developer & Maintenance Utilities

The backend contains handy CLI scripts to simplify local testing and schema synchronization:

* **Database Repair & Synchronization:**
  ```bash
  python backend/ultimate_fix.py
  ```
  Creates missing tables (e.g., library/training), verifies columns in existing tables, and updates PostgreSQL role type ENUMs.

* **Clear Applicant Testing Data:**
  ```bash
  python backend/clear_data.py
  ```
  Deletes all applicant profiles, reviews, submissions, and records while preserving Admin accounts.

* **Reset Applications for Re-Testing:**
  ```bash
  python backend/reset_status.py
  ```
  Resets all approved Instructors back to the `APPLICANT` role and changes their review statuses to `UNDER_REVIEW`.

---

## 🌐 VPS Deployment Details

To deploy latest updates (PDF contract conversion, permissions) to a production VPS:
1. **Install LibreOffice** on VPS to enable headless PDF conversion:
   ```bash
   apt install -y libreoffice-writer libreoffice-java-common
   ```
2. **Set folder permissions** for the uploads directory:
   ```bash
   chown -R www-data:www-data /var/www/spacepoint
   chmod -R 775 /var/www/spacepoint/backend/app/uploads
   ```
For full details, reference the [VPS Deployment Guide](file:///c:/Users/ahmad%20yacine/Desktop/PortalV2/guides/vps_deployment_update.md).
