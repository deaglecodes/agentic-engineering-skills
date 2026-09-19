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
