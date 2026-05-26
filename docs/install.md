# Installation Notes

Use one adapter per target project. Copy skills only when the agent supports reusable skill folders.

## Codex

```sh
cp adapters/codex/AGENTS.md /path/to/project/AGENTS.md
```

Smoke test:

```text
Use the Agentic Engineering workflow. Inspect this repo, propose a tiny safe docs improvement, make it, verify it, review the diff, and summarize checks.
```

Uninstall by removing the copied `AGENTS.md` or merging out the Agentic Engineering section.

## Claude Code

```sh
cp adapters/claude/CLAUDE.md /path/to/project/CLAUDE.md
```

For plugin-style packaging, use `.claude-plugin/plugin.json` with the packaged skills. Hook examples are separate because Claude Code hooks are configured through settings files.

## Cursor

```sh
mkdir -p /path/to/project/.cursor/rules
cp adapters/cursor/.cursor/rules/agentic-engineering.mdc /path/to/project/.cursor/rules/
```

Uninstall by deleting `.cursor/rules/agentic-engineering.mdc`.

## Generic Agents

```sh
cp adapters/generic/AGENTIC_ENGINEERING.md /path/to/project/AGENTIC_ENGINEERING.md
```

Paste or link that file into the agent's instruction mechanism.

## Package Safety

Read-only audit:

```sh
./scripts/check-package-age-safety.sh --scope=all
```

Project-local setup:

```sh
./scripts/setup-package-age-safety.sh --mode=project-local --target /path/to/project
```

Project-local setup does not create backup copies of existing package-manager files, because those files can contain private registry tokens. For pip, use the generated template through `PIP_CONFIG_FILE=.agentic-engineering/package-safety/pip.conf`, set `PIP_UPLOADED_PRIOR_TO=P7D`, or rely on user/site pip config.

User-wide setup is opt-in:

```sh
./scripts/setup-package-age-safety.sh --mode=user-wide --dry-run
./scripts/setup-package-age-safety.sh --mode=user-wide --confirm-user-wide
```

If user-wide setup creates backups, the script prints a restore command. Do not paste private package-manager config contents into issues or pull requests.

## Hooks

Optional hooks live in `hooks/` and `hooks/claude/`. Run them manually or wire them into an agent hook system:

```sh
./hooks/verify-before-finish.sh
./hooks/block-risky-package-install.sh npm /path/to/project
```
