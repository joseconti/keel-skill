# Project State, Resume & Context Discipline (cross-cutting)

Load this reference at two moments, and only these: (a) the moment Phase 1 begins on a new project, (b) the moment a session resumes an in-progress Keel project. It defines the living state system that makes a project survive across many chats, many models, and long gaps — without re-reading the codebase, re-litigating decisions, or losing the exact working position.

The problem this solves: a fresh chat has no memory. Without a state system it reconstructs context by scanning code and re-asking the user, which wastes tokens, breaks prompt caching, and — worse — re-decides things differently each time. With this system, every session starts from the same small set of files, in the same order, and continues instead of restarting.

## The state files (created in Phase 1, live until release)

Created the moment Phase 1 starts producing artifacts — NOT in Phase 5. Before creating them, confirm with the user where the project lives (the project directory / repository); create it if it doesn't exist yet. Never write state into an arbitrary working directory.

| File | Purpose | Created | Updated |
|------|---------|---------|---------|
| `docs/PROGRESS.md` | The single living state: project card, phase status, exact current position, open items | Phase 1, first action | Continuously — after every phase step, slice, or test point |
| `docs/decisions.md` | Append-only log of decisions that shape the project (so no session re-litigates them) | Phase 1, first action | Whenever a decision is made |
| `docs/lessons-learned.md` | Append-only problem → solution log (so no session repeats a mistake) | Phase 1, first action | Whenever something failed and a fix was found |
| `docs/design/design-requests/DR-NNN.md` | One file per Design Request, numbered, with status | Phase 4, when the first gap appears | When a DR is sent / resolved |
| `docs/api/INDEX.md` | One line per public surface — the cheap lookup layer for the reuse rule | Phase 5, first slice | Same slice that adds/changes a surface |
| `docs/issues.md` | Living log of forge issues: inventory + one entry per issue worked (diagnosis, resolution, commits, what remains) | First time forge issues are triaged or worked (any phase) | The moment an issue is triaged, worked, or closed |
| `docs/token-ledger.md` | Actual token usage: one row per working session; final reconciliation (cost + deviation vs estimate) at release | With Estimate v1 (Phase 1 close), per `references/estimation-budget.md` | At the end of every working session; verified at phase/sprint closes |
| `CLAUDE.md` (repo root) | The portability lock: binds ANY assistant/environment opening the repo to the Keel workflow | Phase 1, first action (or adoption) | When Keel's protocol block changes (between its delimiters only) |
| `.claude/skills/keel/` | Embedded copy of the skill (optional, recommended) — makes the repo self-sufficient | Phase 1, first action (with user approval) | Version-synced from the installed skill, one direction |

Everything else in `docs/` (specs, flows, design handoff, BUILD-SPEC, sprint files) is a **stable artifact**: written once at its phase, amended deliberately, never casually rewritten. The state files above are the only ones that change constantly — keeping them small and the artifacts stable is what makes context cheap and cache-friendly.

## `docs/PROGRESS.md` — template (ALWAYS this structure)

Keep it to roughly one page. Detail lives in the linked files, never accumulated here.

```
# PROGRESS — [Project name]

> Living state. Read this FIRST in every session. Keep current and compact.

## Project card
- Name / one-line purpose: ...
- Project type: [primary] / [secondary or none]
- Stack & target platform(s): [from docs/03-technical-plan.md once it exists]
- License: [e.g. GPL-3.0-or-later]
- Docs language: [the language all docs/ artifacts are written in — English by default (token economy)]
- Security profile: references/security/[file]
- Accessibility: [targeted level] (references/accessibility.md)
- i18n: [multi — base X, locales Y, mechanism Z / single — language X]
- Installed base: [fresh v1 / upgrades vX.Y in production with data]
- Design system: [existing — source/location / founding — canonical, will live at X / one-off / n/a no UI]
- Keel portability: [lock only / lock + embedded vX.Y.Z]
- Website intent: [yes — own domain|subdomain / no]

## Phase status
| Phase | Status | Key artifacts |
|-------|--------|---------------|
| 1 Discovery | [pending/in progress/done] | docs/00-competitive-landscape.md, docs/01-discovery.md, docs/estimate.md (v1 preliminary) |
| 2 Functional spec | ... | docs/02-functional-spec.md, docs/03-technical-plan.md, docs/flows/, docs/estimate.md (firm), docs/budget.md |
| 3 Design handoff | ... | docs/design/DESIGN-BRIEF.md |
| 4 Faithful build | ... | docs/BUILD-SPEC.md |
| 5 Development | ... | docs/sprints/, docs/05-test-points.md |
| 6 Documentation | ... | docs/architecture.md, docs/api/, docs/usage/, docs/reference/ |
| 7 Release | ... | docs/07-release.md |
| 8 Website | [n/a if no intent] | docs/site/ or site repo |

## Current position
- Phase: [N — name]  Step/sprint: [exact step or sprint + slice]
- Next action: [the single next concrete thing to do]

## Open items
- Unresolved user questions: [list or "none"]
- Open Design Requests: [DR-001 — sent/resolved | "none"]
- Unverified external steps/assets: [from Phase 4 loops | "none"]
- Forge issues in progress: [see docs/issues.md | "none"]

Last updated: [date — phase/step]
```

