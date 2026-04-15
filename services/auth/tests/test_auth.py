import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
import models  # noqa: F401 — register models with Base metadata
from database import Base, get_db
from main import app

TEST_DATABASE_URL = "sqlite://"  # in-memory

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


def test_register():
    response = client.post("/auth/register", json={
        "email": "alice@example.com",
        "password": "secret123",
        "full_name": "Alice Smith",
        "role": "passenger",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["role"] == "passenger"
    assert "id" in data


def test_register_duplicate_email():
    client.post("/auth/register", json={
        "email": "bob@example.com",
        "password": "secret123",
        "full_name": "Bob Jones",
    })
    response = client.post("/auth/register", json={
        "email": "bob@example.com",
        "password": "another",
        "full_name": "Bob Duplicate",
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login():
    client.post("/auth/register", json={
        "email": "carol@example.com",
        "password": "mypassword",
        "full_name": "Carol White",
    })
    response = client.post("/auth/token", data={
        "username": "carol@example.com",
        "password": "mypassword",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_get_me_with_valid_token():
    client.post("/auth/register", json={
        "email": "dave@example.com",
        "password": "davepass",
        "full_name": "Dave Brown",
    })
    token_resp = client.post("/auth/token", data={
        "username": "dave@example.com",
        "password": "davepass",
    })
    token = token_resp.json()["access_token"]
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "dave@example.com"


def test_get_me_without_token():
    response = client.get("/auth/me")
    assert response.status_code == 401
