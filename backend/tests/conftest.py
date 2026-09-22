import pytest
import sys
import os
from starlette.testclient import TestClient

# Add app to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import SessionLocal, engine, Base

@pytest.fixture(scope="session")
def client():
    # Provide TestClient
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="session")
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
