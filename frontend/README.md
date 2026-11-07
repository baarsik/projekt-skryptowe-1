# Frontend

Next.js, React, TypeScript and next-intl. English/Polish home, login, signup and
forgot-password pages use placeholder content; authentication and API integration
are not implemented. Routes use `/en/` and `/pl/`; `/` redirects to `/pl/`.

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
npm run check:export
```

The build replaces `out/` with static files for Azure Static Web Apps; it runs no
Next.js server or middleware. Set the request locale before translation calls in
new localized pages. Automatic browser-language detection is disabled.

`check:export` checks the exported pages, links, assets, root redirect and 404.
Update its [route expectations](../.github/scripts/check_frontend_export.mjs)
when pages change. Vitest application tests are not configured yet.

See [CI/CD](../README.md#cicd) and [Azure deployment setup](../infra/README.md).
