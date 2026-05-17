# Phase 8 — Project Website (conditional)

Goal: plan and build the project's presentation/marketing website. This phase runs ONLY if Phase 1 recorded website intent (yes). It is normally done after the first release (Phase 7), but can be run later whenever the user is ready. If Phase 1 said no website, skip this phase entirely.

This phase is the former standalone `keel-web` skill, absorbed into Keel so there is no cross-skill dependency. A website is itself a "website" type project, so this phase **reuses Keel's own earlier phases** (3 design handoff, 4 faithful build, 5 development for dynamic parts, 6 documentation, 7 release) treating the site as the project — it does not restate that machinery. The web-specific thinking lives in the six `phase-8-*` references.

## When this runs

- Phase 1 `docs/01-discovery.md` recorded "project website: yes" (and own-domain vs subdomain intent).
- Typically after Phase 7. If the user isn't ready at release, Phase 7 reminds them; resume here later.

## Core stance (do not skip)

- **Assess honestly first.** Before building, judge whether a separate site is even warranted: maybe the marketplace/.org listing already does the job, maybe a README is enough, maybe a one-page landing beats a multi-page site. Say so with the reasoning — same honest-assessment principle as Phase 1. Do not build a bigger site than the project needs.
- **Reuse Keel's phases, don't reinvent.** Design handoff, faithful build, guided image generation, sprint tracking, security, release hygiene are Phases 3–7 — apply them to the site. The six references here only add the web-specific depth.
- **No deviation, no invention.** Same handoff contract and build faithfulness as Phase 4. Missing design detail → Design Request. Build once, reuse by manifest — never regenerate near-identical pages.
- **Vanilla by default; fonts and images self-contained.** Plain HTML/CSS/JS — no frameworks/libraries/CDN/runtime third-party scripts. The only exception is a user-approved static-site generator for a specific site type (e.g. docs micro-site), explicitly recorded; the assistant never decides this itself. Fonts always self-hosted via local `@font-face` (never Google Fonts/CDN), procured through a guided one-step-at-a-time loop. Images Design can't produce use the Phase 4 guided generation loop. Details in `references/phase-8-design-direction.md`.
- **Decide structure-shaping things before design.** Site type, site language (its own blocking decision), design direction, section set and domain are decided and recorded BEFORE the design handoff.

## Steps (web specifics layered on Keel's phases)

| Sub-step | Reuses Keel phase | Web reference to load |
|----------|-------------------|-----------------------|
| Study the product → `docs/design/PRODUCT-BRIEF.md` (what it is, what the site must show) | input to Phase 3 | `references/phase-8-site-discovery.md` (step 0) |
| Site discovery: honest "is it warranted?", purpose/CTA, site type, site language, content strategy | Phase 1 logic | `references/phase-8-site-discovery.md` |
| Section catalogue & sitemap; per-section spec | Phase 2 logic | `references/phase-8-section-catalogue.md` |
| Domain decision (dedicated vs subdomain) | Phase 2 logic | `references/phase-8-domain-decision.md` |
| Technical SEO + AEO plan | Phase 2 logic | `references/phase-8-technical-seo.md` |
| Design direction + vanilla/font constraints + reserved screenshot slots into the brief | Phase 3 (handoff contract + brief) | `references/phase-8-design-direction.md` |
| Faithful build; guided image generation; guided font procurement; guided screenshot capture + CSS-fit; guided DNS setup; SEO + AEO implemented | Phase 4 (as-is) | `references/phase-8-design-direction.md`, `references/phase-8-technical-seo.md` |
| Dynamic parts (forms/CMS) if any: sprints + test points | Phase 5 (as-is) | — |
| Site documentation (how to edit/deploy, SEO/AEO/domain as-built) | Phase 6 (as-is) | `references/phase-8-technical-seo.md` recap |
| Pre-launch real-environment verification | Phase 7 (as-is) | `references/phase-8-launch-checklist.md` |

Run order: study the product → discovery → sections/domain/SEO+AEO spec (all before design) → design handoff with direction (incl. reserved screenshot slots) → faithful build with guided fonts/images/screenshots and SEO+AEO → dynamic parts if any → docs → launch checklist.

## Definition of done

- `docs/design/PRODUCT-BRIEF.md` produced from studying the real product and handed to Design.
- Honest assessment recorded; site justified at the chosen size or a lighter alternative agreed.
- Site type and site language decided (the latter explicit, not silently inherited).
- Sitemap and per-section spec fixed before design; template-reuse identified.
- Domain decided with reasoning; DNS/TLS routed into the Phase 4 guided setup loop.
- Design direction (incl. vanilla + self-hosted fonts + reserved screenshot slots) in the brief; handoff satisfies the Phase 3 contract.
- Built faithfully (Phase 4); fonts self-hosted, images generated, product screenshots captured and CSS-fitted via guided loops; zero unresolved Design Requests.
- SEO and AEO present and verified per page.
- Real-environment launch verification passed (`references/phase-8-launch-checklist.md`).

This is the final phase. Report the launch summary to the user.
