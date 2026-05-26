#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"

if "$ROOT/hooks/verify-before-finish.sh" >/tmp/agentic-claude-stop-check.out 2>&1; then
  cat /tmp/agentic-claude-stop-check.out >&2
  rm -f /tmp/agentic-claude-stop-check.out
  exit 0
fi

cat /tmp/agentic-claude-stop-check.out >&2
rm -f /tmp/agentic-claude-stop-check.out
cat >&2 <<'BLOCK'

Stop blocked: verification-before-finish did not pass.
Fix the reported issue or explain why the check cannot apply before finishing.
BLOCK
exit 2
