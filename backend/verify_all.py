from app.main import app
from starlette.testclient import TestClient

client = TestClient(app)

def run_tests():
    # 1. Test Dashboard HTML
    r1 = client.get("/")
    assert r1.status_code == 200, f"Dashboard failed: {r1.status_code}"
    assert "BugFlow: Foundation & Base Modules" in r1.text
    print("Dashboard rendered successfully!")

    # 2. Test Issues API
    r2 = client.get("/api/v1/bugs/")
    assert r2.status_code == 200, f"Issues API failed: {r2.status_code}"
    issues_data = r2.json()
    print(f"Retrieved {len(issues_data)} issues via REST API!")

    # 3. Test AI Duplicate Detection
    r3 = client.post("/api/v1/bugs/check-duplicate", json={
        "title": "Minor UI Glitch in menu",
        "description": "Navigation bar overflows on mobile screen"
    })
    assert r3.status_code == 200
    dup_data = r3.json()
    print(f"Duplicate check API passed: {dup_data.get('duplicates_found')} duplicates found!")

    # 4. Test Analytics Metrics API
    r4 = client.get("/api/v1/analytics/metrics")
    assert r4.status_code == 200
    metrics = r4.json()
    print(f"Analytics metrics API passed! Fix rate: {metrics.get('bug_fix_rate')}%, MTTR: {metrics.get('avg_resolution_hours')} hrs")

    # 5. Test Sprint Board HTML
    r5 = client.get("/sprint")
    assert r5.status_code == 200
    print("Sprint Board rendered successfully!")

    # 6. Test Analytics Dashboard HTML
    r6 = client.get("/analytics")
    assert r6.status_code == 200
    print("Analytics Dashboard rendered successfully!")

    # 7. Test GitHub Webhook simulation
    r7 = client.post("/api/v1/webhooks/github", json={
        "commits": [{"message": "Fixes B-001 in navbar", "author": {"name": "J.Doe"}, "id": "abc12345"}]
    })
    assert r7.status_code == 200
    print("GitHub Webhook commit parsing passed!")

    print("\n=======================================================")
    print("ALL AUTOMATED VERIFICATION TESTS PASSED SUCCESSFULLY! ")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
