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
exit 0
SH
  chmod +x "$bin/mise"
}

write_fake_supported_tools() {
  local bin="$1"
  cat > "$bin/npm" <<'SH'
#!/usr/bin/env sh
if [ "$1" = --version ]; then echo 11.13.0; exit 0; fi
if [ "$1" = config ] && [ "$2" = get ]; then echo 7; exit 0; fi
if [ "$1" = config ] && [ "$2" = set ]; then exit 0; fi
SH
  cat > "$bin/pnpm" <<'SH'
#!/usr/bin/env sh
if [ "$1" = config ] && [ "$2" = get ]; then echo 10080; exit 0; fi
if [ "$1" = config ] && [ "$2" = set ]; then exit 0; fi
SH
  cat > "$bin/yarn" <<'SH'
#!/usr/bin/env sh
if [ "$1" = config ] && [ "$2" = get ]; then echo 7d; exit 0; fi
if [ "$1" = config ] && [ "$2" = set ]; then exit 0; fi
SH
  cat > "$bin/bun" <<'SH'
#!/usr/bin/env sh
exit 0
SH
  cat > "$bin/uv" <<'SH'
#!/usr/bin/env sh
exit 0
SH
  cat > "$bin/python" <<'SH'
#!/usr/bin/env sh
if [ "$1" = -m ] && [ "$2" = pip ] && [ "$3" = --version ]; then echo "pip 26.1 from fixture"; exit 0; fi
if [ "$1" = -m ] && [ "$2" = pip ] && [ "$3" = config ] && [ "$4" = get ]; then echo P7D; exit 0; fi
if [ "$1" = -m ] && [ "$2" = pip ] && [ "$3" = config ] && [ "$4" = --user ]; then exit 0; fi
SH
  chmod +x "$bin/npm" "$bin/pnpm" "$bin/yarn" "$bin/bun" "$bin/uv" "$bin/python"
}

test_project_local_setup_writes_only_target() {
  local tmp target home files
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  target="$tmp/project"
  home="$tmp/home"
  mkdir -p "$target" "$home"

  HOME="$home" "$ROOT/scripts/setup-package-age-safety.sh" --mode=project-local --target="$target" >/dev/null

  [ -f "$target/.npmrc" ] || fail "missing project .npmrc"
  [ -f "$target/pnpm-workspace.yaml" ] || fail "missing project pnpm-workspace.yaml"
  [ -f "$target/.yarnrc.yml" ] || fail "missing project .yarnrc.yml"
  [ -f "$target/bunfig.toml" ] || fail "missing project bunfig.toml"
  [ -f "$target/uv.toml" ] || fail "missing project uv.toml"
  [ -f "$target/.mise.toml" ] || fail "missing project .mise.toml"
  [ -f "$target/.agentic-engineering/package-safety/pip.conf" ] || fail "missing project pip template"

  files="$(find "$home" -type f | wc -l | tr -d ' ')"
  [ "$files" = "0" ] || fail "project-local setup wrote to HOME"
  pass "project-local setup writes only target"
}

test_project_local_dry_run_writes_no_files() {
  local tmp target files
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  target="$tmp/project"
  mkdir -p "$target"

  HOME="$tmp/home" "$ROOT/scripts/setup-package-age-safety.sh" --mode=project-local --target="$target" --dry-run >/dev/null
  files="$(find "$tmp" -type f | wc -l | tr -d ' ')"
  [ "$files" = "0" ] || fail "project-local dry run wrote files"
  pass "project-local dry run writes no files"
}

test_user_wide_requires_confirmation() {
  local tmp code
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  set +e
  HOME="$tmp/home" PATH="/usr/bin:/bin" "$ROOT/scripts/setup-package-age-safety.sh" --mode=user-wide >/dev/null 2>&1
  code=$?
  set -e
  [ "$code" -ne 0 ] || fail "user-wide setup should require confirmation"
  pass "user-wide setup requires confirmation"
}

test_user_wide_dry_run_writes_no_files() {
  local tmp home bin files
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  home="$tmp/home"
  bin="$tmp/bin"
  mkdir -p "$home" "$bin"
  write_fake_supported_tools "$bin"
  write_fake_mise_for_checks "$bin"

  HOME="$home" PATH="$bin:/usr/bin:/bin" MISE_BIN="$bin/mise" "$ROOT/scripts/setup-package-age-safety.sh" --mode=user-wide --dry-run >/dev/null
  files="$(find "$home" -type f | wc -l | tr -d ' ')"
  [ "$files" = "0" ] || fail "user-wide dry run wrote files"
  pass "user-wide dry run writes no files"
}

