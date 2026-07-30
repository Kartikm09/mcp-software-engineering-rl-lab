# Sample Reward Analysis

> Generated from six synthetic golden-reference episodes. Scores calibrate these tasks; they are not model rankings.

| Task | Language | Classification | Reward | Tool calls | Public | Held-out | Benchmark |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
| `cpp-binary-search` | C++ | accepted | 100.00 | 5 | 2 command(s) | 2 command(s) | 0 command(s) |
| `go-dedupe-index` | Go | accepted | 100.00 | 5 | 1 command(s) | 1 command(s) | 1 command(s) |
| `java-batch-window` | Java | accepted | 100.00 | 5 | 2 command(s) | 2 command(s) | 0 command(s) |
| `python-retry-backoff` | Python | accepted | 100.00 | 6 | 1 command(s) | 1 command(s) | 0 command(s) |
| `rust-structured-limit-error` | Rust | accepted | 100.00 | 5 | 2 command(s) | 2 command(s) | 0 command(s) |
| `typescript-idempotency` | TypeScript | accepted | 100.00 | 5 | 1 command(s) | 1 command(s) | 0 command(s) |

## Interpretation

All six reference patches passed public and held-out checks, used every required MCP tool, remained within the allowed file surface, and included a reviewer-facing explanation. The Go task also passed its deterministic operation-count gate and executed the recorded benchmark command.

Every paired negative control was separately rejected by a held-out test. A perfect golden-reference score confirms evaluator calibration; it does not predict performance on unrelated repositories.

## Weighting

Functional correctness and tests account for 60% of the default reward. Tool discovery, evidence, maintainability, performance, and explanation remain separate fields so reviewers can audit why a score was assigned.
