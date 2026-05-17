# Security Profile — Reusable Component / Library / Package

Load this when the deliverable is a library, package, or reusable component consumed by other code. The threat model is different: you don't control the caller, and your defaults become everyone's defaults.

## Safe by default

- Secure defaults. The zero-config behavior must be the safe behavior; insecure modes are opt-in, explicit, and documented as risky.
- Fail closed: on ambiguous or invalid input, error — don't silently do something unsafe.
- No hidden network calls, telemetry, or file/system access the consumer didn't ask for. Any such behavior is opt-in and documented.

## Input boundaries

- Validate all public API inputs; never assume the caller validated. Document accepted ranges/types and what happens on violation.
- Don't expose internals that let a caller bypass invariants (no leaking mutable internal state, no eval of caller-provided strings, no path/SQL/command built from caller input without validation).
- Be careful with deserialization of untrusted data — never deserialize into arbitrary types from caller-controlled input.

## Supply chain & dependencies

- Minimize dependencies; each one is inherited risk for every consumer. Pin versions; scan; respond to advisories with a patched release.
- No secrets, tokens, or internal endpoints baked into the package or its examples/fixtures.
- Reproducible build; the published artifact contains only what's intended (enforced via Phase 7 export-ignore) — no tests, no dev tooling, no `.env`, no internal docs.

## API stability & disclosure

- Clear public vs internal boundary; internal symbols marked/segregated so consumers don't depend on them.
- Semantic versioning; security fixes called out in the changelog (oldest → newest ordering).
- A documented way for users to report vulnerabilities; document the supported versions.

## Documentation duties (feeds Phase 6)

- Document every security-relevant option, its default, and the consequence of changing it.
- Document the trust assumptions: what the library does and does NOT validate, so the consumer knows their responsibilities.

## Phase test points (verify during Phase 5)

- Default configuration is the safe configuration; insecure modes are opt-in and documented.
- Every public input validated; violation behavior documented and tested.
- No unexpected network/file/system side effects.
- Published artifact contains only intended files; no secrets in package or examples.
- Dependency scan clean; versions pinned.
- Public/internal boundary explicit; changelog notes security fixes oldest → newest.
