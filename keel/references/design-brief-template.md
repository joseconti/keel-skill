# Design Brief Template

Fill every bracket from the Phase 1–2 artifacts (discovery, functional spec, technical plan) and the Phase 3 Step 1 confirmation. Output the filled version as a markdown file the user pastes into Design. Do not leave brackets unfilled — an unfilled bracket is exactly the "left in the air" problem this skill exists to prevent. If a value is genuinely the user's call and unknown, it goes to the user as a question now (Phase 3 Step 1), not into Design as a guess.

---

# Design Brief: [PROJECT NAME]

## 0. How you (Design) must work — read first

You are producing a **reusable design system + real built artifacts + a governing SPEC**, not a pile of pages.

**Hard rules:**

1. **Build once, reuse by manifest.** Pages that are structurally identical must be built ONE time as a template. Do NOT regenerate near-identical pages — it wastes tokens and creates drift. Record every page that reuses a template in `SPEC/manifest.md` with its specific data/variant.
2. **Specify everything. Leave nothing in the air.** Every screen, every state, every breakpoint, every conditional behavior gets exact values and is documented in the SPEC.
3. **When something is undefined, ASK — do not invent or interpret.** Collect open items in `SPEC/open-questions.md` and ask them directly before finalizing. A guessed token or invented behavior is a defect.
4. **Exact values only.** Hex colors, px/rem, real font names + weights, ms durations, easing curves, z-index. Never "some", "a bit", "blue-ish".
5. **Deliver the real files AND the SPEC** in the exact structure in Section 6.

## 1. Context

- **What this is:** [website / web app / plugin admin screen / dashboard / other]
- **Where the final code will live:** [e.g. WordPress admin settings page / React SPA / static site]
- **Host constraints Design must respect:** [e.g. WP admin color scheme, no external font CDNs, must work inside `.wrap`, RTL, existing class names that cannot change — list them, or "none"]
- **Audience / purpose:** [1–2 lines]

## 2. Brand & tokens (the canonical values)

