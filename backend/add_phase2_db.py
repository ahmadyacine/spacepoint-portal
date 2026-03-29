import os
import sys

# Adding backend path to sys.path to run standalone
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import SessionLocal, engine
from app.models.submission import Base, PresentationSubmission  # Important: import PresentationSubmission

def main():
    db = SessionLocal()
    try:
        # Alter Enum type ApplicationStatus
        try:
            # PostgreSQL requires committing before ALTER TYPE
            db.execute(text("COMMIT"))
            db.execute(text("ALTER TYPE applicationstatus ADD VALUE 'PHASE_1_APPROVED'"))
            print("Successfully added PHASE_1_APPROVED to applicationstatus enum.")
        except Exception as e:
            if "already exists" in str(e):
                print("PHASE_1_APPROVED already exists in enum.")
            else:
                db.rollback()
                print(f"Error expanding enum: {e}")

        # Now create the new table presentation_submissions if it doesn't exist
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("Done.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
