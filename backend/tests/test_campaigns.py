import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from festserve_api.main import app
from festserve_api.database import Base, get_db
from festserve_api.create_users import create_users

# Use in-memory SQLite for fast, isolated tests
def _get_test_engine_url():
    return "sqlite:///:memory:"

# Create test engine and sessionmaker
engine_test = create_engine(
    _get_test_engine_url(),
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_test
)

# Override the FastAPI dependency to use our test DB sessions
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fixture: override dependency, create tables, seed users, then drop tables
@pytest.fixture(scope="module", autouse=True)
def prepare_and_seed_db():
    app.dependency_overrides[get_db] = override_get_db
    # Create all tables
    Base.metadata.create_all(bind=engine_test)
    # Seed with test advertiser and scanner using the test DB session
    db = TestingSessionLocal()
    create_users(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine_test)
    app.dependency_overrides.pop(get_db, None)

# FastAPI test client using overridden DB
client = TestClient(app)

def test_create_and_list_get_update_delete_campaign():
    # 1) Create a Stall
    stall_resp = client.post(
        "/api/stalls/",
        json={"location_name": "Test Stall", "latitude": 0.0, "longitude": 0.0, "date": "2025-01-01"},
    )
    assert stall_resp.status_code == 201
    stall_id = stall_resp.json()["stall_id"]

    # 2) Create a Product
    product_resp = client.post(
        "/api/products/",
        json={"name": "Test Product", "description": "desc"},
    )
    assert product_resp.status_code == 201
    product_id = product_resp.json()["product_id"]

    # 3) Authenticate as advertiser
    token_resp = client.post(
        "/api/auth/token",
        data={"username": "adv@example.com", "password": "advpassword123", "scope": "advertiser"}
    )
    assert token_resp.status_code == 200
    token = token_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 4) Create a Campaign
    camp_resp = client.post(
        "/api/campaigns/",
        json={
            "stall_id": stall_id,
            "product_id": product_id,
            "units_allocated": 100,
            "start_datetime": "2025-01-02T00:00:00",
            "end_datetime": "2025-01-10T00:00:00",
        },
        headers=headers,
    )
    assert camp_resp.status_code == 201
    campaign_id = camp_resp.json()["campaign_id"]

    # 5) List Campaigns
    list_resp = client.get("/api/campaigns/", headers=headers)
    assert list_resp.status_code == 200
    assert any(c["campaign_id"] == campaign_id for c in list_resp.json())

    # 6) Get Campaign by ID
    get_resp = client.get(f"/api/campaigns/{campaign_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["campaign_id"] == campaign_id

    # 7) Update the Campaign
    update_resp = client.put(
        f"/api/campaigns/{campaign_id}",
        json={"units_allocated": 150, "status": "active"},
        headers=headers,
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["units_allocated"] == 150
    assert data["status"] == "active"

    # 8) Delete the Campaign
    del_resp = client.delete(f"/api/campaigns/{campaign_id}", headers=headers)
    assert del_resp.status_code == 204

    # 9) Verify Deletion
    final_list = client.get("/api/campaigns/", headers=headers)
    assert all(c["campaign_id"] != campaign_id for c in final_list.json())