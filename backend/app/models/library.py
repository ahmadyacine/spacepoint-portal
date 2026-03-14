from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class LibraryModule(Base):
    __tablename__ = "library_modules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resources = relationship("LibraryResource", back_populates="module", cascade="all, delete-orphan")


class LibraryResource(Base):
    __tablename__ = "library_resources"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    format = Column(String, nullable=False) # e.g., 'PDF', 'PPTX'
    file_path = Column(String, nullable=False) # Local file path
    uploader_id = Column(Integer, ForeignKey("users.id"))
    module_id = Column(Integer, ForeignKey("library_modules.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    module = relationship("LibraryModule", back_populates="resources")
