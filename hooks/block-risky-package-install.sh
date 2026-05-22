#!/usr/bin/env sh
set -eu

cmd="${1:-}"

version_ge() {
  have="$1"
  need="$2"
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

tool_output() {
  tool="$1"
  shift
  if command -v "$tool" >/dev/null 2>&1; then
    "$tool" "$@" 2>/dev/null || true
    return
  fi
  if command -v mise >/dev/null 2>&1; then
    mise exec -- "$tool" "$@" 2>/dev/null || true
    return
  fi
  if [ -x "$HOME/.local/bin/mise" ]; then
    "$HOME/.local/bin/mise" exec -- "$tool" "$@" 2>/dev/null || true
    return
  fi
}

toml_top_level_has() {
  path="$1"
  key="$2"
  expected="$3"
  [ -e "$path" ] || return 1
  awk -v key="$key" -v expected="$expected" '
    /^[[:space:]]*\[/ { exit 1 }
    $0 ~ "^[[:space:]]*" key "[[:space:]]*=" && index($0, expected) { found=1; exit 0 }
    END { exit found ? 0 : 1 }
  ' "$path"
}

bun_install_has_age() {
  path="$1"
  [ -e "$path" ] || return 1
  awk '
    /^[[:space:]]*\[/ {
      in_install=($0 ~ /^[[:space:]]*\[install\][[:space:]]*$/)
      next
    }
    in_install && /^[[:space:]]*minimumReleaseAge[[:space:]]*=[[:space:]]*604800([[:space:]]*(#.*)?)?$/ { found=1; exit 0 }
    END { exit found ? 0 : 1 }
  ' "$path"
}

require_npm_gate() {
  version="$(tool_output npm --version)"
  if [ -z "$version" ] || ! version_ge "$version" "11.10.0"; then
    printf '%s\n' 'blocked: npm must be 11.10.0 or newer for min-release-age'
    exit 1
  fi
  age="$(tool_output npm config get min-release-age)"
  if [ "$age" = "7" ] || { [ -e "$HOME/.npmrc" ] && grep -q '^min-release-age=7$' "$HOME/.npmrc"; }; then
    return
  fi
  printf '%s\n' 'blocked: npm min-release-age is not set to 7'
  exit 1
}

require_pnpm_gate() {
  age="$(tool_output pnpm config get minimumReleaseAge)"
  if [ "$age" = "10080" ]; then
    return
  fi
  printf '%s\n' 'blocked: pnpm minimumReleaseAge is not set to 10080'
  exit 1
}

require_yarn_gate() {
  age="$(tool_output yarn config get npmMinimalAgeGate)"
  if [ "$age" = "10080" ] || [ "$age" = "7d" ]; then
    return
  fi
  printf '%s\n' 'blocked: yarn npmMinimalAgeGate is not set to 7d'
  exit 1
}

require_bun_gate() {
  if bun_install_has_age "$HOME/.bunfig.toml"; then
    return
  fi
  printf '%s\n' 'blocked: bun minimumReleaseAge is not set to 604800'
  exit 1
}

require_uv_gate() {
  if toml_top_level_has "$HOME/.config/uv/uv.toml" "exclude-newer" '"P7D"'; then
    return
  fi
  printf '%s\n' 'blocked: uv exclude-newer is not set to P7D at top level'
  exit 1
}

require_pip_gate() {
  age="$(tool_output python -m pip config get install.uploaded-prior-to)"
  if [ "$age" = "P7D" ]; then
    return
  fi
  printf '%s\n' 'blocked: pip uploaded-prior-to is not set to P7D'
  exit 1
}

case "$cmd" in
  npm)
    require_npm_gate
    ;;
  pnpm)
    require_pnpm_gate
    ;;
  yarn)
    require_yarn_gate
    ;;
  bun)
    require_bun_gate
    ;;
  uv)
    require_uv_gate
    ;;
  pip|pip3|python)
    require_pip_gate
    ;;
  python3)
    require_pip_gate
    ;;
  npx)
    require_npm_gate
    ;;
  gem|bundle|mix|brew|cargo|go|composer)
    printf '%s\n' "blocked: $cmd has no native 7-day release-age gate in this pack"
    exit 1
    ;;
  "")
    printf '%s\n' 'blocked: package command is required'
    exit 1
    ;;
  *)
    printf '%s\n' "blocked: unsupported package command '$cmd'"
    exit 1
    ;;
esac

printf '%s\n' 'package command gate: ok'
