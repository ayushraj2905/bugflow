import pytest

def test_quality_metrics_endpoint(client):
    res = client.get("/api/v1/analytics/quality-metrics")
    assert res.status_code == 200
    data = res.json()
    assert "fix_rate_percentage" in data
    assert "mean_time_to_resolution_hours" in data
    assert "defect_leakage_rate_percentage" in data
    assert "backlog_health_score" in data

def test_developer_workload_matrix(client):
    res = client.get("/api/v1/analytics/developer-workload")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    dev = data[0]
    assert "full_name" in dev
    assert "active_tasks" in dev
    assert "completed_fixes" in dev
    assert "average_mttr_hours" in dev
    assert "resource_balance" in dev

def test_plotly_charts_config(client):
    res = client.get("/api/v1/analytics/plotly-charts")
    assert res.status_code == 200
    data = res.json()
    assert "defect_trends" in data
    assert "severity_donut" in data
    assert "pipeline_bar" in data

def test_health_check_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert "version" in data
