from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.database import engine, get_db
from app.schemas import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationStatus,
    ApplicationUpdate,
    StatisticsResponse,
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Job Application Tracker API"}

@app.post("/applications", response_model=ApplicationResponse)
def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db),
):
    db_application = models.Application(
        company=application.company,
        position=application.position,
        location=application.location,
        status=application.status.value,
        job_url=str(application.job_url) if application.job_url else None,
        notes=application.notes,
    )

    db.add(db_application)
    db.commit()
    db.refresh(db_application)

    return db_application

@app.get("/applications", response_model=list[ApplicationResponse])
def get_applications(
    status: ApplicationStatus | None = None,
    company: str | None = None,
    sort_by: str = "id",
    db: Session = Depends(get_db),
):
    query = db.query(models.Application)

    if status:
        query = query.filter(models.Application.status == status.value)

    if company:
        query = query.filter(models.Application.company == company)

    sort_columns = {
    "id": models.Application.id,
    "company": models.Application.company,
    "status": models.Application.status,
}
    
    sort_column = sort_columns.get(sort_by, models.Application.id)
    
    query = query.order_by(sort_column)
    
    return query.all()

@app.get("/applications/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
):
    application = db.get(models.Application, application_id)

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    return application

@app.patch("/applications/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: int,
    application_update: ApplicationUpdate,
    db: Session = Depends(get_db),
):
    application = db.get(models.Application, application_id)

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    update_data = application_update.model_dump(exclude_unset=True)

    if "status" in update_data:
        update_data["status"] = update_data["status"].value
        
    if "job_url" in update_data and update_data["job_url"] is not None:
        update_data["job_url"] = str(update_data["job_url"])

    for field, value in update_data.items():
        setattr(application, field, value)

    db.commit()
    db.refresh(application)

    return application

@app.delete("/applications/{application_id}")
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
):
    application = db.get(models.Application, application_id)

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    db.delete(application)
    db.commit()

    return {"message": "Application deleted successfully"}

@app.get("/statistics", response_model=StatisticsResponse)
def get_statistics(db: Session = Depends(get_db)):
    applications = db.query(models.Application).all()

    total = len(applications)

    by_status = {}

    for application in applications:
        by_status[application.status] = (
            by_status.get(application.status, 0) + 1
        )

    interview_count = by_status.get("INTERVIEW", 0)
    offer_count = by_status.get("OFFER", 0)

    interview_rate = (
        round(interview_count / total * 100, 2)
        if total > 0
        else 0.0
    )

    offer_rate = (
        round(offer_count / total * 100, 2)
        if total > 0
        else 0.0
    )

    return {
        "total": total,
        "by_status": by_status,
        "interview_rate": interview_rate,
        "offer_rate": offer_rate,
    }
    
# uvicorn app.main:app --reload