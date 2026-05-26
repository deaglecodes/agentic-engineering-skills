# Agentic Engineering Skills Claude Plugin

This directory packages the repository skills and optional hooks for Claude Code plugin-style installation.

## Contents

- `plugin.json`: plugin metadata and skill list.
- `hooks.json`: example Claude Code hooks for package-install gating and final verification.
- `../skills/`: packaged skills used by the plugin.
- `../hooks/claude/`: hook command scripts.
- `../examples/claude/`: settings examples for local, non-plugin use.

## Install Modes

Use Claude Code's plugin commands when publishing through a plugin marketplace. For per-project use without marketplace publishing, copy `adapters/claude/CLAUDE.md` into the target repo and copy only the hook settings you want from `examples/claude/`.

## Hook Safety

The hooks are intentionally local:

- They inspect Bash commands before package installs.
- They run local validation before finishing.
- They do not print private config contents.
- They do not modify global configuration.

Disable hooks by removing the matching section from your Claude settings or uninstalling the plugin.
