# Dzielenie rachunków

`Dzielenie rachunków` is an application for tracking shared household expenses and
showing who should reimburse whom.

## Project status

The repository is at the documentation stage. It contains this README, contributor
instructions, an AI work log, a Python-oriented `.gitignore`, and the MIT license.
Application code, dependency manifests, tests, and CI/CD configuration have not yet
been added. The features and technologies below describe the planned scope, not
functionality that is already available.

## Planned functionality

- Track combined household expenses and payments owed between users.
- Provide three browser views; their contents are still to be defined.
- Retrieve data from a backend API using the browser's `fetch` API.
- Import and export CSV data.

## Local development and testing

There is currently no application to install or run, and no configured test
command.

When those components are added, update this README with the supported runtime
versions, dependency installation steps, configuration variables, and exact
development, build, and test commands. Document how to provide the API address at
frontend build time; no environment variable name has been established yet.

The initial backend dummy test will verify that the test pipeline runs. Behavioral
tests should be added with application functionality. See [AGENTS.md](AGENTS.md)
for the contributor testing policy.

## Repository guide

| File | Purpose |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Instructions for coding agents, including testing and work logging |
| [AI.md](AI.md) | Append-only record of AI-assisted changes and validation |

## Contributing

Read [AGENTS.md](AGENTS.md) before changing the repository. Keep changes focused on
the relevant issue, update documentation when project behavior or setup changes,
and record AI-assisted work in [AI.md](AI.md).

## License

This project is licensed under the [MIT License](LICENSE).
