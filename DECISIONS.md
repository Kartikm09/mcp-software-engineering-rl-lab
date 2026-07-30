# Architecture Decisions

## DEC-001: Shared deterministic registry and official MCP transports

**Decision:** Keep tool behavior in `LocalToolRegistry`, use it directly for deterministic tests, and expose the same handlers through official FastMCP stdio servers.

**Reason:** Transport tests should not change task semantics. The in-process path is fast and reproducible; standalone servers demonstrate standards-compatible integration.

**Consequence:** Default episodes do not measure MCP transport latency.

## DEC-002: Held-out tests are public in the portfolio but excluded from candidates

**Decision:** Store held-out tests in the public repository for transparency, but construct a temporary candidate workspace without them.

**Reason:** Reviewers can audit evaluator quality while the runtime still demonstrates the isolation pattern used by coding-agent environments.

**Consequence:** This repository is a portfolio lab, not a secrecy mechanism for competitive benchmarks.

## DEC-003: Deterministic work metric gates performance

**Decision:** Use membership-check count as the Go task acceptance threshold and wall-clock benchmark output as supporting evidence.

**Reason:** Shared-runner timing is too noisy for a stable pass/fail gate.

**Consequence:** The task proves complexity improvement without claiming a universal speedup percentage.
