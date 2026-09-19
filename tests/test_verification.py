"""Exercise receipts against real commands and changes in disposable projects."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "scripts/verify.sh"


def check(name, code, timeout=5):
    return {"name": name, "argv": [sys.executable, "-B", "-c", code], "timeout_seconds": timeout}


class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix="ae-verify-")
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.project = self.root / "project with spaces"
        self.project.mkdir()
        (self.project / "notes.md").write_text("Uncommitted user work\n")
        self.plan = self.project / "checks.json"
        self.baseline = self.root / "before.json"
        self.output = self.root / "receipt.json"
        self.write_plan([check("unit", "print('all checks passed')")])

    def write_plan(self, checks, protect=None):
        self.plan.write_text(json.dumps({"schema": 1, "checks": checks,
                                        "protect": ["notes.md"] if protect is None else protect}))

    def call(self, action, expected=0, tool=TOOL, **kwargs):
        args = [str(tool), action, "--target", str(self.project), "--plan", str(self.plan),
                "--output", str(self.baseline if action == "snapshot" else self.output)]
        if action == "run":
            args.extend(["--baseline", str(self.baseline)])
        result = subprocess.run(args, capture_output=True, text=True, timeout=15, **kwargs)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def receipt(self):
        return json.loads(self.output.read_text())

    def test_success_receipt_omits_file_contents_and_command_output(self):
        marker = "private-marker-for-fixture"
        self.write_plan([check("unit", f"print({marker!r})")])
        self.call("snapshot")
        result = self.call("run")
        self.assertEqual(self.receipt()["status"], "passed")
        self.assertNotIn(marker, self.output.read_text() + result.stdout)
        self.assertNotIn("Uncommitted user work", self.baseline.read_text())
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o600)

    def test_first_failure_cannot_be_hidden_by_later_success(self):
        self.write_plan([check("unit", "raise SystemExit(7)"), check("lint", "print('ok')")])
        self.call("snapshot")
        self.call("run", expected=1)
        self.assertEqual([c["exit_code"] for c in self.receipt()["checks"]], [7, 0])
        self.assertEqual(self.receipt()["status"], "failed")

    def test_edit_delete_create_and_mode_changes_are_reported(self):
        for operation in ("edit", "delete", "create", "mode"):
            with self.subTest(operation=operation):
                path = self.project / "notes.md"
                path.write_text("User work\n")
                path.chmod(0o600)
                if operation == "create":
                    path.unlink()
                self.call("snapshot")
                if operation in ("edit", "create"):
                    path.write_text("Changed\n")
                elif operation == "delete":
                    path.unlink()
                else:
                    path.chmod(0o640)
                self.call("run", expected=1)
                self.assertEqual(self.receipt()["protected_before_checks"][0]["status"], "changed")
                self.baseline.unlink()
                self.output.unlink()

    def test_command_that_changes_protected_file_is_caught(self):
        self.write_plan([check("unit", "from pathlib import Path; Path('notes.md').write_text('oops')")])
        self.call("snapshot")
        self.call("run", expected=1)
        self.assertEqual(self.receipt()["checks"][0]["status"], "passed")
        self.assertEqual(self.receipt()["protected_after_checks"][0]["status"], "changed")

    def test_restore_during_checks_does_not_hide_initial_drift(self):
        self.write_plan([check("unit", "from pathlib import Path; Path('notes.md').write_text('Uncommitted user work\\n')")])
        self.call("snapshot")
        (self.project / "notes.md").write_text("Changed before checks")
        self.call("run", expected=1)
        self.assertEqual(self.receipt()["protected_after_checks"][0]["status"], "unchanged")

    def test_timeout_and_missing_executable_are_not_passes(self):
        self.write_plan([check("hang", "import time; time.sleep(20)", timeout=0.1),
                         {"name": "missing", "argv": ["/nonexistent/ae-fixture-tool"]}])
        self.call("snapshot")
        self.call("run", expected=1)
        self.assertEqual([c["status"] for c in self.receipt()["checks"]], ["timed_out", "could_not_start"])

    def test_plan_or_project_mismatch_runs_no_commands(self):
        self.call("snapshot")
        original = self.plan.read_text()
        self.plan.write_text(original + "\n")
        self.call("run", expected=2)
        self.assertFalse(self.output.exists())
        self.plan.write_text(original)
        self.project.rename(self.root / "renamed project")
        self.project = self.root / "renamed project"
        self.plan = self.project / "checks.json"
        self.call("run", expected=2)

    def test_timeout_stops_child_that_ignores_termination(self):
        child = "import signal,time; from pathlib import Path; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(1); Path('late-write').touch()"
        parent = f"import subprocess,sys,time; subprocess.Popen([sys.executable,'-c',{child!r}]); time.sleep(20)"
        self.write_plan([check("process tree", parent, timeout=0.3)])
        self.call("snapshot")
        self.call("run", expected=1)
        self.assertEqual(self.receipt()["checks"][0]["status"], "timed_out")
        time.sleep(1)
        self.assertFalse((self.project / "late-write").exists())

    def test_plan_mutation_during_check_fails_receipt(self):
        self.write_plan([check("unit", "from pathlib import Path; Path('checks.json').write_text('{}')")])
        self.call("snapshot")
        self.call("run", expected=1)
        self.assertFalse(self.receipt()["plan_unchanged"])

    def test_symlink_replacement_is_reported_without_reading_target(self):
        self.call("snapshot")
        path = self.project / "notes.md"
        path.unlink()
        outside = self.root / "outside"
        outside.write_text("Private outside file")
        path.symlink_to(outside)
        self.call("run", expected=1)
        self.assertEqual(self.receipt()["protected_after_checks"][0]["status"], "unreadable_or_unsafe")
        self.assertEqual(outside.read_text(), "Private outside file")

    def test_unsafe_protected_paths_rejected_at_snapshot(self):
        for name in ("../outside", str(self.root / "outside"), "."):
            with self.subTest(name=name):
                self.write_plan([check("unit", "pass")], [name])
                self.call("snapshot", expected=2)
                self.assertFalse(self.baseline.exists())

    def test_existing_outputs_and_symlinks_not_overwritten(self):
        self.call("snapshot")
        original = self.baseline.read_bytes()
        self.call("snapshot", expected=2)
        self.assertEqual(self.baseline.read_bytes(), original)
        self.output.symlink_to(self.baseline)
        self.call("run", expected=2)
        self.assertEqual(self.baseline.read_bytes(), original)

    def test_invalid_plans_rejected_before_execution(self):
        invalid = [[], [check("same", "pass"), check("same", "pass")],
                   [check("unit", "pass", timeout=float("nan"))],
                   [{"name": "unit", "argv": "python3 -m unittest"}]]
        for checks in invalid:
            with self.subTest(checks=checks):
                self.write_plan(checks)
                self.call("snapshot", expected=2)
                self.assertFalse(self.baseline.exists())

    def test_argv_does_not_interpret_shell_operators(self):
        self.write_plan([{"name": "args", "argv": [sys.executable, "-B", "-c",
            "import sys; assert sys.argv[1] == '; touch unwanted'", "; touch unwanted"]}])
        self.call("snapshot")
        self.call("run")
        self.assertFalse((self.project / "unwanted").exists())

    def test_installed_runner_works_from_target_project(self):
        subprocess.run([str(ROOT / "scripts/install.sh"), "--agent", "codex", "--target", str(self.project)],
                       check=True, capture_output=True, text=True)
        tool = self.project / ".agentic-engineering/pack/scripts/verify.sh"
        self.call("snapshot", tool=tool)
        self.call("run", tool=tool)


if __name__ == "__main__":
    unittest.main()
