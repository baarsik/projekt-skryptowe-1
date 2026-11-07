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
npm run check:export
```

The development server uses `http://localhost:3000`; the production build writes
`out/`, clearing any old export first. It is deployed as static files without a
Next.js server. There is no
`next start` command for this export configuration.

The home, login, signup, and forgot-password pages have dummy English and Polish
content at `/en/` and `/pl/`. `/` redirects to `/pl/`. Every localized page sets
its locale before translation calls. There is no runtime middleware or automatic
language detection in this static hosting model.

`check:export` verifies the eight localized HTML pages, translated headings,
language attributes, localized links, referenced JS/CSS files, the root redirect,
and the static 404. It checks `out/`, so a successful server build cannot satisfy
it. Extend `.github/scripts/check_frontend_export.mjs` when routes change.

PR and deployment CI call the same frontend validation workflow, including all
four commands above. There is no configured Vitest application suite or live
post-deployment check yet. This frontend does not yet call the API or database.

See the [project README](../README.md) for CI/CD, the manual deployment-secret
setup, infrastructure provisioning, and the distinction between existing starter
code and planned application behavior.
