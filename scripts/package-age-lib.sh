#!/usr/bin/env sh

PACKAGE_AGE_DAYS=7
PACKAGE_AGE_MINUTES=10080
PACKAGE_AGE_SECONDS=604800

package_version_ge() {
  have="$1"
  need="$2"
  awk -v have="$have" -v need="$need" '
    BEGIN {
      gsub(/[^0-9.].*$/, "", have)
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
  if [ -n "${MISE_BIN:-}" ] && [ -x "${MISE_BIN:-}" ]; then
    printf '%s\n' "$MISE_BIN"
    return 0
  fi
  if command -v mise >/dev/null 2>&1; then
    command -v mise
    return 0
  fi
  if [ -x "${HOME:-}/.local/bin/mise" ]; then
    printf '%s\n' "$HOME/.local/bin/mise"
    return 0
  fi
  return 1
}

package_tool_output() {
  tool="$1"
  shift
  output=""

  if [ -n "${MISE_BIN:-}" ] && [ -x "${MISE_BIN:-}" ]; then
    output="$("$MISE_BIN" exec -- "$tool" "$@" 2>/dev/null || true)"
    if [ -n "$output" ]; then
      printf '%s\n' "$output"
      return 0
    fi
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

package_file_has_line() {
  path="$1"
  pattern="$2"
  [ -e "$path" ] || return 1
  grep -Eq "$pattern" "$path"
}

package_toml_top_level_has() {
  path="$1"
  key="$2"
  expected="$3"
  [ -e "$path" ] || return 1
  awk -v key="$key" -v expected="$expected" '
    BEGIN { in_top=1 }
    /^[[:space:]]*\[/ { in_top=0 }
    in_top != 0 && $0 ~ "^[[:space:]]*" key "[[:space:]]*=" && index($0, expected) { found=1 }
    END { exit found ? 0 : 1 }
  ' "$path"
}

package_bun_install_has_age() {
  path="$1"
  [ -e "$path" ] || return 1
  awk -v seconds="$PACKAGE_AGE_SECONDS" '
    /^[[:space:]]*\[/ {
      in_install=($0 ~ /^[[:space:]]*\[install\][[:space:]]*$/)
      next
    }
    in_install && $0 ~ "^[[:space:]]*minimumReleaseAge[[:space:]]*=[[:space:]]*" seconds "([[:space:]]*(#.*)?)?$" {
      found=1
    }
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

package_pip_version() {
  version="$(package_tool_output python -m pip --version | awk '{print $2}')"
  [ -n "$version" ] || version="$(package_tool_output python3 -m pip --version | awk '{print $2}')"
  [ -n "$version" ] || version="$(package_tool_output pip --version | awk '{print $2}')"
  [ -n "$version" ] || version="$(package_tool_output pip3 --version | awk '{print $2}')"
  printf '%s\n' "$version"
}

package_project_path() {
  root="$1"
  path="$2"

  case "$path" in
    "") return 1 ;;
    /*) printf '%s\n' "$path" ;;
    *) printf '%s\n' "$root/$path" ;;
  esac
}

package_pip_duration_ready() {
  pip_version="$(package_pip_version)"
  [ -n "$pip_version" ] || { printf '%s\n' 'pip not found'; return 2; }
  if ! package_version_ge "$pip_version" "26.1"; then
    printf '%s\n' "pip $pip_version may not support duration upload filters"
    return 1
  fi
}

package_npm_env_status() {
  npm_before="${npm_config_before:-${NPM_CONFIG_BEFORE:-}}"
  npm_age="${npm_config_min_release_age:-${NPM_CONFIG_MIN_RELEASE_AGE:-}}"

  if [ -n "$npm_before" ]; then
    printf '%s\n' 'npm before env override is set'
    return 1
  fi

  if [ -n "$npm_age" ]; then
    if [ "$npm_age" = "7" ]; then
      printf '%s\n' 'npm env min-release-age=7'
      return 0
    fi
    printf '%s\n' "npm env min-release-age is $npm_age"
    return 1
  fi

  printf '%s\n' 'npm env has no age override'
  return 2
}

package_age_project_status() {
  tool="$1"
  root="${2:-.}"

  case "$tool" in
    mise)
      if package_file_has_line "$root/.mise.toml" '^[[:space:]]*minimum_release_age[[:space:]]*=[[:space:]]*"7d"'; then
        printf '%s\n' 'project .mise.toml has minimum_release_age=7d'
        return 0
      fi
      printf '%s\n' 'project .mise.toml does not set minimum_release_age=7d'
      return 1
      ;;
    npm|npx)
      version="$(package_tool_output npm --version)"
      if [ -n "$version" ] && ! package_version_ge "$version" "11.10.0"; then
        printf '%s\n' "npm $version is older than 11.10.0"
        return 1
      fi
      npm_env_code=0
      npm_env_message="$(package_npm_env_status)" || npm_env_code=$?
      case "$npm_env_code" in
        0)
          printf '%s\n' "$npm_env_message"
          return 0
          ;;
        1)
          printf '%s\n' "$npm_env_message"
          return 1
          ;;
      esac
      if package_file_has_line "$root/.npmrc" '^[[:space:]]*min-release-age[[:space:]]*=[[:space:]]*7[[:space:]]*$'; then
        printf '%s\n' 'project .npmrc has min-release-age=7'
        return 0
      fi
      printf '%s\n' 'project .npmrc does not set min-release-age=7'
      return 1
      ;;
    pnpm)
      if package_file_has_line "$root/pnpm-workspace.yaml" '^[[:space:]]*minimumReleaseAge[[:space:]]*:[[:space:]]*10080[[:space:]]*$' ||
        package_file_has_line "$root/.npmrc" '^[[:space:]]*minimum-release-age[[:space:]]*=[[:space:]]*10080[[:space:]]*$'; then
        printf '%s\n' 'project pnpm age gate is 10080 minutes'
        return 0
      fi
      printf '%s\n' 'project pnpm age gate is not 10080 minutes'
      return 1
      ;;
    yarn)
      if package_file_has_line "$root/.yarnrc.yml" '^[[:space:]]*npmMinimalAgeGate[[:space:]]*:[[:space:]]*"?7d"?[[:space:]]*$' ||
        package_file_has_line "$root/.yarnrc.yml" '^[[:space:]]*npmMinimalAgeGate[[:space:]]*:[[:space:]]*10080[[:space:]]*$'; then
        printf '%s\n' 'project .yarnrc.yml has npmMinimalAgeGate=7d'
        return 0
      fi
      printf '%s\n' 'project .yarnrc.yml does not set npmMinimalAgeGate=7d'
      return 1
      ;;
    bun)
      if package_bun_install_has_age "$root/bunfig.toml"; then
        printf '%s\n' 'project bunfig.toml has minimumReleaseAge=604800'
        return 0
      fi
      printf '%s\n' 'project bunfig.toml does not set minimumReleaseAge=604800'
      return 1
      ;;
    uv)
      if package_toml_top_level_has "$root/uv.toml" "exclude-newer" '"P7D"'; then
        printf '%s\n' 'project uv.toml has exclude-newer=P7D'
        return 0
      fi
      printf '%s\n' 'project uv.toml does not set top-level exclude-newer=P7D'
      return 1
      ;;
    pip|pip3|python|python3)
      pip_code=0
      pip_message="$(package_pip_duration_ready)" || pip_code=$?
      if [ "$pip_code" -ne 0 ]; then
        printf '%s\n' "$pip_message"
        return "$pip_code"
      fi

      if [ "${PIP_UPLOADED_PRIOR_TO:-}" = "P7D" ]; then
        printf '%s\n' 'PIP_UPLOADED_PRIOR_TO=P7D'
        return 0
      fi

      pip_config_file="${PIP_CONFIG_FILE:-}"
      if [ -n "$pip_config_file" ]; then
        pip_config_path="$(package_project_path "$root" "$pip_config_file")"
        if package_file_has_line "$pip_config_path" '^[[:space:]]*uploaded-prior-to[[:space:]]*=[[:space:]]*P7D[[:space:]]*$'; then
          printf '%s\n' "active pip config has uploaded-prior-to=P7D"
          return 0
        fi
        printf '%s\n' "active pip config does not set uploaded-prior-to=P7D"
        return 1
      fi

      if package_file_has_line "$root/.agentic-engineering/package-safety/pip.conf" '^[[:space:]]*uploaded-prior-to[[:space:]]*=[[:space:]]*P7D[[:space:]]*$'; then
        printf '%s\n' 'project pip template exists but is not active; set PIP_CONFIG_FILE=.agentic-engineering/package-safety/pip.conf'
        return 1
      fi

      printf '%s\n' 'pip has no active project config in this pack'
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
        printf '%s\n' "npm $version is older than 11.10.0"
        return 1
      fi
      npm_env_code=0
      npm_env_message="$(package_npm_env_status)" || npm_env_code=$?
      case "$npm_env_code" in
        0)
          printf '%s\n' "$npm_env_message"
          return 0
          ;;
        1)
          printf '%s\n' "$npm_env_message"
          return 1
          ;;
      esac
      age="$(package_tool_output npm config get min-release-age)"
      [ "$age" = "7" ] && { printf '%s\n' 'min-release-age=7'; return 0; }
      if package_file_has_line "$HOME/.npmrc" '^[[:space:]]*min-release-age[[:space:]]*=[[:space:]]*7[[:space:]]*$'; then
        printf '%s\n' 'user .npmrc has min-release-age=7'
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
      if [ "$age" = "10080" ] || [ "$age" = "7d" ] || [ "$age" = "\"7d\"" ]; then
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
      pip_version="$(package_pip_version)"
      [ -n "$pip_version" ] || { printf '%s\n' 'not found'; return 2; }
      if ! package_version_ge "$pip_version" "26.1"; then
        printf '%s\n' "pip $pip_version may not support duration upload filters"
        return 1
      fi
      [ "${PIP_UPLOADED_PRIOR_TO:-}" = "P7D" ] && { printf '%s\n' 'PIP_UPLOADED_PRIOR_TO=P7D'; return 0; }
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
    *) printf '%s\n' 'unknown ecosystem' ;;
  esac
}
