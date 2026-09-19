import json
import copy
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest import mock
from app import update_settings


class VisibleTests(unittest.TestCase):
    def test_new_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            self.assertEqual(update_settings(path, {"theme": "dark"}), {"theme": "dark"})
            self.assertEqual(json.loads(path.read_text()), {"theme": "dark"})

    def test_retains_other_top_level_keys(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            path.write_text('{"theme": "light", "language": "en"}')
            self.assertEqual(update_settings(path, {"theme": "dark"})["language"], "en")

    def test_recursive_merge_and_replacement_without_mutating_patch(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            path.write_text(json.dumps({
                "ui": {"colors": {"text": "black", "background": "white"},
                       "font": "serif"},
                "list": [1, 2], "nullable": True, "unknown": 42,
                "scalar": 3, "object": {"old": True},
            }))
            patch = {"ui": {"colors": {"text": "blue"}}, "list": [3],
                     "nullable": None, "scalar": {"new": True}, "object": False}
            original_patch = copy.deepcopy(patch)
            expected = {
                "ui": {"colors": {"text": "blue", "background": "white"},
                       "font": "serif"},
                "list": [3], "nullable": None, "unknown": 42,
                "scalar": {"new": True}, "object": False,
            }
            self.assertEqual(update_settings(path, patch), expected)
            self.assertEqual(json.loads(path.read_text()), expected)
            self.assertEqual(patch, original_patch)

    def test_invalid_roots_leave_destination_unchanged(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            for root in ([], None, 1, "text", True):
                with self.subTest(root=root):
                    original = json.dumps(root).encode()
                    path.write_bytes(original)
                    with self.assertRaises(ValueError):
                        update_settings(path, {})
                    self.assertEqual(path.read_bytes(), original)
            for exists in (False, True):
                for patch in ([], None, 1, "text", True):
                    with self.subTest(exists=exists, patch=patch):
                        path.unlink(missing_ok=True)
                        if exists:
                            path.write_bytes(b'{"keep": true}\n')
                        with self.assertRaises(ValueError):
                            update_settings(path, patch)
                        self.assertEqual(path.exists(), exists)
                        if exists:
                            self.assertEqual(path.read_bytes(), b'{"keep": true}\n')

    def test_serialization_failures_preserve_destination(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            for exists in (False, True):
                for value in (float("nan"), float("inf"), -float("inf"), object()):
                    with self.subTest(exists=exists, value=value):
                        path.unlink(missing_ok=True)
                        if exists:
                            path.write_bytes(b'{ "keep": true }\n')
                        with self.assertRaises((ValueError, TypeError)):
                            update_settings(path, {"nested": {"bad": value}})
                        self.assertEqual(path.exists(), exists)
                        if exists:
                            self.assertEqual(path.read_bytes(), b'{ "keep": true }\n')
                        self.assertEqual(set(Path(folder).iterdir()), {path} if exists else set())

    def test_replacement_failure_cleans_temporary_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            for exists in (False, True):
                with self.subTest(exists=exists):
                    if exists:
                        path.write_bytes(b'{"keep": true}\n')
                    def fail_replace(source, destination):
                        self.assertEqual(Path(source).parent, path.parent)
                        self.assertEqual(destination, path)
                        self.assertEqual(json.loads(Path(source).read_text())["new"], 1)
                        raise OSError("replacement failed")
                    with mock.patch("app.os.replace", side_effect=fail_replace):
                        with self.assertRaisesRegex(OSError, "replacement failed"):
                            update_settings(path, {"new": 1})
                    self.assertEqual(path.exists(), exists)
                    if exists:
                        self.assertEqual(path.read_bytes(), b'{"keep": true}\n')
                    self.assertEqual(set(Path(folder).iterdir()), {path} if exists else set())

    def test_atomic_replacement_preserves_permissions(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            path.write_text('{}')
            path.chmod(0o640)
            with mock.patch("app.os.replace", wraps=os.replace) as replace:
                update_settings(path, {"saved": True})
            replace.assert_called_once()
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o640)
            self.assertEqual(json.loads(path.read_text()), {"saved": True})
            self.assertEqual(list(Path(folder).iterdir()), [path])

    def test_missing_parent_is_not_created(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "missing" / "settings.json"
            with self.assertRaises(FileNotFoundError):
                update_settings(path, {})
            self.assertFalse(path.parent.exists())
