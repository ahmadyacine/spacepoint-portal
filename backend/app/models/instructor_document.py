from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.core.database import Base

class InstructorDocument(Base):
    __tablename__ = "instructor_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    document_type = Column(String, nullable=False) # e.g. "ID", "Passport", "Personal Picture", "Other"
    file_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
