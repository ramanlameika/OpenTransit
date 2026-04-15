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


def test_create_stop():
    response = client.post("/stops", json={"name": "Central Station", "lat": 40.7128, "lon": -74.0060})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Central Station"
    assert "id" in data


def test_create_route():
    response = client.post("/routes", json={"name": "Route 1", "description": "Main city route"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Route 1"
    assert "id" in data


def test_add_stop_to_route():
    stop = client.post("/stops", json={"name": "Stop A", "lat": 1.0, "lon": 2.0}).json()
    route = client.post("/routes", json={"name": "Route X", "description": ""}).json()

    response = client.post(f"/routes/{route['id']}/stops", json={"stop_id": stop["id"], "sequence": 1})
    assert response.status_code == 201
    data = response.json()
    assert data["route_id"] == route["id"]
    assert data["stop_id"] == stop["id"]
    assert data["sequence"] == 1


def test_get_route_stops_ordered():
    stop1 = client.post("/stops", json={"name": "First", "lat": 1.0, "lon": 1.0}).json()
    stop2 = client.post("/stops", json={"name": "Second", "lat": 2.0, "lon": 2.0}).json()
    route = client.post("/routes", json={"name": "Ordered Route", "description": ""}).json()

    client.post(f"/routes/{route['id']}/stops", json={"stop_id": stop2["id"], "sequence": 2})
    client.post(f"/routes/{route['id']}/stops", json={"stop_id": stop1["id"], "sequence": 1})

    response = client.get(f"/routes/{route['id']}/stops")
    assert response.status_code == 200
    stops = response.json()
    assert len(stops) == 2
    assert stops[0]["sequence"] == 1
    assert stops[1]["sequence"] == 2


def test_get_route_not_found():
    response = client.get("/routes/nonexistent-id")
    assert response.status_code == 404
