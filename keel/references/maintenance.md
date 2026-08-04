# Maintenance — the post-release lifecycle

Load this when `docs/PROGRESS.md` marks Phase 7 done and anything new arrives: a bug report, a feature request, a dependency alert, a platform update. Phase 7's close hands the project here (current position: "maintenance"), and the Resume entry mode lands here whenever a released project is reopened. Maintenance is not a lighter regime — it is the same discipline (state, tests, evidence, hygiene) applied to smaller units, on a codebase that now has users.

## Every maintenance session opens the same way

Two checks, before triage, because most of a project's life happens here and this is where the contract otherwise evaporates:

- **`scripts/keel-doctor --check`.** Maintenance sessions often start on a machine that has drifted since the last sprint — a runtime upgraded, a container runtime not started, browser binaries pruned. Run it and read the table. If the project has no doctor (it predates v5.0.0, or was adopted), generating it from the technical plan's `## Environment requirements` is the first maintenance change, not a nice-to-have: without it, "the tests pass" cannot be distinguished from "the tests never ran".
- **The conformance sweep, if the baseline moved.** If Keel was updated since the last session, the reconciliation runs per `references/project-state.md` — and it is a sweep from `MANIFEST.md`, not a summary. It never blocks an urgent hotfix: record `Reconciliation pending vX → vY` in PROGRESS.md open items, ship the fix, and complete the sweep before the tag.

**No playground, no drivers?** A released project that never had them gets them as a maintenance change the first time anything is worked on it. It is a few hours once, and it is what turns every future report from "install this zip and tell me if it works" into a driven reproduction with evidence. Do not carry a project indefinitely without the environment its own tests need.

## Triage

- **Reproduce first, in the playground — driven by the assistant, not by the reporter and not by the user.** Before any diagnosis and any fix, reproduce the report in the verification playground (`docs/playground.md`, per `references/playground-recipes.md`). If it only reproduces with production-shaped data, build a synthetic fixture that mimics that shape — same volume, same edge case, invented values — and add it to the seed. Never import real data: the confidential-data rule covers maintenance exactly as it covered development.
- **Classify:** broken for everyone / broken for some (which configuration, which versions) / cosmetic / request. The class decides the path — the first goes to the hotfix path below; the rest are scheduled work, prioritized with the user.
- **Record in `docs/issues.md`** (template in `references/project-state.md`) at the moment of triage — including forge issues, which follow the existing forge-log duty: inventory current, one entry per issue worked. A request the user postpones lands in PROGRESS.md's "Deferred items" (per `references/project-state.md`), never in memory.

- **Sweep both directions before triaging anything.** New issues since the last session, AND new comments on issues that already exist — the second is what tells you whether an issue sitting in `awaiting reporter` has been answered, and in maintenance that gap is measured in weeks. Read them by status per `references/project-state.md`, record what came back in the entry's `Inbound:` field, and only then decide what gets worked. Stamp `docs/issues.md`'s `Last inbound sweep:` line the moment the sweep finishes, found something or not — it is the same field a sprint kickoff reads to decide whether it has to sweep before planning.
- **Answer the issue in three beats, and never close it yourself.** Maintenance is where most forge replies happen, and the lifecycle is the same one the sprint close uses (`references/project-state.md`, "`docs/issues.md`"): comment that the fix has landed and that they will be told when it is testable; notify the developer through the recorded channel that a release or deploy is needed before the reporter can try it (`references/notifications.md`) and WAIT, with the issue at `awaiting deploy` and an open item in PROGRESS.md; comment again once the developer confirms it is up. The reporter's answer is what closes it — or reopens the work. A hotfix shipping and a reporter confirming are different events, and in maintenance they are often weeks apart, which is exactly why the state is written down rather than remembered.

## Hotfix path (critical bug in production)

Phase 7's gate compressed in time — never compressed in content:

