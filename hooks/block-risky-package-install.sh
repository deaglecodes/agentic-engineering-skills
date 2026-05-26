#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/../scripts" && pwd)"
. "$SCRIPT_DIR/package-age-lib.sh"

cmd="${1:-}"
root="${2:-$(pwd)}"

if message="$(package_age_project_status "$cmd" "$root")"; then
  printf '%s\n' "package command gate: ok, $message"
  exit 0
fi

project_message="$message"

if message="$(package_age_status "$cmd")"; then
  printf '%s\n' "package command gate: ok, $message"
  exit 0
fi

printf '%s\n' "blocked: $project_message; $message"
exit 1
