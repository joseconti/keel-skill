# Phase 4 — Faithful Build

Goal: take Design's returned handoff and build exactly that — audit first, consolidate one spec, then build with zero deviation. Code adapts to the design, never the reverse. Where the project needs a human to configure external software, guide them one verified step at a time. This phase absorbs the former `code-faithful-build` skill.

Read `references/handoff-contract.md`, `references/build-spec-template.md`, and `references/design-request-template.md` before starting.

## Non-negotiable rules (whole phase)

1. Do not start coding until the spec is fully consolidated and verified.
2. Do not invent. Missing value/state/behavior/asset/copy is never made up.
3. Do not interpret. Ambiguity is a Design Request, not a choice.
4. Do not deviate. Build matches artifacts + SPEC exactly.
5. Code adapts to the design — never the design to the code.
6. Missing → ask Design (Design Request), not yourself.

State these back to the user when the phase starts.

## Step 1 — Audit the handoff (no code yet) — the completeness gate, run FIRST

The very first thing done when Design's handoff arrives — before any consolidation and long before any code — is to verify Design delivered **everything, without exception**. Nothing downstream is trusted until this gate passes. If anything at all is missing or incomplete, it is not filled in on the build side and it is not worked around: it is written up as a Design Request (Step 3) — a registered file plus a ready-to-paste prompt — so Design finishes and re-delivers the missing pieces. The build never compensates for an incomplete handoff.

Input is `docs/design/design-handoff/`. Check against `references/handoff-contract.md`:

- `SPEC/manifest.md` — every page resolves to a unique page or template + concrete data?
- `SPEC/design-tokens.md` vs `artifacts/styles/` — values agree? Any token referenced but undefined? If the project card records an **existing** design system: do the delivered tokens, logo usage, and component styles match its canonical source exactly? Any unexplained divergence from the brand's canonical system is a gap (Design Request), not a creative choice — the build never "improves" or reinterprets the design system.
- `SPEC/screens/*.md` — every unique screen documents its purpose/functionalities (what it does, not just how it looks) and all states + breakpoints + role/plan variants?
- `SPEC/interactions.md` — every behavior/conditional/transition specified?
- `SPEC/assets-index.md` — every referenced asset exists in `artifacts/assets/` with size/format? **Every logo and icon present in BOTH SVG and PNG?** Is every asset in a format the build uses directly — nothing that would force a build-side conversion, resize, recolor, rasterize, or re-export? An asset shipped in an inconvenient format, or a logo/icon missing one of the two formats, is a gap (Design Request), not a build-side fix. Per `references/handoff-contract.md` rule 4.
- `SPEC/external-assets.md` — for any asset Design couldn't produce, is there full generation detail (role, location, filename, format, dimensions, visual description, palette/style from tokens)? Any asset that's a silent gap or unlabeled placeholder instead of declared here is a gap. If "none", confirm no such assets are actually needed.
- `SPEC/external-setup.md` — if external software must be configured by hand, is EVERY value present (software/version, exact path, each field, each value/toggle, order)? Anything implicit in an artifact instead of here is a gap. If "none", confirm nothing actually requires manual setup.
- `SPEC/accessibility.md` — present and complete (contrast-verified pairs with ratios, visible focus + focus order, accessible name/role/state per component and state, heading/landmark structure, target sizes, reduced-motion variants, text-scaling/high-contrast behavior, error identification)? Is per-screen accessibility present in each `SPEC/screens/*.md`? A missing or thin accessibility spec is a gap — the build must not invent it. Per `references/accessibility.md`.
- `SPEC/open-questions.md` — empty/resolved? Any item is a hard blocker.
- `SPEC/screenshots.md` — only for website projects (Phase 8): every reserved product-screenshot slot declared with target screen/state, approximate size, and slot CSS (per `references/phase-8-design-direction.md`)? For non-website projects this file is not expected.
- Any placeholder copy that would otherwise ship?

Record every discrepancy as a gap (what, where expected, why it blocks faithful build).

## Step 2 — Consolidate `BUILD-SPEC.md` (still no code)

