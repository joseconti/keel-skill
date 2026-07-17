# Phase 6 — Documentation

Goal: produce complete, usable documentation in `docs/` so anyone (including future-you) can understand, use, extend, and maintain the project without reverse-engineering the code. Documentation has been accumulating since Phase 1; this phase **consolidates** it — it does not write the API/class/function/hook reference from scratch. Per the Phase 5 rule, every public surface introduced during development was already documented at the moment of creation, with a runnable example, as part of the slice that introduced it. If something is missing here it is a Phase 5 defect to fix, not new Phase 6 work.

## The `docs/` layout

By now `docs/` should contain the earlier artifacts. Complete it to this canonical layout:

```
docs/
├── 00-competitive-landscape.md   (from Phase 1 — per-competitor inventory, unified list, external demand)
├── 01-discovery.md
├── 02-functional-spec.md
├── 03-technical-plan.md          (stack, architecture, code map, conventions; from Phase 2)
├── 05-test-points.md
├── PROGRESS.md                   (living state since Phase 1 — per references/project-state.md)
├── decisions.md                  (append-only decision log since Phase 1)
├── lessons-learned.md            (accumulating problem→solution log since Phase 1)
├── issues.md                     (living forge-issue log — if the project's forge issues were ever worked; per references/project-state.md)
├── estimate.md                   (internal AI-time estimate, versioned — Phases 1–2, per references/estimation-budget.md)
├── budget.md                     (client-facing budget in the client's language — Phase 2)
├── token-ledger.md               (actual token usage per session + final reconciliation — per references/estimation-budget.md)
├── BUILD-SPEC.md                 (if there was UI)
├── playground.md                 (if the project can be run — from Phase 5: verification playground; start/stop, access details, try-it instructions)
├── sprints/                      (one file per sprint; from Phase 5)
│   └── sprint-<N>.md
├── old/                          (archived per sprint at sprint close — never deleted)
│   └── sprint-<N>/
├── flows/                        (journey docs from Phase 2)
├── design/                       (DESIGN-BRIEF.md + returned design-handoff/ + design-requests/, if UI)
├── architecture.md               (NEW — system overview)
├── api/                          (full API reference — grown since Phase 5, consolidated here)
│   ├── README.md                 (index + conventions)
│   ├── INDEX.md                  (one line per public surface — per references/project-state.md)
│   ├── <module-or-endpoint>.md   (one per public surface)
├── usage/                        (NEW — how to use it)
│   ├── installation.md
│   ├── configuration.md
│   ├── getting-started.md
│   └── examples.md
├── reference/                    (classes, functions, hooks — grown since Phase 5)
│   ├── classes.md
│   ├── functions.md
│   └── hooks-and-extension-points.md
├── security.md                   (NEW — applied security summary, from the profile)
└── accessibility.md              (NEW — applied a11y: standard targeted, per-platform measures, verification, known gaps)
```

Numbering map, so no session wonders about the "gaps": `00` competitive landscape and `01` discovery are Phase 1; `02` spec and `03` technical plan are Phase 2; `04-adoption-audit.md` exists only in adopted projects (`references/adoption.md`); the design brief, BUILD-SPEC, playground.md, estimate.md, budget.md, issues.md and token-ledger.md are unnumbered (they live by role: `design/`, root); `05` is the Phase 5 test-point log; `07-release.md` is added by Phase 7 (it does not exist yet at this phase). Websites (Phase 8) add their own artifacts under `docs/site/` or in the site's own repo. The repo root additionally carries the portability lock (`CLAUDE.md` + `AGENTS.md`, optional `GEMINI.md`, and the embedded skill at `.claude/skills/keel/` + `.agents/skills/keel/`) per `references/project-state.md` — repo-only, export-ignored in Phase 7 — and, unless declined, `guide/`: the end-user HTML guide (see its section below), shipped or repo-only per the recorded decision.

Adapt names to the project type (e.g. for a WordPress plugin, `api/` documents REST routes, WP-CLI commands, and MCP abilities; `reference/hooks-and-extension-points.md` documents actions/filters; for an MCP server, `api/` documents tools/abilities and their schemas).

## What each new document must contain

### architecture.md
System overview: components and how they fit, data model (from Phase 2, now as-built), data flow, external integrations, key decisions and why — consolidated from `docs/decisions.md` and `docs/03-technical-plan.md` (as-built), never reconstructed from memory. A diagram (Mermaid) of the architecture. Enough that a new developer understands the shape of the system in one read.

### api/ (full API reference)
For every public surface (REST endpoint, MCP tool/ability, CLI command, public method, hook):
- Name, purpose, since-version.
- Inputs: every parameter — type, required/optional, constraints, default.
- Output: shape, types, examples.
- Errors: every error condition and what is returned.
- Auth/permissions required (cross-reference the security profile).
- A real, runnable example of calling it and the actual response.

No public surface may be undocumented. If something is intentionally internal/private, say so explicitly.

