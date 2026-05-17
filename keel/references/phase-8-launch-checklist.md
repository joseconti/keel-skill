# Phase 8 — Project Website: Launch Checklist

Phase 7 already enforces a real-environment verification hard gate, git/package hygiene, and versioning. This adds the website-specific launch checks. A failure here blocks the launch — same rule as the rest of Keel: "it works on the real domain" is not "it built locally".

## Real-environment verification (hard gate)

Deploy the exact site to the actual host and the decided domain/subdomain (or a staging that mirrors it), then verify there — not locally:

- The domain/subdomain resolves as decided; HTTPS valid; HTTP→HTTPS redirect works; www/non-www consolidated.
- Every page loads; every internal link works; no broken assets; generated images present at the correct paths/sizes (from the Phase 4 guided generation loop).
- Every form (contact/signup) submits, shows its success and error states, and anti-spam works (the loaded security profile).
- If multilingual: every locale renders, the language switcher works, `hreflang` is correct.

## SEO & AEO presence (verified per page, not assumed)

Walk `references/phase-8-technical-seo.md` against the live site:

### Per-page (sample every distinct template)

- Unique title + meta description + single h1 + canonical on every page.
- Base `<head>` meta tags present: charset, viewport, theme-color, color-scheme (if used), referrer policy, author.
- OG/Twitter render correctly when a URL is shared (test with a real share/preview, not just the source HTML).
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

- Mobile performance and accessibility acceptable on the deployed site, not just in dev (Core Web Vitals: LCP/CLS/INP).
- Self-hosted fonts load locally only (no Google Fonts/CDN request in the network panel); `font-display: swap` applied.
- Compression (gzip/brotli) and sane `Cache-Control` headers on static assets; HTML not aggressively cached.
- HTTPS canonical-host redirect works (the non-canonical host 301s to the canonical one).

## Screenshots & generated assets

- Every reserved screenshot slot is filled with the real product screenshot specified in `SPEC/screenshots.md`, at the right path/name/type, and the slot CSS was adjusted so it sits well (no deformed image, no design change).
- Generated images/fonts from the guided loops are present, correct, and self-hosted (no CDN/Google Fonts request on the live site).

## Content & legal

- No placeholder copy shipped (placeholders were marked in discovery — confirm none remain).
- Required legal pages present and linked (privacy/cookies/imprint as flagged in discovery).
- License stated where relevant (e.g. GPL/open-source statement); repo link works if applicable.

## Faithfulness & hygiene (reuse keel)

- Phase 4 faithfulness checklist still holds on the deployed site (it matches the design SPEC, no drift).
- **Vanilla verified:** no framework/library/CDN crept in; no runtime third-party scripts; if a static-site generator was used it was the explicitly user-approved exception, recorded. **Fonts verified self-hosted:** no Google Fonts/CDN font requests on the live site (check network requests); every font loads from local `@font-face`; only the declared weights/styles shipped.
- Phase 7 git/package hygiene done: `.gitignore`/`.gitattributes` correct, no secrets committed, distributable/deploy artifact clean.
- Version and changelog updated (oldest → newest) if the site is itself versioned/released.

## Definition of done (this reference)

- Real-environment verification passed on the actual domain.
- SEO present and correct on every live page; the full well-known set (`robots.txt`, `sitemap.xml`, `humans.txt`, `manifest.json`, `.well-known/security.txt`, `llms.txt`, favicons) reachable and valid.
- Structured data validates live; AEO checks (answer-first, HTML-extractable, AI-crawler policy, `llms.txt`) all green.
- No placeholder/legal gaps.
- Faithfulness to design holds live; hygiene done.

Only then is the site launched. Note completion back in the project tracking (docs/PROGRESS.md).
