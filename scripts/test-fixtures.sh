#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

pass() {
  printf '%s\n' "ok: $1"
}

fail() {
  printf '%s\n' "fail: $1"
  exit 1
}

write_fake_mise_for_checks() {
  local bin="$1"
  cat > "$bin/mise" <<'SH'
#!/usr/bin/env sh
set -eu
if [ "$1" = settings ] && [ "$2" = get ]; then echo 7d; exit 0; fi
if [ "$1" = exec ] && [ "$2" = -- ] && [ "$3" = npm ] && [ "$4" = --version ]; then echo 11.13.0; exit 0; fi
if [ "$1" = exec ] && [ "$2" = -- ] && [ "$3" = npm ] && [ "$4" = config ]; then echo 7; exit 0; fi
if [ "$1" = exec ] && [ "$2" = -- ] && [ "$3" = pnpm ]; then echo 10080; exit 0; fi
if [ "$1" = exec ] && [ "$2" = -- ] && [ "$3" = yarn ]; then echo 7d; exit 0; fi
if [ "$1" = exec ] && [ "$2" = -- ] && [ "$3" = python ]; then echo P7D; exit 0; fi
exit 0
SH
  chmod +x "$bin/mise"
}

test_check_package_age_happy_path() {
  local tmp home bin
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  home="$tmp/home"
  bin="$tmp/bin"
  mkdir -p "$home/.config/uv" "$bin"
  printf '[install]\nminimumReleaseAge = 604800\n' > "$home/.bunfig.toml"
  printf 'exclude-newer = "P7D"\n[pip]\n' > "$home/.config/uv/uv.toml"
  write_fake_mise_for_checks "$bin"
  HOME="$home" MISE_BIN="$bin/mise" PATH="$bin:/usr/bin:/bin" "$ROOT/scripts/check-package-age-safety.sh" >/dev/null
  pass "check-package-age-safety fixture"
}

test_setup_stops_on_old_npm() {
  local tmp home bin out code
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  home="$tmp/home"
  bin="$tmp/bin"
  mkdir -p "$home" "$bin"
  cat > "$bin/mise" <<'SH'
#!/usr/bin/env sh
set -eu
if [ "$1" = settings ] && [ "$2" = set ]; then exit 0; fi
if [ "$1" = use ]; then exit 0; fi
if [ "$1" = exec ] && [ "$2" = -- ] && [ "$3" = npm ] && [ "$4" = --version ]; then echo 11.9.0; exit 0; fi
if [ "$1" = exec ] && [ "$2" = -- ] && [ "$3" = npm ] && [ "$4" = config ]; then echo called > "$HOME/npm-config-called"; exit 0; fi
exit 0
SH
  chmod +x "$bin/mise"
  out="$tmp/out"
  set +e
  HOME="$home" MISE_BIN="$bin/mise" "$ROOT/scripts/setup-package-age-safety.sh" >"$out" 2>&1
  code=$?
  set -e
  [ "$code" -ne 0 ] || fail "old npm setup should fail"
  grep -q 'older than 11.10.0' "$out" || fail "old npm message missing"
  [ ! -e "$home/npm-config-called" ] || fail "npm config called despite old npm"
  pass "setup stops on old npm"
}

test_setup_writes_uv_top_level_and_private_backups() {
  local tmp home bin adjacent private first_line
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  home="$tmp/home"
  bin="$tmp/bin"
  mkdir -p "$home/.config/uv" "$bin"
  printf '[pip]\nindex-url = "https://example.invalid/simple"\n' > "$home/.config/uv/uv.toml"
  cat > "$bin/mise" <<'SH'
#!/usr/bin/env sh
set -eu
if [ "$1" = settings ] && [ "$2" = set ]; then exit 0; fi
if [ "$1" = use ]; then exit 0; fi
if [ "$1" = exec ] && [ "$2" = -- ] && [ "$3" = npm ] && [ "$4" = --version ]; then echo 11.13.0; exit 0; fi
if [ "$1" = exec ] && [ "$2" = -- ] && [ "$3" = npm ]; then printf 'min-release-age=7\n' > "$HOME/.npmrc"; exit 0; fi
if [ "$1" = exec ] && [ "$2" = -- ] && [ "$3" = pnpm ]; then exit 1; fi
if [ "$1" = exec ] && [ "$2" = -- ] && [ "$3" = yarn ]; then printf 'npmMinimalAgeGate: 7d\n' > "$HOME/.yarnrc.yml"; exit 0; fi
if [ "$1" = exec ] && [ "$2" = -- ] && [ "$3" = python ]; then mkdir -p "$HOME/.config/pip"; printf '[install]\nuploaded-prior-to = P7D\n' > "$HOME/.config/pip/pip.conf"; exit 0; fi
exit 0
SH
  chmod +x "$bin/mise"
  HOME="$home" MISE_BIN="$bin/mise" "$ROOT/scripts/setup-package-age-safety.sh" >/dev/null
  first_line="$(sed -n '1p' "$home/.config/uv/uv.toml")"
  [ "$first_line" = 'exclude-newer = "P7D"' ] || fail "uv exclude-newer not top-level"
  adjacent="$(find "$home" -name '*.agentic-engineering-backup-*' | wc -l | tr -d ' ')"
  private="$(find "$home/.cache/agentic-engineering/backups" -type f 2>/dev/null | wc -l | tr -d ' ')"
  [ "$adjacent" = "0" ] || fail "adjacent backup files created"
  [ "$private" -gt 0 ] || fail "private backup not created"
  pass "setup uv top-level and private backup"
}

