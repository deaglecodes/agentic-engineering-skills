"""Frozen correctness tests. Run externally; never place this file in an agent workspace."""
import argparse
import copy
import importlib.util
import io
import json
import os
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

APP = None


class Money(unittest.TestCase):
    def test_half_cent_rounds_up(self):
        self.assertEqual(APP.build_invoice([{"unit_price": "1.005", "quantity": 1}])["total"], "1.01")

    def test_round_extended_line_not_unit(self):
        self.assertEqual(APP.build_invoice([{"unit_price": "1.005", "quantity": 2}])["total"], "2.01")

    def test_round_each_line_before_sum(self):
        lines = [{"unit_price": "0.005", "quantity": 1}] * 2
        self.assertEqual(APP.build_invoice(lines)["subtotal"], "0.02")

    def test_tax_rounds_half_up(self):
        self.assertEqual(APP.build_invoice([{"unit_price": "0.10", "quantity": 1}], tax_rate="0.05")["tax"], "0.01")

    def test_discount_rounds_and_applies_before_tax(self):
        self.assertEqual(APP.build_invoice([{"unit_price": "10", "quantity": 1}], "1.005", "0.10"),
                         {"subtotal": "10.00", "discount": "1.01", "tax": "0.90", "total": "9.89"})

    def test_invalid_money_and_excess_discount(self):
        for value in ["-1", "NaN", "Infinity", "not money"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                APP.build_invoice([{"unit_price": value, "quantity": 1}])
        with self.assertRaises(ValueError):
            APP.build_invoice([{"unit_price": "1", "quantity": 1}], "2")
        for value in ["-0.1", "NaN", "Infinity"]:
            with self.subTest(tax=value), self.assertRaises(ValueError):
                APP.build_invoice([{"unit_price": "1", "quantity": 1}], tax_rate=value)

    def test_invalid_quantities(self):
        for quantity in [0, -1, 1.5, True, "2"]:
            with self.subTest(quantity=quantity), self.assertRaises(ValueError):
                APP.build_invoice([{"unit_price": "1", "quantity": quantity}])

    def test_inputs_unchanged_and_large_decimal(self):
        lines = [{"unit_price": "9007199254740993.01", "quantity": 1}]
        before = copy.deepcopy(lines)
        self.assertEqual(APP.build_invoice(lines)["subtotal"], "9007199254740993.01")
        self.assertEqual(lines, before)


def event(identifier, day=1, team="A"):
    return {"id": identifier, "team": team, "created_at": f"2026-01-{day:02d}T00:00:00Z"}


class Pagination(unittest.TestCase):
    def test_tie_order(self):
        rows = [event("a"), event("c"), event("b")]
        self.assertEqual([e["id"] for e in APP.list_events(rows, "A")["items"]], ["c", "b"])

    def test_complete_tie_traversal(self):
        rows = [event(str(i)) for i in range(7)]
        cursor = None
        seen = []
        for _ in range(10):
            page = APP.list_events(rows, "A", limit=2, cursor=cursor)
            seen.extend(e["id"] for e in page["items"])
            cursor = page["next_cursor"]
            if cursor is None:
                break
        self.assertEqual(seen, [str(i) for i in reversed(range(7))])

    def test_deleted_anchor(self):
        rows = [event("a"), event("b"), event("c"), event("d")]
        first = APP.list_events(rows, "A", limit=2)
        remaining = [e for e in rows if e["id"] != first["items"][-1]["id"]]
        page = APP.list_events(remaining, "A", limit=2, cursor=first["next_cursor"])
        self.assertEqual([e["id"] for e in page["items"]], ["b", "a"])

    def test_newer_insert_does_not_repeat(self):
        rows = [event("a"), event("b"), event("c"), event("d")]
        first = APP.list_events(rows, "A", limit=2)
        page = APP.list_events(rows + [event("z", 2)], "A", limit=2, cursor=first["next_cursor"])
        self.assertEqual([e["id"] for e in page["items"]], ["b", "a"])

    def test_cursor_scoped_to_team(self):
        rows = [event("a"), event("b"), event("x", team="B")]
        cursor = APP.list_events(rows, "A", limit=1)["next_cursor"]
        with self.assertRaises(ValueError):
            APP.list_events(rows, "B", cursor=cursor)

    def test_invalid_cursor(self):
        for cursor in ["not a cursor", "e30=", "bnVsbA==", "W10="]:
            with self.subTest(cursor=cursor), self.assertRaises(ValueError):
                APP.list_events([event("a")], "A", cursor=cursor)

    def test_invalid_limit(self):
        for limit in [0, -1, 101, True, 1.5, "2"]:
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                APP.list_events([event("a")], "A", limit=limit)

    def test_team_filter_no_mutation_and_last_cursor(self):
        rows = [event("b", team="B"), event("a"), event("c")]
        before = copy.deepcopy(rows)
        page = APP.list_events(rows, "A", limit=2)
        self.assertEqual([e["id"] for e in page["items"]], ["c", "a"])
        self.assertIsNone(page["next_cursor"])
        self.assertEqual(rows, before)


class Settings(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "settings.json"
        self.original = '{"ui": {"theme": "light", "size": 12}, "unknown": 7}\n'
        self.path.write_text(self.original)

    def test_deep_merge(self):
        result = APP.update_settings(self.path, {"ui": {"theme": "dark"}})
        self.assertEqual(result, {"ui": {"theme": "dark", "size": 12}, "unknown": 7})
        self.assertEqual(json.loads(self.path.read_text()), result)

    def test_lists_null_and_type_changes(self):
        result = APP.update_settings(self.path, {"ui": None, "items": [1, 2]})
        self.assertIsNone(result["ui"])
        result = APP.update_settings(self.path, {"ui": {"new": True}, "items": [3]})
        self.assertEqual(result["ui"], {"new": True})
        self.assertEqual(result["items"], [3])

    def test_invalid_root_and_patch(self):
        for root in [[], 3, None]:
            self.path.write_text(json.dumps(root))
            before = self.path.read_bytes()
            with self.subTest(root=root), self.assertRaises(ValueError):
                APP.update_settings(self.path, {})
            self.assertEqual(self.path.read_bytes(), before)
        self.path.write_text(self.original)
        with self.assertRaises(ValueError):
            APP.update_settings(self.path, [])
        self.assertEqual(self.path.read_text(), self.original)

    def test_nonserializable_preserves_original(self):
        with self.assertRaises((TypeError, ValueError)):
            APP.update_settings(self.path, {"bad": {1, 2}})
        self.assertEqual(self.path.read_text(), self.original)
        self.assertEqual(sorted(p.name for p in self.path.parent.iterdir()), ["settings.json"])

    def test_nonfinite_json_rejected(self):
        for value in [float("nan"), float("inf")]:
            with self.subTest(value=value), self.assertRaises((ValueError, TypeError)):
                APP.update_settings(self.path, {"bad": value})
            self.assertEqual(self.path.read_text(), self.original)

    def test_new_file_failure_leaves_no_files(self):
        self.path.unlink()
        with self.assertRaises((TypeError, ValueError)):
            APP.update_settings(self.path, {"bad": {1}})
        self.assertEqual(list(self.path.parent.iterdir()), [])

    def test_replace_failure_preserves_and_cleans(self):
        # Contract explicitly requires os.replace (directly or via pathlib).
        with patch.object(os, "replace", side_effect=OSError("simulated disk failure")):
            with self.assertRaises(OSError):
                APP.update_settings(self.path, {"ui": {"theme": "dark"}})
        self.assertEqual(self.path.read_text(), self.original)
        self.assertEqual(sorted(p.name for p in self.path.parent.iterdir()), ["settings.json"])

    def test_permissions_and_patch_unchanged(self):
        self.path.chmod(0o640)
        patch_data = {"ui": {"theme": "dark"}, "items": [1, 2]}
        before = copy.deepcopy(patch_data)
        APP.update_settings(self.path, patch_data)
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o640)
        self.assertEqual(patch_data, before)


CLASSES = {"money": Money, "pagination": Pagination, "settings": Settings}


def grade(task, workspace):
    global APP
    spec = importlib.util.spec_from_file_location("app", Path(workspace) / "app.py")
    APP = importlib.util.module_from_spec(spec)
    sys.modules["app"] = APP
    try:
        spec.loader.exec_module(APP)
    except Exception as error:
        return {"passed": 0, "total": 8, "failures": [f"import: {type(error).__name__}"]}
    output = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CLASSES[task])
    result = unittest.TextTestRunner(stream=output).run(suite)
    # Count methods, not subtest failure records, so the denominator stays fixed.
    failed = sorted({case.id().split(" (")[0] for case, _ in result.failures + result.errors})
    return {"passed": result.testsRun - len(failed), "total": result.testsRun,
            "failures": failed, "output": output.getvalue()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task", choices=CLASSES)
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()
    print(json.dumps(grade(args.task, args.workspace)))
