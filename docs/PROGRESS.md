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
- Phase: maintenance — **v5.12.0 BUILT, NOT YET RELEASED** (2026-08-04): art direction absorbed into Phase 8 so websites stop coming out looking like the previous one (D-025). New `references/phase-8-art-direction.md` (Design Read, four dials including `EVIDENCE_RATIO`, the divergence round, signature elements, a literal blacklist, the self-critique pass), a machine-local cross-project anti-repetition ledger at `~/.keel/art-ledger.md` constraining against the last three sites, a new conditional handoff artifact `SPEC/art-direction.md`, and anti-pattern 24 with self-audit question 24. Mechanisms adapted from `taste-skill` (Leonxlnx, MIT) and attributed; that skill is deliberately NOT a dependency — its React/Tailwind/npm architecture contradicts Phase 8's vanilla rule, and a recommendation is a weaker gate than a phase with a definition of done.
- Step/sprint: v5.12.0 change set complete — `keel/references/phase-8-art-direction.md` (new); `phase-8-website.md`, `phase-8-design-direction.md` (§2 no longer asks for tone in adjectives), `design-brief-template.md` (§2b), `handoff-contract.md` (two website `SPEC/` files), `phase-8-launch-checklist.md` (live verification + em-dash grep + ledger written), `anti-patterns.md` (trap 24, self-audit 24), `SKILL.md`, `MANIFEST.md` (Table 1 rows, Table 2, Table 3 delta), `CHANGELOG.md`, `README.md`, and the canonical lock stamp in `project-state.md`. `python3 tests/lint-release.py` passed: **All checks passed. Releasable.** Not committed, not tagged, not merged — the user does those.
- Next action: the user reviews the v5.12.0 change set, then commits on `develop`, merges to `main` and tags `v5.12.0`. Two items carried and still open, neither touched by this release: (a) put the chaining question to this repository (its card still says `Autonomy: automatic` / `Chaining: off` from v5.10.0's reconciliation, and answering it on the user's behalf is the one thing that change forbids); (b) **`docs/PROGRESS.md` was never updated for v5.11.0** — it still read "v5.10.3 RELEASED" while `CHANGELOG.md` carried a shipped 5.11.0. Recorded here rather than silently overwritten; the v5.11.0 release state should be reconstructed from its changelog entry and git history when convenient.

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

Last updated: 2026-08-04 — maintenance, v5.12.0 built and lint-clean, awaiting the user's commit/tag/merge
