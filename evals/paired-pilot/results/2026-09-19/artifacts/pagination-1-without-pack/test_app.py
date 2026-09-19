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

    def tied_rows(self):
        return [
            {"id": event_id, "team": "A", "created_at": "2026-01-02T00:00:00Z"}
            for event_id in ["2", "10", "a", "9", "b"]
        ] + [
            {"id": "older", "team": "A", "created_at": "2026-01-01T00:00:00Z"},
            {"id": "other", "team": "B", "created_at": "2026-01-03T00:00:00Z"},
        ]

    def test_ties_across_pages_and_no_mutation(self):
        rows = self.tied_rows()
        original = copy.deepcopy(rows)
        for limit in [1, 2, 3, 5, 6, 100]:
            with self.subTest(limit=limit):
                cursor = None
                ids = []
                for _ in range(len(rows) + 1):
                    result = list_events(rows, "A", limit, cursor)
                    ids.extend(row["id"] for row in result["items"])
                    cursor = result["next_cursor"]
                    if cursor is None:
                        break
                    self.assertEqual(len(result["items"]), limit)
                    self.assertLess(len(ids), 6)
                else:
                    self.fail("Pagination did not terminate")
                self.assertEqual(ids, ["b", "a", "9", "2", "10", "older"])
        self.assertEqual(rows, original)

    def test_deleted_anchor(self):
        rows = self.tied_rows()
        first = list_events(rows, "A")
        rows = [row for row in rows if row["id"] != first["items"][-1]["id"]]
        second = list_events(rows, "A", cursor=first["next_cursor"])
        self.assertEqual([row["id"] for row in second["items"]], ["9", "2"])
        last = list_events(rows, "A", cursor=second["next_cursor"])
        self.assertEqual([row["id"] for row in last["items"]], ["10", "older"])
        self.assertIsNone(last["next_cursor"])
        self.assertEqual(list_events([], "A", cursor=first["next_cursor"]),
                         {"items": [], "next_cursor": None})

    def test_invalid_limits(self):
        for limit in [True, False, 0, -1, 101, 1.0, "2", None, [], {}]:
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                list_events([], "A", limit=limit)

    def test_invalid_cursors(self):
        def encode(payload):
            return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()

        valid = {"created_at": "2026-01-02T00:00:00Z", "id": "a", "team": "A"}
        invalid = ["", "!not-base64!", "é", 0, False, [], {}, b"e30=",
                   base64.urlsafe_b64encode(b"not json").decode(),
                   base64.urlsafe_b64encode(b"\xff").decode()]
        invalid.extend(encode(payload) for payload in [None, [], "text", {},
            {"created_at": valid["created_at"]},
            {**valid, "team": "B"}, {**valid, "id": 2},
            {**valid, "created_at": None}, {**valid, "created_at": "bad"},
            {**valid, "created_at": "2026-01-02T00:00:00"},
            {**valid, "extra": "unexpected"},
        ])
        for cursor in invalid:
            with self.subTest(cursor=cursor), self.assertRaises(ValueError):
                list_events([], "A", cursor=cursor)

    def test_cursor_cannot_cross_teams(self):
        cursor = list_events(self.tied_rows(), "A")["next_cursor"]
        with self.assertRaises(ValueError):
            list_events(self.tied_rows(), "B", cursor=cursor)