test_old_npm_is_skipped_in_user_wide() {
  local tmp home bin out
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  home="$tmp/home"
  bin="$tmp/bin"
  mkdir -p "$home" "$bin"
  cat > "$bin/npm" <<'SH'
#!/usr/bin/env sh
if [ "$1" = --version ]; then echo 11.9.0; exit 0; fi
if [ "$1" = config ] && [ "$2" = set ]; then echo called > "$HOME/npm-config-called"; exit 0; fi
SH
  chmod +x "$bin/npm"
  out="$tmp/out"

  HOME="$home" PATH="$bin:/usr/bin:/bin" "$ROOT/scripts/setup-package-age-safety.sh" --mode=user-wide --confirm-user-wide --no-backup >"$out"
  grep -q 'older than 11.10.0' "$out" || fail "old npm skip message missing"
  [ ! -e "$home/npm-config-called" ] || fail "npm config called despite old npm"
  pass "old npm is skipped in user-wide setup"
}

test_old_npm_blocks_project_hooks() {
  local tmp target home bin payload code
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  target="$tmp/project"
  home="$tmp/home"
  bin="$tmp/bin"
  mkdir -p "$target" "$home" "$bin"
  "$ROOT/scripts/setup-package-age-safety.sh" --mode=project-local --target="$target" >/dev/null
  cat > "$bin/npm" <<'SH'
#!/usr/bin/env sh
if [ "$1" = --version ]; then echo 11.9.0; exit 0; fi
if [ "$1" = config ] && [ "$2" = get ]; then echo 7; exit 0; fi
exit 0
SH
  chmod +x "$bin/npm"

  set +e
  HOME="$home" PATH="$bin:/usr/bin:/bin" "$ROOT/hooks/block-risky-package-install.sh" npm "$target" >/dev/null 2>&1
  code=$?
  set -e
  [ "$code" -ne 0 ] || fail "generic hook allowed old npm with project config"

  payload='{"tool_name":"Bash","tool_input":{"command":"npm install left-pad"},"cwd":"'"$target"'"}'
  set +e
  HOME="$home" PATH="$bin:/usr/bin:/bin" "$ROOT/hooks/claude/pretooluse-package-install-safety.sh" <<<"$payload" >/dev/null 2>&1
  code=$?
  set -e
  [ "$code" -eq 2 ] || fail "Claude hook allowed old npm with project config"
  pass "old npm blocks project hooks"
}

test_old_path_npm_not_hidden_by_failing_mise() {
  local tmp target home bin code
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  target="$tmp/project"
  home="$tmp/home"
  bin="$tmp/bin"
  mkdir -p "$target" "$home" "$bin"
  "$ROOT/scripts/setup-package-age-safety.sh" --mode=project-local --target="$target" >/dev/null
  cat > "$bin/npm" <<'SH'
#!/usr/bin/env sh
if [ "$1" = --version ]; then echo 11.9.0; exit 0; fi
if [ "$1" = config ] && [ "$2" = get ]; then echo 7; exit 0; fi
exit 0
SH
  cat > "$bin/mise" <<'SH'
#!/usr/bin/env sh
exit 1
SH
  chmod +x "$bin/npm" "$bin/mise"

  set +e
  HOME="$home" PATH="$bin:/usr/bin:/bin" MISE_BIN="$bin/mise" "$ROOT/hooks/block-risky-package-install.sh" npm "$target" >/dev/null 2>&1
  code=$?
  set -e
  [ "$code" -ne 0 ] || fail "failing MISE_BIN hid old PATH npm"
  pass "old PATH npm is not hidden by failing MISE_BIN"
}

test_npm_user_wide_config_is_recognized() {
  local tmp target home bin
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  target="$tmp/project"
  home="$tmp/home"
  bin="$tmp/bin"
  mkdir -p "$target" "$home" "$bin"
  printf 'min-release-age=7\n' > "$home/.npmrc"
  cat > "$bin/npm" <<'SH'
#!/usr/bin/env sh
if [ "$1" = --version ]; then echo 11.13.0; exit 0; fi
if [ "$1" = config ] && [ "$2" = get ]; then echo null; exit 0; fi
exit 0
SH
  chmod +x "$bin/npm"

  HOME="$home" PATH="$bin:/usr/bin:/bin" "$ROOT/hooks/block-risky-package-install.sh" npm "$target" >/dev/null
  pass "npm user-wide config is recognized"
}

