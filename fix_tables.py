import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from app.core.database import Base
import app.models  # This triggers __init__.py

engine = create_engine('postgresql://postgres:Ahmad213%23@localhost:5432/portal')
Base.metadata.create_all(engine)
print("Tables created successfully!")
