# Phase 8 — Project Website: Design Direction

This is what to tell Claude Design about the *visual direction* of the site, so it isn't guessing. It is added on top of the design-brief and handoff contract — it does not replace them. Without this, Design invents a look and you get drift; this is the input that prevents it.

## Non-negotiable technical constraints (state these to Design first)

These bind both Design and the build. Put them at the top of the brief:

### Vanilla by default — no libraries or frameworks
The site is plain HTML, CSS and JS. No CSS/JS frameworks, no UI libraries, no build-step dependencies, no runtime third-party scripts. Design must not design assuming a framework, and the build (Phase 4) must not introduce one. The **only** permitted exception is a specific site type where a static-site generator adds real value (e.g. a docs micro-site) — and even then it must be explicitly proposed, justified, and approved by the user for that project, and recorded. The assistant must NOT decide a site "qualifies" for the exception on its own or for convenience; absent explicit user approval, vanilla is mandatory. This is the same anti-drift rule as the rest of Keel: the safe, self-contained option is the default; deviating is a conscious user decision, never the assistant's.

### Fonts are always self-hosted — never Google Fonts or any CDN
If Design chooses a specific typeface, it must NOT use a Google Fonts `@import`/`<link>` or any externally hosted font. The font must live in the site and be loaded via local `@font-face`. Design declares the chosen font(s) as an external asset in the handoff (the same way it declares images it cannot produce — see the `SPEC/external-assets.md` mechanism), with: exact family name, the specific weights/styles actually used, the formats needed (woff2 first), and where to obtain the font legally with its license. The build then guides the user one step at a time (see "Font procurement" below). A font referenced without this declaration is a handoff gap → Design Request, never improvised.

### Images Design can't produce
Same mechanism as Phase 4 — declared in `SPEC/external-assets.md` with a ready base prompt, then generated one asset at a time with the user's chosen generator, saved at the exact path/name/format. Not duplicated here; it applies as-is.

### Product screenshots (Design reserves the space; the user captures; the build fits them)
A plugin/app site usually needs real screenshots of the product. Design cannot take them, so it must NOT leave a guess or an unlabeled gap:

- **Design reserves the slot** in the layout (the exact place a screenshot goes) and declares it in `SPEC/screenshots.md`: what the screenshot is, exactly which product screen/state it must show (cross-referencing `<site-docs>/design/PRODUCT-BRIEF.md`), the approximate size it should be, and the slot's reserved CSS container so the build knows what it's fitting into.
- **The build guides the user one screenshot at a time** (same loop as fonts/images — catch the mistake where it happens, not after the whole site is built): which product screen to open and capture, where to save it, with what filename and file type. Confirm (the user shows it) before the next.
- **The build places each screenshot in its slot and adjusts the slot's CSS** so it sits well — because a real capture never matches the reserved size exactly. Adjusting the container CSS to fit the real image is expected and allowed; deforming the screenshot or changing the design is not.

Two-branch failure handling, same as the rest of Keel:
- Design under-specified the screenshot (which screen/state/size unclear) → stop, do not guess, Design Request for that specific screenshot's spec.
- The screenshot is specified fine but can't be produced as described (feature not available in the user's environment, etc.) → don't fake it; resolve with the user (different state, or a Design Request to change what's shown) — never the assistant inventing the screenshot.

## Decide and put in the brief

