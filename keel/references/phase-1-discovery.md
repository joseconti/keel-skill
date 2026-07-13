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

- The project state files, initialized FIRST (see step 0a): `docs/PROGRESS.md`, `docs/decisions.md`, `docs/lessons-learned.md`.
- `docs/00-competitive-landscape.md` (step 0).
- `docs/01-discovery.md` containing the sections below.
- `docs/estimate.md` — Estimate v1 (preliminary) — and `docs/token-ledger.md`, at the close of this phase (step 10, per `references/estimation-budget.md`).

## Steps

### 0a. Initialize the project state (before anything else)

Read `references/project-state.md` (if not already loaded). Confirm with the user where the project lives — the project directory / repository — and create it if it doesn't exist; never write into an arbitrary working directory. Then create `docs/PROGRESS.md`, `docs/decisions.md`, and `docs/lessons-learned.md` from the templates in that reference, filling the project card with what is known so far (the rest is filled as this phase decides it). From this moment on, every decision goes to `decisions.md` and every position change goes to `PROGRESS.md` — at the moment it happens, not at phase end.

Also make the workflow portable across environments (the user may continue this project from the Claude app, Cowork, Claude Code in VS Code, or another AI — per `references/project-state.md` "Portability"):

- **Create the `CLAUDE.md` lock** at the repo root (or insert the Keel block between its delimiters if a `CLAUDE.md` already exists). This binds ANY future assistant/session opening the repo to the Keel workflow, whether or not the skill is installed there. Mirror it in `AGENTS.md` if the user works with non-Claude assistants.
- **Offer to embed the skill** at `.claude/skills/keel/` (recommended): the repo becomes self-sufficient — Claude Code loads it as a project skill automatically, and any other environment reads it as files via the lock. Ask once; record the choice in the project card.

If the project already has real code but no Keel state, this is not Phase 1 — it is an adoption: switch to `references/adoption.md`.

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

The type selects: the security profile (load it now — see SKILL.md "Security routing"), the project structure, the release/packaging rules, and whether design is needed at all. Fixing the type — and its target platform(s) — also selects the accessibility toolkit: load `references/accessibility.md` now too (see SKILL.md "Accessibility") and apply it from here on, exactly like the security profile.

### 3. Feature discussion

Draft a feature list with the user. For each feature capture: what it does, who uses it, priority (must / should / could), and any hard constraint. Separate **v1 scope** from **later**. Push back gently on scope creep — a tight v1 is a feature, not a limitation.

### 4. Constraints and non-negotiables

- Platform/host constraints (e.g. WordPress admin, must run on specific PHP/Node, Fly.io, no external font CDNs).
- Existing systems it must not break (existing class names, an existing plugin it extends, an existing API contract).
- Compliance/data concerns (PII, payments, auth) — flag these now so the security profile is applied early.
- **Installed base / upgrade reality.** Is this a fresh v1, or does it iterate on something already running in production with real users and stored data (e.g. an existing plugin going from 2.1.0 → 2.1.1)? If there is an installed base, data migration, backward compatibility, and clean uninstall are NOT optional — record this now; it drives hard rules in Phase 5 and a gate in Phase 7.
- **External dependencies with fixed versions.** List every external dependency the project needs and its exact version and source (e.g. the WordPress MCP Adapter plugin from GitHub at a specific tag, a PHP/Node minimum, a packagist/npm package). Record what must happen if a dependency is absent or version-incompatible — the project must fail safe (degrade with an admin notice), never fatal. This drives a Phase 5 verification.
- **License (decide now — it constrains dependencies).** The project's license is a Phase 1 decision, not a release-time afterthought: it determines which dependencies may be adopted at all (license compatibility is checked for every dependency added in Phase 5) and what the marketplace/platform requires (e.g. WordPress.org requires GPL-compatible). Ask the user; record the license in the discovery doc and `decisions.md`. Phase 7 verifies the LICENSE file and headers ship correctly.

### 5. Accessibility commitment (blocking — decide and state up front, never bolt on later)

State plainly to the user, now, that everything with a UI will be built accessible from the first line. This is non-negotiable, and it is said before any building starts on purpose: building accessibly from the start and "making it accessible" at the end are different jobs, and the second is a rewrite — exactly like retrofitting i18n. So it is fixed here, not discovered at release.

