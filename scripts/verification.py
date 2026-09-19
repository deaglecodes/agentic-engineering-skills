"""Run explicit checks and detect edits to protected files; no third-party packages."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import tempfile
import time


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_plan(path):
    raw = path.read_bytes()
    plan = json.loads(raw)
    if not isinstance(plan, dict) or plan.get("schema") != 1:
        raise ValueError("Expected a plan with schema 1")
    checks = plan.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ValueError("Define at least one check")
    names = set()
    for check in checks:
        if not isinstance(check, dict):
            raise ValueError("Each check must be an object")
        name, argv = check.get("name"), check.get("argv")
        limit = check.get("timeout_seconds", 120)
        if not isinstance(name, str) or not name.strip() or name in names:
            raise ValueError("Check names must be nonempty and unique")
        names.add(name)
        if not isinstance(argv, list) or not argv or any(not isinstance(x, str) or not x or "\0" in x for x in argv):
            raise ValueError("Each check needs a nonempty argv array")
        if isinstance(limit, bool) or not isinstance(limit, (float, int)) or not math.isfinite(limit) or not 0 < limit <= 3600:
            raise ValueError("Timeouts must be finite and between 0 and 3600 seconds")
    paths = plan.get("protect", [])
    if not isinstance(paths, list) or any(not isinstance(x, str) or not x for x in paths):
        raise ValueError("protect must be an array of relative file paths")
    if len(set(paths)) != len(paths):
        raise ValueError("Protected paths must be unique")
    return plan, sha(raw)


def fingerprint(target, name):
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts or relative == Path("."):
        raise ValueError("Protected paths must stay inside the project")
    current = target
    for index, part in enumerate(relative.parts):
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Protected path contains a symlink: {name}")
        if current.exists() and index < len(relative.parts) - 1 and not current.is_dir():
            raise ValueError(f"Protected path parent is not a directory: {name}")
    if not current.exists():
        return {"kind": "missing"}
    mode = current.stat().st_mode
    if not stat.S_ISREG(mode):
        raise ValueError(f"Protect regular files, not directories or special files: {name}")
    digest = hashlib.sha256()
    with current.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"kind": "file", "sha256": digest.hexdigest(), "mode": stat.S_IMODE(mode)}


def write_new(path, data):
    # Exclusive creation preserves prior receipts and refuses destination symlinks.
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as stream:
        json.dump(data, stream, indent=2)
        stream.write("\n")


def stop_group(process):
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            pass
        if sig == signal.SIGTERM:
            # Reap an exited parent before the second signal (needed on macOS),
            # then still kill the group in case a child ignored SIGTERM.
            try:
                process.wait(timeout=0.2)
            except subprocess.TimeoutExpired:
                pass
    process.wait()


def run_check(check, target, show_output=False):
    started = time.monotonic()
    status, code, problem = "failed", None, None
    with tempfile.TemporaryFile() as output:
        try:
            process = subprocess.Popen(check["argv"], cwd=target, stdin=subprocess.DEVNULL,
                                       stdout=output, stderr=subprocess.STDOUT,
                                       start_new_session=True, shell=False)
            try:
                code = process.wait(timeout=check.get("timeout_seconds", 120))
                status = "passed" if code == 0 else "failed"
            except subprocess.TimeoutExpired:
                stop_group(process)
                code, status = process.returncode, "timed_out"
            except BaseException:
                stop_group(process)
                raise
        except OSError as error:
            status, problem = "could_not_start", type(error).__name__
        output.seek(0)
        digest, size = hashlib.sha256(), 0
        for chunk in iter(lambda: output.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
            if show_output:
                sys.stdout.buffer.write(chunk)
        if show_output:
            sys.stdout.flush()
    return {"name": check["name"], "status": status, "exit_code": code,
            "seconds": round(time.monotonic() - started, 3), "error_type": problem,
            "output_bytes": size, "output_sha256": digest.hexdigest()}


def protected_results(target, before):
    results = []
    for name, original in before.items():
        try:
            unchanged = fingerprint(target, name) == original
            results.append({"path": name, "status": "unchanged" if unchanged else "changed"})
        except (OSError, ValueError):
            results.append({"path": name, "status": "unreadable_or_unsafe"})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("snapshot", "run"))
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--target", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True, help="New local JSON file; never overwritten")
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--show-output", action="store_true", help="Print command output; receipts omit it")
    args = parser.parse_args()
    try:
        target = args.target.resolve(strict=True)
        if not target.is_dir() or os.name != "posix":
            raise ValueError("An existing project directory on macOS or Linux is required")
        if args.output.exists() or args.output.is_symlink() or not args.output.parent.is_dir():
            raise ValueError("Output must be a new file in an existing directory")
        plan, plan_hash = load_plan(args.plan)
        identity = sha(os.fsencode(target))
        # Receipts must not themselves occupy a protected path or the plan.
        reserved = [target / name for name in plan.get("protect", [])] + [args.plan]
        if args.output.resolve() in [p.resolve() for p in reserved]:
            raise ValueError("Output cannot be the plan or a protected path")
        if args.action == "snapshot":
            before = {name: fingerprint(target, name) for name in plan.get("protect", [])}
            write_new(args.output, {"schema": 1, "kind": "verification_baseline",
                                   "project_id": identity, "plan_sha256": plan_hash,
                                   "protected": before})
            print(f"SNAPSHOT  {len(before)} protected file(s); no file contents copied")
            return 0
        if args.baseline is None:
            raise ValueError("run requires --baseline from before the edits")
        baseline = json.loads(args.baseline.read_text())
        if not isinstance(baseline, dict) or any(baseline.get(k) != v for k, v in {
            "schema": 1, "kind": "verification_baseline", "project_id": identity,
            "plan_sha256": plan_hash,
        }.items()):
            raise ValueError("Baseline belongs to another project or plan")
        original = baseline.get("protected")
        if not isinstance(original, dict) or set(original) != set(plan.get("protect", [])):
            raise ValueError("Baseline does not match the protected path list")
        # Include drift before checks, even if a check happens to restore a file.
        prior = protected_results(target, original)
        started = datetime.now(timezone.utc).isoformat()
        checks = [run_check(check, target, args.show_output) for check in plan["checks"]]
        protected = protected_results(target, original)
        try:
            plan_unchanged = sha(args.plan.read_bytes()) == plan_hash
        except OSError:
            plan_unchanged = False
        passed = all(c["status"] == "passed" for c in checks) and all(
            p["status"] == "unchanged" for p in prior + protected) and plan_unchanged
        receipt = {"schema": 1, "kind": "verification_receipt", "started_at": started,
                   "status": "passed" if passed else "failed", "plan_sha256": plan_hash,
                   "checks": checks, "plan_unchanged": plan_unchanged,
                   "protected_before_checks": prior, "protected_after_checks": protected}
        write_new(args.output, receipt)
        for check in checks:
            print(f"{check['status'].upper():<16} {check['name']} (exit {check['exit_code']})")
        for stage, paths in (("before", prior), ("after", protected)):
            for path in paths:
                if path["status"] != "unchanged":
                    print(f"CHANGED          protected path {path['path']} ({stage} checks)")
        if not plan_unchanged:
            print("CHANGED          check plan changed while checks ran")
        print(f"{'PASS' if passed else 'FAIL'}  {sum(c['status'] == 'passed' for c in checks)}/{len(checks)} checks; receipt saved")
        return 0 if passed else 1
    except (OSError, ValueError, TypeError) as error:
        print(f"Verification error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