test_no_backup_mode() {
  local tmp home bin private
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  home="$tmp/home"
  bin="$tmp/bin"
  mkdir -p "$home/.config/uv" "$bin"
  printf '[pip]\nindex-url = "https://example.invalid/simple"\n' > "$home/.config/uv/uv.toml"
  cat > "$bin/mise" <<'SH'
#!/usr/bin/env sh
set -eu
if [ "$1" = settings ] && [ "$2" = set ]; then exit 0; fi
if [ "$1" = use ]; then exit 0; fi
if [ "$1" = exec ] && [ "$2" = -- ] && [ "$3" = npm ] && [ "$4" = --version ]; then echo 11.13.0; exit 0; fi
if [ "$1" = exec ]; then exit 0; fi
SH
  chmod +x "$bin/mise"
  HOME="$home" MISE_BIN="$bin/mise" "$ROOT/scripts/setup-package-age-safety.sh" --no-backup >/dev/null
  if [ -d "$home/.cache/agentic-engineering/backups" ]; then
    private="$(find "$home/.cache/agentic-engineering/backups" -type f | wc -l | tr -d ' ')"
  else
    private=0
  fi
  [ "$private" = "0" ] || fail "--no-backup created backup files"
  pass "setup --no-backup fixture"
}

test_dry_run_writes_no_files() {
  local tmp files
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  HOME="$tmp" MISE_BIN="${MISE_BIN:-/bin/true}" "$ROOT/scripts/setup-package-age-safety.sh" --dry-run >/dev/null
  files="$(find "$tmp" -type f | wc -l | tr -d ' ')"
  [ "$files" = "0" ] || fail "dry run wrote files"
  pass "setup dry run writes no files"
}

test_secret_scan_markdown_patterns() {
  local tmp repo label code
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  repo="$tmp/repo"
  mkdir -p "$repo"
  for label in "API Key" "api key" "token" "Authorization"; do
    if [ "$label" = "Authorization" ]; then
      printf '# Fixture\n%s: Bearer abc\n' "$label" > "$repo/README.md"
    else
      printf '# Fixture\n%s: abc\n' "$label" > "$repo/README.md"
    fi
    set +e
    "$ROOT/scripts/secret-scan.sh" "$repo" >/dev/null 2>&1
    code=$?
    set -e
    [ "$code" -ne 0 ] || fail "secret scan missed $label"
  done
  pass "secret scan markdown patterns"
}

test_package_hook_negative_and_positive_paths() {
  local tmp home bin code
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  home="$tmp/home"
  bin="$tmp/bin"
  mkdir -p "$home/.config/uv" "$bin"
  printf '[install]\nminimumReleaseAge = 604800\n' > "$home/.bunfig.toml"
  printf 'exclude-newer = "P7D"\n' > "$home/.config/uv/uv.toml"
  cat > "$bin/npm" <<'SH'
#!/usr/bin/env sh
if [ "$1" = --version ]; then echo 11.13.0; exit 0; fi
if [ "$1" = config ] && [ "$2" = get ]; then echo 7; exit 0; fi
SH
  cat > "$bin/pnpm" <<'SH'
#!/usr/bin/env sh
if [ "$1" = config ] && [ "$2" = get ]; then echo 10080; exit 0; fi
SH
  cat > "$bin/yarn" <<'SH'
#!/usr/bin/env sh
if [ "$1" = config ] && [ "$2" = get ]; then echo 7d; exit 0; fi
SH
  cat > "$bin/python" <<'SH'
#!/usr/bin/env sh
if [ "$1" = -m ] && [ "$2" = pip ] && [ "$3" = config ] && [ "$4" = get ]; then echo P7D; exit 0; fi
SH
  chmod +x "$bin/npm" "$bin/pnpm" "$bin/yarn" "$bin/python"
  for cmd in npm npx pnpm yarn bun uv pip pip3 python python3; do
    HOME="$home" PATH="$bin:/usr/bin:/bin" "$ROOT/hooks/block-risky-package-install.sh" "$cmd" >/dev/null
  done
  set +e
  HOME="$home" PATH="$bin:/usr/bin:/bin" "$ROOT/hooks/block-risky-package-install.sh" cargo >/dev/null 2>&1
  code=$?
  set -e
  [ "$code" -ne 0 ] || fail "unsupported package manager was allowed"
  pass "package hook paths"
}

test_check_rejects_uv_wrong_section() {
  local tmp home bin code
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  home="$tmp/home"
  bin="$tmp/bin"
  mkdir -p "$home/.config/uv" "$bin"
  printf '[install]\nminimumReleaseAge = 604800\n' > "$home/.bunfig.toml"
  printf '[pip]\nexclude-newer = "P7D"\n' > "$home/.config/uv/uv.toml"
  write_fake_mise_for_checks "$bin"
  set +e
  HOME="$home" MISE_BIN="$bin/mise" PATH="$bin:/usr/bin:/bin" "$ROOT/scripts/check-package-age-safety.sh" >/dev/null 2>&1
  code=$?
  set -e
  [ "$code" -ne 0 ] || fail "uv wrong-section check passed"
  pass "check rejects uv wrong section"
}

test_check_package_age_happy_path
test_setup_stops_on_old_npm
test_setup_writes_uv_top_level_and_private_backups
test_no_backup_mode
test_dry_run_writes_no_files
test_secret_scan_markdown_patterns
test_package_hook_negative_and_positive_paths
test_check_rejects_uv_wrong_section

printf '%s\n' 'fixtures: ok'
