#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
. "$SCRIPT_DIR/package-age-lib.sh"

MODE="project-local"
TARGET="$(pwd)"
DRY_RUN=0
NO_BACKUP=0
CONFIRM_USER_WIDE=0
RESTORE_DIR=""
TRACK_CREATED=0

usage() {
  cat <<'USAGE'
Usage:
  scripts/setup-package-age-safety.sh [--mode=project-local] [--target PATH] [--dry-run]
  scripts/setup-package-age-safety.sh --mode=user-wide --confirm-user-wide [--dry-run] [--no-backup]
  scripts/setup-package-age-safety.sh --restore BACKUP_DIR

Safe modes:
  project-local  Writes only project files under PATH. This is the default.
                 It does not back up existing package-manager config, to avoid copying private tokens.
  user-wide      Writes user package-manager config under HOME. Requires --confirm-user-wide.
  restore        Restores files from a backup directory created by user-wide setup.

The policy is a 7-day release-age delay where the package manager supports one.
USAGE
}

log() {
  printf '%s\n' "$*"
}

die() {
  printf '%s\n' "error: $*" >&2
  exit 1
}

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --mode=project-local) MODE="project-local" ;;
    --mode=user-wide) MODE="user-wide" ;;
    --mode)
      shift
      [[ "$#" -gt 0 ]] || die "--mode requires project-local or user-wide"
      MODE="$1"
      ;;
    --target=*) TARGET="${1#--target=}" ;;
    --target)
      shift
      [[ "$#" -gt 0 ]] || die "--target requires a path"
      TARGET="$1"
      ;;
    --dry-run) DRY_RUN=1 ;;
    --no-backup) NO_BACKUP=1 ;;
    --confirm-user-wide) CONFIRM_USER_WIDE=1 ;;
    --restore=*) RESTORE_DIR="${1#--restore=}" ;;
    --restore)
      shift
      [[ "$#" -gt 0 ]] || die "--restore requires a backup directory"
      RESTORE_DIR="$1"
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      die "unknown option: $1"
      ;;
  esac
  shift
done

run() {
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'would run:'
    printf ' %q' "$@"
    printf '\n'
  else
    "$@"
  fi
}

run_package_tool() {
  local tool="$1"
  local mise_bin
  shift

  if command -v "$tool" >/dev/null 2>&1; then
    run "$tool" "$@"
    return
  fi

  mise_bin="$(package_find_mise_bin 2>/dev/null || true)"
  if [[ -n "$mise_bin" ]]; then
    run "$mise_bin" exec -- "$tool" "$@"
    return
  fi

  return 127
}

detect_pip_command() {
  local candidate version
  local -a parts

  for candidate in "python -m pip" "python3 -m pip" "pip" "pip3"; do
    read -r -a parts <<< "$candidate"
    version="$(package_tool_output "${parts[@]}" --version | awk '{print $2}')"
    if [[ -n "$version" ]]; then
      printf '%s\t%s\n' "$version" "$candidate"
      return 0
    fi
  done
}

ensure_parent() {
  local path="$1"
  if [[ "$DRY_RUN" == "1" ]]; then
    log "would create directory: $(dirname "$path")"
  else
    mkdir -p "$(dirname "$path")"
  fi
}

USER_BACKUP_ROOT="${HOME:-}/.cache/agentic-engineering/backups/$(date +%Y%m%d%H%M%S)"
ACTIVE_BACKUP_ROOT=""

backup_file() {
  local path="$1"
  local backup_root="$2"
  local backup_name

  [[ -n "$backup_root" ]] || return 0
  [[ "$NO_BACKUP" == "1" ]] && return

  if [[ ! -e "$path" && "$TRACK_CREATED" != "1" ]]; then
    return
  fi

  if [[ "$DRY_RUN" == "1" ]]; then
    if [[ -e "$path" ]]; then
      log "would make a private backup of: $path"
    else
      log "would remember to remove created file on restore: $path"
    fi
    return
  fi

  ACTIVE_BACKUP_ROOT="$backup_root"
  mkdir -p "$backup_root"
  chmod 700 "$backup_root" 2>/dev/null || true

  if [[ -e "$path" ]]; then
    backup_name="$(printf '%s' "$path" | sed 's#^/##; s#[/:]#_#g')"
    cp "$path" "$backup_root/$backup_name"
    chmod 600 "$backup_root/$backup_name" 2>/dev/null || true
  else
    backup_name="__created__"
  fi

  printf '%s\t%s\n' "$backup_name" "$path" >> "$backup_root/manifest.tsv"
  chmod 600 "$backup_root/manifest.tsv" 2>/dev/null || true
}

write_file() {
  local path="$1"
  local backup_root="$2"
  local content="$3"

  ensure_parent "$path"
  backup_file "$path" "$backup_root"
  if [[ "$DRY_RUN" == "1" ]]; then
    log "would write: $path"
    return
  fi
  printf '%s\n' "$content" > "$path"
}

