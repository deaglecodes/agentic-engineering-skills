import unittest
from app import build_invoice


class VisibleTests(unittest.TestCase):
    def test_whole_dollars(self):
        self.assertEqual(build_invoice([{"unit_price": "10", "quantity": 2}], "2", "0.10"),
                         {"subtotal": "20.00", "discount": "2.00", "tax": "1.80", "total": "19.80"})

    def test_empty(self):
        self.assertEqual(build_invoice([])["total"], "0.00")


class RoundingContractTests(unittest.TestCase):
    def test_rounds_extended_lines_before_summing(self):
        self.assertEqual(build_invoice([
            {"unit_price": "0.335", "quantity": 3},
            {"unit_price": "0.005", "quantity": 1},
        ]), {"subtotal": "1.02", "discount": "0.00", "tax": "0.00", "total": "1.02"})

    def test_discount_and_tax_round_half_up(self):
        self.assertEqual(build_invoice(
            [{"unit_price": "1.00", "quantity": 1}], "0.045", "0.10"),
            {"subtotal": "1.00", "discount": "0.05", "tax": "0.10", "total": "1.05"})

    def test_decimal_inputs_and_no_mutation(self):
        from copy import deepcopy
        from decimal import Decimal
        lines = [{"unit_price": Decimal("2.675"), "quantity": 1}]
        original = deepcopy(lines)
        self.assertEqual(build_invoice(lines, Decimal("0"), Decimal("0"))["total"], "2.68")
        self.assertEqual(lines, original)

    def test_discount_limit_uses_rounded_discount(self):
        lines = [{"unit_price": "1", "quantity": 1}]
        self.assertEqual(build_invoice(lines, "1.004")["total"], "0.00")
        for discount in ("1.005", "2"):
            with self.subTest(discount=discount), self.assertRaises(ValueError):
                build_invoice(lines, discount)
        with self.assertRaises(ValueError):
            build_invoice([], "0.01")

    def test_invalid_decimal_values(self):
        from decimal import Decimal
        for value in ("-0.001", "NaN", "sNaN", "Infinity", "-Infinity", "bad", "",
                      Decimal("NaN"), Decimal("-1"), None, True, 0.1):
            for field in ("unit_price", "discount", "tax_rate"):
                with self.subTest(value=value, field=field), self.assertRaises(ValueError):
                    line = {"unit_price": "1", "quantity": 1}
                    kwargs = {}
                    if field == "unit_price":
                        line[field] = value
                    else:
                        kwargs[field] = value
                    build_invoice([line], **kwargs)

    def test_invalid_quantities(self):
        for quantity in (True, False, 0, -1, 1.5, "2", None):
            with self.subTest(quantity=quantity), self.assertRaises(ValueError):
                build_invoice([{"unit_price": "1", "quantity": quantity}])

    def test_malformed_lines(self):
        for lines in (None, [None], [{}], [{"unit_price": "1"}]):
            with self.subTest(lines=lines), self.assertRaises(ValueError):
                build_invoice(lines)

    def test_signed_zero_and_empty_output(self):
        self.assertEqual(build_invoice([], "-0", "-0"),
                         {"subtotal": "0.00", "discount": "0.00", "tax": "0.00", "total": "0.00"})

    def test_large_values_ignore_callers_precision(self):
        from decimal import localcontext
        with localcontext() as context:
            context.prec = 3
            result = build_invoice([
                {"unit_price": "123456789012345678901234567890.125", "quantity": 2}
            ], "0.005", "0.1")
        self.assertEqual(result, {
            "subtotal": "246913578024691357802469135780.25",
            "discount": "0.01", "tax": "24691357802469135780246913578.02",
            "total": "271604935827160493582716049358.26",
        })
