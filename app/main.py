from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.database import engine, get_db
from app.schemas import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
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
        job_url=application.job_url,
        notes=application.notes,
    )

    db.add(db_application)
    db.commit()
    db.refresh(db_application)

    return db_application

@app.get("/applications", response_model=list[ApplicationResponse])
def get_applications(db: Session = Depends(get_db)):
    applications = db.query(models.Application).all()
    return applications

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