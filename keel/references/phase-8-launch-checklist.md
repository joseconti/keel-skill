# Phase 8 — Project Website: Launch Checklist

Phase 7 already enforces a real-environment verification hard gate, git/package hygiene, and versioning. This adds the website-specific launch checks. A failure here blocks the launch — same rule as the rest of Keel: "it works on the real domain" is not "it built locally".

## Launch report — every check leaves a row (read first)

Every check in this file lands as a row in `<site-docs>/launch-report.md`: item, how it was verified (the exact command/tool/step), result, date. An item without its row is NOT verified — "checked it" with no row does not count. The checks split two ways:

- **Assistant-verifiable** — `curl` checks, fetching the well-known files, parsing each page's `<head>`, JSON-LD validation, sitemap coverage, the automated accessibility scan: the assistant executes them itself and records command + output in the row.
- **User-guided** — checks needing the user's hands or accounts (OG/social debuggers that need a login, the real assistive-technology pass): run as guided one-step-at-a-time loops, each step's confirmation recorded in the row.

When the environment provides the subagents defined in `references/assistant-config.md`, delegate: **`launch-verifier`** crawls the sitemap and returns the pass/fail table that feeds `launch-report.md`; **`a11y-auditor`** runs the automated accessibility pass and prepares the guided-loop script for the manual one. The main session validates and records their results; it does not re-crawl.

## Real-environment verification (hard gate)

Deploy the exact site to the actual host and the decided domain/subdomain (or a staging that mirrors it), then verify there — not locally:

- The domain/subdomain resolves as decided; HTTPS valid; HTTP→HTTPS redirect works; www/non-www consolidated.
- Every page loads; every internal link works; no broken assets; generated images present at the correct paths/sizes (from the Phase 4 guided generation loop).
- Every form (contact/signup) submits, shows its success and error states, and anti-spam works (the loaded security profile).
- If multilingual: every locale renders, the language switcher works, `hreflang` is correct.

## SEO & AEO presence (verified per page, not assumed)

Walk `references/phase-8-technical-seo.md` against the live site:

### Per-page (every page on the sitemap)

Derive the page list from `sitemap.xml` and check EVERY page on it. Title/description/`og:url` uniqueness is only provable over the full list — sampling one page per template proves the template, not the site, and is not sufficient.

- Unique title + meta description + single h1 + canonical on every page.
- Base `<head>` meta tags present: charset, viewport, theme-color, color-scheme (if used), referrer policy, author.
- **Open Graph / Twitter card complete on every page** — verify each required tag is actually present, not merely that "something renders":
  - `og:title`, `og:description`, `og:url` (absolute, = canonical), `og:type` and `og:image` all present. The classic failure is `og:image` present while `og:title`/`og:description`/`og:url` are missing — the card then renders blank or not at all.
  - `og:image` is an **absolute HTTPS URL** returning `200`, 1200×630, PNG/JPEG, under ~5 MB, with `og:image:width`/`height`/`alt` set.
  - `twitter:card` set (`summary_large_image`) plus `twitter:title`/`description`/`image`.
  - OG values are **per page** (not the home block copied everywhere): titles, descriptions and `og:url` differ per page.
  - Validated on the live URL in Facebook Sharing Debugger, X Card Validator and LinkedIn Post Inspector (which also force a re-scrape of any cached blank card) — on the deployed domain, not source HTML or localhost.
- `lang` attribute correct; if multilingual, `hreflang` alternates resolve correctly on every locale.

### Site-wide files (fetch each at its absolute URL and inspect)

- `/robots.txt` — reachable, served as `text/plain`, references the absolute sitemap URL, does not block the live site, and contains explicit `User-agent` blocks for the AI crawlers chosen in discovery (allowed or disallowed by user decision — recorded, not assumed).
- `/sitemap.xml` — reachable, contains only canonical URLs on the canonical host, `<lastmod>` reflects real changes, `hreflang` alternates present and consistent on multilingual sites, no 404 entries.
- `/humans.txt` — reachable, served as `text/plain`, linked from the HTML via `<link rel="author" type="text/plain">`.
- `/manifest.json` — reachable, valid JSON, `theme_color` matches the `<meta name="theme-color">`, icons resolve (including a maskable variant), no external/CDN references.
- `/.well-known/security.txt` — reachable, valid `Contact`, future-dated `Expires` (rotate before expiry), `Canonical` self-referential. Coordinated with the loaded security profile.
- `/llms.txt` — reachable, served as `text/plain`, summarises the site for LLMs and links the pages they should read first.
- Favicons all resolve: `/favicon.ico`, `/favicon.svg`, `/apple-touch-icon.png` (180×180), manifest icons (192/512 and a maskable variant). `<link>` declarations in `<head>` all 200.
- Search-engine verification (if used): Search Console / Bing Webmaster / IndexNow file or DNS TXT verified on the live domain.