Update rules: mark a phase `done` only when its definition of done passed (reported ✓/✗ to the user). "Next action" must always be executable by a fresh session with no other context. Never let PROGRESS.md drift from reality — a stale state file is worse than none.

## `docs/decisions.md` — template

Append-only; never edit or delete past entries (if a decision is reversed, append a new entry that supersedes it and says why).

```
# Decisions — [Project name]

> Append-only. A session NEVER re-opens a decision recorded here on its own initiative;
> only the user reverses a decision (append the reversal as a new entry).

## D-001 — [short title]
- Date / phase: ...
- Decision: ...
- Why: ...
- Alternatives rejected (and why): ...
- Supersedes: [D-0XX or none]
```

Record here: project type, stack choice, license, i18n and accessibility levels, scope cuts, architecture choices, anything where a future session could plausibly "re-decide" differently. Phase 6's `architecture.md` consolidates from this log instead of reconstructing memory.

## `docs/lessons-learned.md` — template

Append-only; never trim.

```
# Lessons Learned — [Project name]

## L-001 — [short title]
- Problem: [what went wrong]
- Where: [phase/slice/file]
- What failed: [the attempt that didn't work]
- Working solution: [what fixed it]
- Rule for next time: [one line a future session can apply directly]
```

If a lesson came from a code bug, the fix gets a regression test in the same slice (Phase 5 rule) — the lesson entry links to it.

## Design Request register (Phase 4)

Every Design Request is numbered and saved before it is given to the user: `docs/design/design-requests/DR-001.md`, `DR-002.md`, ... (the filled design-request-template, plus a `Status: sent / resolved [date]` line at the top). PROGRESS.md "Open items" lists every DR and its status. The Phase 4 faithfulness checklist item "zero unresolved Design Requests" is verified against this register, not against memory — a fresh session must be able to see that DR-002 is still open.

## `docs/issues.md` — the forge issue log (any phase)

Whenever the project's forge issues are accessed — GitHub, GitLab, Gitea, Bitbucket, or any other Git forge — the work is tracked in `docs/issues.md`. The purpose is total traceability: at any moment, and from any future session, it must be possible to see everything there is, everything that was done and exactly HOW, and everything still pending — so when a problem surfaces later, what was changed and why is on record, never reconstructed from memory.

Created the first time issues are triaged or worked (any phase — development, post-release maintenance, adoption). Updated **at the moment** an issue is triaged, worked, or closed — like every state file, never "later".

```
# Issues — [Project name]

> Living log of forge issues ([forge + repo URL]). Inventory first, one entry per issue worked.
> Updated the moment an issue is triaged, worked, or closed.

## Inventory
| # | Title | Type | Priority | Status | Entry |
|---|-------|------|----------|--------|-------|
| 123 | Checkout fails on empty cart | bug | high | resolved | E-001 |
| 124 | Support WebP product images | feature | low | open | — |

## Entries (one per issue worked)

### E-001 — #123 Checkout fails on empty cart
- Link: [forge issue URL]   Status: resolved [date] / in progress / won't fix (reason)
- Diagnosis: [what was actually wrong — root cause, not the symptom]
- Resolution: [what was done and why — the approach taken]
- Changes: [commits/PR, files touched, the version that ships the fix]
- Verification: [regression test added (Phase 5 rule), test point, playground check]
- Lesson: [L-NNN in docs/lessons-learned.md if one was recorded | none]
- Pending: [anything left on this issue | none]
```

