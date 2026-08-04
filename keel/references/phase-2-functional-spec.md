# Phase 2 — Functional Spec

Goal: turn the agreed v1 scope into a precise functional specification with flows, so that everything downstream (design, build, docs) has an unambiguous contract. Still no code, no visual design.

## What to produce

- `docs/02-functional-spec.md` — the functional contract.
- `docs/flows/` — one flow per significant user/system journey (markdown with step lists; include a Mermaid diagram where it clarifies branching).
- `docs/03-technical-plan.md` — the technical foundation: stack, architecture, marked code map, change map, conventions (steps 4 and 4b). Without it, every later session invents its own conventions and the codebase drifts.
- `docs/threat-model.md` — the security posture in three parts: assumptions, controls with their delivery state, and the deliberate omissions (step 4c).
- `docs/estimate.md` (firm version appended) and — only when the project card says `Client budget: yes` — `docs/budget.md`, the client-facing budget (step 7, per `references/estimation-budget.md`).

## Steps

### 1. Functional requirements

For each v1 feature from `docs/01-discovery.md`, write testable requirements: inputs, processing, outputs, preconditions, postconditions, error conditions. "The user can X" is not enough — specify what happens on success, on empty, on invalid, on permission failure. These become test points in Phase 5.

**A requirement may be carried by a reference artifact, not only by prose.** Where something higher-fidelity than a description already exists, attach it and point the requirement at it instead of paraphrasing it: a detailed test suite that acts as the executable spec, a function or module from another codebase to port, a working HTML mockup of the behavior. A file written in code states exactly what prose can only approximate, and it cannot drift from itself. When one is used, the prose requirement stays — reduced to what the file cannot say about itself: what is in scope, what must be matched exactly, what must deliberately change. Nothing here weakens the six parts above or the acceptance criteria; a reference raises fidelity, it never replaces the contract, and where artifact and spec disagree the spec governs.

Three conditions, none optional:

- **It lives in the repo.** Copy the file into `docs/spec-references/` (or, for a visual mockup, `docs/design/references/`) and commit it. A path to the user's disk, or to an artifact in another chat, resolves for nobody: not the next session, not the reviewing subagent, not the developer six months from now. The spec cites the in-repo path — Keel's whole resume model depends on the repo being self-sufficient. The confidential-data check runs on it like any other commit: third-party fixtures and test configs are exactly where real personal data and live credentials hide, so they are scrubbed before the artifact is committed, or it is not committed at all.
- **A tests-as-spec suite is also wired to actually run.** The committed copy in `docs/spec-references/` is the pristine as-delivered record; a working copy goes into the project's own test tree under a named directory and is added to the technical plan's test command, so the suite executes in every run and at the Phase 7 gate. A suite nobody executes is not an acceptance contract, it is a document.
- **Ported code carries its provenance.** Source, author, license, and verified compatibility with the project's Phase 1 license, recorded in its `## Reference artifacts` row and as a D-entry in `docs/decisions.md`. Code whose license is incompatible or unknown is NOT ported — it is re-specified in prose and written fresh. This matters doubly for GPL projects and anything bound for WordPress.org.
- **It is registered.** Each artifact gets its row in the `## Reference artifacts` section of the spec template with its path, kind, and what must be matched.

### 2. Flows

Identify every journey that has more than one step or any branching: e.g. install/activation, auth/login, the core task, admin configuration, error/recovery, external-system interaction. For each, write `docs/flows/<flow-name>.md` with:

