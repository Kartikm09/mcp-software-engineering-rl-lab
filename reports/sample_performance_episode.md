# Coding-Agent Episode Report

> Synthetic local task and evidence. This is not a private benchmark result.

- Episode: `episode-bdecd03cfc67`
- Task: `go-dedupe-index`
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
| 5 | `benchmark` | `run_baseline_benchmark` | ok |

## Changed Files

- `dedupe.go`

## Verification Evidence

### Public
- `$GO test ./...`: exit=0, duration=4475ms
### Held-out
- `$GO test ./...`: exit=0, duration=570ms
### Benchmark
- `$GO test -run ^$ -bench BenchmarkUnique -benchtime=100x`: exit=0, duration=253ms

## Final Explanation

The nested scan made worst-case work quadratic in the number of unique values. A local set provides one membership check per input while appending only on the first occurrence, so order remains stable. Expected work becomes O(n) time with O(n) additional space. The deterministic check count is the CI threshold; benchmark timing is recorded but remains machine-dependent.

## Security Boundary

The evaluator uses path validation, an executable allowlist, filtered environment variables, timeouts, and output caps. It is not a hardened production sandbox.
