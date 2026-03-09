from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    sort_order = Column(Integer, nullable=False, default=1)

    sections = relationship("ModuleSection", back_populates="module", cascade="all, delete-orphan")
    checklist_items = relationship("ChecklistItem", back_populates="module", cascade="all, delete-orphan")

class ModuleSection(Base):
    __tablename__ = "module_sections"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    sort_order = Column(Integer, nullable=False, default=1)

    module = relationship("Module", back_populates="sections")
    checklist_items = relationship("ChecklistItem", back_populates="section", cascade="all, delete-orphan")

class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    section_id = Column(Integer, ForeignKey("module_sections.id", ondelete="CASCADE"), nullable=True)
    item_code = Column(String, nullable=False) # e.g., "1.1"
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    sort_order = Column(Integer, nullable=False, default=1)
    is_required = Column(Boolean, default=True, nullable=False)

    module = relationship("Module", back_populates="checklist_items")
    section = relationship("ModuleSection", back_populates="checklist_items")
    progress_records = relationship("UserChecklistProgress", back_populates="checklist_item", cascade="all, delete-orphan")

class UserChecklistProgress(Base):
    __tablename__ = "user_checklist_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    checklist_item_id = Column(Integer, ForeignKey("checklist_items.id", ondelete="CASCADE"), nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", foreign_keys=[user_id])
    checklist_item = relationship("ChecklistItem", back_populates="progress_records")

class ModuleSubmission(Base):
    __tablename__ = "module_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    notes_text = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="SUBMITTED") # SUBMITTED, APPROVED, REJECTED
    feedback = Column(Text, nullable=True)

    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewer_admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    reviewer = relationship("User", foreign_keys=[reviewer_admin_id])
    module = relationship("Module")
