from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSON
from app.core.database import Base

class ApplicantProfile(Base):
    __tablename__ = "applicant_profiles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    university = Column(String, nullable=False)
    highest_degree = Column(String, nullable=False)
    highest_degree_other = Column(String, nullable=True)
    city_of_residence = Column(String, nullable=True)
    deliver_cities_json = Column(String, nullable=True) # Storing as JSON string
    background_areas_json = Column(String, nullable=False) # Storing as JSON string
    background_other = Column(String, nullable=True)
    has_own_transportation = Column(Boolean, default=False, nullable=True)
    country = Column(String, default="United Arab Emirates", nullable=True)

