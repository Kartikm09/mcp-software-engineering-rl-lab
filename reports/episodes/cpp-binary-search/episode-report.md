# Coding-Agent Episode Report

> Synthetic local task and evidence. This is not a private benchmark result.

- Episode: `episode-95acc6ae4438`
- Task: `cpp-binary-search`
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

- `src/binary_search.cpp`

## Verification Evidence

### Public
- `$CLANGXX -std=c++20 -Wall -Wextra -Werror src/binary_search.cpp binary_search_public_test.cpp -o build/cpp-public`: exit=0, duration=784ms
- `build/cpp-public`: exit=0, duration=48ms
### Held-out
- `$CLANGXX -std=c++20 -Wall -Wextra -Werror src/binary_search.cpp binary_search_held_out_test.cpp -o build/cpp-held`: exit=0, duration=730ms
- `build/cpp-held`: exit=0, duration=44ms

## Final Explanation

The baseline mixed an inclusive upper bound with lower-bound updates, which can skip a candidate and underflow when moving left. A half-open `[low, high)` interval keeps every update valid, naturally supports empty input, and verifies equality before returning the insertion position. Complexity remains O(log n) time and O(1) space.

## Security Boundary

The evaluator uses path validation, an executable allowlist, filtered environment variables, timeouts, and output caps. It is not a hardened production sandbox.