### 1. Identity relationship
The default is inheritance: the site uses the brand's design system recorded in the PROGRESS.md project card (Phase 1 step 9) — the product's canonical tokens, logo, typography and component styles. Point Design at the exact source (e.g. the product's `SPEC/design-tokens.md` + `artifacts/styles/` + logo assets). A site-specific identity is the exception: it is the user's explicit, recorded decision, never drift — and even then the user decides the palette/type now; Design must ask, not invent (same ask-don't-invent rule as Phase 3). If no design system exists yet (the product had no UI), the site's design founds it: say so in the brief, per Phase 1 step 9.

### 2. Tone / personality
One or two lines: e.g. "technical and sober, developer audience, no marketing fluff" vs "bold and conversion-focused" vs "minimal and editorial". This single decision drives layout density, imagery, and copy voice. Vague tone → inconsistent design.

### 3. Reference points
If the user has sites they like/dislike, capture them as direction (not to copy — as a vocabulary for what "good" means here). If none, state that and let Design propose, but Design still must specify exactly what it chose in the SPEC.

### 4. Density & layout intent
Content-dense vs spacious; long-scroll landing vs compartmentalised pages; how prominent the primary CTA must be and where it repeats. This ties directly to the section catalogue decisions.

### 5. Imagery strategy
Real screenshots? Illustrations? Photography? Anything Design cannot generate (photos, complex illustration) must be declared in `SPEC/external-assets.md` with a ready base prompt — the Phase 4 guided one-asset-at-a-time generation loop handles producing them with the user's chosen generator. Decide the strategy here so the brief is explicit.

### 6. Responsiveness & accessibility intent
Required breakpoints, mobile-first or not, and the **accessibility spec** Design must deliver per `references/accessibility.md` and the handoff contract's `SPEC/accessibility.md`: contrast-verified color pairs (with ratios), visible focus and focus order, accessible name/role/state per component and state, heading/landmark structure, target sizes, reduced-motion variants, reflow at large text, and error identification. WCAG 2.2 AA is the floor (AAA where feasible; EN 301 549 / EAA in EU scope). These are also SEO/quality gates (`references/phase-8-technical-seo.md`), but accessibility is required in its own right — not deferred to the build.

### 7. Constraints carried from discovery
Host constraints (e.g. static-only, no heavy frameworks), language/RTL needs if the site is multilingual, brand non-negotiables.

## Hand-off rule

All of the above goes INTO the design brief and is governed by the handoff contract: Design must deliver real artifacts + a SPEC, build templates once and manifest reuse, specify every section's states, declare images it can't make AND fonts it wants used, and ask the user when something is undefined. Gaps come back as a Design Request — never improvised by the build.

## Font procurement (guided one step at a time, like images — runs in keel Phase 4)

When the handoff declares a self-hosted font, the build does NOT just write down where to get it and move on. It guides the user one step at a time, the same loop as guided image generation and external setup (catch the mistake where it happens, not after the whole site is built):

1. State the exact font and the specific weights/styles actually used (from the SPEC declaration) — nothing more, to keep the file footprint minimal.
2. Tell the user exactly where to obtain it legally (the source named by Design and its license) and how to download it.
3. Tell the user which files from the download to use (which weights, woff2 preferred) and exactly where to place them in the site (the fonts directory the build expects).
4. Provide the exact local `@font-face` CSS to add (no Google Fonts/CDN), matching the placed files.
5. Ask the user to confirm (screenshot/inspection where verifiable) before continuing.

Two-branch failure handling, same as the rest of Keel:
- The SPEC didn't specify the font well enough to guide procurement (family/weights/source/license missing) → stop, do not guess a substitute font, raise a Design Request for that specific gap.
- The SPEC is fine but the user can't obtain that exact font (licensing, unavailable) → do not silently swap it; resolve with the user (a documented equivalent, or a Design Request to change the typeface) — never the assistant inventing a replacement.

## Definition of done (this reference)

- Vanilla constraint and self-hosted-fonts constraint stated at the top of the brief; any vanilla exception explicitly approved by the user and recorded.
- Identity relationship, tone, density/layout intent and imagery strategy decided and written into the brief.
- Any chosen font declared as an external asset (family, weights, formats, legal source + license) for the guided procurement loop.
- Every product screenshot declared in `SPEC/screenshots.md` with reserved slot, target screen/state, approx size and slot CSS — for the guided capture loop and CSS-fit in the build.
- Reference points captured or explicitly absent.
- Responsiveness stated, and the accessibility spec Design must deliver (`SPEC/accessibility.md`, WCAG 2.2 AA floor) stated per `references/accessibility.md`.
- The brief, with this direction, satisfies the handoff contract before Design starts.
