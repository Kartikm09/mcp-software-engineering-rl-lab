# Business Context

A synthetic notification service uses idempotency keys to avoid duplicate deliveries. Unrelated keys must continue concurrently and failed attempts must not poison the key.

