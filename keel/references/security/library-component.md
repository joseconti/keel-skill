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

## Verify with

- Package-manager audit of the dependency tree (`npm audit` / `composer audit` / `pip-audit` per ecosystem).
- Inspect the PUBLISHED artifact, not the repo: `npm pack --dry-run` or the ecosystem's equivalent — no secrets, no dev files, only intended exports.
- Diff the public API against the previous release before publishing — a breaking change is a major, per the disclosure duty above.

At a test point, the command and its result are the evidence recorded in `docs/05-test-points.md` — an unrecorded check did not happen.

## Deliberate omissions (seed the "Not defended" table)

This profile hardens what it covers and is silent on the rest. Silence is not protection, so the
project's `docs/threat-model.md` (Phase 2 §4c) carries a "Not defended" table naming what is
deliberately out of scope, its consequence, and what the user would add if their risk profile needs
it. **An omission that is written down is a decision; an omission that is silent is a trap** — six
months on, nobody can tell "we decided against it" from "we forgot".

Start from these rows, keep the ones that apply, add the project's own, and move any row into the
"Defended" table the moment the control actually ships with its evidence:

| Not defended | Consequence | If you need it |
|---|---|---|
| How consumers use the API | A consumer can pass unvalidated input straight through; the library validates its own boundary, not the caller's | Document the trust boundary explicitly, and fail loudly on invalid input rather than coercing it |
| The consumer's runtime and environment | Version, platform and configuration are the consumer's; the support matrix states what is tested, not what is guaranteed everywhere | Widen the tested matrix, or narrow the declared one — never leave it implied |
| Transitive dependency compromise | Direct dependencies are pinned and audited; every consumer inherits the whole tree | Minimize the dependency count (the real control), pin by hash, and review update diffs |
| Data the library is handed | It processes what it is given, including secrets a caller passes in | Never log inputs, and document what the library retains and for how long |
| A malicious fork or a typosquatted package name | Users can install something that is not this project | Publish with provenance/signing where the ecosystem supports it, and state the canonical name and source in the README |

Every remaining control in the "Defended" table carries its delivery state — `IN PLACE` (built and
verified), `TO BUILD` (a named slice), `MANUAL` (a human configures it) or `VERIFY` (only a real
environment confirms it) — and only `IN PLACE` may be written in the present tense anywhere in the
project's documentation.
