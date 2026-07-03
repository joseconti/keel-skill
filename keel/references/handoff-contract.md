# Handoff Contract (shared by `design-spec-handoff` and `code-faithful-build`)

This is the single agreed structure that flows from Design to Cowork/Code. Both skills MUST reference this exact structure. If you change it here, change the expectations in both skills.

The Design phase **produces** this. The Build phase **audits and consumes** this. The contract is what makes "code adapts to the design, never the reverse" enforceable.

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
│   ├── assets/                # svg/, img/, fonts/ (real exported files)
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

## Rules baked into the contract

1. **One template, many pages.** If pages share structure, Design builds the template once under `artifacts/templates/` and records every consumer page in `SPEC/manifest.md` with its data/variant. `artifacts/pages/` is only for genuinely unique screens. Regenerating structurally-identical pages is a contract violation.

2. **Every unique screen has a SPEC file** in `SPEC/screens/` documenting all applicable states: default, hover, focus, active, disabled, loading, empty, error, success — plus responsive behavior at each required breakpoint, and any role/plan/conditional variants.

3. **Tokens are exact and centralized.** `SPEC/design-tokens.md` holds canonical values; `artifacts/styles/` holds the same values as code (CSS variables or equivalent). They must agree.

4. **Assets are real and indexed.** Exported SVG/PNG/etc. live in `artifacts/assets/`. `SPEC/assets-index.md` maps each file to where it is used, its intrinsic dimensions, and format. No "an icon goes here" without the actual icon.

5. **Open questions block the build.** `SPEC/open-questions.md` is where Design records anything it could not specify. The Build phase MUST NOT start while this file has unresolved items — instead the Build phase generates a Design Request prompt (see `code-faithful-build`) to send back to Design.

6. **Placeholder content is labeled.** Any non-final copy must be marked as placeholder in the SPEC so it is never shipped as-is.

7. **External setup is fully extracted, never implicit.** If any part of the project requires a human to configure external software (Unity, a hosting panel, an OAuth provider console, a SaaS settings page, DNS, etc.), every exact configuration value MUST be written into `SPEC/external-setup.md` — field names, exact values, toggles, order. It is a contract violation to leave a needed config value implicit inside an artifact file and not surface it in the SPEC. Downstream this is consumed by an interactive, step-by-step human walkthrough: a value that is not in the SPEC cannot be guided safely and becomes a Design Request. Where a value is the user's to decide, Design must ask the user, not invent it.

8. **Assets Design cannot produce are declared, not faked.** If a needed asset is something Design cannot generate itself (a photographic image, a complex illustration, a rendered 3D scene), Design MUST list it in `SPEC/external-assets.md` and, for each, (a) explain what the asset is and why it's needed, (b) give all placement detail (role, exact usage location, intended final filename, format, intrinsic dimensions/aspect ratio), and (c) **write a ready, generator-neutral base prompt** describing subject, composition, mood, what to include and exclude, and the exact palette/style pulled from `design-tokens.md`. The base prompt is Design's authorship: downstream the builder only *adapts* it to the user's chosen generator — it does not invent visual content. It is a contract violation to leave such an asset as a silent gap, an unlabeled placeholder, or a bare description with no base prompt. If Design cannot write a faithful base prompt because something is undefined, that is a question for the user (recorded in `open-questions.md`), never a Build-side invention.

9. **Accessibility is specified, not left to the build.** `SPEC/accessibility.md` plus per-screen accessibility notes capture the a11y contract: contrast-verified color pairs (with measured ratios), the visible focus indicator and focus order, accessible name/role/state per component and per state, heading/landmark structure, target sizes, reduced-motion variants, behavior under text scaling and high-contrast/forced-colors, and error identification (never color-only). A screen delivered without its accessibility spec is an incomplete handoff — the build must not invent it; the gap becomes a Design Request. Per `references/accessibility.md`.

## What "complete" means

The handoff is complete when:

- Every page in `SPEC/manifest.md` resolves to either a unique page artifact or a template + concrete data.
- Every unique screen SPEC file covers all states and breakpoints with exact tokens.
- Every asset referenced in any SPEC exists in `artifacts/assets/` and appears in `assets-index.md`, OR is declared in `SPEC/external-assets.md` with full generation detail.
- Every external-software configuration the user must perform by hand has every value captured in `SPEC/external-setup.md` (no implicit values left inside artifact files).
- `SPEC/accessibility.md` and every unique screen's accessibility are complete per `references/accessibility.md` (contrast pairs, focus order, name/role/state, heading/landmark structure, target sizes, reduced-motion, error identification) — nothing left for the build to invent.
- `open-questions.md` has zero unresolved items.

Anything short of this is an incomplete handoff and the Build phase must treat the gaps as a Design Request, not as license to improvise.
