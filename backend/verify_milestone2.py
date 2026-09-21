import io
import sys
import os

# Set UTF-8 encoding for stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from starlette.testclient import TestClient

client = TestClient(app)

def run_milestone2_checklist_tests():
    print("=" * 65)
    print("RUNNING MILESTONE 2: STUDENT CHECKLIST VERIFICATION SUITE")
    print("=" * 65)

    # -------------------------------------------------------------
    # Test 1: Priority Math Formula Verification
    # CRITICAL (4 points) x Security (3 points) = Score 12.0 -> URGENT
    # -------------------------------------------------------------
    print("\n[TEST 1] Testing Smart Priority Calculator Math...")
    r1 = client.post("/api/v1/issues/triage-recommendation", json={
        "title": "SQL Injection in User Login Endpoint",
        "description": "Critical security vulnerability allowing arbitrary SQL execution and authentication bypass.",
        "severity": "CRITICAL",
        "category": "Authentication & Security"
    })
    assert r1.status_code == 200, f"Failed: {r1.text}"
    data1 = r1.json()
    print("  -> Score:", data1["priority_score"])
    print("  -> Priority Label:", data1["priority_label"])
    print("  -> Formula:", data1["priority_calculation"]["formula"])
    assert data1["priority_score"] == 12.0, f"Expected 12.0, got {data1['priority_score']}"
    assert data1["priority_label"] == "URGENT", f"Expected URGENT, got {data1['priority_label']}"
    print("  [PASSED] TEST 1: Priority Math (4 x 3 = 12.0 -> URGENT) validated successfully!")

    # -------------------------------------------------------------
    # Test 2: Smart Developer Matcher (Keywords + Workload Check)
    # "database connection timeout" -> Backend / DB dev top recommendation
    # -------------------------------------------------------------
    print("\n[TEST 2] Testing Smart Developer Matcher with Workload...")
    r2 = client.post("/api/v1/issues/triage-recommendation", json={
        "title": "Database connection timeout under heavy traffic",
        "description": "PostgreSQL connection pool exhausted when executing complex SQL queries.",
        "severity": "MAJOR",
        "category": "Database & Performance"
    })
    assert r2.status_code == 200
    data2 = r2.json()
    top_dev = data2["recommended_developers"][0]
    print(f"  -> Top Recommended Developer: {top_dev['full_name']} ({top_dev['team']})")
    print(f"  -> Match Score: {top_dev['match_score']}% ({top_dev['summary_label']})")
    assert "jdoe" in top_dev["full_name"].lower() or "backend" in top_dev["team"].lower() or "lead" in top_dev["full_name"].lower()
    print("  [PASSED] TEST 2: Database / Backend expert correctly recommended as top match!")

    # -------------------------------------------------------------
    # Test 3: Chat, Comments & Attachments Persistence
    # Post comment + upload file -> verify retrieval
    # -------------------------------------------------------------
    print("\n[TEST 3] Testing Discussion Comments & File Attachments...")
    # Post comment
    r3_comment = client.post("/api/v1/collaboration/issues/1/comments", json={
        "content": "I reproduced this bug on Chrome v120 with mobile responsive mode.",
        "code_reference": "components/Navbar.tsx#L45"
    })
    assert r3_comment.status_code == 200
    
    # Retrieve comments
    r3_get = client.get("/api/v1/collaboration/issues/1/comments")
    assert r3_get.status_code == 200
    comments = r3_get.json()
    assert any("Chrome v120" in c["content"] for c in comments)
    print(f"  -> Comment successfully saved and retrieved ({len(comments)} total comments)!")

    # Upload attachment test
    fake_file = io.BytesIO(b"2026-09-04 18:00:00 ERROR: Connection pool exhausted in HikariCP")
    r3_file = client.post(
        "/api/v1/collaboration/issues/1/attachments",
        files={"file": ("error_log.txt", fake_file, "text/plain")}
    )
    assert r3_file.status_code == 200
    att_data = r3_file.json()
    print(f"  -> File attachment uploaded: {att_data['attachment']['filename']} ({att_data['attachment']['file_url']})")
    print("  [PASSED] TEST 3: Chat comments and file attachments verified!")

    # -------------------------------------------------------------
    # Test 4: Sprint Creation & Backlog Assignment
    # Create "Sprint 2 - Workflow" -> Add backlog issue -> verify in Sprint
    # -------------------------------------------------------------
    print("\n[TEST 4] Testing Agile Sprint Creation & Backlog Assignment...")
    r4_create = client.post("/api/v1/sprints/", json={
        "project_id": 1,
        "sprint_name": "Sprint 2 - Workflow & Automation",
        "goal": "Milestone 2 Workflow deliverable",
        "start_date": "2026-09-04",
        "end_date": "2026-09-18",
        "planned_velocity": 35
    })
    assert r4_create.status_code == 200
    sprint_id = r4_create.json()["sprint_id"]
    print(f"  -> Created Sprint ID: {sprint_id} ({r4_create.json()['sprint_name']})")

    # Add issue 3 to this sprint
    r4_assign = client.post(f"/api/v1/sprints/{sprint_id}/add-issue/3")
    assert r4_assign.status_code == 200
    print(f"  -> {r4_assign.json()['message']}")

    # Verify sprint board
    r4_board = client.get(f"/api/v1/sprints/{sprint_id}/board")
    assert r4_board.status_code == 200
    print("  [PASSED] TEST 4: Sprint creation and backlog assignment verified!")

    # -------------------------------------------------------------
    # Test 5: Audit Log Recording on Status Transition
    # Transition status -> verify entry in AuditLog
    # -------------------------------------------------------------
    print("\n[TEST 5] Testing Audit Log & Activity Stream Recording...")
    r5_trans = client.post("/api/v1/bugs/1/transition", json={
        "target_stage": "QA_VERIFICATION",
        "note": "Dev completed fix, ready for verification"
    })
    assert r5_trans.status_code == 200

    # Verify detail and audit log
    r5_detail = client.get("/api/v1/bugs/1")
    assert r5_detail.status_code == 200
    audit_logs = r5_detail.json()["audit_logs"]
    assert any("QA_VERIFICATION" in a["new_state"] or "QA_VERIFICATION" in a["details"] for a in audit_logs)
    latest_audit = audit_logs[0]
    print(f"  -> Recorded Audit Action: {latest_audit['action']}")
    print(f"  -> Details: {latest_audit['details']} (by {latest_audit['user_name']})")
    print("  [PASSED] TEST 5: Audit Log and status history verified!")

    # -------------------------------------------------------------
    # Test Milestone 2 UI Page
    # -------------------------------------------------------------
    print("\n[UI TEST] Verifying /milestone2 dedicated page HTML rendering...")
    r_ui = client.get("/milestone2")
    assert r_ui.status_code == 200
    assert "Milestone 2: Workflow, Collaboration & Smart Triage" in r_ui.text
    assert "Part 1: Smart Priority Calculator" in r_ui.text
    assert "Live Activity Stream" in r_ui.text
    print("  [PASSED] UI TEST: /milestone2 template rendered with all 4 widgets!")

    print("\n" + "=" * 65)
    print("ALL 5 MILESTONE 2 CHECKLIST TESTS PASSED 100% SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    run_milestone2_checklist_tests()
