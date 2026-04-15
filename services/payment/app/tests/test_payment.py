import pytest
from fastapi.testclient import TestClient
from app.main import app, payments_db

client = TestClient(app)


def setup_function():
    payments_db.clear()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "payment"


def test_create_payment():
    response = client.post("/payments", json={
        "ticket_id": "T1",
        "amount": 2.50,
        "method": "card"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["ticket_id"] == "T1"
    assert data["amount"] == 2.50
    assert data["method"] == "card"
    assert data["status"] == "completed"
    assert "id" in data


def test_create_payment_zero_amount():
    response = client.post("/payments", json={
        "ticket_id": "T2",
        "amount": 0,
        "method": "card"
    })
    assert response.status_code == 400


def test_get_payment():
    create_resp = client.post("/payments", json={
        "ticket_id": "T3",
        "amount": 5.00,
        "method": "wallet"
    })
    payment_id = create_resp.json()["id"]

    response = client.get(f"/payments/{payment_id}")
    assert response.status_code == 200
    assert response.json()["id"] == payment_id


def test_get_payment_not_found():
    response = client.get("/payments/nonexistent-id")
    assert response.status_code == 404


def test_refund_payment():
    create_resp = client.post("/payments", json={
        "ticket_id": "T4",
        "amount": 3.00,
        "method": "bank_transfer"
    })
    payment_id = create_resp.json()["id"]

    response = client.post(f"/payments/{payment_id}/refund")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "refunded"
    assert data["refunded_at"] is not None


def test_refund_already_refunded_payment():
    create_resp = client.post("/payments", json={
        "ticket_id": "T5",
        "amount": 2.00,
        "method": "card"
    })
    payment_id = create_resp.json()["id"]
    client.post(f"/payments/{payment_id}/refund")

    response = client.post(f"/payments/{payment_id}/refund")
    assert response.status_code == 400


def test_refund_nonexistent_payment():
    response = client.post("/payments/nonexistent-id/refund")
    assert response.status_code == 404
