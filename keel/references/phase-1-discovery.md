# Phase 1 — Discovery

Goal: turn a raw idea into a clear, agreed problem statement, a feature list, and a fixed project type that drives every later decision. No code, no design yet.

## Evaluate the idea honestly (this comes first, and it matters most)

Before shaping the idea, assess it truthfully. The default failure here is enthusiastic validation — telling the user "great idea!" when it isn't. That is the most expensive mistake in the whole process: an idea-level flaw caught in minute one is worth more than any later optimization, and false encouragement wastes exactly the time this skill exists to save.

So: give an honest, critical assessment even when it's uncomfortable.

- If the premise is flawed, say so and say why.
- If something already solves this better, name it and explain the gap (the user does competitive analysis — be concrete, not vague).
- If the scope is unrealistic for v1, say it and propose what a real v1 is.
- If the value is unclear, push on it until it's clear or the user decides to drop it.
- If the idea is genuinely good, say that too — but only because it survived scrutiny, not by default.

This is constructive honesty, not destructive criticism: every objection comes with its reasoning and, where possible, a concrete alternative. The user explicitly wants the truth even when it hurts. Do not soften an assessment to be agreeable, and do not let a weak idea proceed unchallenged just because the user is invested in it.

## What to produce

Create `docs/01-discovery.md` containing the sections below. This is the first artifact in `docs/`.

## Steps

### 0. Competitive scan (always first — before any other step)

The honest assessment in this phase is only as good as the assistant's view of the landscape. Before asking what the idea is supposed to do, scan for what already exists. The output of this step feeds the honest assessment, the feature list, the v1 scope decision, and any optional AI/MCP layer proposal — all of which are weaker or guesswork if this step is skipped.

Always ask the user upfront: **"Which competitors / similar projects do you already know about?"** The user's own list is a useful seed; combine it with the automated research below.

Produce four artifacts. The first three live in their own file; the fourth integrates into the discovery doc.

#### a. Per-competitor inventory → `docs/00-competitive-landscape.md`

Identify the products/projects that already solve the same problem (open source, commercial, plugin, SaaS, MCP server, library — whatever fits the project type). For each competitor record:

- Name, URL, type/category.
- License / pricing model.
- Current status: actively maintained / dormant / abandoned (last release date, last commit).
- A complete-as-possible list of its functionalities.
- The source cited for each finding (homepage, repo README, marketplace listing, docs page) so the user can verify.

No invented features. If something is unclear, say "not determined" rather than guess.

#### b. Unified feature list (in the same file)

The deduplicated union of every functionality across every competitor. This is the de facto baseline for the category — what users of competing products already take for granted. Mark each entry with which competitors have it.

#### c. External-demand list (in the same file)

Functionalities that real users ask for in those competitors and that are NOT already on the unified list. Sources include: open issues with high engagement, top reviews complaining about absence, forum/Reddit/Discord threads, marketplace 1–2 star reviews citing missing features, vendor changelogs that hint at "coming soon" gaps.

Each item is one specific demand + a citable source. Never speculative ("users probably want X"); always grounded ("X is the top request in <link>").

#### d. Honest opportunity proposal (in `docs/01-discovery.md` under "Competitive landscape & opportunity")

Based on (a)–(c), the assistant proposes:

- **Table-stakes features** — functionalities the new project must include because they are now baseline in the category. Building without them ships a v1 that looks unfinished.
- **Differentiator candidates** — gaps users complain about that the new project could close. These are grounded in (c), not invented.
- **AI / MCP / agentic layer proposals (optional).** Only when they add real, logical value (e.g. semantic search over the project's content, MCP exposure of operations a power user would actually script, an agent step that compresses a repetitive workflow). Each AI/MCP proposal is labelled explicitly as **"added value"** (with the reason it actually helps) or **"forced filler"** (AI for AI's sake). Forced filler is dropped, not softened — same honesty rule as the rest of Phase 1. If no AI/MCP layer is warranted, say so plainly.

#### When the scan cannot be done in this environment

If the assistant cannot perform the scan from this environment (no web/search tool available, no network access, sandboxed terminal, search tool restricted, etc.), it MUST NOT silently skip it. Instead, say so plainly and concretely. For example:

> "I should be researching the existing competition for this project, but I cannot do it from this environment because <specific reason — e.g. 'this terminal Claude Code session has no web search tool', 'this environment has no network access', 'WebFetch is restricted on this host'>."

Then offer the user three options, in this order:

1. **Move the conversation to an environment with web access** (e.g. from a terminal Claude Code session to the desktop Claude app where web tools are available, or to a Cowork session, or to any client where browsing/search is enabled). This is the preferred option.
2. **Use a different agent or tool** that has web research, run the scan there, and bring the findings back into this session as input.
3. **Skip the scan and proceed** — explicitly, with the warning below recorded in `docs/01-discovery.md`.

If the user chooses option 3, record it clearly in `docs/01-discovery.md` under a "Competitive scan: SKIPPED" subsection, and include this warning (do not soften it — the honest-assessment principle applies):

> Skipping the competitive scan is a bad idea. Concretely, the risks the project now carries are:
> - **Duplicate effort.** A mature competitor may already solve this better; building blind risks reinventing it worse.
> - **Missing baseline.** Without the unified feature list, v1 will likely launch missing functionalities users of the category already take for granted, making the product look unfinished on day one.
> - **Ungrounded differentiator.** Without the external-demand list, any "what makes us different" claim is opinion, not evidence — it can collapse on first contact with real users.
> - **Weak honest assessment.** The Phase 1 honest assessment is supposed to be analysis, not opinion. Without the landscape, it degrades to opinion — the very thing this skill exists to avoid.
> - **AI/MCP layer becomes guesswork.** Without seeing what competitors already do or fail to do, any AI/MCP proposal is decoration rather than a deliberate strategic choice.
>
> The project may proceed, but the user has been warned and the decision is on the record. The scan can be performed later from a capable environment and the discovery doc retroactively completed.

Even when option 3 is taken, still capture whatever the user already knows about competitors (the upfront question) so the discovery isn't completely blind.

This step is now the actual first action of Phase 1. Only after it completes (or after option 3 is consciously taken and recorded) do we move to "1. Understand the idea".

### 1. Understand the idea

Ask the user, in batched questions, only what you can't infer:

- What problem does this solve, for whom?
- What's the single most important outcome it must deliver?
- Is this a new project or a feature/extension of an existing one? If extending, what does it plug into?

### 2. Fix the project type (this drives everything)

Pin down exactly one primary type (note a secondary if it genuinely spans):

- Website (marketing/content) 
- WordPress plugin / WooCommerce extension
- MCP server
- Web app (SPA, API backend, hosted service)
- Reusable component / library / package

The type selects: the security profile (load it now — see SKILL.md "Security routing"), the project structure, the release/packaging rules, and whether design is needed at all.

### 3. Feature discussion

Draft a feature list with the user. For each feature capture: what it does, who uses it, priority (must / should / could), and any hard constraint. Separate **v1 scope** from **later**. Push back gently on scope creep — a tight v1 is a feature, not a limitation.

### 4. Constraints and non-negotiables

- Platform/host constraints (e.g. WordPress admin, must run on specific PHP/Node, Fly.io, no external font CDNs).
- Existing systems it must not break (existing class names, an existing plugin it extends, an existing API contract).
- Compliance/data concerns (PII, payments, auth) — flag these now so the security profile is applied early.
- **Installed base / upgrade reality.** Is this a fresh v1, or does it iterate on something already running in production with real users and stored data (e.g. an existing plugin going from 2.1.0 → 2.1.1)? If there is an installed base, data migration, backward compatibility, and clean uninstall are NOT optional — record this now; it drives hard rules in Phase 5 and a gate in Phase 7.
- **External dependencies with fixed versions.** List every external dependency the project needs and its exact version and source (e.g. the WordPress MCP Adapter plugin from GitHub at a specific tag, a PHP/Node minimum, a packagist/npm package). Record what must happen if a dependency is absent or version-incompatible — the project must fail safe (degrade with an admin notice), never fatal. This drives a Phase 5 verification.

### 5. Internationalization decision (blocking — decide now, never later)

Decide explicitly, with the user, before any later phase:

- **Is this multi-language or single-language?** This is not a checkbox — it changes how the entire codebase is written from line one. Multi-language means every user-facing string is externalized through the platform's translation functions, never concatenated, never hardcoded in code or in the design. Retrofitting i18n later is a rewrite, not a tweak.
- If multi-language: the **base language**, the **target locales**, and the platform mechanism. Pick the mechanism idiomatic to the project type: a function-wrapping model (e.g. WordPress text domain + `.pot`/`.po`/`.mo`) or a key/constant catalog model (e.g. macOS/iOS `.strings`/String Catalogs, Android `strings.xml`, a web i18n framework with keys). The base language is not just metadata: it is the source of truth for the strings — either the literal source strings written inside the translation functions, or the default values bound to the string keys in the base catalog, depending on the mechanism. Code never hardcodes user-facing text at the use site regardless of model. The user works in Spanish and the base language is often Spanish — confirm it explicitly rather than assuming English.
- If single-language: state it explicitly and the language, so the decision is recorded and intentional (not an accident that blocks future translation).

