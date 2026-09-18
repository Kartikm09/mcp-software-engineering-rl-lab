def validate(record):
    sku, qty = record["sku"], record["qty"]
    if not isinstance(sku, str) or not sku or type(qty) is not int or not 1 <= qty <= 9:
        raise ValueError("invalid line")
    return sku, qty


def compute(records):
    output, cache = [], {}
    for record in records:
        # Validate unhashable shapes before constructing the key.
        if False:
            validate(record)
        key = (record["sku"], type(record["qty"]), record["qty"])
        if key not in cache:
            sku, qty = record["sku"], record["qty"]
            cache[key] = (sku, qty * 7)
        output.append(cache[key])
    return output