Fill `references/build-spec-template.md` into `docs/BUILD-SPEC.md`: resolved screen list, exact token table, per-screen state matrix, interaction table, asset map, external-setup table (each value traced to SPEC), target-stack integration plan (the only place code-side adaptation is allowed, never altering design intent), and the faithfulness checklist. This document is reviewable by the user before any code exists and is what the build will not deviate from.

## Step 3 — Gaps → Design Request (do NOT build)

If Step 1 found any gap or `open-questions.md` is unresolved: do not proceed, do not guess. Fill `references/design-request-template.md` and give it to the user as a ready-to-paste prompt for Design. It names exactly what's missing, asks Design to fill only that (asking the user where it's the user's call), keep the handoff structure, and not redesign what works. Building resumes only after Design re-delivers and Step 1 re-passes.

**Register every Design Request before handing it over** (per `references/project-state.md`): save the filled template as `docs/design/design-requests/DR-NNN.md` (sequential numbering) with a `Status: sent` line at the top, and list it under "Open items" in `docs/PROGRESS.md`. When Design re-delivers and the re-audit passes, mark the DR `Status: resolved [date]` and clear it from PROGRESS.md. A fresh session must be able to see from the register alone which requests are still open — "zero unresolved Design Requests" is always verified against the register, never against memory.

## Step 4 — Build, faithfully

Only when `docs/BUILD-SPEC.md` is complete and gap-free:

- Port real artifacts into the target stack. Templates stay templates; don't flatten into N duplicated pages, don't duplicate where Design unified.
- Match tokens exactly. No "close enough".
- Implement every state in the state matrix; a screen isn't done until every documented state is built.
- Implement the accessibility spec exactly (`SPEC/accessibility.md`): accessible name/role/state for every component and state, keyboard/assistive-tech operability, visible focus and the specified focus order, target sizes, reduced-motion variants, and error identification. A screen isn't done until its accessibility is built and verified, per `references/accessibility.md`.
- Where the stack forces a change, change the code strategy and log it in `BUILD-SPEC.md` integration notes — never alter the design.
- Mid-build unspecified discovery → stop, return to Step 3 for that item.

Steps 4–6 may interleave when the work requires it (e.g. an external-setup value is a build prerequisite, or an asset is needed by the slice being built): run the relevant Step 5/6 loop item at the moment the build needs it, under exactly the same rules. Interleaving changes the order, never the rules — each setup step and each asset still goes one at a time, verified, traced to the SPEC.

## Step 5 — Guide external manual setup, one verified step at a time

External software the builder can't script (Unity, hosting panel, OAuth console, SaaS settings, DNS, payment gateway) is NOT delivered as a big document. A long doc is heavy to follow and a mistake surfaces only after hundreds of steps and wasted hours. Run an interactive loop over `SPEC/external-setup.md` in its exact order:

1. Give exactly ONE step: precise location inside the software, exact field, exact value — read straight from the SPEC, citing which SPEC entry. Never improvise a value.
2. Ask the user to do that one step and report back when done. Don't send the next step yet.
3. Ask for a screenshot when the step is verifiable; inspect it against the expected result before moving on.
4. Advance only when confirmed. If wrong, stay on this step and help fix it.

When the user says "I can't find what you're telling me", diagnose — do not guess a workaround:

- **Value/step was not actually in `SPEC/external-setup.md`** (Design left it implicit): stop, do not invent, generate a Design Request (Step 3) for that specific missing detail. Resume after Design re-delivers.
- **Value IS in the SPEC but the external UI doesn't match** (version/relocation): design is not at fault, SPEC value does not change. Stay on the step, mark it **unverified**, work it out with the user there (find the equivalent option, confirm via screenshot). Don't skip ahead, don't alter the SPEC.

Never collapse these two branches: guessing reintroduces the exact defect this skill prevents; bouncing a Design Request when the value was fine just blocks the user needlessly.

## Step 6 — Guide generation of assets Design couldn't produce, one asset at a time

