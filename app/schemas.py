from enum import Enum

from pydantic import BaseModel, Field, HttpUrl

class ApplicationStatus(str, Enum):
    SAVED = "SAVED"
    APPLIED = "APPLIED"
    OA = "OA"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"
    
class ApplicationCreate(BaseModel):
    company: str = Field(min_length=1, max_length=100)
    position: str = Field(min_length=1, max_length=150)
    location: str | None = Field(default=None, max_length=100)
    status: ApplicationStatus = ApplicationStatus.SAVED
    job_url: HttpUrl | None = None
    notes: str | None = Field(default=None, max_length=1000)

class ApplicationResponse(ApplicationCreate):
    id: int

    model_config = {"from_attributes": True}
    
class ApplicationUpdate(BaseModel):
    company: str | None = Field(default=None, min_length=1, max_length=100)
    position: str | None = Field(default=None, min_length=1, max_length=150)
    location: str | None = Field(default=None, max_length=100)
    status: ApplicationStatus | None = None
    job_url: HttpUrl | None = None
    notes: str | None = Field(default=None, max_length=1000)
    
class StatisticsResponse(BaseModel):
    total: int
    by_status: dict[str, int]
    interview_rate: float
    offer_rate: float