# Backend and database tools

FastAPI still implements only `GET /`, returning `{"msg": "Hello World"}`.
Database tooling uses Python 3.14, SQLAlchemy 2.1, Microsoft's `mssql-python`
driver, Alembic, and python-dotenv. The seven-table SQL Server/Azure SQL schema
is described in [the diagram](../docs/schema.md) and [initial SQL](../docs/schema.sql).
Authentication, application endpoints, and API database access remain planned.
Importing the application never migrates or seeds the database.

## First-time local setup with Docker

Use current Docker Engine/Desktop with x86-64 Linux container support and Docker
Compose v2. The optional Python tools container means no host Python
installation is required for database management. Allocate at least 4 GiB to
Docker. Run these commands from the repository root:

Check the installed engine and Compose versions first:

```sh
docker version
docker compose version
```

Docker Engine 20.10.8 is known to fail this setup: the tools image fails during
APT package installation and SQL Server 2022 aborts with `Operation not permitted`.
Update Docker Desktop/the engine before running the setup on that version.
Parsing the Compose file successfully does not establish runtime compatibility.
The documented build/bootstrap/migration/seed sequence has not passed end to end
on that engine; verification stopped at the build and SQL startup failures.

```sh
cp .env.example .env
```

Fill in two different, strong, local-only passwords in `.env`:
`LOCAL_SQL_ADMIN_PASSWORD` and `LOCAL_SQL_APP_PASSWORD`. SQL Server requires at
least eight characters and three character classes. Do not put Azure credentials
in this file, commit it, or share it. Keep the chosen administrator password while
retaining the volume; changing the environment value does not change the existing
SQL administrator password. Use single-quoted dotenv values if they contain `$`.

Keep `COMPOSE_PROJECT_NAME=rachunki-local` from the template. When upgrading an
existing `.env`, add this non-secret setting if absent to retain the same
container/network/volume namespace. CI supplies its own isolated project name.
Project naming uses this variable instead of a top-level Compose `name`, which
older Compose v2 clients reject.

```sh
docker compose build tools
docker compose up -d db
docker compose run --rm tools python -m db.bootstrap --local
docker compose run --rm tools python -m alembic upgrade head
docker compose run --rm tools python -m db.seed --profile demo
```

The database binds only to `127.0.0.1`, on `LOCAL_SQL_PORT` (default 1433).
Data persists in the Compose project's `sql-data` volume. The tools container
connects to service `db` on port 1433; host Python uses `DB_HOST=127.0.0.1` and
`LOCAL_SQL_PORT`. Its source bind mount makes edits immediately visible.
Rebuild `tools` after changing requirements or the Dockerfile.
The tools service waits for SQL's health check before running commands; the
startup command does not require the newer Compose `--wait` option. The Docker
engine itself must still support the current Python and SQL Server images;
update Docker Desktop if an old engine reports syscall/permission failures.

Bootstrap creates only `rachunki_dev` or `rachunki_test_*` on a local host,
creates/updates the application login's password, and grants that login schema
CRUD permissions. The API uses `DB_USER`/`LOCAL_SQL_APP_PASSWORD`; local migrations
use `sa`/`LOCAL_SQL_ADMIN_PASSWORD`. No server-wide roles are granted to the app.

## Native Python development

Use Python 3.14. From `backend/`:

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt ruff
.venv/bin/python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

On Windows, use the virtual environment's `Scripts/python.exe` instead of
`.venv/bin/python`. Native database tools use the same commands as the container:

```sh
.venv/bin/python -m db.bootstrap --local
.venv/bin/python -m alembic upgrade head
.venv/bin/python -m db.seed --profile demo
```

Local tools explicitly load the root `.env` without overriding existing process
variables. `CI` or `APP_ENV=azure` disables local dotenv loading. Credentials are
passed separately and connection URLs are built in memory. `mssql-python`
installs its driver dependency; Linux also needs `libgssapi-krb5-2` and `libltdl7`,
included in the tools image. Source requirements constrain new database dependencies; CI
freezes all resolved versions into the deployment artifact.

## Daily workflow and schema changes

After pulling changes, rebuild tools if requirements changed, start the database,
and apply committed migrations. Rerun demo seeding only when desired.