- **Design system status:** [existing — the values below COME FROM it (source: <path/repo/URL/doc>); apply them as-is and raise any deviation you want as a question, never restyle silently / founding — no system exists; YOU are creating the brand's canonical design system with this project, so build tokens, logo treatment and component styles for reuse beyond this project / one-off — this look intentionally stands alone]
- **Target surfaces/platforms this system must cover:** [list every one — e.g. web/HTML, WordPress-Woo admin, PrestaShop back office, iOS/iPadOS, watchOS, macOS, tvOS, Android, Windows, cross-platform framework, email, print — marking which ship in THIS project vs which are anticipated for brand reuse]. For each surface deliver the native/idiomatic tokens and component specs (CSS variables + HTML components for web; Dynamic Type, SF Symbols and HIG-aligned components for iOS/macOS; Material for Android; Fluent for Windows; WP admin colour scheme + `.wrap` for WordPress; Bootstrap back office for PrestaShop) and document how the ONE canonical token set maps onto each surface, so the brand is identical across all of them. Define anticipated surfaces now even if this project ships only one. If a single surface, state it so the scope is explicit.
- **Color palette:** [exact hex list with semantic roles: bg, surface, text, primary, danger, etc. — or "UNDEFINED → ask user"]
- **Typography:** [font families, weights, sizes/scale, line-heights — or ask]
- **Spacing scale:** [e.g. 4/8/12/16/24/32 — or ask]
- **Radius / shadows / borders:** [exact — or ask]
- **Motion:** [durations + easing for transitions — or ask]
- **Logo:** [provided — files listed below / **you (Design) create it** as part of founding this system / pending from the user — a dependency, not yours to invent]
  - If you create it: deliver real files, not a description — a master **SVG** *and* exported **PNG** versions, variants (horizontal / stacked / icon-only), on-light and on-dark versions, a monochrome version, minimum sizes and clear-space rules. Deliver the PNGs at the sizes/densities the target needs (e.g. @1x/@2x/@3x, favicon/app-icon sizes). Everything indexed in `SPEC/assets-index.md` and usable to derive favicons/app icons later. Iterate with the user before finalizing — the logo is their call.
- **Brand assets provided:** [list — or "none"]
- **Founding seed (only when founding):** [the Phase 1 founding-interview answers, carried verbatim: colors loved/vetoed, typeface preference + licensing, personality adjectives, references liked/disliked, dark-mode intent, iconography/imagery style, vetoes. This is your starting base — found the identity FROM it; anything unanswered goes to `SPEC/open-questions.md`, never guessed.]

If any of the above is "ask user", you must request it before finalizing — do not choose for them.

If the design system is **existing**, the values above are canonical and closed: do not introduce new colors, typefaces, or component styles outside it without asking the user first. If **founding**, document everything you define in `SPEC/design-tokens.md` and `artifacts/styles/` knowing they become the brand's canonical system for future projects.

## 3. Screen inventory (split for reuse)

**Unique screens** (each built individually, each gets a SPEC file):
- [screen name] — [purpose]
- ...

**Template-reused screens** (build the template ONCE, list consumers in the manifest):
- Template `[template-name]` is used by: [page A with data X], [page B with data Y], ...
- ...

If you discover more reuse opportunities while designing, collapse them into templates and update the manifest — do not produce duplicates.

## 4. States & behavior to specify per screen

For every unique screen, first state **what the screen does** — its purpose and the concrete functionalities/actions available on it (from the functional spec) — so you build the right screen, not just a layout. Then design AND document every applicable state:

- default, hover, focus, active, disabled
- loading, empty, error, success
- responsive behavior at breakpoints: [list exact breakpoints]
- conditional / role-based / plan-based variants: [describe, e.g. "free vs premium", "admin vs editor" — or "none"]

Document each in `SPEC/screens/<screen>.md`. Document cross-screen behavior and logic in `SPEC/interactions.md`.

## 5. Content & assets

- **Copy:** [final copy provided / use placeholder]. If placeholder, mark it clearly as placeholder in the SPEC so it is never shipped.
- **Icons/illustrations:** export real files into `artifacts/assets/`. **Every logo and every icon ships in BOTH SVG and PNG** — the SVG optimized with a `viewBox` and no editor cruft, the PNG at the intrinsic size plus the densities/sizes the target needs (@1x/@2x/@3x, favicon/app-icon sizes). Index every asset in `SPEC/assets-index.md` (filename → where used → intrinsic size → every delivered format).
- **Build-ready formats (no transformation by the build).** Deliver every asset in the format the target stack drops in directly, so the build never has to convert, re-export, trace, recolor, rasterize, or resize it: web → optimized SVG + PNG at the exact container size (WebP only if the brief asks), fonts self-hosted in web-native formats (never a CDN link); iOS/macOS → PDF/SVG vectors or an asset catalog with @1x/2x/3x (SF Symbols where used); Android → vector drawables + density buckets; WordPress admin → whatever the admin page consumes directly. If one asset serves consumers that need different formats, deliver all of them. An asset that would force the build to transform it is an incomplete handoff, not a valid delivery.
- **i18n:** [locales needed, e.g. en + es — or none]. If strings need externalizing, note it in the SPEC.
- **Accessibility target:** WCAG 2.2 AA floor (AAA where feasible); EN 301 549 / EAA if in EU scope; the target platform's native a11y API. This is specified per screen in Section 5d — not a one-line target.

## 5b. External software configuration (critical for the manual walkthrough)

If any part of this project requires a human to configure **external software** that the builder cannot script (Unity, hosting panel, OAuth provider console, SaaS settings, DNS, payment gateway, etc.):

- Identify every such piece of external setup.
- For each, write **every exact configuration value** into `SPEC/external-setup.md`: the software + version if relevant, the exact screen/path inside it, each field name, each exact value/toggle, and the order steps must be done in.
- Do NOT leave any needed value implicit inside an artifact file. Downstream, a builder will walk a human through this **one step at a time**, reading values straight from `SPEC/external-setup.md`. A value that is not there cannot be guided and will block the build.
- Where a value is the user's decision (an account ID, a domain, a secret, a business choice), ASK the user and record the answer — do not invent it.

If there is no external setup, state "none" in `SPEC/external-setup.md` so the absence is explicit.

## 5c. Assets you (Design) cannot produce yourself

If a needed asset is something you cannot generate (a photographic image, a complex illustration, a rendered 3D scene, etc.), do NOT leave a gap or an unlabeled placeholder. Declare it in `SPEC/external-assets.md`, one entry per asset, with:

- A plain explanation of what the asset is and why it's needed.
- Placement detail: role, exactly where it is used (which screen/template/slot), the intended final filename, format, and intrinsic dimensions/aspect ratio.
- **A ready, generator-neutral base prompt you write yourself**: subject, composition, mood/style, what to include and exclude, and the exact palette/style pulled from `SPEC/design-tokens.md` so the generated image matches the design system.

The base prompt must be complete enough to hand off as-is. Downstream, a builder will tell the user you couldn't generate these, ask which image generator the user uses, and only *adapt* your base prompt to that generator (it will not invent visual content). It then tells the user the exact file format, final filename, and directory to save each result.

If you cannot write a faithful base prompt because a creative detail is undefined, that is a question for the user now (record it in `SPEC/open-questions.md`) — not something the builder may invent.

If there are no such assets, state "none" in `SPEC/external-assets.md` so the absence is explicit.

## 5d. Accessibility (non-negotiable — specify per screen, do not defer to the build)

Accessibility is designed and documented by you (Design), not left for the build to infer. For every screen and component, specify and record it in `SPEC/accessibility.md` (plus per-screen notes in `SPEC/screens/<screen>.md`):

- **Targeted level:** [WCAG 2.2 AA floor + AAA where feasible; EN 301 549 / EAA if in EU scope; the target platform's native accessibility API].
- **Contrast-verified color pairs:** every text and UI-object foreground/background pair with its measured ratio (≥4.5:1 text, ≥3:1 large text and UI objects; AAA where feasible). Passing values, not guesses.
- **Visible focus indicator:** exact style/tokens, and the **focus order** per screen.
- **Accessible name, role, state** for every component in every state (default, hover, focus, active, disabled, loading, empty, error, success).
- **Heading and landmark/region structure** per screen (navigable by headings/landmarks).
- **Target sizes** meeting at least the platform minimum (24×24 CSS px / 44×44 pt / 48×48 dp) with adequate spacing.
- **Reduced-motion variant** for every animation/transition; behavior under **text scaling / reflow** and **high-contrast / forced-colors**.
- **Error identification** pattern (shown and announced, never color-only) and how status changes are announced.
- **Text alternatives** intent for every image/icon/media; confirm **no meaning is carried by color alone**.
- **RTL / bidi** behavior if the project is multilingual.

Anything here you cannot decide is a question for the user in `SPEC/open-questions.md` — never an invented value, and never something for the build to fill in. See `references/accessibility.md`.

## 6. Required delivery structure (non-negotiable)

Deliver a `design-handoff/` folder exactly like this:

```
design-handoff/
├── README.md
├── artifacts/
│   ├── templates/      # each reusable template built ONCE
│   ├── components/
│   ├── pages/          # ONLY genuinely unique pages
│   ├── assets/         # real svg/png/img/fonts
│   └── styles/         # tokens as code (CSS variables) + global styles; per target surface, its native token mapping
└── SPEC/
    ├── manifest.md         # every page → template + data, or "unique"
    ├── design-tokens.md    # exact canonical values
    ├── screens/<screen>.md # one per unique screen, ALL states
    ├── interactions.md     # behavior, conditional logic, gating, transitions
    ├── assets-index.md     # every asset mapped
    ├── external-assets.md  # assets you cannot produce — full generation detail (or "none")
    ├── external-setup.md   # every exact config value for external software (or "none")
    ├── accessibility.md    # per-screen a11y spec: contrast pairs, focus, name/role/state, headings, target sizes, reduced-motion, errors
    └── open-questions.md   # anything undefined — ask the user, list it here
```

`SPEC/design-tokens.md` and `artifacts/styles/` must contain the same values. When the system covers more than one surface, `SPEC/design-tokens.md` records the one canonical token set plus its mapping to each target surface's native equivalents, and `artifacts/styles/` carries that mapping as code per surface — the brand values are identical across surfaces, only their expression differs.

## 7. Definition of done

Do not consider the handoff finished until:

- Every page in `manifest.md` resolves to a unique page OR a template + concrete data.
- Every unique screen SPEC documents all states + breakpoints with exact tokens.
- Every target surface named in Section 2 has its native tokens + component specs and the canonical-token-to-surface mapping; no anticipated surface left undefined.
- Every asset referenced anywhere exists in `artifacts/assets/` and is in `assets-index.md`, OR is declared in `external-assets.md` with full generation detail.
- Every logo and icon is present in **both SVG and PNG**, and every asset is in a format the build uses directly (no build-side conversion); `assets-index.md` lists every delivered format per asset.
- Every asset you cannot produce yourself is in `external-assets.md` (or it explicitly says "none"); none left as a silent gap or unlabeled placeholder.
- Every external-software configuration value is captured in `external-setup.md` (or it explicitly says "none"); nothing needed is left implicit in an artifact.
- `SPEC/accessibility.md` and per-screen accessibility are complete (contrast-verified pairs, focus style/order, name/role/state per state, heading/landmark structure, target sizes, reduced-motion, text-scaling/high-contrast behavior, error identification) per `references/accessibility.md` — none left for the build to invent.
- `open-questions.md` has zero unresolved items (you asked the user and recorded the answers).
- No structurally-identical pages were duplicated.

If you cannot meet a point because information is missing: stop, ask the user the specific question, and only then finalize. Inventing the answer is not acceptable.
