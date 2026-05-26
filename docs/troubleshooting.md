# Troubleshooting

## `validate-repo.sh` Fails Because `shellcheck` Is Missing

`shellcheck` is optional. The validation script reports it as skipped when unavailable. CI installs it where feasible.

## Package Install Hook Blocks npm

Run:

```sh
npm --version
./scripts/check-package-age-safety.sh --scope=all
```

npm must be `11.10.0` or newer before relying on `min-release-age`.

## Package Install Hook Blocks pip

Modern pip support is required for duration upload filters. For project-local usage, run pip with:

```sh
PIP_CONFIG_FILE=.agentic-engineering/package-safety/pip.conf python -m pip install PACKAGE_NAME
```

## User-Wide Setup Was A Mistake

If the setup script printed a backup path, restore it:

```sh
./scripts/setup-package-age-safety.sh --restore=/path/to/backup
```

## Claude Stop Hook Keeps Blocking

Run the underlying check:

```sh
./hooks/verify-before-finish.sh
```

Fix the reported issue, or temporarily remove the `Stop` hook from `.claude/settings.json` or `.claude/settings.local.json`.

## Secret Scan Flags Documentation

Use placeholders without assignment syntax. Avoid examples that look like real credential assignments.

## Cursor Does Not Change Behavior

Confirm the rule exists in the target repo at `.cursor/rules/agentic-engineering.mdc` and that Cursor project rules are enabled.
