#!/usr/bin/env bash
set -euo pipefail

payload="$(cat)"

if command -v jq >/dev/null 2>&1; then
  tool_name="$(printf '%s' "$payload" | jq -r '.tool_name // empty')"
else
  tool_name=""
fi

case "$tool_name" in
  Edit|MultiEdit|Write|NotebookEdit)
    ;;
  *)
    exit 0
    ;;
esac

if git rev-parse --is-inside-work-tree >/dev/null 2>&1 && ! git diff --check >/dev/null 2>&1; then
  printf '%s\n' 'Agentic Engineering note: git diff --check found whitespace errors after the edit.' >&2
fi

exit 0
