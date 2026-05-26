# Release Checklist

Use this before tagging, publishing, or public promotion.

## Preflight

- Confirm the release version and scope.
- Review `CHANGELOG.md`, `ROADMAP.md`, `README.md`, `SECURITY.md`, and `CONTRIBUTING.md`.
- Confirm docs do not overclaim official support or security guarantees.
- Confirm Claude plugin metadata is valid JSON and conservative.

## Validation

```sh
./scripts/validate-repo.sh
```

If validation fails, either fix the issue or document the failure and why the release can still proceed.

## Fresh-Install Smoke

In a temp directory:

1. Clone the branch.
2. Run `./scripts/validate-repo.sh`.
3. Copy the Codex adapter into a scratch project.
4. Copy the Claude adapter into a scratch project.
5. Run project-local package safety setup.
6. Run hook scripts with mock inputs.
7. Confirm no global user config changed.

## Release Notes

Include:

- Major changes.
- Supported agents.
- Hook and package-safety caveats.
- Validation results.
- Known limitations.

## Do Not

- Do not push to `main` without maintainer intent.
- Do not publish a plugin marketplace listing without explicit approval.
- Do not include private local paths, credentials, or config contents.
