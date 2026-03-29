from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, func
import enum
from app.core.database import Base

class ApplicationStatus(str, enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    UNDER_REVIEW = "UNDER_REVIEW"
    PHASE_1_APPROVED = "PHASE_1_APPROVED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class ApplicationReview(Base):
    __tablename__ = "application_reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.IN_PROGRESS, nullable=False)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    feedback = Column(String, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
