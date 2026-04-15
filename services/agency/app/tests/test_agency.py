import pytest
from fastapi.testclient import TestClient
from app.main import app, agencies_db, routes_db, agency_routes_index

client = TestClient(app)


def setup_function():
    agencies_db.clear()
    routes_db.clear()
    agency_routes_index.clear()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "agency"


def test_list_agencies_empty():
    response = client.get("/agencies")
    assert response.status_code == 200
    assert response.json() == []


def test_create_agency():
    response = client.post("/agencies", json={
        "name": "City Transit",
        "region": "Downtown",
        "contact_email": "admin@citytransit.com"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "City Transit"
    assert data["region"] == "Downtown"
    assert data["contact_email"] == "admin@citytransit.com"
    assert "id" in data


def test_get_agency():
    create_resp = client.post("/agencies", json={
        "name": "Metro Lines",
        "region": "North",
        "contact_email": "info@metro.com"
    })
    agency_id = create_resp.json()["id"]

    response = client.get(f"/agencies/{agency_id}")
    assert response.status_code == 200
    assert response.json()["id"] == agency_id
    assert response.json()["name"] == "Metro Lines"


def test_get_agency_not_found():
    response = client.get("/agencies/nonexistent-id")
    assert response.status_code == 404


def test_list_agency_routes_empty():
    create_resp = client.post("/agencies", json={
        "name": "Bus Co",
        "region": "East",
        "contact_email": "bus@co.com"
    })
    agency_id = create_resp.json()["id"]

    response = client.get(f"/agencies/{agency_id}/routes")
    assert response.status_code == 200
    assert response.json() == []


def test_list_routes_for_nonexistent_agency():
    response = client.get("/agencies/nonexistent-id/routes")
    assert response.status_code == 404


def test_list_agencies_after_creation():
    client.post("/agencies", json={"name": "A1", "region": "Zone1", "contact_email": "a1@test.com"})
    client.post("/agencies", json={"name": "A2", "region": "Zone2", "contact_email": "a2@test.com"})

    response = client.get("/agencies")
    assert len(response.json()) == 2
