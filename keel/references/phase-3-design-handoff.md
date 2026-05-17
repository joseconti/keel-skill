# Phase 3 — Design Handoff

Goal: produce one complete brief that tells Claude Design exactly what to build and how, so Design delivers a reusable design system + real built artifacts + a governing SPEC — not a pile of token-wasting near-identical pages, and with nothing left "in the air". This phase does not design anything; designing happens in Design.

This phase absorbs the former `design-spec-handoff` skill. Read `references/handoff-contract.md` and `references/design-brief-template.md` before starting.

## Inputs from earlier phases

- `docs/02-functional-spec.md` → the "Design split" (screens that need design, template-reuse candidates, external-setup items).
- `docs/01-discovery.md` → project type, constraints, the loaded security profile (Design must respect host/security constraints, e.g. WP admin scheme, no external font CDNs), and the **internationalization decision**. If multi-language: the brief must tell Design that all copy is translatable — no baked-in text that can't be swapped per locale, mark every string as content (not decoration), account for text expansion/RTL if relevant — so the build can externalize strings without redesigning. Carry the base language and target locales into the brief.

## Core principles to encode into the brief

- **Build once, reuse by manifest.** Structurally-identical pages are built ONCE as a template; every consumer page is recorded in `SPEC/manifest.md` with its data/variant. Regenerating near-identical pages is the failure mode to prevent.
- **Deliver real artifacts AND a governing SPEC.** Design already emits working files (HTML/CSS/JS/SVG/images/components); keep that, but every artifact is governed by the SPEC so nothing is ambiguous.
- **Nothing in the air.** Every screen, every state (default, hover, focus, active, disabled, loading, empty, error, success), every breakpoint, every conditional behavior gets exact values.
- **Ask, don't invent.** When a needed detail (token, state, behavior, copy, breakpoint, external-setup value) is undefined, Design must ASK the user and record it — never guess.
- **Exact values only.** Hex, px/rem, font names+weights, ms durations, easing, z-index.
- **External setup is fully extracted.** Every value the user must set by hand in external software goes into `SPEC/external-setup.md` — never left implicit in an artifact (it will be guided one verified step at a time in Phase 4).
- **Assets Design can't produce are declared, not faked.** Any photo/complex illustration/3D render Design cannot generate goes into `SPEC/external-assets.md` with full generation detail (role, location, filename, format, dimensions, visual description, palette/style from tokens) — never a silent gap or unlabeled placeholder (it will be generated one asset at a time with the user's chosen generator in Phase 4).

## Steps

### 1. Confirm inputs are complete

If the design split in `docs/02-functional-spec.md` is vague, resolve it with the user before writing the brief. An undefined input here becomes an in-the-air defect later.

### 2. Write the brief

Fill `references/design-brief-template.md` completely — no unfilled brackets. A value that is genuinely the user's call and unknown goes to the user as a question now, not to Design as a guess. Save the filled brief as `docs/design/DESIGN-BRIEF.md`.

The brief must:
- State build-once-reuse-by-manifest and give Design the screen list split into unique vs reuses-template-X.
- Require the exact `design-handoff/` structure from `references/handoff-contract.md` (real artifacts + `SPEC/`).
- Include the question protocol: Design stops and asks the user for any undefined detail; collects them in `SPEC/open-questions.md`.
- Enumerate, per screen, every required state and breakpoint.
- Require `SPEC/external-setup.md` with every external-software config value (or explicit "none").
- Require `SPEC/external-assets.md` with every asset Design can't produce, fully detailed (or explicit "none").
- Forbid duplicating structurally-identical pages.

### 3. Hand the brief to the user

Tell the user the brief is at `docs/design/DESIGN-BRIEF.md`, to paste into Design, and state the one rule that matters most: build once, ask don't invent. Keep it short.

## What Design must return (the handoff contract)

A `design-handoff/` folder per `references/handoff-contract.md`: real artifacts under `artifacts/` (templates built once, components, only-unique pages, real assets, tokens-as-code) plus `SPEC/` (`manifest.md`, `design-tokens.md`, `screens/*.md`, `interactions.md`, `assets-index.md`, `external-assets.md`, `external-setup.md`, `open-questions.md`). Place the returned handoff at `docs/design/design-handoff/`.

## Definition of done

- `docs/design/DESIGN-BRIEF.md` exists, fully filled, with no unresolved user questions.
- The brief mandates the exact handoff contract including `external-setup.md` and `external-assets.md`.
- The user has what they need to run Design.

Phase 4 begins only once Design returns the handoff.
