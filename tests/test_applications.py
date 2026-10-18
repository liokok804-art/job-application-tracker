import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_create_application():
    response = create_test_application()

    assert response.status_code == 200

    data = response.json()

    assert data["company"] == "Apple"
    assert data["position"] == "Software Engineer Intern"
    assert data["status"] == "SAVED"
    assert data["id"] == 1
    
def test_get_applications():
    create_test_application()

    response = client.get("/applications")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["company"] == "Apple"

def test_get_application_by_id():
    create_test_application()

    response = client.get("/applications/1")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["company"] == "Apple"


def test_get_nonexistent_application():
    response = client.get("/applications/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"
    
def test_update_application():
    create_test_application()

    response = client.patch(
        "/applications/1",
        json={
            "status": "INTERVIEW",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "INTERVIEW"
    assert data["company"] == "Apple"
    
def test_invalid_application():
    response = client.post(
        "/applications",
        json={
            "company": "",
            "position": "Software Engineer",
        },
    )

    assert response.status_code == 422
    
def test_statistics():
    create_test_application(status="INTERVIEW")

    response = client.get("/statistics")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["by_status"]["INTERVIEW"] == 1
    assert data["interview_rate"] == 100.0

def test_delete_application():
    create_test_application()

    response = client.delete("/applications/1")

    assert response.status_code == 200
    assert response.json()["message"] == "Application deleted successfully"

    response = client.get("/applications/1")

    assert response.status_code == 404
    
def create_test_application(
    company="Apple",
    position="Software Engineer Intern",
    status="SAVED",
):
    return client.post(
        "/applications",
        json={
            "company": company,
            "position": position,
            "status": status,
        },
    )
    
def test_filter_by_status():
    create_test_application(
        company="Apple",
        status="INTERVIEW",
    )

    create_test_application(
        company="Amazon",
        status="APPLIED",
    )

    response = client.get(
        "/applications",
        params={"status": "INTERVIEW"},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["company"] == "Apple"
    assert data[0]["status"] == "INTERVIEW"
    
def test_filter_by_company():
    create_test_application(company="Apple")
    create_test_application(company="Amazon")

    response = client.get(
        "/applications",
        params={"company": "Amazon"},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["company"] == "Amazon"
    
def test_sort_by_company():
    create_test_application(company="Google")
    create_test_application(company="Apple")
    create_test_application(company="Amazon")

    response = client.get(
        "/applications",
        params={"sort_by": "company"},
    )

    assert response.status_code == 200

    data = response.json()

    companies = [
        application["company"]
        for application in data
    ]

    assert companies == [
        "Amazon",
        "Apple",
        "Google",
    ]
    
def test_invalid_status():
    response = client.post(
        "/applications",
        json={
            "company": "Apple",
            "position": "Software Engineer",
            "status": "WAITING_FOR_ALIENS",
        },
    )

    assert response.status_code == 422
    
def test_invalid_job_url():
    response = client.post(
        "/applications",
        json={
            "company": "Apple",
            "position": "Software Engineer",
            "job_url": "banana",
        },
    )

    assert response.status_code == 422
    
def test_empty_statistics():
    response = client.get("/statistics")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 0
    assert data["by_status"] == {}
    assert data["interview_rate"] == 0.0
    assert data["offer_rate"] == 0.0