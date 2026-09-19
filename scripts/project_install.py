"""Install a local workflow pack without replacing a project's instructions."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import stat
import sys
import tempfile


ROOT = Path(__file__).resolve().parent.parent
BASE = Path(".agentic-engineering")
PACK = BASE / "pack"
STATE = BASE / "install.json"
MARKER = "<!-- agentic-engineering:"
ADAPTERS = {
    "codex": ("adapters/codex/AGENTS.md", "AGENTS.md"),
    "claude": ("adapters/claude/CLAUDE.md", "CLAUDE.md"),
    "cursor": (
        "adapters/cursor/.cursor/rules/agentic-engineering.mdc",
        ".cursor/rules/agentic-engineering.mdc",
    ),
    "generic": ("adapters/generic/AGENTIC_ENGINEERING.md", "AGENTIC_ENGINEERING.md"),
}
# A public-file allowlist: never copy the checkout, its .git, or local settings.
DIRECTORIES = ("adapters", "skills", "scripts", "hooks", "templates", "docs", "evals", "examples", "tests", ".claude-plugin")
SUFFIXES = {".md", ".mdc", ".sh", ".py", ".json", ".toml", ".yaml", ".yml", ".conf", ".npmrc"}


def checked_path(target, relative):
    """Refuse links and non-directory parents before reading or writing anything."""
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Installation paths must stay inside the target project.")
    current = target
    for index, part in enumerate(relative.parts):
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Refusing symlink: {relative}")
        if index < len(relative.parts) - 1 and current.exists() and not current.is_dir():
            raise ValueError(f"Expected a directory on path: {relative}")
    return current


def fingerprint(path):
    return {
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "mode": stat.S_IMODE(path.stat().st_mode),
    }


def source_files():
    files = {}
    for directory in DIRECTORIES:
        for path in sorted((ROOT / directory).rglob("*")):
            relative = path.relative_to(ROOT)
            checked_path(ROOT, relative)
            if any(part.startswith(".") for part in path.relative_to(ROOT / directory).parts):
                # Cursor's rule directory is intentionally part of the pack.
                if not str(relative).startswith("adapters/cursor/.cursor/rules/"):
                    continue
            if path.is_file() and path.suffix in SUFFIXES:
                files[str(relative)] = path
    for name in ("README.md", "LICENSE", "AGENTS.md", "CHANGELOG.md", "ROADMAP.md", "CONTRIBUTING.md", "CONTRIBUTORS.md", "SECURITY.md"):
        files[name] = checked_path(ROOT, name)
    return files


def instruction_block(agent):
    text = (ROOT / ADAPTERS[agent][0]).read_text()
    # Commands are run from the user's project; the tools live in the pack.
    text = text.replace("./scripts/", "./.agentic-engineering/pack/scripts/")
    text = text.replace("`hooks/claude/`", "`.agentic-engineering/pack/hooks/claude/`")
    text = text.replace("`examples/claude/`", "the pack's Claude hook documentation")
    text = text.replace("`docs/claude.md`", "`.agentic-engineering/pack/docs/claude.md`")
    note = (
        "\n## Installed Skill Files\n\n"
        "Read `.agentic-engineering/pack/skills/ae-core-charter/SKILL.md` for substantial work.\n"
        "Read other matching skills at `.agentic-engineering/pack/skills/<skill-name>/SKILL.md`.\n"
        "These are local reference files; this install does not register native slash commands.\n"
        "Paths in those skills beginning with `scripts/` refer to `.agentic-engineering/pack/scripts/`.\n"
        "Keep the target project as the working directory for project checks and setup.\n"
        "The pack's `validate-repo.sh` checks the source pack, not this application's behavior.\n"
        "Existing project requirements still apply. Hooks and package-manager settings require separate setup.\n"
    )
    if agent == "cursor":
        return (text + note).encode()
    return (f"{MARKER}begin -->\n" + text + note + f"{MARKER}end -->\n").encode()


def read_state(target):
    path = checked_path(target, STATE)
    if not path.is_file():
        raise ValueError("No managed installation found in this project.")
    state = json.loads(path.read_text())
    if state.get("schema") != 1 or state.get("agent") not in ADAPTERS:
        raise ValueError("Unrecognized installation manifest; no files changed.")
    if state.get("instruction") != ADAPTERS[state["agent"]][1]:
        raise ValueError("Invalid instruction path in installation manifest.")
    return state


def verify_installation(target, state):
    pack = checked_path(target, PACK)
    if not pack.is_dir():
        raise ValueError("Installed pack is missing; no files changed.")
    actual = {}
    for path in pack.rglob("*"):
        checked_path(target, path.relative_to(target))
        if path.is_file():
            actual[str(path.relative_to(pack))] = fingerprint(path)
    if actual != state["files"]:
        raise ValueError("Installed pack has changed or extra files; preserve those edits before removing it.")
    path = checked_path(target, state["instruction"])
    data = path.read_bytes()
    block = state["inserted"].encode()
    if state["agent"] == "cursor":
        if data != block:
            raise ValueError("Installed Cursor rule was edited; no files changed.")
    elif data.count(block) != 1:
        raise ValueError("Managed instruction block was edited or duplicated; no files changed.")
    return path, data, block


def install(target, agent, dry_run):
    state_path = checked_path(target, STATE)
    files = source_files()
    expected = {name: fingerprint(path) for name, path in files.items()}
    if state_path.exists():
        state = read_state(target)
        verify_installation(target, state)
        if state["agent"] != agent or state["files"] != expected:
            raise ValueError("A different pack or adapter is installed. Uninstall it before installing this version.")
        print("Already installed; no changes.")
        return
    pack = checked_path(target, PACK)
    if pack.exists():
        raise ValueError("The pack directory already exists without a manifest; no files changed.")
    instruction = ADAPTERS[agent][1]
    path = checked_path(target, instruction)
    if path.exists() and (not path.is_file() or agent == "cursor"):
        raise ValueError(f"Existing {instruction} will not be replaced.")
    existed = path.exists()
    original = path.read_bytes() if existed else b""
    if MARKER.encode() in original:
        raise ValueError("An unmanaged Agentic Engineering block already exists; no files changed.")
    inserted = (b"\n\n" if original else b"") + instruction_block(agent)
    print(f"{'Would install' if dry_run else 'Installing'} {agent} in {target}")
    print(f"  Append workflow to {instruction}" if existed else f"  Create {instruction}")
    print(f"  Copy {len(files)} public pack files to {PACK}")
    if dry_run:
        return
    base = checked_path(target, BASE)
    base.mkdir(exist_ok=True)
    staged = Path(tempfile.mkdtemp(prefix=".install-", dir=base))
    try:
        for name, source in files.items():
            destination = staged / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        state = {
            "schema": 1, "agent": agent, "instruction": instruction,
            "existed": existed, "inserted": inserted.decode(), "files": expected,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        # Fail if another process changed the instructions while the pack was staged.
        if path.exists() != existed or (existed and path.read_bytes() != original):
            raise ValueError("Project instructions changed during installation; retry after reviewing them.")
        staged.rename(pack)
        try:
            with path.open("ab" if existed else "xb") as stream:
                stream.write(inserted)
            state_path.write_text(json.dumps(state, indent=2) + "\n")
        except OSError:
            # Roll back only the bytes we just appended, never concurrent user edits.
            if path.is_file() and path.read_bytes() == original + inserted:
                if existed:
                    path.write_bytes(original)
                else:
                    path.unlink()
            shutil.rmtree(pack)
            raise
    finally:
        if staged.exists():
            shutil.rmtree(staged)
    print("Installed. Start a new agent session in the target project.")


def uninstall(target, dry_run):
    state = read_state(target)
    path, data, block = verify_installation(target, state)
    remaining = data.replace(block, b"", 1)
    print(f"{'Would remove' if dry_run else 'Removing'} {state['agent']} installation from {target}")
    if dry_run:
        return
    if not remaining and not state["existed"]:
        path.unlink()
    else:
        path.write_bytes(remaining)
    shutil.rmtree(checked_path(target, PACK))
    checked_path(target, STATE).unlink()
    base = checked_path(target, BASE)
    if not any(base.iterdir()):
        base.rmdir()
    print("Removed the managed pack and workflow. Other project files were preserved.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, type=Path, help="Existing project directory")
    parser.add_argument("--agent", choices=ADAPTERS)
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    parser.add_argument("--uninstall", action="store_true", help="Remove an unchanged managed install")
    args = parser.parse_args()
    if not args.uninstall and not args.agent:
        parser.error("--agent is required when installing")
    if args.uninstall and args.agent:
        parser.error("--uninstall uses the saved adapter; omit --agent")
    try:
        target = args.target.expanduser().resolve(strict=True)
        if not target.is_dir() or target == ROOT:
            raise ValueError("Choose an existing target project other than this pack's source directory.")
        if args.uninstall:
            uninstall(target, args.dry_run)
        else:
            install(target, args.agent, args.dry_run)
    except (OSError, ValueError, KeyError, TypeError) as error:
        # Do not echo file contents or configuration values on failure.
        print(f"Install error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
