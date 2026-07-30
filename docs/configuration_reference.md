# Configuration Reference

| Variable | Default | Purpose |
| --- | --- | --- |
| `MCP_RL_TASK_ROOT` | None | Task package used by standalone MCP servers |
| `MCP_RL_MAX_TOOL_CALLS` | `40` | Global tool-call ceiling |
| `MCP_RL_COMMAND_TIMEOUT_SECONDS` | `30` | Global subprocess timeout ceiling |
| `MCP_RL_MAX_OUTPUT_BYTES` | `200000` | Global output-capture ceiling |
| `MCP_RL_NETWORK_ENABLED` | `0` | Reserved policy flag; sample tasks remain offline |
| `MCP_RL_FIXED_TIMESTAMP` | None | Fixed ISO timestamp for deterministic report tests |
| `MCP_RL_JAVA` | `java` on PATH | Java runtime override |
| `MCP_RL_JAVAC` | `javac` on PATH | Java compiler override |
| `MCP_RL_RUSTC` | `rustc` on PATH | Rust compiler override |
| `MCP_RL_GO` | `go` on PATH | Go toolchain override |
| `MCP_RL_NODE` | `node` on PATH | Node runtime override |
| `MCP_RL_CLANGXX` | `clang++` on PATH | C++ compiler override |

Task-specific resource limits always narrow global values. Environment files should contain no credentials.
