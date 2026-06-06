# SpacePoint Portal — VPS Deployment Update Guide
### Updating the Portal with Contract Generation & Rocket Loading

Follow these steps to deploy the latest updates (BOLD contract generation, PDF conversion, and UI improvements) to your Hostinger VPS.

---

## 1. Install New System Dependencies (Linux)
The contract generation uses **LibreOffice** on Linux to convert Word documents to PDF. You MUST install it on your VPS:

```bash
# Connect to your VPS
ssh root@<your-vps-ip>

# Install LibreOffice (Headless mode)
apt update
apt install -y libreoffice-writer libreoffice-java-common
```

---

## 2. Pull Latest Code & Dependencies
Navigate to your project folder and pull the updates.

```bash
cd /var/www/spacepoint

# Pull the latest changes from Git
git pull

# Activate virtual environment
source backend/venv/bin/activate

# Install new Python packages (python-docx, docx2pdf)
pip install -r backend/requirements.txt
```

---

## 3. Run Database Migrations & Structure Repair
We added new columns (contract paths, transportation options, etc.) to the database. You must update your database schema and structure:

```bash
cd /var/www/spacepoint/backend

# 1. Run migrations via Alembic
alembic upgrade head

# 2. Run the ultimate repair script to sync missing columns & custom types
python ultimate_fix.py
```

---

## 4. Fix Permissions
Ensure the web server (`www-data`) has permission to create the new contract folders:

```bash
# Create the contracts folder if it doesn't exist
mkdir -p /var/www/spacepoint/backend/app/uploads/contracts

# Set ownership to the web user
chown -R www-data:www-data /var/www/spacepoint
chmod -R 775 /var/www/spacepoint/backend/app/uploads
```

---

## 5. Restart the Service
To apply the backend changes (email logic, PDF conversion, etc.), restart the `spacepoint` service:

```bash
systemctl restart spacepoint

# Check that it's running correctly
systemctl status spacepoint
```

---

## 6. Verify the Update
1.  **Log in** to your Admin Dashboard at `https://portal.spacepoint.ae/admin`.
2.  **Approve** an applicant.
3.  You should see the **Rocket 🚀 Loading Icon** while it processes.
4.  The applicant should receive a **PDF contract** with their name/area/date in **BOLD**.

---

### Troubleshooting
*   **Alembic Multiple Head Revisions Error?**: 
    If you get an error saying *"Multiple head revisions are present for given argument 'head'"*, it means there are extra untracked migration scripts on your VPS that are not in Git (e.g. from running an autogenerate command on the VPS).
    To fix this, check for untracked files and delete them:
    ```bash
    # 1. Check for untracked migration files on the VPS
    git status backend/alembic/versions/
    
    # 2. Delete any untracked files (e.g. untracked_migration.py)
    rm backend/alembic/versions/some_untracked_migration_file.py
    
    # 3. Verify there is only one head now
    alembic heads
    
    # 4. Run the upgrade again
    alembic upgrade head
    ```
*   **PDF not generating?**: Check if LibreOffice is working: `libreoffice --version`.
*   **Rocket icon not showing?**: Refresh your browser cache (Ctrl + F5).
*   **Service won't start?**: Check logs: `journalctl -u spacepoint -f`.
