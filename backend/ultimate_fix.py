# backend/ultimate_fix.py
import os
import sys
from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv

# Ensure the backend directory is in path for imports
# This allows running the script from within the backend folder
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Load environment
load_dotenv()
db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("Error: DATABASE_URL not found in .env")
    sys.exit(1)

print(f"Connecting to database...")

# Import Base and ALL models to ensure they are registered with metadata
# NOTE: Whenever you add new database models/tables in the future, you MUST import them here 
# so that Base.metadata.create_all() can auto-create the missing tables in the database.
from app.core.database import Base, engine
from app.models.user import User, UserRole
from app.models.instructor_profile import InstructorProfile
from app.models.instructor_document import InstructorDocument
from app.models.submission import VideoSubmission, ResearchSubmission, PresentationSubmission, AssessmentSubmission
from app.models.training import TrainingModule, TrainingVideo, UserTrainingProgress
from app.models.library import LibraryModule, LibraryResource
# Use the correct class names from checklist.py
from app.models.checklist import Module, ModuleSection, ChecklistItem, UserChecklistProgress, ModuleSubmission
from app.models.invitation import InvitationCode
from app.models.profile import ApplicantProfile
from app.models.review import ApplicationReview, ApplicationStatus
from app.models.payment import (
    PaymentBatch, PaymentLetter, PaymentSession, PaymentAddon, 
    InstructorBankDetails, PortalSetting, Certificate, 
    PaymentLetterStatus, SessionRole
)

# Use a separate engine with AUTOCOMMIT for the ENUM fix
# ENUM updates in Postgres cannot run inside a normal transaction
enum_engine = create_engine(db_url, isolation_level="AUTOCOMMIT")

