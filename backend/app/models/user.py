from sqlalchemy import Column, Integer, String, DateTime, func, Enum
import enum
from app.core.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    APPLICANT = "APPLICANT"
    INSTRUCTOR = "INSTRUCTOR"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.APPLICANT, nullable=False)
    invitation_code_used = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    must_change_password = Column(Integer, default=False, nullable=False) # Storing boolean as Integer for SQLite/PG compatibility often, but let's use Boolean if imported
    temp_password_last_set_at = Column(DateTime(timezone=True), nullable=True)
