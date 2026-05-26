#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/../scripts" && pwd)"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if git diff --check >/dev/null 2>&1; then
    printf '%s\n' 'diff whitespace check: ok'
  else
    printf '%s\n' 'diff whitespace check: failed'
    exit 1
  fi
else
  printf '%s\n' 'diff whitespace check: skipped, not a git repo'
fi

"$SCRIPT_DIR/secret-scan.sh" .
