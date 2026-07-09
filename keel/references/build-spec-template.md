# BUILD-SPEC Template

Produce this as `BUILD-SPEC.md` in the project, fully filled, BEFORE writing any code. Every section must be resolved from the handoff. A blank or "TBD" section means the build cannot start — that item goes to a Design Request instead.

---

# BUILD-SPEC: [PROJECT NAME]

> Source handoff: `[path to design-handoff/]`
> This document is the implementation contract. The build does not deviate from it. Code adapts to this; this never adapts to the code.

## 1. Audit result

- Handoff matches the contract structure: [yes / no — if no, this is a Design Request]
- `open-questions.md` status: [empty/resolved / N unresolved items → Design Request]
- Gaps found: [none / list — each gap blocks build until resolved by Design]

## 2. Resolved screen list

| Screen | Type | Source artifact | SPEC file | Notes |
|--------|------|-----------------|-----------|-------|
| [name] | unique / template:`[tpl]`+data | `artifacts/...` | `SPEC/screens/...md` | [variant/data] |

Every page from `SPEC/manifest.md` must appear here and resolve. Templates stay templates — list each consumer with its data; do not plan to duplicate.

## 3. Token table (canonical — must match design exactly)

Copied from `SPEC/design-tokens.md` and reconciled with `artifacts/styles/`. If they disagreed, that disagreement was a Design Request, not a judgment call.

| Token | Value | Role |
|-------|-------|------|
| color.bg | `#......` | ... |
| space.md | `..px/rem` | ... |
| font.body | `...` | ... |
| motion.base | `..ms ...easing` | ... |
| ... | ... | ... |

## 4. Per-screen state matrix

For each unique screen, every state the build MUST implement, with its spec reference. A screen is incomplete until every row is built.

### [Screen name]
| State | Required | Spec reference | Implemented |
|-------|----------|----------------|-------------|
| default | yes | `SPEC/screens/x.md#default` | ☐ |
| hover | [yes/no] | ... | ☐ |
| focus | ... | ... | ☐ |
| active | ... | ... | ☐ |
| disabled | ... | ... | ☐ |
| loading | ... | ... | ☐ |
| empty | ... | ... | ☐ |
| error | ... | ... | ☐ |
| success | ... | ... | ☐ |
| breakpoint [x] | ... | ... | ☐ |
| variant [role/plan] | ... | ... | ☐ |

## 4a. Accessibility spec (from `SPEC/accessibility.md`)

Copied from the handoff's accessibility spec; the build implements every row. A blank row is a gap → Design Request, not a guess. Per `references/accessibility.md`.

| Screen / component | Contrast pairs (ratio) | Name / role / state (per state) | Focus order + visible focus | Target size | Reduced-motion / text-scaling / high-contrast | Error identification | Spec reference | Built |
|--------------------|------------------------|---------------------------------|-----------------------------|-------------|-----------------------------------------------|----------------------|----------------|-------|
| [name] | [pairs + ratios] | [per state] | [order + style] | [px/pt/dp] | [behavior] | [pattern] | `SPEC/accessibility.md#...` | ☐ |

## 5. Interaction & logic table

From `SPEC/interactions.md`. Every behavior, conditional render, gating rule, transition.

| Trigger | Behavior | Condition / gating | Spec reference |
|---------|----------|--------------------|----------------|
| [event] | [what happens] | [role/plan/state] | ... |

## 6. Asset map

From `SPEC/assets-index.md`. Every asset must exist in `artifacts/assets/`, in a format the build uses directly — no build-side conversion, resize, recolor, rasterize, or re-export. Every logo and icon must be present in **both SVG and PNG**. An asset that would force a transformation, or a logo/icon missing one of the two formats, is a gap → Design Request, not a build-side fix.

| Asset file | Used in | Intrinsic size | Format(s) delivered | Logo/icon: SVG+PNG both? | Build-ready (no transform)? | Exists |
|------------|---------|----------------|---------------------|--------------------------|-----------------------------|--------|
| ... | ... | ... | ... | [yes / n/a] | [yes / gap→DR] | ☐ |

