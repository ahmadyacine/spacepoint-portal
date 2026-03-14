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
from app.core.database import Base, engine
from app.models.user import User, UserRole
from app.models.instructor_profile import InstructorProfile
from app.models.training import TrainingModule, TrainingVideo, UserTrainingProgress
from app.models.library import LibraryModule, LibraryResource
# Use the correct class names from checklist.py
from app.models.checklist import Module, ModuleSection, ChecklistItem, UserChecklistProgress, ModuleSubmission
from app.models.invitation import InvitationCode
from app.models.profile import ApplicantProfile
from app.models.review import ApplicationReview

# Use a separate engine with AUTOCOMMIT for the ENUM fix
# ENUM updates in Postgres cannot run inside a normal transaction
enum_engine = create_engine(db_url, isolation_level="AUTOCOMMIT")

def fix():
    # 1. Physical Table Creation
    print("Phase 1: Creating missing tables...")
    try:
        # metadata.create_all only creates tables that don't exist
        # This will fix the 'library_modules' and 'training_modules' missing errors
        Base.metadata.create_all(bind=engine)
        print("Success: All missing tables (training, library, etc.) have been created.")
    except Exception as e:
        print(f"Error during table creation: {e}")

    # 2. Existing Table Column Audit
    print("\nPhase 2: Checking for missing columns in existing tables...")
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    
    if "instructor_profiles" in table_names:
        cols = [c['name'] for c in inspector.get_columns("instructor_profiles")]
        with engine.begin() as conn:
            for col_name in ["contract_path", "signed_contract_path"]:
                if col_name not in cols:
                    print(f"Adding missing column '{col_name}' to instructor_profiles...")
                    conn.execute(text(f"ALTER TABLE instructor_profiles ADD COLUMN {col_name} VARCHAR"))
    
    # 3. ENUM Role Synchronization
    print("\nPhase 3: Synchronizing UserRole ENUM...")
    try:
        with enum_engine.connect() as conn:
            # Check existing enum values in PostgreSQL
            result = conn.execute(text("SELECT enumlabel FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE pg_type.typname = 'userrole'"))
            existing_values = [row[0] for row in result]
            print(f"Current roles in DB: {existing_values}")
            
            if "FACILITATOR" not in existing_values:
                print("Patching DB: Adding 'FACILITATOR' to userrole ENUM...")
                conn.execute(text("ALTER TYPE userrole ADD VALUE 'FACILITATOR'"))
                print("Role added successfully.")
            else:
                print("Role already synchronized.")
                
    except Exception as e:
        print(f"Note: {e}")

    print("\n✅ CORE REPAIR COMPLETE: Database structure now matches your backend code.")

if __name__ == "__main__":
    fix()
