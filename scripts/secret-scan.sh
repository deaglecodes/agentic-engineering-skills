#!/usr/bin/env sh
set -eu

root="${1:-.}"

if ! command -v rg >/dev/null 2>&1; then
  printf '%s\n' 'secret scan failed: rg not found'
  exit 1
fi
if ! rg --version >/dev/null 2>&1; then
  printf '%s\n' 'secret scan failed: rg is not runnable'
  exit 1
fi

pattern='(?i)(api[ _-]?key[[:space:]]*[=:]|auth[ _-]?token[[:space:]]*[=:]|access[ _-]?token[[:space:]]*[=:]|secret[[:space:]]*[=:]|password[[:space:]]*[=:]|token[[:space:]]*[=:]|authorization[[:space:]]*:[[:space:]]*bearer[[:space:]]+|BEGIN (RSA|OPENSSH|PRIVATE) KEY|npmAuthToken[[:space:]]*[=:]|_authToken[[:space:]]*[=:])'
tmp="$(mktemp "${TMPDIR:-/tmp}/agentic-secret-scan.XXXXXX")"
trap 'rm -f "$tmp"' EXIT

set +e
rg -l --hidden \
  --glob '!.git/**' \
  --glob '!node_modules/**' \
  --glob '!dist/**' \
  --glob '!build/**' \
  --glob '!coverage/**' \
  --glob '!*.lock' \
  "$pattern" "$root" >"$tmp" 2>/dev/null
rg_status=$?
set -e

if [ "$rg_status" -eq 0 ]; then
  printf '%s\n' 'secret scan: review these files before publishing'
  sed 's/^/- /' "$tmp"
  exit 1
fi
if [ "$rg_status" -ne 1 ]; then
  printf '%s\n' 'secret scan failed: rg could not complete'
  exit 1
fi

printf '%s\n' 'secret scan: ok'
