# Troubleshooting

## Toolchain unavailable

Run `python scripts/build_environments.py`. Set the matching `MCP_RL_*` variable to an absolute executable path when a compatible toolchain is installed outside `PATH`.

## Patch is malformed

Use a Git unified diff with `a/` and `b/` paths. Run `git apply --check PATCH` against the task baseline. New or changed files must match the manifest's `allowed_changes` list.

## Public tests pass but evaluation fails

Inspect the classification. `hidden_test_failure` means an evaluator-only boundary or regression check failed. `incorrect_tool_use` means the technical patch passed but the recorded trace omitted required discovery tools.

## Go cannot write its cache

The process runner points `GOCACHE` and `GOMODCACHE` inside the candidate workspace. Do not override them with a host-global path in CI.

## Docker command cannot run

Confirm `docker info` succeeds before `docker compose run --rm evaluator`. A missing daemon is an environment limitation, not a successful smoke test.