test_npm_env_override_blocks_project_gate() {
  local tmp target home bin payload code
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  target="$tmp/project"
  home="$tmp/home"
  bin="$tmp/bin"
  mkdir -p "$target" "$home" "$bin"
  "$ROOT/scripts/setup-package-age-safety.sh" --mode=project-local --target="$target" >/dev/null
  cat > "$bin/npm" <<'SH'
#!/usr/bin/env sh
if [ "$1" = --version ]; then echo 11.13.0; exit 0; fi
if [ "$1" = config ] && [ "$2" = get ]; then echo 0; exit 0; fi
exit 0
SH
  chmod +x "$bin/npm"

  set +e
  npm_config_min_release_age=0 HOME="$home" PATH="$bin:/usr/bin:/bin" "$ROOT/hooks/block-risky-package-install.sh" npm "$target" >/dev/null 2>&1
  code=$?
  set -e
  [ "$code" -ne 0 ] || fail "generic hook allowed npm env override"

  payload='{"tool_name":"Bash","tool_input":{"command":"npm install left-pad"},"cwd":"'"$target"'"}'
  set +e
  npm_config_min_release_age=0 HOME="$home" PATH="$bin:/usr/bin:/bin" "$ROOT/hooks/claude/pretooluse-package-install-safety.sh" <<<"$payload" >/dev/null 2>&1
  code=$?
  set -e
  [ "$code" -eq 2 ] || fail "Claude hook allowed inherited npm env override"
  pass "npm env override blocks project gate"
}

test_user_wide_backup_and_restore() {
  local tmp home bin backup_dir restored
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  home="$tmp/home"
  bin="$tmp/bin"
  mkdir -p "$home/.config/uv" "$bin"
  printf 'exclude-newer = "P1D"\n' > "$home/.config/uv/uv.toml"
  write_fake_supported_tools "$bin"

  HOME="$home" PATH="$bin:/usr/bin:/bin" "$ROOT/scripts/setup-package-age-safety.sh" --mode=user-wide --confirm-user-wide >/dev/null
  backup_dir="$(find "$home/.cache/agentic-engineering/backups" -mindepth 1 -maxdepth 1 -type d | sort | tail -n 1)"
  [ -n "$backup_dir" ] || fail "backup directory not created"
  grep -q 'P7D' "$home/.config/uv/uv.toml" || fail "uv config not updated"

  HOME="$home" "$ROOT/scripts/setup-package-age-safety.sh" --restore="$backup_dir" >/dev/null
  restored="$(sed -n '1p' "$home/.config/uv/uv.toml")"
  [ "$restored" = 'exclude-newer = "P1D"' ] || fail "restore did not restore uv config"
  pass "user-wide backup and restore"
}

test_user_wide_restore_removes_created_files() {
  local tmp home bin backup_dir
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  home="$tmp/home"
  bin="$tmp/bin"
  mkdir -p "$home" "$bin"
  write_fake_supported_tools "$bin"

  HOME="$home" PATH="$bin:/usr/bin:/bin" "$ROOT/scripts/setup-package-age-safety.sh" --mode=user-wide --confirm-user-wide >/dev/null
  backup_dir="$(find "$home/.cache/agentic-engineering/backups" -mindepth 1 -maxdepth 1 -type d | sort | tail -n 1)"
  [ -f "$home/.bunfig.toml" ] || fail "bun config was not created"
  [ -f "$home/.config/uv/uv.toml" ] || fail "uv config was not created"

  HOME="$home" "$ROOT/scripts/setup-package-age-safety.sh" --restore="$backup_dir" >/dev/null
  [ ! -e "$home/.bunfig.toml" ] || fail "restore did not remove created bun config"
  [ ! -e "$home/.config/uv/uv.toml" ] || fail "restore did not remove created uv config"
  pass "user-wide restore removes created files"
}

test_user_wide_setup_uses_detected_python3() {
  local tmp home bin
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  home="$tmp/home"
  bin="$tmp/bin"
  mkdir -p "$home" "$bin"
  cat > "$bin/python" <<'SH'
#!/usr/bin/env sh
exit 1
SH
  cat > "$bin/python3" <<'SH'
#!/usr/bin/env sh
if [ "$1" = -m ] && [ "$2" = pip ] && [ "$3" = --version ]; then echo "pip 26.1 from fixture"; exit 0; fi
if [ "$1" = -m ] && [ "$2" = pip ] && [ "$3" = config ] && [ "$4" = --user ] && [ "$5" = set ]; then echo called > "$HOME/python3-pip-called"; exit 0; fi
exit 1
SH
  chmod +x "$bin/python" "$bin/python3"

  HOME="$home" PATH="$bin:/usr/bin:/bin" "$ROOT/scripts/setup-package-age-safety.sh" --mode=user-wide --confirm-user-wide --no-backup >/dev/null
  [ -f "$home/python3-pip-called" ] || fail "user-wide setup did not use detected python3 pip"
  pass "user-wide setup uses detected python3"
}

