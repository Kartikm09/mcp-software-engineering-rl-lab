# Problem Statement

Concurrent calls can pass the completed-value check before either result is stored. Coalesce work per key and clear failed in-flight operations so retries remain possible.

