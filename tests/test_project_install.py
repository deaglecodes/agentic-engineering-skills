"""Exercise the public installer CLI against disposable projects."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
INSTALL = ROOT / "scripts/install.sh"
DESTINATIONS = {
    "codex": "AGENTS.md", "claude": "CLAUDE.md",
    "cursor": ".cursor/rules/agentic-engineering.mdc", "generic": "AGENTIC_ENGINEERING.md",
}


class ProjectInstallTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix="ae-install-test-")
        self.addCleanup(self.scratch.cleanup)
        self.target = Path(self.scratch.name) / "project with spaces"
        self.target.mkdir()

    def run_install(self, *args, success=True):
        result = subprocess.run(
            [str(INSTALL), "--target", str(self.target), *args],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result

    def snapshot(self):
        return {str(p.relative_to(self.target)): p.read_bytes()
                for p in self.target.rglob("*") if p.is_file()}

    def test_fresh_install_each_adapter_and_remove(self):
        for agent, filename in DESTINATIONS.items():
            with self.subTest(agent=agent):
                self.run_install("--agent", agent)
                instruction = self.target / filename
                text = instruction.read_text()
                self.assertIn(".agentic-engineering/pack/skills/ae-core-charter/SKILL.md", text)
                self.assertNotIn("`./scripts/", text)
                self.assertFalse((self.target / ".agentic-engineering/pack/evals/paired-pilot").exists())
                self.assertFalse((self.target / ".agentic-engineering/pack/evals/verification-demo").exists())
                if agent == "cursor":
                    self.assertTrue(text.startswith("---\n"))
                tool = self.target / ".agentic-engineering/pack/scripts/setup-package-age-safety.sh"
                # Prove an installed command actually works from the target directory.
                result = subprocess.run(
                    [str(tool), "--mode=project-local", "--target", ".", "--dry-run"],
                    cwd=self.target, capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.run_install("--uninstall")
                self.assertFalse(instruction.exists())
                self.assertFalse((self.target / ".agentic-engineering").exists())

    def test_preserves_existing_bytes_and_later_user_additions(self):
        original = b"# Team rules\r\nKeep our existing conventions."
        path = self.target / "AGENTS.md"
        path.write_bytes(original)
        path.chmod(0o640)
        self.run_install("--agent", "codex")
        self.assertTrue(path.read_bytes().startswith(original))
        self.assertEqual(path.stat().st_mode & 0o777, 0o640)
        added = b"\n# New project rule\nKeep this too.\n"
        with path.open("ab") as stream:
            stream.write(added)
        # Private project instructions must not be copied into installer state.
        state = (self.target / ".agentic-engineering/install.json").read_text()
        self.assertNotIn("Keep our existing conventions", state)
        self.run_install("--uninstall")
        self.assertEqual(path.read_bytes(), original + added)

    def test_install_and_uninstall_dry_runs_change_nothing(self):
        (self.target / "CLAUDE.md").write_text("Existing instructions\n")
        before = self.snapshot()
        self.run_install("--agent", "claude", "--dry-run")
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.target / ".agentic-engineering").exists())
        self.run_install("--agent", "claude")
        before = self.snapshot()
        self.run_install("--uninstall", "--dry-run")
        self.assertEqual(self.snapshot(), before)

    def test_reinstall_is_idempotent(self):
        self.run_install("--agent", "codex")
        before = self.snapshot()
        result = self.run_install("--agent", "codex")
        self.assertIn("Already installed", result.stdout)
        self.assertEqual(self.snapshot(), before)
        self.run_install("--agent", "claude", success=False)
        self.assertEqual(self.snapshot(), before)

    def test_edited_pack_or_extra_file_blocks_removal(self):
        self.run_install("--agent", "codex")
        path = self.target / ".agentic-engineering/pack/README.md"
        path.write_text(path.read_text() + "\nMy changes\n")
        before = self.snapshot()
        self.run_install("--uninstall", success=False)
        self.assertEqual(self.snapshot(), before)
        path.write_bytes((ROOT / "README.md").read_bytes())
        (path.parent / "personal-notes.txt").write_text("Keep me\n")
        before = self.snapshot()
        self.run_install("--uninstall", success=False)
        self.assertEqual(self.snapshot(), before)

    def test_edited_instruction_block_blocks_removal(self):
        self.run_install("--agent", "claude")
        path = self.target / "CLAUDE.md"
        path.write_text(path.read_text().replace("## Operating Style", "## My Operating Style"))
        before = self.snapshot()
        self.run_install("--uninstall", success=False)
        self.assertEqual(self.snapshot(), before)

    def test_refuses_existing_cursor_rule_and_unmanaged_pack(self):
        path = self.target / DESTINATIONS["cursor"]
        path.parent.mkdir(parents=True)
        path.write_text("My rule\n")
        before = self.snapshot()
        self.run_install("--agent", "cursor", success=False)
        self.assertEqual(self.snapshot(), before)
        pack = self.target / ".agentic-engineering/pack"
        pack.mkdir(parents=True)
        (pack / "notes.md").write_text("Keep this\n")
        before = self.snapshot()
        self.run_install("--agent", "codex", success=False)
        self.assertEqual(self.snapshot(), before)

    def test_refuses_symlinked_instruction_and_managed_directory(self):
        outside = Path(self.scratch.name) / "outside"
        outside.mkdir()
        sentinel = outside / "rules.md"
        sentinel.write_text("Do not change\n")
        instruction = self.target / "AGENTS.md"
        instruction.symlink_to(sentinel)
        self.run_install("--agent", "codex", success=False)
        self.assertEqual(sentinel.read_text(), "Do not change\n")
        instruction.unlink()
        (self.target / ".agentic-engineering").symlink_to(outside, target_is_directory=True)
        self.run_install("--agent", "codex", success=False)
        self.assertEqual(list(outside.iterdir()), [sentinel])

    def test_refuses_symlinked_cursor_parent(self):
        outside = Path(self.scratch.name) / "outside"
        outside.mkdir()
        (self.target / ".cursor").symlink_to(outside, target_is_directory=True)
        self.run_install("--agent", "cursor", success=False)
        self.assertEqual(list(outside.iterdir()), [])

    def test_preserves_separate_package_settings_and_empty_instruction(self):
        (self.target / "AGENTS.md").touch()
        base = self.target / ".agentic-engineering"
        base.mkdir()
        settings = base / "package-safety"
        settings.mkdir()
        (settings / "pip.conf").write_text("[global]\nuploaded-prior-to = P7D\n")
        before = self.snapshot()
        self.run_install("--agent", "codex")
        self.run_install("--uninstall")
        self.assertEqual(self.snapshot(), before)

    def test_rejects_manifest_path_escape(self):
        self.run_install("--agent", "codex")
        path = self.target / ".agentic-engineering/install.json"
        state = json.loads(path.read_text())
        state["instruction"] = "../outside.md"
        path.write_text(json.dumps(state))
        before = self.snapshot()
        self.run_install("--uninstall", success=False)
        self.assertEqual(self.snapshot(), before)

    def test_unmanaged_marker_and_missing_target_fail_without_writes(self):
        path = self.target / "AGENTS.md"
        path.write_text("<!-- agentic-engineering:begin -->\n")
        before = self.snapshot()
        self.run_install("--agent", "codex", success=False)
        self.assertEqual(self.snapshot(), before)
        self.target = self.target / "does not exist"
        self.run_install("--agent", "codex", success=False)
        self.assertFalse(self.target.exists())


if __name__ == "__main__":
    unittest.main()
