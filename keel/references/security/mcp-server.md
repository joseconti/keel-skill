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

## Model-facing threats (what makes an MCP server different)

- **Tool results are an injection channel.** Results that embed third-party or user-generated content (fetched pages, tickets, messages, file contents) feed straight into the calling model: that content is DATA, never instructions. Return it clearly delimited and labelled as untrusted content; never let fetched text rewrite the tool's own framing. Document this contract per tool.
- **Tool descriptions and schemas are prompts** consumed by client models — their integrity matters. A description never changes at runtime based on external input (tool poisoning / rug-pull vector). A description change is a release-level change, reviewed like code.
- **Confused deputy.** The server never exercises broad credentials on behalf of arbitrary model requests. Scope credentials per user/session; one master token that any caller can drive through the server is a finding.
- **Destructive or side-effecting tools** (delete, send, pay, deploy) require explicit human confirmation or run dry-run by default. This is a GATE, not a design suggestion — the confirmation/dry-run rule in "Blast radius & abuse" below is mandatory for these tools.
- **Local/HTTP transports:** bind to localhost (never 0.0.0.0 for a local server) and validate the Origin header on incoming connections — DNS-rebinding defense, as the MCP spec requires. TLS for anything non-local.

## Blast radius & abuse

- Rate-limit and/or quota tools, especially expensive or destructive ones. Destructive or side-effecting tools require explicit human confirmation or dry-run by default — a gate, not a suggestion (see "Model-facing threats").
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
- External content in tool results returned delimited and labelled as data; the malicious-content fixture does not rewrite the tool's framing.
- Tool descriptions/schemas identical to the reviewed release; nothing external can alter them at runtime.
- Credentials scoped per user/session; no master token that any caller can drive.
- Every destructive/side-effecting tool gated: attempt without confirmation (or outside dry-run) → refused.
- Local transport bound to localhost with the Origin header validated (DNS-rebinding attempt rejected); TLS on anything non-local.

## Verify with

- MCP Inspector (`npx @modelcontextprotocol/inspector`) exercising every tool.
- Invalid and malformed-schema calls against every tool — fuzz the boundaries; each rejected cleanly.
- A malicious-content fixture — a resource/tool result that embeds instruction-shaped text — verifying the server returns it labelled as data.
- Dependency audit (`npm audit` / `pip-audit` per stack).

At a test point, the command and its result are the evidence recorded in `docs/05-test-points.md` — an unrecorded check did not happen.
