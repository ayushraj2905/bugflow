# BugFlow REST API Reference Manual
## OpenAPI 3.0 Standard & Payload Specifications

---

### Base URLs
* **Local Development:** `http://127.0.0.1:8000`
* **Interactive Swagger UI:** `http://127.0.0.1:8000/docs`
* **ReDoc Documentation:** `http://127.0.0.1:8000/redoc`

---

## 1. Authentication & User Portals (`/api/v1/auth`)

### `POST /api/v1/auth/login`
Authenticates a user and issues a JWT token.
* **Request Payload:**
```json
{
  "username": "jdoe",
  "password": "password123"
}
```
* **Response (200 OK):**
```json
{
  "message": "Welcome back, J.Doe!",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "username": "jdoe",
    "full_name": "J.Doe",
    "role": "DEVELOPER",
    "team": "Backend Core"
  }
}
```

### `POST /api/v1/auth/switch-user/{user_id}`
Fast session switching between developers for demo and testing.

---

## 2. Issue Management & Smart Triage (`/api/v1/bugs`)

### `POST /api/v1/issues/triage-recommendation`
Calculates mathematical priority score ($\text{Severity Weight} \times \text{Category Urgency Weight}$) and matches developers.
* **Request Payload:**
```json
{
  "title": "SQL Injection in User Login Endpoint",
  "description": "Critical security vulnerability allowing arbitrary execution.",
  "severity": "CRITICAL",
  "category": "Authentication & Security"
}
```
* **Response (200 OK):**
```json
{
  "predicted_severity": "CRITICAL",
  "predicted_category": "Authentication & Security",
  "priority_score": 12.0,
  "priority_label": "URGENT",
  "priority_calculation": {
    "formula": "4 (Severity) × 3 (High Urgency) = 12.0",
    "action_badge": "Drop everything and fix now!"
  },
  "recommended_developers": [
    {
      "dev_id": 1,
      "full_name": "Admin (Lead Dev)",
      "match_score": 95.0,
      "active_tasks_count": 0
    }
  ]
}
```

### `GET /api/v1/bugs/?skip=0&limit=50`
High-performance paginated search with filtering by `stage`, `severity`, `priority`, and `assignee_id`.

---

## 3. Collaboration, Comments & Attachments (`/api/v1/collaboration`)

### `POST /api/v1/collaboration/issues/{id}/comments`
* **Request Payload:**
```json
{
  "content": "I reproduced this bug on Chrome v120 with mobile viewport.",
  "code_reference": "components/Navbar.tsx#L45"
}
```

### `POST /api/v1/collaboration/issues/{id}/attachments`
* **Multipart Form Data:** `file: [binary .png, .jpg, .log, .pdf]`

---

## 4. Agile Sprint Planning & Velocity (`/api/v1/sprints`)

### `POST /api/v1/sprints/`
* **Request Payload:**
```json
{
  "project_id": 1,
  "sprint_name": "Sprint 4 - Optimization",
  "goal": "Milestone 4 delivery",
  "start_date": "2026-09-22",
  "end_date": "2026-10-06",
  "planned_velocity": 40
}
```

### `POST /api/v1/sprints/{id}/complete`
Marks sprint completed and computes delivered velocity.

---

## 5. CI/CD Git Webhooks (`/api/v1/webhooks`)

### `POST /api/v1/webhooks/git`
* **Request Payload:**
```json
{
  "message": "Merge PR #45: fixes #2 login password crash",
  "commit_id": "a7f8c92",
  "author": "Sarah Connor"
}
```
* **Behavior:** Automatically transitions Bug #2 to `QA_VERIFICATION` and logs an immutable audit entry.

---

## 6. Software Quality Telemetry & Exports (`/api/v1/analytics`)

* `GET /api/v1/analytics/quality-metrics`: Returns Fix Rate %, MTTR, Leakage %, and Health Score.
* `GET /api/v1/analytics/developer-workload`: Returns active tasks, completed fixes, and individual MTTR for all team members.
* `GET /api/v1/analytics/plotly-charts`: Returns Plotly chart JSON specs.
* `GET /api/v1/export/pdf`: Downloads formatted Executive PDF Quality Report.
* `GET /api/v1/export/csv`: Downloads Excel-ready raw bug registry.
* `GET /health`: Platform health check.