## 7. External manual setup (driven one step at a time)

From `SPEC/external-setup.md`. These steps are NOT scripted — they are guided to the user interactively, one verified step at a time (Phase 4 Step 5). Every value here must trace to the SPEC; nothing improvised. If `external-setup.md` says "none", write "No external manual setup required" and skip the table.

| # | External software (+version) | Exact location/path inside it | Field | Exact value | Spec reference | Verifiable by screenshot | Status |
|---|------------------------------|-------------------------------|-------|-------------|----------------|--------------------------|--------|
| 1 | [e.g. Unity 2022.3] | [exact menu/panel path] | [field] | [exact value] | `SPEC/external-setup.md#...` | [yes/no] | ☐ pending / ✓ verified / ⚠ unverified |

Order is fixed: do not reorder. A row with no Spec reference is a gap → Design Request, not a guessed step.

## 8. Externally generated assets (one asset at a time)

From `SPEC/external-assets.md`. Assets Design couldn't produce, generated by the user with their chosen image generator, guided one at a time (Phase 4 Step 6). Every prompt detail must trace to the SPEC; nothing invented. Record the user's chosen generator once. If `external-assets.md` says "none", write "No externally generated assets required" and skip the table.

(Website projects: product screenshots declared in `SPEC/screenshots.md` are tracked with the same table and rules — one guided capture at a time, per `references/phase-8-design-direction.md`.)

Chosen image generator: [e.g. Gemini / other / not specified → neutral prompts]

| # | Asset role & where used | Target path | Filename | Format / dimensions | Spec reference | Status |
|---|-------------------------|-------------|----------|---------------------|----------------|--------|
| 1 | [e.g. hero photo, landing template] | `artifacts/assets/img/` | [exact name] | [e.g. PNG, 1600×900] | `SPEC/external-assets.md#...` | ☐ pending / ✓ confirmed / ⚠ unverified |

A row with no Spec reference is a gap → Design Request, not an invented image.

## 9. Target-stack integration plan

How the real artifacts are ported into [target stack]. This is the ONLY place code-side adaptation is allowed — and it must not change the design intent.

- Templates → [how represented in the stack, e.g. WP template parts / React components]
- Tokens → [how delivered, e.g. CSS custom properties file generated from token table]
- Components → [mapping]
- Constraints handled: [host constraints from the brief and how code accommodates them WITHOUT altering design]
- **Code-side adaptations log:** [each adaptation: what, why, and confirmation the visual/behavioral result is identical to the design]

## 10. Faithfulness checklist (verified at Step 7)

- ☐ Every screen visually matches its artifact + SPEC (tokens, layout, spacing).
- ☐ Every documented state implemented and reachable.
- ☐ No invented values; every value traces to the token table or a SPEC reference.
- ☐ No interpreted behavior; every behavior traces to the interaction table.
- ☐ Reuse preserved — templates stayed single sources, no unjustified duplication.
- ☐ If an existing design system governs, every token, logo, and component matches its canonical source exactly; any divergence was raised as a Design Request, never a build-side creative choice.
- ☐ Every logo and icon present in both SVG and PNG; every asset used directly with no build-side transformation (any that would have required one was raised as a Design Request, not converted in the build).
- ☐ No placeholder copy shipped unless explicitly intended.
- ☐ Every external-setup step guided one at a time, every value traced to §7/SPEC, each verifiable step screenshot-confirmed before advancing; unverified steps flagged.
- ☐ Every externally generated asset built from its §8/SPEC entry, saved at the exact path/name/format, confirmed on-system; unverified assets flagged; no invented visual detail.
- ☐ Every code-side adaptation logged in §9 with design intent confirmed intact.
- ☐ Accessibility built to §4a / `SPEC/accessibility.md`: contrast pairs met, keyboard/AT operable, visible focus and specified focus order, name/role/state per state, headings/landmarks, target sizes, reduced-motion and text-scaling/high-contrast honored, error identification — verified with automated tools **and** a real assistive-tech pass (per `references/accessibility.md`).
- ☐ Zero unresolved Design Requests.