```sh
docker compose up -d db
docker compose run --rm tools python -m alembic upgrade head
```

When changing the schema:

1. Apply existing migrations, then edit `db/schema.py`.
2. Generate a candidate revision and review its upgrade/downgrade operations:

   ```sh
   docker compose run --rm tools python -m alembic revision --autogenerate -m "describe change"
   docker compose run --rm tools python -m alembic upgrade head
   docker compose run --rm tools python -m alembic check
   ```

3. Add behavioral tests and update the diagram. Include models, migration, tests,
   and documentation in the same PR. Do not edit already deployed revisions.
   Coordinate parallel revisions into one head before merging.
4. Follow [the strict phased compatibility rule](../AGENTS.md): deploy additions
   and data transitions first; remove old structures in a later release after
   application usage and rollback compatibility have been addressed. Historical
   migrations must retain their own definitions, not import current metadata.

Generate the reviewable SQL for the initial revision from `backend/`:

```sh
.venv/bin/python -m alembic upgrade 20261107_01 --sql > ../docs/schema.sql
```

Normal deployment uses Alembic. The SQL script is an alternative offline artifact,
including Alembic's version record; do not independently apply it to an already
migrated database. Review destructive operations and prefer forward fixes for a
shared database. A downgrade can delete data and is never automatically deployed.

## Seed profiles

`reference` inserts three missing category IDs. `demo` adds reference data plus
three disabled-login demo users, one household, an expense of 10.01 with shares
3.34/3.34/3.33, and a repayment of 1.00. Demo email addresses use the reserved
`example.invalid` domain; there are no demo passwords. Authentication is future work.

Both profiles require the current schema revision, use stable keys, preserve
existing rows/edits, and run in one transaction. A conflicting unique value fails
and rolls back the whole seed. Demo seeding rejects cloud environments and targets.
Run one seed or migration process at a time. Azure runs only `reference`.

```sh
docker compose run --rm tools python -m db.seed --profile reference
```

## Tests

Without SQL Server, the normal suite runs configuration, API, and packaging tests
and explicitly skips the SQL integration tests:

```sh
.venv/bin/python -m ruff check .
.venv/bin/python -m pytest -q
```

To run the complete suite against disposable local databases, from the root:

```sh
DB_INTEGRATION_TESTS=1 docker compose run --rm tools python -m pytest -q
docker compose run --rm tools python -m ruff check .
```

The native equivalent is `DB_INTEGRATION_TESTS=1 .venv/bin/python -m pytest -q`
from `backend/`. Tests create unique `rachunki_test_*` databases and remove only
those databases afterward. They cover initial/repeated migrations, model drift,
seed idempotence and rollback, and database constraints. PR and main CI start
isolated SQL Server containers with generated ephemeral passwords and run these
tests without Azure credentials.

## Stop or reset local SQL

Stop while preserving data:

```sh
docker compose down
```

To delete this local project's database volume:

```sh
docker compose down -v
```

Then repeat startup, bootstrap, migration and seed commands. Neither command
connects to Azure. Each teammate has an independent local volume.

## Azure deployment

[CI/CD](../.github/workflows/ci-cd.yml) validates applications, packages the tested
Git revision and its resolved dependencies, applies migrations and reference
seeds, then allows both application deployments. A failure in the database job
blocks both deploy jobs. PRs do not migrate Azure or receive OIDC permissions.

The database job downloads the validated backend ZIP, uses Python 3.14, signs in
through a separate main-only migration identity, and sets `APP_ENV=azure`,
`DB_HOST`, `DB_NAME`, and `DB_AUTHENTICATION=ActiveDirectoryDefault`.
`AZURE_TOKEN_CREDENTIALS=AzureCliCredential` explicitly selects its Azure CLI
session instead of the runner's own managed identity. Application runtime should use
`ActiveDirectoryMSI`, with its own managed identity and schema CRUD grants.

No migration or seed executes from Uvicorn startup. The API remains independently
hosted on App Service with its existing startup command. The packaging helper
includes the committed database modules, Alembic configuration and revisions.

See [the root README](../README.md#azure-database-setup) for required one-time
identity grants, private runner networking, and GitHub repository variables.
