# SpacePoint portal MVP

This is the fully functioning MVP for the SpacePoint Instructor Scholarship Application flow.

## Technology Stack
- **Backend:** FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT Auth
- **Frontend:** Vanilla HTML, TailwindCSS (CDN), Vanilla JS

## Local Run Instructions (No Docker)

### Prerequisites
- Python 3.9+
- PostgreSQL server active locally.

### Setup Steps
1. **Create Postgres DB:**
   Ensure your local PostgreSQL has a database named `portal`.
   Ensure user `postgres` with password `Ahmad213#` exists.
   
2. **Environment Variables:**
   A `.env` file is already created in the project root containing your specified credentials (including the `%23` encoded database URL).

3. **Virtual Environment & Dependencies:**
   (Already performed by setup, but for reference):
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. **Database Migrations:**
   Ensure the database is up to date with the latest models:
   ```bash
   alembic upgrade head
   ```

5. **Seed the Database:**
   Generate the 5 invitation codes, default admin profile, and test records:
   ```bash
   python seed.py
   ```

6. **Run the Application:**
   Start the FastAPI app using Uvicorn from the project root:
   ```bash
   cd backend
   ..\venv\Scripts\python.exe -m uvicorn app.main:app --reload --env-file ..\.env
   ```

Visit `http://localhost:8000` to interact with the applicant flow.
Visit `http://localhost:8000/admin/login` to manage applications.
Default Admin: `admin@spacepoint.com` / `admin`

## MVP Features Implemented
- **Landing Page & Gate:** Access restricted via validating invitation codes.
- **Signup Flow:** Dynamic profile data collection.
- **Tasks - Videos:** Watch 3 required iframe-embedded videos and save 200+ word summaries.
- **Tasks - Research:** Downloading external PDF terms, and uploading local submission PDFs.
- **Admin Adjudication:** Full SPA dashboard to list applicants, review forms + file downloads, and Issue APPROVE/REJECT decisions with required feedback.
