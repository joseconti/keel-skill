# Phase 8 — Project Website: Domain Decision

A real decision tree for "dedicated domain vs subdomain of the user's existing domain", with the trade-offs that actually matter. Record the decision and its reasoning in the site's functional-spec doc (same doc as the section catalogue) and in `docs/decisions.md`; any manual DNS/registrar steps feed the Phase 4 guided one-step-at-a-time external-setup loop (never dumped as a doc).

## The two options

- **Dedicated domain** — e.g. `theproject.com`.
- **Subdomain of the user's existing domain** — e.g. `theproject.userdomain.com`.

## Decision factors (walk these honestly with the user)

- **Brand independence & memorability.** A dedicated domain stands alone and is easier to say/share; a subdomain ties the project's identity to the parent domain. If the project may be spun off, sold, or branded independently later, a dedicated domain is more portable — moving off a subdomain later means link/SEO migration.
- **Cost & setup.** A subdomain is free and uses existing DNS/TLS infrastructure (often a wildcard cert already covers it). A dedicated domain means registration cost, renewal, separate DNS, and its own TLS.
- **SEO.** Search engines may treat a subdomain somewhat separately from the root domain — it doesn't automatically inherit all of the parent's authority, though it's not penalised. A dedicated domain starts with no authority at all. For a small project site neither is decisive; be honest that domain choice is not an SEO silver bullet.
- **Trust signals.** A subdomain under an established, trusted parent domain can borrow credibility; a brand-new dedicated domain has none yet.
- **Operational simplicity.** Subdomain = one less thing to renew and secure. Dedicated = clean separation, no risk of the parent domain's issues affecting the project site.

## Recommendation logic

- Independent product/brand, possible future spin-off, commercial intent → lean **dedicated domain**.
- A tool/plugin closely tied to the user's existing brand, low budget, fast launch, no spin-off intent → lean **subdomain** of the user's domain (zero cost, reuses infra).
- State the recommendation with its reason; the user decides.

## Once decided — record and route the setup

- Record: chosen domain/subdomain, registrar (if dedicated), DNS provider, TLS approach (e.g. existing wildcard, new certificate, platform-managed).
- The concrete manual steps (DNS records, TLS issuance, registrar config) are NOT written as a document to follow alone. They go into the Phase 4 guided external-setup loop: one step at a time, the user confirms each (screenshot where verifiable) before the next. A value not specified is a Design/setup gap, not something to guess.
- If dedicated and not yet registered: suggest checking availability and sensible TLDs; do not assume or pick a registrar for the user.

## Definition of done (this reference)

- Dedicated vs subdomain decided with explicit reasoning.
- Exact domain/subdomain string recorded.
- DNS/TLS approach recorded and routed into the guided setup loop (not dumped).

Then complete the SEO plan (`references/phase-8-technical-seo.md`).