1. **Branch from the release tag,** not from main and not from `develop`. Users run the tag; the fix must apply to what they run, without dragging unreleased work along. This is the ONE branching exception to SKILL.md's "Git flow", and it is not a loosening: the hotfix branch merges back into `develop` (pushed by the assistant, in automatic mode, like any other work) and the release itself — the merge to `main` and the tag — remains the user's act, exactly as in Phase 7.
2. **The reproduction test FIRST, then the minimal fix** — the test is written before the fix, run, and seen to fail on the bug itself; it passes after, in the same change, and is **driven** where the bug is user-visible: the regression test reproduces the report through the interface, not only through a unit-level call, or it will not catch the same bug coming back through a different path. A hotfix without its regression test is not done. **The order is not tradeable against urgency, and urgency is exactly when it gets traded** (`references/test-automation.md`, "When the test is written"): a test written after the fix demonstrates that the code does what the code does — it never reproduced the bug, so nothing proves it would catch its return, which is the only job it has. This is the rule whose absence surfaces three versions later as the same report from the same customer, and it costs minutes. A fix urgent enough to ship without it takes a `docs/decisions.md` entry with the consequence stated, never a silent omission.
3. **The full gate, fast — and fast means fanned out, not trimmed:** dispatch the reading verifiers this fix calls for in ONE parallel block per `references/assistant-config.md` ("Parallel fan-out") — `code-reviewer` on the fix diff always, `security-auditor` when the fix touches input handling, auth, data writes or external calls, `docs-verifier` when a public surface moved — while the executing half below runs one agent at a time against the environment, and judge the gate on the merged findings. Chaining them is where a hotfix loses the hours it cannot afford, and dropping one is where it loses the release. `scripts/keel-doctor --check` passing (so it is provable the suite really ran), the FULL automated suite green, `scripts/keel-verify` clean, and real-environment verification of the rebuilt distributable — install the exact package in the real-type environment and **have the assistant drive** the fixed flow plus the critical path in it, with the fields filled and the assertions made, not "install it and see". Command + output + evidence recorded, as always. Anything that genuinely cannot be driven carries one of the eight tags from `references/test-automation.md` with its steps; a hotfix verified only by the user's say-so carries a tag or it is not verified.
4. **The version is a patch, PROPOSED to the user** for explicit approval before any number is written anywhere (Phase 7's versioning discipline); only then sync every touchpoint.
5. **Changelog entry** (oldest → newest), naming the bug and the fix.
6. **Tag, release, then merge back to main,** so the fix exists in both lines — a hotfix that never lands on main resurfaces in the next release.

## Rollback (when the fix cannot be immediate)

Rolling back is a user decision, recorded in `docs/decisions.md`: the assistant proposes it when the fix will take longer than users can wait, and executes it on approval —

- **WordPress.org:** lower the `Stable tag` in trunk's `readme.txt` to the previous good version — the fastest path that platform has; sites roll back without a new build.
- **Hosted service:** redeploy the previous artifact/tag.
- **Package registry:** deprecate the bad version with a message pointing to the good one — never unpublish what users already depend on; unpublishing breaks their builds without warning.

The rollback buys time; the hotfix continues in parallel and ships through the path above.

## Dependencies & CVEs

- **Every maintenance session starts with the stack's audit command** — `npm audit` / `composer audit` / `pip-audit`, whichever the stack uses — before the session's own work. Output recorded; a finding is triaged like any bug report.
- **On a CVE in a dependency:** assess whether the vulnerable path is reachable from this project — and record the assessment either way; "we don't call that function" is an assessment to record, not a reason to skip the record. Then pin or patch the dependency, regression-test, and ship a patch release through the hotfix path.
- **On a platform release** (new WordPress / WooCommerce / Node LTS / OS version): re-run the full suite and the playground against the new platform FIRST, then bump "Tested up to" / engines metadata in a patch release. Compatibility metadata is never bumped untested — an untested "Tested up to" is a false claim made to every user who reads it.

## Recurring features

A new feature on a released project is the full cycle at feature scale, never a drive-by commit:

mini-discovery at Phase 1 §3 scale (the assistant proposes the feature's shape, the user reacts) → spec amendment per the "Scope changes" playbook in `references/project-state.md` (spec, flows, and the estimate/budget revision where a budget exists) → design delta if UI is affected (Phase 3–4 mechanics: brief, handoff, faithful build) → a Phase 5 sprint with its test points → the full Phase 7 for its release.

This is the same cycle `references/adoption.md` defines for adopted projects — greenfield projects use it too after v1. There is no "small enough to skip the cycle": a small feature gets a proportionally small pass through every step, not an exemption from steps.

**The end-user guide is part of the cycle, so nothing is ever left dangling:** when the project carries `guide/` (Phase 6), every added or changed capability updates the guide in the SAME change that ships it — its new task page or its corrected steps, in every locale the guide carries — never "later". A capability the guide does not cover is an open defect, exactly like a missing regression test. If the project has no guide yet, a maintenance pass is a fine moment to offer building it (Phase 6 section, with its language and packaging questions).

## The full-suite rule

EVERY maintenance change, however small, re-runs the entire automated suite before its release — one-line fixes included: the blast radius of a change is what the suite exists to measure, not what the author assumes. And every fixed bug carries its regression test, written and failing BEFORE the fix (a hotfix without one is not done, per the hotfix path — the rule holds on every project whatever its `Test-first policy:` line says) — the suite only protects against what it contains.

## Site freshness (when Phase 8 built a site)

Every product release — a hotfix patch included — triggers the site mini-checklist: JSON-LD `softwareVersion`, the changelog/news page, screenshots if the UI changed, `sitemap.xml` `lastmod`, `llms.txt`. The details live in the launch checklist's "After launch — operations" section (`references/phase-8-launch-checklist.md`). A site announcing an old version is a live defect, not cosmetic drift.

`<site-docs>/operations.md` holds the renewal and monitoring duties — domain renewal, TLS, `security.txt` `Expires` (rotate before expiry), uptime monitoring, backups. Check it whenever a maintenance session touches the site, and honor its dates.

## Docs-theme freshness (when the project carries `guide/`)

The freshness duty includes the guide's theme: check whether `keel-docs-theme` has a newer release than the project card's `Docs theme:` line (latest release of `github.com/joseconti/keel-docs-theme`; no network → skip silently, or ask the user as courier if the check matters now). Newer release → OFFER the update, never impose it: what the new version brings (the theme's changelog), what updating means (wholesale re-vendor of `_theme/`, checksum re-verification, `guide-qa` re-run — per `references/guide-theme.md`). The user's yes/no is recorded; a decline is re-offered at the next freshness pass, never nagged mid-work. A theme update is never silent and never partial.

## State discipline

Maintenance changes nothing about the state system:

- `docs/PROGRESS.md` stays alive — current position "maintenance", plus the exact item in flight; open items and deferred items current.
- `docs/decisions.md` and `docs/lessons-learned.md` keep accruing — a rollback decision, a CVE reachability assessment, a reproduction trick are exactly the entries a future session needs.
- `docs/token-ledger.md` keeps its row per working session (per `references/estimation-budget.md`) — maintenance time is real cost and calibrates the next quote.
- `docs/issues.md` stays the traceability spine: what arrived, what was done and exactly how, what remains.

## Definition of done (per maintenance change)

- `scripts/keel-doctor --check` passed at session start (or the doctor was created as this maintenance change), and any pending Keel reconciliation was either completed or recorded as pending in PROGRESS.md.
- Reproduced in the playground **by the assistant**, driven (with a synthetic fixture if production-shaped data was needed), and recorded in `docs/issues.md`.
- The fix STARTED from its reproduction test — written before the fix and seen to fail on the bug — and that test stays as the regression test, driven where the bug is user-visible (the only exception is the recorded one: a `docs/decisions.md` entry stating the fix shipped without it and what that costs); the FULL automated suite is green; `scripts/keel-verify` clean; real-environment verification passed on the rebuilt distributable with the flow driven by the assistant, and anything undrivable carrying its tag and its steps.
- Version proposed and explicitly approved by the user before writing; every touchpoint synced; changelog updated oldest → newest.
- If a Phase 8 site exists: the freshness mini-checklist ran for the release.
- State current at the moment of change: PROGRESS.md, decisions, lessons, token ledger, issues.
