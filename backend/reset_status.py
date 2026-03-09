import sys
sys.path.insert(0, '.')
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    db.execute(text("UPDATE users SET role='APPLICANT', must_change_password=false WHERE role='INSTRUCTOR'"))
    db.execute(text("UPDATE application_reviews SET status='UNDER_REVIEW', admin_id=null, reviewed_at=null WHERE status IN ('APPROVED','REJECTED')"))
    db.commit()
    print('Done! All applications reset to UNDER_REVIEW status and role reset to APPLICANT.')
except Exception as e:
    db.rollback()
    print(f'Error: {e}')
finally:
    db.close()
