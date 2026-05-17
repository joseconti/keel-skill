# Security Profile — MCP Server

Load this when the project is an MCP server (standalone, or shipped inside another product like a WordPress plugin). Apply from Phase 1, verify at every Phase 5 test point. An MCP server exposes capabilities to AI clients — every tool is an attack surface.

## Authorization on every tool

- Every tool/ability has an explicit authorization check appropriate to what it does. There is no "read-only so it's fine" — list-type tools can leak data.
- Map each tool to the least privilege needed. A tool that mutates state must require stronger authz than one that reads public info.
- Never expose an admin/privileged tool without authentication equivalent to the underlying system's.

## Token & transport

- Validate Bearer tokens on every `/mcp/` request; return 401 with a correct `WWW-Authenticate` header pointing to resource metadata when missing/invalid.
- OAuth 2.1 with PKCE (S256): enforce code challenge/verifier; reject public clients without PKCE; validate redirect URIs against a registered allow-list.
- TLS only. Never accept credentials over plaintext.
- Never log tokens, secrets, full Authorization headers, or full tool arguments that may contain secrets.

## Input validation per tool

- Each tool input is schema-validated (type, required, constraints) before use. Reject unknown/extra fields rather than ignoring them.
- Tools that take identifiers, paths, queries, or commands must validate/allow-list them — an MCP tool is a direct path from the model to your system; treat every argument as hostile.
- No tool builds SQL/shell/file paths from raw arguments. Parameterize / sandbox / allow-list.

## Blast radius & abuse

- Rate-limit and/or quota tools, especially expensive or destructive ones. Consider a confirmation/dry-run for destructive tools.
- Bound result sizes (e.g. list limits) so a tool can't be used to exfiltrate everything in one call.
- Idempotency / guard rails on mutating tools to limit accidental or adversarial repeated calls.
- Audit-log tool invocations (who, which tool, when, outcome) without logging secret-bearing payloads.

## Data exposure

- Scope returned data to what the caller is authorized to see; filter at the source, not after fetching everything.
- Never return internal errors, stack traces, or config in tool results.
- Minimize PII in tool outputs; redact where not strictly needed.

## Dependency & supply chain

- The MCP adapter/runtime dependency must fail safe if absent (no fatal that exposes detail); pin and scan dependencies.

## Phase test points (verify during Phase 5)

- Every tool: explicit authz + schema validation + argument allow-listing confirmed.
- Token validation + PKCE + redirect-URI allow-list verified.
- Destructive/expensive tools: rate limit / quota / confirmation in place.
- Result size bounded; returned data scoped to caller.
- No token/secret/argument leakage in logs or tool results.
- Audit log present for tool invocations.
