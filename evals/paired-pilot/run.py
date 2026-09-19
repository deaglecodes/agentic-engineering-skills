"""Run a fixed, sequential, paired coding pilot through the authenticated Codex CLI."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

from grade import grade

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
TASKS = ("money", "pagination", "settings")
PACK_REF = "f2c2de2"
COMMON = (
    "Work only inside the current project directory. Do not access parent directories, "
    "user-level instruction or skill directories, network, or external services. "
    "Use existing runtimes only; do not install dependencies or spawn agents. "
    "Do not edit AGENTS.md or .agentic-engineering. "
    "Finish with a short account of what changed and the checks you actually ran."
)
CONFIG = [
    'model_reasoning_effort="medium"', 'project_doc_max_bytes=0',
    'skills.max_context_tokens=1', 'web_search="disabled"',
    'features.memories=false', 'features.plugins=false', 'features.apps=false',
    'features.multi_agent=false', 'features.hooks=false',
]


def command(args, cwd=None, **kwargs):
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=True, **kwargs).stdout


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_graders():
    evidence = {}
    for task in TASKS:
        broken = grade(task, HERE / "tasks" / task)
        with tempfile.TemporaryDirectory(prefix="ae-reference-") as folder:
            shutil.copy(HERE / "reference" / (task + ".py"), Path(folder) / "app.py")
            fixed = grade(task, folder)
        if fixed["passed"] != fixed["total"] or broken["passed"] == broken["total"]:
            raise RuntimeError(f"Invalid grader: {task}: {fixed['output']}")
        evidence[task] = {"broken_passed": broken["passed"], "reference_passed": fixed["passed"], "total": fixed["total"]}
    return evidence


def freeze_pack(output):
    revision = command(["git", "rev-parse", PACK_REF], REPO).strip()
    archive = subprocess.run(["git", "archive", revision], cwd=REPO, capture_output=True, check=True).stdout
    destination = output / "frozen-pack"
    destination.mkdir()
    # Only unpack regular files/directories from this repository's pinned revision.
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for member in tar.getmembers():
            path = Path(member.name)
            if path.is_absolute() or ".." in path.parts or not (member.isfile() or member.isdir()):
                raise ValueError("Unsupported archive entry")
        for member in tar.getmembers():
            path = destination / member.name
            if member.isdir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                with tar.extractfile(member) as source, path.open("wb") as target:
                    shutil.copyfileobj(source, target)
                path.chmod(member.mode & 0o777)
    return revision, destination


def prepare(task, condition, folder, pack):
    folder.mkdir(parents=True)
    for source in (HERE / "tasks" / task).iterdir():
        if source.name != "PROMPT.txt" and source.is_file():
            shutil.copy2(source, folder / source.name)
    command(["git", "init", "-q"], folder)
    command(["git", "add", "."], folder)
    command(["git", "-c", "user.name=Pilot Fixture", "-c", "user.email=fixture@example.invalid",
             "commit", "-qm", "Frozen task baseline"], folder)
    # A real pre-existing, uncommitted user edit is present in both conditions.
    (folder / "notes.md").write_text((folder / "notes.md").read_text() + "\nUncommitted user edit: preserve this line.\n")
    instructions = COMMON
    if condition == "with-pack":
        command([str(pack / "scripts/install.sh"), "--agent", "codex", "--target", str(folder)])
        instructions += "\n\n" + (folder / "AGENTS.md").read_text()
    return instructions


def invoke(args, folder, instructions, prompt, artifact):
    cmd = [args.codex, "-a", "never", "exec", "--ignore-user-config", "--ephemeral",
           "--sandbox", "workspace-write", "--json", "--color", "never", "-m", args.model]
    for value in CONFIG:
        cmd.extend(["-c", value])
    cmd.extend(["-c", "developer_instructions=" + json.dumps(instructions), "-C", str(folder), "-"])
    started = time.monotonic()
    timed_out = False
    with (artifact / "events.jsonl").open("w") as output, (artifact / "stderr.log").open("w") as errors:
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=output, stderr=errors,
                                   text=True, start_new_session=True)
        try:
            process.communicate(prompt, timeout=args.timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
    return {"returncode": process.returncode, "timed_out": timed_out,
            "seconds": round(time.monotonic() - started, 2)}


def read_events(path):
    result = {"usage": None, "commands": [], "messages": [], "errors": []}
    for line in path.read_text().splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "turn.completed":
            result["usage"] = event.get("usage")
        elif event.get("type") in ("error", "turn.failed"):
            result["errors"].append(event.get("message", event.get("error")))
        item = event.get("item", {})
        if event.get("type") == "item.completed":
            if item.get("type") == "command_execution":
                result["commands"].append({"command": item.get("command"), "exit_code": item.get("exit_code")})
            elif item.get("type") == "agent_message":
                result["messages"].append(item.get("text", ""))
    return result


def trial(args, task, condition, repeat, pack, output):
    name = f"{task}-{repeat}-{condition}"
    folder = output / "workspaces" / name
    artifact = output / "artifacts" / name
    artifact.mkdir(parents=True)
    instructions = prepare(task, condition, folder, pack)
    # Hash the frozen inputs; baseline and treatment application files must match.
    inputs = {name: digest(folder / name) for name in ("app.py", "README.md", "test_app.py", "notes.md")}
    pack_before = {str(p.relative_to(folder)): digest(p) for p in folder.rglob("*")
                   if p.is_file() and (".agentic-engineering" in p.parts or p.name == "AGENTS.md")}
    prompt = (HERE / "tasks" / task / "PROMPT.txt").read_text()
    print(f"START {name}", flush=True)
    result = invoke(args, folder, instructions, prompt, artifact)
    events = read_events(artifact / "events.jsonl")
    scored = grade(task, folder)
    visible_code = (
        "import importlib.util,unittest,sys; "
        "spec=importlib.util.spec_from_file_location('frozen_tests',sys.argv[1]); "
        "module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); "
        "result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module)); "
        "sys.exit(not result.wasSuccessful())"
    )
    visible = subprocess.run([sys.executable, "-B", "-c", visible_code,
                              str(HERE / "tasks" / task / "test_app.py")], cwd=folder,
                             capture_output=True, text=True, timeout=30)
    (artifact / "visible-tests.txt").write_text(visible.stdout + visible.stderr)
    (artifact / "heldout-tests.txt").write_text(scored.pop("output", ""))
    diff = command(["git", "diff", "--", ".", ":(exclude)notes.md"], folder)
    (artifact / "changes.patch").write_text(diff)
    for name_to_copy in ("app.py", "test_app.py"):
        shutil.copy2(folder / name_to_copy, artifact / name_to_copy)
    after_pack = {str(p.relative_to(folder)): digest(p) for p in folder.rglob("*")
                  if p.is_file() and (".agentic-engineering" in p.parts or p.name == "AGENTS.md")}
    result.update({"task": task, "condition": condition, "repeat": repeat,
                   "inputs": inputs, "heldout": scored, "visible_pass": visible.returncode == 0,
                   "notes_preserved": digest(folder / "notes.md") == inputs["notes.md"],
                   "pack_preserved": pack_before == after_pack,
                   "original_tests_preserved": digest(folder / "test_app.py") == inputs["test_app.py"],
                   "diff_stat": command(["git", "diff", "--numstat", "--", ".", ":(exclude)notes.md"], folder).strip(),
                   "app_sha256": digest(folder / "app.py"),
                   "git_status": command(["git", "status", "--porcelain"], folder).strip(),
                   **events})
    result["strict_success"] = (result["returncode"] == 0 and not result["timed_out"] and
                                scored["passed"] == scored["total"] and result["visible_pass"] and
                                result["notes_preserved"] and result["pack_preserved"])
    (artifact / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"DONE {task}-{repeat}-{condition}: {scored['passed']}/{scored['total']} held-out, "
          f"strict={result['strict_success']}, seconds={result['seconds']}", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check graders only; no model calls")
    parser.add_argument("--codex", default="codex", help="Codex CLI supporting the selected model")
    parser.add_argument("--model", default="gpt-6-astra")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    checked = check_graders()
    if args.check:
        print(json.dumps(checked, indent=2))
        return
    if args.output is None:
        parser.error("--output is required for model runs")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    revision, pack = freeze_pack(output)
    metadata = {
        "model": args.model, "reasoning": "medium", "timeout_seconds": args.timeout,
        "cli_version": command([args.codex, "--version"]).strip(), "pack_commit": revision,
        "suite_commit": command(["git", "rev-parse", "HEAD"], REPO).strip(),
        "grader_sha256": digest(HERE / "grade.py"), "grader_checks": checked,
        "config": CONFIG, "common_instructions": COMMON,
        "design": "3 authored runnable tasks x 2 conditions x 2 repetitions; sequential; reversed order in repetition 2",
        "runs": [],
    }
    (output / "manifest.json").write_text(json.dumps(metadata, indent=2) + "\n")
    for task in TASKS:
        for repeat in (1, 2):
            order = ("without-pack", "with-pack") if repeat == 1 else ("with-pack", "without-pack")
            for condition in order:
                result = trial(args, task, condition, repeat, pack, output)
                metadata["runs"].append(result)
                (output / "results.json").write_text(json.dumps(metadata, indent=2) + "\n")


if __name__ == "__main__":
    main()
