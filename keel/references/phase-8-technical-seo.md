# Phase 8 — Project Website: Technical SEO & AEO

A verifiable checklist, not generic advice. Each item is something you can confirm is present and correct, per page or per site. Covers classic SEO, AEO (optimization for AI answer engines), and the supporting site files that consolidate both (`robots.txt`, `sitemap.xml`, `humans.txt`, `manifest.json`, `.well-known/security.txt`, `llms.txt`, favicons and the JSON-LD set). Honest scope: this is sound technical SEO and AEO — it does NOT promise rankings and includes no manipulative tactics. Plan these in Phase 2, build them in Phase 4, verify them at launch (`references/phase-8-launch-checklist.md`).

## Per-page essentials

- **Title**: unique, accurate, ≤ ~60 chars, primary intent first. One per page; no duplicates across pages.
- **Meta description**: unique per page, accurate, ~150–160 chars. Not keyword-stuffed.
- **One `<h1>` per page**, matching the page's purpose; logical `h2/h3` hierarchy (no skipped levels for styling).
- **Canonical URL** set per page; no accidental duplicate-content URLs (trailing slash, query params, www vs non-www consolidated).
- **Open Graph + Twitter card** present and *complete* — not just an image. A partial block (image but missing `og:title`/`og:description`/`og:url`) renders no card at all. Full required set in the dedicated section below.
- **Language**: correct `lang` attribute; if the site is multilingual, `hreflang` between locale versions (ties to the discovery i18n decision).

### Base `<head>` meta tags (every page)

These are non-negotiable and easy to miss in vanilla builds:

- `<meta charset="utf-8">` first.
- `<meta name="viewport" content="width=device-width, initial-scale=1">` for mobile.
- `<meta name="theme-color" content="...">` matching the brand (also referenced from `manifest.json`).
- `<meta name="color-scheme" content="light dark">` if dark mode is supported.
- `<meta name="referrer" content="strict-origin-when-cross-origin">` (or stricter — coordinate with the security profile).
- `<meta name="format-detection" content="telephone=no">` unless phone numbers really should be linkified.
- `<meta name="robots" content="index, follow">` on indexable pages; `noindex, nofollow` only where intended (utility/thank-you pages). **Check that no stray `noindex` survived from a staging build** — a single leftover `noindex` silently de-indexes the whole site.
- Author/`<meta name="author">` per the E-E-A-T item.

### Open Graph & Twitter Card (social share) — every page

A partial social-card block is the single most common share bug. The classic failure: shipping `og:image` (and `twitter:image`) but omitting `og:title`/`og:description`/`og:url` — X, Facebook, LinkedIn, WhatsApp and Slack then render **no card at all, not even the image**. The image alone is never enough. Treat the OG set below as mandatory and complete, not a pick-list; set them **per page**, not one home-page block copied everywhere.

**Required Open Graph — all of these, or the card does not render:**

- `og:title` — share title (may differ from `<title>`; ~40–60 chars).
- `og:description` — one-line share summary (~110–160 chars).
- `og:url` — the page's **absolute** canonical URL, identical to `<link rel="canonical">`.
- `og:type` — `website` for home/landing, `article` for blog/changelog posts.
- `og:image` — see the image rules below.

**Recommended Open Graph:**

- `og:site_name` — the project/site name.
- `og:locale` — e.g. `es_ES`; add an `og:locale:alternate` per extra locale on multilingual sites (consistent with `hreflang`).

**The `og:image` — where most "image doesn't show" bugs live:**

- **Absolute HTTPS URL** (e.g. `https://example.com/og/home.png`) — never a relative path and never `localhost`/a dev host. Relative or dev URLs are the second most common reason the image stays blank.
- **1200×630 px** (1.91:1) — the safe size for X `summary_large_image`, Facebook and LinkedIn.
- `og:image:width` (`1200`) and `og:image:height` (`630`) declared, so scrapers can lay out the card before fetching the file.
- `og:image:type` (`image/png` or `image/jpeg`) matching the real file.
- `og:image:alt` — describes the image.
- The file must return `200` at that URL, be PNG or JPEG (avoid SVG/WebP for maximum compatibility), and stay **under ~5 MB** (X drops larger images).

**Twitter / X card — it needs its own card type:**

- `twitter:card` — `summary_large_image` for a large image (or `summary` for a thumbnail). **Without `twitter:card`, X shows no card even when every `og:` tag is present.**
- `twitter:title`, `twitter:description`, `twitter:image` — set them explicitly; don't rely on X falling back to the OG tags.
- `twitter:image:alt` — accessibility.
- `twitter:site` / `twitter:creator` (`@handle`) — only if the project/author has an X account.

