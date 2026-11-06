# Frontend starter

This is the project's Next.js/React/TypeScript starter, configured for static
export to Azure Static Web Apps. Household application functionality and API
integration are not implemented yet.

Use Node.js 24. From this directory:

```sh
npm ci
npm run dev
```

Run the configured checks and create the static output:

```sh
npm run lint
npm run typecheck
npm run build
```

The development server uses `http://localhost:3000`; the production build writes
`out/`. It is deployed as static files without a Next.js server. There is no
`next start` command for this export configuration.

There is no configured Vitest suite yet. Frontend checks in the PR-only workflow
remain a TODO. The main deployment workflow validates the frontend and backend
before deploying either. This frontend does not yet call the API or database.
There are no smoke tests.

See the [project README](../README.md) for CI/CD, the manual deployment-secret
setup, infrastructure provisioning, and the distinction between existing starter
code and planned application behavior.
