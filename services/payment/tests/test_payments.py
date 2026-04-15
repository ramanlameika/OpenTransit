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

PAYMENT_PAYLOAD = {
    "ticket_id": "ticket-uuid-1234",
    "user_id": "user-uuid-5678",
    "amount": "2.50",
    "currency": "USD",
}


def test_create_payment_completed():
    response = client.post("/payments", json=PAYMENT_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "completed"
    assert data["gateway_ref"] is not None
    assert data["currency"] == "USD"


def test_get_payment():
    payment = client.post("/payments", json=PAYMENT_PAYLOAD).json()
    response = client.get(f"/payments/{payment['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == payment["id"]


def test_refund_payment():
    payment = client.post("/payments", json=PAYMENT_PAYLOAD).json()
    response = client.post(f"/payments/{payment['id']}/refund")
    assert response.status_code == 200
    assert response.json()["status"] == "refunded"


def test_refund_already_refunded():
    payment = client.post("/payments", json=PAYMENT_PAYLOAD).json()
    client.post(f"/payments/{payment['id']}/refund")
    response = client.post(f"/payments/{payment['id']}/refund")
    assert response.status_code == 400


def test_list_payments_by_user():
    uid = "filter-user-pay-999"
    client.post("/payments", json={**PAYMENT_PAYLOAD, "user_id": uid})
    client.post("/payments", json={**PAYMENT_PAYLOAD, "user_id": uid})
    response = client.get(f"/payments?user_id={uid}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(p["user_id"] == uid for p in data)
