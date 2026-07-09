# Phase 3 — Design Handoff

Goal: produce one complete brief that tells Claude Design exactly what to build and how, so Design delivers a reusable design system + real built artifacts + a governing SPEC — not a pile of token-wasting near-identical pages, and with nothing left "in the air". This phase does not design anything; designing happens in Design.

This phase absorbs the former `design-spec-handoff` skill. Read `references/handoff-contract.md` and `references/design-brief-template.md` before starting.

## Inputs from earlier phases

- `docs/02-functional-spec.md` → the "Design split" (screens that need design, template-reuse candidates, external-setup items).
- `docs/03-technical-plan.md` → the target stack and host constraints. The brief's "Where the final code will live" comes from here — Design must know the real target (e.g. WP admin page vs static site vs SPA), never guess it.
- `docs/01-discovery.md` (design-system decision, Phase 1 step 9) → whether a design system already governs this brand. **If existing:** its tokens, logo usage, typography and component styles go INTO the brief as the canonical Section 2 values, with their source cited — Design applies them and proposes any deviation as a question, never restyles silently. **If founding:** the brief tells Design it is creating the brand's canonical design system, built for reuse beyond this project, and carries the Phase 1 **founding-interview answers** verbatim (logo status — including whether Design creates it, colors, typography + licensing, personality, references, modes, imagery, vetoes) as the seed Design starts from. **If one-off:** state it, so Design knows the scope of what it defines.
- `docs/01-discovery.md` (design-system target surfaces, Phase 1 step 9) → the surfaces/platforms the design system must cover (web, WordPress/WooCommerce admin, PrestaShop, iOS/iPadOS, watchOS, macOS, tvOS, Android, Windows, a cross-platform framework, email, print). The brief must name every target surface and require Design to deliver, per surface, the native/idiomatic tokens and component specs plus the mapping from one canonical token set onto that surface — so a design system that must serve iOS and web (for example) ships both the HIG-aligned iOS values and the web CSS values from a single brand source, never a web-only artifact that a native build then has to reinterpret. Surfaces marked "anticipated for reuse" are defined now even if this project ships only one of them.
- `docs/01-discovery.md` → project type, constraints, the loaded security profile (Design must respect host/security constraints, e.g. WP admin scheme, no external font CDNs), and the **internationalization decision**. If multi-language: the brief must tell Design that all copy is translatable — no baked-in text that can't be swapped per locale, mark every string as content (not decoration), account for text expansion/RTL if relevant — so the build can externalize strings without redesigning. Carry the base language and target locales into the brief.
- `docs/01-discovery.md` (accessibility commitment, target platform, targeted level) and `docs/02-functional-spec.md` (per-screen accessibility requirements) → the **accessibility decision**. The brief must require Design to *specify* accessibility, never leave it to the build: contrast-verified color pairs, the visible focus style, focus order, accessible name/role/state per component and per state, heading/landmark structure, target sizes, reduced-motion variants, behavior under text scaling and high-contrast, and error identification. Carry the targeted level (WCAG 2.2 AA floor / AAA where feasible; EN 301 549 / EAA if in scope) into the brief. Per `references/accessibility.md`.

## Core principles to encode into the brief