test_user_wide_setup_uses_detected_pip3() {
  local tmp home bin
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  home="$tmp/home"
  bin="$tmp/bin"
  mkdir -p "$home" "$bin"
  for tool in python python3 pip; do
    cat > "$bin/$tool" <<'SH'
#!/usr/bin/env sh
exit 1
SH
    chmod +x "$bin/$tool"
  done
  cat > "$bin/pip3" <<'SH'
#!/usr/bin/env sh
if [ "$1" = --version ]; then echo "pip 26.1 from fixture"; exit 0; fi
if [ "$1" = config ] && [ "$2" = --user ] && [ "$3" = set ]; then echo called > "$HOME/pip3-called"; exit 0; fi
exit 1
SH
  chmod +x "$bin/pip3"

  HOME="$home" PATH="$bin:/usr/bin:/bin" "$ROOT/scripts/setup-package-age-safety.sh" --mode=user-wide --confirm-user-wide --no-backup >/dev/null
  [ -f "$home/pip3-called" ] || fail "user-wide setup did not use detected pip3"
  pass "user-wide setup uses detected pip3"
}

test_check_package_age_project_scope() {
  local tmp target code
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  target="$tmp/project"
  mkdir -p "$target"
  "$ROOT/scripts/setup-package-age-safety.sh" --mode=project-local --target="$target" >/dev/null

  set +e
  "$ROOT/scripts/check-package-age-safety.sh" --scope=project --target="$target" >/dev/null 2>&1
  code=$?
  set -e
  [ "$code" -ne 0 ] || fail "project scope should warn when pip template is inactive"

  printf '[pip]\nexclude-newer = "P7D"\n' > "$target/uv.toml"
  set +e
  "$ROOT/scripts/check-package-age-safety.sh" --scope=project --target="$target" >/dev/null 2>&1
  code=$?
  set -e
  [ "$code" -ne 0 ] || fail "uv wrong-section check passed"
  pass "check-package-age-safety project scope"
}

test_package_hook_negative_and_positive_paths() {
  local tmp target home bin code
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  target="$tmp/project"
  home="$tmp/home"
  bin="$tmp/bin"
  mkdir -p "$target" "$home" "$bin"
  "$ROOT/scripts/setup-package-age-safety.sh" --mode=project-local --target="$target" >/dev/null

  for cmd in npm npx pnpm yarn bun uv; do
    HOME="$home" PATH="$bin:/usr/bin:/bin" "$ROOT/hooks/block-risky-package-install.sh" "$cmd" "$target" >/dev/null
  done

  for cmd in pip pip3 python python3; do
    set +e
    HOME="$home" PATH="$bin:/usr/bin:/bin" "$ROOT/hooks/block-risky-package-install.sh" "$cmd" "$target" >/dev/null 2>&1
    code=$?
    set -e
    [ "$code" -ne 0 ] || fail "pip template-only config allowed $cmd"
  done

  set +e
  HOME="$home" PATH="$bin:/usr/bin:/bin" "$ROOT/hooks/block-risky-package-install.sh" cargo "$target" >/dev/null 2>&1
  code=$?
  set -e
  [ "$code" -ne 0 ] || fail "unsupported package manager was allowed"
  pass "package hook paths"
}

