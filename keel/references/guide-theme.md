# Guide theme — the canonical documentation theme (keel-docs-theme)

Load this reference at the moments that touch `guide/`: Phase 6 when the guide decision is yes (before building anything under `guide/`), maintenance when the freshness duty runs or a guide regeneration is requested, and adoption when an existing project's docs are being brought onto the theme. It defines the ONLY way keel builds the `guide/` artifact: on the canonical theme, never on improvised per-project HTML/CSS.

## What the theme is

**keel-docs-theme** — public repo `https://github.com/joseconti/keel-docs-theme`, semver releases. Each release publishes `keel-docs-theme-vX.Y.Z.zip` (the consumable theme, version-stamped) and `checksums.txt` (SHA-256 of every packaged file plus the zip). The repo README is the consumption contract; the design SPEC inside the repo (`docs/design/design-handoff/SPEC/`) governs tokens, interactions, accessibility, and the data schemas. Art direction "Errata"; brand-neutral core + a strict, closed brand layer; plain HTML + CSS + vanilla JS; no build step; zero external requests; works from `file://`; WCAG 2.2 AA floor with measured ratios in both modes; light + dark automatic; RTL-ready; print stylesheet; offline client-side search.

The zip contains: `_theme/` (css, js, fonts, icons — **the vendorable unit**), `templates/` (`template-entry.html`, `template-audience-home.html`, `template-topic.html` — slot templates with production-correct relative paths), `brand/` (neutral preset `brand.css`), `examples/` (`search-index.js`, `strings-es.js`, `strings-en.js`, `brand-preset-meridian/`), plus LICENSE (MIT; fonts SIL OFL with their license files inside `_theme/fonts/`) and the theme's CHANGELOG.

## The consumption tree (fixed)

```
guide/
├── index.html                  from template-entry (depth 0 → paths _theme/… , brand/…)
├── _theme/                     the vendored theme unit — NEVER edited per project
├── brand/                      brand.css + logo.svg (+ logo-dark.svg) — the only customized folder
├── search-index.js             generated per project (search schema)
├── strings-<locale>.js         UI strings per locale
└── {locale}/{user|dev}/        index.html + one page per topic, from the templates
                                (depth 2 → paths ../../_theme/… , ../../brand/…)
```

Exactly two relative-path depths exist; the templates already carry the correct paths — keep them. Data loads as global `<script src>` files (`window.KEEL_SEARCH_INDEX`, `window.KEEL_I18N`), never `fetch()`.

## Applying the theme — the procedure (in order)

1. **Obtain the latest release.** Any assistant, no credentials: download the latest release's `keel-docs-theme-vX.Y.Z.zip` + `checksums.txt` (e.g. `gh release download --repo joseconti/keel-docs-theme --pattern '*.zip' --pattern 'checksums.txt'`, or the release asset URLs, or `git clone --depth 1 --branch vX.Y.Z https://github.com/joseconti/keel-docs-theme` and run `scripts/package.sh vX.Y.Z`). Record which version was obtained. **No network in the environment → the user is the courier** (standard keel boundary rule): hand them the exact release URL and the exact local path to place the zip at, then continue from the placed file.
2. **Verify integrity before vendoring.** Recompute SHA-256 of the unzipped files against `checksums.txt`. A mismatch stops the vendoring — re-download; never vendor unverified bytes.
3. **Vendor `_theme/` as a unit** into `guide/_theme/`, byte-intact. It is NEVER edited per project — no exceptions, not one selector. If the project needs something the theme lacks, that is an **issue/release on the theme repo, never a local fork or edit** (same philosophy as handoff-contract rule 10: wholesale-replaceable).
4. **Fill the brand layer** at `guide/brand/`: copy the zip's `brand/brand.css`; set ONLY its six custom properties (`--brand-accent`, `--brand-accent-contrast`, `--brand-accent-soft`, `--brand-logo-w/-h`, light AND dark blocks); add the project's `logo.svg` (required; `logo-dark.svg` optional, auto-swapped). **Recompute the contrast contract — never trust it**: accent vs `#FAF7F1` and vs `#FFFDF8` (light), accent vs `#17150F` and vs `#1E1B14` (dark), and contrast-on-accent vs accent — all ≥ 4.5:1 (WCAG arithmetic; theme SPEC design-tokens §8). A failing accent is adjusted with the user before any page is generated.
   **The José Conti preset:** the first time a guide is built for the user's own products, ask once for the accent + logo values, build the preset per the rule above, and record it (decision entry). Reuse it for every later project of his; offer contributing it upstream to the theme repo (an issue/release adding a preset under `examples/`) so it ships with future releases — never as a core edit.
