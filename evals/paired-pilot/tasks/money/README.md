# Invoice summary

`build_invoice(lines, discount="0", tax_rate="0")` returns subtotal, discount, tax, total as strings with exactly two decimal places.

Contract:
- Every line has `unit_price` (a decimal string or Decimal) and `quantity` (a positive integer, not a boolean).
- Use decimal arithmetic. Round each extended line price (unit price times quantity) to cents using ROUND_HALF_UP, then sum those rounded lines.
- Round discount to cents with the same rule. It must not exceed the subtotal.
- Calculate tax on subtotal minus discount, round tax to cents with ROUND_HALF_UP, then add it to the discounted subtotal.
- All money values and tax_rate must be finite and nonnegative. Invalid inputs raise ValueError. The tax rate is a decimal fraction, not a percentage integer.
- Empty lines produce a zero subtotal. The inputs must not be mutated.

No third-party dependencies. Run `python3 -B -m unittest -v`.
