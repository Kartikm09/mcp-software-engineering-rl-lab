# Sandbox And Security

## Threat model

Candidate patches and task commands may be malformed or attempt to access paths outside the task. The lab protects against accidental host exposure with bounded paths, a command allowlist, environment filtering, timeouts, output caps, and temporary workspaces.

## Controls

- Reject absolute and parent-traversal paths.
- Parse every diff target and compare it with `allowed_changes`.
- Run `git apply --check --whitespace=error-all` before mutation.
- Allow only Python, Java, Rust, Go, Node, Clang, generated test binaries, and Git executables.
- Remove credentials and most host environment variables.
- Point `HOME`, Go caches, and generated output into the temporary workspace.
- Reject HTTP(S) arguments and keep all sample fixtures local.
- Cap each patch at 1 MB and captured output at a task-defined size.
- Delete temporary workspaces on context exit.

## Important limitation

This is not a hardened sandbox. An allowlisted compiler or language runtime can execute code with the permissions of the current user. Containers also do not automatically make hostile code safe. Use a disposable VM or a purpose-built isolation service for genuinely untrusted patches.

Report security issues through the private process in `SECURITY.md`; do not include sensitive proof in a public issue.