**Verify on the live URL, never trust source HTML** (enforced at launch): Facebook Sharing Debugger, X (Twitter) Card Validator, LinkedIn Post Inspector, or opengraph.xyz. They also force a re-scrape, refreshing any cached blank card.

## Site-wide files (the "well-known set")

Every site ships these unless explicitly justified otherwise. They are part of the build's output and verified at launch.

### `robots.txt` (mandatory)

- Located at the site root, reachable at `/robots.txt`, served as `text/plain`.
- Does **not** accidentally block the site (no stray `Disallow: /`).
- References the sitemap at the bottom: `Sitemap: https://example.com/sitemap.xml` (absolute URL).
- Explicitly addresses AI/answer-engine crawlers — the policy is a user decision recorded in discovery, not the assistant's. Default if the user wants AI citation (recommended for project sites): **allow them**. Default if the user wants to opt out of AI training: **disallow them**. Either way, state it explicitly per crawler rather than relying on default behavior. Relevant user-agents at the time of writing include (the list is volatile — verify at launch):
  - Answer engines that cite (usually allow): `ClaudeBot` (Anthropic answers), `PerplexityBot`, `OAI-SearchBot` (ChatGPT search), `Google-Extended` (Google AI), `Applebot-Extended`.
  - Training crawlers (often the user wants to choose): `GPTBot` (OpenAI training), `anthropic-ai` (Anthropic legacy), `CCBot` (Common Crawl), `Bytespider`, `meta-externalagent`.
- For each user-agent, an explicit `User-agent:` block with `Allow:` or `Disallow:` — don't rely on the absence of a rule.

### `sitemap.xml` (mandatory)

- Located at the site root or referenced from `robots.txt`; absolute URLs only; uses `https://`.
- One `<url>` per canonical page (only canonical URLs — never duplicates).
- `<lastmod>` set from the actual last-modified date of the page content (used by AI crawlers and search engines to prioritize). Keep it accurate; do not fake it.
- `<changefreq>` and `<priority>` are optional and often ignored — include if meaningful; do not invent.
- **Multilingual sites**: each locale URL listed, with `xhtml:link rel="alternate" hreflang="..."` entries inside its `<url>` block, including `x-default`. The `hreflang` values match the `<html lang>` on each page.
- **Sitemap index** (`sitemap_index.xml`) when the site is large enough to warrant splitting (e.g. per-locale sitemaps for a multilingual site).
- **Image sitemap** entries (`image:image`) only if the site is image-heavy and images are a primary content type (e.g. a screenshots gallery); otherwise omit.

### `humans.txt` (recommended)

- Located at `/humans.txt`, served as `text/plain`.
- Credits the team behind the site, in the spirit of `humanstxt.org`. At minimum: author/team, role, location/country, contact (optional), site last update, technology used.
- Referenced from the HTML: `<link rel="author" type="text/plain" href="/humans.txt">`.

### `manifest.json` (web app manifest — recommended)

- Located at the site root, referenced from `<head>`: `<link rel="manifest" href="/manifest.json">`.
- Minimum useful set: `name`, `short_name`, `description`, `start_url` (`/`), `display` (`browser` or `standalone`), `theme_color`, `background_color`, `icons` (multiple sizes including a maskable variant — see favicons).
- Even for a non-PWA marketing site, the manifest improves install-to-home-screen behavior and gives mobile browsers proper colors.
- All fonts/images referenced by the manifest are self-hosted (same vanilla rule).

### `.well-known/security.txt` (mandatory if any contact/security surface exists)

- Located at `/.well-known/security.txt` (RFC 9116), served as `text/plain` with the right MIME type.
- Provides the security reporting contact. Required field: `Contact:` (mailto, https URL, or both). Recommended fields: `Expires:` (ISO 8601, future-dated; rotate before expiry — annual is sane), `Preferred-Languages:`, `Canonical:` (the URL of this file), `Policy:` (link to a security policy page), `Acknowledgments:` if relevant.
- Coordinated with the loaded security profile — this is where the security profile's "how to report" surfaces to the outside world.

### `llms.txt` (recommended for AEO)

- Located at the site root: `/llms.txt`, served as `text/plain` (`llms.txt` proposal, fast-evolving — verify the current spec at launch).
- A concise, plain-text summary of the site for LLMs: project name, one-line description, links to the canonical pages an LLM should read first (docs, getting-started, FAQ, license/changelog), and the author. Markdown is allowed.
- Optionally a longer `/llms-full.txt` with the full content concatenated for ingestion.
- This is an AEO aid, **not** a permission file. Crawler policy still goes in `robots.txt`.

### `ai.txt` (optional; only if the user wants a content-licensing statement for AI)

