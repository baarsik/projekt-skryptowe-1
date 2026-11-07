from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_root_unauthenticated_returns_401():
    response = client.get("/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_read_root_authenticated_returns_hello_world():
    # Sign up a user to obtain an authenticated session cookie
    unique_username = "root_test_user"
    signup_payload = {
        "name": "Root Test User",
        "username": unique_username,
        "email": f"{unique_username}@example.com",
        "password": "password123",
    }
    signup_res = client.post("/auth/signup", json=signup_payload)
    assert signup_res.status_code == 201

    # Call pre-existing endpoint with session cookie
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}