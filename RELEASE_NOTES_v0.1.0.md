# v0.1.0 Release Notes

These notes are prepared for the first public release. No public release or tag is claimed until publication approval is received and hosted CI completes.

## Included

- Six local MCP servers sharing one deterministic tool contract
- Six original synthetic tasks across Python, Java, Rust, Go, TypeScript, and C++
- Public and held-out tests, minimal golden patches, and negative controls
- Temporary candidate workspaces with evaluator-only asset separation
- Patch path validation, command allowlist, filtered environment, timeouts, and output caps
- Deterministic classifications and transparent reward components
- Canonical JSON episodes, Markdown reports, benchmark evidence, and a genuine dashboard screenshot
- GitHub Actions for tests, environment resolution, and golden-patch calibration

## Verified Locally

- 23 tests passed
- 6/6 golden patches accepted
- 6/6 incorrect patches rejected
- 45 JSON/YAML files parsed
- Ruff lint and format passed
- Secret scan passed

## Known Limitation

Docker was not available in the local environment, so the image and Compose smoke test remain an explicit pre-release gate rather than a completed claim.
