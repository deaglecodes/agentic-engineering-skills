import json
from pathlib import Path
import tempfile
import unittest
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