- **Confirm the target platform(s).** Accessibility tooling is platform-specific: web/HTML, WordPress/WooCommerce, iOS/iPadOS, Android, macOS, Windows, or a cross-platform framework (Flutter, React Native, MAUI, Electron/Tauri). Record which — a project may span several — so the matching section(s) of `references/accessibility.md` apply.
- **Load `references/accessibility.md`** now (alongside the security profile) and keep it live through every later phase.
- **State the targeted conformance level.** Default and recommended: WCAG 2.2 AA as the floor, AAA where feasible, plus EN 301 549 / the European Accessibility Act where they apply (the EAA has applied since 28 June 2025 and covers EU e-commerce and digital services — in scope for the user's market), plus each target platform's native accessibility API and assistive technologies. Aiming below AA is a conscious decision with a recorded reason — never a silent default.
- This propagates downstream: Phase 2 acceptance criteria include accessibility conditions, the Phase 3 design brief requires Design to specify accessibility, Phase 5 gives every slice an accessibility test point, and Phase 7 has an accessibility release gate.

Record the decision in the discovery doc.

### 6. Internationalization & output language (blocking — decide now, never later)

The language the user and assistant *converse in* (often Spanish) and the language the product is *built in* are different decisions. Decide both explicitly, with the user, before any later phase. Ask these as batched questions — never assume, never skip:

- **Is this multi-language or single-language?** This is not a checkbox — it changes how the entire codebase is written from line one. Multi-language means every user-facing string is externalized through the platform's translation functions, never concatenated, never hardcoded in code or in the design. Retrofitting i18n later is a rewrite, not a tweak.
- **Which output locales must it ship?** The target languages for the built product (not the conversation language). Capture the full list.
- **Is English the base/principal language?** The base/output language of everything built defaults to **English** — always, in every project — regardless of the language this conversation happens in. Spanish is never the assumed base language of the product. Moving off English is a conscious decision with a recorded reason; the default answer is yes.
- **WordPress / WooCommerce is a fixed rule, not a question:** the base language is **always English** and the project is **always prepared to be multi-language** from line one (strings wrapped in the platform i18n functions with the correct text domain, `.pot` generated from the English source). Do not offer Spanish-base or single-language-Spanish as an option for these types — it is a defect. For these projects, confirm the target locales, not the base.
- If multi-language: record the **base language** (English by default), the **target locales**, and the platform mechanism. Pick the mechanism idiomatic to the project type: a function-wrapping model (e.g. WordPress text domain + `.pot`/`.po`/`.mo`) or a key/constant catalog model (e.g. macOS/iOS `.strings`/String Catalogs, Android `strings.xml`, a web i18n framework with keys). The base language is not just metadata: it is the source of truth for the strings — either the literal source strings written inside the translation functions, or the default values bound to the string keys in the base catalog, depending on the mechanism. Code never hardcodes user-facing text at the use site regardless of model.
- If single-language: state it explicitly and the language (English by default) so the decision is recorded and intentional (not an accident that blocks future translation). Single-language Spanish is not a valid outcome for a WordPress/WooCommerce project (see the fixed rule above).
- **Docs language (separate decision — English by default, token economy).** Also record the language for the `docs/` artifacts themselves. The default is **English** in every project: it is the most token-efficient language, and the state files are re-read in every session, so the saving compounds (SKILL.md "Token economy"). When asking, state the default and the trade-off in one line: docs will be created in English to keep token consumption — and therefore cost — down; any other language (e.g. Spanish) is available on request, knowing it increases both. If the user chooses another language, record the choice with the trade-off acknowledged. This is about created artifacts only — the conversation stays in the user's language — and remains independent of the product's output language. Every doc, in every phase and every future session, is written in this one language; mixing languages across sprints is a defect. Whatever language the docs use, it is written with perfect orthography — every accent, tilde and ñ correct, zero spelling or grammatical errors (SKILL.md "Writing quality — perfect orthography"). Record the docs language in the PROGRESS.md project card.

Record the decision in the discovery doc and `decisions.md`. It propagates to Phase 3 (Design must not hardcode copy; strings are translatable) and is a hard verification point in Phase 5.

### 7. Project website intent (global picture only — execution is a separate skill)

Ask now whether the project will have its own presentation website. This is asked early only so the global picture is known (it can influence naming, branding, domain). Record: will there be a project site? and if so, own domain or a subdomain of the user's existing domain? Do NOT build it here — the website is built in Phase 8 of this skill, normally after the first release. This step only captures the intent so it informs naming/branding/domain.

### 8. Decide if design is needed

State plainly: does this have a UI a human will see and that needs visual design? 
- Yes → Phases 3 and 4 are mandatory.
- No (pure backend/library/MCP server with no UI) → Phases 3 and 4 are skipped; note this in the discovery doc with the reason.

### 9. Design system / brand identity (if design is needed — decide BEFORE Design ever starts)

Everything visual the brand ships — this app, its website, the next plugin's admin screens — must be consistent. That consistency comes from a design system (colors, logo, typography, spacing, component styles like buttons and forms), and whether one already exists is a fact to establish now, not something Design discovers or reinvents per project. Ask the user:

- **Does a design system / corporate identity already exist that applies to this project?** (Brand guidelines, a token file, the `SPEC/design-tokens.md` + assets of a previous Keel project, a corporate style guide, an existing product whose look must be matched.)
  - **If yes:** record its **source and location** (exact path, repo, URL, or document) and its format. It becomes a mandatory input to the Phase 3 brief: Design **applies** it — exact palette, logo usage, typography, component styles — and does not reinvent it. Any deviation Design wants is a question to the user, never a silent restyle.
  - **If no:** decide with the user which of these this project is:
    - **Founding** — this project creates the brand's canonical design system. Design is told so in the brief: the tokens, logo treatment and component styles it produces are built for reuse beyond this project. Record WHERE the canonical system will live afterwards (typically this project's `design-handoff/` `SPEC/design-tokens.md` + `artifacts/styles/` + logo assets) so every future project can point at it in its own Phase 1.
    - **One-off** — this project's look intentionally stands alone (rare; record the reason).
