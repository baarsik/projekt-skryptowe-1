# Backend starter

The FastAPI application in `main.py` implements only `GET /`, returning
`{"msg": "Hello World"}`. Pytest checks that response and the CI packaging helper.
Household functionality, authentication, database access, migrations, and seeding
are not implemented yet.

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

The existing requirements include FastAPI, Uvicorn, pytest, and HTTPX2. CI
installs them into an isolated environment, runs pytest, and freezes the resolved
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
