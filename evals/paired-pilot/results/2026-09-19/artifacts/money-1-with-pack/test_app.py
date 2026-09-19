import unittest
from copy import deepcopy
from decimal import Decimal, localcontext
from app import build_invoice


class VisibleTests(unittest.TestCase):
    def test_whole_dollars(self):
        self.assertEqual(build_invoice([{"unit_price": "10", "quantity": 2}], "2", "0.10"),
                         {"subtotal": "20.00", "discount": "2.00", "tax": "1.80", "total": "19.80"})

    def test_empty(self):
        self.assertEqual(build_invoice([])["total"], "0.00")

    def test_round_each_extended_line_half_up(self):
        self.assertEqual(build_invoice([
            {"unit_price": "0.005", "quantity": 1},
            {"unit_price": "0.005", "quantity": 1},
            {"unit_price": "0.004", "quantity": 3},
        ]), {"subtotal": "0.03", "discount": "0.00", "tax": "0.00", "total": "0.03"})

    def test_decimal_rounding_and_discounted_tax(self):
        self.assertEqual(build_invoice([{"unit_price": "2.675", "quantity": 1}],
                                       "0.175", "0.05"),
                         {"subtotal": "2.68", "discount": "0.18",
                          "tax": "0.13", "total": "2.63"})

    def test_discount_limit_applies_after_rounding(self):
        lines = [{"unit_price": "1", "quantity": 1}]
        self.assertEqual(build_invoice(lines, "1.004")["total"], "0.00")
        for discount in ("1.005", "2"):
            with self.subTest(discount=discount), self.assertRaises(ValueError):
                build_invoice(lines, discount)
        with self.assertRaises(ValueError):
            build_invoice([], "0.01")

    def test_invalid_decimal_values(self):
        for value in ("-0.001", "NaN", "sNaN", "Infinity", "-Infinity", "bad", "", None, True):
            for field in ("unit_price", "discount", "tax_rate"):
                with self.subTest(value=value, field=field), self.assertRaises(ValueError):
                    line = {"unit_price": "10", "quantity": 1}
                    kwargs = {}
                    if field == "unit_price":
                        line[field] = value
                    else:
                        kwargs[field] = value
                    build_invoice([line], **kwargs)

    def test_invalid_quantities_and_lines(self):
        for quantity in (0, -1, True, False, "2", 1.5, Decimal("2"), None):
            with self.subTest(quantity=quantity), self.assertRaises(ValueError):
                build_invoice([{"unit_price": "1", "quantity": quantity}])
        for lines in (None, [{}], [None], [{"unit_price": 1.25, "quantity": 1}]):
            with self.subTest(lines=lines), self.assertRaises(ValueError):
                build_invoice(lines)

    def test_decimal_inputs_are_not_mutated(self):
        lines = [{"unit_price": Decimal("1.005"), "quantity": 2}]
        original = deepcopy(lines)
        self.assertEqual(build_invoice(lines, Decimal("0.01"), Decimal("0.1")),
                         {"subtotal": "2.01", "discount": "0.01",
                          "tax": "0.20", "total": "2.20"})
        self.assertEqual(lines, original)

    def test_large_values_and_low_caller_precision(self):
        with localcontext() as context:
            context.prec = 6
            self.assertEqual(build_invoice([
                {"unit_price": "123456789012345678901234567890.125", "quantity": 2}
            ])["total"], "246913578024691357802469135780.25")
            self.assertEqual(context.prec, 6)

    def test_negative_zero_is_formatted_as_zero(self):
        self.assertEqual(build_invoice([{"unit_price": "-0", "quantity": 1}], "-0", "-0"),
                         {"subtotal": "0.00", "discount": "0.00", "tax": "0.00", "total": "0.00"})
