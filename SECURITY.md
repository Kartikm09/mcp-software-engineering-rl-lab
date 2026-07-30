# Security Policy

Report vulnerabilities through GitHub private vulnerability reporting. Do not attach credentials, private repositories, or untrusted executable patches to public issues.

The lab restricts tools to a configured task root, validates patch paths, filters environment variables, uses an explicit command allowlist, caps output, applies timeouts, and disables network access by policy. These controls are educational guardrails, not a hardened production sandbox. Unknown agent-generated code should run only in an externally isolated, credential-free VM or container.