Rules:

- **Inventory covers what is known; entries cover what was worked.** On first contact with the forge, fill the inventory with at least the open issues (closed history is optional). Every issue actually worked gets its E-entry — an issue closed without its entry is a state defect.
- **Status values:** open / triaged / in progress / resolved / won't fix (reason recorded). The inventory row and its entry must agree.
- **An entry must answer "what did we do here?" months later:** diagnosis, approach, commits, verification — enough to reopen the work cold if the problem resurfaces. If the fix produced a lesson, record it in `docs/lessons-learned.md` and link it; the regression test lives with the fix (Phase 5 rule).
- **Both directions:** issues can drive work (a bug report becomes a slice) or record it (work done reveals something to file upstream). Either way the log stays current.
- **Growth:** if the file grows large, old **resolved** entries may move to `docs/old/issues-archive.md` (move, never delete); the inventory always stays complete, with archived entries still referenced from their rows.

## `docs/api/INDEX.md` — the cheap reuse lookup (Phase 5)

The reuse rule ("search the existing internal API before writing new code") must not require loading every file in `docs/api/` and `docs/reference/`. The index is the first — and usually only — thing consulted:

```
# API Index — [Project name]
> One line per public surface. Grep here FIRST; open the full doc only on a hit.

| Surface | Kind | Code file | Doc | Purpose (one line) |
|---------|------|-----------|-----|--------------------|
| mcm_get_licenses() | function | includes/api.php | docs/api/licenses.md | List licenses for a user |
| mcm/license-created | action | includes/api.php | docs/reference/hooks-and-extension-points.md | Fires after license creation |
```

Updated in the same slice that adds or changes a surface — an INDEX row without its doc, or a doc without its row, is a slice defect.

## Sprint files (Phase 5) — template

```
# Sprint [N] — [short goal]
- Scope: [slices/tasks in this sprint]
- Acceptance: [what "done" means for this sprint]
- Status: [planned / in progress / closed]
- Slices:
  | Slice | Status | Test point result | Notes |
- Close-out: [filled at close: what shipped, what moved to next sprint]
```

## Continuation prompt (ANY phase, not just sprint closes)

A chat can fill up in any phase — a long competitive scan, a long external-setup loop — not only during development. Whenever the session is ending (or the user asks to continue elsewhere), produce this ready-to-paste prompt. Phase 5's sprint close-out uses the same mechanism with sprint specifics added.

```
Load the `keel` skill and resume [PROJECT NAME] at Phase [N] ([phase name]), [step/sprint X].
1. Read docs/PROGRESS.md — the project card, phase status, current position, open items.
2. Read docs/decisions.md and docs/lessons-learned.md — do not re-litigate decisions; do not repeat recorded mistakes.
3. Read the current phase's reference (references/phase-[N]-*.md) and the inputs PROGRESS.md names for the current position.
4. Continue EXACTLY from "Next action". Do not restart the phase, do not reinterpret or "improve" earlier decisions, do not redesign. Gaps go to the user or to a Design Request, per the skill.
```

The prompt must be self-sufficient: assume the new session knows nothing except what these files contain. Producing it does not force a chat switch — if the current chat still has capacity, continue in it; the prompt is insurance. Like everything Keel creates, the continuation prompt is written in English (SKILL.md "Token economy"), regardless of the conversation language.

## Context & cache discipline (how every session works)

These rules exist so sessions are cheap, deterministic, and cache-friendly. Follow them literally.

