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
