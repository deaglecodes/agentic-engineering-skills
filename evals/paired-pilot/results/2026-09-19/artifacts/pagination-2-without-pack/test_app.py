import unittest
import base64
import copy
import json
from app import list_events


class VisibleTests(unittest.TestCase):
    def test_two_pages(self):
        rows = [{"id": str(i), "team": "A", "created_at": f"2026-01-0{i}T00:00:00Z"} for i in range(1, 4)]
        first = list_events(rows, "A")
        self.assertEqual([x["id"] for x in first["items"]], ["3", "2"])
        self.assertEqual([x["id"] for x in list_events(rows, "A", cursor=first["next_cursor"])["items"]], ["1"])

    def test_empty(self):
        self.assertEqual(list_events([], "A"), {"items": [], "next_cursor": None})

    def test_ties_across_pages_are_lexicographic_and_do_not_mutate(self):
        rows = [
            {"id": id_, "team": "A", "created_at": "2026-01-02T00:00:00Z"}
            for id_ in ["2", "10", "a", "9", "b"]
        ]
        rows.extend([
            {"id": "other", "team": "B", "created_at": "2026-01-03T00:00:00Z"},
            {"id": "old", "team": "A", "created_at": "2026-01-01T00:00:00Z"},
        ])
        original = copy.deepcopy(rows)
        for limit in [1, 2, 3, 100]:
            with self.subTest(limit=limit):
                cursor = None
                ids = []
                for _ in range(len(rows) + 1):
                    page = list_events(rows, "A", limit, cursor)
                    ids.extend(row["id"] for row in page["items"])
                    cursor = page["next_cursor"]
                    if cursor is None:
                        break
                else:
                    self.fail("Pagination did not terminate")
                self.assertEqual(ids, ["b", "a", "9", "2", "10", "old"])
                self.assertEqual(rows, original)

    def test_deleted_anchor_and_reordered_input(self):
        rows = [
            {"id": id_, "team": "A", "created_at": "2026-01-02T00:00:00Z"}
            for id_ in ["a", "b", "c", "d"]
        ]
        first = list_events(rows, "A")
        self.assertEqual([row["id"] for row in first["items"]], ["d", "c"])
        remaining = [row for row in reversed(rows) if row["id"] != "c"]
        second = list_events(remaining, "A", cursor=first["next_cursor"])
        self.assertEqual([row["id"] for row in second["items"]], ["b", "a"])
        self.assertIsNone(second["next_cursor"])
        self.assertEqual(list_events([], "A", cursor=first["next_cursor"]),
                         {"items": [], "next_cursor": None})

    def test_invalid_limits(self):
        for limit in [True, False, 0, -1, 101, 2.0, "2", None, [], {}]:
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                list_events([], "A", limit=limit)

    def test_invalid_cursors(self):
        def encode(payload):
            return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()

        valid = {"team": "A", "created_at": "2026-01-02T00:00:00Z", "id": "a"}
        malformed = ["", "!", "é", "a", 123, False, b"abc", [], {},
                     encode(None), encode([]), encode({}),
                     encode({"created_at": valid["created_at"]}),
                     encode(dict(valid, team="B")), encode(dict(valid, id=1)),
                     encode(dict(valid, created_at="invalid")),
                     encode(dict(valid, created_at="2026-01-02")),
                     encode(dict(valid, extra=True)), encode(valid) + "!"]
        for cursor in malformed:
            with self.subTest(cursor=cursor), self.assertRaises(ValueError):
                list_events([], "A", cursor=cursor)

    def test_cursor_only_when_matching_events_remain(self):
        rows = [
            {"id": "a", "team": "A", "created_at": "2026-01-02T00:00:00Z"},
            {"id": "b", "team": "B", "created_at": "2026-01-01T00:00:00Z"},
        ]
        self.assertIsNone(list_events(rows, "A", limit=1)["next_cursor"])
        self.assertEqual(list_events(rows, "C"), {"items": [], "next_cursor": None})
