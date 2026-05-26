#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
. "$SCRIPT_DIR/package-age-lib.sh"

SCOPE="all"
TARGET="$(pwd)"
status=0

usage() {
  cat <<'USAGE'
Usage: scripts/check-package-age-safety.sh [--scope=all|project|user] [--target PATH]

Read-only audit for 7-day package release-age settings.

Scopes:
  all      Check project-local files and installed user/runtime tools.
  project  Check only project-local files under PATH.
  user     Check only installed user/runtime package-manager config.
USAGE
}

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --scope=all) SCOPE="all" ;;
    --scope=project) SCOPE="project" ;;
    --scope=user) SCOPE="user" ;;
    --target=*) TARGET="${1#--target=}" ;;
    --target)
      shift
      [[ "$#" -gt 0 ]] || { printf '%s\n' '--target requires a path' >&2; exit 2; }
      TARGET="$1"
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      printf '%s\n' "unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

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

check_user_tool() {
  local tool="$1"
  local code message
  if message="$(package_age_status "$tool")"; then
    ok "user/$tool" "$message"
    return
  fi
  code=$?
  if [[ "$code" -eq 2 ]]; then
    missing "user/$tool"
  else
    warn "user/$tool" "$message"
  fi
}

check_project_tool() {
  local tool="$1"
  local message
  if message="$(package_age_project_status "$tool" "$TARGET")"; then
    ok "project/$tool" "$message"
  else
    warn "project/$tool" "$message"
  fi
}

if [[ "$SCOPE" == "all" || "$SCOPE" == "project" ]]; then
  printf '%s\n' "Project-local package-age audit: $TARGET"
  for tool in mise npm pnpm yarn bun uv pip; do
    check_project_tool "$tool"
  done
fi

if [[ "$SCOPE" == "all" || "$SCOPE" == "user" ]]; then
  printf '%s\n' "User/runtime package-age audit:"
  for tool in mise npm pnpm yarn bun uv pip; do
    check_user_tool "$tool"
  done

  for tool in gem bundle mix brew cargo go composer; do
    if command -v "$tool" >/dev/null 2>&1; then
      printf '%s\n' "- user/$tool: avoid for agent installs, no native 7-day age gate, $(package_unsupported_use "$tool")"
    fi
  done
fi

exit "$status"