- A project may **span** cases (e.g. corporate colors exist but no component library): record what exists and is binding vs what this project will found.

**Which surfaces/platforms must the design system cover? (ask before founding or extending).** A design system is not platform-neutral in practice: tokens, components, the type scale, spacing, iconography and interaction patterns are expressed differently per surface — web/HTML, WordPress or WooCommerce admin, PrestaShop back office, iOS/iPadOS, watchOS, macOS, tvOS, Android, Windows, a cross-platform framework (Flutter, React Native, MAUI, Electron/Tauri), email, print. Ask the user which surfaces this system must serve and record two things:

- The surface(s) **this project** ships on (usually the target platform already fixed in step 5).
- Any **additional surfaces the design system must anticipate** because it is founded for brand-wide reuse (e.g. the brand is web today but an iOS app is planned) — so the system defines platform-appropriate values now instead of forcing a reinvention later.

This applies to existing systems too: if this project targets a surface the existing system does not yet cover, Design **extends** the system to that surface (mapping the canonical tokens to the native equivalents) — it does not reinvent it. Record the full surface list; it drives what the Phase 3 brief asks Design to deliver: for each surface, the native/idiomatic tokens and component specs (CSS variables + HTML components for web; Dynamic Type, SF Symbols and HIG-aligned components for iOS/macOS; Material and `strings`-friendly components for Android; Fluent conventions for Windows; the WP admin colour scheme and `.wrap` constraints for WordPress; PrestaShop's Bootstrap-based back office for PrestaShop), plus how one canonical token set maps onto each surface so the brand stays identical across all of them. If only one surface is named, state it so the scope is explicit and intentional.

**Founding interview (when founding, or for the missing parts when spanning).** Design should not found a corporate identity from nothing — it needs a base to start from, and that base is the user's answers, collected NOW in one batched questionnaire (use the interactive question tool if available). Ask:

- **Logo:** does one exist? If yes: where are the files, in what formats (SVG master?), and are there usage rules. If no: **should Design create it** as part of founding the system? (yes → it becomes a required brief deliverable with real files and variants — see the brief template; no → who provides it and when, recorded as a dependency).
- **Colors:** existing corporate colors (exact values if known)? Colors the user loves or vetoes? Industry conventions to embrace or avoid?
- **Typography:** an existing or preferred typeface? Licensing constraints (self-hosted only — the same rule Phase 8 enforces for the site)?
- **Personality:** two or three adjectives for the brand (e.g. technical and sober / bold and conversion-focused / minimal and editorial).
- **References:** two or three products/sites whose look the user likes or dislikes — vocabulary for what "good" means here, not something to copy.
- **Modes:** dark mode intent? (contrast/high-contrast behavior is already mandatory per accessibility).
- **Iconography & imagery:** line vs filled icons; photos vs illustrations vs screenshots-only.
- **Vetoes:** anything explicitly banned (colors, styles, clichés).

Record every answer in the discovery doc (template below). These answers are carried verbatim into the Phase 3 brief as the seed Design founds the identity from; whatever the user left unanswered goes to `SPEC/open-questions.md` for Design to ask — never to guess (ask-don't-invent).

Record the decision in the discovery doc, `docs/decisions.md`, and the PROGRESS.md project card. If Phase 1 recorded website intent, note that the site (Phase 8) inherits this same design system by default — a different look for the site is its own recorded decision, not drift.

### 10. Preliminary estimate (close of discovery — AI-time based)

With the v1 scope agreed, produce the preliminary estimate so the user can answer whoever asked for a quote. Load `references/estimation-budget.md` and follow it: itemized AI working hours (per phase, session wall-clock ranges), itemized vibe coder hours (segments — what the developer does + hours), contingency, and the AI cost mode (subscription ≈ 0 marginal cost / API with verified per-token prices). Record it as **Estimate v1 (preliminary)** in `docs/estimate.md`, with wide ranges and stated assumptions, and create `docs/token-ledger.md` (template in that reference) so actual token usage is recorded from here on. NEVER estimate from traditional human development time — the estimate is AI time + supervision time, full stop. If the user needs a client-facing preliminary budget now, produce it per the same reference, clearly marked preliminary; the firm budget comes at Phase 2 close.

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
## License
- License: [e.g. GPL-3.0-or-later] (constrains dependency choices from Phase 5; verified shipping in Phase 7)
## Installed base / upgrade
- Fresh v1? or iterates on production with installed users + data? [state it]
- If installed base: migration / backward-compat / clean-uninstall required (drives Phase 5 + 7)
## External dependencies (fixed versions)
| Dependency | Exact version | Source | Behavior if absent/incompatible (must be fail-safe) |
## Internationalization & output language
- Multi-language? [yes / no]
- Base/output language of the built product: [English by default — always English for WordPress/WooCommerce; off-English only with a recorded reason]
- Target output locales: [the languages the product ships]
- If multi-language: mechanism [e.g. WP text domain + .pot, or .strings catalog]
- If single-language: the one language [English by default] (explicit, intentional; never Spanish-base for WordPress/WooCommerce)
- Docs language (separate from output language): [the one language every docs/ artifact uses, across all sessions — English by default (token economy); another language only by explicit user choice with the trade-off acknowledged; always perfect orthography]
## Accessibility (non-negotiable — stated up front)
- Target platform(s): [web / WordPress-Woo / iOS / Android / macOS / Windows / cross-platform framework — one or several]
- Reference loaded: references/accessibility.md
- Targeted level: [WCAG 2.2 AA floor + AAA where feasible; EN 301 549 / EAA if EU scope; native platform a11y APIs] (below AA only with a recorded reason)
## Project website intent
- Will there be a project site? [yes / no]   If yes: own domain / subdomain of user's domain
- (Built in Phase 8 of this skill, later — not built here)
## Design needed?
- [Yes → Phases 3–4 apply | No → reason]
## Design system / brand identity
- Status: [existing / founding — this project creates the canonical one / one-off / n/a — no UI]
- If existing: source + location [exact path/repo/URL/doc, format] — binding input for the Phase 3 brief
- If founding: where the canonical system will live for future projects [e.g. this project's design-handoff SPEC/design-tokens.md + artifacts/styles/ + logo assets]
- If spanning (partial system exists): what is binding vs what this project founds
- Target surfaces/platforms the system must cover: [web / WordPress-Woo admin / PrestaShop / iOS / iPadOS / watchOS / macOS / tvOS / Android / Windows / cross-platform framework / email / print — one or several], marking which ship in THIS project vs which the system anticipates for future reuse
- Founding interview (if founding/spanning — answers seed the Phase 3 brief):
  - Logo: [exists → files/formats/rules | Design creates it → brief deliverable | user provides → when]
  - Colors: [existing/preferred/vetoed]   Typography: [existing/preferred + licensing]
  - Personality: [2–3 adjectives]   References: [liked/disliked]
  - Modes: [dark mode intent]   Iconography & imagery: [style]   Vetoes: [banned things]
  - Unanswered items: [→ SPEC/open-questions.md for Design to ask]
## Preliminary estimate (AI-time based)
- Estimate v1 (preliminary) recorded in docs/estimate.md: AI hours [X–Y], vibe coder hours [X–Y], contingency [+N%], AI cost mode [subscription / API]
- Token ledger created: docs/token-ledger.md (actuals recorded from here on)
## Open questions for the user
- [anything still undefined — must be resolved before Phase 2]
```

## Definition of done

- State files initialized per `references/project-state.md` (`docs/PROGRESS.md` with the project card filled, `docs/decisions.md` with this phase's decisions recorded, `docs/lessons-learned.md` present) and PROGRESS.md reflects this phase's real status.
- The `CLAUDE.md` lock is in place at the repo root (Keel block between delimiters), and the embed-the-skill question was asked and recorded in the project card.
- Competitive scan completed: `docs/00-competitive-landscape.md` exists with per-competitor inventory, unified feature list, and external-demand list (each item cited). OR — if the scan was impossible from this environment — the user has been informed with the specific reason, the three options were offered, and either (a) the conversation moved to a capable environment and the scan was done there, (b) a different agent/tool produced the scan and the findings were brought back, or (c) the user explicitly chose to skip and the full warning block is recorded verbatim in `docs/01-discovery.md`.
- The "Competitive landscape & opportunity" section of `docs/01-discovery.md` lists table-stakes, differentiator candidates, and AI/MCP layer proposals labelled as added-value or forced-filler (with forced-filler dropped).
- The idea received an honest assessment, grounded in the competitive landscape, and the verdict is recorded (not default praise).
- Project type is fixed and the matching security profile has been loaded.
- v1 scope is explicit and the user agreed to it.
- Installed-base/upgrade reality is recorded; if there's an installed base, the migration obligation is noted.
- External dependencies are listed with exact version, source, and fail-safe behavior.
- The license is decided and recorded (it gates dependency adoption in Phase 5).
- The multi-language vs single-language decision is made and recorded, with the target output locales and mechanism; the base/output language is recorded (English by default — always English for WordPress/WooCommerce, off-English only with a recorded reason); and the docs language (separate from the output language) is recorded (English by default — token economy; off-English only as an explicit user choice with the cost trade-off acknowledged).
- Accessibility commitment recorded and stated to the user up front: target platform(s) captured, `references/accessibility.md` loaded, and the targeted conformance level stated (WCAG 2.2 AA floor by default; below AA only with a recorded reason).
- Project-website intent is captured (yes/no + domain choice).
- "Design needed?" is answered.
- If design is needed: the design-system decision is recorded (existing with source/location, founding with future home, or one-off with reason) in the discovery doc, `decisions.md`, and the project card — including the target surfaces/platforms the system must cover (marking which ship in this project vs which it anticipates for reuse).
- Preliminary estimate produced per `references/estimation-budget.md`: `docs/estimate.md` (Estimate v1 — itemized AI hours and vibe coder hours, contingency, AI cost mode, assumptions stated, wide ranges marked as such) and `docs/token-ledger.md` created. No number is based on traditional human development time.
- `docs/01-discovery.md` exists and has zero open questions left unresolved.

Do not enter Phase 2 with open discovery questions — an unresolved idea-level question becomes an expensive rework later.
