# Changelog — Keel

All notable changes to the Keel skill are documented here.
Versions are listed oldest → newest (never inverted). Format groups: Added / Changed / Fixed.

## 1.0.0

Initial public release (GPL-3.0-or-later).

## 1.1.0

### Added
- Phase 8 Technical SEO & AEO: complete, verifiable spec for the full site-wide file set.
  - `robots.txt` with explicit per-bot policy for AI/answer-engine crawlers (ClaudeBot, PerplexityBot, OAI-SearchBot, Google-Extended, Applebot-Extended, GPTBot, anthropic-ai, CCBot, Bytespider, meta-externalagent) — the allow/disallow decision is the user's, recorded in discovery.
  - `sitemap.xml` with absolute URLs, `lastmod`, `xhtml:link hreflang` alternates for multilingual sites, sitemap index for large/multi-locale sites, image sitemap when warranted.
  - `humans.txt` referenced from the HTML.
  - `manifest.json` (web app manifest) with `theme_color`, icons including a maskable variant, self-hosted only.
  - `.well-known/security.txt` (RFC 9116) with `Contact`, future-dated `Expires`, `Canonical`, coordinated with the loaded security profile.
  - `llms.txt` (and optional `llms-full.txt`) as an AEO aid summarising the site for LLMs.
  - Favicon set: `favicon.ico`, `favicon.svg`, `apple-touch-icon.png`, manifest icons including a maskable variant.
  - Search-engine verification (Google Search Console, Bing Webmaster, IndexNow) when used.
  - Base `<head>` meta tag set explicit: charset, viewport, theme-color, color-scheme, referrer policy, format-detection, author.
  - Expanded JSON-LD coverage and rules: `WebSite` with `SearchAction`, `Organization`/`Person` with one canonical `@id`, `BreadcrumbList`, `WebPage`, `Article`/`BlogPosting`, `Product` with `Offer`, `VideoObject`, plus `SoftwareApplication`/`FAQPage`/`HowTo`. Inline-in-HTML rule, absolute URLs, consistency with rendered content.
  - Self-hosted fonts: `font-display: swap` and shipping only the actually-used weights/styles.
  - Compression, cache headers, HTTP/2 or HTTP/3, and resource hints (`preconnect`, `preload`) added as SEO-relevant transport items.
- Phase 8 Launch Checklist updated to fetch and verify every well-known file on the live domain, validate JSON-LD on live URLs, confirm the AI-crawler policy on `robots.txt`, and check self-hosted fonts in the network panel.
- Phase 8 Section Catalogue: site-wide deliverables (the well-known set) listed alongside page sections so they enter sitemap planning instead of being treated as launch-time extras.
- Three cross-cutting operating principles in SKILL.md:
  - **Reuse internal API; never duplicate code.** Search the existing API before writing new functions; generalize close fits instead of forking; duplication is a defect.
  - **Document every public surface at the moment it is created.** Each new function/method/class/hook/action/filter/REST route/MCP ability/CLI command is documented in `docs/api/` or `docs/reference/` as part of the same slice that introduces it; Phase 6 consolidates instead of writing from zero.
  - **Maximum extensibility for extensible project types** (WordPress/WooCommerce plugins, MCP servers, libraries/components): every user-facing string filterable, every meaningful decision exposes before/after actions, every query and response filterable, every public class replaceable. Decided at spec time, built into each slice.