- A separate, emerging proposal (Spawning) for explicit content-licensing terms for AI. Include only if the user wants this stance recorded; otherwise omit. Crawler allow/disallow lives in `robots.txt`.

### Favicons & touch icons (mandatory)

A minimal, complete set served from the root or `/favicons/`:

- `favicon.ico` (multi-size, 16/32/48) at the root for legacy.
- `favicon.svg` (single scalable) — modern browsers prefer it.
- `apple-touch-icon.png` 180×180 at the root (iOS).
- PNG icons referenced by `manifest.json` (typically 192×192 and 512×512), plus one **maskable** icon (`"purpose": "maskable"`) for Android adaptive icons.
- All declared in `<head>` with the right `rel` and `type`, and matching `theme-color` between meta tag and manifest.
- No external CDN for any favicon — same self-hosted rule as fonts.

### Search-engine verification (when used)

- Google Search Console: prefer DNS TXT verification; the HTML file fallback (`google<hash>.html`) goes at the site root.
- Bing Webmaster Tools: DNS TXT, the `BingSiteAuth.xml` file at the root, or the `<meta name="msvalidate.01">` tag.
- IndexNow key file at the site root if used (e.g. `<key>.txt`).
- Other verification files (Yandex, Pinterest, etc.) only if the user actually uses those platforms.

### `opensearch.xml` (optional)

- Only for sites with their own search; declares a browser-installable search engine. Skip otherwise.

### Compression and cache headers (server config, not files — verify at launch)

- gzip and/or brotli enabled for HTML/CSS/JS/SVG/JSON.
- Long cache (`Cache-Control: public, max-age=31536000, immutable`) for fingerprinted static assets; short or `no-cache` for HTML.
- HTTP/2 or HTTP/3 on the host; HSTS already covered above.

### Resource hints (in `<head>`, when justified)

