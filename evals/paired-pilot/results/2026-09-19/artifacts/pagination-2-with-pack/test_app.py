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


class PaginationTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {"id": "2", "team": "A", "created_at": "2026-01-02T00:00:00Z"},
            {"id": "other", "team": "B", "created_at": "2026-01-03T00:00:00Z"},
            {"id": "10", "team": "A", "created_at": "2026-01-02T00:00:00Z"},
            {"id": "old", "team": "A", "created_at": "2026-01-01T00:00:00Z"},
            {"id": "9", "team": "A", "created_at": "2026-01-02T00:00:00Z"},
            {"id": "new", "team": "A", "created_at": "2026-01-03T00:00:00Z"},
        ]

    def test_complete_traversal_with_ties_and_team_filter(self):
        for limit in (1, 2, 3, 5, 100):
            with self.subTest(limit=limit):
                cursor = None
                seen = []
                for _ in range(len(self.rows) + 1):
                    page = list_events(self.rows, "A", limit, cursor)
                    seen.extend(row["id"] for row in page["items"])
                    cursor = page["next_cursor"]
                    if cursor is None:
                        break
                    self.assertEqual(len(page["items"]), limit)
                else:
                    self.fail("Pagination did not terminate")
                self.assertEqual(seen, ["new", "9", "2", "10", "old"])

    def test_deleted_anchor_and_newer_insert(self):
        first = list_events(self.rows, "A", limit=3)
        self.assertEqual([row["id"] for row in first["items"]], ["new", "9", "2"])
        remaining = [row for row in self.rows if row["id"] != "2"]
        remaining.append({"id": "8", "team": "A", "created_at": "2026-01-02T00:00:00Z"})
        page = list_events(remaining, "A", cursor=first["next_cursor"])
        self.assertEqual([row["id"] for row in page["items"]], ["10", "old"])
        self.assertIsNone(page["next_cursor"])
        self.assertEqual(list_events([], "A", cursor=first["next_cursor"]),
                         {"items": [], "next_cursor": None})

    def test_no_mutation(self):
        original = copy.deepcopy(self.rows)
        first = list_events(self.rows, "A")
        list_events(self.rows, "A", cursor=first["next_cursor"])
        self.assertEqual(self.rows, original)

    def test_invalid_limits(self):
        for limit in (True, False, 0, -1, 101, 2.0, "2", None, [], {}):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                list_events([], "A", limit=limit)

    def test_wrong_team(self):
        cursor = list_events(self.rows, "A")["next_cursor"]
        with self.assertRaises(ValueError):
            list_events(self.rows, "B", cursor=cursor)

    def test_malformed_cursors(self):
        valid = {"team": "A", "id": "9", "created_at": "2026-01-02T00:00:00Z"}
        payloads = [None, [], 12, "text", {},
                    {"created_at": valid["created_at"]},
                    dict(valid, id=9), dict(valid, team=None),
                    dict(valid, created_at=None), dict(valid, created_at="garbage"),
                    dict(valid, created_at="2026-01-02"), dict(valid, extra=True)]
        cursors = ["", "!", "é", "e30", False, 5, b"e30=", [],
                   base64.urlsafe_b64encode(b"not json").decode(),
                   base64.urlsafe_b64encode(b"\xff").decode()]
        cursors.extend(base64.urlsafe_b64encode(json.dumps(p).encode()).decode()
                       for p in payloads)
        valid_cursor = base64.urlsafe_b64encode(json.dumps(valid).encode()).decode()
        cursors.append(valid_cursor + "!")
        for cursor in cursors:
            with self.subTest(cursor=cursor), self.assertRaises(ValueError):
                list_events([], "A", cursor=cursor)
