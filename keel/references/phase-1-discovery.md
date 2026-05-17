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
## Project type
- Primary: [type]   Secondary: [type or none]
- Security profile loaded: [filename]
## Feature list
| Feature | What it does | Users | Priority | Constraint |
## Scope
- v1: ...
- Later: ...
## Honest assessment
- [the truthful evaluation of the idea: weaknesses, prior art, scope realism — and the verdict]
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

- The idea received an honest assessment and the verdict is recorded (not default praise).
- Project type is fixed and the matching security profile has been loaded.
- v1 scope is explicit and the user agreed to it.
- Installed-base/upgrade reality is recorded; if there's an installed base, the migration obligation is noted.
- External dependencies are listed with exact version, source, and fail-safe behavior.
- The multi-language vs single-language decision is made and recorded (with base/locales/mechanism if multi-language).
- Project-website intent is captured (yes/no + domain choice).
- "Design needed?" is answered.
- `docs/01-discovery.md` exists and has zero open questions left unresolved.

Do not enter Phase 2 with open discovery questions — an unresolved idea-level question becomes an expensive rework later.
