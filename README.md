# Dzielenie rachunków

`Dzielenie rachunków` is a planned shared household expense and reimbursement
application. See [issue #11](https://github.com/baarsik/projekt-skryptowe-1/issues/11)
for the proposed functional scope.

## Current state

- `frontend/` contains the Next.js 16.4.3, React 19.3.0, and TypeScript starter. It
  does not yet implement expenses, accounts, balances, or API requests.
- The frontend exports static HTML/CSS/JavaScript to `frontend/out/`.
- [Application CI/CD](.github/workflows/ci-cd.yml) validates both applications and
  prepares their Azure deployments. Frontend deployment requires the user-provided
  GitHub secret described below and this workflow on GitHub.
- `backend/` contains a FastAPI starter with a `GET /` endpoint returning
  `{"msg": "Hello World"}`, with pytest checks for the endpoint and deployment
  packaging. Explicit SQLAlchemy/Alembic database tools implement the initial
  seven-table schema and reference/demo seeding. The HTTP API does not yet access
  the database or implement household application functionality.
- `infra/` defines the frontend host, enabled Python backend host, its narrowly
  scoped GitHub deployment identity, and a separate free-offer SQL database.
  A separate main-only migration identity is provisioned. Database grants and SQL
  network access require administrator setup before Azure migrations can run.
- PRs to `main` run backend Ruff and pytest on Python 3.14. Frontend PR checks
  remain a TODO because Vitest tests are not configured. The main deployment
  workflow separately validates both applications using Python 3.14 for the backend.
  There are no smoke tests or post-deployment application checks.

The current Azure frontend host replaces the GitHub Pages suggestion in
[issue #1](https://github.com/baarsik/projekt-skryptowe-1/issues/1). The planned
Python backend remains separate from the browser frontend.

## Local frontend development

Use Node.js 24, as specified in [.nvmrc](.nvmrc), and the committed npm lockfile.
Run these commands from `frontend/`:

```sh
npm ci
npm run dev
```

The development server uses `http://localhost:3000`. Before submitting changes:

```sh
npm run lint
npm run typecheck
npm run build
```

The build writes the static deployment files to `frontend/out/`. Static hosting
runs no Next.js server. Server Actions, runtime server rendering, and API routes
requiring a server are outside this deployment model. Image optimization is
disabled so images do not require a Next.js server. Cache Components and Partial
Prefetching from the starter are disabled for the static configuration.

The frontend currently has no API address setting and does not contact the
backend or database. Define and document build-time API configuration
when API integration is implemented. Never put database configuration into the
browser build.

## Pull request CI

[ci.yml](.github/workflows/ci.yml) runs only for pull requests targeting `main`.
It installs `backend/requirements.txt` and Ruff, runs `python -m ruff check .`, and
runs `python -m pytest -q` from `backend/` using Python 3.14. An isolated SQL
Server container exercises migrations, constraints, model drift and repeatable
seeds. Its generated credentials are masked and never sent to Azure.

Frontend setup, ESLint, and Vitest remain a commented TODO until frontend tests
exist. No placeholder job reports frontend tests as passed. This workflow does
not deploy or request Azure credentials.

## Application CI/CD

The [workflow](.github/workflows/ci-cd.yml) implements this initial portion of
[issue #2](https://github.com/baarsik/projekt-skryptowe-1/issues/2) and
[issue #3](https://github.com/baarsik/projekt-skryptowe-1/issues/3):

1. Pushes to `main` and manual runs validate the frontend and run backend pytest
   in parallel. The frontend uses the committed npm lockfile; backend requirements
   are installed into a Python 3.14 virtual environment matching Azure.
2. Backend validation also runs migrations and seed/constraint tests against a
   disposable SQL Server container with generated ephemeral credentials.
3. `frontend-static` contains the exported frontend. `backend-source` contains a
   ZIP of the tested commit's Git-tracked backend code, excluding tests and local
   environments. Its requirements record the exact dependency versions resolved
   during that validation run. Artifacts are retained for seven days.
4. Successful `main` runs first apply Alembic migrations and reference seeds from
   the validated backend ZIP. Both application deployments require that database
   job to succeed. A manual run can deploy only when its branch is `main`.
5. Pull requests never deploy, receive the Azure deployment secret, or obtain
   Azure OIDC tokens. Main runs are serialized. There are no preview environments
   or smoke tests.

The workflow is organized in that order: **validate → migrate → deploy**.
Every step has a descriptive name. Backend ZIP creation lives in the
[packaging helper](.github/scripts/package_backend.py), so the YAML shows the
release sequence rather than embedded Python code. Its regression tests run as
part of the backend pytest job.

The backend deployment and migration gate are mandatory on `main`.
`ENABLE_BACKEND_DEPLOYMENT` and `ENABLE_DATABASE_MIGRATIONS` are no longer used.
Missing SQL identity/runner configuration fails the database job and blocks both
application deployments; see [Azure database setup](#azure-database-setup).

Required-check branch protection has not been configured. More backend behavioral
coverage and frontend Vitest tests must be added with application functionality;
issue #2 is not complete merely because this initial workflow exists.

### Backend deployment authentication

The backend job uses OpenID Connect through `id-projekt-skryptowe-1-deploy`.
Its federated credential accepts only `baarsik/projekt-skryptowe-1` on
`refs/heads/main`, with the Azure token-exchange audience. The Bicep parameter
`githubOidcSubjectPrefix` includes GitHub's immutable owner/repository IDs and
must match `sub_claim_prefix` from
`gh api repos/baarsik/projekt-skryptowe-1/actions/oidc/customization/sub`.
Website Contributor is scoped to `projekt-skryptowe-1-api-baarsik`, not the shared resource group,
SQL server, or subscription. Only the backend deployment job requests
`id-token: write`.

The workflow contains public client, tenant, and subscription identifiers, not
an Azure password or publish profile. No backend deployment secret is required.
The app's system-assigned runtime identity is separate and has no database grants.

## Local database development

Each teammate gets an independent SQL Server database using the root
[Compose file](compose.yaml), with a persistent local volume. Copy
[.env.example](.env.example) to `.env` and manually fill in two different local
SQL passwords. No Azure account is needed. Use current Docker with x86-64 Linux
containers and Compose v2. The template sets `COMPOSE_PROJECT_NAME=rachunki-local`
to keep container and volume names stable. For an existing `.env`, add this
non-secret setting if absent. Project naming uses the environment variable so
older Compose v2 clients can parse the file.

Check `docker version` before building: Engine 20.10.8 is known to fail the
current tools image and SQL Server startup. Update Docker Desktop/the engine
first if using that version. Compose parsing alone is not an end-to-end check;
see [the verified setup limitations](backend/README.md#first-time-local-setup-with-docker).

```sh
docker compose build tools
docker compose up -d db
docker compose run --rm tools python -m db.bootstrap --local
docker compose run --rm tools python -m alembic upgrade head
docker compose run --rm tools python -m db.seed --profile demo
```

The optional Python 3.14 tools container runs database commands without installing
Python on the host. Its SQL health-check dependency waits for database readiness.
The frontend and API keep their existing native development
commands. After pulling changes, apply the committed migrations; generate new
ones only when changing the schema. See [backend setup and team workflow](backend/README.md)
for native Python commands, seed profiles, full integration tests, and resetting
local data. See [the schema](docs/schema.md) and [generated creation SQL](docs/schema.sql).

## Azure database setup

The migration identity and its main-only GitHub federation were provisioned on
2026-11-07 in `rg-projekt-skryptowe-1-dev`. Deployment
`rachunki-migration-identity-20261107` applied only those two identity resources,
using an incremental ARM template generated from the Bicep definitions. The
existing hosting resources were outside that deployment. Database permissions,
runner networking and GitHub variables remain separate setup steps.
Before the next `main` deployment:

1. Identity provisioning is complete: `id-projekt-skryptowe-1-migrate` has
   main-only GitHub federation and no Azure management roles. Obtain its public
   client ID with:

   ```sh
   az identity show \
     --resource-group rg-projekt-skryptowe-1-dev \
     --name id-projekt-skryptowe-1-migrate \
     --query clientId --output tsv
   ```

   [hosting.bicep](infra/hosting.bicep) retains the resource definitions; future
   full hosting deployments also reapply hosting settings and need a what-if
   review. The API deployment identity stays separate.
2. As the Microsoft Entra database administrator, connect specifically to
   `rachunki-db` and run [the grants script](infra/sql/grant-database-access.sql).
   It creates contained users for the migration and runtime identities, grants
   schema DDL/DML to the migrator and CRUD to the API, and grants no server-wide
   roles. It must not be run against another database. For customized identity
   names, update the script before running it. Entra administrator/directory
   configuration on the existing shared SQL server is a prerequisite.
3. Provide a Linux x86-64 migration runner with routing and DNS to the SQL private
   endpoint. A self-hosted runner on the connected network is one option; configure
   a dedicated label such as `rachunki-sql`. It needs Azure CLI, unzip, support for
   `actions/setup-python`, the SQL driver's native `libgssapi-krb5-2`/`libltdl7`
   dependencies, and outbound access to GitHub/PyPI/Entra. Standard
   GitHub-hosted networking alone cannot reach the existing private endpoint.
   Keep untrusted PR jobs off that private runner. If using a hosted runner,
   arrange private connectivity explicitly before selecting its label.
4. Manually configure these GitHub repository **variables**, which are public
   identifiers, not secrets:

   | Variable | Value |
   | --- | --- |
   | `AZURE_SQL_MIGRATION_CLIENT_ID` | The new identity's `migrationClientId` |
   | `AZURE_SQL_MIGRATION_RUNNER` | The label of the SQL-connected runner |

The migration job uses OIDC and a tenant-level Azure CLI login; the SQL identity
does not need Website Contributor or subscription-wide permissions. Driver
authentication explicitly selects that CLI session through
`AZURE_TOKEN_CREDENTIALS=AzureCliCredential`. The job installs the tested ZIP's exact
resolved requirements, runs `alembic upgrade head`, then seeds only reference
categories. Either failure blocks both application deployments. Missing variables
fail with an explicit setup message. The old migration opt-in flag is unused.

The API has no HTTP database access yet. When it gains that functionality, configure
its SQL network route/DNS and non-secret settings (`APP_ENV=azure`, `DB_HOST`,
`DB_NAME`, `DB_AUTHENTICATION=ActiveDirectoryMSI`) for its own managed identity.
Neither migrations nor seeds run at application startup. Schema changes must
follow the strict phased compatibility rule in [AGENTS.md](AGENTS.md).

### One-time GitHub secret setup

The user must perform this step manually. In the Azure portal, open the
`projekt-skryptowe-1-web` Static Web App and choose **Manage deployment token**.
Copy that token directly into this GitHub repository's secrets:

```text
AZURE_STATIC_WEB_APPS_API_TOKEN
```

## Azure resources

The [Bicep definitions](infra/main.bicep) describe these development resources:

| Resource | Name | Configuration |
| --- | --- | --- |
| Project resource group | `rg-projekt-skryptowe-1-dev` | Poland Central |
| Frontend | `projekt-skryptowe-1-web` | Static Web Apps Free, West Europe |
| Backend | `projekt-skryptowe-1-api-baarsik` | Python 3.14, enabled, own system-assigned identity |
| Backend deployment identity | `id-projekt-skryptowe-1-deploy` | Main-only GitHub OIDC; API-scoped Website Contributor |
| Database migration identity | `id-projekt-skryptowe-1-migrate` | Provisioned 2026-11-07; main-only GitHub OIDC; database grants applied separately |
| Database | `rachunki-db` | Separate free-offer database on `grandduchy-server` |

The hosting/database resources were provisioned on 2026-11-06; the migration
identity and GitHub federation were provisioned separately on 2026-11-07.
The reserved frontend address is
[ashy-meadow-0ba2cda03.3.azurestaticapps.net](https://ashy-meadow-0ba2cda03.3.azurestaticapps.net).
Frontend files have not been uploaded: the GitHub workflow must first be
published and its frontend deployment token manually configured. The backend
starter was deployed separately while enabling the API, with a successful Azure
build/deployment result. Its address is
[projekt-skryptowe-1-api-baarsik.azurewebsites.net](https://projekt-skryptowe-1-api-baarsik.azurewebsites.net).
Configuration and deployment status were checked through Azure management and
deployment APIs; live application endpoints were not called. The local workflow
changes have not been executed by GitHub Actions.

### Custom domains

| Application | Custom address |
| --- | --- |
| Frontend | [ps1.mmalakhouski.eu](https://ps1.mmalakhouski.eu) |
| Backend | [api.ps1.mmalakhouski.eu](https://api.ps1.mmalakhouski.eu) |

### Shared resources

The backend reuses the existing Linux B1 plan
`ASP-GrandDuchyResourceGroupPolandCe-9c45`; it does not create another paid plan.
It shares that plan's capacity while running. The database is a child
of the existing server in `GrandDuchyResourceGroup-PolandCentral`, so it resides
in that shared resource group rather than the new project resource group.

The database has a 32 GiB maximum size, free limits enabled, a 60-minute idle
auto-pause delay, and `AutoPause` on monthly free-limit exhaustion. There is no
paid-overage fallback. Existing databases and the server's networking are not
modified. Other services, such as future monitoring or additional networking,
can still incur charges.

The identity deployment did not apply SQL grants. Before adding database
integration, create a contained runtime user only in `rachunki-db`, grant the
required application schema permissions, and grant the provisioned migration
identity its database permissions. Do not reuse
GrandDuchy's database credentials or grant server-wide roles. Neither migration
nor seed code should run automatically from application startup.

Future migration jobs also need network connectivity to SQL. The server's
existing private endpoint can serve the new database, but a GitHub-hosted runner
does not automatically have access to that private network.

### Infrastructure setup

Use Azure CLI with Bicep installed, sign in, and confirm the intended subscription.
From the repository root, compile and preview the resources:

```sh
az bicep build --file infra/main.bicep --outfile /tmp/projekt-skryptowe-1-infra.json
az deployment sub what-if \
  --name projekt-skryptowe-1-bootstrap \
  --location polandcentral \
  --parameters infra/dev.bicepparam \
  --result-format ResourceIdOnly
```

To create or update these resources in the selected subscription:

```sh
az deployment sub create \
  --name projekt-skryptowe-1-bootstrap \
  --location polandcentral \
  --parameters infra/dev.bicepparam
```

This is infrastructure provisioning, not an application deployment. It is not
part of normal application CI/CD. Review the parameters and what-if before
applying. The template enables the backend and configures remote dependency build
and Uvicorn startup, but does not upload application code. It produces resource
IDs, public OIDC identifiers, and hostnames, never tokens, passwords, or connection
strings. Initial identity provisioning also needs permission to assign the
API-scoped Azure role; that permission is not granted to the CI identity.

To update only hosting and its deployment identity without applying the SQL module:

```sh
az deployment group what-if \
  --resource-group rg-projekt-skryptowe-1-dev \
  --parameters infra/hosting.dev.bicepparam \
  --result-format ResourceIdOnly
az deployment group create \
  --resource-group rg-projekt-skryptowe-1-dev \
  --parameters infra/hosting.dev.bicepparam
```

The Python startup command is `python -m uvicorn main:app --host 0.0.0.0 --port 8000`.
Azure's remote build installs the artifact's requirements. `alwaysOn` remains
false, so the API can idle and incur a cold start; it does not poll SQL.

## Planned application

Household accounts, expenses, repayments, corrections, balances, three browser
views, and CSV import/export remain planned. CSV details still require agreement.
Backend business functionality and HTTP persistence integration require their own
tasks. Initial migrations/seeding implement
[issue #15](https://github.com/baarsik/projekt-skryptowe-1/issues/15).
See [backend setup issue #5](https://github.com/baarsik/projekt-skryptowe-1/issues/5)
and [backend commands](backend/README.md).

## Contributing

Read [AGENTS.md](AGENTS.md) and append completed AI-assisted work to [AI.md](AI.md).
This project uses the [MIT License](LICENSE).
