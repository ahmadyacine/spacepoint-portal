from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.core.database import Base

class InvitationCode(Base):
    __tablename__ = "invitation_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    max_uses = Column(Integer, default=20, nullable=False)
    used_count = Column(Integer, default=0, nullable=False)
    source_type = Column(String, nullable=True)
    source_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
