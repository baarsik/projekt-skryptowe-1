# Frontend

Next.js, React and TypeScript starter. Household screens and API integration are
not implemented yet.

Use Node.js 24, as specified in [`.nvmrc`](../.nvmrc). From `frontend/`:

```sh
npm ci
npm run dev
```

Open `http://localhost:3000`. Before submitting changes:

```sh
npm run lint
npm run typecheck
npm run build
```

The build exports static files to `out/` for Azure Static Web Apps. Features
requiring a Next.js server, such as API routes and runtime server rendering,
are unavailable in this deployment. Vitest is not configured yet.

See [CI/CD](../README.md#cicd) and [Azure deployment setup](../infra/README.md).