def fix():
    # 1. Physical Table Creation
    print("Phase 1: Creating missing tables...")
    try:
        # metadata.create_all only creates tables that don't exist
        Base.metadata.create_all(bind=engine)
        print("Success: All missing tables have been created.")
    except Exception as e:
        print(f"Error during table creation: {e}")

    # 2. Existing Table Column Audit
    print("\nPhase 2: Checking for missing columns in existing tables...")
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    
    # Audit Users Table
    if "users" in table_names:
        cols = [c['name'] for c in inspector.get_columns("users")]
        with engine.begin() as conn:
            if "must_change_password" not in cols:
                print("Adding missing column 'must_change_password' to users...")
                conn.execute(text("ALTER TABLE users ADD COLUMN must_change_password INTEGER DEFAULT 0 NOT NULL"))
            if "temp_password_last_set_at" not in cols:
                print("Adding missing column 'temp_password_last_set_at' to users...")
                conn.execute(text("ALTER TABLE users ADD COLUMN temp_password_last_set_at TIMESTAMP WITH TIME ZONE"))

    # Audit Instructor Profiles
    if "instructor_profiles" in table_names:
        cols = [c['name'] for c in inspector.get_columns("instructor_profiles")]
        with engine.begin() as conn:
            for col_name in ["contract_path", "signed_contract_path"]:
                if col_name not in cols:
                    print(f"Adding missing column '{col_name}' to instructor_profiles...")
                    conn.execute(text(f"ALTER TABLE instructor_profiles ADD COLUMN {col_name} VARCHAR"))

    # Audit Applicant Profiles
    if "applicant_profiles" in table_names:
        cols = [c['name'] for c in inspector.get_columns("applicant_profiles")]
        with engine.begin() as conn:
            if "has_own_transportation" not in cols:
                print("Adding missing column 'has_own_transportation' to applicant_profiles...")
                conn.execute(text("ALTER TABLE applicant_profiles ADD COLUMN has_own_transportation BOOLEAN DEFAULT FALSE"))
            if "country" not in cols:
                print("Adding missing column 'country' to applicant_profiles...")
                conn.execute(text("ALTER TABLE applicant_profiles ADD COLUMN country VARCHAR DEFAULT 'United Arab Emirates'"))
            if engine.dialect.name == "postgresql":
                try:
                    conn.execute(text("ALTER TABLE applicant_profiles ALTER COLUMN city_of_residence DROP NOT NULL"))
                    conn.execute(text("ALTER TABLE applicant_profiles ALTER COLUMN deliver_cities_json DROP NOT NULL"))
                except Exception as e:
                    print(f"Note dropping NOT NULL constraints: {e}")
    
    # 3. ENUM UserRole Synchronization
    print("\nPhase 3: Synchronizing UserRole ENUM...")
    if engine.dialect.name == "postgresql":
        try:
            with enum_engine.connect() as conn:
                # Check existing enum values in PostgreSQL
                result = conn.execute(text("SELECT enumlabel FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE pg_type.typname = 'userrole'"))
                existing_values = [row[0] for row in result]
                print(f"Current roles in DB: {existing_values}")
                
                for role_val in UserRole:
                    val_str = role_val.value
                    if val_str not in existing_values:
                        print(f"Patching DB: Adding '{val_str}' to userrole ENUM...")
                        conn.execute(text(f"ALTER TYPE userrole ADD VALUE '{val_str}'"))
                        print(f"Role '{val_str}' added successfully.")
                    else:
                        print(f"Role '{val_str}' is already in DB.")
        except Exception as e:
            print(f"Note: {e}")
    else:
        print("Skipping UserRole ENUM sync (non-PostgreSQL dialect).")

    # 4. ENUM ApplicationStatus Synchronization
    print("\nPhase 4: Synchronizing ApplicationStatus ENUM...")
    if engine.dialect.name == "postgresql":
        try:
            with enum_engine.connect() as conn:
                # Check existing enum values in PostgreSQL
                result = conn.execute(text("SELECT enumlabel FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE pg_type.typname = 'applicationstatus'"))
                existing_values = [row[0] for row in result]
                print(f"Current application statuses in DB: {existing_values}")
                
                for status_val in ApplicationStatus:
                    val_str = status_val.value
                    if val_str not in existing_values:
                        print(f"Patching DB: Adding '{val_str}' to applicationstatus ENUM...")
                        conn.execute(text(f"ALTER TYPE applicationstatus ADD VALUE '{val_str}'"))
                        print(f"Status '{val_str}' added successfully.")
                    else:
                        print(f"Status '{val_str}' is already in DB.")
        except Exception as e:
            print(f"Note: {e}")
    else:
        print("Skipping ApplicationStatus ENUM sync (non-PostgreSQL dialect).")

    # 5. ENUM PaymentLetterStatus Synchronization
    print("\nPhase 5: Synchronizing PaymentLetterStatus ENUM...")
    if engine.dialect.name == "postgresql":
        try:
            with enum_engine.connect() as conn:
                # Check existing enum values in PostgreSQL
                result = conn.execute(text("SELECT enumlabel FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE pg_type.typname = 'paymentletterstatus'"))
                existing_values = [row[0] for row in result]
                print(f"Current payment letter statuses in DB: {existing_values}")
                
                for status_val in PaymentLetterStatus:
                    val_str = status_val.value
                    if val_str not in existing_values:
                        print(f"Patching DB: Adding '{val_str}' to paymentletterstatus ENUM...")
                        conn.execute(text(f"ALTER TYPE paymentletterstatus ADD VALUE '{val_str}'"))
                        print(f"Status '{val_str}' added successfully.")
                    else:
                        print(f"Status '{val_str}' is already in DB.")
        except Exception as e:
            print(f"Note: {e}")
    else:
        print("Skipping PaymentLetterStatus ENUM sync (non-PostgreSQL dialect).")

    # 6. ENUM SessionRole Synchronization
    print("\nPhase 6: Synchronizing SessionRole ENUM...")
    if engine.dialect.name == "postgresql":
        try:
            with enum_engine.connect() as conn:
                # Check existing enum values in PostgreSQL
                result = conn.execute(text("SELECT enumlabel FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE pg_type.typname = 'sessionrole'"))
                existing_values = [row[0] for row in result]
                print(f"Current session roles in DB: {existing_values}")
                
                for role_val in SessionRole:
                    val_str = role_val.value
                    if val_str not in existing_values:
                        print(f"Patching DB: Adding '{val_str}' to sessionrole ENUM...")
                        conn.execute(text(f"ALTER TYPE sessionrole ADD VALUE '{val_str}'"))
                        print(f"Role '{val_str}' added successfully.")
                    else:
                        print(f"Role '{val_str}' is already in DB.")
        except Exception as e:
            print(f"Note: {e}")
    else:
        print("Skipping SessionRole ENUM sync (non-PostgreSQL dialect).")

    print("\n[SUCCESS] CORE REPAIR COMPLETE: Database structure now matches your backend code.")

if __name__ == "__main__":
    fix()
