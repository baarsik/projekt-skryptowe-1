# Dzielenie rachunków

`Dzielenie rachunków` is a planned shared household expense and reimbursement
application. See [issue #11](https://github.com/baarsik/projekt-skryptowe-1/issues/11)
for the proposed functional scope.

## Current state

- `frontend/` contains the Next.js 16.4.3, React 19.3.0, and TypeScript starter. It
  does not yet implement expenses, accounts, balances, or API requests.
- The frontend exports static HTML/CSS/JavaScript to `frontend/out/`, including
  English and Polish home, login, signup, and forgot-password pages with dummy
  content. `/` redirects to `/pl/` without a Next.js server.
- [Application CI/CD](.github/workflows/ci-cd.yml) validates both applications and
  prepares their Azure deployments. Frontend deployment requires the user-provided
  GitHub secret described below and this workflow on GitHub.
- `backend/` contains a FastAPI starter with a `GET /` endpoint returning
  `{"msg": "Hello World"}`, with pytest checks for the endpoint and deployment
  packaging. It has no database integration or household application functionality.
- `infra/` defines the frontend host, enabled Python backend host, its narrowly
  scoped GitHub deployment identity, and a separate free-offer SQL database.
  Database users, application tables, migrations, and seeding are not implemented.
- PRs to `main` run backend Ruff/pytest on Python 3.14 and frontend validation on
  Node.js 24 in parallel. PR and deployment workflows share frontend lint,
  TypeScript, build, and static artifact checks. Vitest application tests and
  post-deployment application checks remain planned.

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
npm run check:export
```

The build clears old `frontend/out/` files before writing the static deployment
artifact, so an earlier export cannot hide a later server build. Static hosting
runs no Next.js server. Server Actions, runtime server rendering, and API routes
requiring a server are outside this deployment model. Image optimization is
disabled so images do not require a Next.js server. Cache Components and Partial
Prefetching from the starter are disabled for the static configuration.

Localization uses next-intl with explicit `/en/` and `/pl/` prefixes. Every
localized page sets its request locale before using translations, so rendering
never needs incoming request headers. Middleware and automatic browser-language detection are disabled
for static hosting. The root page emits a static redirect to `/pl/`.

`check:export` checks the actual `out/` artifact: all eight localized pages,
translated headings, language attributes, localized links, referenced JS/CSS,
the root redirect, and `404.html`. It fails if a server build succeeds without
producing the static files. Run it after every build; extend its route expectations
when adding or changing pages. It uses Node's standard library with no additional
dependencies and does not replace future Vitest application tests.

The frontend currently has no API address setting and does not contact the
backend or database. Define and document build-time API configuration
when API integration is implemented. Never put database configuration into the
browser build.

## Pull request CI

[ci.yml](.github/workflows/ci.yml) runs only for pull requests targeting `main`.
Its backend job installs `backend/requirements.txt` and Ruff, runs
`python -m ruff check .`, and runs `python -m pytest -q` from `backend/` using
Python 3.14. In parallel, it calls the shared
[frontend validation workflow](.github/workflows/frontend-validation.yml), which
uses Node.js 24 and runs `npm ci`, lint, type checking, the production build, and
`npm run check:export` before saving the validated static artifact. The same
workflow validates the frontend before deployment on `main`.

This workflow does not deploy or request Azure credentials. Frontend Vitest
application tests remain planned; static artifact validation runs now.

## Application CI/CD

The [workflow](.github/workflows/ci-cd.yml) implements this initial portion of
[issue #2](https://github.com/baarsik/projekt-skryptowe-1/issues/2) and
[issue #3](https://github.com/baarsik/projekt-skryptowe-1/issues/3):

1. Pushes to `main` and manual runs validate the frontend and run backend pytest
   in parallel. The frontend uses the committed npm lockfile; backend requirements
   are installed into a Python 3.14 virtual environment matching Azure.
2. Both validation jobs must pass before either deployment can start.
3. `frontend-static` contains the exported frontend. `backend-source` contains a
   ZIP of the tested commit's Git-tracked backend code, excluding tests and local
   environments. Its requirements record the exact dependency versions resolved
   during that validation run. Artifacts are retained for seven days.
4. Successful `main` runs deploy those artifacts independently to Static Web Apps
   and App Service. A manual run can deploy only when its branch is `main`.
5. Pull requests never deploy, receive the Azure deployment secret, or obtain
   Azure OIDC tokens. Main runs are serialized. There are no preview environments
   or smoke tests.

The workflow is organized in that order: **validate → deploy → future database
work**. Every step has a descriptive name. Backend ZIP creation lives in the
[packaging helper](.github/scripts/package_backend.py), so the YAML shows the
release sequence rather than embedded Python code. Its regression tests run as
part of the backend pytest job.

The backend deployment is enabled without an opt-in repository variable.
`ENABLE_BACKEND_DEPLOYMENT` is no longer used. Only the database job remains a
placeholder: leave `ENABLE_DATABASE_MIGRATIONS` unset. Setting it to `true` fails
that job until real migrations and seeding replace it.

The existing `main-protection` ruleset requires a pull request and approval, but
does not require passing status checks (checked on 2026-11-07). To prevent merging
failed checks, also require the PR's `Frontend validation / Static frontend checks`
and `Backend lint and tests` checks in that ruleset. This change does not update
GitHub settings; workflow files alone cannot enforce repository merge rules.
More backend behavioral coverage and frontend Vitest tests must be added with
application functionality; issue #2 is not complete merely because this workflow exists.

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
| Database | `rachunki-db` | Separate free-offer database on `grandduchy-server` |

These resources were provisioned on 2026-11-06. The reserved frontend address is
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

The backend runtime identity has no database grants. Before adding database
integration, create a contained runtime user only in `rachunki-db`, grant the
required application schema permissions, and configure a separate migration identity. Do not reuse
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
Backend business functionality, persistence integration, and database design
require their own tasks. See [backend setup issue #5](https://github.com/baarsik/projekt-skryptowe-1/issues/5)
and [backend commands](backend/README.md).

## Contributing

Read [AGENTS.md](AGENTS.md) and append completed AI-assisted work to [AI.md](AI.md).
This project uses the [MIT License](LICENSE).
