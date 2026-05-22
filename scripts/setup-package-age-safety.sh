#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=0
NO_BACKUP=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --no-backup) NO_BACKUP=1 ;;
    *)
      printf '%s\n' "unknown option: $arg"
      exit 1
      ;;
  esac
done

log() {
  printf '%s\n' "$*"
}

run() {
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'would run: %s\n' "$*"
  else
    "$@"
  fi
}

backup_file() {
  local path="$1"
  if [[ "$NO_BACKUP" == "1" ]]; then
    return
  fi
  if [[ "$DRY_RUN" == "1" ]]; then
    [[ -e "$path" ]] && log "would make a private backup of: $path"
    return
  fi
  if [[ -e "$path" ]]; then
    local backup_root backup_name
    backup_root="$HOME/.cache/agentic-engineering/backups/$(date +%Y%m%d%H%M%S)"
    backup_name="$(printf '%s' "$path" | sed 's#^/##; s#[/:]#_#g')"
    mkdir -p "$backup_root"
    chmod 700 "$HOME/.cache" "$HOME/.cache/agentic-engineering" "$HOME/.cache/agentic-engineering/backups" "$backup_root" 2>/dev/null || true
    cp "$path" "$backup_root/$backup_name"
    chmod 600 "$backup_root/$backup_name" 2>/dev/null || true
    find "$HOME/.cache/agentic-engineering/backups" -mindepth 1 -maxdepth 1 -type d -mtime +14 -exec rm -rf {} + 2>/dev/null || true
  fi
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

upsert_line() {
  local path="$1"
  local key="$2"
  local line="$3"
  mkdir -p "$(dirname "$path")"
  backup_file "$path"
  if [[ "$DRY_RUN" == "1" ]]; then
    log "would set $key in $path"
    return
  fi
  touch "$path"
  if grep -qE "^[[:space:]]*$key[[:space:]]*[:=]" "$path"; then
    tmp="$(mktemp)"
    awk -v key="$key" -v line="$line" '
      $0 ~ "^[[:space:]]*" key "[[:space:]]*[:=]" { print line; next }
      { print }
    ' "$path" > "$tmp"
    mv "$tmp" "$path"
  else
    printf '%s\n' "$line" >> "$path"
  fi
}

ensure_bunfig() {
  local path="$HOME/.bunfig.toml"
  local tmp
  mkdir -p "$(dirname "$path")"
  backup_file "$path"
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

upsert_top_level_toml() {
  local path="$1"
  local key="$2"
  local line="$3"
  local tmp
  mkdir -p "$(dirname "$path")"
  backup_file "$path"
  if [[ "$DRY_RUN" == "1" ]]; then
    log "would set top-level $key in $path"
    return
  fi
  touch "$path"
  tmp="$(mktemp)"
  awk -v key="$key" -v line="$line" '
    BEGIN { in_top=1; wrote=0 }
    /^[[:space:]]*\[/ {
      if (!wrote) {
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

MISE_BIN="${MISE_BIN:-}"
if [[ -z "$MISE_BIN" ]]; then
  if command -v mise >/dev/null 2>&1; then
    MISE_BIN="$(command -v mise)"
  elif [[ -x "$HOME/.local/bin/mise" ]]; then
    MISE_BIN="$HOME/.local/bin/mise"
  else
    log "mise not found. Install mise first, then rerun this script."
    exit 1
  fi
fi

log "Setting mise 7-day tool delay"
run "$MISE_BIN" settings set minimum_release_age 7d

log "Installing package tools through mise"
run "$MISE_BIN" use -g node@latest pnpm@latest yarn@latest bun@latest uv@latest python@latest

if [[ "$DRY_RUN" == "1" ]]; then
  log "dry run complete"
  exit 0
fi

npm_version="$("$MISE_BIN" exec -- npm --version 2>/dev/null || true)"
if [[ -z "$npm_version" ]]; then
  log "npm not found after mise setup"
  exit 1
fi
if ! version_ge "$npm_version" "11.10.0"; then
  log "stop: npm $npm_version is older than 11.10.0 and may ignore min-release-age"
  log "update npm through mise or Node before setting npm package-age safety"
  exit 1
fi

log "Setting npm 7-day package delay"
"$MISE_BIN" exec -- npm config set min-release-age 7 --location=user

log "Setting pnpm 7-day package delay"
export PNPM_HOME="${PNPM_HOME:-$HOME/Library/pnpm}"
export PATH="$PATH:$PNPM_HOME/bin"
if ! "$MISE_BIN" exec -- pnpm config set --global minimumReleaseAge 10080 >/dev/null 2>&1; then
  upsert_line "$HOME/.config/pnpm/config.yaml" "minimumReleaseAge" "minimumReleaseAge: 10080"
fi

log "Setting Yarn 7-day package delay"
"$MISE_BIN" exec -- yarn config set -H npmMinimalAgeGate 7d >/dev/null

log "Setting Bun 7-day package delay"
ensure_bunfig

log "Setting uv 7-day package delay"
upsert_top_level_toml "$HOME/.config/uv/uv.toml" "exclude-newer" 'exclude-newer = "P7D"'

log "Setting pip 7-day package delay"
"$MISE_BIN" exec -- python -m pip config --user set install.uploaded-prior-to P7D >/dev/null

log "done"
