from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from app.models.user import UserRole
from app.models.submission import SubmissionStatus
from app.models.review import ApplicationStatus
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    phone: str
    email: EmailStr
    password: str
    invitation_code: str
    university: str
    highest_degree: str
    highest_degree_other: Optional[str] = None
    city_of_residence: Optional[str] = None
    deliver_cities: Optional[List[str]] = None
    background_areas: List[str]
    background_other: Optional[str] = None
    has_own_transportation: Optional[bool] = None
    country: Optional[str] = "United Arab Emirates"


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class VideoSummaryUpdate(BaseModel):
    summary_text: str
    status: SubmissionStatus

class AdminReviewUpdate(BaseModel):
    status: ApplicationStatus
    feedback: str
