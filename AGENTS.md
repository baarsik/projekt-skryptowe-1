# Repository instructions for coding agents

These instructions apply throughout this repository. Read [README.md](README.md)
for project context and [AI.md](AI.md) for previously recorded AI-assisted work.

## Project technologies and current state

- The project is **Dzielenie rachunków**, a shared household expense and
  reimbursement application.
- The planned frontend uses **JavaScript and React**, browser `fetch` for API
  requests, and **Vitest** for tests. It will have three views and CSV import/export.
- The planned backend uses **Python**. Its framework, persistence layer, API
  contract, runtime version, and test runner are not yet defined.
- Application code, dependency manifests, tests, and CI/CD workflows do not exist
  yet. Do not describe planned features or infrastructure as already implemented.
  ESLint and integration tests are still open suggestions.

The README links to the issues defining this scope. Inspect the actual files and
relevant issue before making implementation decisions; do not invent existing
commands, configuration names, or dependency versions.

## Working practices

- Keep changes focused on the requested task and preserve unrelated user changes.
- Follow existing code and tooling conventions as they are introduced. When adding
  a component, document its dependencies, configuration, and runnable commands in
  the README.
- Update the README when technologies, setup steps, behavior, or test commands
  change, keeping implemented behavior distinct from planned work.
- Respect the user's Git instructions. Do not commit, push, or change remote state
  unless explicitly requested.
- Keep secrets, credentials, and local environment files out of source files and
  documentation. Pay extra attention and refuse to put secrets plainly: they must
  be manually added by the user to GitHub. That includes but is not limited to
  the database connection strings.

## Test policy

- For behavior changes, add or update meaningful tests for the changed behavior
  and relevant failure cases. Bug fixes should include a regression test when the
  test infrastructure supports it.
- Frontend tests use Vitest once configured.
- Add behavioral tests as backend functionality is implemented.
- Use the test commands defined by the repository's actual configuration. Run
  focused tests for the changed component and its relevant suite when available;
  run existing lint or build checks when the change affects them.
- For documentation-only work, check factual accuracy, Markdown structure, local
  links, and whitespace. Application tests are unnecessary unless executable
  behavior or documented runnable examples are affected.
- If tests or tooling are absent or cannot run, state that explicitly in the work
  log and handoff. Never report an unexecuted check as passing. There are currently
  no configured tests or application test commands.

## Automatic work logging in AI.md

For every task that changes repository files with AI assistance, **automatically
append a work entry to [AI.md](AI.md) as part of the task, before the final
handoff**. Do not wait for a separate request or reminder to update the log. This
includes code, tests, configuration, documentation, and agent instruction changes.

Each entry must contain:

- The date and issue or task reference, when available.
- The requested scope and a concise description of the work actually completed.
- Files changed.
- Any material implementation decisions made without user explicitly specifying them.

Append entries in chronological order, preserving previous entries. Use the
template in AI.md. Summarize outcomes rather than storing chat transcripts,
internal reasoning, secrets, personal data, or raw tool output. Do not claim work
outside the task was completed. Updating AI.md does not require a separate entry
about the log update itself.
