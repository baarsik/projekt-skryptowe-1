from __future__ import annotations

import time
import uuid

import jwt
from fastapi.testclient import TestClient

from app.core.config import COOKIE_NAME, JWT_ALGORITHM, JWT_SECRET_KEY
from app.main import app
from app.services.email import email_service

client = TestClient(app)


def random_string() -> str:
    return uuid.uuid4().hex[:8]


def test_signup_success_sets_cookie_and_returns_user():
    # Ensure unauthenticated
    client.cookies.clear()
    uid = random_string()
    payload = {
        "name": "Alice Tester",
        "username": f"alice_{uid}",
        "email": f"alice_{uid}@example.com",
        "password": "mypassword123",
    }
    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "User registered successfully"
    assert data["user"]["username"] == payload["username"]
    assert data["user"]["email"] == payload["email"]
    assert "password" not in data["user"]
    assert "password_hash" not in data["user"]
    assert COOKIE_NAME in response.cookies


def test_signup_duplicate_username_or_email_rejected():
    client.cookies.clear()
    uid = random_string()
    payload = {
        "name": "Bob Tester",
        "username": f"bob_{uid}",
        "email": f"bob_{uid}@example.com",
        "password": "mypassword123",
    }
    res1 = client.post("/auth/signup", json=payload)
    assert res1.status_code == 201

    client.cookies.clear()
    # Same username, different email
    dup_username = payload.copy()
    dup_username["email"] = f"other_{uid}@example.com"
    res2 = client.post("/auth/signup", json=dup_username)
    assert res2.status_code == 409
    assert res2.json()["detail"] == "Username or email already registered"

    # Different username, same email
    dup_email = payload.copy()
    dup_email["username"] = f"other_{uid}"
    res3 = client.post("/auth/signup", json=dup_email)
    assert res3.status_code == 409


def test_signin_with_username_and_email():
    client.cookies.clear()
    uid = random_string()
    username = f"charlie_{uid}"
    email = f"charlie_{uid}@example.com"
    password = "charliepassword123"

    signup_res = client.post(
        "/auth/signup",
        json={
            "name": "Charlie",
            "username": username,
            "email": email,
            "password": password,
        },
    )
    assert signup_res.status_code == 201

    # Clear cookie to simulate signing in from a fresh browser
    client.cookies.clear()

    # Sign in with username
    res_user = client.post(
        "/auth/signin",
        json={"username": username, "password": password},
    )
    assert res_user.status_code == 200
    assert res_user.json()["message"] == "Signed in successfully"
    assert COOKIE_NAME in res_user.cookies

    # Clear cookie again and sign in with email
    client.cookies.clear()
    res_email = client.post(
        "/auth/signin",
        json={"username": email, "password": password},
    )
    assert res_email.status_code == 200
    assert res_email.json()["message"] == "Signed in successfully"


def test_signin_invalid_credentials_rejected():
    client.cookies.clear()
    uid = random_string()
    username = f"dave_{uid}"
    password = "davepassword123"

    client.post(
        "/auth/signup",
        json={
            "name": "Dave",
            "username": username,
            "email": f"{username}@example.com",
            "password": password,
        },
    )

    client.cookies.clear()
    # Wrong password
    res = client.post(
        "/auth/signin",
        json={"username": username, "password": "wrongpassword"},
    )
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid username or password"

    # Non-existent user
    res2 = client.post(
        "/auth/signin",
        json={"username": f"nonexistent_{uid}", "password": password},
    )
    assert res2.status_code == 401


def test_authenticated_user_rejected_from_guest_only_routes():
    client.cookies.clear()
    uid = random_string()
    username = f"eve_{uid}"
    email = f"eve_{uid}@example.com"
    password = "evepassword123"

    # Sign up (which automatically logs the user in and sets cookie)
    res = client.post(
        "/auth/signup",
        json={
            "name": "Eve",
            "username": username,
            "email": email,
            "password": password,
        },
    )
    assert res.status_code == 201

    # While logged in, attempting signup must be rejected
    signup_attempt = client.post(
        "/auth/signup",
        json={
            "name": "Another",
            "username": f"another_{uid}",
            "email": f"another_{uid}@example.com",
            "password": "password123",
        },
    )
    assert signup_attempt.status_code == 400
    assert signup_attempt.json()["detail"] == "Already authenticated"

    # While logged in, attempting signin must be rejected
    signin_attempt = client.post(
        "/auth/signin",
        json={"username": username, "password": password},
    )
    assert signin_attempt.status_code == 400
    assert signin_attempt.json()["detail"] == "Already authenticated"

    # While logged in, requesting password reset must be rejected
    reset_req_attempt = client.post(
        "/auth/reset-password/request",
        json={"email": email},
    )
    assert reset_req_attempt.status_code == 400
    assert reset_req_attempt.json()["detail"] == "Already authenticated"

    # While logged in, confirming password reset must be rejected
    reset_confirm_attempt = client.post(
        "/auth/reset-password",
        json={"token": "some-token", "new_password": "newpassword123"},
    )
    assert reset_confirm_attempt.status_code == 400
    assert reset_confirm_attempt.json()["detail"] == "Already authenticated"


