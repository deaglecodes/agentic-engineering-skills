import unittest
from app import build_invoice


class VisibleTests(unittest.TestCase):
    def test_whole_dollars(self):
        self.assertEqual(build_invoice([{"unit_price": "10", "quantity": 2}], "2", "0.10"),
                         {"subtotal": "20.00", "discount": "2.00", "tax": "1.80", "total": "19.80"})

    def test_empty(self):
        self.assertEqual(build_invoice([])["total"], "0.00")


class ContractTests(unittest.TestCase):
    def test_round_each_extended_line_half_up(self):
        self.assertEqual(build_invoice([
            {"unit_price": "0.005", "quantity": 1},
            {"unit_price": "0.005", "quantity": 3},
        ]), {"subtotal": "0.03", "discount": "0.00", "tax": "0.00", "total": "0.03"})

    def test_discount_and_tax_half_up(self):
        self.assertEqual(build_invoice([{"unit_price": "1.005", "quantity": 1}],
                                      "0.105", "0.05"),
                         {"subtotal": "1.01", "discount": "0.11", "tax": "0.05", "total": "0.95"})

    def test_decimal_inputs_and_no_mutation(self):
        from copy import deepcopy
        from decimal import Decimal
        lines = [{"unit_price": Decimal("2.675"), "quantity": 2}]
        original = deepcopy(lines)
        self.assertEqual(build_invoice(lines, Decimal("0"), Decimal("0"))["total"], "5.35")
        self.assertEqual(lines, original)

    def test_large_amount_with_low_context_precision(self):
        from decimal import localcontext
        with localcontext() as context:
            context.prec = 6
            self.assertEqual(build_invoice([
                {"unit_price": "123456789012345678901234567890.005", "quantity": 1}
            ])["total"], "123456789012345678901234567890.01")
            self.assertEqual(context.prec, 6)

    def test_invalid_money_and_rates(self):
        for value in ("-0.001", "NaN", "sNaN", "Infinity", "-Infinity", "bad", None, True, 0.1):
            for field in ("unit_price", "discount", "tax_rate"):
                with self.subTest(value=value, field=field), self.assertRaises(ValueError):
                    line = {"unit_price": "10", "quantity": 1}
                    kwargs = {}
                    if field == "unit_price":
                        line[field] = value
                    else:
                        kwargs[field] = value
                    build_invoice([line], **kwargs)

    def test_invalid_quantities(self):
        from decimal import Decimal
        for quantity in (True, False, 0, -1, 1.5, "2", None, Decimal("2")):
            with self.subTest(quantity=quantity), self.assertRaises(ValueError):
                build_invoice([{"unit_price": "1", "quantity": quantity}])

    def test_discount_limit_applies_after_rounding(self):
        lines = [{"unit_price": "1", "quantity": 1}]
        self.assertEqual(build_invoice(lines, "1.004")["total"], "0.00")
        for discount in ("1.005", "2"):
            with self.subTest(discount=discount), self.assertRaises(ValueError):
                build_invoice(lines, discount)
        with self.assertRaises(ValueError):
            build_invoice([], "0.01")

    def test_zero_and_empty_invoice_fields(self):
        self.assertEqual(build_invoice([], "-0", "-0"),
                         {"subtotal": "0.00", "discount": "0.00", "tax": "0.00", "total": "0.00"})

    def test_invalid_line_structure(self):
        for lines in (None, [None], [{}], [{"unit_price": "1"}]):
            with self.subTest(lines=lines), self.assertRaises(ValueError):
                build_invoice(lines)
