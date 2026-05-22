#!/usr/bin/env sh
set -eu

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

if command -v rg >/dev/null 2>&1; then
  if ! rg --version >/dev/null 2>&1; then
    printf '%s\n' 'secret pattern check: failed, rg is not runnable'
    exit 1
  fi
  set +e
  rg -n --hidden --glob '!node_modules/**' --glob '!.git/**' --glob '!*.lock' '(?i)(api[ _-]?key[[:space:]]*[=:]|secret[[:space:]]*[=:]|token[[:space:]]*[=:]|password[[:space:]]*[=:]|authorization[[:space:]]*:[[:space:]]*bearer[[:space:]]+|BEGIN (RSA|OPENSSH|PRIVATE) KEY)' . >/dev/null 2>&1
  rg_status=$?
  set -e
  if [ "$rg_status" -eq 0 ]; then
    printf '%s\n' 'secret pattern check: review needed'
    exit 1
  fi
  if [ "$rg_status" -ne 1 ]; then
    printf '%s\n' 'secret pattern check: failed, rg could not complete'
    exit 1
  fi
  printf '%s\n' 'secret pattern check: ok'
else
  printf '%s\n' 'secret pattern check: failed, rg missing'
  exit 1
fi