- `<link rel="preconnect">` only for origins the page actually contacts (typically none in vanilla; if there's an analytics endpoint, preconnect to it).
- `<link rel="preload">` for above-the-fold critical fonts (woff2) only — preloading everything hurts more than it helps.

## Structured data (JSON-LD)

Validate every JSON-LD block against a structured-data validator on the live URLs. Keep JSON-LD consistent with the visible content (no fabricated facts).

Pick the types that match what's on each page; do not stack types that don't apply:

- **`WebSite`** on the home page, with `name`, `url`, and (if there's a site search) a `SearchAction` `potentialAction` so search engines may surface a sitelinks search box.
- **`Organization`** or **`Person`** for the author/maintainer — once per site, referenced via `@id` from other types.
- **`SoftwareApplication`** for a plugin/app/MCP server/tool: `name`, `applicationCategory`, `operatingSystem`, `offers` (if priced; or a free statement), `softwareVersion`, `releaseNotes` (changelog URL), `author` (`@id` of the Organization/Person).
- **`WebPage`** for content pages where more specific types don't fit; ties into the breadcrumb.
- **`BreadcrumbList`** on every page deeper than the home (matches the visible breadcrumb).
- **`FAQPage`** for the FAQ section/page only; question + answer pairs must match the rendered text.
- **`HowTo`** for setup/usage step pages; `step` items match the rendered steps.
- **`Article`** / **`BlogPosting`** for blog/changelog entries (if the site has them).
- **`Product`** with `Offer` for commercial products (paid plugin/app). Use `AggregateRating`/`Review` only if real, verified reviews exist on-site; never fabricate.
- **`VideoObject`** for embedded product videos.

A few rules that catch most mistakes:

- One canonical `Organization`/`Person` `@id`, referenced from everywhere else — don't redefine the author per page.
- JSON-LD is inline in the HTML (not loaded via JS) so AI crawlers reading server HTML see it.
- Every URL inside JSON-LD is absolute and matches the canonical.

## Site-wide URL/transport rules

- **Clean, stable URL structure**: human-readable, lowercase, hyphenated, no session/junk params; URLs won't change after launch (or have redirects if they must).
- **HTTPS everywhere**, valid TLS, HTTP→HTTPS redirect, HSTS (also a security-profile item).
- **404 and any redirects** behave correctly; no broken internal links.
- One canonical host (www or non-www) — the other 301-redirects to it; sitemap and canonicals use only the canonical host.

## Performance as SEO (Core Web Vitals reality)

- Images optimized: correct format and dimensions, lazy-loaded below the fold, explicit width/height to avoid layout shift. Generated images from the Phase 4 loop must meet the SPEC's intrinsic dimensions.
- No render-blocking bloat; critical CSS sane; defer non-critical JS.
- Acceptable LCP/CLS/INP on mobile, not just desktop.
- Self-hosted fonts (Phase 8 design direction) loaded with `font-display: swap` and only the actual weights/styles used — no unused font files shipped.
- Accessible markup doubles as SEO: meaningful `alt` text, sufficient contrast, keyboard navigability, semantic landmarks — but accessibility is required in its own right, not merely as an SEO side effect. The site meets the Web/HTML section of `references/accessibility.md` (WCAG 2.2 AA floor, AAA where feasible; EN 301 549 / EAA in EU scope), verified with real assistive technology, per the Phase 1 commitment.

## Honesty rule

Do not claim or imply ranking guarantees. Do not add cloaking, hidden text, doorway pages, or link schemes. If the user asks for ranking tricks, explain plainly that technical SEO makes a site indexable and fast — content and authority drive rankings, and manipulative tactics risk penalties.

## AEO — Answer Engine Optimization (for AI answer engines)

The build must also get the site AEO-ready, not only classic SEO. AEO is about being the source AI answer engines (ChatGPT, Claude, Perplexity, Google AI Overviews, Gemini) extract, understand and cite. AEO and SEO are complementary and share a foundation — a site that isn't crawlable/fast won't do well at either — so do these on top of the SEO checklist, not instead of it:

- **Answer-first content.** Under each question-style heading, lead with a concise, direct ~40–60 word answer before any elaboration. Answer engines favour content they can extract verbatim.
- **Question-shaped structure.** Headings phrased as the questions users actually ask (e.g. "What does <plugin> do?", "How do I install <plugin>?"); logical, shallow hierarchy; one idea per section so a passage is independently quotable.
- **Structured data for meaning.** JSON-LD that helps engines interpret the content (see the structured-data section above). Valid and consistent with the visible content.
- **`llms.txt` present.** Provides a curated map of the site for LLMs — title, summary, the handful of pages an LLM should read first.
- **Crawler policy explicit.** `robots.txt` decides per-bot whether AI crawlers are allowed (see the `robots.txt` section above). The decision is recorded; default behavior is not assumed.
- **Extractable facts.** State concrete, specific, accurate facts (versions, requirements, prices, units) plainly — vague marketing prose doesn't get cited; specific data does.
- **E-E-A-T signals.** Clear authorship, the author/maintainer's credentials, the project's track record, accurate and dated content, consistent facts about the product across the site (and matching the listing/repo).
- **Freshness & accuracy.** Keep version-specific and changelog content current (ties to Keel's oldest→newest changelog rule); stale facts get dropped by answer engines. Sitemap `<lastmod>` reflects real changes.
- **Content present in the HTML.** Server-rendered or static HTML so the answer is extractable without JS — aligns with the vanilla, no-heavy-JS default.
- **Honesty rule applies here too.** No fabricated stats, fake Q&A, or claims the product doesn't deliver to court AI citation — answer engines and users both punish that, and it misrepresents the product.

## Definition of done (this reference)

- Every page has unique title, meta description, single h1, canonical, a **complete OG/Twitter card** (`og:title`/`description`/`url`/`type`/`image` + `twitter:card` — not just an image), base meta tags (charset/viewport/theme-color/referrer/robots), correct `lang`, and `hreflang` if multilingual.
- Site-wide files present and correct: `robots.txt` (with sitemap reference and explicit AI-crawler policy), `sitemap.xml` (with `lastmod`, hreflang alternates if multilingual), `humans.txt`, `manifest.json` (with theme/background color and icons including a maskable variant), `.well-known/security.txt` (with `Contact` and future-dated `Expires`), `llms.txt` (AEO), favicon set (`.ico`, `.svg`, `apple-touch-icon`, manifest icons).
- HTTPS / canonical-host / redirects / 404 all behave correctly; URL structure clean and stable.
- JSON-LD shipped per page type (WebSite + Organization/Person at minimum; SoftwareApplication/FAQPage/HowTo/Article/Product/BreadcrumbList as applicable), inline in HTML, validated on live URLs, consistent with rendered content.
- Accessibility meets the Web/HTML section of `references/accessibility.md` (WCAG 2.2 AA floor: semantic structure, keyboard operability, visible focus, contrast, reduced-motion, reflow), verified with automated tools **and** a real assistive-tech pass — not only a performance-adjacent check. Performance checks pass on mobile, with self-hosted fonts using `font-display: swap`.
- Search-engine verification done if the user uses Search Console / Bing Webmaster / IndexNow.
- AEO: answer-first passages under question headings, `llms.txt` published, AI-crawler policy explicit, extractable factual content, E-E-A-T and freshness, content present in HTML.
- No manipulative tactics introduced (SEO or AEO).

Verified for real at launch — see `references/phase-8-launch-checklist.md`.
