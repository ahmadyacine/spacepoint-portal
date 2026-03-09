import json
import logging
from sqlalchemy.orm import Session
from app.models.checklist import Module, ModuleSection, ChecklistItem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_modules(db: Session, json_path: str = '../seed_data.json'):
    # Check if data already exists
    if db.query(Module).first():
        logger.info("Modules already seeded. Skipping.")
        return

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for mod_data in data:
            # Create Module
            module = Module(
                title=mod_data['module_title'],
                sort_order=mod_data['sort_order']
            )
            db.add(module)
            db.flush() # Get module.id

            for sec_data in mod_data.get('sections', []):
                section_id = None
                
                # Create Section if it exists
                if sec_data.get('section_title'):
                    section = ModuleSection(
                        module_id=module.id,
                        title=sec_data['section_title'],
                        sort_order=sec_data['sort_order']
                    )
                    db.add(section)
                    db.flush()
                    section_id = section.id
                
                # Create Items
                for item_data in sec_data.get('items', []):
                    item = ChecklistItem(
                        module_id=module.id,
                        section_id=section_id,
                        item_code=item_data['item_code'],
                        title=item_data['title'],
                        description=item_data['description'],
                        sort_order=item_data['sort_order'],
                        is_required=True
                    )
                    db.add(item)
                    
        db.commit()
        logger.info("Successfully seeded Space.Terms.pdf modules and checklists!")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding modules: {e}")
        raise e

if __name__ == "__main__":
    import sys
    import os
    from dotenv import load_dotenv
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Load .env before initializing DB connection directly
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))
    
    engine = create_engine(os.environ.get("DATABASE_URL"))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        seed_modules(db)
    finally:
        db.close()