### usage/
- installation.md: exact install steps for the project type (e.g. WP plugin install + dependency like the MCP Adapter plugin; or service deploy).
- configuration.md: every setting, where it lives, valid values, defaults, effects. Include any external setup recap (link to the verified `external-setup` results).
- getting-started.md: shortest path from zero to the core outcome.
- examples.md: several realistic end-to-end examples.

### reference/
- classes.md: every public class — responsibility, constructor, public methods, properties, usage example.
- functions.md: every public function — signature, params, return, side effects, example.
- hooks-and-extension-points.md: how to extend the project safely (WP actions/filters, MCP ability registration, plugin extension points), with examples. For extensible project types this must reflect the Phase 5 density rule: every user-facing string filter, every before/after decision action, every queryable filter, every response filter, and every replaceable public class is listed with its prefixed name, the slice where it was introduced, the parameters passed to listeners, and a runnable example. A missing extension point here means it was not exposed in Phase 5 — that's the defect, not a doc gap.

### security.md
A concrete summary of how the loaded security profile was applied in THIS project: which protections are in place, where, and how a maintainer should keep them intact. Not the generic profile — the applied result.

### Repo `README.md` (the front door)
The repository root gets a short README: what the project is (one paragraph), requirements, install in brief, quickstart, and links into `docs/usage/` and `docs/api/` for everything else. It duplicates nothing — it points. Phase 7 refreshes it for the release.

### accessibility.md
A concrete summary of how accessibility was applied in THIS project: the standard targeted (WCAG 2.2 AA floor / AAA where reached; EN 301 549 / EAA if in scope), the per-platform measures actually implemented (semantic/native structure, keyboard/AT operability, focus management, contrast, target sizes, reduced-motion, honored user preferences), how it was verified (which automated tools and which assistive technologies were tested), how a maintainer keeps it intact, and any known gaps recorded honestly (no overlay, no false conformance claim). Not the generic reference — the applied result. See `references/accessibility.md`.

## The end-user guide — `guide/` at the repo root

`docs/` is written for developers and maintainers. The END USER gets their own artifact: a navigable HTML guide at `guide/` in the repo root — a main `index.html` plus one page per topic — explaining what the product is for and how to do everything with it. The whole `guide/` artifact is built on the **canonical documentation theme** per `references/guide-theme.md` — vendored `_theme/`, brand layer, slot templates — never on improvised per-project HTML/CSS; the same artifact can additionally carry the **developer portal** (a themed render of `docs/`), decided below.

**Ask four questions before building it** (batched, with recommended defaults, per SKILL.md "How to run a phase" §3):

1. **Languages.** One language or several? When more than one, English is recommended as the principal. The default list mirrors the product's shipped locales from Phase 1 §6. One directory per locale (`guide/en/`, `guide/es/`, ...), a language switcher on the index, the principal listed first.
2. **Does it ship in the release package?** The user may not want the guide in the distributable. Yes → it ships and becomes a distributable surface: the placeholder scan in `scripts/keel-verify` covers it and Phase 7 verifies it on the release candidate. No → add `/guide/` to `.gitattributes` `export-ignore` now (Phase 7 re-verifies the boundary) and the guide stays repo-only.
3. **Developer portal?** Render `docs/` into `guide/{locale}/dev/` on the same theme (architecture, API, usage, reference, security, accessibility, changelog), per `references/guide-theme.md`. Recommended **yes** for projects with a public API/hook surface (plugins, libraries, MCP servers); a plain end-user product may skip it. `docs/` stays the single source of truth either way.
4. **Does the developer portal ship in the release package, or stay repo-only?** Same mechanics as question 2, decided separately — a product may ship the user guide and keep the portal repo-only (export-ignore the `guide/*/dev/` subtrees; Phase 7 re-verifies the boundary).

Record all four answers in `docs/decisions.md` and on the project card: the `User guide:` line (languages + ships yes/no + dev portal yes/no and ships/repo-only; "declined" if the user wants no guide at all, which is a valid recorded choice) and the `Docs theme:` line (the vendored theme version, set the moment the theme is vendored per `references/guide-theme.md`).

**Coverage — the guide is VERY detailed, by contract.** The reader must be able to do EVERYTHING the product is capable of, without asking anyone: every capability appears as a task ("how do I ..."), with the exact steps (paths, clicks, commands), what the user should see after each one, and the why in one plain-language line. The completeness check is mechanical, not felt: every v1 feature in `docs/01-discovery.md`/`docs/02-functional-spec.md` and every setting in `docs/usage/configuration.md` maps to its guide section — a capability or setting without its section is a gap that blocks this phase, exactly like an undocumented public surface. Include: what the product is for (one page), installation, configuration (every setting: where it lives, valid values, defaults, effects), one task page per feature, troubleshooting — including how to switch on the debug log and copy its entries (the Phase 5 log switch) — and where to get support.

Build rules:

