#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
. "$ROOT/scripts/package-age-lib.sh"

payload="$(cat)"

if command -v jq >/dev/null 2>&1; then
  tool_name="$(printf '%s' "$payload" | jq -r '.tool_name // empty')"
  command_text="$(printf '%s' "$payload" | jq -r '.tool_input.command // empty')"
  cwd_value="$(printf '%s' "$payload" | jq -r '.cwd // .tool_input.cwd // empty')"
else
  tool_name=""
  command_text=""
  cwd_value=""
fi

[[ "$tool_name" == "Bash" ]] || exit 0
[[ -n "$command_text" ]] || exit 0

root_dir="${cwd_value:-$(pwd)}"

trim_quotes() {
  local value="$1"
  value="${value%\"}"
  value="${value#\"}"
  value="${value%\'}"
  value="${value#\'}"
  printf '%s\n' "$value"
}

resolve_cd() {
  local current="$1"
  local target="$2"

  target="$(trim_quotes "$target")"
  case "$target" in
    "") printf '%s\n' "$current" ;;
    /*) printf '%s\n' "$target" ;;
    *) printf '%s\n' "$current/$target" ;;
  esac
}

next_non_option() {
  local token
  shift
  for token in "$@"; do
    case "$token" in
      --*) continue ;;
      *) printf '%s\n' "$token"; return 0 ;;
    esac
  done
}

detect_manager_from_tokens() {
  local words=("$@")
  local first second third action

  while ((${#words[@]} > 0)); do
    first="${words[0]}"
    case "$first" in
      *=*)
        words=("${words[@]:1}")
        ;;
      env)
        words=("${words[@]:1}")
        while ((${#words[@]} > 0)) && [[ "${words[0]}" == *=* ]]; do
          words=("${words[@]:1}")
        done
        ;;
      command)
        words=("${words[@]:1}")
        [[ "${words[0]:-}" == "-p" ]] && words=("${words[@]:1}")
        ;;
      exec|time)
        words=("${words[@]:1}")
        ;;
      *)
        break
        ;;
    esac
  done

  ((${#words[@]} > 0)) || return 1
  first="${words[0]##*/}"
  second="${words[1]:-}"
  third="${words[2]:-}"

  case "$first" in
    python|python3)
      [[ "$second" == "-m" && "$third" == "pip" && "${words[3]:-}" == "install" ]] && { printf '%s\n' "pip"; return 0; }
      ;;
    npm)
      action="$(next_non_option npm "${words[@]:1}" || true)"
      [[ "$action" == "install" || "$action" == "i" || "$action" == "add" || "$action" == "ci" ]] && { printf '%s\n' "npm"; return 0; }
      ;;
    npx)
      printf '%s\n' "npx"
      return 0
      ;;
    pnpm|yarn|bun)
      action="$(next_non_option "$first" "${words[@]:1}" || true)"
      [[ "$action" == "install" || "$action" == "add" ]] && { printf '%s\n' "$first"; return 0; }
      ;;
    uv)
      [[ "$second" == "add" ]] && { printf '%s\n' "uv"; return 0; }
      [[ "$second" == "pip" && "$third" == "install" ]] && { printf '%s\n' "uv"; return 0; }
      ;;
    pip|pip3)
      [[ "$second" == "install" ]] && { printf '%s\n' "pip"; return 0; }
      ;;
    cargo)
      [[ "$second" == "add" || "$second" == "install" ]] && { printf '%s\n' "cargo"; return 0; }
      ;;
    go)
      [[ "$second" == "get" ]] && { printf '%s\n' "go"; return 0; }
      ;;
    composer)
      [[ "$second" == "require" ]] && { printf '%s\n' "composer"; return 0; }
      ;;
    gem)
      [[ "$second" == "install" ]] && { printf '%s\n' "gem"; return 0; }
      ;;
    bundle)
      [[ "$second" == "add" ]] && { printf '%s\n' "bundle"; return 0; }
      ;;
    brew)
      [[ "$second" == "install" ]] && { printf '%s\n' "brew"; return 0; }
      ;;
    mix)
      [[ "$second" == "deps.get" ]] && { printf '%s\n' "mix"; return 0; }
      ;;
  esac

  return 1
}

