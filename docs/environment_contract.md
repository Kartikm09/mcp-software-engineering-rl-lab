# Environment Contract

Each `environments/*/environment.yaml` identifies one language, toolchain expectation, task package, and network policy. JSON Schema validates the descriptor before a task is built.

## Candidate-visible assets

- Baseline repository files
- Public tests
- An empty local `build/` directory
- Tool results explicitly requested through MCP

## Evaluator-only assets

- Held-out tests before the held-out phase
- Golden patch and explanation
- Intentionally incorrect patches
- Reward implementation and evaluator internals

## Runtime controls

| Control | Default | Task override |
| --- | ---: | ---: |
| Tool calls | 40 | Lower per-task ceiling |
| Command timeout | 30 seconds | 20-45 seconds in sample tasks |
| Captured output | 200 KB | 100-150 KB in sample tasks |
| Network | Disabled by policy | Cannot be enabled by a task |
| Patch size | 1 MB | Fixed |

The evaluator uses the stricter value when process settings and task limits differ. Host toolchain executables can be supplied with the `MCP_RL_JAVA`, `MCP_RL_JAVAC`, `MCP_RL_RUSTC`, `MCP_RL_GO`, `MCP_RL_NODE`, and `MCP_RL_CLANGXX` environment variables.
