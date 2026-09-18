def normalize(name, enabled):
    if not isinstance(name, str) or type(enabled) is not bool:
        raise ValueError("invalid record")
    return {"name": name.strip().casefold(), "enabled": enabled}
