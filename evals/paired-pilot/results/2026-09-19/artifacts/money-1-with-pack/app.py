"""Build an invoice summary without changing the supplied line items."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext


def _decimal(value):
    if isinstance(value, bool) or not isinstance(value, (str, Decimal, int)):
        raise ValueError("Expected a decimal value")
    try:
        number = Decimal(value)
    except InvalidOperation as error:
        raise ValueError("Expected a decimal value") from error
    if not number.is_finite() or number < 0:
        raise ValueError("Values must be finite and nonnegative")
    return number.copy_abs()


def build_invoice(lines, discount="0", tax_rate="0"):
    discount = _decimal(discount)
    tax_rate = _decimal(tax_rate)
    items = []
    try:
        for line in lines:
            price, quantity = line["unit_price"], line["quantity"]
            if not isinstance(price, (str, Decimal)):
                raise ValueError("Unit prices must be decimal strings or Decimal values")
            if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
                raise ValueError("Quantities must be positive integers")
            items.append((_decimal(price), Decimal(quantity)))
    except (KeyError, TypeError) as error:
        raise ValueError("Expected lines with unit_price and quantity") from error

    # Allow exact intermediate arithmetic, including amounts beyond the default
    # Decimal precision, independently of the caller's precision setting.
    values = [discount, tax_rate] + [value for item in items for value in item]
    precision = 10 + sum(len(value.as_tuple().digits) + abs(value.as_tuple().exponent)
                         for value in values)
    with localcontext() as context:
        context.prec = max(28, precision)
        cents = Decimal("0.01")
        subtotal = sum(( (price * quantity).quantize(cents, rounding=ROUND_HALF_UP)
                         for price, quantity in items), Decimal("0.00"))
        discount = discount.quantize(cents, rounding=ROUND_HALF_UP)
        if discount > subtotal:
            raise ValueError("Discount must not exceed subtotal")
        taxable = subtotal - discount
        tax = (taxable * tax_rate).quantize(cents, rounding=ROUND_HALF_UP)
        return {"subtotal": f"{subtotal:.2f}", "discount": f"{discount:.2f}",
                "tax": f"{tax:.2f}", "total": f"{taxable + tax:.2f}"}
