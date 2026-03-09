import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    db.execute(text("DELETE FROM research_submissions WHERE user_id IN (SELECT id FROM users WHERE role != 'ADMIN')"))
    db.execute(text("DELETE FROM user_checklist_progress WHERE user_id IN (SELECT id FROM users WHERE role != 'ADMIN')"))
    db.execute(text("DELETE FROM module_submissions WHERE user_id IN (SELECT id FROM users WHERE role != 'ADMIN')"))
    db.execute(text("DELETE FROM video_submissions WHERE user_id IN (SELECT id FROM users WHERE role != 'ADMIN')"))
    db.execute(text("DELETE FROM applicant_profiles WHERE user_id IN (SELECT id FROM users WHERE role != 'ADMIN')"))
    db.execute(text("DELETE FROM application_reviews WHERE user_id IN (SELECT id FROM users WHERE role != 'ADMIN')"))
    db.execute(text("DELETE FROM users WHERE role != 'ADMIN'"))
    db.commit()
    print('All applicant data cleared successfully.')
except Exception as e:
    db.rollback()
    print(f'Error: {e}')
finally:
    db.close()