- **The design system is inherited or founded — never parallel.** If a design system exists (Phase 1 step 9), Design works inside it: exact palette, logo rules, typography, component styles. If none exists and this project founds it, Design builds tokens and components deliberately for brand-wide reuse. What must never happen is a third thing: a new, slightly-different look created per project, which is how a brand's surfaces drift apart.
- **Build once, reuse by manifest.** Structurally-identical pages are built ONCE as a template; every consumer page is recorded in `SPEC/manifest.md` with its data/variant. Regenerating near-identical pages is the failure mode to prevent.
- **Deliver real artifacts AND a governing SPEC.** Design already emits working files (HTML/CSS/JS/SVG/images/components); keep that, but every artifact is governed by the SPEC so nothing is ambiguous.
- **Nothing in the air.** Every screen, every state (default, hover, focus, active, disabled, loading, empty, error, success), every breakpoint, every conditional behavior gets exact values.
- **Ask, don't invent.** When a needed detail (token, state, behavior, copy, breakpoint, external-setup value) is undefined, Design must ASK the user and record it — never guess.
- **Exact values only.** Hex, px/rem, font names+weights, ms durations, easing, z-index.
- **External setup is fully extracted.** Every value the user must set by hand in external software goes into `SPEC/external-setup.md` — never left implicit in an artifact (it will be guided one verified step at a time in Phase 4).
- **Assets Design can't produce are declared, not faked.** Any photo/complex illustration/3D render Design cannot generate goes into `SPEC/external-assets.md` with full generation detail (role, location, filename, format, dimensions, visual description, palette/style from tokens) — never a silent gap or unlabeled placeholder (it will be generated one asset at a time with the user's chosen generator in Phase 4).
- **Assets are delivered build-ready — the build never transforms them.** Every logo and icon is delivered in **both SVG and PNG** (PNG at the intrinsic size plus the platform's required densities/sizes), and every asset is exported in the format the target stack drops in directly, so Code uses it as-is without converting, re-exporting, tracing, recoloring, or resizing. `SPEC/assets-index.md` records every delivered format per asset with its exact use and size. An asset that would force a build-side conversion is an incomplete handoff (a Design Request), per `references/handoff-contract.md` rule 4.
- **Every screen is defined by what it DOES, not just how it looks.** For each screen the brief carries its purpose and the concrete functionalities/actions available on it (from `docs/02-functional-spec.md`), so Design builds the right screen — not just a nice-looking layout. Behavior, conditional logic and gating live in `SPEC/interactions.md`; each screen's job is stated in its `SPEC/screens/*.md`.
- **Accessibility is specified, never deferred.** Every screen's accessibility is designed and documented by Design: contrast-verified color pairs (with measured ratios), the visible focus indicator, focus order, accessible name/role/state per component and per state (including error/empty/loading/disabled), heading/landmark structure, target sizes, reduced-motion variants, behavior under text scaling and high-contrast/forced-colors, and error identification (never color-only). A screen without its accessibility spec is incomplete — the build must not invent it. Per `references/accessibility.md`.

## Steps

### 1. Confirm inputs are complete

If the design split in `docs/02-functional-spec.md` is vague, resolve it with the user before writing the brief. An undefined input here becomes an in-the-air defect later.

### 2. Write the brief

Fill `references/design-brief-template.md` completely — no unfilled brackets. A value that is genuinely the user's call and unknown goes to the user as a question now, not to Design as a guess. Save the filled brief as `docs/design/DESIGN-BRIEF.md`.

The brief must:
- State the design-system status (existing → canonical values + source in Section 2, apply without reinventing; founding → building the brand's canonical system for reuse; one-off → explicit).
- Name the target surfaces/platforms the system must cover and require, per surface, native/idiomatic tokens + component specs and the mapping from the one canonical token set onto that surface (or explicit single-surface scope).
- State build-once-reuse-by-manifest and give Design the screen list split into unique vs reuses-template-X.
- Require the exact `design-handoff/` structure from `references/handoff-contract.md` (real artifacts + `SPEC/`).
- Include the question protocol: Design stops and asks the user for any undefined detail; collects them in `SPEC/open-questions.md`.
- Enumerate, per screen, every required state and breakpoint — and, per screen, what it DOES (its purpose and the functionalities/actions on it, from the functional spec), so Design builds the right screen, not just a layout.
- Require every logo and icon in **both SVG and PNG**, and every asset in a format the target stack uses directly (no build-side conversion), all recorded in `SPEC/assets-index.md` with format(s), exact use, and size — per `references/handoff-contract.md` rule 4.
- Require `SPEC/external-setup.md` with every external-software config value (or explicit "none").
- Require `SPEC/external-assets.md` with every asset Design can't produce, fully detailed (or explicit "none").
- Require `SPEC/accessibility.md` plus per-screen accessibility notes (contrast-verified pairs, focus style/order, name/role/state per component and state, heading/landmark structure, target sizes, reduced-motion variants, text-scaling/high-contrast behavior, error identification), per `references/accessibility.md`.
- Forbid duplicating structurally-identical pages.

### 3. Hand the brief to the user

Tell the user the brief is at `docs/design/DESIGN-BRIEF.md`, to paste into Design, and state the one rule that matters most: build once, ask don't invent. Keep it short.

## What Design must return (the handoff contract)

A `design-handoff/` folder per `references/handoff-contract.md`: real artifacts under `artifacts/` (templates built once, components, only-unique pages, real assets, tokens-as-code) plus `SPEC/` (`manifest.md`, `design-tokens.md`, `screens/*.md`, `interactions.md`, `assets-index.md`, `external-assets.md`, `external-setup.md`, `accessibility.md`, `open-questions.md`). Place the returned handoff at `docs/design/design-handoff/`.

## Definition of done

- `docs/design/DESIGN-BRIEF.md` exists, fully filled, with no unresolved user questions.
- The design-system status is stated in the brief; if a system exists, Section 2's values come from it with the source cited (nothing left for Design to reinvent).
- The brief names every target surface/platform the system must cover and requires per-surface native tokens + component specs and the canonical-token mapping onto each surface.
- The brief mandates the exact handoff contract including `external-setup.md`, `external-assets.md`, and `accessibility.md`.
- The brief requires logos and icons in both SVG and PNG and every asset in a directly-usable format (no build-side transformation), and requires each screen's purpose/functionalities to be stated, not just its visuals.
- The brief requires Design to specify accessibility per screen (`SPEC/accessibility.md` + per-screen notes), per `references/accessibility.md`.
- The user has what they need to run Design.

Phase 4 begins only once Design returns the handoff.
