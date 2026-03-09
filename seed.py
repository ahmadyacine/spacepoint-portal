import sys
import os
import json

# Add the backend directory to python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.invitation import InvitationCode
from app.models.submission import VideoSubmission, SubmissionStatus
from app.models.checklist import Module, ModuleSection, ChecklistItem

def seed():
    db = SessionLocal()
    try:
        # 1. Check if admin exists
        admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if not admin:
            admin = User(
                name="Admin User",
                email=settings.ADMIN_EMAIL,
                password_hash=get_password_hash(settings.ADMIN_PASSWORD),
                role=UserRole.ADMIN,
                must_change_password=0 # Use integer for PG/SQLite compatibility
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

        # 2. Seed Invitation Codes
        codes = ["INV-ALPHA", "INV-BETA", "INV-GAMMA", "INV-DELTA", "INV-EPSILON"]
        for code in codes:
            existing = db.query(InvitationCode).filter(InvitationCode.code == code).first()
            if not existing:
                inv = InvitationCode(code=code, max_uses=20, is_active=True)
                db.add(inv)
                print(f"Created invitation code: {code}")
        db.commit()

        # 3. Seed Learning Modules from seed_data.json
        seed_data_path = os.path.join(os.path.dirname(__file__), 'seed_data.json')
        if os.path.exists(seed_data_path):
            with open(seed_data_path, 'r') as f:
                modules_data = json.load(f)
            
            for m_data in modules_data:
                # Get or create Module
                module = db.query(Module).filter(Module.sort_order == m_data['sort_order']).first()
                if not module:
                    module = Module(
                        title=m_data['module_title'],
                        sort_order=m_data['sort_order']
                    )
                    db.add(module)
                    db.commit()
                    db.refresh(module)
                    print(f"Created Module: {module.title}")
                
                # Sections
                for s_data in m_data.get('sections', []):
                    # Get or create Section
                    section = None
                    if s_data.get('section_title'):
                        section = db.query(ModuleSection).filter(
                            ModuleSection.module_id == module.id,
                            ModuleSection.title == s_data['section_title']
                        ).first()
                        if not section:
                            section = ModuleSection(
                                module_id=module.id,
                                title=s_data['section_title'],
                                sort_order=s_data['sort_order']
                            )
                            db.add(section)
                            db.commit()
                            db.refresh(section)
                            print(f"  Created Section: {section.title}")
                    
                    # Items
                    for i_data in s_data.get('items', []):
                        # Get or create ChecklistItem
                        item = db.query(ChecklistItem).filter(
                            ChecklistItem.module_id == module.id,
                            ChecklistItem.item_code == i_data['item_code']
                        ).first()
                        if not item:
                            item = ChecklistItem(
                                module_id=module.id,
                                section_id=section.id if section else None,
                                item_code=i_data['item_code'],
                                title=i_data['title'],
                                description=i_data['description'],
                                sort_order=i_data['sort_order'],
                                is_required=True
                            )
                            db.add(item)
                            print(f"    Added Item: {item.item_code} - {item.title}")
            
            db.commit()
            print("Successfully seeded all modules and checklist items from seed_data.json")

        print("Seeding completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
