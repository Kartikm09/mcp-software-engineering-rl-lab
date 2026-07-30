# Golden Solution Methodology

A golden solution is a reference for verifier calibration, not a claim that only one implementation is valid.

## Construction

1. Reproduce the baseline failure.
2. Read the same issue and documentation facts available through MCP.
3. Make the smallest contract-complete change allowed by the task.
4. Run public and held-out tests.
5. Run benchmarks where applicable.
6. Explain root cause, trade-offs, complexity, and evidence.
7. Save a clean unified diff and verification metadata.

## Negative controls

Each sample task includes a patch that appears plausible but violates a held-out requirement: linear rather than exponential retry, a Java capacity off-by-one, collapsed Rust errors, sorted rather than stable Go output, globally coalesced TypeScript work, or an absent-value C++ insertion index.

The calibration rule is strict: every golden patch must be accepted and every negative control must be rejected. A task is not releasable otherwise.
