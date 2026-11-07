# Backend

The FastAPI application is structured as a modular package in `app/`, with
`main.py` providing the top-level application entrypoint. It implements the user
authentication subsystem, SQLAlchemy database models, and route protection
middleware. All non-auth endpoints (including pre-existing `GET /` and future
application routes) require a valid authenticated session.

## Implemented authentication & API behavior

- **Sign up** (`POST /auth/signup`, alias `POST /auth/register`): registers a new user, hashes password with bcrypt, generates a JWT, and sets an `HttpOnly` cookie.
- **Sign in** (`POST /auth/signin`, alias `POST /auth/login`): authenticates with username or email, sets an `HttpOnly` session cookie.
- **Password reset**:
  - Request: `POST /auth/reset-password/request` (alias `POST /auth/forgot-password`). Generates a secure reset token. Password reset plumbing uses a stub email service (`StubEmailService`) that logs and records outgoing messages, returning the token in development/test responses.
  - Confirm: `POST /auth/reset-password` (alias `POST /auth/reset-password/confirm`). Validates the single-use reset token and updates the password hash.
- **Change password** (`POST /auth/change-password`): requires an authenticated JWT cookie, verifies the current password, updates the password hash, revokes the current token, and issues a fresh session token cookie.
- **Log out** (`POST /auth/logout`): revokes the active token in the database, clears the cookie, and silently returns success if the token is invalid or absent.
- **Global route protection (`AuthMiddleware`)**:
  - All pre-existing (`GET /`) and future routes require a valid, unrevoked JWT token in the cookie (or Bearer header).
  - Guest-only routes (`signup`, `signin`, `reset-password`) reject requests from already-authenticated users with `400 Bad Request`.
  - Logged-out or revoked tokens are permanently denied access until re-authentication.

## Database schema

SQLAlchemy models reflect the ER diagram:
- `users`: UUID PK, name, unique username, unique email, password hash, created_at.
- `groups`: UUID PK, name, created_at.
- `group_members`: composite PK (group_id, user_id), joined_at.
- `categories`: int PK, name.
- `expenses`: UUID PK, group_id, payer_id, category_id, description, total_amount, split_method, occurred_on, created_at.
- `expense_splits`: UUID PK, expense_id, debtor_id, amount_owed.
- `settlements`: UUID PK, group_id, sender_id, receiver_id, amount, status, occurred_on, created_at, updated_at.
- `revoked_tokens` & `password_reset_tokens`: authentication security tables.

SQLite is configured by default for local development and tests (`DATABASE_URL=sqlite:///./app.db`). Production databases can be set via `DATABASE_URL`.

## Local setup

Use Python 3.14. From `backend/`:

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt ruff
.venv/bin/python -m ruff check .
.venv/bin/python -m pytest -q
```

For local development, run:

```sh
.venv/bin/python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The existing requirements include FastAPI, Uvicorn, pytest, HTTPX2,
SQLAlchemy, PyJWT, and bcrypt. CI installs them into an isolated environment, runs pytest, and freezes the resolved
versions into the deployment ZIP. The source requirements themselves are not
version-locked. Local environments, test files, and ignored files are not deployed.

Ruff is installed alongside `requirements.txt` for local and PR checks. The
deployment workflow installs `requirements.txt`. The
[PR workflow](../.github/workflows/ci.yml), release validation, and Azure hosting
all use Python 3.14.

The [packaging helper](../.github/scripts/package_backend.py) can also be run
from the repository root using the backend's tested virtual environment:

```sh
backend/.venv/bin/python .github/scripts/package_backend.py \
  --repository . \
  --revision HEAD \
  --output /tmp/backend.zip
```

It packages the selected Git revision, so uncommitted backend edits are excluded.
The helper's tests cover the selected revision, frozen requirements, exclusion of
local/test files, calls from a subdirectory, and failure for an invalid revision.

## Azure deployment

The [application workflow](../.github/workflows/ci-cd.yml) deploys validated
backend artifacts on `main` after both frontend and backend checks pass. OIDC
authentication uses an identity with Website Contributor scoped only to the API
App Service. No backend password or publish-profile secret is required.

App Service runs Python 3.14 and installs the ZIP's requirements through its
remote build. Its startup command is:

```sh
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

The host is enabled on the existing B1 plan. Always On remains disabled, so idle
instances can stop and requests may incur a cold start. No database grants or
connection settings are configured. SQL migrations/seeding remain a disabled
workflow placeholder. There are no smoke tests or post-deployment endpoint checks.

See the [project README](../README.md) for infrastructure and frontend setup.