1. **Fixed session-start reading order.** On resume, read in this exact order and nothing more: `docs/PROGRESS.md` → `docs/decisions.md` → `docs/lessons-learned.md` → the current phase's reference file → only the inputs PROGRESS.md names for the current position. The same order every session keeps context predictable and maximizes prompt-cache reuse.
2. **Read each static reference once per session.** Phase references and templates do not change mid-session — never re-read a file already loaded in this conversation; rely on the copy in context.
3. **Orient by state, not by scanning code.** The project's shape lives in `docs/03-technical-plan.md` (code map, conventions), `docs/architecture.md` (once it exists), and `docs/api/INDEX.md`. A session that needs to know "where is X / does Y exist" consults these first, then opens the one specific file it needs. Tree-wide code exploration is a signal that the state files are incomplete — fix the state files, don't normalize the scanning.
4. **Surgical code reads.** When code must be read, read the specific file/function the state points to — not whole directories "for context".
5. **Small living state, stable artifacts.** Only PROGRESS.md, decisions.md, lessons-learned.md, the DR register, INDEX.md, sprint files, and 05-test-points.md change routinely. Specs, flows, design handoff, and BUILD-SPEC are amended only deliberately (a recorded decision or Design Request), because every rewrite invalidates what other sessions and caches rely on.
6. **Reference paths, don't duplicate content.** When producing or discussing a large artifact, write it to its file and refer to the path. Do not paste large file bodies into the conversation when a path reference serves.
7. **Keep PROGRESS.md ~one page.** History goes to sprint files and `docs/old/`; PROGRESS.md holds only the present.
8. **Update state at the moment of change.** After each phase step, decision, slice, test point, or DR: update the relevant state file immediately. State updated "later" is state lost when the chat dies.

## Portability across environments — the CLAUDE.md lock and the embedded skill

A Keel project moves between environments and assistants: the Claude app, Cowork, Claude Code in VS Code / terminal, sometimes other AIs entirely. The state files make the project resumable; this section makes the WORKFLOW itself travel with the repo, so whatever opens the project is bound to Keel — even if the Keel skill is not installed there.

Two mechanisms, created at Phase 1 step 0a (and during adoption step 2):

### 1. The `CLAUDE.md` lock (mandatory)

The project root carries a `CLAUDE.md` with the Keel block below. Claude Code, Cowork and the Claude app read the project's `CLAUDE.md` automatically — that is what makes this the lock: it is read before anything else, in every environment, by every session, without depending on any skill being installed. If `CLAUDE.md` already exists, insert the block between its delimiters without touching the rest; the delimiters make it safely updatable later.

```
<!-- KEEL:BEGIN — do not remove: binds every AI/session in this repo to the Keel workflow -->
# Keel protocol (mandatory for ANY assistant working in this repository)

This project is governed by the Keel workflow. Before reading code or changing ANYTHING:

1. Read `docs/PROGRESS.md` (project card, current position, next action), then
   `docs/decisions.md` (decisions are NEVER re-opened on your initiative), then
   `docs/lessons-learned.md` (recorded mistakes are never repeated).
2. If the `keel` skill is installed in this environment, it governs. If it is NOT,
   read the embedded copy at `.claude/skills/keel/SKILL.md` plus the phase reference
   it names for the current phase, and follow it literally.
3. Follow the recorded specs and design exactly: no reinterpretation, no silent
   deviation, no "improving" recorded decisions. Anything undefined → ask the user.
   Design gaps → Design Request (Keel Phase 4).
4. Update `docs/PROGRESS.md` and `docs/decisions.md` at the moment of every change.
   Commit at passed test points. If ending mid-work, produce the continuation prompt
   from `.claude/skills/keel/references/project-state.md`.
5. Work with execution discipline, whatever model or environment is running:
   - Batch independent tool calls in ONE parallel block; never run sequentially what
     does not depend on a previous result.
   - Delegate broad searches/scans to a subagent when the environment provides them;
     bring back conclusions, never file dumps — the main context stays clean.
   - Do not narrate between tool calls ("now I will…"); accumulate findings and
     report once, at the end of the work block.
   - Locate before reading: search/grep first, then read only the relevant fragment.
     Never read whole files or directories "for context".
   - Edit surgically (exact-match edits on the changed lines); never rewrite a whole
     file to change one part.
   - Batch clarifying questions at the START of a work block; close every work block
     with an explicit verification step (diff, test, or re-read) before calling it
     done.

If neither the skill nor the embedded copy is available: STOP and tell the user to
install Keel (or restore `.claude/skills/keel/`) before continuing.
<!-- KEEL:END -->
```

If the user also works with non-Claude assistants, mirror the same block in `AGENTS.md` (the multi-agent convention file) so those tools are bound too.

### 2. The embedded skill copy (recommended — ask the user once)

