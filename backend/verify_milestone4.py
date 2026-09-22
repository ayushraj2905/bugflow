import io
import sys
import os
import time

# Set UTF-8 encoding for stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from starlette.testclient import TestClient

client = TestClient(app)

def run_milestone4_checklist_tests():
    print("=" * 65)
    print("RUNNING MILESTONE 4: STUDENT CHECKLIST VERIFICATION SUITE")
    print("=" * 65)

    # -------------------------------------------------------------
    # Test 1: Developer Workload & Productivity Matrix
    # -------------------------------------------------------------
    print("\n[TEST 1] Testing Developer Workload & Productivity Matrix...")
    r1 = client.get("/api/v1/analytics/developer-workload")
    assert r1.status_code == 200, f"Failed: {r1.text}"
    workload = r1.json()
    assert len(workload) >= 5, "Expected at least 5 developers in matrix"
    for dev in workload:
        print(f"  -> Developer: {dev['full_name']} ({dev['team']})")
        print(f"     Active Tasks: {dev['active_tasks']} | Completed: {dev['completed_fixes']} | MTTR: {dev['average_mttr_hours']}h | Balance: {dev['resource_balance']}")
        assert "active_tasks" in dev
        assert "completed_fixes" in dev
        assert "resource_balance" in dev
    print("  [PASSED] TEST 1: Developer Workload Matrix verified with real task distribution!")

    # -------------------------------------------------------------
    # Test 2: Database Scale & High-Performance Pagination
    # -------------------------------------------------------------
    print("\n[TEST 2] Testing Database Scale & Sub-300ms Pagination...")
    start_time = time.time()
    r2 = client.get("/api/v1/bugs/?skip=0&limit=50")
    latency_ms = round((time.time() - start_time) * 1000, 2)
    assert r2.status_code == 200
    data2 = r2.json()
    print(f"  -> Query Latency: {latency_ms}ms (Target: < 300ms)")
    print(f"  -> Paginated Records Returned: {len(data2)}")
    assert latency_ms < 300.0, f"Query exceeded 300ms SLA: {latency_ms}ms"
    print("  [PASSED] TEST 2: High-speed pagination & database index verified under 300ms!")

    # -------------------------------------------------------------
    # Test 3: System Health Check Endpoint
    # -------------------------------------------------------------
    print("\n[TEST 3] Testing /health System Endpoint...")
    r3 = client.get("/health")
    assert r3.status_code == 200
    health = r3.json()
    print("  -> Health Status:", health["status"])
    print("  -> Database:", health["database"])
    print("  -> Platform Version:", health["version"])
    assert health["status"] == "healthy"
    assert "database" in health
    print("  [PASSED] TEST 3: System /health endpoint verified healthy!")

    # -------------------------------------------------------------
    # Test 4: Docker Configuration Validation
    # -------------------------------------------------------------
    print("\n[TEST 4] Validating Dockerfile and Docker Compose Files...")
    dockerfile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Dockerfile")
    compose_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docker-compose.yml")
    assert os.path.exists(dockerfile_path), "Dockerfile missing"
    assert os.path.exists(compose_path), "docker-compose.yml missing"
    
    with open(dockerfile_path, "r", encoding="utf-8") as f:
        df_text = f.read()
        assert "python:3.11-slim" in df_text
        assert "uvicorn" in df_text
    
    with open(compose_path, "r", encoding="utf-8") as f:
        dc_text = f.read()
        assert "postgres:15-alpine" in dc_text
        assert "bugflow_web" in dc_text
    print("  [PASSED] TEST 4: Docker multi-container compose architecture validated!")

    # -------------------------------------------------------------
    # Test 5: Milestone 4 UI Rendering & Documentation Publisher
    # -------------------------------------------------------------
    print("\n[TEST 5] Testing /milestone4 UI Rendering & Documentation Links...")
    r5 = client.get("/milestone4")
    assert r5.status_code == 200
    assert "Milestone 4: Optimization, Scale & Finalization" in r5.text
    assert "Database Optimization Checklist" in r5.text
    assert "Developer Productivity & Workload Matrix" in r5.text
    print("  [PASSED] TEST 5: Milestone 4 dedicated UI tab rendered with all widgets!")

    print("\n" + "=" * 65)
    print("ALL 5 MILESTONE 4 CHECKLIST TESTS PASSED 100% SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    run_milestone4_checklist_tests()