- Trigger / entry point
- Numbered steps (actor → system response)
- Branches and conditions (role/plan/state gating — the user's products often have plan/role gating)
- Failure paths and recovery
- A Mermaid diagram when branching is non-trivial

### 3. Data & integrations

- Data model: entities, fields, relationships, validation rules, persistence.
- External integrations: every external API/service, with auth method, endpoints used, rate/quota limits, failure handling. Cross-check the security profile for anything sensitive (tokens, secrets, PII).
- Permissions matrix: who (role/plan) can do what.

### 4. Technical foundation → `docs/03-technical-plan.md`

Decide, with the user, the technical shape of the project — BEFORE design (Phase 3's brief must state where the final code will live) and before any code (Phase 5 confirms and follows it). This is where stack, architecture, and conventions are fixed once, so no later session re-decides them. Record the significant choices in `docs/decisions.md` too.

ALWAYS use this template for `docs/03-technical-plan.md`:

```
# Technical Plan — [Project name]

## Stack (exact versions)
- Language/runtime + minimum versions; host/framework (e.g. WP min, Woo min, PHP min); key dependencies (pinned, from the Phase 1 dependency table)
- Why this stack: [1–3 lines]
## Support matrix & budgets
- Minimum supported platform versions (e.g. PHP / WordPress / WooCommerce / browsers / OS) — these go in the platform headers where applicable
- Performance budgets or capacity assumptions, if relevant
## Architecture
- Components and their responsibilities; data flow (Mermaid where branching)
- Persistence: engine, schema ownership, migration approach (if Phase 1 recorded an installed base: versioned, idempotent migrations per Phase 5)
## Code map (keep current — future sessions orient HERE, never by scanning the tree)
Every row carries a state marker. [E] exists on disk now. [A] to be created by the assistant, naming the slice/phase. [G] generated by a tool once its source exists (build output, .pot, minified asset, codegen).
| Path | State | Purpose (one line) |
## Change map (what a change of each type must touch — see step 4b)
| Change type | Touch always |
## Conventions
- Prefix/namespace: [the project prefix — every function/class/option/hook uses it]
- Naming: [functions / classes / files / hooks patterns]
- Error handling: [one strategy: exceptions vs error objects (e.g. WP_Error) vs result types; user-facing error policy]
- Logging: [mechanism + levels; never log secrets — per the security profile]
## Testing
- Unit tests: framework + the exact run command
- Integration and end-to-end tests: framework + the exact run command, and what gets unit vs integration vs e2e coverage. E2E is REQUIRED when the project has a UI or multi-step user flows — for web that means a browser-driven test (e.g. Playwright)
- Verification playground (whenever the project can be run): the recipe chosen from references/playground-recipes.md for the project type — how the software will be exercised for REAL beyond the automated suite (Docker/docker-compose, wp-env, a playground script, a disposable sandbox, whatever fits the stack) — with exact start/stop commands, the seed-data mechanism (synthetic fixtures or a seeding script — NEVER real data) and its reset command. Stood up at the Phase 5 scaffold; access details + step-by-step try-it instructions for the user live in docs/playground.md
- Driver per surface (per references/test-automation.md): one row per user-visible or externally-reachable surface — surface | driver | headless? | evidence it produces. Where a driver CANNOT run headless (macOS and native Windows UI tests drive the real cursor and keyboard), name the agreed mitigation here: dedicated machine/VM, separate user session, or scheduled batch. The user is never ambushed by a test run taking their screen
- Run mode and recording (browser surfaces): headless is the default; the documented script that runs the same suite headed and slowed down for watching or debugging; and the recording settings (video and trace on, artifacts path, retention). The recording is the evidence and is never traded away for "you can watch it run" — a headed run leaves nothing behind
- Element addressability: the attribute convention every interactive element carries so tests bind to identifiers, not to localized visible text (data-testid / accessibilityIdentifier / AutomationId / resource-id) and the naming pattern. Never fake an accessibility label to make a test findable — it is read aloud to real users
- Division of labour: which flows the assistant drives end to end (the default: all of them) and the exhaustive list of legs it cannot, each with its tag — CREDENTIAL / HARDWARE / ASSISTIVE-TECH / JUDGMENT / EXTERNAL-APPROVAL / PLATFORM-IMPOSSIBLE / PRODUCTION-RISK / NO-EXECUTION — and the steps whoever runs it will follow. A tag covers only the leg that needs it, never the whole flow
- Static analysis and sniffers: the exact command for each (linters, coding-standard sniffers, static analysers, platform-specific checkers), run at every test point, not once before release
- Accessibility automation: the exact mechanism per platform (axe inside the e2e tests per screen AND per state; performAccessibilityAudit inside the Apple UI tests; AccessibilityChecks in the Android test target) and the driven keyboard/focus-order pass
- Read-back duty: how console errors, uncaught exceptions, failed requests, 5xx responses and the platform's own log are captured and asserted, so a screen that looks right while throwing fails its test
- Real exercise per flow: the exact command, URL, or tool call that exercises each main flow in the playground
- Debug logging: the product's own log mechanism and its on/off switch, per platform (Woo: `WC_Logger` + a settings checkbox; WP: plugin log + checkbox/constant; PrestaShop: module config; panel apps: a panel toggle; servers/CLIs/libraries: env var or constant; MCP servers: stderr) — designed for copy-paste diagnosis by the user, ON during development, OFF by default at release (built at the Phase 5 scaffold; verified at the Phase 7 gate)
- Performance budget measurement: how any budget declared in §Support matrix & budgets will be measured
- Regression rule: every bug fixed gets a test pinning the fix, WRITTEN AND FAILING BEFORE the fix (linked from lessons-learned) — the order holds on every project whatever the test-first policy below says
- Test-first policy: [pure-logic / pure-logic + acceptance / none] — the project card's value (see step 4e and references/test-automation.md "When the test is written"): whether pure logic, and on the wider value each slice's acceptance criterion, gets its test written and seen failing BEFORE the code. Name the exact scope where the acceptance level covers only part of the codebase. The second rule that holds at every value, beside the regression rule above: a test derived from an AC-nn or a reproduced bug is never edited to make it pass
## Environment requirements (the source of scripts/keel-doctor — see step 4d)
| Requirement | Required version/state | Severity (blocking/optional) | How it is installed on macOS / Windows / Linux |
## Tooling commands
- lint / test / build / package: the exact commands (verified end-to-end at Phase 5 scaffold)
- Front-end asset build (only if the project ships JS/CSS): the exact minify command/script that regenerates every `*.min.*` from its committed unminified source — run locally by the working assistant, never CI/forge. Source and minified live as a pair in the same dir (`name.js`+`name.min.js`, `name.css`+`name.min.css`); the minified file is never hand-edited. Per SKILL.md "Build assets — source first, minified for production"
## Version touchpoints
- Every place the project's version string lives (e.g. plugin header, readme.txt Stable tag, a VERSION constant, package.json) — Phase 7 syncs ALL of them on release
## License & dependency compatibility
- Project license (from Phase 1); rule: every dependency's license is verified compatible BEFORE adoption
```

The code map and conventions are what keep multi-chat development coherent: a fresh session reads this file instead of exploring the codebase. Keeping the code map current when the layout changes is part of the change, not optional.

**The code map is a TARGET tree, not an inventory — which is why every row is marked.** A tree diagram and a directory listing look identical on the page, and nothing in a plain diagram says which lines are aspiration. So each row carries its state:

| Marker | Meaning | The rule that follows |
|---|---|---|
| `[E]` | Exists on disk now | Confirm it before relying on it — the marker records the last check, not a guarantee |
| `[A]` | To be created by the assistant, in the named slice or phase | **Treat as absent** until that slice creates it |
| `[G]` | Generated by a tool once its source exists (build output, `.pot`, `*.min.*`, codegen) | **Treat as absent** until the source exists AND the generator has run |

The binding rule: **never claim a path exists, or report work as in place, because the code map shows it.** A path that is not `[E]` is absent until a slice makes it real, and a slice's first action is confirming the `[E]` inputs it depends on. Markers are updated in the slice that changes reality — an `[A]` that shipped becomes `[E]` in the same commit, exactly like the docs. This is trap 4 in `references/anti-patterns.md`, and `scripts/keel-verify` checks that every `[E]` row actually exists on disk.

The Testing block is decided in this much detail now for one reason: the coding agent must deliver code that works on first run. Anything a compile, a boot, or a basic test would have caught must never survive to a hand-over — and that is only enforceable in Phase 5 if the frameworks, commands, playground recipe, seed data and per-flow exercises were fixed here, not improvised there.

### 4a. Materialize the assistant config rules and agents (if accepted at step 0a)

If the project card records `Assistant config:` with rules and/or agents accepted, this is the moment to generate them — their sources (the §Conventions above and the loaded security profile) are now fixed. Load `references/assistant-config.md` and produce the rules (path-scoped to the code map's source globs) and the subagents in EVERY accepted tool's container per its matrix and templates; record a D-entry in `docs/decisions.md`. Permissions, the pre-commit gate, and the MCP registration wait for the Phase 5 scaffold.

### 4b. The change map — what each type of change must touch

A table in `docs/03-technical-plan.md`, one row per recurring type of change in THIS project, listing every artifact that must be touched when it happens. It is the highest-value section of the technical plan, because the failure it prevents — changing one side and forgetting the other four — is the characteristic bug of a project with a public surface, a translation layer, a persistence layer and user documentation.

Keel already carries the rule ("document every public surface at the moment it changes", "regenerate the minified asset from its source", "register the uninstall cleanup"). The change map turns that rule into a **checklist specific to this project**, so no slice has to re-derive it. Build it from the project type, the code map and the loaded security profile. For a WordPress plugin it looks like this:

```markdown
| Change type | Touch always |
|---|---|
| New user-facing string | source string in the i18n function with the text domain, regenerate .pot, guide copy if visible there |
| New setting | registration, sanitize callback, default, uninstall cleanup, docs/reference/, guide, changelog |
| New hook or filter | fire site + docblock, docs/api/ entry + INDEX row, a test asserting it fires with its documented args |
| New public function/class/method | docs/api/ entry + INDEX row, runnable example, unit test |
| Changed public signature | the same entry updated (params, return, errors, permissions), the example re-run, changelog; a released surface needs a decisions.md entry |
| New DB table or option | schema + install routine, migration (idempotent), uninstall cleanup, docs/architecture.md |
| New REST route or AJAX action | capability + nonce check, schema, docs/api/ entry + INDEX row, a permission-failure test |
| Front-end asset edited | edit the source, regenerate its *.min.* with the build script, commit the pair |
| New dependency | decisions.md entry with alternatives, license compatibility verified, support matrix if it moves a floor |
| Version bump | every Version touchpoint above, changelog, readme.txt Stable tag |
```

Rules: one row per change type that has happened or will happen more than once — a one-off is not a row. Every artifact named must be a real path or a real command. **A new type of change discovered during Phase 5 adds its row in the slice that discovered it**, not later. The change map is verified at each slice test point (did this slice touch everything its row names?) and at the Phase 7 gate.

### 4c. `docs/threat-model.md` — including what is deliberately NOT defended

The loaded security profile says what to do. The threat model says what this project's posture actually is, and — the part that carries the value — what it deliberately leaves out. Produce it here, from the profile plus the data model, integrations and permissions decided above; keep it current through Phase 5 and re-verify it at the Phase 7 gate.

Three sections, none optional:

1. **Assumptions.** What is public by construction (shipped client code, endpoint shapes, plugin source in a WordPress install), who the adversaries are and what they want. Obscurity is never a control: if publishing the design weakens the system, the design is already broken.
2. **Defended.** One row per threat: the threat, the control, and its **delivery state** — `IN PLACE` (built and verified, with the evidence), `TO BUILD` (a named slice will build it), `MANUAL` (a human configures it in a console, panel or host) or `VERIFY` (only a real-environment test confirms it). **Only `IN PLACE` may be written in the present tense.** Never claim a control that does not ship: "input is sanitized" is false until the sanitization is in the code and a test proves it (trap 10 in `references/anti-patterns.md`).
3. **Not defended — and what to do if it matters.** One row per deliberate omission: what is not covered, the concrete consequence, and what the user would have to add if their risk profile includes it. This table is the reason the artifact exists. **An omission that is written down is a decision; an omission that is silent is a trap** — six months on, nobody can tell "we decided against it" from "we forgot", and the second reading is the dangerous one.

Each security profile in `references/security/` lists the deliberate omissions typical of its project type as the starting point; the project adds its own. Moving a row from the second table to the first is a normal change — it happens when the control ships — and it goes in `docs/decisions.md` like any other.

### 4d. The environment requirements table — what `scripts/keel-doctor` will enforce

Phase 1 §5a asked whether this machine *can* do the job. Here the answer becomes an exhaustive, versioned list, because the doctor generated at the Phase 5 scaffold is a direct compilation of this table — not a fresh improvisation. Read `references/test-automation.md` if it is not already in context.

Fill `## Environment requirements` in the technical plan with one row per requirement, covering four groups:

1. **Build and run:** the language runtime and its minimum version, the package manager, the container runtime if the recipe needs one, the database, anything the app itself needs to boot.
2. **Test drivers:** the browser automation package and its browser binaries, the mobile or desktop driver, the protocol driver, the PTY tooling for interactive CLIs — whatever the "Driver per surface" rows require.
3. **Static analysis:** every linter, coding-standard sniffer, static analyser and platform checker named in §Tooling commands.
4. **Platform toolchains, where they apply:** the full Apple toolchain (Xcode.app, not just the Command Line Tools — plus accepted licence, first-launch components and simulator runtimes), the Android SDK with an emulator image and hardware acceleration, a virtual display for Linux GUI runs.

For every row record: the required version or state, whether it is **blocking** (no work possible without it) or **optional**, and the install path per operating system the project supports. Two rules keep the table honest:

- **Distinguish "installed but not operational".** A container runtime present with its daemon stopped is not the same as absent, and the doctor must say which. Collapsing the two is what makes an assistant propose reinstalling something that only needed starting.
- **Flag licence and privilege consequences in the row itself**, not in a footnote — a desktop container product whose licence depends on company size and revenue, a group membership that is effectively root, a download of hundreds of megabytes. These are the user's decisions, and they need to see them before `--fix` runs. Where a lighter path exists, name it in the same row.

Also record here **what cannot be installed on this machine at all** and what happens instead: a platform toolchain that requires different hardware, a permission that cannot be granted without degrading system security, a system-dependency installer that does not know this Linux distribution (the container is the answer there). Those rows exist so the doctor reports a clear stop instead of attempting a workaround that does not exist.

### 4e. The test-first policy — one question, asked once

Read `references/test-automation.md` ("When the test is written") if it is not already in context, then ask the user ONE question and record the answer on the project card as `Test-first policy:`. It never gets asked again.

> "Tests can be written before the code or after it. Written after, a test tends to describe what the code does rather than what we asked for, so a bug can end up baked into a test that passes forever. Written first, it can't copy an implementation that doesn't exist yet. It isn't free everywhere, so Keel's default is the half that is: **`pure-logic`** — anything that is a pure function of its inputs (signatures, parsers, validators, state machines, money) gets its test first; everything else stays as it is today. The wider option, **`pure-logic + acceptance`**, also starts every slice from a failing check derived from its acceptance criterion — better evidence, and it adds real time at the front of each slice. **`none`** turns both off. Which one?"

Rules for this step:

- **The default is `pure-logic`.** Propose it explicitly; it is the value with a negative net cost. Silence is not an answer — the card gets a value, not a blank.
- **`n/a` exists for one case only:** a project that ships no executable product — a documentation or instruction package, a content repository. It is not an answer for "this project has little logic"; that is `pure-logic` with few rows.
- **`none` needs a `docs/decisions.md` entry** with the consequence stated. A project can decline this the way it can decline anything else in Keel, but not by omission.
- **`pure-logic + acceptance` may be scoped.** If the user wants the acceptance level on one subsystem rather than the whole codebase, record the card value plus the exact scope in the plan's `## Testing` line. A scope that lives only in the conversation does not exist.
- **Whatever the answer, tell the user the two rules it does NOT govern:** every bug fix — slice, maintenance or hotfix — starts from a failing reproduction test, and no test derived from an acceptance criterion or a reproduced bug is ever edited to make it pass. Both apply at `none` too.
- This is a decision about ORDER, not about coverage. Nothing here reduces what gets tested; the driven-test contract of `references/test-automation.md` is unchanged at every value.

### 5. Decide precisely what needs design

This is the bridge to Phase 3. Produce a clear split:

- **Needs design:** every screen/UI surface, listed. Mark which are structurally similar (template-reuse candidates — this prevents Design from regenerating near-identical pages later).
- **No design needed:** backend, jobs, CLI, pure logic.
- **External software the user must configure by hand** (Unity, hosting panel, OAuth console, SaaS settings, DNS, payment gateway): list each. These become the `SPEC/external-setup.md` requirements in Phase 3 and the guided walkthrough in Phase 4.
- **Assets Design likely can't produce** (photographic images, complex illustrations, 3D renders): flag any you can already foresee. These become `SPEC/external-assets.md` requirements in Phase 3 and the guided one-asset-at-a-time generation loop in Phase 4.
- **Rich references the user already holds:** an HTML mockup or prototype of a screen, an artifact generated in another Claude chat, a built page whose behavior should be matched. Copy each into `docs/design/references/`, commit it, and list it per screen by its in-repo path — it travels verbatim into the Phase 3 brief as reference material and is never paraphrased into a description, which is exactly what loses the fidelity that made it worth having. Registered here for the design split and in `## Reference artifacts` when it also carries a functional requirement; the file is the same one.
- **Target devices/viewports and exact breakpoints** (per screen): which devices/viewports each screen must serve and the exact breakpoint values — numbers, not adjectives. The Phase 3 design brief requires exact breakpoints per screen and copies these values verbatim; nothing else upstream captures them, so they are fixed here. Propose recommended defaults (e.g. 360 / 768 / 1280 px) and let the user react.

For every screen that needs design, also record its **accessibility requirements** (semantic structure and heading order, keyboard/assistive-tech operability, contrast, focus order and visible focus, error identification, target size, reduced-motion) — these become part of what Design must specify in Phase 3, per `references/accessibility.md`. Accessibility is not deferred to the build; it is specified with the screen.

Three of these recorded items — foreseen external assets, per-screen accessibility requirements, and target devices/viewports with exact breakpoints — get their own lines in the spec template below (an instruction that dies before the template gets lost) and are inputs Phase 3 carries verbatim into the brief. Ask each with a recommended default, per SKILL.md "How to run a phase": every question answerable by a non-developer.

### 6. Acceptance criteria

Define, per feature, the conditions under which it's considered done. These feed Phase 5 test points and the Phase 4 faithfulness checklist.

**Every criterion carries a stable ID: `AC-01`, `AC-02`, … assigned here, never reused, never renumbered.** The ID is not bookkeeping — it is what makes coverage checkable by a script instead of by anyone's account of themselves. It travels to three places: this list, the name of the test that covers it (`AC-07 checkout rejects an invalid postcode`), and the `Criterion` column of `docs/05-test-points.md`. Renumbering breaks the link between a shipped test and the requirement it proves, so criteria are appended, and a criterion that dies is marked withdrawn rather than deleted and its number reused. A criterion with no ID cannot be verified as covered, which in practice means it will not be.

Every feature with a UI includes **accessibility conditions** in its acceptance criteria — operable by keyboard and assistive technology, accessible name/role/state exposed, contrast met, visible focus, error identification (not color-only), adequate target size, and honored user preferences (reduced motion, text scaling). Accessibility is a done condition of the feature, not a separate later pass (see `references/accessibility.md`).

### 6a. Adversarial spec review (fresh context — before the firm estimate)

Before any number is closed, the spec gets an adversarial review from fresh context: a subagent when the environment provides one, otherwise a strict self-check against this checklist. The reviewer's job is to break the spec, not to admire it. Verify mechanically:

- Every Phase 1 feature has requirements with all six parts: inputs / processing / outputs / preconditions / postconditions / error behavior.
- Every branching journey has its flow file.
- Every screen in the design split has its per-screen accessibility requirements.
- Every requirement has an acceptance criterion.
- Ambiguities are attacked: what happens on empty? On permission denied? On double submit?

Findings fix the spec NOW — a hole closed here costs minutes; the same hole found later is a Design Request or a Phase 5 rework.

**Rubric pass — verifying shape, not only completeness.** The checklist above is mechanical: it catches what is *missing*, never what is *badly shaped*. A spec can pass every item above and still describe an API that third parties will curse for years. So, once, here, put this question to the user — in their language, and in these terms:

> Some things can't be ticked off a list: whether other developers will find this pleasant to build on, whether the screens look like one product, whether the wording sounds like you. We can write down what "good" means for one of those, and the reviewer will check the spec against it. **Recommended: yes for a plugin, an MCP server or a library** — once it ships, the way other people hook into it can't be changed without breaking their sites. For anything else, usually not worth it.

"Whatever you think" is a valid answer: apply the default, record it, move on. Asking and recording the answer is the requirement; taking a rubric is not.

A **rubric** is a short recorded set of criteria for ONE domain, stating in concrete terms what good and bad look like there (`references/accessibility.md` is the shape to imitate — it is exactly this, for accessibility). If the user takes one, write it with them into `docs/rubrics/<domain>.md`, record a D-entry, and have the reviewer score the spec against it in this same step, reporting where it falls short. Where the environment provides subagents and a rubric is ALREADY on record when §6a starts, the mechanical checklist pass and each domain's rubric pass are independent reads of the same spec: dispatch them in ONE parallel block — one agent for the checklist plus one per domain — and merge their findings before fixing anything (`references/assistant-config.md`, "Parallel fan-out"). When the rubric is authored here for the first time, its pass necessarily follows this conversation and runs on the spec as the checklist findings left it; the fan-out applies from the next review onward. Three rules govern it, wherever it is applied:

- **Recorded, never improvised.** A reviewer that invents its own quality bar mid-run has not verified anything — it has substituted its taste for the user's. No rubric on record means no rubric pass.
- **The reviewer flags; it never rewrites.** A rubric adds criteria, never write access.
- **The spec wins.** Where a rubric and something already fixed disagree, the fixed artifact governs and the disagreement is raised as a question (a Design Request when it is design-side), never resolved unilaterally.

Do it now, at authoring time, and never later: an API shape corrected in the spec costs minutes; the same correction after release is a breaking change for every site that installed it. When the project carries assistant subagents, the verifier side is defined in `references/assistant-config.md` ("Domain rubrics"); without them the same pass runs inline, exactly like the review above.

### 7. Firm estimate & client budget (close of spec — AI-time based)

With the real scope now fixed (requirements, flows, screens, slices implied by the technical plan, integrations, external-setup items) and the spec hardened by the step 6a review, close the numbers. Follow `references/estimation-budget.md` end to end: recompute the itemized AI hours and vibe coder hours from the actual spec; compute the AI cost (verified per-token prices if API; ≈ 0 marginal on subscription); append **Estimate v[N] (firm)** to `docs/estimate.md`. The client budget is conditioned on the Phase 1 project-card line — read it, never re-ask it:

- **`Client budget: yes`** → ask the batched budget questions (rate + currency, AI mode and model(s), contingency, the budget's language — it is a client-facing deliverable — taxes note, availability for the calendar estimate) and produce `docs/budget.md` in the client's language — itemized segments priced line by line, the developer block and the AI block SEPARATE, totals, estimated calendar delivery, and terms. Then run the mandatory present → adjust → approve loop with the user (e.g. choosing not to bill the AI cost on subscription) and record the approval and its choices in `docs/decisions.md`. Any scope change after this budget → new version, re-approved (same reference).
- **`Client budget: no`** → skip `docs/budget.md` entirely; the rate, currency and budget-language questions are never asked (AI mode, contingency and availability are still asked — the estimate needs them). The firm estimate in `docs/estimate.md` still closes the phase.

NEVER price from traditional human development time.

## `docs/02-functional-spec.md` structure

ALWAYS use this template:

```
# Functional Spec — [Project name]

## Functional requirements
- per feature: inputs / processing / outputs / pre / post / errors
## Reference artifacts
(only if any — a spec carried by a file instead of prose; the file lives in the repo)
- [in-repo path] — [kind: tests-as-spec / code to port / HTML mockup] — [what must be matched exactly, what must deliberately change, what is out of scope] — [for ported code: source, author, license, compatibility verified — D-entry]
## Data model
## Integrations (with auth, limits, failure handling)
## Permissions matrix
## Flows index
- links to docs/flows/*.md
## Technical plan
- see docs/03-technical-plan.md (stack, architecture, code map, conventions — produced in step 4)
## Design split
- Needs design: [screens, with template-reuse notes]
- No design: [...]
- External manual setup: [...]
- Foreseen external assets (Design likely can't produce): [...]
- Per-screen accessibility requirements: [...]
- Rich references held by the user (HTML mockups, prototypes, artifacts): [in-repo path per screen, committed under docs/design/references/ — the Phase 3 brief ships the files themselves]
- Target devices/viewports and exact breakpoints: [per screen — the Phase 3 brief copies these values verbatim]
## Acceptance criteria (per feature — include accessibility conditions for every UI feature)
## Estimate & budget
- see docs/estimate.md (Estimate v[N] firm) and, when the project card says Client budget: yes, docs/budget.md (client-facing, approved — D-entry in docs/decisions.md)
## Open questions for the user
```

## Definition of done

- Every v1 feature has testable requirements and acceptance criteria, and **every criterion carries its stable `AC-nn` ID** (step 6) — the key the test name and the test-point row are matched on.
- Every UI feature's acceptance criteria include accessibility conditions (keyboard/AT operable, name/role/state, contrast, visible focus, error identification, target size, honored user preferences) per `references/accessibility.md`; every screen that needs design has its accessibility requirements recorded for the Phase 3 brief.
- Every multi-step/branching journey has a flow file.
- Data model, integrations, and permissions are specified.
- `docs/03-technical-plan.md` complete per its template: stack with exact versions, support matrix, architecture, code map, conventions (prefix, naming, error handling, logging), testing approach with run commands, version touchpoints, license-compatibility rule. Significant choices recorded in `docs/decisions.md`.
- Every code-map row carries its state marker (`[E]` / `[A]` / `[G]`), and every `[E]` row was confirmed against the tree rather than assumed (step 4).
- The change map exists with a row per recurring change type in this project, each naming real paths or real commands (step 4b).
- `docs/threat-model.md` exists with all three sections — assumptions, defended controls each carrying a delivery state (`IN PLACE` / `TO BUILD` / `MANUAL` / `VERIFY`), and the "Not defended" table with consequences. No control is written in the present tense unless it is `IN PLACE` with its evidence (step 4c).
- The testing block names a driver per surface, each with its headless verdict and — where a driver takes over the user's screen — the agreed mitigation; the element-addressability convention is recorded; the division of labour lists every leg the assistant cannot drive with its tag (`CREDENTIAL` / `HARDWARE` / `ASSISTIVE-TECH` / `JUDGMENT` / `EXTERNAL-APPROVAL` / `PLATFORM-IMPOSSIBLE` / `PRODUCTION-RISK` / `NO-EXECUTION`) and its steps; on browser surfaces the default run mode and the recording settings are recorded, and a browser surface with no trace/video configured does not pass this gate; static analysis, accessibility automation and the read-back duty each have their exact commands (step 4/§Testing, per `references/test-automation.md`). A UI surface with no driver, or a delegation with no tag, does not pass this gate.
- `## Environment requirements` is complete (step 4d): one row per build, driver, static-analysis and platform-toolchain requirement, with required version/state, blocking-or-optional severity, the per-OS install path, and any licence or privilege consequence flagged in the row. Anything that cannot be installed on this machine at all is recorded with what happens instead. This table is what `scripts/keel-doctor` compiles from at the Phase 5 scaffold.
- The test-first policy is settled and recorded (step 4e): the project card carries `Test-first policy:` with one of the three values (or `n/a` with its reason, on a project that ships no executable product at all), a `none` answer carries its `docs/decisions.md` entry, and a scoped `pure-logic + acceptance` names the exact scope in the plan's `## Testing`. A blank card line does not pass this gate — the question has a default (`pure-logic`), not an absence.
- If the project ships front-end JS/CSS: the technical plan names the build/minify script that regenerates every `*.min.*` from its committed source (run locally, never CI/forge) and records the source→minified pairing convention — per SKILL.md "Build assets — source first, minified for production". Projects with no front-end assets, or a different pipeline recorded in `docs/decisions.md`, note it as such.
- If the project card accepted assistant config rules/agents: the rules and subagents generated in every accepted tool's container per `references/assistant-config.md`, path-scoped, identical in substance, recorded in `docs/decisions.md`.
- The design split is explicit, including external-setup items, foreseen external assets, per-screen accessibility requirements, and target devices/viewports with exact breakpoints — each on its own template line, carried into the Phase 3 brief.
- Zero unresolved open questions.
- The adversarial spec review (step 6a) ran before the firm estimate — fresh context (subagent when available, strict self-check otherwise), the full checklist verified mechanically — and every finding was fixed in the spec. The rubric question (§6a) was put to the user and its answer recorded — either a rubric in `docs/rubrics/` whose pass ran with its findings resolved, or a recorded "none for this project".
- Firm estimate appended to `docs/estimate.md` per `references/estimation-budget.md`, and the client budget approved — `docs/budget.md` in the client's language (itemized per segment, developer and AI blocks separate, totals and terms), explicitly approved by the user with the approval recorded in `docs/decisions.md` — or recorded as not applicable (no client: `Client budget: no` on the project card). Client acceptance itself is the user's business — it does not gate Phase 3.
- `docs/PROGRESS.md` updated (phase status, artifacts, next action).

If the project needs design, proceed to Phase 3. If Phase 1 said no design and Phase 2 confirms no UI, skip to Phase 5.