test_package_hook_allows_active_pip_config() {
  local tmp target home bin
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  target="$tmp/project"
  home="$tmp/home"
  bin="$tmp/bin"
  mkdir -p "$target" "$home" "$bin"
  "$ROOT/scripts/setup-package-age-safety.sh" --mode=project-local --target="$target" >/dev/null
  cat > "$bin/python" <<'SH'
#!/usr/bin/env sh
if [ "$1" = -m ] && [ "$2" = pip ] && [ "$3" = --version ]; then echo "pip 26.1 from fixture"; exit 0; fi
if [ "$1" = -m ] && [ "$2" = pip ] && [ "$3" = config ] && [ "$4" = get ]; then echo P7D; exit 0; fi
exit 1
SH
  chmod +x "$bin/python"

  PIP_CONFIG_FILE="$target/.agentic-engineering/package-safety/pip.conf" HOME="$home" PATH="$bin:/usr/bin:/bin" "$ROOT/hooks/block-risky-package-install.sh" pip "$target" >/dev/null
  PIP_UPLOADED_PRIOR_TO=P7D HOME="$home" PATH="$bin:/usr/bin:/bin" "$ROOT/hooks/block-risky-package-install.sh" pip "$target" >/dev/null
  pass "package hook allows active pip config"
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

test_claude_pretooluse_hook_blocks_and_allows() {
  local tmp target home code payload
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  target="$tmp/project"
  home="$tmp/home"
  mkdir -p "$target" "$home"
  payload='{"tool_name":"Bash","tool_input":{"command":"npm install left-pad"},"cwd":"'"$target"'"}'

  set +e
  HOME="$home" PATH="/usr/bin:/bin" "$ROOT/hooks/claude/pretooluse-package-install-safety.sh" <<<"$payload" >/dev/null 2>&1
  code=$?
  set -e
  [ "$code" -eq 2 ] || fail "Claude package hook should block without age gate"

  "$ROOT/scripts/setup-package-age-safety.sh" --mode=project-local --target="$target" >/dev/null
  HOME="$home" PATH="/usr/bin:/bin" "$ROOT/hooks/claude/pretooluse-package-install-safety.sh" <<<"$payload" >/dev/null 2>&1

  payload='{"tool_name":"Bash","tool_input":{"command":"npm install left-pad --min-release-age=0"},"cwd":"'"$target"'"}'
  set +e
  HOME="$home" PATH="/usr/bin:/bin" "$ROOT/hooks/claude/pretooluse-package-install-safety.sh" <<<"$payload" >/dev/null 2>&1
  code=$?
  set -e
  [ "$code" -eq 2 ] || fail "Claude package hook should block npm min-release-age override"

  payload='{"tool_name":"Bash","tool_input":{"command":"NPM_CONFIG_MIN_RELEASE_AGE=0 npm install left-pad"},"cwd":"'"$target"'"}'
  set +e
  HOME="$home" PATH="/usr/bin:/bin" "$ROOT/hooks/claude/pretooluse-package-install-safety.sh" <<<"$payload" >/dev/null 2>&1
  code=$?
  set -e
  [ "$code" -eq 2 ] || fail "Claude package hook should block npm env min-release-age override"

  payload='{"tool_name":"Bash","tool_input":{"command":"npm ci"},"cwd":"'"$target"'"}'
  HOME="$home" PATH="/usr/bin:/bin" "$ROOT/hooks/claude/pretooluse-package-install-safety.sh" <<<"$payload" >/dev/null 2>&1

  target="$tmp/project-without-config"
  mkdir -p "$target"
  payload='{"tool_name":"Bash","tool_input":{"command":"npm ci"},"cwd":"'"$target"'"}'
  set +e
  HOME="$home" PATH="/usr/bin:/bin" "$ROOT/hooks/claude/pretooluse-package-install-safety.sh" <<<"$payload" >/dev/null 2>&1
  code=$?
  set -e
  [ "$code" -eq 2 ] || fail "Claude package hook should block npm ci without age gate"

  payload='{"tool_name":"Bash","tool_input":{"command":"cd '"$target"' && npm install left-pad"},"cwd":"'"$tmp"'"}'
  set +e
  HOME="$home" PATH="/usr/bin:/bin" "$ROOT/hooks/claude/pretooluse-package-install-safety.sh" <<<"$payload" >/dev/null 2>&1
  code=$?
  set -e
  [ "$code" -eq 2 ] || fail "Claude package hook should block chained npm install without age gate"

  pass "Claude PreToolUse package hook"
}

test_project_local_setup_writes_only_target
test_project_local_dry_run_writes_no_files
test_user_wide_requires_confirmation
test_user_wide_dry_run_writes_no_files
test_old_npm_is_skipped_in_user_wide
test_old_npm_blocks_project_hooks
test_old_path_npm_not_hidden_by_failing_mise
test_npm_user_wide_config_is_recognized
test_npm_env_override_blocks_project_gate
test_user_wide_backup_and_restore
test_user_wide_restore_removes_created_files
test_user_wide_setup_uses_detected_python3
test_user_wide_setup_uses_detected_pip3
test_check_package_age_project_scope
test_package_hook_negative_and_positive_paths
test_package_hook_allows_active_pip_config
test_secret_scan_markdown_patterns
test_claude_pretooluse_hook_blocks_and_allows

printf '%s\n' 'fixtures: ok'
