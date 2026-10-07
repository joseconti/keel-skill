# PROGRESS — Keel (the skill itself)

> Living state. Read this FIRST in every session. Keep current and compact.

## Project card
- Name / one-line purpose: **Keel** — the project-lifecycle skill (idea → release) that this repository authors and distributes.
- Project type: skill / workflow package (Markdown instruction set + deterministic standard-library helper and release linter). No UI or hosted runtime.
- Stack & target platform(s): Markdown, consumed by any AI coding assistant; Python 3 standard library for `keel/scripts/keel_parallel.py`, its tests and `tests/lint-release.py`; GitHub for distribution and releases.
- License: GPL-3.0-or-later
- Docs language: English (token economy). The conversation with the user is Spanish.
- Security profile: library/component — the packaged helper validates local plans/worktrees and launches only an adapter-provided argv under an explicit cwd; it has no network or model-service code. The confidential-data rule governs every commit.
- Accessibility: n/a — no user interface. The Markdown is kept readable and structured.
- i18n: single — English. The skill's *output* language contract is a separate matter, defined inside SKILL.md.
- Installed base: yes — released versions are installed by users and embedded in their projects. Every change must consider projects on older baselines (that is what `MANIFEST.md` Table 3 is for).
- Design system: n/a no UI
- Keel portability: lock only — this repo is the SOURCE of the skill; it does not embed a copy of itself.
- Assistant config: none (tools: claude) — no `.claude/` package generated for this repo.
- Models: runtime-selected — no backend is assumed from a product name; real writing backends remain unverified in this repository.
- Keel baseline: v7.1.0 — this repository authors the version it is on, so the baseline always equals the version being written.
- Website intent: no
- Client budget: no — the skill is the user's own product, not client work.
- User guide: n/a — `README.md` and `INSTALL.md` serve that role for a skill.
- Docs theme: n/a
- Test-first policy: n/a — this repository ships no executable product; its only code is `tests/lint-release.py`, whose checks are added the moment the promise they verify is written. The two universal rules still apply: a linter bug is fixed from a failing check first, and a check derived from a release rule is never relaxed to make a release pass.
- Sprints: on — plan in `docs/sprints/` since 2026-09-16 (sprint 6 = v7.0.0). Sessions timed by hand with `date -u` into `docs/.keel/clock.jsonl` (no `scripts/keel-time` in this repo — see deferred items).
- Parallel development: auto; max_workers: 2 — capability-gated; this bootstrap ran serially because no real isolated writing backend was verified (D-037).
- Push test scope: affected — scheduler changes run `python3 -B -m unittest discover -s tests -p 'test_parallel*.py' -v`; every release also runs `python3 tests/lint-release.py`.
- Durability: **git remote `origin` — https://github.com/joseconti/keel-skill.git** (verified 2026-07-31 with `git remote -v`). The tree is not inside a synced folder; the remote covers the requirement on its own.
- Autonomy: **automatic** — Keel does not ask, and does every merge to `develop` and every push itself (`.claude/settings.local.json` written by Keel, gitignored; see D-003, D-004) / issues: on-request — this repo's forge issues are worked when the user raises them / Issue sweep interval: n/a (the after-sprint duty was not accepted here)
- Branches: integration branch `develop` / no open work branch / v7.1.0 awaits the user's merge to `main`; tagging and publication are not yet authorized.
- Notify: **native Claude Code notification** — desktop always; phone only while Remote Control is connected. No address needed. The Gmail connector is compose-only (draft, no send) and is not a channel. Re-probe each session per `references/notifications.md`.
- Chaining: off — pending re-ask under the v5.10.0 recommendation (this card is `Autonomy: automatic`)

## Phase status

This repository was adopted into its own discipline late (state files created 2026-07-30, at v5.5.0). It is not a greenfield Keel project and does not run Phases 1–4: the skill exists, is released, and has users. Its working mode is **maintenance** — each version is a change set with a changelog entry, a manifest delta, and the release linter as its gate.

