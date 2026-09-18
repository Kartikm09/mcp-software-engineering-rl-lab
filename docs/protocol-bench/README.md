# Real MCP software-task calibration

This isolated module extends the existing six-language MCP lab. It keeps their task identifiers,
reference patches, servers and CLI unchanged. A separate runtime/repository was unnecessary because
the existing project already owns the official Python MCP dependency and evaluator boundary.

The new module launches **two actual stdio server subprocesses** with `mcp==2.0.0`. The SDK Client
uses explicit initialize/initialized negotiation, discovers advertised tools and makes JSON-RPC
calls. The servers are not aliases for direct Python function calls. Each process is scoped to one
immutable task at launch and exposes three tools:

| Server | Tools |
| --- | --- |
| Specification | search_specs, get_requirement, get_schema_version |
| Evidence | get_issue, read_sanitized_log, get_expected_transition |

Arguments have typed size/pattern limits. Versioned output uses a bounded Pydantic schema. Missing,
stale and denied records return distinct statuses; SDK-invalid calls are captured separately.
Cross-task identifiers cannot select another process's corpus. Tests exercise real initialization,
discovery, all six tools, invalid arguments, missing/stale/denied records, request timeout, restart,
and cross-task leakage. Initialization has a 60-second cold-start budget; the explicit request
cancellation test uses a 10ms deadline against a controlled 200ms server delay.

## Run locally

Use the repository's documented development install first:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install pip==26.2.1
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest tests/protocol_bench
.venv/bin/python -m mcp_rl_lab.protocol_bench.runner duplicate-work reference --output reports/generated/protocol-reference
```

The output directory must be new or empty. For another run choose another directory. The runner
requires no keys or provider accounts. It is a **scripted synthetic calibration**, not a live model
solving a coding problem or evidence of an agent's independent MCP reasoning. No paid model runs
were performed. Visible calls and concise scripted decisions are recorded; private reasoning and
session history are not collected.

Four task IDs are available: `duplicate-work`, `scheduled-delivery`, `module-boundary`, and
`repeated-validation`. Each has `baseline`, `reference`, `alternative`, `wrong-1`, and `wrong-2`
variants. The baseline source and public smoke contract are copied into a resettable temporary
workspace. Every variant has a unified patch against that baseline. File SHA-256 values identify
the exact starting/candidate bytes; task version 1 is immutable within a published Git commit.

| Task | Behavioral acceptance | Two plausible incorrect controls |
| --- | --- | --- |
| duplicate-work | Shared equal-key effects, independent keys, success cache, retry after failure, waiter cancellation | Cached failure; global key coalescing |
| scheduled-delivery | Due tick, cancellation, terminal completion, bounded retries, stable schedule identity | Cancels completed jobs; terminal first failure |
| module-boundary | Pure standard-library domain logic, no vendor/network coupling, strict input and Unicode behavior | Boolean coercion; lower instead of Unicode casefold |
| repeated-validation | Same values validated once, order preserved, distinct quantities, invalid typed values rejected | Skips validation; caches by SKU only |

The baseline and incorrect patches must fail **named behavioral assertions**, not missing imports,
compilers or setup. The independent verifier admits the alternative correct solution without
comparing it to the reference text. Public smoke checks preserve the exposed interface; acceptance
checks and versioned incident/spec fixtures are outside the copied candidate workspace.

`result.json` separates functional acceptance and MCP usage. Usage requires successful current-
version requirement and incident retrieval, response digests, and references to a changed allowed
file with a written implementation decision. A schema-only token call fails. An unchanged baseline
has no linked patch and therefore fails the usage verdict even though calls were recorded. This
checks evidence linkage, not causal proof of comprehension or authentication of arbitrary supplied
logs. The runner's own trace comes from actual SDK calls.

Every attempt writes `manifest.json`, `result.json`, `test_results.json`, `changed_files.json`,
`mcp_tool_trace.jsonl`, `reproduction.md`, and `review.md`. Manifest records include SDK/Python
versions, negotiated protocol, tool schemas, candidate baseline hash and trusted verifier hash.
Public fixture files are inspectable; they are not a private benchmark or contamination-proof test.

## Execution and trust boundary

Only `solution.py` can change through the workspace API. Absolute/traversal paths, symlinks,
protected files and unexpected post-execution changes are rejected. Verifier/golden/incident files
are never copied into candidate roots. The trusted verifier is an external file, launched with an
isolated Python import mode and a fresh environment. Submitted command strings are never executed.

Default variants are trusted, reviewed synthetic source. A subprocess, allowlist or Docker container
alone is **not hardened hostile-code containment**. Local subprocesses share the machine filesystem;
these controls are not a claim that malicious candidate Python cannot inspect the evaluator process
or external files. Run adversarial code only with an independently hardened filesystem/process/network
boundary. The campaign used a credential-free macOS sandbox for inspected fixtures. CI uses a fresh
hosted runner and filtered child environment; no provider credentials are passed to candidates.

The module-boundary check combines behavioral tests with a documented static import/literal rule
for common network modules. It rejects `urllib`, `http`, `socket`, `ftplib`, `smtplib`, `telnetlib`,
`xmlrpc` and `ssl`, and third-party imports. It is not a proof against dynamically obfuscated imports.

## Review-driven corrections

A controlled cancellation regression exposed a subtle reference issue: if the only waiter cancels
before shared work fails, cleanup in that waiter's exception handler cannot observe the later
failure. A task completion callback now evicts failed work and consumes its exception, so the very
next request can retry. The public task ID and success-caching rule stay unchanged.

Independent review reproduced `import urllib.request` passing the first draft dependency gate,
because it only distinguished standard-library and third-party imports. The explicit network set
and import/literal regressions now enforce the stated domain boundary. Discovery-failure cleanup
also closes the already-entered SDK client before cleaning up its temporary resources.

The optimization fixture measures exactly 200 validation calls for its baseline and 2 for the
correct repeated-value solution. This deterministic operation count is distinct from elapsed-time
performance; no machine-independent latency or production savings claim follows from it.

Official sources checked 18 September 2026:
- [Python MCP SDK client](https://py.sdk.modelcontextprotocol.io/client/)
- [SDK transports](https://py.sdk.modelcontextprotocol.io/client/transports/)
- [SDK server tools](https://py.sdk.modelcontextprotocol.io/servers/tools/)
- [SDK testing](https://py.sdk.modelcontextprotocol.io/get-started/testing/)
