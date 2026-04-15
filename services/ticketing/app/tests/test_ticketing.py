import pytest
from fastapi.testclient import TestClient
from app.main import app, tickets_db

client = TestClient(app)


def setup_function():
    tickets_db.clear()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "ticketing"


def test_list_tickets_empty():
    response = client.get("/tickets")
    assert response.status_code == 200
    assert response.json() == []


def test_create_ticket():
    response = client.post("/tickets", json={
        "route_id": "R1",
        "passenger_id": "P1",
        "ticket_type": "single"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["route_id"] == "R1"
    assert data["passenger_id"] == "P1"
    assert data["ticket_type"] == "single"
    assert data["status"] == "active"
    assert "id" in data


def test_get_ticket():
    create_resp = client.post("/tickets", json={
        "route_id": "R2",
        "passenger_id": "P2",
        "ticket_type": "day_pass"
    })
    ticket_id = create_resp.json()["id"]

    response = client.get(f"/tickets/{ticket_id}")
    assert response.status_code == 200
    assert response.json()["id"] == ticket_id


def test_get_ticket_not_found():
    response = client.get("/tickets/nonexistent-id")
    assert response.status_code == 404


def test_validate_ticket():
    create_resp = client.post("/tickets", json={
        "route_id": "R3",
        "passenger_id": "P3",
        "ticket_type": "weekly"
    })
    ticket_id = create_resp.json()["id"]

    response = client.post(f"/tickets/{ticket_id}/validate")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "validated"
    assert data["validated_at"] is not None


def test_validate_already_validated_ticket():
    create_resp = client.post("/tickets", json={
        "route_id": "R4",
        "passenger_id": "P4",
        "ticket_type": "monthly"
    })
    ticket_id = create_resp.json()["id"]
    client.post(f"/tickets/{ticket_id}/validate")

    response = client.post(f"/tickets/{ticket_id}/validate")
    assert response.status_code == 400


def test_list_tickets_after_creation():
    client.post("/tickets", json={"route_id": "R5", "passenger_id": "P5", "ticket_type": "single"})
    client.post("/tickets", json={"route_id": "R6", "passenger_id": "P6", "ticket_type": "day_pass"})

    response = client.get("/tickets")
    assert response.status_code == 200
    assert len(response.json()) == 2
