#!/usr/bin/env sh
set -eu

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
tmp="$(mktemp "${TMPDIR:-/tmp}/agentic-skills.XXXXXX")"
trap 'rm -f "$tmp"' EXIT

find "$root/skills" -mindepth 2 -maxdepth 2 -name SKILL.md | sort >"$tmp"
count="$(wc -l < "$tmp" | tr -d ' ')"

if [ "$count" -lt 10 ]; then
  printf '%s\n' 'verify pack: expected at least 10 skills'
  exit 1
fi

for path in \
  "$root/AGENTS.md" \
  "$root/adapters/codex/AGENTS.md" \
  "$root/adapters/claude/CLAUDE.md" \
  "$root/adapters/cursor/.cursor/rules/agentic-engineering.mdc" \
  "$root/adapters/generic/AGENTIC_ENGINEERING.md" \
  "$root/.claude-plugin/plugin.json" \
  "$root/.claude-plugin/hooks.json" \
  "$root/.claude-plugin/README.md" \
  "$root/docs/codex.md" \
  "$root/docs/claude.md" \
  "$root/docs/cursor.md" \
  "$root/docs/generic.md" \
  "$root/docs/audit-v0.2.md" \
  "$root/docs/architecture.md" \
  "$root/docs/release-checklist.md" \
  "$root/docs/troubleshooting.md" \
  "$root/ROADMAP.md" \
  "$root/templates/package-age/npm.npmrc" \
  "$root/templates/package-age/pnpm-workspace.yaml" \
  "$root/templates/package-age/bunfig.toml" \
  "$root/templates/package-age/yarnrc.yml" \
  "$root/templates/package-age/uv.toml" \
  "$root/templates/package-age/pip.conf" \
  "$root/templates/package-age/mise-config.toml" \
  "$root/scripts/package-age-lib.sh" \
  "$root/scripts/validate-repo.sh" \
  "$root/scripts/run-evals-smoke.sh" \
  "$root/hooks/claude/pretooluse-package-install-safety.sh" \
  "$root/hooks/claude/stop-verify-before-finish.sh" \
  "$root/hooks/claude/posttooluse-light-checks.sh" \
  "$root/hooks/claude/sessionstart-reminder.sh"; do
  if [ ! -s "$path" ]; then
    printf '%s\n' "verify pack: missing $path"
    exit 1
  fi
done

for path in "$root"/skills/*/SKILL.md; do
  for heading in "## When To Use" "## Workflow" "## Do" "## Don't" "## Expected Output" "## Verification Checklist" "## Failure Modes"; do
    if ! grep -q "^$heading" "$path"; then
      printf '%s\n' "verify pack: $path missing $heading"
      exit 1
    fi
  done
done

printf '%s\n' 'verify pack: ok'
