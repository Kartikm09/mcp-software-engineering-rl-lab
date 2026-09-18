def normalize(name, enabled):
    if not isinstance(name, str) or enabled is None:
        raise ValueError("invalid record")
    return {"name": name.strip().casefold(), "enabled": bool(enabled)}