- Phase 5 Development reflects the three principles operationally: per-slice checklist now includes search-before-writing, docs-at-creation, and extension-points-as-you-go; `docs/05-test-points.md` columns extended to record each; Definition of done enforces all three.
- Phase 6 Documentation rewritten as consolidation rather than creation. Undocumented public surfaces or missing extension points entering Phase 6 are Phase 5 defects to fix, not Phase 6 work.
- Phase 1 Discovery: new Step 0 — **Competitive scan**.
  - Always asks the user upfront which competitors they already know about.
  - Produces `docs/00-competitive-landscape.md` with per-competitor inventory (functionalities + license/pricing + status + cited sources), unified deduplicated feature list (de facto baseline for the category), and external-demand list (real user requests with citable sources).
  - Feeds `docs/01-discovery.md` with a "Competitive landscape & opportunity" section: table-stakes features, differentiator candidates, and optional AI/MCP/agentic layer proposals labelled as added-value or forced-filler (forced-filler dropped, not softened).
  - Cannot-research handling: when the environment lacks web/search, the assistant says so plainly with the specific reason and offers three options — move to a capable environment (preferred), use a different agent and bring findings back, or skip with an explicit warning block recorded verbatim in the discovery doc.
  - Definition of done updated; Phase 1 cannot complete without the scan being done or its absence explicitly recorded with the warning.

### Changed
- AEO section in technical SEO now explicitly references `llms.txt` and the per-bot `robots.txt` policy rather than only stating "don't block AI crawlers".
- SKILL.md phase map: Phase 1 description updated to "Competitive scan first, then idea, feature discussion, project type, constraints".
- Honest assessment in Phase 1 is now explicitly grounded in the competitive landscape (`docs/00-competitive-landscape.md`); without the landscape, the assessment is downgraded to opinion — the warning block makes this explicit.
- Version-change policy in SKILL.md hardened to unbreakable: version (`metadata.version`, heading line, `CHANGELOG.md`) is never bumped without explicit user instruction in the current conversation.

### Added
- Full idea-to-release multi-phase workflow with on-demand phase reference loading (progressive disclosure).
- Phase 1 Discovery: honest idea assessment (no default praise), project type fixing, installed-base/upgrade reality, fixed-version external dependencies, blocking multi-language vs single-language decision (function-wrapping and key/constant i18n models, base language as source of truth), project-website intent capture, design-needed decision.
- Phase 2 Functional Spec: flows, data model, integrations, permissions, design split (including external manual setup and assets Design can't produce), acceptance criteria.
- Phase 3 Design Handoff: brief enforcing build-once-reuse-by-manifest, ask-don't-invent, exact tokens, `external-setup.md` and `external-assets.md`, the shared handoff contract.
- Phase 4 Faithful Build: audit-first, consolidated BUILD-SPEC, zero-deviation build, one-step-at-a-time guided external setup, one-asset-at-a-time guided generation of images Design couldn't produce (adapting Design's base prompt to the user's chosen generator), two-branch failure handling, Design Request mechanism.
- Phase 5 Development: sprint planning, `docs/PROGRESS.md` living tracker, `docs/lessons-learned.md`, vertical slices with test points, live security profile, i18n build rule, migrations/backward-compat for installed base, fail-safe external dependencies, mandatory sprint close-out with archival to `docs/old/sprint-<N>/` and a self-sufficient continuation prompt for a fresh chat.
- Phase 6 Documentation: full `docs/` layout (architecture, API, usage, reference, security) with runnable examples; changelog ordering rule (oldest → newest).
- Phase 7 Release: `.gitignore` vs `.gitattributes` export-ignore boundaries, versioning, real-environment verification hard gate, release artifacts.
- Phase 8 Project Website (conditional): study the product → `docs/design/PRODUCT-BRIEF.md`; honest "is a site warranted?"; site type and the site's own blocking language decision; section catalogue & sitemap; dedicated-domain vs subdomain decision tree; design direction; vanilla-by-default (no frameworks/libraries/CDN unless a user-approved static-site-generator exception); self-hosted fonts with a guided procurement loop; product screenshots (Design reserves the slot, guided capture, build fits the CSS); technical SEO and AEO; real-environment launch checklist. Reuses Phases 3–7 rather than duplicating them.
- Per-platform security profiles: WordPress/WooCommerce, web app, MCP server, library/component.
- Shared templates: handoff contract, design brief, build spec, design request.
- Version reporting instruction and GPL-3.0-or-later licensing.
