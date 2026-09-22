import pytest
from app.services.triage_engine import TriageEngine
from app.services.duplicate_detector import DuplicateDetector

def test_priority_score_calculation_urgent():
    # CRITICAL (4 points) x High Urgency (3 points) = 12.0 -> URGENT
    calc = TriageEngine.calculate_priority_score("CRITICAL", "Authentication & Security")
    assert calc["priority_score"] == 12.0
    assert calc["priority_label"] == "URGENT"

def test_priority_score_calculation_medium():
    # MINOR (2 points) x Medium Urgency (2 points) = 4.0 -> MEDIUM
    calc = TriageEngine.calculate_priority_score("MINOR", "API & Integrations")
    assert calc["priority_score"] == 4.0
    assert calc["priority_label"] == "MEDIUM"

def test_create_issue_endpoint(client):
    payload = {
        "project_id": 1,
        "category_id": 1,
        "title": "PyTest Simulated Defect in API",
        "description": "500 Internal server error when payload exceeds 1MB limit.",
        "severity": "MAJOR",
        "priority": "HIGH"
    }
    res = client.post("/api/v1/bugs/", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "issue_id" in data
    assert "issue_key" in data
    assert data["issue_key"].startswith("BF-")

def test_issue_workflow_transitions(client):
    res = client.post("/api/v1/bugs/1/transition", json={
        "target_stage": "IN_PROGRESS",
        "note": "Developer began active debugging"
    })
    assert res.status_code == 200
    assert res.json()["dev_stage"] == "IN_PROGRESS"

def test_duplicate_detector():
    from app.models.issue import Issue
    mock_issues = [
        Issue(id=1, issue_key="BF-001", title="Database connection timeout on checkout", description="HikariCP connection pool exhausted", dev_stage="OPEN"),
        Issue(id=2, issue_key="BF-002", title="Button alignment in login modal", description="CSS padding mismatch", dev_stage="CLOSED")
    ]
    dupes = DuplicateDetector.find_potential_duplicates(
        "Database connection timeout on checkout page",
        "HikariCP connection pool exhausted during payment",
        mock_issues
    )
    assert len(dupes) >= 1
    assert dupes[0]["id"] == 1

def test_issues_pagination(client):
    res = client.get("/api/v1/bugs/?skip=0&limit=3")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) <= 3
