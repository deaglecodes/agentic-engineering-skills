# Install Into a Project

Run these commands from a checkout of Agentic Engineering Skills. The installer requires Python 3.9+ and an existing target directory. Paths containing spaces should be quoted.

```sh
./scripts/install.sh --agent codex --target "/path/to/my project" --dry-run
./scripts/install.sh --agent codex --target "/path/to/my project"
```

Choose one adapter per project:

| Adapter | Project instruction file |
| --- | --- |
| `codex` | `AGENTS.md` |
| `claude` | `CLAUDE.md` |
| `cursor` | `.cursor/rules/agentic-engineering.mdc` |
| `generic` | `AGENTIC_ENGINEERING.md` |

For Codex, Claude, and generic agents, the installer appends a marked section while preserving existing bytes. For Cursor it creates a dedicated rule and refuses to replace an existing file with that name. Existing unrelated Cursor rules stay in place.

The public pack is copied into `.agentic-engineering/pack/`; the manifest at `.agentic-engineering/install.json` records its files and the generated instruction section. The manifest does not copy your original instructions. Scripts in the installed adapter point to their actual location in the project.

This installs local skill reference files, not native slash commands or a registered plugin. The adapter tells the agent which `SKILL.md` files to read. Hooks and package-manager settings are separate, optional steps. No global configuration is changed.

Start a new agent session so the project instructions are loaded. For a generic agent, explicitly point it at `AGENTIC_ENGINEERING.md`. Try:

```text
Use the Agentic Engineering workflow. Inspect this repo, make one small useful improvement, verify it, review the diff, and summarize the evidence.
```

## Reinstall or Change Adapters

Repeating the same installation is a no-op. To use a newer pack or a different adapter, uninstall the current copy, then install again. The installer refuses symlinked managed paths, an unrecognized existing pack directory, or a modified installation.

## Remove

From the source checkout:

```sh
./scripts/install.sh --target "/path/to/my project" --uninstall --dry-run
./scripts/install.sh --target "/path/to/my project" --uninstall
```

Removal deletes only the unchanged managed pack and its generated instruction section. Additions outside that section are preserved. A pre-existing instruction file, including an empty one, is kept. If you changed the managed section or added/changed files inside the pack, removal stops without changing anything; preserve your edits and remove the installation manually or restore the managed files before retrying. Separate package-safety files remain in place.

Review the target project's diff before committing the installation. Keep the manifest with the pack if committing it so another checkout can remove it safely. Installing the pack is not proof that an agent followed it.

## Optional Package Safety

From the **target project**, inspect the current configuration:

```sh
./.agentic-engineering/pack/scripts/check-package-age-safety.sh --scope=all --target .
```

To add project-local settings after reviewing the preview:

```sh
./.agentic-engineering/pack/scripts/setup-package-age-safety.sh --mode=project-local --target . --dry-run
./.agentic-engineering/pack/scripts/setup-package-age-safety.sh --mode=project-local --target .
```

The pip template is active only when selected through `PIP_CONFIG_FILE=.agentic-engineering/package-safety/pip.conf`, `PIP_UPLOADED_PRIOR_TO=P7D`, or user/site pip configuration. Read [package safety](package-age-safety.md) for supported managers and the separate, explicitly confirmed user-wide setup.

## Optional Hooks

See the [Claude guide](claude.md) before merging settings into an existing configuration. The installer does not enable hooks. From the target project you can run the generic checks manually:

```sh
./.agentic-engineering/pack/hooks/verify-before-finish.sh
./.agentic-engineering/pack/hooks/block-risky-package-install.sh npm .
```

Use your application's own tests and runtime checks to validate application changes. The pack's validation script validates the pack itself.
