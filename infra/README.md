# Azure deployment

[Bicep](main.bicep) defines the project infrastructure. GitHub Actions deploys
application code separately using **validate → migrate → deploy**. The API
deployment and database migration jobs use separate identities, each trusted only
for this repository's `main` branch.

## Resources

| Resource | Name |
| --- | --- |
| Project resource group | `rg-projekt-skryptowe-1-dev` |
| Static Web App | `projekt-skryptowe-1-web` |
| Python App Service | `projekt-skryptowe-1-api-baarsik` |
| API deployment identity | `id-projekt-skryptowe-1-deploy` |
| Migration identity | `id-projekt-skryptowe-1-migrate` |
| SQL database | `rachunki-db` on `grandduchy-server` |

The API shares the existing B1 App Service plan. SQL belongs to the shared
`GrandDuchyResourceGroup-PolandCentral` resource group. See the [parameters](dev.bicepparam)
and [hosting parameters](hosting.dev.bicepparam) for exact resource settings.
The SQL free limit pauses the database on exhaustion rather than allowing paid
overage; its configured idle auto-pause delay is 60 minutes.

## Database access

The migration identity and GitHub federation were provisioned on 2026-11-07.
Database grants, runner connectivity and GitHub variables still require setup:

1. As the Microsoft Entra database administrator, connect to **`rachunki-db`**
   and run [grant-database-access.sql](sql/grant-database-access.sql). The migrator
   gets schema-change/data permissions in `dbo`; the API gets CRUD permissions.
   This requires Entra authentication on the SQL server and grants no server-wide
   roles. Use this project's identities rather than another application's credentials.
2. Provide a Linux x86-64 migration runner with routing and DNS to SQL's private
   endpoint. It needs Azure CLI, unzip, support for `actions/setup-python`,
   `libgssapi-krb5-2`, `libltdl7`, and access to GitHub, PyPI and Entra endpoints.
   A standard GitHub-hosted runner has no access to the private endpoint by default.
   Assign a dedicated label, such as `rachunki-sql`; PR jobs stay on hosted runners.
3. Set the GitHub repository variables below. Obtain the public client ID with:

   ```sh
   az identity show \
     --resource-group rg-projekt-skryptowe-1-dev \
     --name id-projekt-skryptowe-1-migrate \
     --query clientId --output tsv
   ```

   | Variable | Value |
   | --- | --- |
   | `AZURE_SQL_MIGRATION_CLIENT_ID` | Migration identity's client ID |
   | `AZURE_SQL_MIGRATION_RUNNER` | SQL-connected runner label |

The migration job uses OIDC and explicitly selects its Azure CLI credential.
It runs `alembic upgrade head` and reference seeding from the validated backend
ZIP, with the dependency versions resolved during CI. A failed migration/seed
or missing configuration blocks both application deployments. Demo data is local
only; migrations and seeds never run from API startup.

## Frontend deployment token

The user must manually copy the Static Web App's **Manage deployment token**
value from the Azure portal into the GitHub secret
`AZURE_STATIC_WEB_APPS_API_TOKEN`. Database authentication uses identities rather
than a password. Keep secrets and connection strings out of source and documentation.

## Infrastructure changes

Use Azure CLI with Bicep installed. From the repository root, sign in and confirm
the subscription referenced in [hosting.dev.bicepparam](hosting.dev.bicepparam).
Review what-if before applying: deploying a template can reapply existing app
settings. Initial provisioning also requires permission to create role assignments;
the CI identities do not have that permission.

For hosting changes without applying the SQL module:

```sh
az deployment group what-if \
  --resource-group rg-projekt-skryptowe-1-dev \
  --parameters infra/hosting.dev.bicepparam
az deployment group create \
  --resource-group rg-projekt-skryptowe-1-dev \
  --parameters infra/hosting.dev.bicepparam
```

For initial provisioning or changes that also include the database:

```sh
az deployment sub what-if \
  --location polandcentral \
  --parameters infra/dev.bicepparam
az deployment sub create \
  --location polandcentral \
  --parameters infra/dev.bicepparam
```

