# Coding-Agent Episode Report

> Synthetic local task and evidence. This is not a private benchmark result.

- Episode: `episode-06f52dbaddcc`
- Task: `typescript-idempotency`
- Classification: **accepted**
- Reward: **100.00/100**
- Candidate exclusions verified: **True**

## Tool Trace

| # | Server | Tool | Result |
| ---: | --- | --- | --- |
| 1 | `issue_tracker` | `get_acceptance_criteria` | ok |
| 2 | `documentation` | `search_docs` | ok |
| 3 | `repository` | `read_file` | ok |
| 4 | `database` | `query_context` | ok |
| 5 | `test_runner` | `run_public_tests` | ok |

## Changed Files

- `idempotency.ts`

## Verification Evidence

### Public
- `$NODE --test idempotency_public.test.mjs`: exit=0, duration=123ms
### Held-out
- `$NODE --test idempotency_held_out.test.mjs`: exit=0, duration=106ms

## Final Explanation

The completed cache alone cannot close the interval between starting and finishing an operation. An in-flight map keyed by idempotency key shares only equivalent work, keeps unrelated keys independent, stores successful values, and deletes the promise in `finally` so failures can retry. Average lookup remains O(1).

## Security Boundary

The evaluator uses path validation, an executable allowlist, filtered environment variables, timeouts, and output caps. It is not a hardened production sandbox.
