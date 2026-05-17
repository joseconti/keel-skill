# Design Brief Template

Fill every bracket from the Step 1 interview. Output the filled version as a markdown file the user pastes into Design. Do not leave brackets unfilled — an unfilled bracket is exactly the "left in the air" problem this skill exists to prevent. If a value is genuinely the user's call and unknown, it goes to the user as a question (Step 1), not into Design as a guess.

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

- **Color palette:** [exact hex list with semantic roles: bg, surface, text, primary, danger, etc. — or "UNDEFINED → ask user"]
- **Typography:** [font families, weights, sizes/scale, line-heights — or ask]
- **Spacing scale:** [e.g. 4/8/12/16/24/32 — or ask]
- **Radius / shadows / borders:** [exact — or ask]
- **Motion:** [durations + easing for transitions — or ask]
- **Logo & brand assets provided:** [yes: list / no]

If any of the above is "ask user", you must request it before finalizing — do not choose for them.

## 3. Screen inventory (split for reuse)

**Unique screens** (each built individually, each gets a SPEC file):
- [screen name] — [purpose]
- ...

**Template-reused screens** (build the template ONCE, list consumers in the manifest):
- Template `[template-name]` is used by: [page A with data X], [page B with data Y], ...
- ...

If you discover more reuse opportunities while designing, collapse them into templates and update the manifest — do not produce duplicates.

## 4. States & behavior to specify per screen

For every unique screen, design AND document every applicable state:

- default, hover, focus, active, disabled
- loading, empty, error, success
- responsive behavior at breakpoints: [list exact breakpoints]
- conditional / role-based / plan-based variants: [describe, e.g. "free vs premium", "admin vs editor" — or "none"]

Document each in `SPEC/screens/<screen>.md`. Document cross-screen behavior and logic in `SPEC/interactions.md`.

## 5. Content & assets

- **Copy:** [final copy provided / use placeholder]. If placeholder, mark it clearly as placeholder in the SPEC so it is never shipped.
- **Icons/illustrations:** export real SVG/PNG into `artifacts/assets/`. Index every asset in `SPEC/assets-index.md` (filename → where used → intrinsic size → format).
- **i18n:** [locales needed, e.g. en + es — or none]. If strings need externalizing, note it in the SPEC.
- **Accessibility target:** [e.g. WCAG AA, keyboard nav, focus visible — or state baseline].

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
│   └── styles/         # tokens as code (CSS variables) + global styles
└── SPEC/
    ├── manifest.md         # every page → template + data, or "unique"
    ├── design-tokens.md    # exact canonical values
    ├── screens/<screen>.md # one per unique screen, ALL states
    ├── interactions.md     # behavior, conditional logic, gating, transitions
    ├── assets-index.md     # every asset mapped
    ├── external-assets.md  # assets you cannot produce — full generation detail (or "none")
    ├── external-setup.md   # every exact config value for external software (or "none")
    └── open-questions.md   # anything undefined — ask the user, list it here
```

`SPEC/design-tokens.md` and `artifacts/styles/` must contain the same values.

## 7. Definition of done

Do not consider the handoff finished until:

- Every page in `manifest.md` resolves to a unique page OR a template + concrete data.
- Every unique screen SPEC documents all states + breakpoints with exact tokens.
- Every asset referenced anywhere exists in `artifacts/assets/` and is in `assets-index.md`, OR is declared in `external-assets.md` with full generation detail.
- Every asset you cannot produce yourself is in `external-assets.md` (or it explicitly says "none"); none left as a silent gap or unlabeled placeholder.
- Every external-software configuration value is captured in `external-setup.md` (or it explicitly says "none"); nothing needed is left implicit in an artifact.
- `open-questions.md` has zero unresolved items (you asked the user and recorded the answers).
- No structurally-identical pages were duplicated.

If you cannot meet a point because information is missing: stop, ask the user the specific question, and only then finalize. Inventing the answer is not acceptable.
