# AI-assisted work log

This file records the scope, results, and validation of AI-assisted repository
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

### 2026-11-07 — Issue #23: Vitest frontend tests

- Scope: Add frontend unit testing to local checks and shared CI, documented in the repository. The test was written by the user; AI assistance was limited to review, verification, and guidance.
- Changes: Added Vitest, React Testing Library, jsdom, and `test`/`test:run` scripts to `frontend/package.json`. Added a root page test in `frontend/__tests__/page.test.tsx` checking the link to the default locale. Added a `Run frontend tests` step (`npm run test:run`) to `.github/workflows/frontend-validation.yml` between type checking and build. Updated `README.md` and `AGENTS.md`. Chose `test:run` for CI so the job cannot hang in watch mode. The deprecated `vite-tsconfig-paths` warning was left for a separate change.
