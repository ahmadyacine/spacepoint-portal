from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, func
import enum
from app.core.database import Base

class SubmissionStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"

class VideoSubmission(Base):
    __tablename__ = "video_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    video_no = Column(Integer, nullable=False) # 1, 2, 3
    youtube_url = Column(String, nullable=False)
    summary_text = Column(String, nullable=True)
    word_count = Column(Integer, default=0)
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.DRAFT, nullable=False)
    submitted_at = Column(DateTime(timezone=True), nullable=True)

class ResearchSubmission(Base):
    __tablename__ = "research_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_path = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    content_text = Column(String, nullable=True)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
