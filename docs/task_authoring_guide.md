# Task Authoring Guide

## Authoring sequence

1. Start with one observable engineering failure and a compact synthetic baseline.
2. Write the business context and acceptance criteria before the patch.
3. Put essential facts in issue, documentation, or database fixtures so tool discovery matters.
4. Add public tests that orient the candidate without fully specifying every edge case.
5. Add held-out tests for boundaries, regressions, and contract details.
6. Create a minimal golden patch and at least one plausible incorrect patch.
7. Record an expected tool trace and explicit reward weights.
8. Run `python scripts/validate_task_packages.py` and `python scripts/verify_golden_patches.py`.

## Required package

```text
task.yaml
problem_statement.md
business_context.md
acceptance_criteria.md
constraints.md
baseline/
public_tests/
held_out_tests/
golden/solution.patch
golden/explanation.md
golden/verification.json
incorrect_patches/
expected_tool_trace.json
```

## Quality rules

- Use synthetic, self-contained source code.
- Restrict `allowed_changes` to the smallest reasonable surface.
- Avoid tests that depend on current time, network, or random input.
- Keep public tests useful; do not make them intentionally misleading.
- Test the incorrect patch and explain which held-out contract rejects it.
- For performance tasks, make a deterministic work metric the gate and wall-clock data supporting evidence.
