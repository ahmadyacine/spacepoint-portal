from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class TrainingModule(Base):
    __tablename__ = "training_modules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    videos = relationship("TrainingVideo", back_populates="module", cascade="all, delete-orphan", order_by="TrainingVideo.sort_order")


class TrainingVideo(Base):
    __tablename__ = "training_videos"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("training_modules.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True) # Long format text or HTML
    video_path = Column(String, nullable=False) # Local file path to the video
    sort_order = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    module = relationship("TrainingModule", back_populates="videos")
    progress_records = relationship("UserTrainingProgress", back_populates="video", cascade="all, delete-orphan")


class UserTrainingProgress(Base):
    __tablename__ = "user_training_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(Integer, ForeignKey("training_videos.id", ondelete="CASCADE"), nullable=False, index=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User")
    video = relationship("TrainingVideo", back_populates="progress_records")
