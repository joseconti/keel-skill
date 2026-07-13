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

Numbering map, so no session wonders about the "gaps": `00` competitive landscape and `01` discovery are Phase 1; `02` spec and `03` technical plan are Phase 2; `04-adoption-audit.md` exists only in adopted projects (`references/adoption.md`); the design brief, BUILD-SPEC, playground.md, estimate.md, budget.md, issues.md and token-ledger.md are unnumbered (they live by role: `design/`, root); `05` is the Phase 5 test-point log; `07-release.md` is added by Phase 7 (it does not exist yet at this phase). Websites (Phase 8) add their own artifacts under `docs/site/` or in the site's own repo. The repo root additionally carries the portability lock (`CLAUDE.md`, optional `AGENTS.md` and `.claude/skills/keel/`) per `references/project-state.md` — repo-only, export-ignored in Phase 7.

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
- Every public API/class/function/hook is documented with a runnable example, and `docs/api/INDEX.md` matches the docs one-to-one (no orphan rows, no missing rows).
- architecture.md (consolidating the key entries of `docs/decisions.md`), usage/, security.md, accessibility.md complete and reconciled with the as-built code.
- Repo README.md present: short front door linking into `docs/`.
- No undocumented public surface; no unlabeled placeholder.
- `docs/PROGRESS.md` updated.

Then Phase 7.
