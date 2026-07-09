# Design Request Template

When the audit (Phase 4 Step 1) finds gaps, or `open-questions.md` is unresolved, do not build and do not guess. Fill this template and give it to the user as a ready-to-paste prompt for Claude Design. Keep it surgical: name exactly what is missing, ask Design to fill only that, and to re-deliver into the same handoff structure.

Before handing it over, register it (per `references/project-state.md`): save the filled version as `docs/design/design-requests/DR-NNN.md` (sequential), set the `Status:` line to `sent`, and list it in `docs/PROGRESS.md` "Open items". Mark it `resolved [date]` only when the re-audit passes.

---

# Design Request DR-[NNN]: complete the handoff for [PROJECT NAME]

Status: [sent / resolved YYYY-MM-DD]

The build cannot start because the handoff has gaps. Do **not** redesign anything that already works. Only specify the items listed below, then re-deliver the updated `design-handoff/` in the same structure (artifacts/ + SPEC/).

For anything below that is the user's decision (brand choice, copy, business rule), **ask the user directly — do not invent it.** Record the answers in `SPEC/` and clear the corresponding `open-questions.md` entry.

## Missing or ambiguous items

For each item: what is missing, where it was expected, and what is needed.

### [Category — e.g. Tokens]
- **Missing:** [e.g. `color.danger` is referenced in `SPEC/screens/checkout.md` but absent from `design-tokens.md`]
- **Where expected:** [exact file/screen]
- **Needed:** [exact value, or "ask the user — it's their brand call"]
- **Deliver into:** [`SPEC/design-tokens.md` + `artifacts/styles/`]

### [Category — e.g. States]
- **Missing:** [e.g. `error` and `empty` states for the listing screen are not designed or documented]
- **Where expected:** [`SPEC/screens/listing.md`]
- **Needed:** [design + document those states with exact tokens, at all required breakpoints]
- **Deliver into:** [updated artifact + `SPEC/screens/listing.md`]

### [Category — e.g. Assets]
- **Missing:** [e.g. `icon-export.svg` referenced in assets-index but not present in `artifacts/assets/`; OR the logo/icons shipped only as SVG (or only as PNG); OR an asset delivered in a format the build would have to convert/resize/recolor to use]
- **Needed:** [export the real asset; deliver every logo and icon in BOTH SVG and PNG (PNG at intrinsic size + the platform's required densities/sizes); deliver every asset in a format the build uses directly with no transformation; add each to `assets-index.md` with intrinsic size + every delivered format + exact use]
- **Deliver into:** [`artifacts/assets/` + `SPEC/assets-index.md`]

### [Category — e.g. Behavior / logic]
- **Missing:** [e.g. plan-based gating mentioned but the free vs premium difference per screen is unspecified]
- **Needed:** [specify exact behavior per plan in `SPEC/interactions.md`]

### [Category — e.g. External software setup]
- **Missing:** [e.g. the OAuth provider console requires a redirect URI and scopes, but `SPEC/external-setup.md` has no values — they were left implicit]
- **Where expected:** [`SPEC/external-setup.md`]
- **Needed:** [every exact value the user must enter by hand: software + version, exact path inside it, each field, each exact value/toggle, and the order — because downstream the user is walked through this one verified step at a time and an implicit value cannot be guided. Ask the user for anything that is theirs to decide (IDs, domains, secrets).]
- **Deliver into:** [`SPEC/external-setup.md`]

### [Category — e.g. Accessibility spec]
- **Missing:** [e.g. `SPEC/accessibility.md` has no contrast ratios for the primary buttons, and the listing screen has no focus order or error-identification pattern]
- **Where expected:** [`SPEC/accessibility.md` + `SPEC/screens/<screen>.md`]
- **Needed:** [the accessibility spec for those screens per `references/accessibility.md`: contrast-verified pairs with measured ratios, visible focus + focus order, accessible name/role/state per state, heading/landmark structure, target sizes, reduced-motion variant, text-scaling/high-contrast behavior, and error identification (never color-only). Ask the user for anything that is their brand/content call.]
- **Deliver into:** [`SPEC/accessibility.md` + the relevant `SPEC/screens/*.md`]

### [Category — e.g. Asset Design couldn't produce, missing/thin base prompt]
- **Missing:** [e.g. the landing hero is a photographic image Design can't generate; `SPEC/external-assets.md` names it but has no base prompt, or one too thin to adapt to a generator faithfully]
- **Where expected:** [`SPEC/external-assets.md`]
- **Needed:** [for that asset: a plain explanation of what it is and why, placement detail (role, exact usage location, intended filename, format, intrinsic dimensions/aspect ratio), and a ready, generator-neutral base prompt Design writes itself (subject, composition, mood, include/exclude, exact palette/style from `SPEC/design-tokens.md`). The builder only adapts this base prompt to the user's generator; it must not invent visual content. Ask the user for anything that is their creative call.]
- **Deliver into:** [`SPEC/external-assets.md`]

## Re-delivery requirements

- Keep the existing handoff structure (`references/handoff-contract.md`).
- Do not regenerate structurally-identical pages — keep the template + manifest model.
- Ensure `SPEC/open-questions.md` ends with zero unresolved items.
- Only touch the named gaps; leave everything else byte-stable so the audit can re-pass cleanly.

Once re-delivered, the build will re-audit and proceed only if every gap above is resolved.
