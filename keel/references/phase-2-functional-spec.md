# Phase 2 — Functional Spec

Goal: turn the agreed v1 scope into a precise functional specification with flows, so that everything downstream (design, build, docs) has an unambiguous contract. Still no code, no visual design.

## What to produce

- `docs/02-functional-spec.md` — the functional contract.
- `docs/flows/` — one flow per significant user/system journey (markdown with step lists; include a Mermaid diagram where it clarifies branching).
- `docs/03-technical-plan.md` — the technical foundation: stack, architecture, code map, conventions (step 4). Without it, every later session invents its own conventions and the codebase drifts.
- `docs/estimate.md` (firm version appended) and `docs/budget.md` — the client-facing budget (step 7, per `references/estimation-budget.md`).

## Steps

### 1. Functional requirements

For each v1 feature from `docs/01-discovery.md`, write testable requirements: inputs, processing, outputs, preconditions, postconditions, error conditions. "The user can X" is not enough — specify what happens on success, on empty, on invalid, on permission failure. These become test points in Phase 5.

### 2. Flows

Identify every journey that has more than one step or any branching: e.g. install/activation, auth/login, the core task, admin configuration, error/recovery, external-system interaction. For each, write `docs/flows/<flow-name>.md` with:

- Trigger / entry point
- Numbered steps (actor → system response)
- Branches and conditions (role/plan/state gating — the user's products often have plan/role gating)
- Failure paths and recovery
- A Mermaid diagram when branching is non-trivial

### 3. Data & integrations

- Data model: entities, fields, relationships, validation rules, persistence.
- External integrations: every external API/service, with auth method, endpoints used, rate/quota limits, failure handling. Cross-check the security profile for anything sensitive (tokens, secrets, PII).
- Permissions matrix: who (role/plan) can do what.

### 4. Technical foundation → `docs/03-technical-plan.md`

Decide, with the user, the technical shape of the project — BEFORE design (Phase 3's brief must state where the final code will live) and before any code (Phase 5 confirms and follows it). This is where stack, architecture, and conventions are fixed once, so no later session re-decides them. Record the significant choices in `docs/decisions.md` too.

ALWAYS use this template for `docs/03-technical-plan.md`:

```
# Technical Plan — [Project name]

## Stack (exact versions)
- Language/runtime + minimum versions; host/framework (e.g. WP min, Woo min, PHP min); key dependencies (pinned, from the Phase 1 dependency table)
- Why this stack: [1–3 lines]
## Support matrix & budgets
- Minimum supported platform versions (e.g. PHP / WordPress / WooCommerce / browsers / OS) — these go in the platform headers where applicable
- Performance budgets or capacity assumptions, if relevant
## Architecture
- Components and their responsibilities; data flow (Mermaid where branching)
- Persistence: engine, schema ownership, migration approach (if Phase 1 recorded an installed base: versioned, idempotent migrations per Phase 5)
## Code map (keep current — future sessions orient HERE, never by scanning the tree)
| Path | Purpose (one line) |
## Conventions
- Prefix/namespace: [the project prefix — every function/class/option/hook uses it]
- Naming: [functions / classes / files / hooks patterns]
- Error handling: [one strategy: exceptions vs error objects (e.g. WP_Error) vs result types; user-facing error policy]
- Logging: [mechanism + levels; never log secrets — per the security profile]
## Testing
- Framework(s) + exact run commands; what gets unit vs integration vs end-to-end coverage
- Verification playground (whenever the project can be run): how the software will be exercised for REAL beyond the automated suite — Docker/docker-compose, wp-env, a playground script, a disposable sandbox, whatever fits the stack — with exact start/stop commands. Stood up at the Phase 5 scaffold; access details + step-by-step try-it instructions for the user live in docs/playground.md
- Regression rule: every bug fixed gets a test pinning the fix (linked from lessons-learned)
## Tooling commands
- lint / test / build / package: the exact commands (verified end-to-end at Phase 5 scaffold)
## Version touchpoints
- Every place the project's version string lives (e.g. plugin header, readme.txt Stable tag, a VERSION constant, package.json) — Phase 7 syncs ALL of them on release
## License & dependency compatibility
- Project license (from Phase 1); rule: every dependency's license is verified compatible BEFORE adoption
```

The code map and conventions are what keep multi-chat development coherent: a fresh session reads this file instead of exploring the codebase. Keeping the code map current when the layout changes is part of the change, not optional.

### 5. Decide precisely what needs design

This is the bridge to Phase 3. Produce a clear split:

- **Needs design:** every screen/UI surface, listed. Mark which are structurally similar (template-reuse candidates — this prevents Design from regenerating near-identical pages later).
- **No design needed:** backend, jobs, CLI, pure logic.
- **External software the user must configure by hand** (Unity, hosting panel, OAuth console, SaaS settings, DNS, payment gateway): list each. These become the `SPEC/external-setup.md` requirements in Phase 3 and the guided walkthrough in Phase 4.
- **Assets Design likely can't produce** (photographic images, complex illustrations, 3D renders): flag any you can already foresee. These become `SPEC/external-assets.md` requirements in Phase 3 and the guided one-asset-at-a-time generation loop in Phase 4.

For every screen that needs design, also record its **accessibility requirements** (semantic structure and heading order, keyboard/assistive-tech operability, contrast, focus order and visible focus, error identification, target size, reduced-motion) — these become part of what Design must specify in Phase 3, per `references/accessibility.md`. Accessibility is not deferred to the build; it is specified with the screen.

### 6. Acceptance criteria

Define, per feature, the conditions under which it's considered done. These feed Phase 5 test points and the Phase 4 faithfulness checklist.

Every feature with a UI includes **accessibility conditions** in its acceptance criteria — operable by keyboard and assistive technology, accessible name/role/state exposed, contrast met, visible focus, error identification (not color-only), adequate target size, and honored user preferences (reduced motion, text scaling). Accessibility is a done condition of the feature, not a separate later pass (see `references/accessibility.md`).

### 7. Firm estimate & client budget (close of spec — AI-time based)

With the real scope now fixed (requirements, flows, screens, slices implied by the technical plan, integrations, external-setup items), close the numbers. Follow `references/estimation-budget.md` end to end: recompute the itemized AI hours and vibe coder hours from the actual spec; ask the batched budget questions (rate + currency, AI mode and model(s), contingency, the budget's language — it is a client-facing deliverable — taxes note, availability for the calendar estimate); compute the AI cost (verified per-token prices if API; ≈ 0 marginal on subscription); append **Estimate v[N] (firm)** to `docs/estimate.md`; and produce `docs/budget.md` in the client's language — itemized segments priced line by line, the developer block and the AI block SEPARATE, totals, estimated calendar delivery, and terms. Then run the mandatory present → adjust → approve loop with the user (e.g. choosing not to bill the AI cost on subscription) and record the approval and its choices in `docs/decisions.md`. Any scope change after this budget → new version, re-approved (same reference). NEVER price from traditional human development time.

## `docs/02-functional-spec.md` structure

ALWAYS use this template:

```
# Functional Spec — [Project name]

## Functional requirements
- per feature: inputs / processing / outputs / pre / post / errors
## Data model
## Integrations (with auth, limits, failure handling)
## Permissions matrix
## Flows index
- links to docs/flows/*.md
## Technical plan
- see docs/03-technical-plan.md (stack, architecture, code map, conventions — produced in step 4)
## Design split
- Needs design: [screens, with template-reuse notes]
- No design: [...]
- External manual setup: [...]
## Acceptance criteria (per feature — include accessibility conditions for every UI feature)
## Estimate & budget
- see docs/estimate.md (Estimate v[N] firm) and docs/budget.md (client-facing, approved — D-entry in docs/decisions.md)
## Open questions for the user
```

## Definition of done

- Every v1 feature has testable requirements and acceptance criteria.
- Every UI feature's acceptance criteria include accessibility conditions (keyboard/AT operable, name/role/state, contrast, visible focus, error identification, target size, honored user preferences) per `references/accessibility.md`; every screen that needs design has its accessibility requirements recorded for the Phase 3 brief.
- Every multi-step/branching journey has a flow file.
- Data model, integrations, and permissions are specified.
- `docs/03-technical-plan.md` complete per its template: stack with exact versions, support matrix, architecture, code map, conventions (prefix, naming, error handling, logging), testing approach with run commands, version touchpoints, license-compatibility rule. Significant choices recorded in `docs/decisions.md`.
- The design split is explicit, including external-setup items.
- Zero unresolved open questions.
- Firm estimate appended to `docs/estimate.md` and `docs/budget.md` produced in the client's language (itemized per segment, developer and AI blocks separate, totals and terms) per `references/estimation-budget.md`, explicitly approved by the user with the approval recorded in `docs/decisions.md`. Client acceptance itself is the user's business — it does not gate Phase 3.
- `docs/PROGRESS.md` updated (phase status, artifacts, next action).

If the project needs design, proceed to Phase 3. If Phase 1 said no design and Phase 2 confirms no UI, skip to Phase 5.
