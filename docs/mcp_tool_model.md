# MCP Tool Model

The lab uses the official Python MCP SDK's `MCPServer` for standalone local servers and an in-process transport for fast deterministic tests. Both call the same `LocalToolRegistry`, so transport mechanics do not change tool semantics.

## Servers

| Server | Tools | Evidence returned |
| --- | --- | --- |
| Repository | `list_files`, `read_file`, `search_text` | Bounded source discovery |
| Issue tracker | `get_issue`, `get_acceptance_criteria` | Problem and acceptance contract |
| Documentation | `search_docs`, `read_doc` | Versioned policy context |
| Test runner | `run_public_tests` | Command, exit code, output, duration |
| Benchmark | `run_baseline_benchmark` | Reproducible baseline measurements |
| Database | `query_context` | Allowlisted local SQLite facts |

## Structured errors

Every call returns `ok`, `content`, `error_code`, and `error_message`. Unknown tools, missing files, unsafe paths, invalid query names, and malformed arguments are data rather than transport exceptions.

```json
{
  "ok": false,
  "content": {},
  "error_code": "valueerror",
  "error_message": "path escapes tool root"
}
```

## Launching a standalone server

Set a task root, then run one module through the official SDK's stdio transport:

```bash
export MCP_RL_TASK_ROOT=tasks/bug_fixing/python-retry-backoff
python -m mcp_servers.repository_server.server
```

No server enables network access. The repository and documentation tools resolve paths beneath fixed roots, while the database tool permits only named read queries.
