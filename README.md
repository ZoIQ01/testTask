# Travel Management Application

A Django REST API for planning trips. You can create travel projects, add places to visit (from the Art Institute of Chicago API), take notes, and track which places you've visited.

## Features

- Create and manage travel projects
- Add up to 10 places per project (validated against the Art Institute of Chicago API)
- Mark places as visited
- Attach notes to places

## Getting Started

### With Docker (recommended)

```bash
docker compose up --build
```

App will be available at `http://localhost:8000`

### Without Docker

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Main API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/projects/` | List all projects |
| `POST` | `/api/projects/` | Create a project |
| `GET/PUT/DELETE` | `/api/projects/{id}/` | Get, update, or delete a project |
| `GET` | `/api/projects/{id}/places/` | List places in a project |
| `POST` | `/api/projects/{id}/places/` | Add a place to a project |
| `POST` | `/api/project-places/{id}/mark-visited/` | Mark a place as visited |
| `GET/POST` | `/api/project-places/{id}/notes/` | List or add notes for a place |
| `PUT/DELETE` | `/api/notes/{id}/` | Update or delete a note |

## Notes

- Places must exist in the [Art Institute of Chicago API](https://api.artic.edu/docs/) to be added
- Projects with visited places cannot be deleted
- Admin interface available at `http://localhost:8000/admin/`