Record the decision in the discovery doc. It propagates to Phase 3 (Design must not hardcode copy; strings are translatable) and is a hard verification point in Phase 5.

### 6. Project website intent (global picture only — execution is a separate skill)

Ask now whether the project will have its own presentation website. This is asked early only so the global picture is known (it can influence naming, branding, domain). Record: will there be a project site? and if so, own domain or a subdomain of the user's existing domain? Do NOT build it here — the website is built in Phase 8 of this skill, normally after the first release. This step only captures the intent so it informs naming/branding/domain.

### 7. Decide if design is needed

State plainly: does this have a UI a human will see and that needs visual design? 
- Yes → Phases 3 and 4 are mandatory.
- No (pure backend/library/MCP server with no UI) → Phases 3 and 4 are skipped; note this in the discovery doc with the reason.

## `docs/01-discovery.md` structure

ALWAYS use this template:

```
# Discovery — [Project name]

## Problem & outcome
## Competitive landscape & opportunity
- Scan status: [done / partial / SKIPPED — with warning recorded below]
- Source: see `docs/00-competitive-landscape.md` for per-competitor inventory, unified feature list, and external-demand list
- Table-stakes features the new project must include: ...
- Differentiator candidates (gaps real users complain about, grounded in external-demand list): ...
- AI / MCP / agentic layer proposals (each labelled "added value: <reason>" or "forced filler: dropped"): ...
- (If skipped: copy the full warning block from Step 0 verbatim into this section)
## Project type
- Primary: [type]   Secondary: [type or none]
- Security profile loaded: [filename]
## Feature list
| Feature | What it does | Users | Priority | Constraint |
## Scope
- v1: ...
- Later: ...
## Honest assessment
- [the truthful evaluation of the idea, grounded in the competitive landscape: weaknesses, prior art, scope realism — and the verdict]
## Constraints & non-negotiables
## Installed base / upgrade
- Fresh v1? or iterates on production with installed users + data? [state it]
- If installed base: migration / backward-compat / clean-uninstall required (drives Phase 5 + 7)
## External dependencies (fixed versions)
| Dependency | Exact version | Source | Behavior if absent/incompatible (must be fail-safe) |
## Internationalization
- Multi-language? [yes / no]
- If yes: base language [..], target locales [..], mechanism [e.g. WP text domain + .pot, or .strings catalog]
- If no: single language [..] (explicit, intentional)
## Project website intent
- Will there be a project site? [yes / no]   If yes: own domain / subdomain of user's domain
- (Built in Phase 8 of this skill, later — not built here)
## Design needed?
- [Yes → Phases 3–4 apply | No → reason]
## Open questions for the user
- [anything still undefined — must be resolved before Phase 2]
```

## Definition of done

- Competitive scan completed: `docs/00-competitive-landscape.md` exists with per-competitor inventory, unified feature list, and external-demand list (each item cited). OR — if the scan was impossible from this environment — the user has been informed with the specific reason, the three options were offered, and either (a) the conversation moved to a capable environment and the scan was done there, (b) a different agent/tool produced the scan and the findings were brought back, or (c) the user explicitly chose to skip and the full warning block is recorded verbatim in `docs/01-discovery.md`.
- The "Competitive landscape & opportunity" section of `docs/01-discovery.md` lists table-stakes, differentiator candidates, and AI/MCP layer proposals labelled as added-value or forced-filler (with forced-filler dropped).
- The idea received an honest assessment, grounded in the competitive landscape, and the verdict is recorded (not default praise).
- Project type is fixed and the matching security profile has been loaded.
- v1 scope is explicit and the user agreed to it.
- Installed-base/upgrade reality is recorded; if there's an installed base, the migration obligation is noted.
- External dependencies are listed with exact version, source, and fail-safe behavior.
- The multi-language vs single-language decision is made and recorded (with base/locales/mechanism if multi-language).
- Project-website intent is captured (yes/no + domain choice).
- "Design needed?" is answered.
- `docs/01-discovery.md` exists and has zero open questions left unresolved.

Do not enter Phase 2 with open discovery questions — an unresolved idea-level question becomes an expensive rework later.
