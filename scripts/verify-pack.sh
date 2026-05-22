#!/usr/bin/env sh
set -eu

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
tmp="$(mktemp "${TMPDIR:-/tmp}/agentic-skills.XXXXXX")"
trap 'rm -f "$tmp"' EXIT

find "$root/skills" -mindepth 2 -maxdepth 2 -name SKILL.md | sort >"$tmp"
count="$(wc -l < "$tmp" | tr -d ' ')"

if [ "$count" -lt 6 ]; then
  printf '%s\n' 'verify pack: expected at least 6 skills'
  exit 1
fi

for path in \
  "$root/adapters/codex/AGENTS.md" \
  "$root/adapters/claude/CLAUDE.md" \
  "$root/adapters/cursor/.cursor/rules/agentic-engineering.mdc" \
  "$root/templates/package-age/npm.npmrc" \
  "$root/templates/package-age/pnpm-workspace.yaml" \
  "$root/templates/package-age/bunfig.toml" \
  "$root/templates/package-age/yarnrc.yml" \
  "$root/templates/package-age/uv.toml" \
  "$root/templates/package-age/pip.conf" \
  "$root/templates/package-age/mise-config.toml"; do
  if [ ! -s "$path" ]; then
    printf '%s\n' "verify pack: missing $path"
    exit 1
  fi
done

printf '%s\n' 'verify pack: ok'
