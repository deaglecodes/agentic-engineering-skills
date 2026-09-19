#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

section() {
  printf '\n%s\n' "== $1 =="
}

section "Shell syntax"
bash -n scripts/*.sh hooks/*.sh hooks/claude/*.sh
sh -n scripts/package-age-lib.sh hooks/*.sh

section "Optional shellcheck"
if [[ "${RUN_SHELLCHECK:-0}" == "1" ]] && command -v shellcheck >/dev/null 2>&1; then
  shellcheck scripts/*.sh hooks/*.sh hooks/claude/*.sh
else
  printf '%s\n' 'shellcheck skipped; set RUN_SHELLCHECK=1 to enable'
fi

section "JSON config"
jq empty .claude-plugin/plugin.json .claude-plugin/hooks.json examples/claude/settings.project.json examples/claude/settings.local.json

section "Pack structure"
./scripts/verify-pack.sh

section "Secret scan"
./scripts/secret-scan.sh .

section "Fixture tests"
./scripts/test-fixtures.sh

section "Python tool and installer tests"
python3 -B -m unittest discover -s tests -p 'test_*.py'

section "Eval smoke"
./scripts/run-evals-smoke.sh

section "Paired pilot grader checks (no model calls)"
if [ -f evals/paired-pilot/run.py ]; then
  python3 -B evals/paired-pilot/run.py --check
else
  printf '%s\n' 'pilot corpus not bundled in installed packs; grader checks skipped'
fi

section "Verification receipt demo (no model calls)"
if [ -f evals/verification-demo/run.py ]; then
  python3 -B evals/verification-demo/run.py
else
  printf '%s\n' 'demo not bundled in installed packs; skipped'
fi

section "Executable permissions"
bad_permissions="$(find . -path './.git' -prune -o -type f -perm -111 -print | grep -Ev '^\./(scripts|hooks)/.*\.sh$' || true)"
if [[ -n "$bad_permissions" ]]; then
  printf '%s\n' "$bad_permissions"
  printf '%s\n' 'Only scripts and hooks should be executable.' >&2
  exit 1
fi

printf '\n%s\n' 'validate repo: ok'
