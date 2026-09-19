import json
import copy
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch
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


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(dir=".")
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "settings.json"
        self.original = b'{ "nested": {"keep": true, "change": 1}, "unknown": 42 }\n'
        self.path.write_bytes(self.original)

    def assert_unchanged(self, existed=True):
        if existed:
            self.assertEqual(self.path.read_bytes(), self.original)
        else:
            self.assertFalse(self.path.exists())
        self.assertEqual(list(self.path.parent.iterdir()), [self.path] if existed else [])

    def test_recursive_merge_and_replacements(self):
        self.path.write_text(json.dumps({
            "nested": {"deep": {"keep": 1, "change": 2}, "keep": True},
            "list": [1, 2], "nullable": 1, "scalar": 1, "object": {"a": 1},
            "unknown": 42,
        }))
        changes = {"nested": {"deep": {"change": 3}}, "list": [3],
                   "nullable": None, "scalar": {"new": 1}, "object": False}
        before = copy.deepcopy(changes)
        expected = {
            "nested": {"deep": {"keep": 1, "change": 3}, "keep": True},
            "list": [3], "nullable": None, "scalar": {"new": 1},
            "object": False, "unknown": 42,
        }
        self.assertEqual(update_settings(self.path, changes), expected)
        self.assertEqual(json.loads(self.path.read_text()), expected)
        self.assertEqual(changes, before)

    def test_rejects_non_object_roots(self):
        for value in [[], None, 1, "text", True]:
            with self.subTest(value=value):
                self.original = json.dumps(value).encode()
                self.path.write_bytes(self.original)
                with self.assertRaises(ValueError):
                    update_settings(self.path, {})
                self.assert_unchanged()

    def test_rejects_non_object_patches(self):
        for existed in [True, False]:
            if not existed:
                self.path.unlink()
            for value in [[], [("key", 1)], None, 1, "text", True]:
                with self.subTest(existed=existed, value=value):
                    with self.assertRaises(ValueError):
                        update_settings(self.path, value)
                    self.assert_unchanged(existed)

    def test_serialization_failures_preserve_destination(self):
        circular = {}
        circular["self"] = circular
        for existed in [True, False]:
            if not existed:
                self.path.unlink()
            for value in [float("nan"), float("inf"), -float("inf"), object(), circular]:
                with self.subTest(existed=existed, value=type(value).__name__):
                    with self.assertRaises((ValueError, TypeError)):
                        update_settings(self.path, {"nested": {"bad": value}})
                    self.assert_unchanged(existed)

    def test_malformed_json_is_preserved(self):
        self.original = b'{"broken":'
        self.path.write_bytes(self.original)
        with self.assertRaises(ValueError):
            update_settings(self.path, {})
        self.assert_unchanged()

    def test_replacement_failure_cleans_up(self):
        for existed in [True, False]:
            if not existed:
                self.path.unlink()

            def fail_replace(source, destination):
                self.assertEqual(Path(source).parent.resolve(), self.path.parent.resolve())
                self.assertEqual(Path(destination), self.path)
                self.assertEqual(json.loads(Path(source).read_text())["new"], True)
                raise OSError("replacement failed")

            with patch("app.os.replace", side_effect=fail_replace):
                with self.assertRaisesRegex(OSError, "replacement failed"):
                    update_settings(self.path, {"new": True})
            self.assert_unchanged(existed)

    def test_write_failure_cleans_up(self):
        real_temporary_file = tempfile.NamedTemporaryFile

        def failing_temporary_file(*args, **kwargs):
            stream = real_temporary_file(*args, **kwargs)

            def fail_write(value):
                stream.file.write(value[:5])
                raise OSError("write failed")

            stream.write = fail_write
            return stream

        with patch("app.tempfile.NamedTemporaryFile", side_effect=failing_temporary_file):
            with self.assertRaisesRegex(OSError, "write failed"):
                update_settings(self.path, {"new": True})
        self.assert_unchanged()

    @unittest.skipUnless(os.name == "posix", "POSIX permission bits")
    def test_preserves_permissions(self):
        self.path.chmod(0o640)
        update_settings(self.path, {"new": True})
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o640)

    def test_missing_parent_is_not_created(self):
        missing = self.path.parent / "missing"
        with self.assertRaises(FileNotFoundError):
            update_settings(missing / "settings.json", {})
        self.assertFalse(missing.exists())
        self.assert_unchanged()
