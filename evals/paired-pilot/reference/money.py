from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext


def build_invoice(lines, discount="0", tax_rate="0"):
    def decimal(value):
        try:
            result = Decimal(value)
        except (TypeError, ValueError, InvalidOperation) as error:
            raise ValueError("Invalid decimal") from error
        if not result.is_finite() or result < 0:
            raise ValueError("Expected finite nonnegative decimal")
        return result

    with localcontext() as context:
        context.prec = 80
        cents = lambda value: value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        subtotal = Decimal("0")
        for line in lines:
            quantity = line["quantity"]
            if type(quantity) is not int or quantity <= 0:
                raise ValueError("Invalid quantity")
            subtotal += cents(decimal(line["unit_price"]) * quantity)
        discount = cents(decimal(discount))
        if discount > subtotal:
            raise ValueError("Discount exceeds subtotal")
        tax = cents((subtotal - discount) * decimal(tax_rate))
        return {key: f"{value:.2f}" for key, value in {
            "subtotal": subtotal, "discount": discount, "tax": tax,
            "total": subtotal - discount + tax}.items()}
