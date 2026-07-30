# Limitations

- The six repositories are compact synthetic task sources, not replicas of private production systems.
- The in-process MCP client validates tool semantics but does not measure transport latency.
- Official SDK stdio servers are included, while default tests use the deterministic in-process registry.
- Resource controls are application-level. They do not provide kernel isolation.
- Build reproducibility still depends on compatible local compilers and runtimes.
- Duration values vary by host and do not affect deterministic reward.
- The reward does not judge architectural elegance beyond allowed-file scope.
- The current database server exposes only two fixed SQLite read queries.
- Docker verification depends on a locally available Docker daemon and must be reported separately.

These constraints are intentional and documented so the portfolio demonstrates reproducible engineering methods without implying a production RL platform or a hardened execution service.