Some assets (photos, complex illustrations, 3D renders) can't be produced by Design or scripted by the builder. Design has declared each in `SPEC/external-assets.md` with an explanation and a ready base prompt it wrote. Do NOT invent them, do NOT ship an unlabeled placeholder, and do NOT dump all prompts at once — if the user generates a dozen images and the first didn't fit (aspect, background, style), all that work is wasted. Run an interactive, one-asset-at-a-time loop.

First, **tell the user plainly that Design could not generate these images itself**, so you'll guide them to generate each one. Then, once per project, ask which image generator they'll use (e.g. Gemini, or another). You will *adapt* Design's base prompts to that generator — you do not author new visual content. If they don't know, hand Design's base prompt as-is (it's generator-neutral) and note common adjustments.

Then, for each asset in `SPEC/external-assets.md`, one at a time:

1. **Adapt Design's base prompt to the chosen generator.** Take the base prompt verbatim from the SPEC entry and only rephrase it / add tool-specific guidance for that generator. Every descriptive element must trace to `SPEC/external-assets.md` (and `design-tokens.md`). Never add or invent visual details Design didn't put in the base prompt — if the base prompt is missing something needed, that's the failure branch below, not a place to improvise.
2. **Give the user exactly ONE adapted prompt**, plus the exact place to save the result: target directory (so it lands where `assets-index.md`/the build expects, normally `artifacts/assets/...`), the exact filename, and the format (and intrinsic dimensions/aspect ratio from the SPEC).
3. **Ask the user to generate it, save it exactly as instructed, and report back / show the result.** Don't send the next asset's prompt yet.
4. **Confirm the asset fits** (right subject, style on-system, correct dimensions/format, saved at the right path/name) before moving on. If it's off, re-adapt against Design's base prompt and retry — do not lower the design bar to accept a mismatch.

When the user can't produce a faithful asset, diagnose — don't guess:

- **Design's base prompt was missing or too thin to adapt faithfully** (Design under-specified it): stop, do not invent the missing visual detail to fill the gap, generate a Design Request (Step 3) for that specific asset's missing base prompt / specification. Resume after Design re-delivers.
- **Design's base prompt is sufficient but the generator can't match it** (tool limitation, e.g. won't hold an aspect ratio): the design isn't at fault and the SPEC doesn't change. Stay on this asset, mark it **unverified**, and work it out with the user (re-adapt within the base prompt's bounds, try crop/resize to the SPEC's exact dimensions, or try another generator). Don't skip ahead and don't alter the SPEC's intent.

Never collapse these two branches: inventing a visual detail reintroduces the exact defect this skill prevents; bouncing a Design Request when the spec was fine just blocks the user.

Once an asset is confirmed and saved at its target path/name, treat it as a real artifact: it must satisfy `assets-index.md` exactly like any Design-produced asset.

## Step 7 — Verify against the faithfulness checklist

Walk the checklist in `docs/BUILD-SPEC.md`: every screen matches artifact+SPEC; every state exists and is reachable; no invented values/behavior; no unintended placeholder copy; reuse preserved; if an existing design system governs, every token/logo/component matches its canonical source (any divergence was a Design Request, never a build-side choice); every logo/icon present in both SVG and PNG and every asset used directly with no build-side transformation; every external-setup step guided one at a time with traced values and screenshot confirmation (unverified flagged); every external asset generated from the SPEC, saved at its exact path/name/format, and confirmed (unverified flagged); accessibility built to `SPEC/accessibility.md` and verified (automated checks plus a real assistive-tech pass); every code-side adaptation logged with design intent intact; zero unresolved Design Requests. Report results. A failure is a build defect (fix code) or a genuine gap (Design Request) — never a reason to relax the design.

## Definition of done

`docs/BUILD-SPEC.md` complete and gap-free, build matches it, external setup verified or explicitly flagged, every external asset generated and placed or explicitly flagged, accessibility built to `SPEC/accessibility.md` and verified (automated + real assistive-tech pass), faithfulness checklist passed, Design Request register shows zero open DRs, and `docs/PROGRESS.md` updated. Then Phase 5.
