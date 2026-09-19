"""Build an invoice summary without changing the supplied line items."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext


_CENT = Decimal("0.01")


def _decimal(value):
    if not isinstance(value, (str, Decimal)):
        raise ValueError("Money values and tax_rate must be decimal strings or Decimal")
    try:
        value = Decimal(value)
    except InvalidOperation as error:
        raise ValueError("Invalid decimal value") from error
    if not value.is_finite() or value < 0:
        raise ValueError("Money values and tax_rate must be finite and nonnegative")
    return value.copy_abs()  # Normalize negative zero.


def build_invoice(lines, discount="0", tax_rate="0"):
    prices = []
    try:
        for line in lines:
            price = _decimal(line["unit_price"])
            quantity = line["quantity"]
            if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
                raise ValueError("Quantity must be a positive integer")
            prices.append((price, Decimal(quantity)))
    except (TypeError, KeyError) as error:
        raise ValueError("Invalid invoice lines") from error
    discount = _decimal(discount)
    tax_rate = _decimal(tax_rate)

    # Allow exact intermediate arithmetic even beyond the caller's precision.
    values = [discount, tax_rate] + [value for pair in prices for value in pair]
    precision = 10 + sum(len(value.as_tuple().digits) + abs(value.as_tuple().exponent)
                         for value in values)
    with localcontext() as context:
        context.prec = max(28, precision)
        context.rounding = ROUND_HALF_UP
        subtotal = sum((price * quantity).quantize(_CENT) for price, quantity in prices)
        subtotal = Decimal(subtotal).quantize(_CENT)
        discount = discount.quantize(_CENT)
        if discount > subtotal:
            raise ValueError("Discount must not exceed subtotal")
        taxable = subtotal - discount
        tax = (taxable * tax_rate).quantize(_CENT)
        return {"subtotal": f"{subtotal:.2f}", "discount": f"{discount:.2f}",
                "tax": f"{tax:.2f}", "total": f"{taxable + tax:.2f}"}
