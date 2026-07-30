# Coding-Agent Episode Report

> Synthetic local task and evidence. This is not a private benchmark result.

- Episode: `episode-aeb327a0f5cf`
- Task: `python-retry-backoff`
- Classification: **accepted**
- Reward: **100.00/100**
- Candidate exclusions verified: **True**

## Tool Trace

| # | Server | Tool | Result |
| ---: | --- | --- | --- |
| 1 | `issue_tracker` | `get_issue` | ok |
| 2 | `issue_tracker` | `get_acceptance_criteria` | ok |
| 3 | `documentation` | `search_docs` | ok |
| 4 | `repository` | `read_file` | ok |
| 5 | `database` | `query_context` | ok |
| 6 | `test_runner` | `run_public_tests` | ok |

## Changed Files

- `retry.py`

## Verification Evidence

### Public
- `$PYTHON -m unittest test_public.py`: exit=0, duration=39ms
### Held-out
- `$PYTHON -m unittest test_held_out.py`: exit=0, duration=37ms

## Final Explanation

The implementation treated the one-based attempt number as a zero-based exponent, so attempt 1 used `base * 2`. Subtracting one preserves exponential growth and the existing cap while keeping validation and the public API unchanged. The patch changes one expression and has constant time and space complexity.

## Security Boundary

The evaluator uses path validation, an executable allowlist, filtered environment variables, timeouts, and output caps. It is not a hardened production sandbox.