Copy the installed skill into the repo at `.claude/skills/keel/` (SKILL.md + references/, verbatim). Consequences: Claude Code loads it automatically as a project-level skill; any other environment can read it as plain files via the lock's step 2; the repo is self-sufficient — a collaborator or a future session needs nothing pre-installed. Ask the user once at creation (it adds ~150 KB of markdown to the repo); record the choice in the project card.

Rules for the embedded copy:

- **Copy the WHOLE skill — every file, verified — never a partial copy.** Copy from the installed skill's own directory, file for file: `SKILL.md` AND the complete `references/` tree (every `phase-*.md`, every template, `project-state.md`, `adoption.md`, `accessibility.md`, and the entire `references/security/` folder), plus `CHANGELOG.md`, `LICENSE`, and `NOTICE`. A partial copy is the single most common failure here and it silently breaks the workflow in the target environment — a missing phase reference makes that phase unrunnable, so the skill never really reaches the other tool. This is therefore a **verified** operation, not fire-and-forget:
  1. **Copy everything at once.** Prefer a recursive copy of the entire `keel/` folder into `.claude/skills/keel/` (e.g. `cp -R`), not a hand-picked file list — hand-picking is how files get left behind.
  2. **Verify against the source manifest.** After copying, list what actually landed in `.claude/skills/keel/` and compare it file-for-file against the source directory: same file set, nothing missing, nothing zero-bytes. `SKILL.md` must sit at `.claude/skills/keel/SKILL.md` (not nested one level deeper), and every reference the source has must be present.
  3. **If anything is missing or wrong, retry the copy, then verify again.**
  4. **If it still fails after the retry, STOP and tell the user plainly** — name exactly which files did not arrive and why the copy could not complete from this environment — and ask them to move the `keel/` folder into `.claude/skills/keel/` themselves. Never leave a half-copied skill in place as if it worked: an embedded skill that reaches other tools with files missing is a defect, not a partial success. Record the outcome (complete / user-completed) in the project card.
  If this environment cannot access the installed skill's files at all, do not reconstruct reference files from memory — tell the user to copy the `keel/` folder from the release into `.claude/skills/keel/` manually, then verify as above once they have.
- **Sync by version, one direction.** The embedded copy's `SKILL.md` frontmatter carries its version. If the installed skill is newer than the embedded copy, update the embedded copy (tell the user); if the embedded copy is newer than what's installed, tell the user to update their installed skill. Never hand-edit the embedded copy. A version sync is also a full-tree copy — apply the same verify → retry → tell-user protocol above so an update can't silently drop a file either.
- **It never ships.** `.claude/`, `CLAUDE.md` and `AGENTS.md` are repo-only: Phase 7 marks them `export-ignore` so they stay out of the distributable package.

Project card line: `Keel portability: [lock only / lock + embedded vX.Y.Z]`.

## Archiving (`docs/old/`) — what moves, what never moves

At each sprint close (Phase 5) move to `docs/old/sprint-<N>/` only documents that are finished AND no longer consulted: closed sprint files, resolved one-off scratch documents, superseded drafts. Move — never delete.

These NEVER move while the project is alive: `PROGRESS.md`, `decisions.md`, `lessons-learned.md`, `issues.md` (old resolved entries may move to `docs/old/issues-archive.md`, the file itself never), `estimate.md`, `budget.md`, `00-competitive-landscape.md`, `01-discovery.md`, `02-functional-spec.md`, `03-technical-plan.md`, `05-test-points.md`, `BUILD-SPEC.md`, `flows/`, `design/` (brief, handoff, DR register), `api/`, `reference/`, the current sprint file.

## Definition of done (this reference)

- `docs/PROGRESS.md`, `docs/decisions.md`, `docs/lessons-learned.md` exist from Phase 1 and match the templates.
- PROGRESS.md reflects reality at all times: correct phase status, executable "Next action", complete open items.
- Every decision that shapes the project has a D-entry; every solved failure has an L-entry.
- Every Design Request exists as a numbered file with current status.
- If forge issues were ever accessed: `docs/issues.md` exists, its inventory reflects the forge, and every worked issue has its entry (diagnosis, resolution, changes, verification, pending).
- From Phase 5: `docs/api/INDEX.md` exists and matches the docs; sprint files follow the template.
- Any session ending mid-work produced a continuation prompt.
