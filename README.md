# Job Application Tracker

A REST API for managing and tracking job applications, built with Python, FastAPI, SQLAlchemy, and SQLite.

The project supports CRUD operations, application status tracking, filtering, sorting, statistics, input validation, and automated API testing.

## Features

- Create, retrieve, update, and delete job applications
- Track application status:
  - SAVED
  - APPLIED
  - OA
  - INTERVIEW
  - OFFER
  - REJECTED
  - WITHDRAWN
- Filter applications by status or company
- Sort applications by ID, company, or status
- View application statistics
- Validate request data with Pydantic
- Handle missing resources with HTTP 404 responses
- Automatically generate interactive API documentation with FastAPI
- Test API behavior with pytest and an isolated SQLite test database

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- pytest
- HTTPX

## Project Structure

```text
job-application-tracker/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── tests/
│   └── test_applications.py
├── .gitignore
├── README.md
└── requirements.txt
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/applications` | Create an application |
| GET | `/applications` | Get applications with optional filtering and sorting |
| GET | `/applications/{application_id}` | Get an application by ID |
| PATCH | `/applications/{application_id}` | Partially update an application |
| DELETE | `/applications/{application_id}` | Delete an application |
| GET | `/statistics` | Get application statistics |

### Filtering and Sorting

`GET /applications` supports optional query parameters:

- `status` — filter by application status
- `company` — filter by company
- `sort_by` — sort by `id`, `company`, or `status`

Example:

```text
GET /applications?status=INTERVIEW&sort_by=company
```

## Setup

Clone the repository and enter the project directory:

```bash
git clone https://github.com/liokok804-art/job-application-tracker.git
cd job-application-tracker
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the API

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Example

Create a job application:

```json
{
  "company": "Apple",
  "position": "Software Engineer Intern",
  "location": "Tokyo",
  "status": "APPLIED",
  "job_url": "https://example.com/jobs/123",
  "notes": "Applied through the careers page."
}
```

Example response:

```json
{
  "company": "Apple",
  "position": "Software Engineer Intern",
  "location": "Tokyo",
  "status": "APPLIED",
  "job_url": "https://example.com/jobs/123",
  "notes": "Applied through the careers page.",
  "id": 1
}
```

## Testing

The project includes automated API tests for CRUD operations, validation, filtering, sorting, error handling, and statistics.

Tests use an isolated in-memory SQLite database so development data is not modified.

Run the test suite with:

```bash
python -m pytest
```

Run tests with detailed output:

```bash
python -m pytest -v
```

## Design

The application separates API validation from database persistence:

```text
Client
  ↓
FastAPI
  ↓
Pydantic Validation
  ↓
SQLAlchemy ORM
  ↓
SQLite
```

FastAPI dependency injection is used to manage database sessions. During testing, the database dependency is overridden with an isolated test database.

## Future Improvements

Possible improvements for a production-scale version include:

- Database migrations with Alembic
- PostgreSQL instead of SQLite
- Pagination for large application collections
- SQL-based aggregation for statistics
- Authentication and per-user application data
- More flexible search and filtering