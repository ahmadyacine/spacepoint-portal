from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from app.core.database import Base

class ApplicantProfile(Base):
    __tablename__ = "applicant_profiles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    university = Column(String, nullable=False)
    highest_degree = Column(String, nullable=False)
    highest_degree_other = Column(String, nullable=True)
    city_of_residence = Column(String, nullable=False)
    deliver_cities_json = Column(String, nullable=False) # Storing as JSON string
    background_areas_json = Column(String, nullable=False) # Storing as JSON string
    background_other = Column(String, nullable=True)
