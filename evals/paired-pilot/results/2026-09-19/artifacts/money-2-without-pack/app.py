"""Build an invoice summary without changing the supplied line items."""

from decimal import Context, Decimal, InvalidOperation, ROUND_HALF_UP, localcontext


_CENT = Decimal("0.01")


def _decimal(value):
    if not isinstance(value, (str, Decimal)):
        raise ValueError("Money values and tax_rate must be decimal strings or Decimal")
    try:
        value = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("Invalid decimal value") from exc
    if not value.is_finite() or value < 0:
        raise ValueError("Money values and tax_rate must be finite and nonnegative")
    # Normalize signed zero so monetary output always uses 0.00.
    return value if value else Decimal(0)


def build_invoice(lines, discount="0", tax_rate="0"):
    discount = _decimal(discount)
    tax_rate = _decimal(tax_rate)
    parsed_lines = []
    try:
        for line in lines:
            price = _decimal(line["unit_price"])
            quantity = line["quantity"]
            if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
                raise ValueError("Quantity must be a positive integer")
            parsed_lines.append((price, Decimal(quantity)))
    except (KeyError, TypeError) as exc:
        raise ValueError("Lines must contain unit_price and quantity") from exc

    # Allow exact intermediate arithmetic, including values beyond the default
    # 28-digit precision, without depending on the caller's decimal context.
    values = [discount, tax_rate]
    values.extend(value for line in parsed_lines for value in line)
    precision = 10 + sum(len(value.as_tuple().digits) + abs(value.as_tuple().exponent)
                         for value in values)
    with localcontext(Context(prec=precision, rounding=ROUND_HALF_UP)):
        subtotal = sum(( (price * quantity).quantize(_CENT)
                         for price, quantity in parsed_lines), Decimal("0.00"))
        discount = discount.quantize(_CENT)
        if discount > subtotal:
            raise ValueError("Discount must not exceed subtotal")
        taxable = subtotal - discount
        tax = (taxable * tax_rate).quantize(_CENT)
        return {"subtotal": f"{subtotal:.2f}", "discount": f"{discount:.2f}",
                "tax": f"{tax:.2f}", "total": f"{taxable + tax:.2f}"}
