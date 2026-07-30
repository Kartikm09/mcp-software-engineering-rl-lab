# Coding-Agent Episode Report

> Synthetic local task and evidence. This is not a private benchmark result.

- Episode: `episode-14763d4dd0d4`
- Task: `java-batch-window`
- Classification: **accepted**
- Reward: **100.00/100**
- Candidate exclusions verified: **True**

## Tool Trace

| # | Server | Tool | Result |
| ---: | --- | --- | --- |
| 1 | `issue_tracker` | `get_acceptance_criteria` | ok |
| 2 | `documentation` | `read_doc` | ok |
| 3 | `repository` | `read_file` | ok |
| 4 | `database` | `query_context` | ok |
| 5 | `test_runner` | `run_public_tests` | ok |

## Changed Files

- `src/BatchWindow.java`

## Verification Evidence

### Public
- `$JAVAC -d build src/BatchWindow.java BatchWindowPublicTest.java`: exit=0, duration=292ms
- `$JAVA -cp build BatchWindowPublicTest`: exit=0, duration=29ms
### Held-out
- `$JAVAC -d build src/BatchWindow.java BatchWindowHeldOutTest.java`: exit=0, duration=294ms
- `$JAVA -cp build BatchWindowHeldOutTest`: exit=0, duration=28ms

## Final Explanation

The feature derives remaining capacity from the immutable maximum and validates impossible current states. The existing acceptance predicate used a strict comparison, incorrectly rejecting a request that exactly filled the batch; changing it to `<=` matches the discovered contract. All operations remain O(1), allocation-free, and thread-safe.

## Security Boundary

The evaluator uses path validation, an executable allowlist, filtered environment variables, timeouts, and output caps. It is not a hardened production sandbox.
