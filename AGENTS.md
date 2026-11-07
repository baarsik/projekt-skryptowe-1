# Repository instructions for coding agents

These instructions apply throughout this repository. Read [README.md](README.md)
for project context and [AI.md](AI.md) for previously recorded AI-assisted work.

## Project technologies and current state

- The project is **Dzielenie rachunków**, a shared household expense and
  reimbursement application.
- The frontend starter uses **Next.js, React, and TypeScript**, exporting static
  files from `frontend/` to Azure Static Web Apps. Browser `fetch` integration,
  **Vitest**, three application views, and CSV import/export remain planned.
- The backend uses **Python 3.14**, **FastAPI**, **Uvicorn**, and **pytest**.
- Explicit database tools use **SQLAlchemy 2.1**, **Alembic**, and
  **mssql-python** for local SQL Server and Azure SQL. Docker Compose provides
  isolated local SQL and an optional Python tools container. The API has no
  database-backed household endpoints yet.
- The frontend has a dependency lockfile, ESLint, type checking, a static build,
  and a GitHub Actions workflow with parallel frontend/backend validation and
  main-only deployment of both artifacts.

The README links to the issues defining this scope. Inspect the actual files and
relevant issue before making implementation decisions; do not invent existing
commands, configuration names, or dependency versions.

## Working practices

- Keep changes focused on the requested task and preserve unrelated user changes.
- Follow existing code and tooling conventions as they are introduced. When adding
  a component, document its dependencies, configuration, and runnable commands in
  the README.
- Update the README when technologies, setup steps, behavior, or test commands
  change, keeping implemented behavior distinct from planned work.
- Respect the user's Git instructions. Do not commit, push, or change remote state
  unless explicitly requested.
- Keep secrets, credentials, and local environment files out of source files and
  documentation. Pay extra attention and refuse to put secrets plainly: they must
  be manually added by the user to GitHub. That includes but is not limited to
  the database connection strings.

## Database compatibility rule

Schema changes must preserve compatibility with the currently deployed application.
Add replacement structures and migrate data before switching application usage.
Remove obsolete columns or tables only in a later deployment, after all deployed
application versions have stopped using them and rollback compatibility has been
addressed. Apply this rule strictly during implementation and code review.

Run migrations as an explicit deployment step before application deployment.
Never run migrations or seeds from application startup. Keep demo seed data local.

## Test policy

- For behavior changes, add or update meaningful tests for the changed behavior
  and relevant failure cases. Bug fixes should include a regression test when the
  test infrastructure supports it.
- Frontend tests use Vitest once configured.
- Add behavioral tests as backend functionality is implemented.
- Use the test commands defined by the repository's actual configuration. Run
  focused tests for the changed component and its relevant suite when available;
  run existing lint or build checks when the change affects them.
- For documentation-only work, check factual accuracy, Markdown structure, local
  links, and whitespace. Application tests are unnecessary unless executable
  behavior or documented runnable examples are affected.
- If tests or tooling are absent or cannot run, state that explicitly in the work
  log and handoff. Never report an unexecuted check as passing. There are currently
  no configured frontend application tests. Frontend checks are `npm run lint`,
  `npm run typecheck`, and `npm run build` from `frontend/`. Run backend tests
  with `.venv/bin/python -m pytest -q` from `backend/` after installing its
  requirements into that virtual environment.

SQL integration tests are skipped unless `DB_INTEGRATION_TESTS=1`. With local SQL
running and credentials configured, use
`DB_INTEGRATION_TESTS=1 .venv/bin/python -m pytest -q` from `backend/`, or
`DB_INTEGRATION_TESTS=1 docker compose run --rm tools python -m pytest -q` from
the root. These tests create/remove only isolated `rachunki_test_*` databases.
Both backend CI workflows run them against disposable SQL containers.

## Automatic work logging in AI.md

For every task that changes repository files with AI assistance, **automatically
append a work entry to [AI.md](AI.md) as part of the task, before the final
handoff**. Do not wait for a separate request or reminder to update the log. This
includes code, tests, configuration, documentation, and agent instruction changes.

Each entry must contain:

- The date and issue or task reference, when available.
- The requested scope and a concise description of the work actually completed (except validations).
- Files changed.
- Any material implementation decisions made without user explicitly specifying them.

Append entries in chronological order, preserving previous entries. Use the
template in AI.md. Summarize outcomes rather than storing chat transcripts,
internal reasoning, secrets, personal data, or raw tool output. Do not claim work
outside the task was completed. Updating AI.md does not require a separate entry
about the log update itself.
