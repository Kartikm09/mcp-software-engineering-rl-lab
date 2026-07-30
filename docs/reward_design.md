# Reward Design

The score is inspectable and task-specific. Functional correctness carries more weight than presentation.

| Component | Default weight | Evidence |
| --- | ---: | --- |
| Tool discovery | 5% | Distinct relevant MCP servers used |
| Relevant tool selection | 5% | Required tools present in trace |
| Evidence gathering | 10% | Successful evidence calls |
| Patch correctness | 25% | Final verifier acceptance |
| Public tests | 15% | All public commands pass |
| Held-out tests | 20% | All held-out commands pass |
| Maintainability | 5% | Change remains within allowed surface |
| Performance | 10% | Benchmark gate passes or is not applicable |
| Final explanation | 5% | Sufficient reviewer-facing explanation |

The Go performance task moves five percentage points from patch correctness to performance, while correctness and tests still total 55%. Scores are calibration aids, not claims about general model capability.

## Known trade-off

The current maintainability and explanation checks are deliberately simple and deterministic. A learned judge could provide nuance but would add nondeterminism, cost, and prompt sensitivity. The JSON evidence is designed so a separate reviewer can add qualitative assessment without changing the canonical score.
