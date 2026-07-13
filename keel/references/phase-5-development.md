# Phase 5 — Development

Goal: implement the functional spec (and, if there was UI, the faithful build) into working software, with test points throughout so defects surface early instead of at the end. Work is organized into sprints with a living tracking file and a self-sufficient continuation prompt at each sprint close, so a large project survives across multiple chats without losing context or repeating past mistakes.

## Inputs

- `docs/02-functional-spec.md` (requirements, data model, integrations, acceptance criteria, permissions)
- `docs/03-technical-plan.md` (stack, architecture, code map, conventions, testing, tooling commands — the build follows it; if it must change, update it and record the decision, never silently diverge)
- `docs/flows/*.md` (journeys to implement)
- `docs/BUILD-SPEC.md` (if there was a UI — the faithful build contract; never deviate from it)
- `docs/decisions.md` and `docs/lessons-learned.md` (never re-litigate, never repeat)
- The loaded security profile (`references/security/<type>.md`) — apply throughout, not at the end.
- `references/accessibility.md` and the accessibility decision from `docs/01-discovery.md` — apply throughout, not at the end; if there was UI, also the accessibility spec in the handoff (`SPEC/accessibility.md` / `docs/BUILD-SPEC.md` §4a).

## Principles

- **Implement to the spec, not around it.** If the spec is wrong or incomplete, fix the spec (and, if UI-related, that's a Design Request) — don't silently diverge in code.
- **Reuse internal API; never duplicate code.** Before writing any new function, method, or class, search `docs/api/` and `docs/reference/` (which were started at the beginning of Phase 5 and grow with each slice) for an existing fit. If one exists, reuse it. If one is close but not exact, generalize the existing function (add a parameter, lift the type) rather than create a near-duplicate. A near-duplicate is a defect: it gets refactored, not committed. The codebase has exactly one canonical implementation per behavior.
- **Document every new public surface at creation, not later.** Every new function/method/class/hook/action/filter/REST route/MCP ability/CLI command is documented in the right `docs/api/` or `docs/reference/` file as part of the same slice that introduces it. The slice's test point includes "docs updated; example runs". Phase 6 consolidates the documentation that exists; it does not write it from zero.
- **Maximum extensibility for extensible project types.** For WordPress/WooCommerce plugins, MCP servers, and libraries/components, every slice exposes extension points so third parties can override behavior without forking. The default density is: every user-facing string passes through a filter (e.g. WordPress `apply_filters`), every meaningful decision in a flow exposes a `do_action` before and after, every database/query result is filterable before return, every external response (REST, MCP, webhook) is filterable before send, and every public class supports a documented mechanism to be replaced or extended. All extension points are prefixed (the project's namespace), documented in `docs/reference/hooks-and-extension-points.md` at the same slice, and have at least one runnable example.
- **Test points are checkpoints, not a final phase.** After each meaningful unit (a flow, an integration, a permission boundary), stop and verify before continuing — same logic as the one-step-at-a-time external setup: catch the defect where it happened.
- **Real functional verification, not only automated tests.** Whenever the project can be run, the verification playground defined in `docs/03-technical-plan.md` (Docker/docker-compose, wp-env, a playground script, a disposable sandbox — whatever fits the stack) exists from the scaffold onward, and test points include exercising the software in it for real: walk the flow end to end, run the CLI command if one was built, call the API with real requests. Automated tests prove the parts; the playground proves the product. `docs/playground.md` stays current (start/stop commands, access details, step-by-step try-it instructions) so the user can try the current state at any moment.
- **Security profile is live.** Every input boundary, auth path, data write, and external call is checked against the profile as you build it.
- **Accessibility is live, built into every slice.** Every UI slice is built accessible as it is written — semantic/native controls first, accessible name/role/state exposed to the platform accessibility API, keyboard/assistive-tech operability, visible focus and correct focus order, contrast met, adequate target sizes, error identification (not color-only), and honored user preferences (reduced motion, text scaling, high contrast). It is verified at the slice's test point, never deferred. The target is the Phase 1 level (WCAG 2.2 AA floor / AAA where feasible; EN 301 549 / EAA where in scope; the platform's native a11y API). Per `references/accessibility.md`.
- **Project-type structure.** Lay the codebase out per the conventions for the type (WordPress plugin layout, MCP server layout, etc.) — the security profile and Phase 7 depend on a sane structure.
- **Internationalization is a build rule from line one.** If Phase 1 decided multi-language: every user-facing string is externalized through the platform's i18n mechanism, never hardcoded at the use site, never concatenated (use parameterized/placeholder formatting with translator notes, not string addition). The mechanism is platform-specific — do not assume the WordPress pattern is universal:
  - *Function-wrapping model* (WordPress, many web backends): strings wrapped at the use site, e.g. `__()`/`_e()`/`esc_html__()` with the correct text domain; the base locale file (`.pot`) generated from the source strings.
  - *Key/constant model* (native apps — macOS/iOS `.strings` / String Catalogs with `NSLocalizedString`/keys, Android `strings.xml` with `R.string.*`, web frameworks like i18next): code references a stable key/constant and the system substitutes the localized value; the base language is the set of default values bound to those keys in the base catalog.
  In both, the **base language decided in Phase 1** is the source of truth (the literal source strings, or the default values of the keys). That base language is **English by default in every project** — and **always English for WordPress/WooCommerce**, never Spanish-base (per SKILL.md "Output language & internationalization"); write the source strings in English accordingly. The base catalog/locale resource is generated from it and kept current; all other locales are translations derived from it. Pick the idiomatic mechanism for the project's platform/type from Phase 1. If Phase 1 decided single-language, don't scatter a fake i18n layer — but still keep user-facing strings centralized enough that future translation isn't a rewrite. Retrofitting i18n later is a rewrite; that's why the decision was made in Phase 1.
- **Migrations and backward compatibility (if Phase 1 recorded an installed base).** Never assume a clean install. Version the data schema; write migrations that are idempotent and, where feasible, reversible; preserve or transform existing user data, never silently drop it; keep backward compatibility for anything external code or stored config depends on, or provide a documented, gated breaking change. Clean uninstall must not leave sensitive residue unless the user opted in. The upgrade path is tested from the *real previous version*, not only from a clean install — that test point is mandatory.
- **External dependencies fail safe.** For every dependency recorded in Phase 1: pin/check the exact version, and if it's absent or version-incompatible, degrade gracefully (admin notice / disabled feature) — never a fatal that takes down the host. This is verified, not assumed.
- **Forge issues get a living log.** When work originates in — or resolves — an issue on the project's forge (GitHub, GitLab, Gitea, Bitbucket, any other), `docs/issues.md` (template and rules in `references/project-state.md`) is updated at the moment it happens: inventory on triage, and the issue's entry (diagnosis, resolution, commits, verification, pending) as the work is done. The slice that resolves an issue is not done until its entry is written — exactly like its docs and tests.

## Steps

### 0. Plan sprints and extend the tracking (before any code)

Real projects don't fit in one chat. Plan the work as sprints so it survives across sessions and a fresh chat can resume faithfully. The state files (`docs/PROGRESS.md`, `docs/decisions.md`, `docs/lessons-learned.md`) exist since Phase 1 (per `references/project-state.md`) — this step extends them with sprint tracking; it does not create them.

- **Confirm the technical plan.** Re-read `docs/03-technical-plan.md` with the user and complete anything still open (exact tooling commands, test framework specifics). From here on it is the build's rulebook: conventions, error handling, code map.
- **Define the sprints with the user.** Sprints are not fixed-size; decide them together based on this project (a sprint may be one slice or several, e.g. "OAuth + PKCE end to end"). Each sprint is a coherent, closeable chunk with its own acceptance.
- **Create one file per sprint:** `docs/sprints/sprint-<N>.md`, using the sprint template in `references/project-state.md` — scope, slices, acceptance, status.
- **Extend `docs/PROGRESS.md`:** record the sprint plan in the phase-status table and set "Current position" to sprint 1's first slice. During development PROGRESS.md always names the current sprint and the exact point within it. Update it continuously, not just at sprint end.
- **`docs/lessons-learned.md` keeps accumulating.** Whenever something is tried, fails, and a working solution is found, record the problem and the solution so the same mistake is never repeated. Append-only; never trim it.

### 1. Scaffold

Create the project structure per the technical plan's code map, the `docs/` dir (already seeded by earlier phases), and a `tests/` location. Set up `.gitignore` and `.gitattributes` now (full rules in Phase 7) so secrets and build cruft never enter history from commit one.

**Verify the toolchain end to end before slice 1:** run the exact lint / test / build commands from `docs/03-technical-plan.md` on the scaffold (with one trivial passing test). A broken toolchain discovered at slice 8 costs a day; discovered here it costs minutes. Record the verified commands back into the technical plan if they changed.

**Stand up the verification playground with the scaffold (whenever the project can be run):** create the environment the technical plan defined — `docker-compose.yml`, wp-env config, a playground script, a disposable sandbox — start it with the documented commands and verify the software actually loads in it. Create `docs/playground.md` now: exact start/stop commands, access details (URL/host, user, password — local, throwaway credentials only; never production secrets, never reused ones), and step-by-step try-it instructions per flow, extended as slices land. Whenever the user wants to try the current state, hand them the access details and the instructions.

**Commit discipline (from the first commit):** commit at minimum at every passed test point, with a message naming the slice; never end a working session with the repo in a broken state — if a slice is mid-flight, the exact stopping point goes in `docs/PROGRESS.md`. Git history is part of the project's resumable state.

### 2. Build in vertical slices with test points

Work feature/flow by feature/flow, not layer by layer. For each slice:

- **Search the existing internal API before writing new code.** Consult `docs/api/INDEX.md` first (one line per public surface — per `references/project-state.md`); open the full doc in `docs/api/` or `docs/reference/` only on a hit. Reuse if it exists. If a near-fit exists, generalize the existing function instead of forking it. Only create a new function when there is genuinely no fit. Record any reuse/generalization in the slice's notes.
- Implement the slice to its functional requirements.
- **Add extension points as you go (extensible project types).** For WordPress/WooCommerce plugins, MCP servers, and libraries: as each user-facing string, decision, query, and response is written, expose the corresponding filter/action (or platform-equivalent extension point) with the project's prefix. Default to "filterable" rather than hard-coded; opt out only with a recorded reason.
- **Document the new public surfaces of this slice — now, not later.** For every new function, method, class, hook, action, filter, REST route, MCP ability, or CLI command introduced by this slice, write the entry in `docs/api/` and/or `docs/reference/` (signature, params, return, errors, auth, runnable example) AND its one-line row in `docs/api/INDEX.md`. The example must actually run. An INDEX row without its doc, or a doc without its row, is a slice defect.
- **Build the slice accessible as you write it (UI slices).** Use semantic/native controls first; expose accessible name/role/state to the platform accessibility API; ensure keyboard/assistive-tech operability, visible focus and correct focus order; meet contrast and target size; identify errors non-visually too; honor reduced motion, text scaling and high contrast. If there was a design handoff, implement to `SPEC/accessibility.md` / `BUILD-SPEC.md` §4a. Per `references/accessibility.md`.
- **Test point:** verify the slice against its acceptance criteria from `docs/02-functional-spec.md` — success path, empty, invalid, permission failure, and the failure/recovery branch from its flow file. Write automated tests where the output is objectively verifiable; for UI, verify against `docs/BUILD-SPEC.md` state matrix. If a playground exists, also exercise the slice in it for real — walk its flow end to end, run its CLI command, call its endpoint — not only through the automated suite, and extend `docs/playground.md` if the slice added something tryable. The test point also confirms: (a) no duplicated function was introduced; (b) every new public surface is documented and its example runs; (c) for extensible types, the planned extension points are present and prefixed; (d) for UI slices, accessibility is verified — an automated check plus a keyboard pass and a real assistive-tech pass — against `references/accessibility.md` and the accessibility spec; (e) if a playground exists, the slice was exercised in it for real.
- Run the relevant security checks from the profile for this slice (e.g. nonce/capability for a WP admin action, scope/PKCE for an OAuth step, input sanitization, output escaping).
- **If the slice fixed a bug, pin it with a regression test** in the same slice, and link the test from the `docs/lessons-learned.md` entry. If the bug (or feature) came from a forge issue, update its `docs/issues.md` entry in the same slice: diagnosis, resolution, commits, verification, anything pending.
- Only move to the next slice when this one passes its test point. **Commit the passing slice** (message naming the slice) and update `docs/PROGRESS.md` and `docs/05-test-points.md` before continuing. Report the test-point result to the user on substantial slices.

### 3. Integration test points

After integrating external services: verify auth, the happy path, rate/quota handling, and failure handling against the spec. Never hardcode secrets — load from environment/secure store per the security profile.

### 4. Cross-cutting verification

Before declaring development done, run the full pass: all acceptance criteria, all flows including failure paths, the full security profile checklist, and (if UI) the Phase 4 faithfulness checklist still holds after wiring. If a playground exists: run the full pass in it too — every flow exercised for real (UI walked, CLI commands run, API called) — verify `docs/playground.md` matches reality (start/stop commands, access details, try-it instructions), and invite the user to try the flows themselves with those instructions. If UI: accessibility verified end to end against `references/accessibility.md` — automated checks plus keyboard-only and real assistive-technology passes, at the largest text size, with user preferences honored. If multi-language: confirm no user-facing string is hardcoded or concatenated, every string uses the translation mechanism with the right text domain, and the base locale file is generated and current.

### 5. Close the sprint (mandatory at the end of every sprint)

When a sprint's scope is complete and its test points pass, run this close-out before starting the next sprint. Do not skip it — this is what makes the project survive across chats.

1. **Leave the repo clean:** all of the sprint's tests green, everything committed. A sprint never closes with a broken or uncommitted state.
2. **Update `docs/PROGRESS.md`:** mark the sprint's tasks done, record what was completed, and state exactly what the next sprint is and what remains. PROGRESS.md must always reflect reality. Close the sprint's file (`docs/sprints/sprint-<N>.md` status + close-out). Append the sprint's working sessions to `docs/token-ledger.md` if any row is missing (per `references/estimation-budget.md`).
3. **Update `docs/lessons-learned.md`:** add any problem→solution discovered during the sprint. If nothing failed, note that explicitly so it's clear it wasn't skipped. If forge issues were worked this sprint, verify `docs/issues.md` reflects them: entries complete, inventory current.
4. **Archive what's no longer needed:** move documents that are finished AND no longer consulted from `docs/` into `docs/old/sprint-<N>/` (move, never delete — they stay traceable). Follow the archiving rules in `references/project-state.md`: the state files, specs, technical plan, flows, design handoff, api/reference docs, and the current sprint file NEVER move while the project is alive.
5. **Generate the continuation prompt** using the universal template in `references/project-state.md`, with the sprint specifics added: the next sprint's file (`docs/sprints/sprint-<N+1>.md`), the instruction to build **faithfully to the existing spec and design — no reinterpreting, no deviating, no inventing** (gaps go to a Design Request, exactly as in Phase 4), and to run the same per-slice test points and close the next sprint the same way. It MUST be self-sufficient — a new chat has no memory of this conversation or the design.

   Give this prompt to the user and close the sprint cleanly. If the current chat still has capacity, development may continue here — the prompt is insurance, not an order to switch chats.

## Test point log

Maintain `docs/05-test-points.md`:

```
# Test Points — [Project name]
| Slice | Acceptance criteria checked | Real run in playground | Security checks | Accessibility (automated + AT pass) | i18n (strings externalized) | Reuse checked (no new duplicate) | Docs updated (api/reference, example runs) | Extension points exposed (filter/action) | Result | Notes |
```

Every slice must appear with a result before Phase 6. The playground, accessibility, reuse, docs, and extension-point columns are not optional fields — an empty cell is a missing check. (The accessibility cell applies to UI slices; the playground cell to runnable slices; where genuinely not applicable record "n/a".)

## Definition of done

- Every v1 feature implemented to spec with its test point passed and logged.
- Every flow, including failure/recovery paths, verified.
- **If the project can be run: the verification playground exists and starts from its documented commands.** Every flow, CLI command, and API surface was exercised in it for real — not only through the automated suite — and `docs/playground.md` is current: start/stop commands, access details (local, throwaway credentials only), and step-by-step try-it instructions the user can follow to verify the result themselves.
- Security profile checklist passed for every relevant boundary.
- **Accessibility built into every UI slice and verified** (automated + keyboard + real assistive-tech), meeting the Phase 1 targeted level per `references/accessibility.md`, with user preferences honored; if there was UI, built to `SPEC/accessibility.md`.
- **Internal API coherent and reused.** No near-duplicate functions/methods/classes; reuse verified per slice; the codebase has one canonical implementation per behavior.
- **Every public surface introduced in Phase 5 is already documented** in `docs/api/` and/or `docs/reference/` with a runnable example, **and has its row in `docs/api/INDEX.md`**. Phase 6 will only consolidate — there is no undocumented public surface entering Phase 6.
- The build followed `docs/03-technical-plan.md` (conventions, error handling, code map current); any change to the plan was recorded as a decision, never silent.
- Every fixed bug has its regression test; every passed test point has its commit; the repo is clean and green.
- If forge issues were worked: `docs/issues.md` is current — every worked issue has its complete entry (diagnosis, resolution, commits, verification, pending) and the inventory matches the forge.
- `docs/token-ledger.md` has a row per working session (measured or honestly estimated, method stated — per `references/estimation-budget.md`).
- **For extensible project types (WP/Woo plugins, MCP servers, libraries):** every meaningful user-facing string passes through a filter, every meaningful decision exposes an action before/after, every query/response is filterable, and every public class supports a documented replace/extend mechanism. All extension points are prefixed and documented in `docs/reference/hooks-and-extension-points.md` with at least one runnable example each.
- If multi-language: zero hardcoded/concatenated user-facing strings; every string externalized via the platform's idiomatic i18n mechanism (function-wrapping or key/constant catalog); base language is the Phase 1 base language (English by default — always English for WordPress/WooCommerce); base catalog/locale resource generated from it and current. WordPress/WooCommerce projects are verified multi-language-ready with an English `.pot` regardless of what the conversation language was.
- If installed base: upgrade tested from the real previous version (not just clean install); existing data preserved/migrated; backward compat held or breaking change gated and documented; clean uninstall verified.
- Every Phase 1 dependency: version checked and fail-safe behavior verified when absent/incompatible (no fatal).
- If UI: build still matches `docs/BUILD-SPEC.md`.
- `docs/05-test-points.md` complete (all columns, including accessibility / reuse / docs / extension points).
- Every sprint was closed properly: `docs/PROGRESS.md` reflects reality, `docs/lessons-learned.md` updated, finished docs archived to `docs/old/sprint-<N>/`, and a self-sufficient continuation prompt was produced at each sprint close.

No silent divergence from the spec or the design. Then Phase 6.
