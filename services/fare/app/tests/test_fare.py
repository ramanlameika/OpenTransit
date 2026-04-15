import pytest
from fastapi.testclient import TestClient
from app.main import app, fares_db, route_fares_index

client = TestClient(app)


def setup_function():
    fares_db.clear()
    route_fares_index.clear()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "fare"


def test_list_fares_empty():
    response = client.get("/fares")
    assert response.status_code == 200
    assert response.json() == []


def test_create_fare():
    response = client.post("/fares", json={
        "route_id": "R1",
        "fare_type": "standard",
        "amount": 2.50
    })
    assert response.status_code == 201
    data = response.json()
    assert data["route_id"] == "R1"
    assert data["fare_type"] == "standard"
    assert data["amount"] == 2.50
    assert "id" in data


def test_create_fare_negative_amount():
    response = client.post("/fares", json={
        "route_id": "R1",
        "fare_type": "standard",
        "amount": -1.0
    })
    assert response.status_code == 400


def test_get_fares_for_route():
    client.post("/fares", json={"route_id": "R2", "fare_type": "standard", "amount": 3.00})
    client.post("/fares", json={"route_id": "R2", "fare_type": "concession", "amount": 1.50})

    response = client.get("/fares/R2")
    assert response.status_code == 200
    fares = response.json()
    assert len(fares) == 2
    fare_types = {f["fare_type"] for f in fares}
    assert "standard" in fare_types
    assert "concession" in fare_types


def test_get_fares_for_nonexistent_route():
    response = client.get("/fares/nonexistent-route")
    assert response.status_code == 404


def test_list_fares_after_creation():
    client.post("/fares", json={"route_id": "R3", "fare_type": "child", "amount": 1.00})
    client.post("/fares", json={"route_id": "R4", "fare_type": "senior", "amount": 1.25})

    response = client.get("/fares")
    assert len(response.json()) == 2
