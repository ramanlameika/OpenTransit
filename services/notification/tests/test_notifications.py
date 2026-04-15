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

NOTIF_PAYLOAD = {
    "user_id": "user-uuid-1234",
    "channel": "email",
    "subject": "Your ticket is ready",
    "body": "Here is your ticket details...",
}


def test_create_notification_sent_status():
    response = client.post("/notifications", json=NOTIF_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "sent"
    assert data["sent_at"] is not None
    assert data["user_id"] == NOTIF_PAYLOAD["user_id"]


def test_create_notification_sms():
    response = client.post("/notifications", json={**NOTIF_PAYLOAD, "channel": "sms"})
    assert response.status_code == 201
    assert response.json()["channel"] == "sms"


def test_list_notifications_by_user():
    uid = "filter-user-notif-42"
    client.post("/notifications", json={**NOTIF_PAYLOAD, "user_id": uid})
    client.post("/notifications", json={**NOTIF_PAYLOAD, "user_id": uid})
    response = client.get(f"/notifications?user_id={uid}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(n["user_id"] == uid for n in data)


def test_get_notification_by_id():
    notif = client.post("/notifications", json=NOTIF_PAYLOAD).json()
    response = client.get(f"/notifications/{notif['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == notif["id"]


def test_get_notification_not_found():
    response = client.get("/notifications/nonexistent-id")
    assert response.status_code == 404
