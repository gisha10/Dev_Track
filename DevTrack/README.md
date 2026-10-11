# DevTrack

A small backend API for tracking engineering issues (kind of like a very basic GitHub Issues). Reporters file issues, each issue has a status and a priority. Data is stored in two JSON files instead of a database.

Built with Django, no Django models/ORM — the entities are plain Python classes in `issues/models.py`.

## How to run

```bash
git clone <your-repo-url>
cd devtrack

python -m venv venv
venv\Scripts\activate       

pip install -r requirements.txt
python manage.py runserver
```

Server runs at `http://127.0.0.1:8000/`. All endpoints are under `/api/`.

(You'll see a warning about unapplied migrations when starting — that's fine, the app doesn't use the database.)

## Project structure

```
devtrack/
├── manage.py
├── issues.json
├── reporters.json
├── devtrack/
│   ├── settings.py
│   └── urls.py
└── issues/
    ├── models.py     # BaseEntity, Reporter, Issue, CriticalIssue, LowPriorityIssue
    ├── views.py
    └── urls.py
```

## Endpoints

### Reporters

| Method | URL | What it does |
|---|---|---|
| POST | `/api/reporters/` | Creates a new reporter |
| GET | `/api/reporters/` | Returns all reporters |
| GET | `/api/reporters/?id=1` | Returns one reporter by id (404 if not found) |

Sample body for POST:

```json
{
    "id": 1,
    "name": "Isha Gangamwar",
    "email": "Isha@example.com",
    "team": "backend"
}
```

### Issues

| Method | URL | What it does |
|---|---|---|
| POST | `/api/issues/` | Creates a new issue |
| GET | `/api/issues/` | Returns all issues |
| GET | `/api/issues/?id=1` | Returns one issue by id (404 if not found) |
| GET | `/api/issues/?status=open` | Returns all issues with that status |

Sample body for POST:

```json
{
    "id": 1,
    "title": "Login button not working on mobile",
    "description": "Users on iOS 17 cannot tap the login button",
    "status": "open",
    "priority": "critical",
    "reporter_id": 1
}
```

Response (201):

```json
{
    "id": 1,
    "title": "Login button not working on mobile",
    "description": "Users on iOS 17 cannot tap the login button",
    "status": "open",
    "priority": "critical",
    "reporter_id": 1,
    "created_at": "2026-10-11 11:09:36.855991",
    "message": "[URGENT] Login button not working on mobile — needs immediate attention"
}
```

The `message` depends on priority:
- `critical` → `CriticalIssue`
- `low` → `LowPriorityIssue`
- `medium` / `high` → base `Issue`

Allowed values:
- status: `open`, `in_progress`, `resolved`, `closed`
- priority: `low`, `medium`, `high`, `critical`

### Errors

| Case | Status | Response |
|---|---|---|
| Empty title | 400 | `{"error": "Title cannot be empty"}` |
| Wrong status / priority | 400 | `{"error": "Invalid status. Allowed: ..."}` |
| Duplicate id | 400 | `{"error": "Issue with this id already exists"}` |
| Issue id not found | 404 | `{"error": "Issue not found"}` |
| reporter_id doesn't exist | 404 | `{"error": "Reporter not found"}` |

