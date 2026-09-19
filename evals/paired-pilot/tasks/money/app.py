"""Build an invoice summary without changing the supplied line items."""


def build_invoice(lines, discount="0", tax_rate="0"):
    subtotal = round(sum(float(line["unit_price"]) * line["quantity"] for line in lines), 2)
    discount = float(discount)
    taxable = max(0, subtotal - discount)
    tax = round(taxable * float(tax_rate), 2)
    return {"subtotal": f"{subtotal:.2f}", "discount": f"{discount:.2f}",
            "tax": f"{tax:.2f}", "total": f"{taxable + tax:.2f}"}