upsert_line() {
  local path="$1"
  local key="$2"
  local line="$3"
  local backup_root="$4"
  local tmp

  ensure_parent "$path"
  backup_file "$path" "$backup_root"
  if [[ "$DRY_RUN" == "1" ]]; then
    log "would set $key in $path"
    return
  fi

  touch "$path"
  tmp="$(mktemp)"
  if grep -qE "^[[:space:]]*$key[[:space:]]*[:=]" "$path"; then
    awk -v key="$key" -v line="$line" '
      $0 ~ "^[[:space:]]*" key "[[:space:]]*[:=]" { print line; next }
      { print }
    ' "$path" > "$tmp"
  else
    cp "$path" "$tmp"
    printf '%s\n' "$line" >> "$tmp"
  fi
  mv "$tmp" "$path"
}

upsert_top_level_toml() {
  local path="$1"
  local key="$2"
  local line="$3"
  local backup_root="$4"
  local tmp

  ensure_parent "$path"
  backup_file "$path" "$backup_root"
  if [[ "$DRY_RUN" == "1" ]]; then
    log "would set top-level $key in $path"
    return
  fi

  touch "$path"
  tmp="$(mktemp)"
  awk -v key="$key" -v line="$line" '
    BEGIN { in_top=1; wrote=0 }
    /^[[:space:]]*\[/ {
      if (in_top && !wrote) {
        print line
        wrote=1
      }
      in_top=0
      print
      next
    }
    in_top && $0 ~ "^[[:space:]]*" key "[[:space:]]*=" {
      if (!wrote) {
        print line
        wrote=1
      }
      next
    }
    { print }
    END {
      if (!wrote) print line
    }
  ' "$path" > "$tmp"
  mv "$tmp" "$path"
}

ensure_bunfig() {
  local path="$1"
  local backup_root="$2"
  local tmp

  ensure_parent "$path"
  backup_file "$path" "$backup_root"
  if [[ "$DRY_RUN" == "1" ]]; then
    log "would set minimumReleaseAge in $path"
    return
  fi

  if [[ ! -e "$path" ]]; then
    printf '[install]\nminimumReleaseAge = 604800\n' > "$path"
    return
  fi

  tmp="$(mktemp)"
  awk '
    BEGIN { in_install=0; saw_install=0; wrote=0 }
    /^[[:space:]]*\[/ {
      if (in_install && !wrote) {
        print "minimumReleaseAge = 604800"
        wrote=1
      }
      in_install=($0 ~ /^[[:space:]]*\[install\][[:space:]]*$/)
      if (in_install) saw_install=1
      print
      next
    }
    in_install && /^[[:space:]]*minimumReleaseAge[[:space:]]*=/ {
      if (!wrote) {
        print "minimumReleaseAge = 604800"
        wrote=1
      }
      next
    }
    { print }
    END {
      if (saw_install && in_install && !wrote) print "minimumReleaseAge = 604800"
      if (!saw_install) print "\n[install]\nminimumReleaseAge = 604800"
    }
  ' "$path" > "$tmp"
  mv "$tmp" "$path"
}

ensure_mise_settings() {
  local path="$1"
  local backup_root="$2"
  local tmp

  ensure_parent "$path"
  backup_file "$path" "$backup_root"
  if [[ "$DRY_RUN" == "1" ]]; then
    log "would set minimum_release_age in $path"
    return
  fi

  if [[ ! -e "$path" ]]; then
    printf '[settings]\nminimum_release_age = "7d"\n' > "$path"
    return
  fi

  tmp="$(mktemp)"
  awk '
    BEGIN { in_settings=0; saw_settings=0; wrote=0 }
    /^[[:space:]]*\[/ {
      if (in_settings && !wrote) {
        print "minimum_release_age = \"7d\""
        wrote=1
      }
      in_settings=($0 ~ /^[[:space:]]*\[settings\][[:space:]]*$/)
      if (in_settings) saw_settings=1
      print
      next
    }
    in_settings && /^[[:space:]]*minimum_release_age[[:space:]]*=/ {
      if (!wrote) {
        print "minimum_release_age = \"7d\""
        wrote=1
      }
      next
    }
    { print }
    END {
      if (saw_settings && in_settings && !wrote) print "minimum_release_age = \"7d\""
      if (!saw_settings) print "\n[settings]\nminimum_release_age = \"7d\""
    }
  ' "$path" > "$tmp"
  mv "$tmp" "$path"
}

restore_backup() {
  local backup_dir="$1"
  local manifest="$backup_dir/manifest.tsv"
  local backup_name original

  [[ -f "$manifest" ]] || die "backup manifest not found: $manifest"
  while IFS="$(printf '\t')" read -r backup_name original; do
    [[ -n "$backup_name" && -n "$original" ]] || continue
    if [[ "$DRY_RUN" == "1" ]]; then
      log "would restore: $original"
    elif [[ "$backup_name" == "__created__" ]]; then
      rm -f "$original"
    else
      mkdir -p "$(dirname "$original")"
      cp "$backup_dir/$backup_name" "$original"
      chmod 600 "$original" 2>/dev/null || true
    fi
  done < "$manifest"
  log "restore complete: $backup_dir"
}

setup_project_local() {
  local target="$1"
  local backup_root=""

  log "Setting project-local package-age files under: $target"
  upsert_line "$target/.npmrc" "min-release-age" "min-release-age=7" "$backup_root"
  upsert_line "$target/pnpm-workspace.yaml" "minimumReleaseAge" "minimumReleaseAge: 10080" "$backup_root"
  upsert_line "$target/.yarnrc.yml" "npmMinimalAgeGate" 'npmMinimalAgeGate: "7d"' "$backup_root"
  ensure_bunfig "$target/bunfig.toml" "$backup_root"
  upsert_top_level_toml "$target/uv.toml" "exclude-newer" 'exclude-newer = "P7D"' "$backup_root"
  ensure_mise_settings "$target/.mise.toml" "$backup_root"
  write_file "$target/.agentic-engineering/package-safety/pip.conf" "$backup_root" "$(sed -n '1,120p' "$ROOT/templates/package-age/pip.conf")"

  log "Project-local setup complete."
  log "Project-local mode does not back up existing package-manager config, to avoid copying private registry tokens."
  log "Note: pip does not auto-read project pip.conf; use PIP_CONFIG_FILE=.agentic-engineering/package-safety/pip.conf for pip installs."
}

setup_user_wide() {
  local backup_root="$USER_BACKUP_ROOT"
  local npm_version pip_version pip_command pip_info mise_bin
  local -a pip_parts

  [[ "$CONFIRM_USER_WIDE" == "1" || "$DRY_RUN" == "1" ]] || die "user-wide mode requires --confirm-user-wide"
  TRACK_CREATED=1

  log "Setting user-wide package-age config under HOME. No package tools will be installed."

  mise_bin="$(package_find_mise_bin 2>/dev/null || true)"
  if [[ -n "$mise_bin" ]]; then
    log "Setting mise 7-day tool delay"
    run "$mise_bin" settings set minimum_release_age 7d
  else
    log "mise not found; skipping mise setting"
  fi

  npm_version="$(package_tool_output npm --version)"
  if [[ -n "$npm_version" ]]; then
    if package_version_ge "$npm_version" "11.10.0"; then
      log "Setting npm 7-day package delay"
      backup_file "$HOME/.npmrc" "$backup_root"
      run npm config set min-release-age 7 --location=user
    else
      log "skip npm: npm $npm_version is older than 11.10.0"
    fi
  else
    log "npm not found; skipping npm"
  fi

  if command -v pnpm >/dev/null 2>&1; then
    log "Setting pnpm 7-day package delay"
    backup_file "$HOME/.config/pnpm/config.yaml" "$backup_root"
    run pnpm config set --global minimumReleaseAge 10080
  else
    log "pnpm not found; skipping pnpm"
  fi

  if command -v yarn >/dev/null 2>&1; then
    log "Setting Yarn 7-day package delay"
    backup_file "$HOME/.yarnrc.yml" "$backup_root"
    run yarn config set -H npmMinimalAgeGate 7d
  else
    log "yarn not found; skipping yarn"
  fi

  if command -v bun >/dev/null 2>&1; then
    ensure_bunfig "$HOME/.bunfig.toml" "$backup_root"
  else
    log "bun not found; skipping bun"
  fi

  if command -v uv >/dev/null 2>&1; then
    upsert_top_level_toml "$HOME/.config/uv/uv.toml" "exclude-newer" 'exclude-newer = "P7D"' "$backup_root"
  else
    log "uv not found; skipping uv"
  fi

  pip_info="$(detect_pip_command || true)"
  if [[ -n "$pip_info" ]]; then
    pip_version="${pip_info%%$'\t'*}"
    pip_command="${pip_info#*$'\t'}"
  else
    pip_version=""
    pip_command=""
  fi

  if [[ -n "$pip_version" ]] && package_version_ge "$pip_version" "26.1"; then
    log "Setting pip 7-day upload-time delay"
    backup_file "$HOME/.config/pip/pip.conf" "$backup_root"
    read -r -a pip_parts <<< "$pip_command"
    run_package_tool "${pip_parts[@]}" config --user set install.uploaded-prior-to P7D
  elif [[ -n "$pip_version" ]]; then
    log "skip pip: pip $pip_version may not support duration upload filters"
  else
    log "pip not found; skipping pip"
  fi

  if [[ "$DRY_RUN" == "0" && -n "$ACTIVE_BACKUP_ROOT" ]]; then
    log "Backups written under: $ACTIVE_BACKUP_ROOT"
    log "Restore with: scripts/setup-package-age-safety.sh --restore=$ACTIVE_BACKUP_ROOT"
  fi
}

if [[ -n "$RESTORE_DIR" ]]; then
  restore_backup "$RESTORE_DIR"
  exit 0
fi

case "$MODE" in
  project-local)
    setup_project_local "$TARGET"
    ;;
  user-wide)
    setup_user_wide
    ;;
  *)
    die "unknown mode: $MODE"
    ;;
esac
