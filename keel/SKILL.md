---
name: keel
license: GPL-3.0-or-later
metadata:
  version: 1.3.0
description: Use this skill for ANY new software project from idea to release — websites, WordPress/WooCommerce plugins, MCP servers, web apps, components, or libraries. It runs a complete multi-phase workflow so the user never has to re-explain their standing requirements each project. The phases are discovery and feature discussion, functional spec with flows, the design handoff to Claude Design (and what Design must return), faithful build by Cowork/Code with no deviation, development with test points, full docs/ (API, classes, functions, usage, architecture), platform-specific security, non-negotiable accessibility applied from the first line on every platform (web, iOS, Android, macOS, Windows), and release hygiene (.gitignore, .gitattributes export-ignore). Trigger whenever the user starts a new project or feature, says "I have an idea for a plugin/site/app", "let's plan this project", "set up the project", mentions design handoff between Design and Code/Cowork, asks for project documentation or security review, is preparing a release/package, resumes/continues an in-progress Keel project (any repo containing docs/PROGRESS.md), or wants to apply Keel to an EXISTING project already underway (adoption: bring an ongoing codebase up to Keel's specifications). Each phase loads its own reference file on demand, and a living state system (docs/PROGRESS.md, decisions log, lessons learned) makes every project resumable across chats without losing context.
---

# Keel — project lifecycle (idea → release)

**Keel v1.3.0** — Licensed under GPL-3.0-or-later. *Keel* is the structural backbone laid down first, on which the whole project is built.

## Version reporting

If the user asks which version of Keel they have or are using (e.g. "what version is this skill", "which Keel version do I have"), state it plainly from the frontmatter: "You're using Keel v1.3.0." Keep the version in the frontmatter (`metadata.version`), this line, and `CHANGELOG.md` in sync whenever the skill is updated; the frontmatter is the source of truth.

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

Scope note: this rule governs **Keel's own version** (this skill's files). The versions of projects *built with* Keel follow their own project rules (Phase 7 versioning) and are not restricted by this section.

## Why this skill exists

The user builds many projects (WordPress/WooCommerce plugins, MCP servers, web apps, components, libraries) and was repeating the same standing requirements every time: document everything, security per platform, full API/class/function docs in a `docs/` dir, a design handoff that doesn't waste tokens, a build that stays faithful to the design, proper git/package hygiene. This skill encodes that whole process once. Follow the phases in order; load each phase's reference file only when you reach it (progressive disclosure — do not pull every reference into context at once).

## Operating principles (hold across every phase)

- **Keep the living state current from the first minute.** `docs/PROGRESS.md`, `docs/decisions.md`, and `docs/lessons-learned.md` are created the moment Phase 1 starts (per `references/project-state.md`) and updated at the moment of every change — not at phase ends. A fresh chat resumes from state, never from re-scanning code or re-asking the user. Decisions recorded in `decisions.md` are never re-opened by the assistant on its own initiative.
- **Work from recorded state; read code surgically.** Orient via `docs/PROGRESS.md`, the technical plan's code map, `docs/architecture.md`, and `docs/api/INDEX.md` — then open only the specific file needed. Read each static reference once per session, in the fixed order defined in `references/project-state.md`; never re-read files already in context. This keeps sessions cheap, deterministic, and prompt-cache-friendly.
- **Decide the project type early and let it drive everything.** Web / WordPress plugin / WooCommerce extension / MCP server / web app / component / library. Type selects the security profile, the structure, and what needs design.
- **Assess ideas and decisions honestly, even when it's uncomfortable.** Never default to praise. If an idea, a feature, a scope, or an approach is weak, say so with the reason and a concrete alternative. False encouragement wastes the user's time, which is the opposite of this skill's purpose. The user has explicitly asked for the truth even when it hurts.
- **Document as you go, in `docs/`.** Documentation is not a final-phase afterthought; each phase contributes its artifacts to `docs/`.
- **Never invent or interpret silently.** When something is undefined, ask the user. When a design detail is missing downstream, request it from Design — don't guess.
- **Code adapts to the design, never the design to the code.**
- **Security is per-platform and non-optional.** The relevant profile is consulted from Phase 1 onward, not bolted on at the end.
- **Accessibility is non-negotiable, on every platform, and designed in from the first line — never retrofitted.** Whatever is built — HTML, iOS, Android, macOS, Windows, or a cross-platform framework — is usable with assistive technology from the first slice, using every accessibility tool the platform offers. It is stated up front in Phase 1 (like the internationalization decision) precisely because building accessibly from the start and "making it accessible" at the end are not the same work — the second is a rewrite. The target is the maximum reasonably achievable: WCAG 2.2 AA as the floor (AAA where feasible), EN 301 549 and the European Accessibility Act where they apply, and the native accessibility API on every other platform. See "Accessibility" below and `references/accessibility.md`.
- **Build once, reuse by manifest.** Never regenerate structurally-identical pages/screens.
- **Reuse internal API; never duplicate code.** Before writing any new function, method, or class, search the project's existing internal API. If a suitable function already exists, reuse it. If one is *close* but not exact, generalize it (parameterize) rather than fork it. Write a new function only when there is no existing fit. Duplication is treated as a defect, the same as a security issue: it gets refactored, not left behind. The internal API grows deliberately and is documented as it grows (see next).
- **Document every public surface at the moment it is created, not retrospectively.** Every new function, method, class, hook, action, filter, REST route, MCP ability, CLI command, or other public surface is documented in `docs/api/` and/or `docs/reference/` at the same test point where it is built. The slice does not pass its Phase 5 test point until its docs are written and its example actually runs. Phase 6 *consolidates* documentation; it does not create it from scratch.
- **Maximum extensibility for extensible project types.** For project types meant to be extended (WordPress/WooCommerce plugins, MCP servers, libraries/components), expose the maximum reasonable set of extension points so third parties can modify texts, behaviors, queries, and responses from outside without forking the code. Concretely: every meaningful user-facing string passes through a filter, every meaningful decision exposes a hook before/after, every query and every response is filterable. This is decided at spec time and built into the slice, not bolted on later.
- **Confirm before advancing a phase.** Each phase has a definition of done; do not slide into the next phase with the current one's gaps open.

