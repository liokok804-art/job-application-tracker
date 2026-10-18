from enum import Enum

from pydantic import BaseModel

class ApplicationStatus(str, Enum):
    SAVED = "SAVED"
    APPLIED = "APPLIED"
    OA = "OA"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"
    
class ApplicationCreate(BaseModel):
    company: str
    position: str
    location: str | None = None
    status: ApplicationStatus = ApplicationStatus.SAVED
    job_url: str | None = None
    notes: str | None = None

class ApplicationResponse(ApplicationCreate):
    id: int

    model_config = {"from_attributes": True}
    
class ApplicationUpdate(BaseModel):
    company: str | None = None
    position: str | None = None
    location: str | None = None
    status: ApplicationStatus | None = None
    job_url: str | None = None
    notes: str | None = None