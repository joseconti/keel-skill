# Changelog — Keel

All notable changes to the Keel skill are documented here.
Versions are listed oldest → newest (never inverted). Format groups: Added / Changed / Fixed.

## 1.0.0

Initial public release (GPL-3.0-or-later).

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