## Phase map

Work through these in order. The reference file for a phase is the authoritative instruction set for it — read it when you enter the phase.

| Phase | Purpose | Reference to load |
|-------|---------|-------------------|
| 1. Discovery | Competitive scan first, then idea, feature discussion, project type, constraints | `references/phase-1-discovery.md` |
| 2. Functional spec | Flows, requirements, scope, technical plan (stack/architecture/conventions), what needs design | `references/phase-2-functional-spec.md` |
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

## Accessibility (cross-cutting, non-negotiable)

Accessibility is not a project type or a phase — it applies to everything built, on every platform, and it is decided and stated **up front in Phase 1**, not discovered at the end. Building accessibly from line one and "making it accessible" after the fact are different jobs; the second is a rewrite. Treat accessibility exactly like security: load its reference the moment the project type and target platform(s) are fixed in Phase 1, keep it live through every later phase, and tell the user it is in force before anything is built.

Load `references/accessibility.md` once the platform is known. It has a universal core (applies everywhere) plus a section per platform — Web/HTML, WordPress/WooCommerce, iOS/iPadOS, Android, macOS, Windows, and cross-platform frameworks. Apply the universal core plus the section(s) matching the project's target platform(s). If the project spans platforms, apply every matching section.

The commitment is the maximum reasonably achievable, never a token gesture: WCAG 2.2 AA as the floor with AAA where feasible, EN 301 549 and the European Accessibility Act where they apply (they apply to the user's EU market), and the platform's native accessibility API and assistive technologies fully supported — screen readers (VoiceOver, TalkBack, Narrator, NVDA/JAWS), Switch Control / Switch Access, Voice Control / Voice Access, Dynamic Type / system text scaling, and the reduced-motion and high-contrast preferences. "Use every accessibility tool the platform offers" is the standing rule.

## How to run a phase

1. Announce the phase to the user in one line.
2. Read that phase's reference file (once — do not re-read it later in the session).
3. Do the phase's work, asking the user batched questions for anything undefined (use the interactive question tool if available).
4. Produce that phase's artifacts into the project (most land in `docs/`; see Phase 6 for the docs layout), updating `docs/PROGRESS.md` and `docs/decisions.md` as the work happens — not at the end.
5. Check the phase's definition of done **item by item**, and report it to the user as an explicit checklist (✓ met / ✗ not met, one line each). If gaps remain that are the user's call → ask. If gaps are design-side → Design Request (Phase 4 mechanism). Do not advance with any ✗ open.
6. Mark the phase done in `docs/PROGRESS.md` (with its artifacts) and set the next action. Briefly tell the user what was produced and what the next phase will do.

## Entry modes (decide which one applies before doing anything)

1. **New project** — no code yet. Read `references/project-state.md`, initialize the state files (confirming the project directory with the user first), and run Phase 1.
2. **Resume** — `docs/PROGRESS.md` exists. Follow the fixed session-start order from `references/project-state.md`: `docs/PROGRESS.md` (project card, phase status, exact position, open items) → `docs/decisions.md` (never re-litigate) → `docs/lessons-learned.md` (never repeat) → the current phase's reference → only the inputs PROGRESS.md names. Continue from where things stand — never restart, never reinterpret decisions already made. (Keel-built projects that somehow lack state: identify the furthest completed phase from the artifacts in `docs/`, create the state files, then continue.)
3. **Adoption** — real code exists (often released, often with users) but no Keel state: the project predates Keel. Read `references/adoption.md` and follow it: inventory read-only, initialize state and the CLAUDE.md lock, ask the never-made Phase 1 decisions, reconstruct `01/02/03` as-built plus a complete `docs/api/INDEX.md`, audit gaps into `docs/04-adoption-audit.md`, prioritize them with the user, then continue as a normal Keel project. Adoption changes no code.

Portability lock: every Keel project carries a `CLAUDE.md` block (plus optionally the skill embedded at `.claude/skills/keel/`) so that ANY environment or AI opening the repo — Claude app, Cowork, Claude Code, or another assistant — is bound to this workflow even without the skill installed. Defined in `references/project-state.md` ("Portability"); created in Phase 1 step 0a / adoption step 2. If you are running in a project whose lock is missing or predates this mechanism, add it (with the user's OK) before continuing.

Ending a session mid-work (any phase): produce the self-sufficient continuation prompt from `references/project-state.md` so the next chat resumes exactly where this one stopped.

## Shared templates and contract

- `references/project-state.md` — the living state system (PROGRESS.md, decisions.md, lessons-learned.md, Design Request register, api/INDEX.md), the universal continuation prompt, and the context & cache discipline. Read at project start (Phase 1) and on every resume.
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
- `references/project-state.md` (cross-cutting — state, resume, context & cache discipline, portability lock; loaded at project start and on resume)
- `references/adoption.md` (entry mode 3 — adopting Keel in an existing project)
- `references/handoff-contract.md`
- `references/design-brief-template.md`
- `references/build-spec-template.md`
- `references/design-request-template.md`
- `references/accessibility.md` (cross-cutting — non-negotiable, loaded from Phase 1 like the security profile)
- `references/security/wordpress.md`
- `references/security/web-app.md`
- `references/security/mcp-server.md`
- `references/security/library-component.md`
