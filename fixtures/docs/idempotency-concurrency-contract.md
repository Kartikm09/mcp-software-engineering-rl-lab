# Idempotency Concurrency Contract

Concurrent calls with the same key share one in-flight operation. Distinct keys must retain distinct values and independent progress. Failed work is removed from the in-flight map so a later retry can execute.

