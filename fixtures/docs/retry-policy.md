# Retry Policy

The attempt counter is one-based. Exponential backoff therefore uses `base * 2^(attempt - 1)` and applies the cap after calculating the delay. Invalid attempt, base, or cap values are rejected rather than corrected silently.

