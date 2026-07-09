# Handoff Contract (shared by Phase 3 — Design Handoff and Phase 4 — Faithful Build)

This is the single agreed structure that flows from Design to Cowork/Code. Phases 3 and 4 MUST reference this exact structure. If you change it here, change the expectations in both phase references.

The Design phase **produces** this (Phase 3 brief mandates it). Phase 4 **audits and consumes** this. The contract is what makes "code adapts to the design, never the reverse" enforceable.

## Why this shape

Design already emits real working files (HTML/CSS/JS, components, SVG, images, markdown). The problem was never that Design produces too little — it's that (a) it regenerates near-identical pages, and (b) the behavior/state/token decisions live only in Design's head. So the contract keeps the real artifacts **and** adds a SPEC layer that captures everything the raw files cannot self-describe.

## Folder structure

```
design-handoff/
├── README.md                  # 1-paragraph orientation + how to read this handoff
├── artifacts/                 # the REAL built files Design produces
│   ├── templates/             # each reusable template/layout built ONCE
│   │   ├── template-listing/  # e.g. an index/listing layout
│   │   ├── template-detail/
│   │   └── ...
│   ├── components/            # reusable components (buttons, cards, nav, modals…)
│   ├── pages/                 # ONLY pages that are genuinely unique (not template clones)
│   ├── assets/                # svg/ + png/, img/, fonts/ (real exported files; logos & icons in BOTH svg and png, build-ready formats)
│   └── styles/                # global css / tokens as code (variables file)
└── SPEC/
    ├── manifest.md            # the reuse map: every page → which template + what data/variant
    ├── design-tokens.md       # exact values: color, type, space, radius, shadow, motion, z
    ├── screens/
    │   ├── <screen-a>.md       # one file per UNIQUE screen, ALL states documented
    │   └── <screen-b>.md
    ├── interactions.md        # behavior, conditional logic, role/plan gating, transitions
    ├── assets-index.md        # every asset: filename → where used, intrinsic size, format
    ├── external-assets.md     # assets Design CANNOT produce itself (photos, complex art) — to be generated externally
    ├── external-setup.md      # EVERY config value for external software the user must set by hand
    ├── accessibility.md       # the a11y contract: contrast pairs, focus order, name/role/state, headings, target sizes, reduced-motion, errors
    └── open-questions.md      # anything undefined; MUST be empty/resolved before build starts
```

