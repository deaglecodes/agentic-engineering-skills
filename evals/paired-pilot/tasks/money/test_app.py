import unittest
from app import build_invoice


class VisibleTests(unittest.TestCase):
    def test_whole_dollars(self):
        self.assertEqual(build_invoice([{"unit_price": "10", "quantity": 2}], "2", "0.10"),
                         {"subtotal": "20.00", "discount": "2.00", "tax": "1.80", "total": "19.80"})

    def test_empty(self):
        self.assertEqual(build_invoice([])["total"], "0.00")
