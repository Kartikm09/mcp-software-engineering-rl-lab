CREATE TABLE task_context (task_id TEXT NOT NULL, key TEXT NOT NULL, value TEXT NOT NULL);
CREATE TABLE failure_history (task_id TEXT NOT NULL, category TEXT NOT NULL, detail TEXT NOT NULL);

INSERT INTO task_context VALUES
('python-retry-backoff', 'attempt_index', 'one-based'),
('java-batch-window', 'exact_fill', 'allowed'),
('rust-structured-limit-error', 'supported_range', '1..=1000'),
('go-dedupe-index', 'order', 'first occurrence'),
('typescript-idempotency', 'scope', 'per key'),
('cpp-binary-search', 'interval', 'half-open');

INSERT INTO failure_history VALUES
('python-retry-backoff', 'boundary', 'attempt 1 observed at twice the configured base'),
('java-batch-window', 'boundary', 'exact-capacity request was rejected'),
('rust-structured-limit-error', 'contract', 'callers parsed error strings'),
('go-dedupe-index', 'performance', 'unique batches caused quadratic comparisons'),
('typescript-idempotency', 'concurrency', 'same-key requests duplicated an operation'),
('cpp-binary-search', 'boundary', 'existing values near interval edges were missed');

