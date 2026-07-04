# Phase 8 — Project Website: Section Catalogue & Sitemap

Run alongside Phase 2 (Functional Spec). This produces the sitemap and the exact section set per page, with required vs optional and the template-reuse logic — the depth the old skill lacked. Record it in the **site's** functional-spec doc (`docs/site/02-functional-spec.md`, or the site repo's `docs/02-functional-spec.md`) under "Site structure".

## How to use this

Take the site type from `references/phase-8-site-discovery.md` and assemble the section set from the catalogue below. For every section decide: included? with what content? what states (e.g. a form's empty/submitting/success/error)? Mark structurally-identical pages as template-reuse candidates so Design builds the template once and the manifest lists the rest — the same anti-token-waste rule as Phase 3/4.

## Section catalogue (pick per site type)

Sections are building blocks; not all apply to all site types. For each, "required" means the site usually fails its purpose without it.

- **Hero** — value proposition in one sentence + primary CTA. *Required for all types.* The single most important section.
- **Social proof** — logos, user counts, testimonials, ratings. Strong on landings/multi-page; optional for docs micro-sites.
- **Features / benefits** — what it does, framed as user benefit not feature list. *Required* for landing & multi-page.
- **How it works** — steps/flow, screenshots or short demo. Recommended when the value isn't obvious in one line.
- **Screenshots / demo / video** — visual proof. Images Design can't produce go to `external-assets.md` and the Phase 4 guided generation loop.
- **Pricing / licensing** — paid tiers, or an explicit "free / open-source (GPL)" statement. *Required* if there's any commercial aspect; for GPL projects state the license clearly.
- **Docs / getting-started entry** — link or embedded quickstart. *Required* for developer tools; *is* the core for a docs micro-site.
- **FAQ** — pre-empts support load and objections. Optional but high value.
- **Changelog / roadmap** — especially for plugins/tools with an installed base; ties to the changelog ordering (oldest → newest).
- **About / author** — trust, especially for independent/open-source projects.
- **Contact / support** — how to get help; if a form, spec its states and the anti-spam approach (the loaded security profile applies).
- **Legal** — privacy, cookies, imprint as required by jurisdiction; flagged in discovery.
- **Footer** — navigation, legal links, repo/license link, language switcher if multilingual.

## Sitemap by site type

- **One-page landing:** all chosen sections on a single page in priority order; anchors for navigation; one URL. No near-duplicate "pages".
- **Multi-page:** Home (hero + condensed highlights + CTA), then dedicated pages drawn from the catalogue (Features, Pricing, Docs entry, About, Contact, Legal). Pages that share structure (e.g. several content pages) are ONE template + manifest, never duplicated.
- **Docs micro-site:** thin marketing front (hero + getting-started CTA) + the docs system; treat docs navigation as a template.
- **Hybrid:** the explicitly listed pages only — do not let it grow silently.

## Per-section spec (feeds the keel design handoff)

For each included section record: purpose, content (final or marked placeholder), any states, responsive intent, and whether it reuses a template. This becomes part of what Design must specify in the handoff (Phase 3 contract). Anything left vague here is exactly what causes Design to guess later.

## Site-wide deliverables (not sections, but mandatory output)

In addition to the page sections above, the sitemap planning must list the site-wide files that ship with every site. They are produced in the build, not in design, but they are decided here because they affect content and discovery decisions:

- `robots.txt` (with the explicit AI-crawler policy decided in discovery)
- `sitemap.xml` (or a sitemap index, with `hreflang` alternates if multilingual)
- `humans.txt`
- `manifest.json` (PWA web app manifest)
- `.well-known/security.txt` (coordinated with the loaded security profile)
- `llms.txt` (AEO summary for LLMs)
- Favicon set (`favicon.ico`, `favicon.svg`, `apple-touch-icon.png`, manifest icons including a maskable variant)
- Search-engine verification files (Google Search Console / Bing Webmaster / IndexNow) — only if the user actually uses those platforms

Specifics for each live in `references/phase-8-technical-seo.md`. List them here so they appear in the sitemap planning and don't get forgotten as "extras" at launch.

## Definition of done (this reference)

- Sitemap fixed for the chosen site type.
- Every page's section set decided, with content (or marked placeholder) and states.
- Template-reuse candidates identified; no plan to duplicate near-identical pages.
- Required sections for the type are all present or their absence is justified.

Then do the domain decision (`references/phase-8-domain-decision.md`) and the SEO plan (`references/phase-8-technical-seo.md`).
