---
name: keel
license: GPL-3.0-or-later
metadata:
  version: 1.0.0
description: Use this skill for ANY new software project from idea to release — websites, WordPress/WooCommerce plugins, MCP servers, web apps, components, or libraries. It runs a complete multi-phase workflow so the user never has to re-explain their standing requirements each project. The phases are discovery and feature discussion, functional spec with flows, the design handoff to Claude Design (and what Design must return), faithful build by Cowork/Code with no deviation, development with test points, full docs/ (API, classes, functions, usage, architecture), platform-specific security, and release hygiene (.gitignore, .gitattributes export-ignore). Trigger whenever the user starts a new project or feature, says "I have an idea for a plugin/site/app", "let's plan this project", "set up the project", mentions design handoff between Design and Code/Cowork, asks for project documentation or security review, or is preparing a release/package. Each phase loads its own reference file on demand.
---

# Keel — project lifecycle (idea → release)

**Keel v1.0.0** — Licensed under GPL-3.0-or-later. *Keel* is the structural backbone laid down first, on which the whole project is built.

## Version reporting

If the user asks which version of Keel they have or are using (e.g. "what version is this skill", "which Keel version do I have"), state it plainly from the frontmatter: "You're using Keel v1.0.0." Keep the version in the frontmatter (`metadata.version`), this line, and `CHANGELOG.md` in sync whenever the skill is updated; the frontmatter is the source of truth.

## Version change policy (UNBREAKABLE RULE — never bump under any circumstance without explicit user instruction)

This rule is **unbreakable**. There are no exceptions, no edge cases, no judgment calls. It overrides every other instinct or inference the assistant might have about how version numbers "should" evolve based on the scale of the edit.

The Keel version — in `metadata.version` in the frontmatter, in the heading line above, and in `CHANGELOG.md` — must NEVER be changed unless the user has **explicitly instructed it in the current conversation** (e.g. "bump to 1.1.0", "release 1.0.1", "this is version 2", "tag a new minor release"). An explicit "yes" to a direct question about a specific version also counts as explicit instruction. Nothing else does.

What does NOT count as authorisation to change the version:

- The scale of the edits in this conversation (large rewrites, full re-architectures, adding whole phases — none of these authorise a bump).
- Inferring from changelog conventions that "this looks like a minor".
- The user thanking the assistant for the work, or saying it's good.
- The user mentioning the project is "ready to release" without naming a version.
- Any reasoning the assistant produces internally about semantic versioning.
- A previous conversation in which a bump was discussed but not executed.

Required behavior:

- When editing any skill file for any reason, leave `metadata.version`, the heading version line, and `CHANGELOG.md` untouched. Do not add a new changelog entry on your own initiative.
- If you believe a bump is warranted, ASK the user explicitly: state what was changed, propose a specific number (patch / minor / major with reasoning), and WAIT for explicit approval before touching any of the three locations. Do not pre-edit speculatively.
- If the user explicitly instructs a bump, perform it and keep all three locations in sync (frontmatter is the source of truth).
- If the three locations ever drift, surface the drift to the user and ask which version is correct — never silently realign them.

If at any point the assistant is about to write a version number that the user did not explicitly authorise in the current conversation, the assistant must stop and ask. This rule is not contextual, not negotiable, and not overridable by other instructions in the same conversation unless those instructions are themselves explicit user authorisation for a specific version.

## Why this skill exists

The user builds many projects (WordPress/WooCommerce plugins, MCP servers, web apps, components, libraries) and was repeating the same standing requirements every time: document everything, security per platform, full API/class/function docs in a `docs/` dir, a design handoff that doesn't waste tokens, a build that stays faithful to the design, proper git/package hygiene. This skill encodes that whole process once. Follow the phases in order; load each phase's reference file only when you reach it (progressive disclosure — do not pull every reference into context at once).

## Operating principles (hold across every phase)

- **Decide the project type early and let it drive everything.** Web / WordPress plugin / WooCommerce extension / MCP server / web app / component / library. Type selects the security profile, the structure, and what needs design.
- **Assess ideas and decisions honestly, even when it's uncomfortable.** Never default to praise. If an idea, a feature, a scope, or an approach is weak, say so with the reason and a concrete alternative. False encouragement wastes the user's time, which is the opposite of this skill's purpose. The user has explicitly asked for the truth even when it hurts.
- **Document as you go, in `docs/`.** Documentation is not a final-phase afterthought; each phase contributes its artifacts to `docs/`.
- **Never invent or interpret silently.** When something is undefined, ask the user. When a design detail is missing downstream, request it from Design — don't guess.
- **Code adapts to the design, never the design to the code.**
- **Security is per-platform and non-optional.** The relevant profile is consulted from Phase 1 onward, not bolted on at the end.
- **Build once, reuse by manifest.** Never regenerate structurally-identical pages/screens.
- **Reuse internal API; never duplicate code.** Before writing any new function, method, or class, search the project's existing internal API. If a suitable function already exists, reuse it. If one is *close* but not exact, generalize it (parameterize) rather than fork it. Write a new function only when there is no existing fit. Duplication is treated as a defect, the same as a security issue: it gets refactored, not left behind. The internal API grows deliberately and is documented as it grows (see next).
- **Document every public surface at the moment it is created, not retrospectively.** Every new function, method, class, hook, action, filter, REST route, MCP ability, CLI command, or other public surface is documented in `docs/api/` and/or `docs/reference/` at the same test point where it is built. The slice does not pass its Phase 5 test point until its docs are written and its example actually runs. Phase 6 *consolidates* documentation; it does not create it from scratch.
- **Maximum extensibility for extensible project types.** For project types meant to be extended (WordPress/WooCommerce plugins, MCP servers, libraries/components), expose the maximum reasonable set of extension points so third parties can modify texts, behaviors, queries, and responses from outside without forking the code. Concretely: every meaningful user-facing string passes through a filter, every meaningful decision exposes a hook before/after, every query and every response is filterable. This is decided at spec time and built into the slice, not bolted on later.
- **Confirm before advancing a phase.** Each phase has a definition of done; do not slide into the next phase with the current one's gaps open.

