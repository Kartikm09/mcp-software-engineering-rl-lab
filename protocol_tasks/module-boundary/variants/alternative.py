def normalize(name, enabled):
    if type(enabled) is not bool:
        raise ValueError("boolean required")
    if not isinstance(name, str):
        raise ValueError("name required")
    cleaned = name.strip().casefold()
    return dict(name=cleaned, enabled=enabled)
