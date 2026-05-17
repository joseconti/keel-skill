# Phase 2 — Functional Spec

Goal: turn the agreed v1 scope into a precise functional specification with flows, so that everything downstream (design, build, docs) has an unambiguous contract. Still no code, no visual design.

## What to produce

- `docs/02-functional-spec.md` — the functional contract.
- `docs/flows/` — one flow per significant user/system journey (markdown with step lists; include a Mermaid diagram where it clarifies branching).

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

### 4. Decide precisely what needs design

This is the bridge to Phase 3. Produce a clear split:

- **Needs design:** every screen/UI surface, listed. Mark which are structurally similar (template-reuse candidates — this prevents Design from regenerating near-identical pages later).
- **No design needed:** backend, jobs, CLI, pure logic.
- **External software the user must configure by hand** (Unity, hosting panel, OAuth console, SaaS settings, DNS, payment gateway): list each. These become the `SPEC/external-setup.md` requirements in Phase 3 and the guided walkthrough in Phase 4.
- **Assets Design likely can't produce** (photographic images, complex illustrations, 3D renders): flag any you can already foresee. These become `SPEC/external-assets.md` requirements in Phase 3 and the guided one-asset-at-a-time generation loop in Phase 4.

### 5. Acceptance criteria

Define, per feature, the conditions under which it's considered done. These feed Phase 5 test points and the Phase 4 faithfulness checklist.

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
## Design split
- Needs design: [screens, with template-reuse notes]
- No design: [...]
- External manual setup: [...]
## Acceptance criteria (per feature)
## Open questions for the user
```

## Definition of done

- Every v1 feature has testable requirements and acceptance criteria.
- Every multi-step/branching journey has a flow file.
- Data model, integrations, and permissions are specified.
- The design split is explicit, including external-setup items.
- Zero unresolved open questions.

If the project needs design, proceed to Phase 3. If Phase 1 said no design and Phase 2 confirms no UI, skip to Phase 5.