## Phase map

Work through these in order. The reference file for a phase is the authoritative instruction set for it — read it when you enter the phase.

| Phase | Purpose | Reference to load |
|-------|---------|-------------------|
| 1. Discovery | Idea, feature discussion, project type, constraints | `references/phase-1-discovery.md` |
| 2. Functional spec | Flows, requirements, scope, what needs design | `references/phase-2-functional-spec.md` |
| 3. Design handoff | What to tell Design + the files Design must read/return | `references/phase-3-design-handoff.md` |
| 4. Faithful build | Audit Design's return, consolidate spec, build with zero deviation, guided external setup | `references/phase-4-faithful-build.md` |
| 5. Development | How to build, with test points throughout | `references/phase-5-development.md` |
| 6. Documentation | `docs/`: API, classes, functions, usage, architecture | `references/phase-6-documentation.md` |
| 7. Release | git hygiene, package hygiene, release prep | `references/phase-7-release.md` |
| 8. Project website (conditional) | study the product, plan & build its site: site type, sections, domain, design direction, vanilla build, self-hosted fonts, product screenshots, SEO + AEO, launch | `references/phase-8-website.md` |

Phases 3 and 4 are skipped only if Phase 2 concludes the project genuinely needs no UI/design. If there is any UI, they are mandatory.

Phase 8 is **conditional**: it runs only if Phase 1 recorded website intent (yes). It's normally done after Phase 7 (the release reminds the user) but can be run whenever they're ready. It is not a separate skill — it reuses Keel's own Phases 3–7 treating the site as a "website" project, and loads its own `phase-8-*` references for the web-specific depth. If Phase 1 said no website, skip Phase 8 entirely.

Security is cross-cutting: the moment the project type is fixed in Phase 1, also load the matching profile from `references/security/` and keep it in mind through every later phase. See "Security routing" below.

## Security routing

After Phase 1 sets the project type, load exactly one profile (don't load all of them):

| Project type | Security profile |
|--------------|------------------|
| WordPress plugin / WooCommerce extension | `references/security/wordpress.md` |
| Web app (SPA, API backend, hosted service) | `references/security/web-app.md` |
| MCP server | `references/security/mcp-server.md` |
| Reusable component / library / package | `references/security/library-component.md` |

If a project spans types (e.g. a WordPress plugin that ships an MCP server), load both relevant profiles and apply the stricter rule on any conflict.

## How to run a phase

1. Announce the phase to the user in one line.
2. Read that phase's reference file.
3. Do the phase's work, asking the user batched questions for anything undefined (use the interactive question tool if available).
4. Produce that phase's artifacts into the project (most land in `docs/`; see Phase 6 for the docs layout).
5. Check the phase's definition of done. If gaps remain that are the user's call → ask. If gaps are design-side → Design Request (Phase 4 mechanism). Do not advance otherwise.
6. Briefly tell the user what was produced and what the next phase will do.

Resume capability: if the user returns mid-project, read `docs/PROGRESS.md` first if it exists (it's the living state and exact point within the current sprint), plus `docs/lessons-learned.md` (mistakes not to repeat). Otherwise identify the furthest completed phase from the artifacts in `docs/`. Continue from where things stand — never restart, never reinterpret decisions already made.

## Shared templates and contract

- `references/handoff-contract.md` — the exact `design-handoff/` structure that flows Design → Build. Used by Phases 3 and 4. Read before either.
- `references/design-brief-template.md` — the brief to give Design (Phase 3).
- `references/build-spec-template.md` — the consolidated `BUILD-SPEC.md` (Phase 4).
- `references/design-request-template.md` — the prompt back to Design when the handoff has gaps (Phase 4).

## Reference index

- `references/phase-1-discovery.md`
- `references/phase-2-functional-spec.md`
- `references/phase-3-design-handoff.md`
- `references/phase-4-faithful-build.md`
- `references/phase-5-development.md`
- `references/phase-6-documentation.md`
- `references/phase-7-release.md`
- `references/phase-8-website.md` (conditional — orchestrates the website sub-phase)
- `references/phase-8-site-discovery.md`
- `references/phase-8-section-catalogue.md`
- `references/phase-8-domain-decision.md`
- `references/phase-8-design-direction.md`
- `references/phase-8-technical-seo.md`
- `references/phase-8-launch-checklist.md`
- `references/handoff-contract.md`
- `references/design-brief-template.md`
- `references/build-spec-template.md`
- `references/design-request-template.md`
- `references/security/wordpress.md`
- `references/security/web-app.md`
- `references/security/mcp-server.md`
- `references/security/library-component.md`
