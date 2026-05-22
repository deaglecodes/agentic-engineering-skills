#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
. "$SCRIPT_DIR/package-age-lib.sh"

status=0

ok() {
  printf '%s\n' "- $1: ok, $2"
}

warn() {
  printf '%s\n' "- $1: check, $2"
  status=1
}

missing() {
  printf '%s\n' "- $1: not found"
}

for tool in mise npm pnpm yarn bun uv pip; do
  if message="$(package_age_status "$tool")"; then
    ok "$tool" "$message"
  else
    code=$?
    if [[ "$code" -eq 2 ]]; then
      missing "$tool"
    else
      warn "$tool" "$message"
    fi
  fi
done

for tool in gem bundle mix brew cargo go composer; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf '%s\n' "- $tool: avoid for agent installs, no native 7-day age gate, $(package_unsupported_use "$tool")"
  fi
done

exit "$status"