**Website projects (Phase 8) add one file to `SPEC/`:** `screenshots.md` — every reserved product-screenshot slot (what it shows, which product screen/state, approximate size, the slot's reserved CSS container), per `references/phase-8-design-direction.md`. All the completeness rules below apply to it equally. Non-website projects do not include it.

## Rules baked into the contract

1. **One template, many pages.** If pages share structure, Design builds the template once under `artifacts/templates/` and records every consumer page in `SPEC/manifest.md` with its data/variant. `artifacts/pages/` is only for genuinely unique screens. Regenerating structurally-identical pages is a contract violation.

2. **Every unique screen has a SPEC file** in `SPEC/screens/` documenting all applicable states: default, hover, focus, active, disabled, loading, empty, error, success — plus responsive behavior at each required breakpoint, and any role/plan/conditional variants.

3. **Tokens are exact and centralized.** `SPEC/design-tokens.md` holds canonical values; `artifacts/styles/` holds the same values as code (CSS variables or equivalent). They must agree. The file states its **origin**: derived from an existing design system (cite the source — values must match it), or founded by this project as the brand's canonical system (future projects will inherit these values), or one-off. It also states the **target surfaces** the system covers (web, WordPress/WooCommerce admin, PrestaShop, iOS/iPadOS, watchOS, macOS, tvOS, Android, Windows, cross-platform framework, email, print) and, for each, the mapping from the one canonical token set onto that surface's native equivalents plus the surface's component specs — so the brand is identical across surfaces and no build has to reinterpret a single-surface artifact for another platform. Surfaces the system anticipates for reuse are defined even if this project ships only one.

4. **Assets are real, indexed, and delivered ready for the build to use directly — never something the build must transform.** Exported files live in `artifacts/assets/`. `SPEC/assets-index.md` maps each file to where it is used, its intrinsic dimensions, and format. No "an icon goes here" without the actual icon. On top of that, two hard delivery rules:

   - **Every logo and every icon ships in BOTH SVG and PNG.** The SVG is the scalable master — optimized, `viewBox` present, no editor cruft or stray metadata. The PNG is a raster version at the intrinsic display size, plus the standard densities/sizes the target platform needs (e.g. @1x/@2x/@3x for the web and native apps, or the exact favicon/app-icon sizes). A logo or icon delivered in only one of the two formats is an incomplete handoff.
   - **Every asset is delivered in the format the target build drops in as-is.** Design chooses, per asset and per target surface/stack, the format the build can use directly — so the build never has to convert, re-export, trace, recolor, rasterize, or resize an asset to use it (web: optimized SVG + PNG at the exact container size, or WebP where the brief calls for it, fonts self-hosted in the web-native formats and never a CDN link; iOS/macOS: PDF/SVG vectors or an asset catalog with @1x/2x/3x, SF Symbols where used; Android: vector drawables + density buckets; WordPress admin: whatever the admin page consumes directly). If one asset serves several consumers that need different formats, Design delivers all of them. `SPEC/assets-index.md` records, per asset, every delivered format and the exact place and size the build uses it. This is the asset-side of "code adapts to the design": the build must never be forced to transform an asset because Design shipped it in an inconvenient format — an asset that would force a build-side conversion is an incomplete handoff, i.e. a Design Request.

5. **Open questions block the build.** `SPEC/open-questions.md` is where Design records anything it could not specify. The Build phase MUST NOT start while this file has unresolved items — instead the Build phase generates a Design Request prompt (Phase 4 Step 3, `references/design-request-template.md`) to send back to Design.

6. **Placeholder content is labeled.** Any non-final copy must be marked as placeholder in the SPEC so it is never shipped as-is.

7. **External setup is fully extracted, never implicit.** If any part of the project requires a human to configure external software (Unity, a hosting panel, an OAuth provider console, a SaaS settings page, DNS, etc.), every exact configuration value MUST be written into `SPEC/external-setup.md` — field names, exact values, toggles, order. It is a contract violation to leave a needed config value implicit inside an artifact file and not surface it in the SPEC. Downstream this is consumed by an interactive, step-by-step human walkthrough: a value that is not in the SPEC cannot be guided safely and becomes a Design Request. Where a value is the user's to decide, Design must ask the user, not invent it.

8. **Assets Design cannot produce are declared, not faked.** If a needed asset is something Design cannot generate itself (a photographic image, a complex illustration, a rendered 3D scene), Design MUST list it in `SPEC/external-assets.md` and, for each, (a) explain what the asset is and why it's needed, (b) give all placement detail (role, exact usage location, intended final filename, format, intrinsic dimensions/aspect ratio), and (c) **write a ready, generator-neutral base prompt** describing subject, composition, mood, what to include and exclude, and the exact palette/style pulled from `design-tokens.md`. The base prompt is Design's authorship: downstream the builder only *adapts* it to the user's chosen generator — it does not invent visual content. It is a contract violation to leave such an asset as a silent gap, an unlabeled placeholder, or a bare description with no base prompt. If Design cannot write a faithful base prompt because something is undefined, that is a question for the user (recorded in `open-questions.md`), never a Build-side invention.

9. **Accessibility is specified, not left to the build.** `SPEC/accessibility.md` plus per-screen accessibility notes capture the a11y contract: contrast-verified color pairs (with measured ratios), the visible focus indicator and focus order, accessible name/role/state per component and per state, heading/landmark structure, target sizes, reduced-motion variants, behavior under text scaling and high-contrast/forced-colors, and error identification (never color-only). A screen delivered without its accessibility spec is an incomplete handoff — the build must not invent it; the gap becomes a Design Request. Per `references/accessibility.md`.

## What "complete" means

The handoff is complete when:

- Every page in `SPEC/manifest.md` resolves to either a unique page artifact or a template + concrete data.
- Every unique screen SPEC file covers all states and breakpoints with exact tokens.
- Every asset referenced in any SPEC exists in `artifacts/assets/` and appears in `assets-index.md`, OR is declared in `SPEC/external-assets.md` with full generation detail.
- Every logo and icon is present in **both SVG and PNG** (PNG at the intrinsic size + the platform's required densities/sizes), and every asset is in a format the target build uses directly — nothing that would force a build-side conversion. `assets-index.md` lists every delivered format per asset with its exact use and size.
- Every external-software configuration the user must perform by hand has every value captured in `SPEC/external-setup.md` (no implicit values left inside artifact files).
- `SPEC/accessibility.md` and every unique screen's accessibility are complete per `references/accessibility.md` (contrast pairs, focus order, name/role/state, heading/landmark structure, target sizes, reduced-motion, error identification) — nothing left for the build to invent.
- `open-questions.md` has zero unresolved items.

Anything short of this is an incomplete handoff and the Build phase must treat the gaps as a Design Request, not as license to improvise.
