def validate(record):
    sku, qty = record["sku"], record["qty"]
    if not isinstance(sku, str) or not sku or type(qty) is not int or not 1 <= qty <= 9:
        raise ValueError("invalid line")
    return sku, qty


def compute(records):
    output = []
    for record in records:
        sku, qty = validate(record)
        output.append((sku, qty * 7))
    return output
