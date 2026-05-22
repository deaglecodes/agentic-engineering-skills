#!/usr/bin/env bash
set -euo pipefail

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

version_ge() {
  local have="$1"
  local need="$2"
  awk -v have="$have" -v need="$need" '
    BEGIN {
      split(have, h, ".")
      split(need, n, ".")
      for (i = 1; i <= 3; i++) {
        hv = h[i] + 0
        nv = n[i] + 0
        if (hv > nv) exit 0
        if (hv < nv) exit 1
      }
      exit 0
    }
  '
}

toml_top_level_has() {
  local path="$1"
  local key="$2"
  local expected="$3"
  [[ -e "$path" ]] || return 1
  awk -v key="$key" -v expected="$expected" '
    /^[[:space:]]*\[/ { exit 1 }
    $0 ~ "^[[:space:]]*" key "[[:space:]]*=" && index($0, expected) { found=1; exit 0 }
    END { exit found ? 0 : 1 }
  ' "$path"
}

bun_install_has_age() {
  local path="$1"
  [[ -e "$path" ]] || return 1
  awk '
    /^[[:space:]]*\[/ {
      in_install=($0 ~ /^[[:space:]]*\[install\][[:space:]]*$/)
      next
    }
    in_install && /^[[:space:]]*minimumReleaseAge[[:space:]]*=[[:space:]]*604800([[:space:]]*(#.*)?)?$/ { found=1; exit 0 }
    END { exit found ? 0 : 1 }
  ' "$path"
}

MISE_BIN="${MISE_BIN:-}"
if [[ -z "$MISE_BIN" ]]; then
  if command -v mise >/dev/null 2>&1; then
    MISE_BIN="$(command -v mise)"
  elif [[ -x "$HOME/.local/bin/mise" ]]; then
    MISE_BIN="$HOME/.local/bin/mise"
  fi
fi

if [[ -n "$MISE_BIN" ]]; then
  mise_age="$("$MISE_BIN" settings get minimum_release_age 2>/dev/null || true)"
  [[ "$mise_age" == "7d" ]] && ok "mise" "minimum_release_age=7d" || warn "mise" "minimum_release_age is not 7d"
else
  missing "mise"
fi

if [[ -n "$MISE_BIN" ]]; then
  npm_version="$("$MISE_BIN" exec -- npm --version 2>/dev/null || true)"
else
  npm_version="$(npm --version 2>/dev/null || true)"
fi
if [[ -n "$npm_version" ]]; then
  if version_ge "$npm_version" "11.10.0"; then
    if [[ -n "$MISE_BIN" ]]; then
      npm_age="$("$MISE_BIN" exec -- npm config get min-release-age 2>/dev/null || true)"
    else
      npm_age="$(npm config get min-release-age 2>/dev/null || true)"
    fi
    if [[ "$npm_age" == "7" ]] || { [[ -e "$HOME/.npmrc" ]] && grep -q '^min-release-age=7$' "$HOME/.npmrc"; }; then
      ok "npm" "min-release-age=7"
    else
      warn "npm" "min-release-age is not 7"
    fi
  else
    warn "npm" "version $npm_version is older than 11.10.0"
  fi
else
  missing "npm"
fi

if [[ -n "$MISE_BIN" ]]; then
  pnpm_age="$("$MISE_BIN" exec -- pnpm config get minimumReleaseAge 2>/dev/null || true)"
else
  pnpm_age="$(pnpm config get minimumReleaseAge 2>/dev/null || true)"
fi
[[ "$pnpm_age" == "10080" ]] && ok "pnpm" "minimumReleaseAge=10080" || warn "pnpm" "minimumReleaseAge is not 10080"

if [[ -n "$MISE_BIN" ]]; then
  yarn_age="$("$MISE_BIN" exec -- yarn config get npmMinimalAgeGate 2>/dev/null || true)"
else
  yarn_age="$(yarn config get npmMinimalAgeGate 2>/dev/null || true)"
fi
[[ "$yarn_age" == "10080" || "$yarn_age" == "7d" ]] && ok "yarn" "npmMinimalAgeGate=7d" || warn "yarn" "npmMinimalAgeGate is not 7d"

if bun_install_has_age "$HOME/.bunfig.toml"; then
  ok "bun" "minimumReleaseAge=604800"
else
  warn "bun" "minimumReleaseAge is not 604800"
fi

if toml_top_level_has "$HOME/.config/uv/uv.toml" "exclude-newer" '"P7D"'; then
  ok "uv" 'exclude-newer=P7D'
else
  warn "uv" "exclude-newer is not P7D"
fi

if [[ -n "$MISE_BIN" ]]; then
  pip_age="$("$MISE_BIN" exec -- python -m pip config get install.uploaded-prior-to 2>/dev/null || true)"
else
  pip_age="$(python3 -m pip config get install.uploaded-prior-to 2>/dev/null || true)"
fi
[[ "$pip_age" == "P7D" ]] && ok "pip" "uploaded-prior-to=P7D" || warn "pip" "uploaded-prior-to is not P7D"

for tool in gem bundle mix brew cargo go composer; do
  if command -v "$tool" >/dev/null 2>&1; then
    case "$tool" in
      gem) use="Ruby packages" ;;
      bundle) use="Ruby app dependencies" ;;
      mix) use="Elixir and Erlang packages" ;;
      brew) use="macOS command-line apps" ;;
      cargo) use="Rust packages" ;;
      go) use="Go modules" ;;
      composer) use="PHP packages" ;;
    esac
    printf '%s\n' "- $tool: avoid for agent installs, no native 7-day age gate, $use"
  fi
done

exit "$status"
