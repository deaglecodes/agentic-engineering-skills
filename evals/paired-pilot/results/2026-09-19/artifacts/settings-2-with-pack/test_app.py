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
        self.original = b'{ "nested": {"keep": true, "change": 1}, "unknown": 7 }\n'

    def assert_unchanged(self, exists):
        if exists:
            self.assertEqual(self.path.read_bytes(), self.original)
        else:
            self.assertFalse(self.path.exists())
        self.assertEqual(list(self.path.parent.iterdir()), [self.path] if exists else [])

    def test_recursive_merge_and_replacement_values(self):
        current = {
            "nested": {"deep": {"keep": 1, "change": 2}, "sibling": True},
            "list": [1, 2], "nullable": {"old": 1}, "scalar": 3,
            "object": {"old": 1}, "unknown": "retained",
        }
        changes = {
            "nested": {"deep": {"change": 4}}, "list": [3],
            "nullable": None, "scalar": {"new": 2}, "object": False,
        }
        before = copy.deepcopy(changes)
        self.path.write_text(json.dumps(current))
        expected = {
            "nested": {"deep": {"keep": 1, "change": 4}, "sibling": True},
            "list": [3], "nullable": None, "scalar": {"new": 2},
            "object": False, "unknown": "retained",
        }
        self.assertEqual(update_settings(self.path, changes), expected)
        self.assertEqual(json.loads(self.path.read_text()), expected)
        self.assertEqual(changes, before)

    def test_rejects_non_object_roots(self):
        for value in (None, [], "text", 1, True):
            with self.subTest(value=value):
                original = json.dumps(value).encode()
                self.path.write_bytes(original)
                with self.assertRaises(ValueError):
                    update_settings(self.path, {})
                self.assertEqual(self.path.read_bytes(), original)

    def test_invalid_patches_leave_destination_unchanged(self):
        circular = {}
        circular["self"] = circular
        cases = [
            (value, ValueError) for value in (None, [], "text", 1, True)
        ] + [
            ({"nested": {"value": value}}, ValueError)
            for value in (float("nan"), float("inf"), -float("inf"))
        ] + [({"bad": object()}, TypeError), (circular, ValueError)]
        for exists in (False, True):
            for changes, error in cases:
                with self.subTest(exists=exists, error=error, changes=changes):
                    if exists:
                        self.path.write_bytes(self.original)
                    with self.assertRaises(error):
                        update_settings(self.path, changes)
                    self.assert_unchanged(exists)

    def test_invalid_existing_json_is_preserved(self):
        for contents in (b'{"broken":', b'{"value": NaN}', b'{"value": Infinity}'):
            with self.subTest(contents=contents):
                self.path.write_bytes(contents)
                with self.assertRaises(ValueError):
                    update_settings(self.path, {"new": 1})
                self.assertEqual(self.path.read_bytes(), contents)

    def test_atomic_replacement_and_permissions(self):
        self.path.write_bytes(self.original)
        self.path.chmod(0o640)
        replace = os.replace

        def inspect_replace(source, destination):
            self.assertEqual(Path(source).parent.resolve(), self.path.parent.resolve())
            self.assertEqual(self.path.read_bytes(), self.original)
            self.assertEqual(json.loads(Path(source).read_text())["new"], 2)
            self.assertEqual(stat.S_IMODE(Path(source).stat().st_mode), 0o640)
            replace(source, destination)

        with patch("app.os.replace", side_effect=inspect_replace) as mocked:
            update_settings(self.path, {"new": 2})
        mocked.assert_called_once()
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o640)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_replacement_failure_cleans_up(self):
        for exists in (False, True):
            with self.subTest(exists=exists):
                if exists:
                    self.path.write_bytes(self.original)
                with patch("app.os.replace", side_effect=OSError("replace failed")):
                    with self.assertRaisesRegex(OSError, "replace failed"):
                        update_settings(self.path, {"new": 2})
                self.assert_unchanged(exists)

    def test_write_failure_cleans_up(self):
        factory = tempfile.NamedTemporaryFile

        def failing_file(*args, **kwargs):
            stream = factory(*args, **kwargs)

            def fail_write(contents):
                stream.file.write(contents[:3])
                raise OSError("write failed")

            stream.write = fail_write
            return stream

        for exists in (False, True):
            with self.subTest(exists=exists):
                if exists:
                    self.path.write_bytes(self.original)
                with patch("app.tempfile.NamedTemporaryFile", side_effect=failing_file):
                    with self.assertRaisesRegex(OSError, "write failed"):
                        update_settings(self.path, {"new": 2})
                self.assert_unchanged(exists)

    def test_missing_parent_is_not_created(self):
        path = self.path.parent / "missing" / "settings.json"
        with self.assertRaises(FileNotFoundError):
            update_settings(path, {"new": 2})
        self.assertFalse(path.parent.exists())
