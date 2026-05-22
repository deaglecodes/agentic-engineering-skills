#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/../scripts" && pwd)"
. "$SCRIPT_DIR/package-age-lib.sh"

cmd="${1:-}"

if ! message="$(package_age_status "$cmd")"; then
  printf '%s\n' "blocked: $message"
  exit 1
fi

printf '%s\n' 'package command gate: ok'
