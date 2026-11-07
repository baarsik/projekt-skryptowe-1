# Dzielenie rachunków

A prototype for sharing household expenses and calculating reimbursements.
The proposed application scope is in [issue #11](https://github.com/baarsik/projekt-skryptowe-1/issues/11).

## Current state

- **Frontend:** Static English/Polish home and placeholder authentication screens
  built with Next.js, React and TypeScript.
- **Backend:** Python 3.14/FastAPI starter with `GET /` returning
  `{"msg": "Hello World"}`.
- **Database:** SQL Server/Azure SQL schema, Alembic migrations and repeatable
  reference/demo seeds. The HTTP API does not use the database yet.
- **Deployment:** Azure hosting and a separate migration identity are provisioned.
  SQL permissions, migration-runner connectivity and GitHub configuration are
  still needed before the deployment workflow can complete.

Authentication, household screens, expense/repayment logic, corrections, balances
and CSV import/export remain planned.

## Development

| Area | Requirements | Instructions |
| --- | --- | --- |
| Frontend | Node.js 24 | [Run and check the frontend](frontend/README.md) |
| Backend and database | Python 3.14; current Docker for local SQL | [Setup, migrations, seeds and tests](backend/README.md) |
| Azure | Azure CLI, Bicep and administrator access | [Deployment and remaining setup](infra/README.md) |
| Schema | SQL Server/Azure SQL | [Diagram and constraints](docs/schema.md), [creation SQL](docs/schema.sql) |

## CI/CD

[Pull requests](.github/workflows/ci.yml) run backend Ruff and pytest, including
SQL integration tests against a disposable database. Frontend checks cover lint,
TypeScript, build and static export validation, shared with deployment CI.
Vitest application tests are not configured yet.

[Main builds](.github/workflows/ci-cd.yml) validate the frontend and backend,
apply database migrations and reference seeds, then deploy both applications.
Both deployments require successful migrations and use the validated build
artifacts. Only `main` can deploy, including manual runs.

To block merges on failed CI, require `Frontend validation / Static frontend checks`
and `Backend lint and tests` in branch protection.

Configured addresses: [frontend](https://ps1.mmalakhouski.eu) and
[API](https://api.ps1.mmalakhouski.eu).

## Contributing

Follow [AGENTS.md](AGENTS.md). AI-assisted changes are recorded in [AI.md](AI.md).
The project uses the [MIT License](LICENSE).