- **Consolidated, never invented.** The content derives from what already exists — `docs/usage/`, the functional spec, `docs/playground.md`'s try-it instructions, the applied `docs/accessibility.md` — rewritten task-first in plain end-user language. The guide is never a second source of truth: on any conflict, `docs/` wins and the guide is corrected.
- **Built on the canonical theme — vanilla, self-contained, offline by inheritance.** The theme satisfies the standing rules by design (no frameworks, no CDN, self-hosted fonts, relative links only, works from `file://`); building on it is the ONLY path — vendoring, integrity check, brand layer with the contrast contract recomputed, templates, data files and version registration exactly per `references/guide-theme.md`. Never write per-project CSS, never edit `_theme/`; images and screenshots are stored inside `guide/`. Product screenshots, where they genuinely help, follow the guided capture discipline (the user captures, the assistant places).
- **Accessible.** It is HTML: `references/accessibility.md` applies to the guide itself — semantic structure, contrast, keyboard navigation, alt text on every image. The theme ships this verified (WCAG 2.2 AA floor, measured both modes); the content keel pours into it must not break it.
- **The developer portal renders `docs/`, never replaces it** (when chosen). `guide/{locale}/dev/` is regenerated from `docs/` onto the theme's technical components; on any conflict `docs/` wins and the portal is corrected. Its coverage is mechanical against `docs/api/INDEX.md`, one-to-one (`references/guide-theme.md`).
- **Per-locale correct.** Every locale meets the same orthography standard as everything else (SKILL.md "Writing quality"); secondary locales are translations of the principal and are kept in sync with it.
- **Kept current.** Once the guide exists, every feature or behavior change updates it in the same slice/sprint that changes the behavior (the Phase 5 docs-at-creation discipline extends to it), and the maintenance freshness duty (`references/maintenance.md`) includes it.

**The guide check is independent.** When the environment provides subagents (per `references/assistant-config.md`), the completeness check runs as a fresh-context pass: **`guide-qa`** receives ONLY `guide/` plus the capability and settings lists and reports coverage gaps, links or images that do not resolve, steps that assume context the guide never gave, per-locale orthography faults, and misses in the guide's own accessibility basics, plus the three theme checks from `references/guide-theme.md`: every page's `keel-docs-theme` version meta present and equal to the project card's `Docs theme:` line; `guide/_theme/` byte-intact against the theme release's `checksums.txt`; dev-portal coverage vs `docs/api/INDEX.md` one-to-one when the portal exists. The session that wrote the guide never self-certifies it when an independent pass is available; without subagents, the same checks run inline and say so. Findings are Phase 6 defects — fixed before the phase closes; the guide, never the reader, gets fixed.

## Rules

- **This phase consolidates.** Per Phase 5, every public surface was documented at the moment it was created with a runnable example. If a surface is undocumented here, it is a Phase 5 defect — fix the slice, do not retroactively invent docs from the code.
- **Document the as-built reality**, reconciled with the spec. If code and `docs/02-functional-spec.md` disagree, that's a defect to resolve (fix code to match spec, or, if UI, raise a Design Request) — don't document a divergence as if intended.
- **Every public surface documented, with a runnable example.** Examples that don't actually run are a defect.
- **No duplicate functions/methods/classes in the docs.** A near-duplicate in the docs is the trace of a duplicate in the code — refactor the code (per the Phase 5 reuse rule) before consolidating the docs.
- **Extensible project types:** the hooks-and-extension-points reference reflects the density rule (filters on user-facing strings, before/after actions on decisions, filters on queries and responses, replace/extend mechanism on public classes). Missing extension points are Phase 5 defects.
- **Accessibility is consolidated, not invented at the end.** Per Phase 5, accessibility was built and verified in each slice; `docs/accessibility.md` consolidates the applied result and the verification evidence (tools + assistive technologies tested). A barrier discovered here is a Phase 5 defect to fix, not a doc to soften — and no accessibility overlay or unverified conformance claim substitutes for the real thing.
- **Changelog ordering:** in changelogs, list versions oldest → newest (e.g. 2.1.0 then 2.1.1). Never invert.
- **Mark placeholders.** Any not-yet-final doc section is labeled as such, never shipped as if complete.

## Definition of done

- The full `docs/` layout exists and is populated.
- Every public API/class/function/hook is documented with a runnable example, and `docs/api/INDEX.md` matches the docs one-to-one (no orphan rows, no missing rows) — verified by `docs-verifier` when the environment provides subagents, inline otherwise.
- architecture.md (consolidating the key entries of `docs/decisions.md`), usage/, security.md, accessibility.md complete and reconciled with the as-built code.
- Repo README.md present: short front door linking into `docs/`.
- The end-user guide decision is recorded (`User guide:` card line + decisions.md), and — unless declined — `guide/` exists with its navigable index in the chosen language(s), **built on the canonical theme** (`references/guide-theme.md`: `_theme/` vendored checksum-intact, brand layer contrast-verified, `Docs theme:` card line set, version meta on every page), passing the mechanical coverage check (run by `guide-qa` when the environment provides subagents, inline otherwise): every v1 feature and every setting has its guide section — and, when the developer portal was chosen, its `docs/api/INDEX.md` coverage is one-to-one. If it ships, it is placeholder-clean; if not, `/guide/` is export-ignored.
- No undocumented public surface; no unlabeled placeholder.
- `docs/PROGRESS.md` updated.

Then Phase 7.
