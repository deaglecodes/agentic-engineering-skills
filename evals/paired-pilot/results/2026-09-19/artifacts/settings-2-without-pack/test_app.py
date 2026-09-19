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
        original = {
            "ui": {"colors": {"text": "black", "background": "white"}, "size": 12},
            "items": [1, 2], "nullable": "old", "unknown": True,
            "object": {"old": 1}, "scalar": 1,
        }
        patch = {
            "ui": {"colors": {"text": "blue"}}, "items": [3],
            "nullable": None, "object": False, "scalar": {"new": 2},
        }
        snapshot = copy.deepcopy(patch)
        expected = {
            "ui": {"colors": {"text": "blue", "background": "white"}, "size": 12},
            "items": [3], "nullable": None, "unknown": True,
            "object": False, "scalar": {"new": 2},
        }
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            path.write_text(json.dumps(original))
            self.assertEqual(update_settings(path, patch), expected)
            self.assertEqual(json.loads(path.read_text()), expected)
            self.assertEqual(patch, snapshot)

    def test_rejects_non_object_roots_and_patches(self):
        for value in ([], None, "text", 1, True):
            for invalid_root in (True, False):
                with self.subTest(value=value, invalid_root=invalid_root):
                    with tempfile.TemporaryDirectory() as folder:
                        path = Path(folder) / "settings.json"
                        before = json.dumps(value if invalid_root else {}).encode()
                        path.write_bytes(before)
                        with self.assertRaises(ValueError):
                            update_settings(path, {} if invalid_root else value)
                        self.assertEqual(path.read_bytes(), before)
                        self.assertEqual(list(Path(folder).iterdir()), [path])

    def test_serialization_failure_preserves_destination(self):
        for value in (float("nan"), float("inf"), float("-inf"), object()):
            for exists in (True, False):
                with self.subTest(value=value, exists=exists):
                    with tempfile.TemporaryDirectory() as folder:
                        path = Path(folder) / "settings.json"
                        before = b'{ "keep": 42 }\n'
                        if exists:
                            path.write_bytes(before)
                        with self.assertRaises((ValueError, TypeError)):
                            update_settings(path, {"nested": {"bad": value}})
                        self.assertEqual(path.exists(), exists)
                        if exists:
                            self.assertEqual(path.read_bytes(), before)
                        self.assertEqual(list(Path(folder).iterdir()), [path] if exists else [])

    def test_failed_replace_preserves_destination_and_cleans_temp(self):
        for exists in (True, False):
            with self.subTest(exists=exists), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "settings.json"
                before = b'{ "keep": 42 }\n'
                if exists:
                    path.write_bytes(before)

                def fail_replace(source, destination):
                    self.assertEqual(Path(source).parent, path.parent)
                    self.assertEqual(destination, path)
                    self.assertEqual(json.loads(Path(source).read_text())["new"], 1)
                    raise OSError("replacement failed")

                with mock.patch("app.os.replace", side_effect=fail_replace):
                    with self.assertRaisesRegex(OSError, "replacement failed"):
                        update_settings(path, {"new": 1})
                if exists:
                    self.assertEqual(path.read_bytes(), before)
                self.assertEqual(list(Path(folder).iterdir()), [path] if exists else [])

    @unittest.skipUnless(os.name == "posix", "POSIX permissions required")
    def test_preserves_permission_bits(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            path.write_text("{}")
            path.chmod(0o640)
            update_settings(path, {"new": 1})
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o640)

    def test_missing_parent_is_not_created(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "missing" / "settings.json"
            with self.assertRaises(FileNotFoundError):
                update_settings(path, {})
            self.assertFalse(path.parent.exists())
