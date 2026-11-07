# Backend and database

The FastAPI starter exposes only `GET /`. Database tools use SQLAlchemy,
`mssql-python` and Alembic; application endpoints and authentication are planned.
See the [schema](../docs/schema.md) and [Azure setup](../infra/README.md).

## Local database with Docker

Use current Docker with x86-64 Linux container support, Compose v2 and at least
4 GiB of memory. **Docker Engine 20.10.8 fails the tools build and SQL startup**;
update it before following these steps.

From the repository root:

```sh
cp .env.example .env
```

Set two different, strong local passwords in `.env`: `LOCAL_SQL_ADMIN_PASSWORD`
and `LOCAL_SQL_APP_PASSWORD`. Use at least eight characters with three of:
uppercase letters, lowercase letters, digits and symbols. Single-quote values
containing `$`. Keep `.env` private.
Retain `COMPOSE_PROJECT_NAME=rachunki-local` so existing volumes keep their names.

```sh
docker compose build tools
docker compose up -d db
docker compose run --rm tools python -m db.bootstrap --local
docker compose run --rm tools python -m alembic upgrade head
docker compose run --rm tools python -m db.seed --profile demo
```

The tools container waits for SQL's health check. Bootstrap creates the local
`rachunki_dev` database and an application login with CRUD permissions; local
migrations use the administrator login. SQL is exposed only on `127.0.0.1`, at
`LOCAL_SQL_PORT` (default 1433), and data persists in a Docker volume.

After pulling changes, start SQL and run `alembic upgrade head` again. Rebuild
`tools` when its requirements or Dockerfile change. Keep the original administrator
password while retaining the volume; editing `.env` does not reset it.

Stop with `docker compose down`. **`docker compose down -v` deletes local data**;
repeat bootstrap, migrations and seeding afterward.

## Run the API with Python

Use Python 3.14. From `backend/`:

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt ruff
.venv/bin/python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

On Windows, use `.venv\Scripts\python.exe`. For native database commands, replace
`docker compose run --rm tools python` with `.venv/bin/python` and run from
`backend/`. Linux also needs `libgssapi-krb5-2` and `libltdl7`; the tools image
includes them.

Local database commands load the root `.env`, preserving process environment
values. `CI` or `APP_ENV=azure` disables dotenv loading. No migrations or seeds
run when the API starts.

## Change the schema

Apply existing migrations first, then edit `db/schema.py`. From the repository root:

```sh
docker compose run --rm tools python -m alembic revision --autogenerate -m "describe change"
docker compose run --rm tools python -m alembic upgrade head
docker compose run --rm tools python -m alembic check
```

Review generated migrations. Include schema changes, migration files, tests and
the diagram in the same PR; do not edit deployed revisions or import current
schema definitions into historical migrations. Resolve parallel revisions to one
head before merging.

Follow the [phased compatibility rule](../AGENTS.md#database-compatibility-rule):
add replacements and switch application usage before removing old structures in
*a later deployment*. Downgrades can delete data and are never deployed automatically.

To regenerate the initial [SQL script](../docs/schema.sql), from `backend/`:

```sh
.venv/bin/python -m alembic upgrade 20261107_01 --sql > ../docs/schema.sql
```

Use Alembic for normal migrations. The SQL script includes the version record
and is intended for an empty database, not an already migrated one.

## Seed data

| Profile | Contents | Where it runs |
| --- | --- | --- |
| `reference` | Three expense categories | Local development and Azure deployment |
| `demo` | Reference data, a household, three users, an expense and a repayment | Local development/test only |

Select a profile with `python -m db.seed --profile reference` (or `demo`), using
Docker or the virtual environment as above. Both require the latest migration,
preserve existing rows and roll back the whole seed on conflicts. Demo logins
are disabled. Run one seed or migration process at a time.

## Checks

From `backend/` with the Python environment installed:

```sh
.venv/bin/python -m ruff check .
.venv/bin/python -m pytest -q
```

SQL integration tests are skipped by default. To include them, start local SQL
and run from the repository root:

```sh
DB_INTEGRATION_TESTS=1 docker compose run --rm tools python -m pytest -q
docker compose run --rm tools python -m ruff check .
```

The native equivalent is `DB_INTEGRATION_TESTS=1 .venv/bin/python -m pytest -q`
from `backend/`. Integration tests create and remove isolated `rachunki_test_*`
databases. Both backend CI workflows run them against disposable SQL containers.
