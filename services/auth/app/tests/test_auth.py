import pytest
from fastapi.testclient import TestClient
from app.main import app, users_db

client = TestClient(app)


def setup_function():
    users_db.clear()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "auth"


def test_register_success():
    response = client.post("/auth/register", json={
        "email": "alice@example.com",
        "password": "Password123!",
        "full_name": "Alice Smith"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["full_name"] == "Alice Smith"
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_email():
    client.post("/auth/register", json={
        "email": "bob@example.com",
        "password": "Password123!",
        "full_name": "Bob"
    })
    response = client.post("/auth/register", json={
        "email": "bob@example.com",
        "password": "Password123!",
        "full_name": "Bob Again"
    })
    assert response.status_code == 409


def test_login_success():
    client.post("/auth/register", json={
        "email": "carol@example.com",
        "password": "Password123!",
        "full_name": "Carol"
    })
    response = client.post("/auth/login", json={
        "email": "carol@example.com",
        "password": "Password123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    client.post("/auth/register", json={
        "email": "dave@example.com",
        "password": "Password123!",
        "full_name": "Dave"
    })
    response = client.post("/auth/login", json={
        "email": "dave@example.com",
        "password": "WrongPassword"
    })
    assert response.status_code == 401


def test_get_me_with_valid_token():
    client.post("/auth/register", json={
        "email": "eve@example.com",
        "password": "Password123!",
        "full_name": "Eve"
    })
    login_resp = client.post("/auth/login", json={
        "email": "eve@example.com",
        "password": "Password123!"
    })
    token = login_resp.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "eve@example.com"


def test_get_me_without_token():
    response = client.get("/auth/me")
    assert response.status_code in (401, 403)


def test_get_me_invalid_token():
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
