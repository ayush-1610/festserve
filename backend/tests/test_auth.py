# backend/tests/test_auth.py

import pytest
from fastapi.testclient import TestClient

from festserve_api.main import app
from festserve_api.create_users import create_users

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def seed_users():
    # ensure test users are in the DB before any tests run
    create_users()
    yield

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
