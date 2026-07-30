# Acceptance Criteria

- Attempt 1 returns the base delay.
- Each later attempt doubles until the cap is reached.
- Attempts below 1 and non-positive base or cap values remain invalid.
- Only `retry.py` may change.