### Structured data

- Structured data validates on the **live URLs** (not localhost) with a structured-data validator (`SoftwareApplication`, `WebSite` with `SearchAction`, `Organization`/`Person`, `BreadcrumbList`, `FAQPage`, `HowTo`, `Article`, `Product` as applicable).
- JSON-LD is inline in the HTML (curl/view-source confirms it — not injected by JS).
- A single canonical `Organization`/`Person` `@id` is reused via reference across pages — not redefined per page.
- Every URL inside JSON-LD is absolute and matches the canonical host.

### AEO behaviour

- Answer-first passages (~40–60 words) under question-style headings; key content present in the HTML (`curl` returns the answer text, not a JS shell).
- Concrete facts (versions / requirements / price) accurate and consistent with the listing/repo/changelog.
- Authorship/E-E-A-T visible on the page and matches the `Person`/`Organization` JSON-LD.
- `robots.txt` AI-crawler policy matches the discovery decision.
- `llms.txt` reflects the actual site (no dead links, summary current).

### Performance & headers

- Mobile performance acceptable on the deployed site, not just in dev (Core Web Vitals: LCP/CLS/INP). Accessibility is verified in its own section below.
- Self-hosted fonts load locally only (no Google Fonts/CDN request in the network panel); `font-display: swap` applied.
- Compression (gzip/brotli) and sane `Cache-Control` headers on static assets; HTML not aggressively cached.
- HTTPS canonical-host redirect works (the non-canonical host 301s to the canonical one).

## Security headers & forms

Per the website security profile loaded at the start of Phase 8 (`references/security/website.md`):

- **Header set verified with `curl -sI` on the live site** — the exact expected set lives in the security profile; record the command and the returned headers in the launch report.
- **Anti-spam exercised for real, not assumed:** submit with the honeypot field filled → rejected; N rapid submissions → rate-limited. Record both results.
- **Email deliverability:** send a real test message through the form and confirm SPF/DKIM/DMARC alignment on the received message (inspect its headers) — contact mail that lands in spam is a launch failure.

## Accessibility (hard gate — verified with real assistive technology on the live site)

Per the Web/HTML section of `references/accessibility.md` and the Phase 1 commitment. Verify on the deployed site, not just in dev — automated tooling alone is insufficient. The manual passes below run as the guided assistive-technology pass in `references/accessibility.md` — one step at a time, the user confirms each — with results recorded in `docs/accessibility.md`:

- **Keyboard-only:** every interactive element reachable and operable, logical focus order, visible focus, no keyboard trap, the skip link works, focus not obscured by sticky headers/overlays.
- **Screen-reader pass** (VoiceOver / NVDA): landmarks and a single-`h1` heading outline are navigable; every control exposes an accessible name/role/state; images have correct text alternatives (decorative ones empty); forms have associated labels and errors are announced.
- **Contrast:** every text and UI-object pair meets WCAG 2.2 AA (4.5:1 text / 3:1 large text and UI objects) — measured, not eyeballed.
- **Reflow & text scaling:** usable at 200% text and 320px reflow with no clipping, overlap, or loss of content/function.
- **User preferences honored:** `prefers-reduced-motion`, `prefers-contrast` / forced-colors (Windows High Contrast), `prefers-color-scheme`.
- **Automated scan over the full sitemap URL list** (e.g. `pa11y-ci --sitemap <url>`, or axe-core run across every URL from `sitemap.xml`), executed by the assistant (or the `a11y-auditor` subagent), clean of violations — as a complement to, never a replacement for, the manual passes above.
- **Accessibility statement** (when EU scope applies): the page from the section catalogue exists and is linked, and its conformance status and known gaps match `docs/accessibility.md`.
- The result meets WCAG 2.2 AA (AAA where reached) or the shortfall is honestly recorded in `docs/accessibility.md` (no overlay, no false conformance claim).

