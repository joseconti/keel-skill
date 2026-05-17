# Phase 6 — Documentation

Goal: produce complete, usable documentation in `docs/` so anyone (including future-you) can understand, use, extend, and maintain the project without reverse-engineering the code. Documentation has been accumulating since Phase 1; this phase completes and consolidates it.

## The `docs/` layout

By now `docs/` should contain the earlier artifacts. Complete it to this canonical layout:

```
docs/
├── 01-discovery.md
├── 02-functional-spec.md
├── 05-test-points.md
├── PROGRESS.md                   (living state — to do / done / remaining; from Phase 5)
├── lessons-learned.md            (accumulating problem→solution log; from Phase 5)
├── BUILD-SPEC.md                 (if there was UI)
├── sprints/                      (one file per sprint; from Phase 5)
│   └── sprint-<N>.md
├── old/                          (archived per sprint at sprint close — never deleted)
│   └── sprint-<N>/
├── flows/                        (journey docs from Phase 2)
├── design/                       (DESIGN-BRIEF.md + returned design-handoff/, if UI)
├── architecture.md               (NEW — system overview)
├── api/                          (NEW — full API reference)
│   ├── README.md                 (index + conventions)
│   ├── <module-or-endpoint>.md   (one per public surface)
├── usage/                        (NEW — how to use it)
│   ├── installation.md
│   ├── configuration.md
│   ├── getting-started.md
│   └── examples.md
├── reference/                    (NEW — classes, functions, hooks)
│   ├── classes.md
│   ├── functions.md
│   └── hooks-and-extension-points.md
└── security.md                   (NEW — applied security summary, from the profile)
```

Adapt names to the project type (e.g. for a WordPress plugin, `api/` documents REST routes, WP-CLI commands, and MCP abilities; `reference/hooks-and-extension-points.md` documents actions/filters; for an MCP server, `api/` documents tools/abilities and their schemas).

## What each new document must contain

### architecture.md
System overview: components and how they fit, data model (from Phase 2, now as-built), data flow, external integrations, key decisions and why. A diagram (Mermaid) of the architecture. Enough that a new developer understands the shape of the system in one read.

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
- hooks-and-extension-points.md: how to extend the project safely (WP actions/filters, MCP ability registration, plugin points), with examples.

### security.md
A concrete summary of how the loaded security profile was applied in THIS project: which protections are in place, where, and how a maintainer should keep them intact. Not the generic profile — the applied result.

## Rules

- **Document the as-built reality**, reconciled with the spec. If code and `docs/02-functional-spec.md` disagree, that's a defect to resolve (fix code to match spec, or, if UI, raise a Design Request) — don't document a divergence as if intended.
- **Every public surface documented, with a runnable example.** Examples that don't actually run are a defect.
- **Changelog ordering:** in changelogs, list versions oldest → newest (e.g. 2.1.0 then 2.1.1). Never invert.
- **Mark placeholders.** Any not-yet-final doc section is labeled as such, never shipped as if complete.

## Definition of done

- The full `docs/` layout exists and is populated.
- Every public API/class/function/hook is documented with a runnable example.
- architecture.md, usage/, security.md complete and reconciled with the as-built code.
- No undocumented public surface; no unlabeled placeholder.

Then Phase 7.
