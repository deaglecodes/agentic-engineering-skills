"""Build an invoice summary without changing the supplied line items."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext


def _decimal(value):
    if not isinstance(value, (str, Decimal)):
        raise ValueError("Money values and tax_rate must be decimal strings or Decimals")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("Invalid decimal value") from exc
    if not result.is_finite() or result < 0:
        raise ValueError("Money values and tax_rate must be finite and nonnegative")
    return result.copy_abs()  # Normalize signed zero.


def build_invoice(lines, discount="0", tax_rate="0"):
    discount = _decimal(discount)
    tax_rate = _decimal(tax_rate)
    items = []
    try:
        for line in lines:
            price = _decimal(line["unit_price"])
            quantity = line["quantity"]
            if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
                raise ValueError("Quantity must be a positive integer")
            items.append((price, quantity))
    except (KeyError, TypeError) as exc:
        raise ValueError("Invalid invoice lines") from exc

    # Reserve enough digits for exact products and sums before cent rounding,
    # including when callers have changed the ambient decimal precision.
    values = [discount, tax_rate] + [price for price, _ in items]
    precision = 4 + sum(len(value.as_tuple().digits) + abs(value.as_tuple().exponent)
                        for value in values)
    precision += sum(len(str(quantity)) for _, quantity in items)
    cents = Decimal("0.01")
    with localcontext() as context:
        context.prec = max(28, precision)
        context.rounding = ROUND_HALF_UP
        subtotal = sum(((price * quantity).quantize(cents) for price, quantity in items),
                       Decimal("0.00"))
        discount = discount.quantize(cents)
        if discount > subtotal:
            raise ValueError("Discount must not exceed subtotal")
        taxable = subtotal - discount
        tax = (taxable * tax_rate).quantize(cents)
        return {"subtotal": f"{subtotal:.2f}", "discount": f"{discount:.2f}",
                "tax": f"{tax:.2f}", "total": f"{taxable + tax:.2f}"}
