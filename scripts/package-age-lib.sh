#!/usr/bin/env sh

package_version_ge() {
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

package_find_mise_bin() {
  if [ -n "${MISE_BIN:-}" ]; then
    printf '%s\n' "$MISE_BIN"
    return 0
  fi
  if command -v mise >/dev/null 2>&1; then
    command -v mise
    return 0
  fi
  if [ -x "$HOME/.local/bin/mise" ]; then
    printf '%s\n' "$HOME/.local/bin/mise"
    return 0
  fi
  return 1
}

package_tool_output() {
  tool="$1"
  shift
  if [ -n "${MISE_BIN:-}" ]; then
    "$MISE_BIN" exec -- "$tool" "$@" 2>/dev/null || true
    return 0
  fi
  if command -v "$tool" >/dev/null 2>&1; then
    "$tool" "$@" 2>/dev/null || true
    return 0
  fi
  mise_bin="$(package_find_mise_bin 2>/dev/null || true)"
  if [ -n "$mise_bin" ]; then
    "$mise_bin" exec -- "$tool" "$@" 2>/dev/null || true
  fi
}

package_toml_top_level_has() {
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

package_bun_install_has_age() {
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

package_pip_age() {
  age="$(package_tool_output python -m pip config get install.uploaded-prior-to)"
  [ -n "$age" ] || age="$(package_tool_output python3 -m pip config get install.uploaded-prior-to)"
  [ -n "$age" ] || age="$(package_tool_output pip config get install.uploaded-prior-to)"
  [ -n "$age" ] || age="$(package_tool_output pip3 config get install.uploaded-prior-to)"
  printf '%s\n' "$age"
}

package_age_status() {
  tool="$1"
  case "$tool" in
    mise)
      mise_bin="$(package_find_mise_bin 2>/dev/null || true)"
      [ -n "$mise_bin" ] || { printf '%s\n' 'not found'; return 2; }
      age="$("$mise_bin" settings get minimum_release_age 2>/dev/null || true)"
      [ "$age" = "7d" ] && { printf '%s\n' 'minimum_release_age=7d'; return 0; }
      printf '%s\n' 'minimum_release_age is not 7d'
      return 1
      ;;
    npm|npx)
      version="$(package_tool_output npm --version)"
      [ -n "$version" ] || { printf '%s\n' 'not found'; return 2; }
      if ! package_version_ge "$version" "11.10.0"; then
        printf '%s\n' "version $version is older than 11.10.0"
        return 1
      fi
      age="$(package_tool_output npm config get min-release-age)"
      if [ "$age" = "7" ] || { [ -e "$HOME/.npmrc" ] && grep -q '^min-release-age=7$' "$HOME/.npmrc"; }; then
        printf '%s\n' 'min-release-age=7'
        return 0
      fi
      printf '%s\n' 'min-release-age is not 7'
      return 1
      ;;
    pnpm)
      age="$(package_tool_output pnpm config get minimumReleaseAge)"
      [ "$age" = "10080" ] && { printf '%s\n' 'minimumReleaseAge=10080'; return 0; }
      printf '%s\n' 'minimumReleaseAge is not 10080'
      return 1
      ;;
    yarn)
      age="$(package_tool_output yarn config get npmMinimalAgeGate)"
      if [ "$age" = "10080" ] || [ "$age" = "7d" ]; then
        printf '%s\n' 'npmMinimalAgeGate=7d'
        return 0
      fi
      printf '%s\n' 'npmMinimalAgeGate is not 7d'
      return 1
      ;;
    bun)
      if package_bun_install_has_age "$HOME/.bunfig.toml"; then
        printf '%s\n' 'minimumReleaseAge=604800'
        return 0
      fi
      printf '%s\n' 'minimumReleaseAge is not 604800'
      return 1
      ;;
    uv)
      if package_toml_top_level_has "$HOME/.config/uv/uv.toml" "exclude-newer" '"P7D"'; then
        printf '%s\n' 'exclude-newer=P7D'
        return 0
      fi
      printf '%s\n' 'exclude-newer is not P7D at top level'
      return 1
      ;;
    pip|pip3|python|python3)
      age="$(package_pip_age)"
      [ "$age" = "P7D" ] && { printf '%s\n' 'uploaded-prior-to=P7D'; return 0; }
      printf '%s\n' 'uploaded-prior-to is not P7D'
      return 1
      ;;
    gem|bundle|mix|brew|cargo|go|composer)
      printf '%s\n' "no native 7-day release-age gate, $(package_unsupported_use "$tool")"
      return 4
      ;;
    "")
      printf '%s\n' 'package command is required'
      return 5
      ;;
    *)
      printf '%s\n' "unsupported package command '$tool'"
      return 5
      ;;
  esac
}

package_unsupported_use() {
  case "$1" in
    gem) printf '%s\n' 'Ruby packages' ;;
    bundle) printf '%s\n' 'Ruby app dependencies' ;;
    mix) printf '%s\n' 'Elixir and Erlang packages' ;;
    brew) printf '%s\n' 'macOS command-line apps' ;;
    cargo) printf '%s\n' 'Rust packages' ;;
    go) printf '%s\n' 'Go modules' ;;
    composer) printf '%s\n' 'PHP packages' ;;
  esac
}
