# PROGRESS — Keel (the skill itself)

> Living state. Read this FIRST in every session. Keep current and compact.

## Project card
- Name / one-line purpose: **Keel** — the project-lifecycle skill (idea → release) that this repository authors and distributes.
- Project type: skill / documentation package (Markdown instruction set + release linter). Not runnable software; no UI, no runtime.
- Stack & target platform(s): Markdown, consumed by any AI coding assistant; Python 3 for `tests/lint-release.py`; GitHub for distribution and releases.
- License: GPL-3.0-or-later
- Docs language: English (token economy). The conversation with the user is Spanish.
- Security profile: n/a — the skill ships no executable product. The confidential-data rule still governs every commit.
- Accessibility: n/a — no user interface. The Markdown is kept readable and structured.
- i18n: single — English. The skill's *output* language contract is a separate matter, defined inside SKILL.md.
- Installed base: yes — released versions are installed by users and embedded in their projects. Every change must consider projects on older baselines (that is what `MANIFEST.md` Table 3 is for).
- Design system: n/a no UI
- Keel portability: lock only — this repo is the SOURCE of the skill; it does not embed a copy of itself.
- Assistant config: none (tools: claude) — no `.claude/` package generated for this repo.
- Models: n/a no agents
- Keel baseline: v5.11.0 — this repository authors the version it is on, so the baseline always equals the version being written.
- Website intent: no
- Client budget: no — the skill is the user's own product, not client work.
- User guide: n/a — `README.md` and `INSTALL.md` serve that role for a skill.
- Docs theme: n/a
- Test-first policy: n/a — this repository ships no executable product; its only code is `tests/lint-release.py`, whose checks are added the moment the promise they verify is written. The two universal rules still apply: a linter bug is fixed from a failing check first, and a check derived from a release rule is never relaxed to make a release pass.
- Durability: **git remote `origin` — https://github.com/joseconti/keel-skill.git** (verified 2026-07-31 with `git remote -v`). The tree is not inside a synced folder; the remote covers the requirement on its own.
- Autonomy: **automatic** — Keel does not ask, and does every merge to `develop` and every push itself (`.claude/settings.local.json` written by Keel, gitignored; see D-003, D-004) / issues: on-request — this repo's forge issues are worked when the user raises them / Issue sweep interval: n/a (the after-sprint duty was not accepted here)
- Branches: integration branch `develop` (created from `main` 2026-07-30 and published) / no open work branch / nothing awaiting `main` — v5.10.2 merged and tagged on the user's explicit instruction
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
- Phase: maintenance — **v5.10.3 RELEASED** (2026-08-04): the `scripts/keel-continue` contract closes four gaps found on a real macOS `start` launch (three quoting/parser bugs that hid behind each other, plus a canonical `env.PATH` template that made the script's own live PATH re-check report `claude` as absent on a machine actively running it) — reported against this skill from a downstream project (`docs/keel-continue-launch-postmortem.md` / `docs/keel-skill-bug-report-keel-continue.md` in WHMWP). v5.10.2, the day before: whether to chain is decided by the script, never the session.
- Step/sprint: v5.10.3 change set — new contract points 6a (script-file-by-path, never an interpolated string; the BSD `mktemp` suffix trap) and 6b (never pass the hand-off's raw `---`-prefixed content as `claude`'s CLI argument) in `references/project-state.md`, plus point 8 stating the exit-code trap explicitly; `references/keel-maintenance.md`'s `env.PATH` template now always includes the user's own per-user installer directory (`~/.local/bin`, literal absolute path). `python3 tests/lint-release.py` passed. Merged to `main` (PR #4, by the user — `protect-main.sh` reserves that step) and tagged `v5.10.3`; GitHub release published by the `release.yml` pipeline (https://github.com/joseconti/keel-skill/releases/tag/v5.10.3).
- Next action: put the chaining question to the user for THIS repository — its card still says `Autonomy: automatic` and `Chaining: off`, unchanged since v5.10.0's reconciliation asked for a re-ask that has not happened yet. Answering it here on the user's behalf is the one thing the change forbids.

## Open items
- Unresolved user questions: none
- Open Design Requests: none
- Unverified external steps/assets: none
- Forge issues in progress: none
- **Ready for `main`:** nothing. v5.10.3 shipped; `main` and `develop` are level at the release commit.

### Deferred items (consciously postponed work)
- **The user's `~/.claude/settings.json` carries an unexpanded `env.PATH`** (`$HOME/...:${PATH}` literal), which removes `/usr/bin` and `/bin` and breaks `git`, `ls`, `cut` and `grep` in every session on this machine — worked around all release day with absolute paths and `/usr/bin/env`. Severity: high (machine-wide, every project) — review trigger: the user's go-ahead; it is their personal global config, so Keel proposed the one-line fix and did not apply it. v5.5.0 fixed the RECIPE that would have propagated it.
- **Notification reach is desktop-only unless Remote Control is connected** — severity: low — review trigger: the first time a real absence goes unnoticed, or if the user wants alerts while away from the building. The native channel covers "walked away from the desk"; an SMTP sender or messaging MCP would be the escalation, and is not built.
- **This repo has no `scripts/keel-verify`, `keel-doctor` or `keel-handoff-verify`** — severity: low — review trigger: if the repo ever ships executable content. `tests/lint-release.py` is this project's equivalent gate and is genuinely mechanical; generating the other three would be ceremony over a Markdown package.

Last updated: 2026-08-04 — maintenance, v5.10.3 released