| Phase | Status | Key artifacts |
|-------|--------|---------------|
| 1 Discovery | n/a — predates its own state files | `README.md` (purpose and scope) |
| 2 Functional spec | n/a — the spec is the skill | `keel/SKILL.md`, `keel/MANIFEST.md` |
| 3 Design handoff | n/a — no UI | — |
| 4 Faithful build | n/a — no UI | — |
| 5 Development | ongoing (per version) | `keel/references/`, `tests/lint-release.py` |
| 6 Documentation | done | `README.md`, `INSTALL.md`, `keel/CHANGELOG.md`, `keel/MANIFEST.md` |
| 7 Release | recurring | git tag `vX.Y.Z` + GitHub release; gate = `python3 tests/lint-release.py` |
| 8 Website | n/a — website intent: no | — |

## Current position
- Phase: maintenance — **v7.1.0 adds static-analysis evidence classification; v7.0.0 backend acceptance remains incomplete**, sprint 6 / S-011 (D-037). The six reproduced scheduler defects are fixed and covered by regression tests; the static-analysis rule prevents launcher failures from being reported as code results. See `docs/parallel-development-review.md` for the remaining backend acceptance boundary.
- Previous states: v6.6.0 is the Git baseline this change started from; older release history is in `keel/CHANGELOG.md` and Git.
- Next action: review the v7.1.0 candidate committed locally on `develop`. Before declaring unattended model writing supported, complete the isolated backend and generated-hook acceptance described in `docs/parallel-development-review.md`. Push, merge to `main`, tag and publication remain pending.

## Open items
- Unresolved user questions: none
- Open Design Requests: none
- Unverified external steps/assets: real writing-backend smoke run in a disposable repository (native or CLI); deterministic scheduling is verified separately and does not prove this.
- Forge issues in progress: none
- **Local release candidate:** v7.1.0 static-analysis evidence rule and local packaging checks pass; committed on `develop` at the user's request. This is not a completed unattended-backend acceptance.
- **Reconciliation pending on other projects:** apply the v7.0.0 Table 3 delta only when each project chooses parallel development; apply v7.1.0's evidence rule at the next static-analysis test point.

### Deferred items (consciously postponed work)
- **No `scripts/keel-time` and no `plan.json` generator in this repo** — severity: low — review trigger: the next session that finds timing by hand error-prone. The clock is read with `date -u` at every boundary and the events appended to `docs/.keel/clock.jsonl`; `docs/sessions.md` is written from them.
- **The user's `~/.claude/settings.json` carries an unexpanded `env.PATH`** (`$HOME/...:${PATH}` literal), which removes `/usr/bin` and `/bin` and breaks `git`, `ls`, `cut` and `grep` in every session on this machine — worked around all release day with absolute paths and `/usr/bin/env`. Severity: high (machine-wide, every project) — review trigger: the user's go-ahead; it is their personal global config, so Keel proposed the one-line fix and did not apply it. v5.5.0 fixed the RECIPE that would have propagated it.
- **Notification reach is desktop-only unless Remote Control is connected** — severity: low — review trigger: the first time a real absence goes unnoticed, or if the user wants alerts while away from the building. The native channel covers "walked away from the desk"; an SMTP sender or messaging MCP would be the escalation, and is not built.
- **This repo has no project-generated `scripts/keel-verify`, `keel-doctor` or `keel-handoff-verify`** — severity: low — review trigger: if this source repository gains a deployed runtime. `tests/lint-release.py` plus the scheduler suite are its mechanical gates; the packaged `keel/scripts/keel_parallel.py` is a skill resource, not this repo's generated project helper.

Last updated: 2026-10-07 — v7.1.0 candidate verified and committed locally on develop; package and evidence in docs/release-v7.1.0.md; backend acceptance remains incomplete; publication pending
