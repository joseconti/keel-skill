# Phase 8 — Project Website: Site Discovery

Run alongside Phase 1 (Discovery), treating the website as the project. This adds the web-specific decisions the generic discovery doesn't cover. Record everything in the **site's** discovery doc — `docs/site/01-discovery.md` when the site shares the product repo, or the site repo's own `docs/01-discovery.md` (per the "Where the site lives" decision in `references/phase-8-website.md`).

## 0. Study the product first (mandatory input for Design)

Before honest assessment, sections, or any handoff, study the actual product the site is about — the plugin/app/MCP server/library itself, the real thing, not assumptions. Design cannot design the site of a plugin without knowing what the plugin does; if it doesn't have this, it invents.

- Inspect the real product: what it does, its concrete features, its screens/admin pages, its public surfaces (REST routes, MCP abilities, WP-CLI, hooks), pricing/licensing, requirements/dependencies, what makes it different. If the product was built with Keel, its `docs/` already has most of this — read it (start at `docs/api/INDEX.md`, `docs/architecture.md`, `docs/01-discovery.md`); do not re-derive what's documented.
- Produce `<site-docs>/design/PRODUCT-BRIEF.md` (path per the "Where the site lives" decision): a clear statement of **what the product is and therefore what the site must communicate and show** — the value proposition, the features worth a section, the screens worth a screenshot, the audience, the primary action. This is a required input to the Phase 3 design handoff: it goes to Design alongside everything else so Design knows what to build and what each section is about.
- Anything you cannot determine about the product is a question for the user now — never invented into the brief.

## 1. Honest assessment — is a separate site even warranted?

Before any planning, say the truth (mirrors the honest-assessment principle):

- Does the project already have a sufficient presence (a good WordPress.org/marketplace listing, a solid README, existing docs)? If so, a separate site may add little — say that.
- Is the goal something a single page can do, or does it genuinely need multiple pages?
- Who actually visits a project site like this, and would they convert better via the listing or a site?

Do not build a bigger site than the project needs. State the recommendation and let the user decide with full information.

## 2. Purpose, audience, primary CTA

- The single most important action a visitor should take: install/download, read docs, buy/upgrade, sign up, contribute, contact.
- Secondary actions, ranked.
- Audience: developers? end users? buyers? Each implies different content and tone.

## 3. Site type (blocking decision — drives sections, SEO, effort)

Pick exactly one primary type. This is the website equivalent of the "project type" and it shapes everything downstream:

- **One-page landing** — a single scrolling page, one primary CTA. Best when the message is focused and conversion is the only goal. Lowest cost; SEO concentrated on one URL.
- **Multi-page site** — home + dedicated pages (features, pricing, docs entry, about, contact, etc.). Best when there are distinct audiences or content depth, or SEO needs multiple targeted URLs.
- **Docs/reference micro-site** — primarily documentation with a thin marketing front. Best for developer tools/libraries where the docs *are* the product pitch.
- **Hybrid** — a landing plus a small set of pages. State explicitly which pages, so it doesn't silently grow into an unplanned multi-page site.

Record the chosen type and the reason. If the user wants multi-page but the content doesn't justify it, say so (it dilutes SEO and adds maintenance for empty pages).

## 4. Site language — multi-language or not (blocking decision, the site's own)

This is a decision in its own right, not an implicit inheritance. A project can be multi-language while its site is single-language, or vice versa — so decide and record it explicitly, before design, with the same blocking logic as the Phase 1 i18n decision (retrofitting a multilingual site is a rewrite, not a tweak):

- **Is the site multi-language or single-language?** Decide this independently of the product, then sanity-check it against the project's i18n decision from Phase 1 (e.g. it's odd to ship a single-language site for a product translated into 5 locales — raise it, don't just inherit silently).
- If multi-language: the **base language**, the target locales, and the mechanism for a (preferably vanilla) site — typically one set of pages per locale with correct `lang`/`hreflang`, a language switcher in the footer, and no machine-translation placeholder shipped as final.
- If single-language: state which language and that it's intentional, so future translation isn't an accidental rewrite.

## 5. Content strategy (decide now, not during build)

- Who writes the copy: the user provides final copy, or placeholder is used? If placeholder, it must be clearly marked so it's never shipped (same rule as the rest of Keel).
- Tone of voice, in one or two lines, so Design and copy stay consistent.
- Legal/compliance content needed (privacy, cookies, imprint) — flag now; it becomes required sections.
- **Analytics & consent (decide now, not at launch).** Options, in order of preference under the vanilla rule: **none** (default — a project site often doesn't need it), **self-hosted analytics** (e.g. a self-hosted Matomo/Plausible — still a conscious addition, recorded), or **third-party analytics** (a runtime third-party script: this is an exception to the vanilla rule and requires explicit user approval, recorded). If any analytics uses cookies/identifiers and the audience includes the EU: consent management and the cookie/privacy pages become REQUIRED sections, and nothing tracks before consent. Record the decision; the launch checklist verifies it.

## 6. Constraints

- Where it will be hosted/deployed (static host, the user's existing hosting, a platform), since it affects the domain decision and the launch checklist.
- Brand assets available (logo, palette) or to be created.
- Performance expectations, and accessibility — non-negotiable and inherited from the Phase 1 commitment: the site targets WCAG 2.2 AA (AAA where feasible; EN 301 549 / EAA in EU scope) per `references/accessibility.md`, verified with real assistive technology at launch. Both are also SEO/quality gates.

## Definition of done (this reference)

- Site location decided (own repo vs `docs/site/` in the product repo) per `references/phase-8-website.md`.
- `<site-docs>/design/PRODUCT-BRIEF.md` produced from studying the real product — what it is and what the site must communicate/show; queued as a required input to the Phase 3 handoff.
- Honest assessment recorded; site justified at the chosen size or a lighter alternative agreed.
- Purpose and primary CTA explicit.
- Site type chosen and justified.
- Site language decided explicitly (multi vs single, base language if multi), sanity-checked against the project's i18n decision — not silently inherited.
- Content strategy decided, including the analytics & consent decision (none / self-hosted / third-party with explicit approval; consent + legal pages required if tracking in EU scope).
- Constraints captured.

Only then proceed to the section catalogue (`references/phase-8-section-catalogue.md`).
