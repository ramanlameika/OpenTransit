import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
import models  # noqa: F401 — register models with Base metadata
from database import Base, get_db
from main import app

TEST_DATABASE_URL = "sqlite://"

engine_test = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine_test)

client = TestClient(app)

TICKET_PAYLOAD = {
    "user_id": "user-uuid-1234",
    "route_id": "route-uuid-5678",
    "fare": "2.50",
}


def test_issue_ticket():
    response = client.post("/tickets", json=TICKET_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "active"
    assert data["user_id"] == TICKET_PAYLOAD["user_id"]
    assert "qr_code" in data
    assert "expires_at" in data


def test_validate_ticket():
    ticket = client.post("/tickets", json=TICKET_PAYLOAD).json()
    response = client.post(f"/tickets/{ticket['id']}/validate")
    assert response.status_code == 200
    assert response.json()["status"] == "used"
    assert response.json()["used_at"] is not None


def test_double_validate_returns_error():
    ticket = client.post("/tickets", json=TICKET_PAYLOAD).json()
    client.post(f"/tickets/{ticket['id']}/validate")
    response = client.post(f"/tickets/{ticket['id']}/validate")
    assert response.status_code == 400
    assert "cannot be validated" in response.json()["detail"].lower()


def test_cancel_ticket():
    ticket = client.post("/tickets", json=TICKET_PAYLOAD).json()
    response = client.post(f"/tickets/{ticket['id']}/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_list_tickets_by_user():
    uid = "filter-user-999"
    client.post("/tickets", json={**TICKET_PAYLOAD, "user_id": uid})
    client.post("/tickets", json={**TICKET_PAYLOAD, "user_id": uid})
    response = client.get(f"/tickets?user_id={uid}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(t["user_id"] == uid for t in data)
