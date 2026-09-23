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
- Keel baseline: v6.3.0 — this repository authors the version it is on, so the baseline always equals the version being written.
- Website intent: no
- Client budget: no — the skill is the user's own product, not client work.
- User guide: n/a — `README.md` and `INSTALL.md` serve that role for a skill.
- Docs theme: n/a
- Test-first policy: n/a — this repository ships no executable product; its only code is `tests/lint-release.py`, whose checks are added the moment the promise they verify is written. The two universal rules still apply: a linter bug is fixed from a failing check first, and a check derived from a release rule is never relaxed to make a release pass.
- Sprints: on — plan in `docs/sprints/` since 2026-09-16 (sprint 1 = v6.0.0, sprint 2 = v6.1.0, sprint 3 = v6.3.0). Sessions timed by hand with `date -u` into `docs/.keel/clock.jsonl` (no `scripts/keel-time` in this repo — see deferred items).
- Push test scope: n/a — this repository ships no executable product; its only check, `python3 tests/lint-release.py`, is run whole at every release.
- Durability: **git remote `origin` — https://github.com/joseconti/keel-skill.git** (verified 2026-07-31 with `git remote -v`). The tree is not inside a synced folder; the remote covers the requirement on its own.
- Autonomy: **automatic** — Keel does not ask, and does every merge to `develop` and every push itself (`.claude/settings.local.json` written by Keel, gitignored; see D-003, D-004) / issues: on-request — this repo's forge issues are worked when the user raises them / Issue sweep interval: n/a (the after-sprint duty was not accepted here)
- Branches: integration branch `develop` (created from `main` 2026-07-30 and published) / no open work branch / **v6.2.0 and v6.3.0 await `main`** — both committed and tagged on `develop`; v6.3.0 NOT pushed, on the user's instruction (2026-09-23)
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
- Phase: maintenance — **v6.3.0 committed and tagged on `develop`, NOT pushed** (2026-09-23), sprint 3 closed. New optional active security audit (`keel/references/security-audit.md`): the `references/security/*.md` profiles become hunting modules, an independent verifier refutes each candidate, `findings.json` + `SECURITY-AUDIT.md`, output gitignored while findings are open, card line `Security audit:` derived at Phase 2 §4c and gating Phase 7 when `required` (D-032, D-033, D-034).
- Previous states: v6.2.0 committed and tagged on `develop` 2026-09-19 (Codex launch flags; it carries no D-entry of its own in this log, recorded here rather than back-filled); v6.1.0 released 2026-09-18 (the tool registry as data, D-029–D-031); the history before it is in `keel/CHANGELOG.md` and git.
- Next action: **the user pushes `develop` and the `v6.3.0` tag**, then decides the merge to `main` (PR) and the GitHub releases for v6.2.0 and v6.3.0 (Actions is disabled; `gh release create` by hand). After that, the pending v6.1.0 reconciliation on `new-gymai` still stands.

## Open items
- Unresolved user questions: none
- Open Design Requests: none
- Unverified external steps/assets: none
- Forge issues in progress: none
- **Ready for `main`:** v6.2.0 and v6.3.0 on `develop`. **Unpushed (user's instruction):** the v6.3.0 commit and tag.
- **Reconciliation pending on other projects:** v6.0.0 → v6.3.0, starting with `new-gymai`.

### Deferred items (consciously postponed work)
- **No `scripts/keel-time` and no `plan.json` generator in this repo** — severity: low — review trigger: the next session that finds timing by hand error-prone. The clock is read with `date -u` at every boundary and the events appended to `docs/.keel/clock.jsonl`; `docs/sessions.md` is written from them.
- **The user's `~/.claude/settings.json` carries an unexpanded `env.PATH`** (`$HOME/...:${PATH}` literal), which removes `/usr/bin` and `/bin` and breaks `git`, `ls`, `cut` and `grep` in every session on this machine — worked around all release day with absolute paths and `/usr/bin/env`. Severity: high (machine-wide, every project) — review trigger: the user's go-ahead; it is their personal global config, so Keel proposed the one-line fix and did not apply it. v5.5.0 fixed the RECIPE that would have propagated it.
- **Notification reach is desktop-only unless Remote Control is connected** — severity: low — review trigger: the first time a real absence goes unnoticed, or if the user wants alerts while away from the building. The native channel covers "walked away from the desk"; an SMTP sender or messaging MCP would be the escalation, and is not built.
- **This repo has no `scripts/keel-verify`, `keel-doctor` or `keel-handoff-verify`** — severity: low — review trigger: if the repo ever ships executable content. `tests/lint-release.py` is this project's equivalent gate and is genuinely mechanical; generating the other three would be ceremony over a Markdown package.

Last updated: 2026-09-23 — maintenance, v6.3.0 (active security audit) committed and tagged on develop, not pushed
