import base64
import copy
import json
import unittest
from app import list_events


class VisibleTests(unittest.TestCase):
    def test_two_pages(self):
        rows = [{"id": str(i), "team": "A", "created_at": f"2026-01-0{i}T00:00:00Z"} for i in range(1, 4)]
        first = list_events(rows, "A")
        self.assertEqual([x["id"] for x in first["items"]], ["3", "2"])
        self.assertEqual([x["id"] for x in list_events(rows, "A", cursor=first["next_cursor"])["items"]], ["1"])

    def test_empty(self):
        self.assertEqual(list_events([], "A"), {"items": [], "next_cursor": None})

    def test_ties_across_pages_and_input_preservation(self):
        rows = [
            {"id": ident, "team": "A", "created_at": "2026-01-02T00:00:00Z"}
            for ident in ["2", "10", "z", "a", "1"]
        ]
        rows += [
            {"id": "other", "team": "B", "created_at": "2026-01-03T00:00:00Z"},
            {"id": "old", "team": "A", "created_at": "2026-01-01T00:00:00Z"},
        ]
        original = copy.deepcopy(rows)
        for limit in [1, 2, 3, 6, 100]:
            with self.subTest(limit=limit):
                cursor = None
                seen = []
                for _ in range(len(rows) + 1):
                    result = list_events(rows, "A", limit, cursor)
                    seen.extend(event["id"] for event in result["items"])
                    cursor = result["next_cursor"]
                    if cursor is None:
                        break
                    self.assertEqual(len(result["items"]), limit)
                    self.assertLess(len(seen), 6)
                self.assertIsNone(cursor)
                self.assertEqual(seen, ["z", "a", "2", "10", "1", "old"])
                self.assertEqual(rows, original)

    def test_deleted_anchor(self):
        rows = [
            {"id": ident, "team": "A", "created_at": "2026-01-02T00:00:00Z"}
            for ident in ["a", "d", "b", "c"]
        ]
        first = list_events(rows, "A")
        self.assertEqual([e["id"] for e in first["items"]], ["d", "c"])
        rows = [e for e in rows if e["id"] != "c"]
        second = list_events(rows, "A", cursor=first["next_cursor"])
        self.assertEqual([e["id"] for e in second["items"]], ["b", "a"])
        self.assertIsNone(second["next_cursor"])
        self.assertEqual(list_events([], "A", cursor=first["next_cursor"]),
                         {"items": [], "next_cursor": None})

    def test_invalid_limits(self):
        for limit in [True, False, 0, -1, 101, 2.0, "2", None, [], {}]:
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                list_events([], "A", limit=limit)

    def test_invalid_cursors(self):
        valid = {"team": "A", "created_at": "2026-01-01T00:00:00Z", "id": "a"}
        bad_payloads = [
            None, [], 1, "text", {},
            {"created_at": valid["created_at"]},
            dict(valid, team="B"), dict(valid, id=1),
            dict(valid, created_at=None), dict(valid, created_at="invalid"),
            dict(valid, created_at="2026-01-01T00:00:00"),
            dict(valid, extra="unexpected"),
        ]
        cursors = ["", "%%%", "é", "e30", False, 0, [], {}, b"e30="]
        cursors += [base64.urlsafe_b64encode(json.dumps(p).encode()).decode()
                    for p in bad_payloads]
        cursors += [base64.urlsafe_b64encode(p).decode() for p in [b"not json", b"\xff"]]
        for cursor in cursors:
            with self.subTest(cursor=cursor), self.assertRaises(ValueError):
                list_events([], "A", cursor=cursor)

    def test_generated_cursor_rejects_other_team(self):
        rows = [{"id": str(i), "team": "A", "created_at": "2026-01-01T00:00:00Z"}
                for i in range(3)]
        cursor = list_events(rows, "A")["next_cursor"]
        with self.assertRaises(ValueError):
            list_events(rows, "B", cursor=cursor)
