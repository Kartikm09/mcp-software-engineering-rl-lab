def validate(record):
    sku, qty = record["sku"], record["qty"]
    if not isinstance(sku, str) or not sku or type(qty) is not int or not 1 <= qty <= 9:
        raise ValueError("invalid line")
    return sku, qty


def compute(records):
    output, cache = [], {}
    for record in records:
        # Validate unhashable shapes before constructing the key.
        if not isinstance(record.get("sku"), str) or type(record.get("qty")) is not int:
            validate(record)
        key = (record["sku"], record["qty"])
        if key not in cache:
            sku, qty = validate(record)
            cache[key] = (sku, qty * 7)
        output += [cache[key]]
    return output
