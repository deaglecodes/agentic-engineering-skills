#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
PROMPT_DIR="$ROOT/evals/prompts"
status=0

fail() {
  printf '%s\n' "eval smoke: $1" >&2
  status=1
}

if [[ ! -d "$PROMPT_DIR" ]]; then
  fail "missing evals/prompts"
  exit "$status"
fi

count="$(find "$PROMPT_DIR" -type f -name '*.md' | wc -l | tr -d ' ')"
if [[ "$count" -lt 7 ]]; then
  fail "expected at least 7 eval prompt files, found $count"
fi

while IFS= read -r file; do
  grep -q '^## Prompt' "$file" || fail "$file missing ## Prompt"
  grep -q '^## Expected Behavior' "$file" || fail "$file missing ## Expected Behavior"
  grep -q '^## Pass Criteria' "$file" || fail "$file missing ## Pass Criteria"
done < <(find "$PROMPT_DIR" -type f -name '*.md' | sort)

if [[ "$status" -eq 0 ]]; then
  printf '%s\n' 'eval smoke: ok'
fi

exit "$status"
