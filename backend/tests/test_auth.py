# backend/tests/test_auth.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from festserve_api.main import app
from festserve_api.create_users import create_users
from festserve_api.database import Base, get_db

# Use an in-memory SQLite database for isolation
engine_test = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_test
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def prepare_and_seed_db():
    """Create tables, override DB dependency, and seed test users."""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine_test)
    db = TestingSessionLocal()
    create_users(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine_test)
    app.dependency_overrides.pop(get_db, None)


def test_token_and_me_flow():
    # 1) request a token for the advertiser
    resp = client.post(
        "/api/auth/token",
        data={
            "username": "adv@example.com",
            "password": "advpassword123",
            "scope": "advertiser",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "access_token" in body
    token = body["access_token"]

    # 2) call /api/auth/me with the Bearer token
    resp2 = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp2.status_code == 200, resp2.text
    me = resp2.json()
    assert me["contact_email"] == "adv@example.com"
