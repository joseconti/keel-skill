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
- Keel baseline: v5.5.0 — this repository authors the version it is on, so the baseline always equals the version being written.
- Website intent: no
- Client budget: no — the skill is the user's own product, not client work.
- User guide: n/a — `README.md` and `INSTALL.md` serve that role for a skill.
- Docs theme: n/a
- Autonomy: permission mode: auto (`.claude/settings.local.json`, written by Keel, gitignored) / push: unattended (Keel pushes; see D-003) / issues: on-request — the repo's forge issues are worked when the user raises them
- Branches: integration branch `develop` (created from `main` 2026-07-30 and published) / work branch `feature/v5.5.0-autonomy-and-notifications` (merged) / **awaiting the user:** v5.5.0 on `develop`, to be merged to `main` and tagged by them
- Notify: none — no delivering channel probed in this environment; the Gmail connector is compose-only (draft, no send). Re-probe each session per `references/notifications.md`.
- Chaining: off

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
- Phase: maintenance — **v5.5.0** authored and integrated on `develop`; unreleased (not merged to `main`, not tagged)
- Step/sprint: v5.5.0 change set — committed on `feature/v5.5.0-autonomy-and-notifications`, merged into `develop` and pushed (`bf823c0`) — session setup batch, permission mode, out-of-band notification, three-beat forge-issue lifecycle, `develop`-based git flow, uninterrupted advance
- Next action: **the user's call** — v5.5.0 is on `develop` and pushed; merging `develop` into `main` and tagging `v5.5.0` are their acts (D-002). Keel does not perform them.

## Open items
- Unresolved user questions: none
- Open Design Requests: none
- Unverified external steps/assets: none
- Forge issues in progress: none
- **Ready for `main`:** v5.5.0 is on `develop` and pushed, awaiting the user's decision to merge to `main` and tag. Keel does not do this on its own initiative.

### Deferred items (consciously postponed work)
- **No delivering notification channel exists on this machine** — severity: medium — review trigger: when the user wires an SMTP sender or a messaging MCP. Until then `references/notifications.md`'s protocol is correct but has nothing to deliver through, and Keel says so instead of pretending.
- **This repo has no `scripts/keel-verify`, `keel-doctor` or `keel-handoff-verify`** — severity: low — review trigger: if the repo ever ships executable content. `tests/lint-release.py` is this project's equivalent gate and is genuinely mechanical; generating the other three would be ceremony over a Markdown package.
- **Untracked working notes at the repo root** (`INFORME-v5.4.0.md`, `PROMPT-v5.4.0-*.md`) — severity: low — review trigger: next release hygiene pass. Decide per file: commit as project record, move under `docs/old/`, or delete.

Last updated: 2026-07-30 — maintenance, v5.5.0 authoring
