"""Retry timing used by a synthetic local worker."""


def backoff_delay(attempt: int, base: int = 1, cap: int = 16) -> int:
    if attempt < 1:
        raise ValueError("attempt must be at least 1")
    if base < 1 or cap < 1:
        raise ValueError("base and cap must be positive")
    return min(cap, base * (2**attempt))