5. **Generate the pages from `templates/`** into the tree above: fill the `{{ slot }}` placeholders with real project content; keep markup, classes, ARIA and relative paths exactly as templated; set `html[lang]`, `[dir]`, `[data-audience]`, `[data-root]` correctly per page. One entry page at the root; per locale and audience, one `index.html` (audience-home) plus one topic page per subject. The end-user pages follow the Phase 6 coverage contract (every capability and setting, task-first).
6. **The developer portal** — `guide/{locale}/dev/` is a themed RENDER of `docs/`: architecture, API surfaces, usage, reference, security, accessibility, changelog, onto the same templates (the theme ships the technical components: code tabs, API surface blocks, hook/class blocks, since/deprecated badges, terminal). `docs/` (Markdown) remains the single source of truth — the portal is regenerated from it, never edited by hand, and never becomes a second source. Coverage is mechanical: every row of `docs/api/INDEX.md` appears in the portal one-to-one (like docs-verifier), and portal content that contradicts `docs/` is a defect of the portal.
7. **Generate the data files per project:** `search-index.js` (one entry per page: title/path/audience/lang/section/excerpt/terms — schema in the theme SPEC assets-index §4) and `strings-<locale>.js` (es/en ship ready in `examples/` — copy as-is; a new locale copies one and translates VALUES only; the 32 keys are the stable contract).
8. **Register the version, on the record:** the project card gets/updates the `Docs theme: vX.Y.Z` line; `docs/decisions.md` records the vendoring (version, date, brand values). Every page already carries `<meta name="keel-docs-theme" content="vX.Y.Z">` from the release-stamped files — keep it; it is the mechanical version marker tooling checks.

## Purity and verification (what guide-qa enforces)

Three mechanical checks, run at the Phase 6 guide check and re-run on the exact candidate at the Phase 7 gate (and after any theme update):

1. **Version meta:** every page under `guide/` carries `<meta name="keel-docs-theme">` and its value equals the project card's `Docs theme:` line — no page missing it, no mixed versions.
2. **`_theme/` integrity:** every file under `guide/_theme/` matches the release's `checksums.txt` (SHA-256, recomputed) — nothing edited, nothing missing, nothing foreign added.
3. **Dev-portal coverage** (when the portal exists): `docs/api/INDEX.md` rows ↔ portal entries, one-to-one, like docs-verifier — no orphan, no gap.

A check failure is a defect: an edited `_theme/` is restored from the release (the project-side need goes upstream as a theme issue); a version drift is re-registered or re-vendored; a coverage gap is filled from `docs/`.

## Updates — offered, never imposed

New projects always take the **latest** release. Existing projects update ONLY in maintenance, with the user's explicit approval, never silently: the maintenance freshness duty checks whether a newer theme release exists and OFFERS it (what the new version brings, from the theme's changelog). On approval: re-vendor `_theme/` wholesale from the new release (never merge), re-verify checksums, regenerate pages only if the new version's templates changed, update the `Docs theme:` card line + decision entry, and re-run the guide-qa checks. Declining is recorded and re-offered on the next freshness pass — never nagged mid-work.