def test_password_reset_flow_with_email_stub():
    client.cookies.clear()
    email_service.clear()
    uid = random_string()
    username = f"frank_{uid}"
    email = f"frank_{uid}@example.com"
    old_password = "oldpassword123"
    new_password = "newpassword456"

    # Create user
    client.post(
        "/auth/signup",
        json={
            "name": "Frank",
            "username": username,
            "email": email,
            "password": old_password,
        },
    )
    client.cookies.clear()

    # Request password reset
    req_res = client.post("/auth/reset-password/request", json={"email": email})
    assert req_res.status_code == 200
    data = req_res.json()
    assert data["message"] == "Password reset instructions sent if email exists"
    reset_token = data.get("reset_token")
    assert reset_token is not None

    # Check stub email service received the message
    assert len(email_service.sent_emails) == 1
    sent = email_service.sent_emails[0]
    assert sent.recipient == email
    assert reset_token in sent.body

    # Confirm password reset with token
    confirm_res = client.post(
        "/auth/reset-password",
        json={"token": reset_token, "new_password": new_password},
    )
    assert confirm_res.status_code == 200
    assert confirm_res.json()["message"] == "Password reset successfully"

    # Token cannot be reused
    reuse_res = client.post(
        "/auth/reset-password",
        json={"token": reset_token, "new_password": "anotherpassword"},
    )
    assert reuse_res.status_code == 400
    assert reuse_res.json()["detail"] == "Invalid or expired reset token"

    # Old password fails
    fail_res = client.post(
        "/auth/signin",
        json={"username": username, "password": old_password},
    )
    assert fail_res.status_code == 401

    # New password succeeds
    success_res = client.post(
        "/auth/signin",
        json={"username": username, "password": new_password},
    )
    assert success_res.status_code == 200


def test_change_password_requires_token_and_validates_current_password():
    client.cookies.clear()
    uid = random_string()
    username = f"grace_{uid}"
    email = f"grace_{uid}@example.com"
    old_password = "gracepassword123"
    new_password = "newgracepassword123"

    # Attempt change password unauthenticated -> 401
    unauth_res = client.post(
        "/auth/change-password",
        json={"current_password": old_password, "new_password": new_password},
    )
    assert unauth_res.status_code == 401
    assert unauth_res.json()["detail"] == "Not authenticated"

    # Authenticate user
    client.post(
        "/auth/signup",
        json={
            "name": "Grace",
            "username": username,
            "email": email,
            "password": old_password,
        },
    )

    # Attempt with wrong current password -> 400
    wrong_pass_res = client.post(
        "/auth/change-password",
        json={"current_password": "wrongpassword", "new_password": new_password},
    )
    assert wrong_pass_res.status_code == 400
    assert wrong_pass_res.json()["detail"] == "Incorrect current password"

    # Attempt with correct current password -> 200
    change_res = client.post(
        "/auth/change-password",
        json={"current_password": old_password, "new_password": new_password},
    )
    assert change_res.status_code == 200
    assert change_res.json()["message"] == "Password changed successfully"

    # Can sign in with new password
    client.cookies.clear()
    signin_res = client.post(
        "/auth/signin",
        json={"username": username, "password": new_password},
    )
    assert signin_res.status_code == 200


def test_logout_revokes_token_and_subsequent_requests_are_unauthorized():
    client.cookies.clear()
    uid = random_string()
    username = f"heidi_{uid}"
    email = f"heidi_{uid}@example.com"
    password = "heidipassword123"

    signup_res = client.post(
        "/auth/signup",
        json={
            "name": "Heidi",
            "username": username,
            "email": email,
            "password": password,
        },
    )
    token = signup_res.cookies.get(COOKIE_NAME)
    assert token is not None

    # Verify protected endpoint works with active session
    me_res = client.get("/auth/me")
    assert me_res.status_code == 200
    assert me_res.json()["username"] == username

    # Log out
    logout_res = client.post("/auth/logout")
    assert logout_res.status_code == 200
    assert logout_res.json()["message"] == "Logged out successfully"

    # Using the old revoked token must fail with 401
    client.cookies.set(COOKIE_NAME, token)
    blocked_res = client.get("/auth/me")
    assert blocked_res.status_code == 401

    root_res = client.get("/")
    assert root_res.status_code == 401


def test_logout_silently_succeeds_when_unauthenticated_or_invalid():
    client.cookies.clear()

    # 1. No token at all
    res1 = client.post("/auth/logout")
    assert res1.status_code == 200
    assert res1.json()["message"] == "Logged out successfully"

    # 2. Malformed token
    client.cookies.set(COOKIE_NAME, "malformed.garbage.token")
    res2 = client.post("/auth/logout")
    assert res2.status_code == 200
    assert res2.json()["message"] == "Logged out successfully"

    # 3. Expired token
    expired_payload = {
        "sub": str(uuid.uuid4()),
        "username": "expired_user",
        "email": "expired@example.com",
        "jti": str(uuid.uuid4()),
        "iat": int(time.time()) - 3600,
        "exp": int(time.time()) - 1800,
    }
    expired_token = jwt.encode(
        expired_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM
    )
    client.cookies.set(COOKIE_NAME, expired_token)
    res3 = client.post("/auth/logout")
    assert res3.status_code == 200
    assert res3.json()["message"] == "Logged out successfully"


def test_all_other_endpoints_require_valid_token():
    client.cookies.clear()

    # Pre-existing endpoint
    res_root = client.get("/")
    assert res_root.status_code == 401

    # Protected auth profile
    res_me = client.get("/auth/me")
    assert res_me.status_code == 401

    # Arbitrary non-existent or future endpoints
    res_future = client.get("/future/expenses")
    assert res_future.status_code == 401

    res_docs = client.get("/docs")
    assert res_docs.status_code == 401

    # Malformed token
    client.cookies.set(COOKIE_NAME, "invalid-token-string")
    res_bad_token = client.get("/")
    assert res_bad_token.status_code == 401

    # Token signed with wrong secret key
    bad_key_token = jwt.encode(
        {"sub": str(uuid.uuid4()), "jti": str(uuid.uuid4())},
        "wrong-secret-key-minimum-32-bytes-long",
        algorithm="HS256",
    )
    client.cookies.set(COOKIE_NAME, bad_key_token)
    res_wrong_key = client.get("/")
    assert res_wrong_key.status_code == 401