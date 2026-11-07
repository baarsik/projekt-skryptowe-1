# AI-assisted work log

This file records the scope and results of AI-assisted repository
changes. Coding agents append an entry for each task that changes files, following
[AGENTS.md](AGENTS.md). Entries describe completed work and preserve earlier history.

## Entry template

Copy this template to the end of the log and replace the placeholders:

```markdown
### YYYY-MM-DD — Issue #N or task title

- Scope: Requested goal and boundaries.
- Changes: Work completed, affected files, and material decisions.
```

## Entries

### 2026-10-24 — Issue #6: Documentation

- Scope: Documentation.
- Changes: Added README.md, AI.md. Introduced AI policies. Added a reusable entry template.

### 2026-11-06 — Issues #2/#3: CI/CD

- Scope: Initial CI/CD using existing Azure setup.
- Changes: Configured static frontend and backend deployment, added setup documentation. Enabled deployment with pytest checks and OIDC authentication.

### 2026-11-06 — Issue #2: Pull request checks

- Scope: Backend checks for PRs to main; frontend checks left as TODO.
- Changes: Switched `ci.yml` to Python 3.14, installed Ruff directly, and updated both READMEs; kept deployment CI on main/manual runs and updated setup instructions.

### 2026-11-07 — Issue #15: Alembic migrations, seeding and local SQL

- Scope: Set up initial migrations and repeatable seed data, support independent
  local Docker development, and make Azure deployment depend on migrations.
- Changes: Added connection/settings, bootstrap, schema and transactional seeds
  in `backend/db/`; Alembic configuration/revision in `backend/alembic.ini` and
  `backend/migrations/`; generated `docs/schema.sql` and aligned `docs/schema.md`.
  Extended the existing user-created `compose.yaml`/`.env.example`, added
  `backend/Dockerfile.tools`/`.dockerignore`, and declared database dependencies.
  Added configuration/SQL integration tests and extended packaging tests. Updated
  both workflows and added `.github/scripts/start_test_database.py`. Added a
  separate migration identity/output in hosting/main Bicep and a guarded grants
  script in `infra/sql/`. Updated both READMEs, amended AGENTS.md with strict
  phased compatibility and database/test guidance, and recorded the plan in
  `docs/superpowers/plans/2026-11-07-database-migrations.md`.

### 2026-11-07 — Simplify project documentation

- Scope: Review documentation for relevance, duplication and readability.
- Changes: Shortened README.md to an overview; consolidated developer commands in
  backend/README.md and frontend/README.md and Azure administration in the new
  infra/README.md. Trimmed docs/schema.md to the diagram and key constraints;
  removed deployment narration, obsolete flags and repeated implementation details.
  Updated the AI.md introduction and appended this entry. Kept runnable setup,
  Docker limitations, pending Azure prerequisites and existing agent policies.

### 2026-11-07 — Issues #2/#3: Static frontend export and PR validation

- Scope: Fix Application CI/CD runs #2/#3 in a separate worktree and catch the
  same regressions in pull request CI, preserving the original checkout.
- Changes: Restored export settings in `frontend/next.config.ts`, initialized
  locale in all four `frontend/app/[locale]/` pages, restricted generated locales
  in its layout, added root `frontend/app/(default)/layout.tsx` and `page.tsx`, disabled
  request-based locale detection in `frontend/i18n/routing.ts`, and removed
  `frontend/proxy.ts`. Added `.github/scripts/check_frontend_export.mjs` to check
  localized HTML, links, JS/CSS, the root redirect, and 404; added its command and
  stale-output cleanup to `frontend/package.json`. Both `.github/workflows/ci.yml`
  and `ci-cd.yml` now call the shared `frontend-validation.yml` workflow. Updated
  `README.md`, `frontend/README.md`, and `AGENTS.md`. Kept static hosting and
  the existing Polish default locale; used Node's standard library for artifact
  checks without adding dependencies. Documented the existing ruleset's missing
  required status checks; GitHub repository settings were not changed.

### 2026-11-07 — Merge latest main into Alembic branch

- Scope: Pull latest changes, resolve conflicts, keep documentation minimal and push.
- Changes: Merged main's localized frontend and shared CI validation into the
  Alembic branch. Resolved README.md and frontend/README.md with concise current
  setup/check instructions; combined both AI.md histories and appended this entry.
  Kept the existing database migration gate and separate Azure guide.
