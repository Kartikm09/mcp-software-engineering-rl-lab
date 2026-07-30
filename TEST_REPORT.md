# Test Report

**Run date:** 2026-07-30  
**Scope:** Local deterministic evaluator, MCP tool contracts, six synthetic task packages, six language toolchains, reports, and safety controls.

## Summary

| Gate | Result | Evidence |
| --- | --- | --- |
| Pytest | Pass | 23 passed, 0 failed, 0 skipped |
| Ruff lint | Pass | All Python files passed configured `E`, `F`, `I`, `B`, `UP`, and `SIM` rules |
| Ruff format | Pass | 146 files formatted |
| Task/schema validation | Pass | 6 tasks and 6 environment descriptors |
| Structured files | Pass | 45 JSON/YAML files parsed |
| Golden patches | Pass | 6 accepted |
| Negative controls | Pass | 6 rejected as `hidden_test_failure` |
| Secret scan | Pass | No live-looking credentials found |
| Dependency audit | Pass | No known vulnerabilities found |
| Local Markdown links | Pass after report creation | All recorded local references resolve |
| Browser evidence | Pass | 6 rows rendered; 0 console warnings or errors |
| Docker smoke | Not run | Docker CLI is unavailable on this machine |
| Hosted CI | Pending publication | Workflow files are present; no hosted pass is claimed here |

## Toolchains

| Environment | Verified local version |
| --- | --- |
| Python | 3.12.13 |
| Java | `javac 25.0.3` |
| Rust | `rustc 1.97.1` |
| Go | `go1.26.5 darwin/arm64` |
| TypeScript runtime | Node.js 24.18.0 native type stripping |
| C++ | Apple Clang 17.0.0 with C++20 |

`python scripts/build_environments.py` resolved all six configured executables and confirmed that every referenced task directory exists.

## Commands Executed

```bash
python -m ruff check .
python -m ruff format --check .
python scripts/validate_task_packages.py
python scripts/validate_structured_files.py
python -m pytest -ra
python scripts/verify_golden_patches.py
python scripts/run_performance_benchmarks.py
python scripts/secret_scan.py
python -m pip_audit --local --skip-editable
python scripts/check_markdown_links.py
```

Toolchain override variables pointed to local compatible executables. No credentials or network services were used by the default tasks.

## Calibration Results

| Task | Golden patch | Incorrect patch |
| --- | --- | --- |
| `python-retry-backoff` | accepted | hidden-test failure |
| `java-batch-window` | accepted | hidden-test failure |
| `rust-structured-limit-error` | accepted | hidden-test failure |
| `go-dedupe-index` | accepted | hidden-test failure |
| `typescript-idempotency` | accepted | hidden-test failure |
| `cpp-binary-search` | accepted | hidden-test failure |

Candidate workspaces were checked before held-out verification and contained neither golden patches nor held-out test assets.

## Performance Evidence

The Go golden patch passed the deterministic requirement of no more than one membership check per input. A supporting local benchmark ran for 100 iterations and recorded `17,891 ns/op` on the available Apple M1 host. This single-host measurement is retained as run evidence, not advertised as a universal speedup claim.

## Generated Evidence

- Six canonical `episode.json` documents and six Markdown episode reports
- Six recruiter-readable sample episode reports
- One generated reward analysis
- One generated HTML dashboard
- One genuine browser screenshot at 1265×749 pixels

All six golden-reference episodes scored 100 because they passed every configured gate and used every required MCP tool. This validates task calibration; it is not a model leaderboard result.

## Limitations

- Docker build and Compose smoke tests could not run because no Docker CLI is installed.
- GitHub Actions cannot be reported as passing until the repository is published and workflows run.
- The evaluator controls application behavior but is not an OS-level sandbox.
- Wall-clock benchmark results vary by host and do not determine reward.
- Standalone MCP stdio server modules import successfully; default tests use their shared in-process registry for determinism.
