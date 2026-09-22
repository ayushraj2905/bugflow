import pytest
from app.services.auth_service import hash_password, verify_password, create_access_token

def test_password_hashing():
    plain = "secret123"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_jwt_token_issuance():
    token = create_access_token(data={"sub": "testuser", "role": "DEVELOPER"})
    assert isinstance(token, str)
    assert len(token) > 20

def test_login_success(client):
    res = client.post("/api/v1/auth/login", json={
        "username": "jdoe",
        "password": "password123"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["username"] == "jdoe"
    assert data["user"]["role"] == "DEVELOPER"

def test_login_invalid_credentials(client):
    res = client.post("/api/v1/auth/login", json={
        "username": "jdoe",
        "password": "wrongpassword999"
    })
    assert res.status_code == 401
    assert "Invalid username or password" in res.json()["detail"]

def test_switch_user_account(client):
    res = client.post("/api/v1/auth/switch-user/3")
    assert res.status_code == 200
    data = res.json()
    assert data["user"]["id"] == 3
    assert data["user"]["role"] == "QA_TESTER"

def test_logout(client):
    res = client.post("/api/v1/auth/logout")
    assert res.status_code == 200
    assert "Logged out successfully" in res.json()["message"]
