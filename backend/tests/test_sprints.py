import pytest

def test_create_sprint(client):
    res = client.post("/api/v1/sprints/", json={
        "project_id": 1,
        "sprint_name": "PyTest Sprint 4 - Performance & Final",
        "goal": "Milestone 4 verification and delivery",
        "start_date": "2026-09-22",
        "end_date": "2026-10-06",
        "planned_velocity": 40
    })
    assert res.status_code == 200
    data = res.json()
    assert "sprint_id" in data
    assert data["status"] == "ACTIVE"

def test_add_issue_to_sprint(client):
    # Add Issue 1 to Sprint 1
    res = client.post("/api/v1/sprints/1/add-issue/1")
    assert res.status_code == 200
    assert "successfully added" in res.json()["message"]

def test_sprint_board_columns(client):
    res = client.get("/api/v1/sprints/1/board")
    assert res.status_code == 200
    data = res.json()
    assert "columns" in data
    assert "REPORTED" in data["columns"]
    assert "IN_PROGRESS" in data["columns"]

def test_complete_sprint_and_velocity(client):
    res = client.post("/api/v1/sprints/1/complete")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "COMPLETED"
    assert "final_velocity" in data
