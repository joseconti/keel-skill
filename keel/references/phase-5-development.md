# Phase 5 — Development

Goal: implement the functional spec (and, if there was UI, the faithful build) into working software, with test points throughout so defects surface early instead of at the end. Work is organized into sprints with a living tracking file and a self-sufficient continuation prompt at each sprint close, so a large project survives across multiple chats without losing context or repeating past mistakes.

## Inputs

- `docs/02-functional-spec.md` (requirements, data model, integrations, acceptance criteria, permissions)
- `docs/flows/*.md` (journeys to implement)
- `docs/BUILD-SPEC.md` (if there was a UI — the faithful build contract; never deviate from it)
- The loaded security profile (`references/security/<type>.md`) — apply throughout, not at the end.

## Principles

- **Implement to the spec, not around it.** If the spec is wrong or incomplete, fix the spec (and, if UI-related, that's a Design Request) — don't silently diverge in code.
- **Test points are checkpoints, not a final phase.** After each meaningful unit (a flow, an integration, a permission boundary), stop and verify before continuing — same logic as the one-step-at-a-time external setup: catch the defect where it happened.
- **Security profile is live.** Every input boundary, auth path, data write, and external call is checked against the profile as you build it.
- **Project-type structure.** Lay the codebase out per the conventions for the type (WordPress plugin layout, MCP server layout, etc.) — the security profile and Phase 7 depend on a sane structure.
- **Internationalization is a build rule from line one.** If Phase 1 decided multi-language: every user-facing string is externalized through the platform's i18n mechanism, never hardcoded at the use site, never concatenated (use parameterized/placeholder formatting with translator notes, not string addition). The mechanism is platform-specific — do not assume the WordPress pattern is universal:
  - *Function-wrapping model* (WordPress, many web backends): strings wrapped at the use site, e.g. `__()`/`_e()`/`esc_html__()` with the correct text domain; the base locale file (`.pot`) generated from the source strings.
  - *Key/constant model* (native apps — macOS/iOS `.strings` / String Catalogs with `NSLocalizedString`/keys, Android `strings.xml` with `R.string.*`, web frameworks like i18next): code references a stable key/constant and the system substitutes the localized value; the base language is the set of default values bound to those keys in the base catalog.
  In both, the **base language decided in Phase 1** is the source of truth (the literal source strings, or the default values of the keys — not assumed English), and the base catalog/locale resource is generated from it and kept current; all other locales are translations derived from it. Pick the idiomatic mechanism for the project's platform/type from Phase 1. If Phase 1 decided single-language, don't scatter a fake i18n layer — but still keep user-facing strings centralized enough that future translation isn't a rewrite. Retrofitting i18n later is a rewrite; that's why the decision was made in Phase 1.
- **Migrations and backward compatibility (if Phase 1 recorded an installed base).** Never assume a clean install. Version the data schema; write migrations that are idempotent and, where feasible, reversible; preserve or transform existing user data, never silently drop it; keep backward compatibility for anything external code or stored config depends on, or provide a documented, gated breaking change. Clean uninstall must not leave sensitive residue unless the user opted in. The upgrade path is tested from the *real previous version*, not only from a clean install — that test point is mandatory.
- **External dependencies fail safe.** For every dependency recorded in Phase 1: pin/check the exact version, and if it's absent or version-incompatible, degrade gracefully (admin notice / disabled feature) — never a fatal that takes down the host. This is verified, not assumed.

## Steps

### 0. Plan sprints and set up tracking (before any code)

Real projects don't fit in one chat. Plan the work as sprints so it survives across sessions and a fresh chat can resume faithfully.

- **Define the sprints with the user.** Sprints are not fixed-size; decide them together based on this project (a sprint may be one slice or several, e.g. "OAuth + PKCE end to end"). Each sprint is a coherent, closeable chunk with its own acceptance.
- **Create one file per sprint:** `docs/sprints/sprint-<N>.md` — scope of that sprint, the slices/tasks it contains, its acceptance, and its current status.
- **Create the master tracking file:** `docs/PROGRESS.md` — the single living state of the project: everything to do, everything done, everything remaining, the current sprint and the exact point within it. This is the source of truth a new chat reads first. Update it continuously, not just at sprint end.
- **Create `docs/lessons-learned.md`:** an accumulating log. Whenever something is tried, fails, and a working solution is found, record the problem and the solution so the same mistake is never repeated. Append-only; never trim it.

### 1. Scaffold

Create the project structure appropriate to the type, the `docs/` dir (already seeded by earlier phases), and a `tests/` location. Set up `.gitignore` and `.gitattributes` now (full rules in Phase 7) so secrets and build cruft never enter history from commit one.

### 2. Build in vertical slices with test points

Work feature/flow by feature/flow, not layer by layer. For each slice:

- Implement the slice to its functional requirements.
- **Test point:** verify the slice against its acceptance criteria from `docs/02-functional-spec.md` — success path, empty, invalid, permission failure, and the failure/recovery branch from its flow file. Write automated tests where the output is objectively verifiable; for UI, verify against `docs/BUILD-SPEC.md` state matrix.
- Run the relevant security checks from the profile for this slice (e.g. nonce/capability for a WP admin action, scope/PKCE for an OAuth step, input sanitization, output escaping).
- Only move to the next slice when this one passes its test point. Report the test-point result to the user before continuing on substantial slices.

### 3. Integration test points

After integrating external services: verify auth, the happy path, rate/quota handling, and failure handling against the spec. Never hardcode secrets — load from environment/secure store per the security profile.

### 4. Cross-cutting verification

Before declaring development done, run the full pass: all acceptance criteria, all flows including failure paths, the full security profile checklist, and (if UI) the Phase 4 faithfulness checklist still holds after wiring. If multi-language: confirm no user-facing string is hardcoded or concatenated, every string uses the translation mechanism with the right text domain, and the base locale file is generated and current.

### 5. Close the sprint (mandatory at the end of every sprint)

When a sprint's scope is complete and its test points pass, run this close-out before starting the next sprint. Do not skip it — this is what makes the project survive across chats.

1. **Update `docs/PROGRESS.md`:** mark the sprint's tasks done, record what was completed, and state exactly what the next sprint is and what remains. PROGRESS.md must always reflect reality.
2. **Update `docs/lessons-learned.md`:** add any problem→solution discovered during the sprint. If nothing failed, note that explicitly so it's clear it wasn't skipped.
3. **Archive what's no longer needed:** move documents that are done with and no longer live from `docs/` into `docs/old/sprint-<N>/` (move, never delete — they stay traceable). `docs/` keeps only what's still active. PROGRESS.md, lessons-learned.md, the spec, and the design handoff stay in `docs/` (they're always live).
4. **Generate the continuation prompt.** Produce a ready-to-paste prompt the user will paste into a NEW chat to continue, because the current chat is full. It MUST be self-sufficient — a new chat has no memory of this conversation or the design. The prompt must instruct the new chat to:
   - Load the `keel` skill and resume at Phase 5.
   - Read, in order: `docs/PROGRESS.md` (where we are), `docs/lessons-learned.md` (mistakes not to repeat), `docs/02-functional-spec.md`, `docs/BUILD-SPEC.md` if UI, and the design handoff under `docs/design/`.
   - Identify the next sprint from PROGRESS.md and its sprint file `docs/sprints/sprint-<N+1>.md`.
   - Continue building **faithfully to the existing spec and design — no reinterpreting, no deviating, no inventing**; gaps go to a Design Request, exactly as in Phase 4. The new chat does not redesign or "improve" decisions already made.
   - Run the same per-slice test points and close the next sprint the same way.
   
   Give this prompt to the user and stop the current sprint cleanly. The user starts the next sprint in a fresh chat with that prompt.

## Test point log

Maintain `docs/05-test-points.md`:

```
# Test Points — [Project name]
| Slice | Acceptance criteria checked | Security checks | i18n (strings externalized) | Result | Notes |
```

Every slice must appear with a result before Phase 6.

## Definition of done

- Every v1 feature implemented to spec with its test point passed and logged.
- Every flow, including failure/recovery paths, verified.
- Security profile checklist passed for every relevant boundary.
- If multi-language: zero hardcoded/concatenated user-facing strings; every string externalized via the platform's idiomatic i18n mechanism (function-wrapping or key/constant catalog); base language is the Phase 1 base language; base catalog/locale resource generated from it and current.
- If installed base: upgrade tested from the real previous version (not just clean install); existing data preserved/migrated; backward compat held or breaking change gated and documented; clean uninstall verified.
- Every Phase 1 dependency: version checked and fail-safe behavior verified when absent/incompatible (no fatal).
- If UI: build still matches `docs/BUILD-SPEC.md`.
- `docs/05-test-points.md` complete.
- Every sprint was closed properly: `docs/PROGRESS.md` reflects reality, `docs/lessons-learned.md` updated, finished docs archived to `docs/old/sprint-<N>/`, and a self-sufficient continuation prompt was produced at each sprint close.

No silent divergence from the spec or the design. Then Phase 6.