## Screenshots & generated assets

- Every reserved screenshot slot is filled with the real product screenshot specified in `SPEC/screenshots.md`, at the right path/name/type, and the slot CSS was adjusted so it sits well (no deformed image, no design change).
- Generated images/fonts from the guided loops are present, correct, and self-hosted (no CDN/Google Fonts request on the live site).

## Content & legal

- No placeholder copy shipped (placeholders were marked in discovery — confirm none remain).
- Required legal pages present and linked (privacy/cookies/imprint as flagged in discovery).
- **Analytics matches the discovery decision:** if "none", the network panel shows zero tracking requests; if self-hosted, only the self-hosted endpoint; if third-party, it is the explicitly approved exception. If tracking uses cookies/identifiers in EU scope: consent is requested first, nothing fires before consent, and the cookie/privacy pages describe it accurately.
- License stated where relevant (e.g. GPL/open-source statement); repo link works if applicable.

## Faithfulness & hygiene (reuse keel)

- Phase 4 faithfulness checklist still holds on the deployed site (it matches the design SPEC, no drift).
- **Vanilla verified:** no framework/library/CDN crept in; no runtime third-party scripts; if a static-site generator was used it was the explicitly user-approved exception, recorded. **Fonts verified self-hosted:** no Google Fonts/CDN font requests on the live site (check network requests); every font loads from local `@font-face`; only the declared weights/styles shipped.
- Phase 7 git/package hygiene done: `.gitignore`/`.gitattributes` correct, no secrets committed, distributable/deploy artifact clean.
- Version and changelog updated (oldest → newest) if the site is itself versioned/released.

## After launch — operations

Launch is not the end state. Record the site's operational duties in `<site-docs>/operations.md` before closing the phase:

- **Renewal dates:** domain renewal; TLS renewal if manually managed (platform-managed: note the platform instead); `security.txt` `Expires` — rotate before expiry.
- **Uptime monitoring:** which check is in place (service, URL, alert target) — or the recorded decision not to have one. Never silently none.
- **Backups:** where site backups live and how to restore — or why none is needed (e.g. the site is fully reproducible from the repo), recorded.
- **Sitemap submitted to Search Console** (and Bing Webmaster if used) — a guided user loop, it needs the user's account; recheck coverage once indexed (pages discovered, no unexpected exclusions).
- **Standing freshness duty:** from now on every product release (Phase 7) triggers the site-freshness mini-checklist — JSON-LD `softwareVersion`, the changelog/news page, screenshots if the UI changed, `sitemap.xml` `lastmod`, `llms.txt` — per `references/maintenance.md`.

## Definition of done (this reference)

- Every check in this file has its row in `<site-docs>/launch-report.md` (item, how verified, result, date) — no row, not verified.
- Real-environment verification passed on the actual domain.
- SEO present and correct on every live page (the full `sitemap.xml` list, not a sample); the full well-known set (`robots.txt`, `sitemap.xml`, `humans.txt`, `manifest.json`, `.well-known/security.txt`, `llms.txt`, favicons) reachable and valid.
- Structured data validates live; AEO checks (answer-first, HTML-extractable, AI-crawler policy, `llms.txt`) all green.
- Security headers verified live with `curl -sI` per `references/security/website.md`; form anti-spam exercised for real (honeypot, rate limit); SPF/DKIM/DMARC aligned on a received test message.
- Accessibility verified on the live site with real assistive technology (WCAG 2.2 AA floor: keyboard, screen reader, contrast, reflow, honored user preferences) per `references/accessibility.md`; accessibility statement present and linked when EU scope applies.
- No placeholder/legal gaps.
- Faithfulness to design holds live; hygiene done.
- `<site-docs>/operations.md` produced: renewals, monitoring decision, backups, sitemap submission, standing freshness duty (`references/maintenance.md`).

Only then is the site launched and the phase closed. Note completion back in the project tracking (docs/PROGRESS.md).