find_install_command() {
  local current_root="$1"
  local segment manager
  local words

  while IFS= read -r segment; do
    [[ -n "${segment//[[:space:]]/}" ]] || continue
    read -r -a words <<< "$segment"
    ((${#words[@]} > 0)) || continue

    if [[ "${words[0]}" == "cd" ]]; then
      current_root="$(resolve_cd "$current_root" "${words[1]:-}")"
      continue
    fi

    if manager="$(detect_manager_from_tokens "${words[@]}")"; then
      printf '%s\t%s\t%s\n' "$manager" "$current_root" "$segment"
      return 0
    fi
  done < <(printf '%s\n' "$command_text" | sed -E 's/(&&|;|\|\||\|)/\
/g')

  return 1
}

has_regex() {
  local pattern="$1"
  local text="$2"
  printf '%s\n' "$text" | grep -Eq "$pattern"
}

has_unsafe_age_override() {
  local manager="$1"
  local segment="$2"

  case "$manager" in
    npm|npx)
      if has_regex '(^|[[:space:]])--before(=|[[:space:]]|$)|(^|[[:space:]])NPM_CONFIG_BEFORE=|(^|[[:space:]])npm_config_before=' "$segment"; then
        return 0
      fi
      if has_regex '(^|[[:space:]])--min-release-age(=|[[:space:]])|(^|[[:space:]])NPM_CONFIG_MIN_RELEASE_AGE=|(^|[[:space:]])npm_config_min_release_age=' "$segment" &&
        ! has_regex '(^|[[:space:]])--min-release-age(=|[[:space:]]+)7([[:space:]]|$)|(^|[[:space:]])NPM_CONFIG_MIN_RELEASE_AGE=7([[:space:]]|$)|(^|[[:space:]])npm_config_min_release_age=7([[:space:]]|$)' "$segment"; then
        return 0
      fi
      ;;
    bun)
      if has_regex '(^|[[:space:]])--minimum-release-age(=|[[:space:]])' "$segment" &&
        ! has_regex '(^|[[:space:]])--minimum-release-age(=|[[:space:]]+)604800([[:space:]]|$)' "$segment"; then
        return 0
      fi
      ;;
    uv)
      if has_regex '(^|[[:space:]])--exclude-newer(=|[[:space:]])|(^|[[:space:]])UV_EXCLUDE_NEWER=' "$segment" &&
        ! has_regex '(^|[[:space:]])--exclude-newer(=|[[:space:]]+)P7D([[:space:]]|$)|(^|[[:space:]])UV_EXCLUDE_NEWER=P7D([[:space:]]|$)' "$segment"; then
        return 0
      fi
      ;;
    pip)
      if has_regex '(^|[[:space:]])--uploaded-prior-to(=|[[:space:]])|(^|[[:space:]])PIP_UPLOADED_PRIOR_TO=' "$segment" &&
        ! has_regex '(^|[[:space:]])--uploaded-prior-to(=|[[:space:]]+)P7D([[:space:]]|$)|(^|[[:space:]])PIP_UPLOADED_PRIOR_TO=P7D([[:space:]]|$)' "$segment"; then
        return 0
      fi
      ;;
  esac

  return 1
}

has_safe_inline_pip_gate() {
  local segment="$1"
  local root="$2"
  local pip_config_value pip_config_path

  package_pip_duration_ready >/dev/null || return 1

  if has_regex '(^|[[:space:]])--uploaded-prior-to(=|[[:space:]]+)P7D([[:space:]]|$)|(^|[[:space:]])PIP_UPLOADED_PRIOR_TO=P7D([[:space:]]|$)' "$segment"; then
    return 0
  fi

  pip_config_value="$(printf '%s\n' "$segment" | sed -nE 's/.*(^|[[:space:]])PIP_CONFIG_FILE=([^[:space:]]+).*/\2/p' | head -n 1)"
  [[ -n "$pip_config_value" ]] || return 1
  pip_config_value="$(trim_quotes "$pip_config_value")"
  pip_config_path="$(package_project_path "$root" "$pip_config_value")"
  package_file_has_line "$pip_config_path" '^[[:space:]]*uploaded-prior-to[[:space:]]*=[[:space:]]*P7D[[:space:]]*$'
}

install_info="$(find_install_command "$root_dir" || true)"
[[ -n "$install_info" ]] || exit 0

manager="${install_info%%$'\t'*}"
remaining="${install_info#*$'\t'}"
root_dir="${remaining%%$'\t'*}"
install_segment="${remaining#*$'\t'}"

if has_unsafe_age_override "$manager" "$install_segment"; then
  cat >&2 <<BLOCK
Package install blocked by Agentic Engineering Skills.

Manager: $manager
Reason: command includes a package-age override that could weaken the 7-day gate.
BLOCK
  exit 2
fi

if [[ "$manager" == "pip" ]] && has_safe_inline_pip_gate "$install_segment" "$root_dir"; then
  printf '%s\n' "package install allowed: inline pip upload-time gate is P7D" >&2
  exit 0
fi

if message="$(package_age_project_status "$manager" "$root_dir")"; then
  printf '%s\n' "package install allowed: $message" >&2
  exit 0
fi

project_message="$message"
if message="$(package_age_status "$manager")"; then
  printf '%s\n' "package install allowed: $message" >&2
  exit 0
fi

cat >&2 <<BLOCK
Package install blocked by Agentic Engineering Skills.

Manager: $manager
Project check: $project_message
User/runtime check: $message

Run a read-only audit:
  ./scripts/check-package-age-safety.sh --scope=all

For project-local setup:
  ./scripts/setup-package-age-safety.sh --mode=project-local --target .

For user-wide setup, use dry-run first:
  ./scripts/setup-package-age-safety.sh --mode=user-wide --dry-run
  ./scripts/setup-package-age-safety.sh --mode=user-wide --confirm-user-wide
BLOCK

exit 2
