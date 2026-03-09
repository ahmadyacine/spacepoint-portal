import sys
import os

# Add the backend directory to python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.invitation import InvitationCode
from app.models.submission import VideoSubmission, SubmissionStatus

def seed():
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if not admin:
            admin = User(
                name="Admin User",
                email=settings.ADMIN_EMAIL,
                password_hash=get_password_hash(settings.ADMIN_PASSWORD),
                role=UserRole.ADMIN
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"Admin created: {settings.ADMIN_EMAIL}")

            # Seed 3 video records for admin to satisfy seed requirements explicitly
            urls = [
                "https://youtu.be/6KcV1C1Ui5s?si=n_6wINrLhwe8JDuL",
                "https://youtu.be/qr1AvisQcV8?si=3vzFE1dRYqKiMKQS",
                "https://youtu.be/5voQfQOTem8?si=MZ5ztg6y9jiJASk6"
            ]
            for i, url in enumerate(urls, 1):
                db.add(VideoSubmission(user_id=admin.id, video_no=i, youtube_url=url))
            db.commit()
            print("Created 3 video records.")

        # Seed 5 Invitation Codes
        codes = ["INV-ALPHA", "INV-BETA", "INV-GAMMA", "INV-DELTA", "INV-EPSILON"]
        for code in codes:
            existing = db.query(InvitationCode).filter(InvitationCode.code == code).first()
            if not existing:
                inv = InvitationCode(code=code, max_uses=20, is_active=True)
                db.add(inv)
                print(f"Created invitation code: {code}")
        db.commit()

        print("Seeding completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
