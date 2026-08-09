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
| `docs/api/INDEX.md` | One line per public surface — the cheap lookup layer for the reuse rule | Phase 5, first slice | Same slice that adds, changes, or removes a surface |
| `docs/issues.md` | Living log of forge issues: inventory + one entry per issue worked (diagnosis, resolution, commits, what remains) | First time forge issues are triaged or worked (any phase) | The moment an issue is triaged, worked, or closed |
| `docs/token-ledger.md` | Actual token usage: one row per working session; final reconciliation (cost + deviation vs estimate) at release | With Estimate v1 (Phase 1 close), per `references/estimation-budget.md` | At the end of every working session; verified at phase/sprint closes |
| `CLAUDE.md` + `AGENTS.md` (repo root) | The portability lock, the same Keel block mirrored in both: binds ANY assistant/environment opening the repo to the Keel workflow | Phase 1, first action (or adoption) | When Keel's protocol block changes (between its delimiters only) — verified every session by the lock-freshness check (version stamp on the BEGIN delimiter) |
| `.claude/skills/keel/` + `.agents/skills/keel/` | Embedded copy of the skill (optional, recommended), one tree per discovery convention — makes the repo self-sufficient | Phase 1, first action (with user approval) | Version-synced from the installed skill, one direction, both trees |
| Assistant rules + subagents (`.claude/rules/`, `.claude/agents/`, and the other accepted tools' containers) | Optional native assistant config: path-scoped rules + reviewer subagents, generated from recorded decisions | Phase 2 close, if accepted at 0a (adoption: after its step 4) — per `references/assistant-config.md` | When a recorded decision changes their source — deliberately, never silently, every container in the same change |
| Permission allow-lists, `.githooks/pre-commit`, MCP registration (per tool) | Optional: confirmed permission allow-lists, confidential-data commit gate (one per project), dev MCP servers | Phase 5 scaffold (gate at adoption step 2 if accepted) | Tooling/playground commands or the dev MCP set change |

Everything else in `docs/` (specs, flows, design handoff, BUILD-SPEC, sprint files) is a **stable artifact**: written once at its phase, amended deliberately — a mid-project scope change follows "Scope changes" below — never casually rewritten. The state files above are the only ones that change constantly — keeping them small and the artifacts stable is what makes context cheap and cache-friendly.

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
- Assistant config: [none / rules / rules+agents / full] (tools: [claude, codex, copilot, cursor, gemini, windsurf, ...]) — per references/assistant-config.md
- Models: [orchestrator=<model> / reviewer=<model> / mechanical=<model>, per accepted tool — role→model map, per references/assistant-config.md; n/a if no agents]
- Keel baseline: [vX.Y.Z — last Keel version this project was reconciled to]
- Website intent: [yes — own domain|subdomain / no]
- Client budget: [yes / no — asked once at Phase 1 step 10; yes → docs/budget.md at Phase 2 close]
- User guide: [languages + ships in release yes/no + dev portal yes/no and ships/repo-only / declined — asked at Phase 6; guide/ at the repo root]
- Docs theme: [keel-docs-theme vX.Y.Z vendored in guide/_theme/ / n/a until Phase 6 — per references/guide-theme.md]
- Test-first policy: [pure-logic / pure-logic + acceptance / none (D-0XX) / n/a — <why> (only where the project ships no executable product at all, e.g. a documentation or instruction package)] — asked once at Phase 2 step 4e, default `pure-logic`; decides whether pure logic (and, on the wider value, each slice's acceptance criterion) gets its test written and seen failing BEFORE the code. Never re-asked. Two rules hold at EVERY value including `none`: a bug fix starts from a failing reproduction test, and a test derived from an AC-nn or a reproduced bug is never edited to make it pass. Per references/test-automation.md ("When the test is written")
- Durability: [git remote <name> <url> / synced folder <service> / both / repo but NO remote — <what is pending> / NONE — accepted risk (D-0XX)] — per SKILL.md "Work never lives only on this machine": the work must survive this computer. Asked as Question 0 of the session-start setup batch, before anything is created. The ANSWER is never re-asked, but the two facts behind it (a repository exists; it has a remote or the tree replicates off the machine) are re-verified every session — a remote can be removed and a folder can leave sync without anyone noticing
- Autonomy: [automatic — Keel does not ask, and does every merge to develop and every push itself | not automatic — Keel asks every time and pushes only what was explicitly requested] / issues: [after-sprint|on-request|n/a no forge] / Issue sweep interval: [Xh — default 24h; n/a unless after-sprint] / Issue capture: [on — a problem the user reports becomes a forge issue before the work starts | off | n/a no forge] — the session-start setup batch (SKILL.md), asked once and applied silently thereafter. Everything hangs off the first value; it is never inferred per action. `Issue sweep interval:` gates the kickoff-side check in `references/phase-5-development.md` ("Sprint kickoff") against `docs/issues.md`'s `Last inbound sweep:` line. The MODE lives in a per-machine file (`.claude/settings.local.json` is gitignored, so a fresh checkout has none) while this line is the recorded DECISION, so a new machine gets the file written without re-asking
- Branches: [integration branch (default `develop`) / current work branch / anything on develop awaiting the user's merge to main] — per SKILL.md "Git flow": Keel merges work branches to develop and pushes; the merge to main, the tag and the release are the user's act, always
- Notify: [channel — recipient / none — nothing delivering in this environment / declined] — the out-of-band channel per references/notifications.md; re-probed every session, because a channel that answered yesterday is not a fact about today
- Chaining: [off / prefill / start — default follows `Autonomy:`: automatic → the maximum tier the gates allow, otherwise off. What a CLEAN close-out does beyond writing docs/continuation-prompt.md and showing the prompt, which happen on every value including off; prefill opens the next chat pre-filled (user presses Enter), start launches and submits. Asked at Phase 1 step 0a with the warning attached, never filled in silently. start is GATED on the single-lane lock and is verified on macOS only; without both, prefill is the maximum offered. Falls back to printing]
- Chaining model: [the model every chained chat launches with, e.g. `opus` — passed as `claude --model <value>`. Asked once at Phase 1 step 0a in the same breath as `Chaining:`, never inferred. `n/a` when `Chaining: off`. A new `claude` process inherits NOTHING from the one that launched it, so without this the chain resolves the model from settings and silently runs on whatever the account default happens to be]
- Chain verified: [YYYY-MM-DD, tier <prefill|start>, Keel <version>, keel-continue <checksum> — written ONLY by `scripts/keel-chain-check --smoke` after it observed the launch actually run, never by hand and never from a reading of the script. Absent, or a checksum that no longer matches `scripts/keel-continue`, means the launcher is unproven and `keel-chain-check` reports NOT READY until `--smoke` is run again. `n/a` when `Chaining: off`]

## Phase status
| Phase | Status | Key artifacts |
|-------|--------|---------------|
| 1 Discovery | [pending/in progress/done/parked — <why>] | docs/00-competitive-landscape.md, docs/01-discovery.md, docs/estimate.md (v1 preliminary) |
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

### Deferred items (consciously postponed work)
- [what — severity — review trigger: "revisit when touching X" / "before release" | "none"]

Last updated: [date — phase/step]
```

Update rules: mark a phase `done` only when its definition of done passed (reported ✓/✗ to the user). `parked — <why>` is a recognized project status: set it when the user parks or discards the project — at the Phase 1 verdict or at any later point; the artifacts stay in place, never deleted, so the project can be resumed or revisited cold. "Next action" must always be executable by a fresh session with no other context. Never let PROGRESS.md drift from reality — a stale state file is worse than none. One deliberate exception to "the session updates it at the moment of change": when work is fanned out over git worktrees, only the session owning the MAIN tree writes this file, and a worker writes a report instead — see "Fan-out over worktrees" below, which records why.

Deferred items are the living list of consciously postponed WORK — a definition-of-done ✗ the user accepted, a performance finding accepted as-is — each entry carrying a severity and a review trigger ("revisit when touching X", "before release"). This is the greenfield counterpart of adoption's fix-now / fix-when-touched / accepted triage: `docs/decisions.md` logs the DECISION to defer; this list tracks the work until its trigger fires or the user closes it.

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

Record here: project type, stack choice, license, i18n and accessibility levels, scope cuts, architecture choices, anything where a future session could plausibly "re-decide" differently. Phase 6's `architecture.md` consolidates from this log instead of reconstructing memory. When an entry must reference a secret-shaped string (a token format, a key pattern), describe it or split it apart — never paste it verbatim: the confidential-data gate scans decision notes like any other file (SKILL.md "Confidential data never reaches Git", point 5).

## `docs/lessons-learned.md` — template

Append-only; never trim.

```
# Lessons Learned — [Project name]

## L-001 — [short title]
- Symptom: [what was observed — the thing a future session would recognize]
- Cause: [what was actually wrong, once diagnosed]
- Fix: [what resolved it]
- Where: [phase/slice/file]
- What failed first: [the attempt that didn't work — saves the next session from repeating it]
- Check added: [the keel-verify check, test, or gate that now catches it — or "none possible: <reason>"]
- Rule for next time: [one line a future session can apply directly]
```

The entry leads with **symptom → cause → fix** because that is how it gets read: a future session arrives holding a symptom, not a diagnosis, and an entry organized any other way is not found at the moment it would have helped.

If a lesson came from a code bug, the fix gets a regression test in the same slice (Phase 5 rule) — the lesson entry links to it. And **"Check added" is a real field, not a formality**: whenever a lesson could have been caught mechanically, adding that check to `scripts/keel-verify` (or to the test suite) is part of closing the lesson, because a rule that lives only in prose is a rule that will be broken again by a session under pressure.

**Where a lesson goes — two destinations, and the distinction is load-bearing:**

| What happened | Destination |
|---|---|
| A problem specific to THIS project | `docs/lessons-learned.md` — this file. Memory. |
| A trap that would bite ANY project of this class | Keel's `references/anti-patterns.md`. Prevention. |

When something is clearly the second, propose codifying it into the skill — per SKILL.md, an improvement the user agrees to is codified into Keel, not only recorded in the project that found it. Recording it in both places is fine; recording a class-wide trap only in one project's log means the next project pays for it again.

## Design Request register (Phase 4)

Every Design Request is numbered and saved before it is given to the user: `docs/design/design-requests/DR-001.md`, `DR-002.md`, ... (the filled design-request-template, plus a `Status: sent / resolved [date]` line at the top). PROGRESS.md "Open items" lists every DR and its status. The Phase 4 faithfulness checklist item "zero unresolved Design Requests" is verified against this register, not against memory — a fresh session must be able to see that DR-002 is still open.

## `docs/issues.md` — the forge issue log (any phase)

Whenever the project's forge issues are accessed — GitHub, GitLab, Gitea, Bitbucket, or any other Git forge — the work is tracked in `docs/issues.md`. The purpose is total traceability: at any moment, and from any future session, it must be possible to see everything there is, everything that was done and exactly HOW, and everything still pending — so when a problem surfaces later, what was changed and why is on record, never reconstructed from memory.

Created the first time issues are triaged or worked (any phase — development, post-release maintenance, adoption). Updated **at the moment** an issue is triaged, worked, or closed — like every state file, never "later".

```
# Issues — [Project name]

> Living log of forge issues ([forge + repo URL]). Inventory first, one entry per issue worked.
> Updated the moment an issue is triaged, worked, or closed.
> Last inbound sweep: [date time, ISO-ish e.g. 2026-07-31 18:40 | never] — set the moment an inbound sweep finishes (new issues + new comments on existing ones), whether or not it found anything. Read at every sprint kickoff against the card's `Issue sweep interval:` to decide whether the kickoff re-sweeps before planning.

## Inventory
| # | Title | Type | Priority | Status | Entry |
|---|-------|------|----------|--------|-------|
| 123 | Checkout fails on empty cart | bug | high | awaiting deploy | E-001 |
| 124 | Support WebP product images | feature | low | open | — |
| 125 | Wrong tax on refunds | bug | high | awaiting reporter | E-002 |

## Entries (one per issue worked)

### E-001 — #123 Checkout fails on empty cart
- Link: [forge issue URL]   Status: in progress / awaiting deploy / awaiting reporter / resolved [date] / won't fix (reason)
- Diagnosis: [what was actually wrong — root cause, not the symptom]
- Resolution: [what was done and why — the approach taken]
- Changes: [commits/PR, files touched, the version that ships the fix]
- Verification: [regression test added (Phase 5 rule), test point, playground check]
- Replies: [beat 1 — fix-landed comment, date + link | beat 2 — testable comment, date + link | none yet]
- Deploy: [notified <date> via <channel> | confirmed up by the developer <date>, version X | n/a]
- Closed by: [the reporter <date> / the developer <date> / Keel after the reporter confirmed <date> | still open]
- Inbound: [last comment received — who, when, what it said, and what it changed | none since the last sweep]
- Lesson: [L-NNN in docs/lessons-learned.md if one was recorded | none]
- Pending: [anything left on this issue | none]
```

Rules:

- **Inventory covers what is known; entries cover what was worked.** On first contact with the forge, fill the inventory with at least the open issues (closed history is optional). Every issue actually worked gets its E-entry — an issue closed without its entry is a state defect.
- **Status values:** open / triaged / in progress / resolved / won't fix (reason recorded). The inventory row and its entry must agree.
- **An entry must answer "what did we do here?" months later:** diagnosis, approach, commits, verification — enough to reopen the work cold if the problem resurfaces. If the fix produced a lesson, record it in `docs/lessons-learned.md` and link it; the regression test lives with the fix (Phase 5 rule).
- **Issue capture — a problem the user reports becomes a forge issue, when the card says so.** Governed by the project card's `Issue capture:` value, asked once in the session-start setup batch (SKILL.md, Question 2b) and **never assumed**: a tracker is a shared public surface, and a project that keeps its tracker for third-party reports is entitled to that. With `on`:
  1. **The issue is opened BEFORE the work starts**, not after it succeeds. That ordering is the whole point — a session that dies mid-fix, runs out of context, or gets interrupted leaves the report standing on the forge instead of only in a chat log nobody can search. It is written in English like everything Keel opens ("Token economy"), carries what was observed, how to reproduce it, expected versus actual, and the version or commit it was seen on, and it is filed as reported by the user, never dressed up as a third-party report.
  2. **Check for a duplicate first, and comment instead of opening one.** If an open issue already covers it, the new information goes there as a comment — the same problem filed twice fragments its own history and makes both copies less useful than either would have been. This is the one case where capture produces no new issue.
  3. **Comment as the work advances**, not only at the end: what it turned out to be, the commit or PR that addresses it, anything found on the way that changes the diagnosis. An issue whose thread jumps from "opened" to "fixed" has thrown away the part that is worth reading in six months.
  4. **The user still closes it.** "Keel never closes an issue on its own reading of the code" holds here exactly as everywhere else, and the fact that the reporter is the user sitting in the chat does not soften it — the confirmation that it is actually fixed is theirs to give. The three beats below apply unchanged where a deploy stands between the fix and the reporter being able to try it.
- **Replying is publishing, and it runs in three beats — never one (UNBREAKABLE).** A comment on a forge issue is read by a third party, carries the developer's name, and cannot be taken back. So an issue whose fix has landed is never answered with "fixed" and closed in the same motion, because the code changing and the reporter being able to try it are two different events, usually days apart:

  1. **Fix landed.** Comment on the issue: what was wrong, that the fix is implemented, and that they will be told when there is something they can actually test. Status → `awaiting deploy`. **The issue is not closed.**
  2. **The developer is notified** through the recorded channel (`references/notifications.md`) that a build/upload/deploy is needed before the reporter can test — naming the issue, the version and what has to go up. This is a real stop: it goes in `docs/PROGRESS.md` open items and Keel waits.
  3. **The developer confirms it is up.** Comment again on the issue: it can be tested now, on which version, and what to look for. Status → `awaiting reporter`.

  Then the reporter answers. A confirmation closes it; a "still broken" reopens the work on that issue with the report as new evidence. **Keel never closes an issue on its own reading of the code** — not after the fix, not after the deploy, not at a sprint close, not at a release. And if the reporter or the developer already closed it, Keel leaves it closed and records who did; re-closing a closed issue is noise on someone else's thread.
- **The language of a forge message is decided by WHO owns the thread, not by Keel's English default (UNBREAKABLE).** An issue Keel OPENS is written in English, title and body, whatever language the conversation runs in — it is a permanent public artifact of the project (SKILL.md, "Token economy"). Every one of the three beats above, and every other reply on an issue somebody else opened, is written in **the language that issue is written in**, read from the reporter's own text — not from the repo, not from this conversation, not inferred from a name or a locale. Answering a Spanish bug report in English moves the translation cost onto the person who did the project the favour of reporting it, on their own thread, and it is the exact error the English default produces if this is not said. Mixed thread → the language the reporter last used; genuinely undecidable → English. Record replies in `Replies:` in whatever language they were published, and hold the orthography contract in that language — a reply in Spanish carries every accent and every ñ.
- **Reading the thread back is half the duty (UNBREAKABLE).** A log that records what Keel published and nothing about what came back is a monologue, and it fails exactly where the lifecycle needs an answer. Every issue sweep — at each sprint close and at each maintenance touch — looks at BOTH new issues and **new comments on existing ones**, and reads them by status: on `awaiting reporter` a comment IS the verdict, closing the issue (recorded under `Closed by:`) or reopening the work with that report as new evidence; on `awaiting deploy` it is usually "when?", and gets a straight answer; anywhere else it is triaged like any other input. What it says, and what it changed, goes in the entry's `Inbound:` field. A comment that asks something only the user can decide is a stop with its notification — never a guess published on a public thread.
- **The three beats survive across sessions**, which is the whole reason they are recorded rather than remembered: the `Replies:`, `Deploy:` and `Closed by:` fields let a fresh session tell beat 2 from beat 3 without reading the forge thread and guessing. An issue sitting in `awaiting deploy` for weeks is a visible open item, not a forgotten one.
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

Updated in the same slice that adds, changes, or removes a surface — an INDEX row without its doc, or a doc without its row, is a slice defect. A changed surface has its row and its doc updated in that same slice; a removed surface has its row deleted (never released) or marked deprecated/removed with its replacement (already released), per SKILL.md "Document every public surface at the moment it changes". A row pointing at a symbol the code no longer has is a defect like any other.

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

A chat can fill up in any phase — a long competitive scan, a long external-setup loop — not only during development. Whenever the session is ending (or the user asks to continue elsewhere), produce this ready-to-paste prompt — **and at every sprint close too, even when the session carries straight on into the next sprint**, so the person can shut the laptop at a close and lose nothing (see "The continuation file" below). Phase 5's sprint close-out uses the same mechanism with sprint specifics added. Before producing the prompt, append the session's row to `docs/token-ledger.md` (per `references/estimation-budget.md`) — the continuation prompt is not complete without it. **Show it to the user proactively** — at every sprint close and whenever a session is ending, with the one-line instruction to paste it into a new chat to continue; the user never has to ask for it.

```
Load the `keel` skill and resume [PROJECT NAME] at Phase [N] ([phase name]), [step/sprint X].
1. Before anything else, apply the recorded session setup — from the hand-off's own `Mode:` field, then confirmed against the project card's `Autonomy:` and `Notify:` lines (the card is the authority; where they disagree, say so in one line and follow the card). Do not re-ask what is already recorded. If the card says automatic and this session is in `manual`, resolve it (write or merge .claude/settings.local.json with permissions.defaultMode "auto", or restart with --permission-mode auto): in `manual` every composite command opens a dialog and the work cannot run unattended. Re-probe the notification channel for THIS session and say so if nothing delivers.
2. Read the `Branches:` card line: which branch the work is on, what still has to be merged into the integration branch, and whether anything is waiting on the user's merge to main. Merge your work to develop and push it as you go (automatic mode); never merge to main, never tag, never release — say it is ready and stop there. Re-verify the `Durability:` line mechanically (a repository exists; it has a remote, or the tree replicates off the machine) — do not re-ask the question, but say so in one line if what was recorded is no longer true. Nothing this session produces is left uncommitted: commits go to develop or to a work branch bound for develop, and a repo with only main/master gets develop created first.
3. Keep going while the queue holds work that does not depend on what is unfinished. Do not stop to ask whether to continue, and do not hand back a menu of remaining items: stop only when the next step depends on something not yet done, or when a decision is genuinely the user's. If context runs out, that is a hand-off, not a decision — write docs/continuation-prompt.md and continue there under this same rule.
4. Read docs/PROGRESS.md — the project card, phase status, current position, open items.
5. Read docs/decisions.md and docs/lessons-learned.md — do not re-litigate decisions; do not repeat recorded mistakes.
6. Read the current phase's reference (references/phase-[N]-*.md) and the inputs PROGRESS.md names for the current position.
7. Continue EXACTLY from "Next action". Do not restart the phase, do not reinterpret or "improve" earlier decisions, do not redesign. Gaps go to the user or to a Design Request, per the skill.
```

The prompt must be self-sufficient: assume the new session knows nothing except what these files contain. Producing it does not force a chat switch — if the current chat still has capacity, continue in it; the prompt is insurance. Like everything Keel creates, the continuation prompt is written in English (SKILL.md "Token economy"), regardless of the conversation language.

### The continuation file — `docs/continuation-prompt.md` (UNBREAKABLE)

The prompt is not only shown in the chat; it is also WRITTEN to `docs/continuation-prompt.md`, always at that exact path, overwritten each time. The fixed path is what makes the hand-off addressable by a short constant instruction instead of a wall of text that has to be selected, copied and pasted without losing a line, and it removes every length limit from the hand-off, because what travels between chats is a path.

The file is ephemeral session state, not project history: it is listed in `.gitignore` and never committed. Showing the prompt in the chat does not stop — the file is in addition, never instead.

**Three moments write it, and the third is the one that gets skipped.** A session ending, a session running out of context — those are obvious, because the session is stopping. The third is **every sprint close, whether or not the session stops there** (`references/phase-5-development.md` §5, step 11): a sprint close is where the person actually walks away, and the guarantee they need is that closing the laptop at that moment costs nothing — a new chat, opened days later by hand, needs one instruction and no memory of anything. It holds in automatic mode exactly as in manual, and on `Chaining: off` exactly as on `start`: chaining decides whether a next chat is OPENED, never whether the hand-off EXISTS.

**A hand-off that is not current is worse than no hand-off (UNBREAKABLE).** The courier checks compare `Commit` and `Tree` against the repository, so once the session works past the moment the file describes, the file stops being insurance and becomes a `VERDICT: STOP` waiting to happen — and it looks exactly like protection until the day it is used. So a session that keeps working after writing one **regenerates it as the work advances** — at every commit point, which in Phase 5 means every test point that commits — and unconditionally before the session ends. Overwriting is cheap and the file is small; a stale one costs the user the reconstruction the mechanism was built to eliminate.

It opens with a freshness header, then the prompt verbatim:

```
---
Repo: 8f2c1ab
Generated: 2026-07-29T18:40:00+02:00
Keel: 5.3.0
Commit: a1b2c3d
Tree: clean
Position: Phase 5 — Sprint 3, slice 3.4 closed; next action: slice 3.5
Branch: feature/sprint-3 (merged+pushed to develop); nothing awaiting main
Mode: automatic — chaining start
Handover: clean
---

[the continuation prompt, exactly as templated above]
```

`Mode:` carries the card's `Autonomy:` and `Chaining:` values into the hand-off itself, and the arriving session applies them BEFORE anything else — step 1 of the template already says so, but until this field existed the template said it about a card the session had not read yet. **This is the failure that looks least like a chaining failure and is the most common:** the chain fires perfectly, the next window opens perfectly, the arriving session reads the hand-off, starts working in `manual` because nobody told it otherwise, and stops at the first composite command with a permission dialog nobody is there to answer. From outside it is indistinguishable from a chain that never fired. The field costs one line and makes the mode travel with the work rather than waiting to be looked up. It is carried, not checked: the card remains the authority, and where they disagree the card wins and the session says so — but a hand-off that never mentions the mode cannot even produce the disagreement.

`Branch:` names the work branch, whether it is already merged and pushed to the integration branch, and anything sitting on `develop` awaiting the user's merge to `main` — a hand-off that does not say where the code IS sends the next session hunting. `Handover:` is `clean`, or `blocked: <one line>` naming what stopped the session — and it is `blocked` only when the SESSION could not proceed at all, never because some item in it is parked awaiting an answer, a deploy or a merge. A session that parked three questions and still shipped two slices hands off `clean`, with the parked items listed as open items. `Tree:` is `clean`, or `dirty (N files)` from `git status --porcelain` — the session that writes a hand-off while running out of context is exactly the one likely to leave work uncommitted, and `Commit:` alone says nothing about it, so the next session would inherit changes it believes do not exist.

**Producing `Repo:` — three traps, all silent.** It is the SHORT root-commit hash, and the command has edges that return a wrong answer with exit 0:

```
git rev-parse --is-shallow-repository        # true → do NOT write a hash
git rev-list --max-parents=0 HEAD | sort | head -1
```

- **A shallow clone returns the grafted commit, not the root**, with no error, and the value CHANGES after `git fetch --unshallow`. A hand-off written under `--depth 1` therefore carries an identity no full clone accepts, and the same directory rejects its own hand-off once deepened. When `--is-shallow-repository` is `true`, write `Repo: unavailable (shallow)`; the reader treats repository identity as unverifiable and relies on the containment check below.
- **A repository can have more than one root commit** (unrelated histories merged), and the command then prints several lines — a naive `$(...)` yields a multi-line value that can never match a 7-character header. `sort | head -1` picks one stably, independent of traversal order.
- **`Repo:` identifies the REPOSITORY, not the working directory** — see the containment check below.

**Why `Repo:` exists, and why the obvious fix is not enough.** The filename is IDENTICAL in every Keel project. So a chat opened in the wrong window reads that project's own hand-off, and every other check passes — the commit really is its `HEAD`, the position really is its `PROGRESS.md`, the timestamp really is recent. Nothing is stale; the session simply continues the wrong project, coherently and unsupervised. That is why two independent halves are required and neither is optional:

- **Every launch passes this repository's ABSOLUTE hand-off path**, not a relative one, so the right file gets read even from the wrong window.
- **`Repo:` carries the root-commit hash** — the stable identity of a repository, unlike a remote URL, which may be absent or plural — so a session that finds itself in a different repository than the hand-off names STOPS and says so instead of working.

The first makes the right file get read; the second makes a session in the wrong place refuse. Alone, each leaves the failure silent.

**And `Repo:` alone is still not enough, because a repository is not a directory.** Two checkouts of the SAME repository at the same commit — a `git worktree`, a second clone, a copied folder, a sync-service duplicate — share their root commit AND their `HEAD`. A session in one of them reading the other's hand-off passes every identity check while working in the wrong directory, which is the original flaw wearing a narrower disguise. Worktrees are not exotic: agent harnesses create them routinely to isolate parallel work. The separating check is containment — the hand-off's REAL path must lie inside this session's own `git rev-parse --show-toplevel` — and it costs one command.

**The file is a courier, never a source of truth.** `docs/PROGRESS.md` and the repository are the authority; this file only points at them. The session that reads it verifies, in this order:

| Check | How | Mechanical? |
|---|---|---|
| **Containment** | the file's REAL path (symlinks resolved) is inside this session's `git rev-parse --show-toplevel` | Yes |
| `Repo:` | against `git rev-list --max-parents=0 HEAD \| sort \| head -1` in the repo the session is actually in | Yes |
| `Commit:` | against `git rev-parse HEAD`; `git merge-base --is-ancestor <Commit> HEAD` also reports HOW FAR behind, which is more useful than a yes/no | Yes |
| `Generated:` | against the current time AND the file's own modification time (`stat`), which the header cannot forge | Yes |
| `Tree:` | against `git status --porcelain` — a hand-off written `clean` on a tree that is now dirty, or vice versa, means work moved outside the hand-off's account of it | Yes |
| `Branch:` | against `git rev-parse --abbrev-ref HEAD` for the branch, and `git log @{u}..HEAD --oneline` for what the hand-off claims was pushed — a hand-off saying "merged and pushed" over commits that never left the machine is the exact failure the git-flow rule exists to prevent, and it is one command to catch | Yes |
| `Position:` | against PROGRESS.md's current position and next action | **No — prose against prose** |

The first six are executable. `Position:` is a human-readable corroborator, deliberately kept in prose because a position is a sentence, and it is NOT claimed as a mechanical check anywhere — a check that cannot be run is a promise, and this skill does not write promises as checks. Containment runs FIRST because it is the only one that catches a second checkout of the same repository, where every identity check legitimately passes.

**A session never composes these checks itself — it runs `scripts/keel-handoff-verify` (UNBREAKABLE).** This is not a style preference, it is what makes the checks run at all. A session writing them inline produces one line of nested `$(...)`, the permission matcher cannot decompose it, the call comes back `Parse error`, and the project's allow-list is bypassed **even when every git command in it is allowed** — at every link of a chain, not only the first. Measured. So the checks live in a generated script with ONE allow-list entry:

```json
{ "permissions": { "allow": ["Bash(./scripts/keel-handoff-verify:*)"] } }
```

The table above is that script's CONTRACT, not a recipe for the session to reimplement. Keel generates it at the Phase 5 scaffold beside `keel-verify` and `keel-doctor`, and the continuation prompt instructs the next session to run it. Its output is one line per check plus a `VERDICT: CONTINUE` or `VERDICT: STOP`, so the session reads a verdict instead of interpreting five command outputs. Written any other way, the courier checks are exactly the promise this skill refuses to write.

**Timestamps are compared as epoch seconds, never as strings.** The header writes an ISO offset (`+02:00`) and `stat` reports another form (`+0200`); a string comparison of the same instant therefore reports tampering on every run. Normalise both to epoch first — the script does; a human reading them will silently do the right thing and never notice the trap.

Everything agrees → continue. Containment fails → STOP: this hand-off belongs to another working directory, name it and do not act. `Repo:` disagrees → STOP: this hand-off belongs to another repository. `Repo: unavailable (shallow)` is neither pass nor fail: identity is unverifiable, containment carries the weight, and the session says so rather than pretending either way. Anything else disagrees, or `Generated:` is old enough that the repository has moved since (new commits, a changed position) → **STOP and say exactly what disagrees**, then resume from `docs/PROGRESS.md` instead. A stale or foreign hand-off is more dangerous than no hand-off: it reads like an instruction and is actually a memory. A missing file is not an error — it means resume normally from PROGRESS.md.

Timestamping is done in the header and not in the filename deliberately: a dated filename would make the path change on every write, and the header plus the file's modification time answer "was this written just now or three days ago?" at no cost.

**The most common case is not a new chat at all — it is `/clear` in the same window.** A session whose context is full but whose window is perfectly good starts a fresh session in place (`/clear` — "start a new session with empty context; the previous session stays on disk, resumable with `/resume`"), then reads the hand-off. This is the SAFEST route and it is the one to recommend by default: same window, same repository, permissions already granted, the wrong-window failure impossible by construction. It is also the least automatable — nothing lets a session clear its own context — which is exactly why it is stated here rather than left implicit. All the chaining machinery below exists for when a new window is genuinely wanted; `/clear` needs none of it.

### Chaining the next chat (opt-in — `Chaining:` on the project card)

**Split this in two before reading further, because only one half is universal.** The continuation FILE works with every assistant, everywhere, with no integration whatsoever: "read `<abs-path>/docs/continuation-prompt.md` and continue" is an ordinary prompt, so Codex, Copilot, Cursor, Gemini CLI, Windsurf, a web chat or a human typing it all consume the hand-off identically. That half is the mechanism. Opening the next chat automatically is the other half — a per-tool convenience that depends on an integration each vendor either offers or does not, and that Keel must never assume on a tool's behalf.

The card records what a CLEAN close-out does beyond writing the file:

| `Chaining:` | What happens | Human gesture left |
|---|---|---|
| `off` | The file is written and the prompt shown. Nothing opens. | Open a chat, paste |
| `prefill` | The tool's recorded action opens a session with the prompt already typed | Press Enter |
| `start` | The tool's recorded action launches AND submits | None — unless the lane is busy, in which case the new window prints the prompt |

The values name the BEHAVIOUR, not the mechanism, on purpose: the same tool family does both — Claude Code's URI handler pre-fills and never submits, while its CLI, started with a prompt argument, submits immediately. A single value meaning different things on different tools is precisely the ambiguity this skill refuses everywhere else.

**`start` is opt-in per project and is GATED on the single-lane lock below.** It is the RECOMMENDED value on a card that says `Autonomy: automatic` (see the question below) and is not recommended anywhere else, but it is never selected silently on any card. The protections that matter survive without a human keystroke: a blocked hand-off never chains, and a stale, foreign or misplaced one is refused on reading — all machine checks. What a keystroke uniquely guarded against was landing in the wrong place, and the absolute path, `Repo:` and containment close that.

But removing the human removes something else that nobody had accounted for, and it was found by RUNNING the mechanism rather than reading it: **the person between links was the only thing keeping the chain single-file.** A three-link chain under test produced four live sessions and four windows in sixteen seconds — two launches were still in flight while the counter was read, so the cap was passed by design rather than by accident. Two sessions live on one checkout means interleaved commits on one branch, `docs/PROGRESS.md` overwritten by whichever finishes last, a hand-off describing a state neither of them left, and edits made on reads the other has already invalidated. **None of the courier checks fire**: same repository, same starting commit, a perfectly fresh hand-off. And it escaped the person who had just written the cap, which is the part that matters — a user who merely switched `start` on has strictly worse odds.

So `start` requires four things, and a project missing any of them is offered `prefill` at most:

1. **The single-lane lock** (below). Without it, `start` is a chain that can fork silently.
2. **A verified open action for the tool that produces a VISIBLE session**, not a headless run. On macOS that is `osascript` driving Terminal.app, verified. Linux (`gnome-terminal` / `konsole` / `xterm`) and Windows are NOT verified: an implementer who reaches for the plain platform open command ships the headless variant, which runs correctly and opens nothing, leaving the user waiting for a window that will never appear. **`start` is therefore verified on macOS only today.**
3. **The project's allow-list entry for `scripts/keel-handoff-verify`**, plus folder trust granted once. Without them every link stops for a permission prompt, which is not automation with extra steps — it is `prefill` pretending.
4. **The `claude` command on PATH.** `start` launches a CLI session, so without the standalone CLI there is nothing to launch. This is worth stating because it is not obvious: neither the desktop app nor the VS Code extension puts `claude` on PATH — the app runs Claude Code graphically, and the extension bundles a private copy for its own panel — so a user can have both installed, use Claude Code daily, and still have no `claude` command. Absent → `prefill` is the maximum, and say which requirement failed rather than letting the first close-out of a chain discover it. **The probe and the install offer belong to the Phase 1 environment preflight** (`references/phase-1-discovery.md` §5a, question 5), which runs `command -v claude` whenever the card is `prefill` or `start`, offers the platform's install command if it is missing, and records the answer either way — but that answer is a snapshot, not a standing guarantee: `scripts/keel-continue` re-checks it live before every `start` fire (its contract, point 5a), because Phase 1 cannot see a PATH that changes weeks later.

The residual risk stays real even with all three: a window begins working unsupervised from a hand-off composed by a session that was running out of context. That is not uniform — a routine slice is not a migration, a release, or anything touching production data — so it remains the user's call per project, recorded on the card and in `docs/decisions.md`.

#### What may stop a chain — decided by the script, not the session (UNBREAKABLE)

A close-out on a card that says `prefill` or `start` runs `scripts/keel-continue` **unconditionally**, the moment the hand-off is written — whether that hand-off is `clean` or `blocked`. The session does not pre-judge whether to run it; it always runs it, then relays exactly what it printed. This is deliberate, and it is the fix for the failure class this section used to invite: a decision phrased as "the session checks four things first" is a decision the session can get wrong in a new way every time, because it is asking an LLM to interpret prose under pressure at the worst possible moment. A decision phrased as "the session always runs the script, and the script alone can say no" removes that interpretation entirely — the same principle already applied to the courier checks ("a session never composes these checks itself") now applies to the fire-or-not question too.

**The session's own judgment is reduced to exactly one mechanical test:** does `scripts/keel-continue` exist (`[ -x scripts/keel-continue ]`)? If not, print the prompt and stop — the session cannot run what is not there. If it exists, run it. That is the whole of the session's role.

Everything that can stop a chain is answered BY THE SCRIPT, freshly, on every invocation — never recalled from the card, never inferred by the session from the hand-off's prose:

1. **`Handover:` on the hand-off it is about to launch.** Contract point 3: not `clean` → print the reason and the prompt, fire nothing. A string match on a header the session just wrote — no interpretation, no exception for a reason that "sounds minor," and critically, **not a check the session performs before deciding whether to call the script** — the script performs it.
2. **The tier's gates, re-verified live, never recalled from the card:** the tool registry probe (contract points 4–5) re-detects the entrypoint and its VERIFIED tier on every run rather than trusting Phase 1's answer, and the script re-checks `command -v claude` before firing a `start` action (contract point 5a) rather than trusting the Phase 1 preflight — PATH changes, a script gets deleted, an allow-list entry gets reverted by a merge, all after the card was written. Any one missing → print, name which.
3. `scripts/keel-continue` does not exist on this project — the session's one pre-check, above; the script never gets here.
4. The launch receipt for this hand-off is already claimed, the lane is busy, or the circuit breaker has tripped — the script's own state (contract point 6).

**Nothing else stops it, and the closed list is the point.** A note on the card, an uneasy feeling about an untested path, the fact that a window will appear on the user's screen — none of these are inputs the script reads, so none of them can stop it, and the session has no seat at this table to begin with. If the script printed instead of firing, the session states which of its lines said so, verbatim; it does not add a reason of its own.

**An unexercised mechanism is not a blocked one, and this is the failure that was measured.** A card carrying "the end-to-end chain has never actually fired on this project — the pieces are tested, the launch is not; the first real close that chains is its own evidence" was read as a prohibition and the close-out printed instead of running the script at all. The note says the opposite: it is a request for the next close to BE the evidence. Written on the card, an unexercised path is a fact about the project's history, never a veto — the only things that can veto are the four entries above, all mechanical, all inside the script, and "not yet exercised" is not among them. Where the distinction has to be made in prose elsewhere, say what is missing and what unblocks it, never a bare "unverified": a note that reads like a warning will be obeyed as one.

**And the close-out NEVER asks the user for permission to chain.** The card's `Chaining:` value IS that permission — asked at Phase 1 step 0a, in full, with the warning that `start` opens CLI sessions and removes the supervisor, and recorded in `docs/decisions.md`. Asking again at the close ("this will open a Terminal window on your Mac, shall I?") re-litigates a settled decision at the exact moment the user is least likely to be there to answer, which converts an automatic close into a stop. That a window becomes visible is not a new decision; it is what `start` means. The permission question was answered once and is not asked twice.

**A stop is reserved for what cannot be gotten past, never for what could still be worked around.** This is the same principle that governs the rest of `Autonomy: automatic` — a session with buildable work left in its queue does not stop to ask, it works the queue (SKILL.md, "Finish the queue") — applied to the one moment at the very end of a session where it is easiest to forget: closing is not exempt from "automatic means the work does not wait for a person who is not there." The four entries above are exhaustive precisely because each names a case where nothing further CAN be done without the missing piece — a blocked hand-off, a missing gate, a missing script, a script that has already answered no. Anything short of one of those four resolves to continuing, whether the continuation is the next slice or the next chat, and a session that pauses to weigh whether this particular close feels different has already left the closed list — the list exists exactly so that question is never reached.

#### The single-lane lock

One rule, and its two properties are both consequences of how the failure actually happened:

- **The ARRIVING session takes the lock, not the launching one.** A launcher cannot know who else is in flight — that is precisely what failed. A session that starts, finds the lock held by a live process, and exits saying so is the only shape that closes the window between launch and execution.
- **The lock file lives OUTSIDE the repository** (the user's state directory), **keyed by the REAL path of `git rev-parse --show-toplevel`** — not by the root-commit hash. A lock inside the tree is a brake the chain can erase: a `git clean`, a checkout, or a fresh clone resets it, and the thing it protects is the thing that modifies it. The key is the working directory for two reasons: the root-commit hash carries the shallow trap described above (it is not the root in a shallow clone and it CHANGES on `--unshallow`, so a live session's lock would become invisible to the next one in the same directory), and what has to be serialised is the tree being written to, not the repository in the abstract — two worktrees of one repository are two legitimate lanes, exactly as containment already treats them.

It holds the owning PID and its start time. **The holder releases it at its CLOSE-OUT, which is a moment in the session, not "on exit", which is a moment in the process (UNBREAKABLE).** A lock is only a lane if somebody gives it back; "detectable" is a property, not a policy, and a lane that is merely detectable stops serialising the moment anything goes wrong.

**"On exit" was the wrong moment, and under `start` it deadlocked the chain on the very first link.** The rule used to read "the holder releases it on exit — every exit, including the failing ones", and that sentence is unimplementable by the party it names: the holder is a SESSION, and a session does not get to run code when it ends. Its process outlives it — a CLI chat sits in its window, alive and idle, for as long as the window is open, and under `start` nobody is there to close the window. So the closing session fires the launch while still holding the lane; the window it opened arrives two seconds later, finds a lane held by a PID that is genuinely alive, and stops exactly as specified. Measured on a real project: the chain did not fork, it deadlocked — deterministically, at link one, with the previous chat's window sitting empty on screen holding a lane it had finished with. Every guard behaved correctly and the mechanism was useless, which is the shape a wrong moment always takes. The release therefore happens where the session can actually act: at the close-out, before the launch fires (`references/phase-5-development.md` §5 step 11, and the session-end path). Releasing before firing is not an optimisation of ordering — a release that lands after the new window has already checked is a race the chain loses, and it loses it silently.

**Every close-out releases, not only a chaining one.** `off` and `prefill` are not exempt and the temptation to exempt them is the same error one level down: the user who opens a chat by hand ten seconds later hits precisely the wall `start` hit. So the last act of any close-out that holds the lane is `scripts/keel-handoff-verify --release`, which frees it only if THIS session is the recorded owner and otherwise says there was nothing to release. It is idempotent, it costs one command, and it needs no allow-list entry of its own — the script already has one.

**Recovery, because release cannot be guaranteed.** A killed process runs no cleanup, so an orphan will happen. When the lock names a PID that no longer exists, or one whose start time does not match the recorded one (the number was reused), the arriving session TAKES the lane, says in one line that it recovered an orphan and from which PID, and continues. It does not ask: a stale lock that requires permission to clear is a lane nobody can enter, which is the same outage as a lane nobody leaves. If the PID is alive, the lane is busy and nothing is taken — that case is not recovery, it is the lock doing its job. One exception, and only one, is the baton below.

**The baton, because a release that depends on the previous session behaving is not a mechanism.** The close-out release above is the fix; this is what makes the fix hold when the close-out did not run — the session was interrupted, it crashed after firing, or the project still carries a `scripts/keel-continue` generated before this version. So the launcher leaves its own PID inside the launch receipt it just claimed (one file, `launcher-pid`), and the arriving session — which is verifying the SAME hand-off and therefore derives the SAME receipt identity, `Generated:` plus `Commit:` — compares the live lane holder against it. **Holder equals the PID recorded as this hand-off's launcher → that holder is by definition a session that has already closed out, so the lane passes to the arriving one**, reported in one line as a baton and not as a recovery, because nothing went wrong. Any other live holder still stops the session. The check cannot be loosened into "the holder looks idle" or "the holder is old": those are guesses about another session's state, whereas this is the launcher's own signed statement that it was finished when it fired.

A session that cannot take the lane does what every other blocked path does: prints the prompt and exits 0 — **and says how to clear the lane**, since the user is the only one who can: the holder's PID and start time, and that closing that window (or running `scripts/keel-handoff-verify --release` in it) frees it. A blocked session that does not name the remedy leaves the user with a deadlock and no vocabulary for it.

**Who implements it, and when: `scripts/keel-handoff-verify`, at the Phase 5 scaffold** (`references/phase-5-development.md` §1). The lane is claimed by the same script the arriving session already runs before acting, because that is precisely the moment it must be claimed — one command, one allow-list entry, and no window between verifying and starting work in which a second session could slip through. There is no separate lock script and no lock step for the user to remember. On a card that is not `Chaining: start` the script runs its five checks and takes nothing. The same script also RELEASES, under `--release`: it frees the lane when this session is the recorded owner, prints one line either way, and exits 0 — so taking and giving back live in one artifact behind one allow-list entry, and `scripts/keel-continue` still never touches the lane except to hand back what the closing session already held.

Until a project has this, `start` is not offered — not as a warning, as a gate.

#### One launch per hand-off — the launch receipt (UNBREAKABLE)

The single-lane lock serialises **execution**, and that is not the same as serialising **launching**. It was written for the case of two sessions racing to work in one tree, and it handles that correctly. It does nothing about one closing session firing the launch four times: four windows open, three of them arrive, find the lane held, and politely exit — the mechanism working exactly as specified while the user watches four chats appear instead of one, with no way to tell which is the live one. Measured, on a real close-out.

So the launcher gets its own guard, and it is the simpler of the two because it protects an **event**, not a resource:

- **A launch is claimed against the HAND-OFF's identity, not against the clock and not against the repo alone.** The identity is the hand-off's `Generated:` plus `Commit:` (a hash of the header is enough). A receipt exists → this exact hand-off has already been launched, and the script prints the prompt and exits 0 without firing. Regenerate the hand-off and you get a new identity and one new launch — which is correct, because that is genuinely a different continuation.
- **The claim is ATOMIC or it is decoration.** `mkdir` of the receipt path — it succeeds exactly once and fails if the directory exists, in one syscall, with no window. A `test -f` followed by a `touch` is two operations with a gap between them, and the gap is precisely where the duplicate is born. Same file location discipline as the lane: outside the repository, in the user's state directory, keyed by the real path of `git rev-parse --show-toplevel`, so a `git clean` or a fresh clone cannot erase the brake on the thing it is braking.
- **A launch is NEVER retried. Ever.** The open command's exit code says the command ran, not that a window appeared, and no available signal distinguishes "it opened" from "it did not". Under that uncertainty, firing again is how one hand-off becomes four. The rule is therefore absolute: fire once, and if the outcome is unknown or the command failed, PRINT the prompt. Printing is always the right answer to "I do not know", and it is never wrong — the user reads it and decides.
- **A session NEVER composes the launch itself — it runs `scripts/keel-continue`, or it prints (UNBREAKABLE).** This is the same rule the courier checks already carry ("A session never composes these checks itself"), and it was missing here, so the skill said how many times the launch may be fired and never said that the script is the only thing allowed to fire it. A session that finds no `scripts/keel-continue` — an older project, a scaffold that predates it, a checkout where it was never generated — **prints the prompt and stops.** It does not reach for `osascript`, `open`, or a terminal of any kind. Measured, on a real close-out: a session without the script hand-wrote its own launch and produced five windows, four of them killed by hand, none of the receipt's protections in play because no receipt was ever claimed. The absent script is not an obstacle to work around, it is the answer: no script means no chaining on this project yet, which is exactly the `off` behaviour the user already knows how to live with. Regenerating it is a maintenance touch on a later session, never an improvisation at the end of this one.
- **A launch that fired WRONG is spent, exactly like one that fired unobserved.** The never-retry rule above covers "I cannot tell whether a window appeared". It does not, in its own words, cover "a window appeared and I can see it is wrong" — the window opened in the wrong directory, or with a mangled command — and that gap was used: the measured close-out killed the process it had just launched and fired again, four times, each iteration technically honouring "never retry a failed launch" because each launch had, in fact, succeeded. So the rule is stated for both cases: **once the launch has fired, this session's chaining is over, whatever the outcome.** A wrong window is reported in one line and the prompt is printed; the user closes the window and pastes. Killing another session's process to make room for a better attempt is forbidden for the reasons in "Designs measured and rejected" — no cleanup runs, the lane is never released, and an orphaned lock is guaranteed — and it is forbidden even when the session that fired it is the one doing the killing.
- **Exactly one place in the whole skill may invoke `scripts/keel-continue`:** the session close-out (`references/phase-5-development.md` §5, and the session-end path above, which is the same procedure). A close-out that runs twice hits its receipt and fires nothing. A fanned-out worker never launches at all — only the session owning the main tree closes out.
- **A circuit breaker, because a loop is not a hypothesis.** More than three receipts for the same repository within one hour means something is re-running a close-out; the script stops chaining entirely, prints the prompt, and says in one line that it detected repeated launches and disabled chaining for this session. A runaway that announces itself costs a message; one that does not costs a screenful of windows and the user's trust in the mechanism.
- **The receipt carries the launcher's PID**, written into it the moment it is claimed. It costs one file and it is what makes the baton above possible: the arriving session derives the same receipt identity from the hand-off it is verifying, so a lane held by that exact PID is a lane whose owner has already closed out. Writing it is the launcher's last statement about itself, and it is worth more than any inference the arriving session could make about a process it did not start.
- **Receipts are disposable state**, cleaned with the lane's own housekeeping. Losing them can only cause one extra launch, never a missed continuation — the failure direction that matters is the one the user just saw.

**How the question is asked — at the start, and with the warning attached.** `Chaining:` is not a configuration preference to be buried in the project card and filled in silently. It is asked at Phase 1 step 0a (and at the reconciliation, for an existing project) alongside the other opening decisions, in this shape:

> **Do you want development to chain automatically between chats?**
>
> - `off` — every chat ends with the hand-off written and the prompt ready to copy. You decide when it continues.
>
> Recommended value: on `Autonomy: automatic`, the highest of `start` / `prefill` this project's gates allow; otherwise `off`.
> - `prefill` — the next chat opens with the instruction already typed; you press Enter.
> - `start` — the next chat opens **and starts by itself**, without you touching anything.
>
> **If you choose `start`, that happens in the CLI, not in your editor.** It is the only verified way to automate the full cycle: the VS Code URI pre-fills and does not submit, and its handler accepts no parameter that changes this. Choosing `start` means development moves to command-line sessions.
>
> **And it means development advances with nobody watching.** Decide whether that is acceptable on this project before choosing it.

**One follow-up question, asked in the same breath and only when the answer is not `off`: which model should every chained chat run on?** Record it as `Chaining model:` on the card. It is a real question and not a default to fill in silently, because it is the difference between a chain that runs on the model the user thinks it runs on and one that quietly runs on something else at a different price — **a new `claude` process inherits nothing from the one that launched it**, so an unstated model is not "the same as now", it is "whatever the settings file says". Propose the model the user is working with in this session as the value, say plainly that it will be used at every link until they change the card, and record what they answer.

**The recommendation follows `Autonomy:`, it is not fixed.** On a project whose card says `Autonomy: automatic` the recommended value is the MAXIMUM tier the project's gates allow — `start` where the four requirements are met, `prefill` otherwise — because automatic mode means the work does not stop for a person who is not there, and a hand-off nobody opens is a stop. Outside automatic mode the recommendation is `off`. The gates never bend: a recommendation cannot promote `start` on a project that has not earned it, and the user can always answer `off`.

Two reasons the warning is text the user reads and not a footnote. **It changes the tool, not just a setting** — someone working in VS Code who picks `start` expecting their editor to do something gets terminal windows instead, and that belongs before the choice, not after. **And it changes who supervises** — `off` and `prefill` keep a person between links; `start` removes the only participant who can notice that the chain has forked.

Whatever the value:

- **Chaining fires only on a clean hand-off** — but `blocked` describes the SESSION, not an item in it. A "When to stop and ask" row (SKILL.md), a failed test point, an open Design Request, or the three-attempt rule blocks the ITEM it fired on, and the hand-off is `blocked` only when that leaves the queue with nothing independent to do. Parked items with buildable work still in the queue are a `clean` hand-off that CARRIES them: the next session picks up the work and the parked list travels with it, in the hand-off's own open-items section, so nothing is lost by not stopping. Writing `blocked` because something is blocked — rather than because everything is — is the same error the item/session distinction exists to prevent, and here it costs the whole next session: nothing is opened, and the user comes back to a chain that stopped at a link that had somewhere to go. When the hand-off IS genuinely blocked, it says so with the reason and nothing is opened: chaining a blocked state hands the next session a problem dressed as an instruction, and the next session cannot tell the difference.
- **Opening a window the user did not ask for takes over their screen**, so it is never done silently and never on `off`.
- **An open action is a local convenience only.** It needs the tool running on the same machine as the repository, so it has no meaning in CI, in a cloud session, or anywhere the repo is not open locally. Where it does not apply, the file alone does the whole job — chaining is a convenience on top of the file, never a replacement for it.

#### Whenever a chat cannot be opened, the prompt is shown to be copied (UNBREAKABLE)

Chaining fails for ordinary reasons — the card says `off`, the tool has no recorded action (the normal case), the tool is not running, the command is missing, the action does not fire, the hand-off is blocked. Every one of them ends the same way: **the full continuation prompt is printed in the conversation, ready to copy, with the one line saying to paste it into a new chat.** There is no path in which a session ends without the user holding either an opened chat or a copyable prompt.

This is why the file and the chat display are never traded against each other. Writing the file does not excuse skipping the prompt, chaining does not excuse skipping it either, and a failure to chain is not an error to report but a fallback to take — say in one line that the chat could not be opened, then show the prompt. A session that ends with "I could not open the next chat" and nothing else has stranded the user at exactly the moment the mechanism existed to help them.

#### Closing the current chat when a new one is launched (UNBREAKABLE)

When chaining DOES fire, the session that fired it is finished, and it says so as its last message — otherwise the user is left with two live chats and no idea which one is theirs. The closing message is short and states three things:

1. This chat is closed.
2. A continuation chat is being launched, and where the hand-off lives.
3. What is left for them to do: press Enter in the window that just opened (`prefill`), or nothing at all (`start`) — **and, under `start`, that if the single lane is already busy the new window will say so and print the prompt instead of continuing.** The closing session cannot know: the lock is taken by the ARRIVING session, after this one has finished. Promising an unconditional "nothing to do" is the one claim in this message that can be false, and the user is by definition not watching.

Nothing else — no summary of the sprint, which is already in `docs/PROGRESS.md` and in the file, and no work started after it.

**This closing message follows the language of the conversation, not the English default.** It is spoken TO the person, so it obeys SKILL.md's rule that the assistant always talks in the user's language; the English default governs what Keel *creates*, and `docs/continuation-prompt.md` — an artifact — stays in English like every other. Getting this backwards is a real and easy mistake: the file in Spanish and the goodbye in English is precisely the wrong way round.

For a Spanish-speaking user, that last message reads like: *"Chat cerrado. Lanzo el chat de continuación — el traspaso está en `docs/continuation-prompt.md`. Solo tienes que pulsar Enter en la ventana nueva."*

#### The tool registry — what each assistant may do

The chaining action is a property of the TOOL, not of Keel, so the script detects rather than assumes and probes at the moment it runs. Evidence is graded in three tiers, because "documented" and "verified" are not the same claim:

| Tool | Recognised by | Action | Evidence |
|---|---|---|---|
| Claude Code, VS Code extension | `CLAUDECODE=1` **and** `CLAUDE_CODE_ENTRYPOINT=claude-vscode` | `vscode://anthropic.claude-code/open?prompt=…` — pre-fills, does NOT submit → `prefill` | **VERIFIED** on macOS: new tab opened, box pre-filled, no session file written until Enter |
| Claude Code, CLI | `CLAUDECODE=1` **and** `CLAUDE_CODE_ENTRYPOINT` set to anything OTHER than `claude-vscode` (observed: `cli` when a person types the command, `sdk-cli` when another session launches it) | `osascript` driving Terminal.app on `cd '<ABSOLUTE repo root>' && claude --model <card's `Chaining model:`> '<prompt>'` — submits immediately; **the `cd` and the `--model` are both part of the action, not niceties** — a new process inherits neither the launcher's directory nor its model (see "The launch does not inherit the launcher's directory" and "nor its model" below) → `start` | **VERIFIED** on macOS: `sdk-cli` in Terminal.app, end to end in a scratch repo; `cli` in VS Code's integrated terminal |
| Cursor | Marker not verified | `cursor://anysphere.cursor-deeplink/prompt?text=…`; its documentation states deeplinks never trigger automatic execution → would be `prefill` | **DOCUMENTED, UNTESTED** — no row is active until someone runs it |
| Codex | Marker not verified | A positional prompt argument is documented; whether it submits or pre-fills is not | **DOCUMENTED, UNTESTED** |
| Gemini CLI | Marker not verified | The documented prompt flags are headless mode — run and exit, i.e. submitting, not pre-filling | **DOCUMENTED, UNTESTED** |
| GitHub Copilot, Windsurf | — | No documented mechanism for opening a chat with a prompt | **NONE FOUND** |
| Anything unidentified — a cloud session, a web or desktop chat, CI, an unknown tool | No marker matches | — | Print |

**Match one value positively; treat every other entrypoint as the CLI. Never exclude on `VSCODE_*`, and never enumerate the CLI's values.** Two drafts got this wrong the same way — by describing the environment that had happened to be measured rather than the property that matters.

The first required the CLI row to see zero `VSCODE_*`, which would have un-matched the CLI whenever it runs inside VS Code's integrated terminal, a shell that inherits the editor's variables. The second pinned the CLI row to `CLAUDE_CODE_ENTRYPOINT=sdk-cli`, the one value measured at the time — and then a plain `claude '<prompt>'` typed by a person turned out to report `cli`, so the row would have missed the most ordinary case there is. The entrypoint set belongs to the vendor, and a rule that lists its members ages the day they add one.

So the rule is asymmetric on purpose: **`claude-vscode` is the only value matched by name**, because it is the only one whose BEHAVIOUR differs — a URI handler that pre-fills and never submits. Everything else carrying `CLAUDECODE=1` is the CLI: it submits, and it takes its repository from the directory it is started in. That holds whichever label the vendor prints and whoever started the session, and it is safe in both directions — a future CLI entrypoint matches correctly, and if one ever appears that is NOT the CLI, containment and `Repo:` still refuse to let it work in the wrong place.

Measured on macOS, and worth reading twice because two of the four are counter-intuitive: the extension reports `claude-vscode` and sets **no** `TERM_PROGRAM` at all; VS Code's integrated terminal reports `cli` with `TERM_PROGRAM=vscode`; a session launched programmatically by another reports `sdk-cli`; Terminal.app sets `TERM_PROGRAM=Apple_Terminal`. So `TERM_PROGRAM=vscode` identifies the terminal PANEL, not the VS Code extension — the exact inversion of the first draft's guess. And `VSCODE_*` is not one family but two disjoint ones: the extension host carries `VSCODE_PID` / `VSCODE_IPC_HOOK` / `VSCODE_ESM_ENTRYPOINT`, the integrated terminal carries `VSCODE_GIT_ASKPASS_*` / `VSCODE_INJECTION`. Three surfaces, overlapping variables, one reliable discriminator.

**Only a VERIFIED row is ever acted on.** Documented-but-untested is not a permission: it is a lead, telling whoever verifies it where to start. Everything else prints, which costs the user one paste and never fails silently.

Two properties make this safe to extend. **An unrecognised tool is never a failure**, it is the print row. And **a tool is promoted to VERIFIED only from an observation on a real machine** — the exact marker, the exact command, and what it actually did (pre-filled or submitted) — never from a plausible-looking URI scheme or an environment variable someone assumed exists. That second rule was written after being broken here: this table's first version identified the VS Code surface by `TERM_PROGRAM=vscode`, which is NOT set there; the real discriminator is `CLAUDE_CODE_ENTRYPOINT`. The guess failed safe, into the print row, but it was a guess, and guessing about a tool nobody is watching produces a close-out that reports a chat as opened when nothing opened.

Adding a tool is therefore a small, ordinary contribution: verify it, promote the row, record the D-entry. Removing one is the same in reverse — if a vendor changes its scheme, the row drops back rather than staying wrong.

#### `scripts/keel-continue`

Generated at the Phase 5 scaffold on projects whose card is not `Chaining: off`. It writes nothing and decides nothing: it detects the tool, looks up its row, and either fires the recorded action or prints. Keeping it that thin is what keeps the mechanism testable without any editor at all — the hand-off is verified by reading the file, not by watching a window appear. One script serves every tool on the project; there is no per-tool script and no per-tool branch in the skill.

The contract it must satisfy, whatever language it is written in:

1. Resolve `REPO_ROOT` (`git rev-parse --show-toplevel`) and build the ABSOLUTE hand-off path from it. Never emit a relative path.
2. **Verify before firing**, by running `scripts/keel-handoff-verify` — not by composing git commands. A `VERDICT: STOP` → print, do not chain. Firing first and verifying afterwards means the next session discovers it must stop only after it has launched and spent context, which is the wrong order — and under `start` there is no human in between to notice.
3. A missing file, an unreadable or malformed header (treat it exactly like a missing file — a header that cannot be parsed cannot be trusted), or a `Handover:` that is not `clean` → **print the reason AND the prompt itself, marked as a blocked hand-off, and exit 0.** The prompt rule admits no exception: "whenever a chat cannot be opened, for ANY reason, the prompt is printed" includes this one. Refusing to chain and refusing to print are different things, and only the first is intended.
4. Detect the tool by `CLAUDE_CODE_ENTRYPOINT` (or the equivalent marker recorded for that tool), matching `claude-vscode` by name and treating every other value as the CLI — never by enumerating the CLI's values, which the vendor extends. No match, or a match whose row is not VERIFIED → print and exit 0. This is a success, not a failure.
5. A VERIFIED row whose action tier exceeds the card's `Chaining:` value → downgrade to what the card allows; never upgrade. **If the row has no action at the resulting tier, print** — downgrading never means substituting another tier's action. (The CLI row knows only `start`; on a card that says `prefill`, it prints.)
5a. **Before firing a `start` action, re-check `command -v claude` live — never trust the Phase 1 preflight's recorded answer.** The card only proves the CLI was on PATH the day it was asked; PATH is a property of the shell the script happens to run in, and it changes between sessions, between terminals, and across a reinstall. Absent → print the prompt and say so by name, rather than firing `osascript` on a command that will fail inside the new Terminal window with nobody there to read the error. This is the same reasoning as re-detecting the tool tier on every run (point 4) applied to the one dependency Phase 1 can only ever have checked once.
5b. **Pass `--model <card's `Chaining model:`>` on every `start` fire — never a bare `claude '<prompt>'`.** The launched process inherits nothing from this one, so an omitted flag is not "keep the current model", it is "resolve from settings" — and the result is a chain that works perfectly, on a model nobody chose, at a capability and a price nobody agreed to, and says nothing about it. Card line missing or `n/a` on a chaining project → print and name the absent line, rather than firing a launch whose model is a guess. **Never substitute the launching session's model for the card's value:** the card is the recorded decision; the session's model is an accident of how the user happened to start it.
6. **Claim the launch receipt atomically (`mkdir`), write this session's PID into it, and fire ONCE.** Receipt already present → this hand-off was already launched: print the prompt, exit 0, fire nothing. The PID goes in because the arriving session needs to recognise its own launcher (the baton, in "The single-lane lock"); it is written immediately after the claim, before firing, since a launcher that fires first and records afterwards can be dead before it records. On a non-zero exit, or on any uncertainty about whether a window appeared, fall back to printing — **never to firing again** (see "One launch per hand-off").
6a. **Never build the Terminal command as an interpolated string. Write it to a real, executable script file (shebang + `chmod +x`) and have `do script` execute that file BY PATH.** `do script "<absolute path to a script file>"` needs no nested quoting in any layer — the string handed to Terminal is a bare path. An inline string built by embedding one shell command inside another inside an AppleScript string literal stacks three independent quoting dialects (the generating shell, AppleScript's string literal, the shell Terminal spawns to run what it receives) that do not compose safely, and a mismatch fails **silently**: `osascript` still exits 0 and a window still opens, but the new shell receives the literal, un-executed text instead of running the intended command. This is not achievable "carefully" with more escaping; it requires not nesting the layers at all. Measured, twice, on a real close-out (see `docs/keel-continue-launch-postmortem.md` if a project has one) — the interpolated form typed the raw multi-line prompt into the shell instead of running it.
When that script file is created with `mktemp`, use a template with the `X` run as the **last characters and no suffix after it** (`mktemp "$TMPDIR/keel-continue-launch.XXXXXX"`, never `...XXXXXX.sh`) — the launch script needs no file extension to run; it already has a shebang and is `chmod +x`'d. BSD/macOS `mktemp` (the vendor-supplied one on macOS, no `--suffix` flag) does not recognise a literal suffix after the `X` run as a pattern at all — given one, it silently creates the literal, unsubstituted filename. The FIRST call succeeds, because nothing yet exists at that literal path; the SECOND call to the same template collides with the file the first one left and fails with `mkstemp failed: File exists`. A single test run will not catch this trap.
6b. **Never pass the hand-off file's raw content as `claude`'s CLI argument.** Its documented format ("The continuation file") opens with a `---` freshness header, and `claude`'s own argument parser reads a leading `---` as an unrecognized option and exits (`error: unknown option '---'`) before the content is ever read as prompt text — regardless of how correctly the argument was quoted at the shell level, because this failure is inside the target program's own parser, downstream of every shell-level quoting layer. Pass a short instruction that tells `claude` to read the file itself instead: `claude "Lee <hand-off path> y continua"` (or the equivalent in the conversation's language) — simpler, and the instruction text never starts with `-`.
7. **Hand the lane back IMMEDIATELY BEFORE firing**, by running `scripts/keel-handoff-verify --release` — which frees it only if the calling session is the recorded owner. This is not the script taking the lane (it never does that, point 9): it is the closing session giving back what it already held, at the only moment it still can. Order is the whole of it — the launched window checks the lane within seconds of opening, so a release that happens after the fire is a race the chain loses, and losing it looks exactly like the lane working correctly.
8. Exit 0 in every path that leaves the user with either an opened chat or a printed prompt. Exit non-zero only when it could do neither. **A `start` action's own exit code proves a window opened, not that the intended command ran inside it** — `osascript` exits 0 for a window that received a broken command exactly as readily as for one that ran correctly (this is how 6a and 6b hid behind each other in the first place). Where the environment allows it (macOS: `tell application "Terminal" to get history of tab …`), verify by reading back the new window's actual terminal output — at least while developing or changing this script, not necessarily on every production run — since that is the only way to distinguish "launched" from "launched something broken that also exits 0."
9. **Two guards, two owners, and they solve different problems.** The single-lane LOCK is taken by the ARRIVING session and serialises who may WORK in the tree; `keel-continue` never takes it — it only releases the one its own session is holding, per point 7. The launch RECEIPT is taken by this script and serialises how many windows OPEN for one hand-off. Neither substitutes for the other: the lock alone lets four windows open and three excuse themselves, which is the failure this receipt exists to end.
10. Releasing the lane is the holder's job at its CLOSE-OUT — never deferred to "on exit", a moment a session never reaches (see "The single-lane lock") — and recovering an orphan (dead PID, or a live PID whose start time does not match) is the arriving session's, as is taking the baton from a live PID recorded as this hand-off's launcher. Taken, reported in one line, never queued behind a permission prompt.

Two details an implementer would otherwise have to invent, so they are fixed here: the prompt is **percent-encoded** when it goes into a URI (space → `%20`, `/` → `%2F`), using whatever the platform provides rather than a hand-rolled table; and "copy to the clipboard where available" means `pbcopy` (macOS), `wl-copy` or `xclip -selection clipboard` (Linux), `clip.exe` (Windows) — absent all of them, printing alone satisfies the contract.

**Two different jobs, two different commands, and conflating them is a real trap.** Firing a URI is `open` (macOS), `xdg-open` (Linux), `Start-Process` (Windows) — that serves `prefill`. Opening a VISIBLE CLI session is something else entirely: on macOS it is `osascript` driving Terminal.app, verified; on Linux (`gnome-terminal` / `konsole` / `xterm`) and on Windows it is NOT verified. Reaching for the plain open command to satisfy `start` ships the headless variant, which runs the next session correctly and opens no window at all — the user waits for a chat that does not exist, and nothing reports an error. Until those platforms are verified, `start` resolves only on macOS and prints everywhere else.

**The launch does not inherit the launcher's directory, and an earlier version of this file claimed it did (UNBREAKABLE).** The registry's CLI row used to read "inherits `cwd` so it cannot land in the wrong repository". That is true of a direct exec — `claude '<prompt>'` run as a child process of a session already standing in the repository — and it is **false of the action this skill actually verified for `start`**, because `osascript` asking Terminal.app to `do script` opens a NEW login shell, which starts in `$HOME` and inherits nothing from the process that asked. The two sentences sat six lines apart and contradicted each other, and the false one was the reassuring one.

**Nor does it inherit the launcher's MODEL, and this one is worse because it never announces itself.** A wrong directory produces a session that finds no repository and starts inventing — loud, eventually. A wrong model produces a session that does the work correctly, at a different capability and a different price, and says nothing at all. Claude Code's documented precedence is `/model` in-session, then `--model` at startup, then `ANTHROPIC_MODEL`, then the `model` field in settings; the flag and the variable **apply only to the session launched with them**, and a fresh process resolves the whole order from scratch. So a chain launched from an Opus session with a bare `claude '<prompt>'` runs on whatever the settings say — measured, repeatedly: every link came up on Sonnet while the session that launched it was on Opus. (Resumed sessions are the exception that proves it: `--resume` and `--continue` restore the model from the transcript, and a chain is not a resume.) **The `--model` therefore comes from the card's `Chaining model:` line**, not from the launching session and not from the environment: a project's chain runs on one model, chosen once, visible on the card, and identical at every link — rather than on whatever a user settings file happened to say the day the chain fired.

So the command handed to Terminal.app is `cd '<absolute repo root>' && claude --model '<Chaining model:>' '<prompt>'`, always, with the root taken from `git rev-parse --show-toplevel` and single-quoted. Omitting it does not fail: a session opens in the home directory, reads no hand-off, finds no repository, and starts inventing — and under `start` there is nobody watching it do so. Measured: a real close-out fired the launch without the `cd`, the window opened in `$HOME`, and the closing session then spent three further attempts trying to correct it (see the next rule for why those attempts were themselves the larger error). Note what did NOT save it — containment, `Repo:` and the absolute hand-off path are checks the ARRIVING session runs on a file it was told to read; a session that never reaches a hand-off at all runs none of them. The `cd` is the only thing standing between `start` and a chat working in the wrong directory.

**Quoting is the second reason this belongs in a generated script and not in a session's improvisation.** `osascript -e 'tell application "Terminal" to do script "…"'` nests three levels — the shell's quotes, AppleScript's, and the inner command's — around a payload that itself contains absolute paths and a prompt sentence. Hand-composed at close-out time it is a coin flip, and the same measured close-out got it wrong twice before writing the command to a file and running that instead. A script written once, tested once, with the prompt passed through a file rather than interpolated into three quoting layers, has this problem exactly zero times. This paragraph states the reasoning; **point 6a above is the enforceable version** — a numbered contract point a generator must satisfy, not a narrative aside a generator can read past. Point 6b covers the companion trap this same rewrite exposed: even a correctly quoted file-content argument can still be rejected by `claude`'s own parser if the file starts with `---`.

`scripts/keel-handoff-verify` is the sibling artifact, generated at the same scaffold: it runs the five mechanical checks and prints one line each plus `VERDICT: CONTINUE|STOP`. Portability is the same open question — the first prototype was BSD/macOS only (`stat -f`, `date -j`); the Linux/GNU forms (`stat -c`, `date -d`) and Windows are unwritten. A generated script that only runs on the machine that generated it is a check that cannot be run, so this is tracked as a real gap rather than a detail.

#### `scripts/keel-chain-check` — the chain is verified, never assumed (UNBREAKABLE)

**Everything above this line is a contract that nothing executes.** `keel-continue` has a thirteen-entry numbered contract, `start` has four gates, the permission mode, the `env.PATH`, the allow-list entries and the lane each have their own rule — and until this script existed, the first thing that ever checked any of it was a real close-out, at the end of a session, with the context nearly spent and nobody watching. That is the worst possible test harness, and it is the one the chain shipped with. Every field failure of the chain has the same shape: a piece of the contract was silently unmet for days, and the mechanism reported it exactly once, at the moment it was least recoverable.

This skill's own rule settles what to do about it: *a check that cannot be run is a promise, and this skill does not write promises as checks.* So the chaining contract becomes an executable, generated beside `keel-verify`, `keel-doctor` and `keel-handoff-verify`, with ONE allow-list entry — `Bash(./scripts/keel-chain-check:*)` — and one job: answer, before anything depends on it, whether this project can actually chain unattended right now.

It writes nothing to the repository, changes nothing, and asks nothing. Output is one line per row plus a final `VERDICT: READY` / `VERDICT: NOT READY` / `VERDICT: N/A (Chaining: off)`, and every `NOT READY` row names the exact fix rather than the symptom. `--json` for the assistant to read structured, like the doctor.

**Section A — structural rows, run in every mode, no window opened, under a second.** Twelve rows in total across A and B.

1. **The card parses.** `Chaining:` and `Autonomy:` are read from `docs/PROGRESS.md`. `Chaining: off` → `VERDICT: N/A` and exit 0 immediately; there is no chain to check and this is a success. Missing or unparsable card line → NOT READY, because a chain running on a value nobody can read is the failure mode this whole file exists to prevent.
2. **`scripts/keel-continue` exists and is executable** (`[ -x ]`). This is the single most common cause of a close-out that prints instead of chaining, and it is one `test` away from being known days earlier instead of at the close.
3. **`scripts/keel-handoff-verify` exists and is executable.** `keel-continue` point 2 runs it before firing; a chain whose verifier is absent cannot fire at all.
4. **Both allow-list entries are present in every capable tool's permission container** — `Bash(./scripts/keel-handoff-verify:*)` and `Bash(./scripts/keel-continue:*)`. A missing entry does not fail loudly: it opens a permission dialog at the one moment there is nobody to answer it, which is a chain that hangs rather than a chain that stops, and the two look identical from outside.
5. **Permission mode is `auto`** in the machine-local settings (`.claude/settings.local.json`, `permissions.defaultMode`), on a card that says `Autonomy: automatic`. In `manual` every composite command opens a dialog, so the chain fires correctly, the next window opens correctly, and the work stops on the first command anyway — the failure lands one link away from its cause, which is why it is so consistently misdiagnosed.
6. **`env.PATH` is sane**: written expanded and absolute (no `${PATH}`, no `$HOME`, no variable of any kind), it contains the system directories (`/usr/bin`, `/bin`, `/usr/sbin`, `/sbin`), and it contains the user's per-user installer directory. The three failures this row catches are all machine-wide and all silent (`references/keel-maintenance.md`, "Permission mode").
7. **`docs/continuation-prompt.md` is gitignored.** A committed hand-off is a courier that outlives its own truth.

**Section B — `start`-only rows, added when the card says `start`.**

8. **`claude` resolves live — and it resolves under the DECLARED `env.PATH`, not only under the current shell's.** Two different questions, and only the second one matches what the chain will actually experience: `keel-continue`'s point 5a re-check runs against the PATH the settings file declares. A machine where `command -v claude` succeeds interactively and fails under `env.PATH` is exactly the shape of the most misleading failure this mechanism can produce — "tool not installed," stated with authority, on the machine running it.
9. **The single-lane lock is reachable**: its directory exists outside the repository, in the user's state dir, and is writable. A lane that cannot be taken blocks the arriving session, not the launcher, so the launcher reports success.
10. **`keel-continue` does not carry any of the four measured launch bugs.** These are greppable properties of the generated script, not judgments, and each one is a real incident: the Terminal command is not built as an interpolated string (point 6a); no `mktemp` template carries a literal suffix after its `X` run (point 6a); `claude` is not handed `$(cat …)` of the hand-off (point 6b); `keel-handoff-verify` is invoked before the fire and `--release` immediately before it (points 2 and 7). A row here failing means the launcher will exit 0 while doing the wrong thing, which is the one failure no downstream check can catch.
10a. **The launcher passes `--model`, and the card says which** (contract point 5b). Two greppable facts: `scripts/keel-continue` builds its `claude` invocation with an explicit `--model`, and the card's `Chaining model:` line exists with a real value. Either missing → NOT READY. This is the quietest failure the chain has: a bare `claude '<prompt>'` opens a window that works perfectly, on whatever model the settings resolve to, at a capability and a price nobody chose — and nothing anywhere reports it, because from the launcher's side nothing went wrong. Measured: every link of a chain came up on Sonnet while the session launching it was on Opus.
11. **The proof has not gone stale — `Chain verified:` matches the script on disk.** The card carries a `Chain verified:` line recording the date, the tier proven, the Keel version that proved it, and the **checksum of `scripts/keel-continue` at the moment of the proof**. The script's current checksum is compared against it. They differ, or the line is absent → NOT READY, with one instruction: run `scripts/keel-chain-check --smoke`. This row is the load-bearing one. Every other row proves the pieces are present and shaped correctly; only this row answers whether the launcher has ever been *observed* to work, and it invalidates that answer the instant anybody edits the launcher. **A launcher that changed since it was last proven is an unproven launcher**, however careful the change looked.

**Section C — `--smoke`, the launch actually performed and read back.**

Rows 1-11 are static analysis — they read files and grep scripts. `--smoke` is the only thing in Keel that proves the launch RUNS, and it exists because point 8 of the `keel-continue` contract is true and unfixable by any amount of reading: *a `start` action's own exit code proves a window opened, not that the intended command ran inside it.* The four bugs of the v5.10.3 incident all exited 0.

What `--smoke` does, in order:

- Fires the recorded action for the detected tool, with a **harmless prompt that is not the hand-off** — a one-line instruction whose only job is to produce a recognisable marker in the new shell (`printf` of a nonce the checker generated). It never reads, never writes and never touches `docs/continuation-prompt.md`.
- **Uses a dedicated smoke namespace for the receipt and never the lane.** It does not claim the launch receipt of any real hand-off, does not take the single lane, and does not count against the circuit breaker. A test that consumes the mechanism it is testing is worse than no test.
- **Reads the new window's real terminal history back** and asserts the nonce is present — the only evidence that distinguishes "launched" from "launched something broken that also exits 0". On macOS: `tell application "Terminal" to get history of tab …`, matched by `tty`. Where the environment offers no read-back, the smoke test reports `INCONCLUSIVE` and says so — never `passed`, and never silently skipped: an unreadable result is a third state, not the good one.
- **Closes the window it opened.** A smoke test that leaves debris trains the user to ignore it.
- On success, writes the `Chain verified:` line onto the card with today's date, the tier, the Keel version and the launcher's checksum. On failure, writes nothing, prints what came back instead of the nonce, and leaves row 11 failing.

**When `--smoke` is mandatory** — three moments, and they are exhaustive:

- **At the Phase 5 scaffold**, the moment `scripts/keel-continue` is generated on a card that is not `off`. A launcher that has never launched is not installed, it is merely present — the same rule the scaffold already applies to the test drivers.
- **Whenever `scripts/keel-continue` is regenerated or edited**, by anyone, for any reason. Row 11 detects this whether or not the editor remembers.
- **Whenever `Chaining:` is raised a tier** (`off` → `prefill` → `start`), because the tiers do not share a command and a proven `prefill` says nothing about `start`.

It is NOT run at every sprint close. The close runs Section A+B, which is static and instant; the window-opening proof is checkpointed by checksum instead of repeated, because a smoke test on every close would open an extra window at exactly the moment the user is trying to walk away.

**Where the structural check runs — two gates, both mechanical.**

- **At session start, on any project whose card is not `Chaining: off`**, alongside `scripts/keel-doctor --check`, in the fixed reading order. `NOT READY` at the START of a session is a problem with hours left to fix it; the same fact discovered at the close is a problem with none. This is the whole point: the failure was never that the chain broke, it was that it broke where nothing could be done about it.
- **At the sprint close, immediately BEFORE `scripts/keel-continue` is invoked** (`references/phase-5-development.md` §5 step 11). A `NOT READY` here does not stop the close and does not stop the chain: the close-out still runs `keel-continue`, which still decides for itself, exactly as before. What changes is that the session **prints the failing rows with the hand-off** and, in automatic mode, sends them through the notification channel — so the person learns which row broke instead of finding a printed prompt and no explanation. **`keel-chain-check` never vetoes a fire.** It is a diagnostic, and adding a fifth entry to the closed list of four things that may stop a chain would re-open the exact judgment call v5.10.2 removed.

**And the reason it can be trusted to say READY: it is the same source as the contract.** The rows above are generated from the numbered `keel-continue` contract and the four `start` gates in this file — one row per requirement — so a requirement added here without a row is a release bug in the same way a manifest row missing its reference is. `scripts/keel-verify` checks that the script exists and that its row count matches.


## Fan-out over worktrees — who writes the state, and how a worker reports

A session may dispatch several workers into git worktrees to work on independent slices at once. Everything in this section was measured; it applies to any such fan-out, and none of it requires a second chat with a role (see "Designs measured and rejected" below).

### Dispatching a worker

One worktree and one branch per slice, then one process per worker, launched from the main tree's session after the sprint kickoff approved the slices:

```bash
git worktree add -q ../w<N> -b slice-<N>
mkdir -p ../w<N>/.claude && cp .claude/settings.local.json ../w<N>/.claude/   # see below — it does NOT travel
"$KEEL_CLI" --session-id <uuid> --model <model> -p --permission-mode auto \
  "$(cat ../slice-<N>.prompt)" > ../w<N>.log 2>&1 &
```

**`$KEEL_CLI` is resolved, never assumed.** The dispatch needs the assistant's own CLI on this machine, and the bare word `claude` is a probe rather than an answer — resolve it per the corroboration rule in `references/test-automation.md` ("Detection rules that are not obvious"), which covers both the shell whose `PATH` hides an installed binary and the binary that is present but cannot run. A session running under Claude Code already holds the answer in `CLAUDE_CODE_EXECPATH`, an absolute path that works with no `PATH` at all. If no working CLI can be resolved, the fan-out does not happen: say so and build the sprint's slices in this session, serially, which is a slower plan and not a degraded one.

**`--session-id <uuid>` assigns the id up front** instead of looking it up afterwards, so the dispatcher knows every worker's id before it starts. The log file is for post-mortem reading, never for detecting completion (see the report section below).

**`--permission-mode auto`, and NOT `bypassPermissions` (UNBREAKABLE).** An earlier version of this dispatch used `bypassPermissions` on the grounds that it is what lets an unattended worker finish. **That premise is false, and it was measured: `bypassPermissions` asks for confirmation EVERY time** — entering it is itself a gated act, so instead of removing prompts it guarantees one, and an unattended worker sits waiting for an answer nobody will give. It therefore breaks precisely the automation it was chosen to enable, which is the worst kind of wrong flag: it fails in the direction of looking like a hang rather than an error.

The safety argument points the same way, and would be sufficient on its own. `bypassPermissions` evaluates no permission rules at all, `deny` included. That put the skill in direct contradiction with itself: the session-start step writes a `deny` block precisely to keep `rm -rf /*`, `sudo *` and `curl * | sh` out of reach, and then the fan-out handed that exemption to the only sessions that are simultaneously **parallel, unattended, and writing to real branches** — the worst place in the whole skill to remove a barrier, and the one where nobody is watching to notice. `auto` keeps the worker moving through everything the allow-list covers and keeps the `deny` block enforced.

**The honest cost of that swap, stated rather than discovered:** `auto` is not a drop-in. A worker in `-p` mode that reaches an action the allow-list does not cover cannot be asked, so that call is refused and the slice may fail. That is the correct failure direction — a refused call surfaces in the worker's report and its log and is fixed by extending the allow-list, whereas an unattended `sudo` is not fixed by anything. So: if workers stall, **extend the project's allow-list; never go back to bypassing.** And the fan-out's other three preconditions stand unchanged, because they were never a substitute for this one: dispatched only from a session with a person in it, only over slices approved at the kickoff, only into worktrees of this repository.

**A worktree does NOT inherit the permission settings, and this is the part that silently undoes everything above.** `.claude/settings.local.json` is gitignored — that is what makes it machine-local — so `git worktree add` produces a clean checkout **without it**. A worker launched there falls back to user-level configuration: no project `deny` block, no project `env.PATH`, no project allow-list. The rule that was just enforced on the flag would be quietly absent in the directory. So the dispatch **copies the file into each worktree before launching**, as in the command above, and a dispatch that skips that step is not dispatching under the project's rules whatever flag it passes. Verify it landed: the file's absence is invisible at runtime and shows up only as a worker mysteriously blocked, or mysteriously unblocked.

### The living state is written by the session that owns the MAIN tree — and by nobody else

This **inverts** the rule that governs everywhere else in this file ("update state at the moment of change"), so it is recorded as a deliberate decision with its reason rather than left as an exception someone will treat as an oversight.

- **The session in the main tree writes `docs/PROGRESS.md`**, after each merge, as always.
- **A worker in a worktree never writes it.** Not a line. The prohibition goes in the worker's own prompt, in those words.

The measurement: with three worktrees where each worker touched its own code file AND `docs/PROGRESS.md`, the code merged clean every time and `PROGRESS.md` conflicted in **100% of merges — N−1 times for N workers**, and not on one line but on the whole structured block. With the workers writing only their own report path instead, three merges produced **zero conflicts** and `PROGRESS.md` was left intact for the main session to rewrite.

**`.gitattributes` with `merge=union` is not the fix and must not be reached for.** With two branches that only APPEND it works; a Keel `PROGRESS.md` is REWRITTEN — phase, version, position — and union merging then produces a clean merge and a corrupt file: two contradictory `**Fase actual:**`/`Phase:` lines, two `## Log` headings, and no conflict marker anywhere. A silent wrong answer is worse than a conflict.

### The worker's report — `docs/.keel/slices/<n>.json`

What a worker writes instead, committed on its own branch, one path per worker so two never touch the same file:

```json
{ "slice": "3", "status": "blocked", "branch": "slice-3", "commit": "4416bf5",
  "needs_user": "What should divide(a, b) do when b is 0?" }
```

`status` is `done` or `blocked`. A `blocked` report is **not merged**: the branch and its worktree stay untouched, the question goes to the user in the chat where a person actually is, and the main session records the block in `PROGRESS.md`. That escalation is the whole reason a fan-out is driven from a session with a human in it — a worker that invents an answer to a product question is the failure this prevents.

Two things the report deliberately is not. **Not stdout:** a `claude -p` worker writes nothing until it finishes, so a working worker and a dead one both show an empty log (measured: 0 lines while both were working). **Not the transcript:** it belongs to the process rather than to the project, and a transcript resumed after an interruption gains a fabricated `Continue from where you left off.` turn that nobody wrote.

### The close-out contract — this order, and the order is the point

Every worker prompt ends with these four steps in exactly this sequence:

1. `git add -A && git commit -m "slice <N>: …"`
2. Write `docs/.keel/slices/<N>.json` and commit it.
3. Signal completion **atomically**: `printf '<N> done\n' > <signal>.tmp && mv <signal>.tmp <signal>.done`.
4. Finish.

The signal comes LAST so that **an existing signal implies committed work, never the reverse**. It is written by rename because a rename cannot be observed half-written, which a direct `>` redirect can. The dispatching session waits on the signal file — one blocking call with a ceiling (`until [ -f <signal>.done ]; do sleep 5; done`), which costs one line of context however long it takes.

### The slice prompt is self-sufficient, and is not a continuation prompt

Each worker receives a complete prompt that starts with the ABSOLUTE path of ITS worktree, states that no other directory may be touched, forbids reading or writing `docs/PROGRESS.md`, and carries the task in full. It reads no state file. There is also a mechanical reason the hand-off cannot get confused with a slice prompt: `docs/continuation-prompt.md` is gitignored, so a fresh worktree does not contain one at all (measured). The party that needs a hand-off is the session that owns the main tree, never the workers.

**What needs serialising is the merge, not the slice.** Three worktrees give three different `git rev-parse --show-toplevel` values and therefore three legitimate lanes, exactly as the single-lane lock already intends. Since only the main session merges, the main tree's lane already covers the thing that must not happen twice at once; nothing about the lock changes for this.

### Seeing which sessions are live — `claude agents --json`

The supported way to enumerate live sessions, replacing any parsing of `*.jsonl` transcripts. It returns one object per session with `pid`, `cwd`, `kind`, `sessionId`, `name` and a status of `idle` or busy — enough to discover sessions, spot a dead one, and tell whether one is working. It needs no TTY and is scriptable.

Two caveats, both measured, both load-bearing:

- **`-p` (print) sessions do NOT appear** — only interactive and `--bg` ones. So it is not a completion detector for `-p` workers; the done-signal file is.
- **`--session-id <uuid>` lets the launcher assign the id up front**, so whoever dispatches a worker already knows its id without looking it up.

## Designs measured and rejected — do not re-propose

Each of these was built or probed on a real machine and failed for a reason that will not change by trying again. They are recorded so the next session finds the result before spending the round that produces it a second time.

- **A "chat director" — a second chat whose role is orchestrating worker chats. Abandoned as a design.** It works: a prototype ran three slices with three workers, merged without conflicts, wrote the state itself, and escalated a product question instead of inventing an answer. It still does not earn its scaffolding. Measured, it costs **≈7k tokens of context per slice in a toy project and 15–20k in a real one** (a `PROGRESS.md` of 4–18 KB read and rewritten every slice is what fills it, not the waiting loop — that is one Bash call returning one line however long it blocks), which degrades the director **between the 6th and the 9th slice**. It has no cost accounting, no cancellation and no concurrency cap, all to obtain parallelism that native subagents and workflows already provide with all three. Its one genuine advantage — a chat with a person in it, which can be asked a question and can answer — is obtained by something far smaller: **one ordinary Keel session that, in a single turn, dispatches N workers into worktrees, waits for their signals and merges**, exactly as this section describes. The chat where the person is, is the chat you are already working in.
- **Delivering a message into a live session with `claude --resume`.** There is no mailbox. `--resume` starts a NEW process that reads the transcript from disk and writes to the same file: against an idle session the target's window sees nothing, and against a session mid-turn the transcript FORKS, a `Continue from where you left off.` / `No response requested.` pair that nobody wrote is fabricated, and the message is **silently lost** from the resumable history. It is also scoped to the current directory's slug, so a worker in a worktree could not reach a session in the main tree even if the mechanism worked. Workers report through their file, and nothing else.
- **Closing another session's window from a script.** Measured on macOS with Terminal.app: `close` takes **40–78 seconds** with no confirmation and no error either way, so the caller cannot know whether it happened without polling; it is a hard kill that runs **no cleanup hooks at all** (three signal traps were installed and none fired, and the log file was never created); and because the holder can therefore never release its lane, an orphaned lock is guaranteed rather than exceptional. Killing the child instead leaves the window open with an idle shell. Opening an unrequested window was already placed behind the user's decision; closing one is more destructive and its mechanics are worse. **Do not do it, not even opt-in.** The defensible version, if it is ever wanted, is `kill -TERM` on a worker whose done-signal already exists — the commit is guaranteed by the close-out order — leaving the window open; even that needs an explicit lane release, which is specified for the arriving session and not for a third party.

## Context & cache discipline (how every session works)

These rules exist so sessions are cheap, deterministic, and cache-friendly. Follow them literally.

1. **Fixed session-start reading order, and `docs/continuation-prompt.md` comes FIRST.** Before the state files, check whether that file exists — it is the freshest pointer in the project and the cheapest read there is, and checking it is what makes a bare "continue" enough to restart the work. If it exists, run `scripts/keel-handoff-verify` (never compose those checks inline) and act on the verdict: **`CONTINUE`** → it names the exact position and the next action, so the session starts there instead of re-deriving it; **`STOP`** → the file is discarded as a courier and the session resumes from the committed state files instead, saying in one line that it did and why — a stale or foreign hand-off must never paralyse a session, it must only lose its authority. If the file is absent, that is ordinary (it is gitignored, so a fresh clone has none) and the order below simply proceeds. **The hand-off is a courier, never an authority:** where it and the committed state disagree, `docs/PROGRESS.md` wins and the divergence is stated. Then read in this exact order and nothing more: `docs/PROGRESS.md` → `docs/decisions.md` → `docs/lessons-learned.md` → the current phase's reference file → only the inputs PROGRESS.md names for the current position. On a runnable project, the first test point of the session also runs `scripts/keel-doctor --check` and boots the playground from `docs/playground.md` (the freshness stamp) — a session that assumes the environment still works is a session whose green results mean nothing. **And on any project whose card is not `Chaining: off`, the same moment runs `scripts/keel-chain-check`** — for the same reason and against the other mechanism the session will depend on without looking at it again: the chain is verified at the START of the session, where a `NOT READY` row still has hours in which to be fixed, instead of at the close, where it has none. A `NOT READY` here is reported with its rows and fixed as ordinary work; it never blocks the session's actual task. The same order every session keeps context predictable and maximizes prompt-cache reuse. While reading PROGRESS.md, compare the card's `Keel baseline:` with the running Keel version — if it is older or missing, offer the post-update reconciliation (see below) before continuing. In the same pass, re-verify the card's `Durability:` line against reality — two cheap commands (`git rev-parse --git-dir`, `git remote -v`) plus the project's absolute path; a card that claims a remote the repo no longer has, or a `NONE` that is now covered, is corrected on the spot and the user is told in one line (SKILL.md "Work never lives only on this machine"). A recorded `NONE — accepted risk` is not re-litigated.
2. **Read each static reference once per session.** Phase references and templates do not change mid-session — never re-read a file already loaded in this conversation; rely on the copy in context. Single exception: immediately after a Keel update, the copies in context belong to the old version — re-read the new `SKILL.md` and the current phase's reference (see "Post-update reconciliation").
3. **Orient by state, not by scanning code.** The project's shape lives in `docs/03-technical-plan.md` (code map, conventions), `docs/architecture.md` (once it exists), and `docs/api/INDEX.md`. A session that needs to know "where is X / does Y exist" consults these first, then opens the one specific file it needs. Tree-wide code exploration is a signal that the state files are incomplete — fix the state files, don't normalize the scanning.
4. **Surgical code reads.** When code must be read, read the specific file/function the state points to — not whole directories "for context".
5. **Small living state, stable artifacts.** Only PROGRESS.md, decisions.md, lessons-learned.md, the DR register, INDEX.md, sprint files, 05-test-points.md, issues.md, token-ledger.md, and playground.md change routinely. Specs, flows, design handoff, and BUILD-SPEC are amended only deliberately (a recorded decision, a Design Request, or a scope change per "Scope changes" below), because every rewrite invalidates what other sessions and caches rely on.
6. **Reference paths, don't duplicate content.** When producing or discussing a large artifact, write it to its file and refer to the path. Do not paste large file bodies into the conversation when a path reference serves.
7. **Keep PROGRESS.md ~one page.** History goes to sprint files and `docs/old/`; PROGRESS.md holds only the present.
8. **Update state at the moment of change.** After each phase step, decision, slice, test point, or DR: update the relevant state file immediately. State updated "later" is state lost when the chat dies.

## Scope changes (a feature or requirement changes mid-project)

Scope moves mid-project — a feature is added, dropped, or redefined after its spec closed. What never happens: code first and artifacts later, or a silent rewrite that leaves the record contradicting the build. The loop, in this order:

1. **`docs/decisions.md` first.** Append the D-entry: what changed, why, decided by whom. No artifact is amended before the decision is on record.
2. **Amend the spec artifacts.** `docs/01-discovery.md` (feature table) and `docs/02-functional-spec.md` plus its flow files — visible amendments, never silent rewrites.
3. **If UI is affected: a DELTA brief to Design.** Same templates as Phase 3, scoped to the change; the returned delivery passes the Phase 4 Step 1 audit like any delivery, then lands as a delta in `docs/BUILD-SPEC.md`.
4. **Re-plan the open sprint** (`docs/sprints/`): re-cut the slices the change invalidates; the sprint file records what moved and why.
5. **Recompute the estimate** — and the client budget when one exists — per `references/estimation-budget.md`.
6. **`docs/PROGRESS.md` reflects the new scope** — updated at the moment of change, as always.

Boundary: Design Requests exist for GAPS in an existing handoff — a scope change is never smuggled through a DR.

## Portability across environments — the lock and the embedded skill

A Keel project moves between environments and assistants: the Claude app, Cowork, Claude Code in VS Code / terminal, OpenAI Codex, GitHub Copilot, Cursor, Gemini CLI, Windsurf, sometimes other AIs entirely. The state files make the project resumable; this section makes the WORKFLOW itself travel with the repo, so whatever opens the project is bound to Keel — even if the Keel skill is not installed there.

Two mechanisms, created at Phase 1 step 0a (and during adoption step 2):

### 1. The lock — `CLAUDE.md` + `AGENTS.md` (mandatory, both)

The project root carries the Keel block below in TWO files, always: `CLAUDE.md` (Claude Code, Cowork and the Claude app read it automatically) and `AGENTS.md` (the open agent-instructions standard — Codex, Copilot, Cursor, Windsurf, opencode, Zed, Warp, JetBrains Junie, Kiro, Cline and most other tools read it automatically). That is what makes this the lock: it is read before anything else, in every environment, by every session, without depending on any skill being installed. Both files carry the SAME block — created together, refreshed together, stamped together. If either file already exists, insert the block between its delimiters without touching the rest; the delimiters make it safely updatable later.

One tool needs a third step: **Gemini CLI reads `GEMINI.md`, not `AGENTS.md`, by default.** If the user works with Gemini CLI, ask once and record the pick: mirror the same block in `GEMINI.md` (a third copy of the lock, refreshed with the others), or commit a `.gemini/settings.json` whose `context.fileName` includes `AGENTS.md` (no third copy to maintain). Either satisfies the lock.

```
<!-- KEEL:BEGIN — v5.13.0 do not remove: binds every AI/session in this repo to the Keel workflow -->
# Keel protocol (mandatory for ANY assistant working in this repository)

This project is governed by the Keel workflow. Before reading code or changing ANYTHING:

1. Read the FULL Keel `SKILL.md` FIRST, before anything else in this repository —
   from the installed `keel` skill if present, otherwise from the embedded copy
   at `.claude/skills/keel/SKILL.md` or `.agents/skills/keel/SKILL.md` — and
   follow it literally, starting by
   executing its maintenance block (`references/keel-maintenance.md` — update
   check, lock freshness). Remembering the protocol from an earlier chat, or
   having this lock in context, does NOT count as having read it: a session that
   works without having read SKILL.md in this session is out of protocol. If the
   update check installs a newer Keel, re-read the new `SKILL.md` and run its
   post-update reconciliation (defined in Keel's `references/project-state.md`)
   BEFORE normal work continues, so this project is brought up to date with
   everything the new version requires — new files or directories, new
   project-card lines, this very lock block, questions never asked here.
2. Then check `docs/continuation-prompt.md` BEFORE the state files — it is the
   freshest pointer in this project, and it is what lets a bare "continue" start
   the work with no recap. If it exists, run `scripts/keel-handoff-verify` and
   obey the verdict: CONTINUE starts at the position it names; STOP discards it
   as a courier and you resume from the committed state instead, saying so in
   one line — a stale or foreign hand-off loses its authority, it never stops
   the session. Absent is ordinary (it is gitignored, so a fresh clone has
   none). It is a courier and never an authority: where it and the committed
   state disagree, `docs/PROGRESS.md` wins. Then read
   `docs/PROGRESS.md` (project card, current position, next action),
   `docs/decisions.md` (decisions are NEVER re-opened on your initiative), and
   `docs/lessons-learned.md` (recorded mistakes are never repeated), plus the
   phase reference SKILL.md names for the current phase. If the project card's
   `Keel baseline:` is older than the running Keel (or missing), offer the
   post-update reconciliation before continuing.
3. Follow the recorded specs and design exactly: no reinterpretation, no silent
   deviation, no "improving" recorded decisions. Anything undefined → ask the user.
   Design gaps → Design Request (Keel Phase 4). Never claim something that was not
   verified: the code map in `docs/03-technical-plan.md` is a TARGET tree, so a path
   not marked `[E]` is absent until a slice creates it, and a control, check or test
   is only described in the present tense once it is built and evidenced. A check
   whose inputs do not exist yet is "not yet applicable", naming what is missing —
   never "passed". Before changing anything, read the change map's row for that type
   of change: it lists every artifact that must be touched.
4. Update `docs/PROGRESS.md` and `docs/decisions.md` at the moment of every change.
   Commit at passed test points — never without first checking the staged files for
   confidential data (secrets, credentials, private keys, tokens, real personal or
   customer data). A finding STOPS the commit: warn the user file by file that
   pushing it is a serious security risk, and exclude it via `.gitignore` (already
   tracked: untrack it too; ever pushed: purge history AND rotate the credential)
   before committing anything. NEVER leave work uncommitted at the end of a block:
   commit to `develop` or to a work branch bound for it, and where this repository
   has only `main`/`master`, create `develop` first. If it has NO REMOTE, say so and
   offer to publish it — a local commit survives a bad edit, not a dead disk, and
   work that exists only on one machine is one accident from not existing at all.
5. NEVER end a session mid-work — and NEVER close a sprint, even if you carry on
   working — leaving the user with nothing current to continue from
   (UNBREAKABLE). A sprint close is where a person walks away, so the hand-off
   must already be on disk and CURRENT at that moment, whatever the autonomy or
   chaining settings say; if you keep working past it, rewrite the file as the
   work advances, because a hand-off pointing at an old commit fails its own
   verification and is worse than none. Produce the continuation prompt from the embedded skill's
   `references/project-state.md`, SHOW it in the conversation ready to copy, and
   WRITE it to `docs/continuation-prompt.md` with its freshness header
   (`Repo` / `Generated` / `Keel` / `Commit` / `Tree` / `Position` / `Handover`). Running low on
   context is when this is most likely to be skipped and most expensive to skip:
   do it BEFORE the session is exhausted, never as an afterthought. Reading one of
   those files obliges the reverse duty — check that its real path is INSIDE this
   session's `git rev-parse --show-toplevel`, then its `Repo`, `Commit`, `Tree` and
   timestamp against the repository you are actually in, and STOP rather than act on
   a stale hand-off OR on another checkout's: the filename is the same in every Keel
   project, and a worktree or second clone shares both repository and commit, so
   containment is the only check that separates them. Where the project card's `Chaining:` allows it and the hand-off
   is clean, and the tool you are running in has a VERIFIED action recorded, also
   chain the next chat — passing this repository's ABSOLUTE hand-off path — then
   close this one in one short message in the CONVERSATION's language. If a chat
   cannot be opened for ANY reason — including "this tool has no recorded action",
   which is the normal case — that is not an error to report: print the prompt to
   be copied. The FILE works in every tool and needs no integration; only the
   auto-open is tool-specific, and it is never guessed.
6. Work with execution discipline, whatever model or environment is running:
   - Batch independent tool calls in ONE parallel block; never run sequentially what
     does not depend on a previous result.
   - Delegate broad searches/scans to a subagent when the environment provides them;
     bring back conclusions, never file dumps — the main context stays clean.
   - The same batching rule governs delegation: independent READING verifiers at one
     gate, and one agent per independent unit (screen, locale, competitor), go out in
     ONE parallel block — with at most one EXECUTING verifier per environment running
     alongside them — and the gate is judged against their merged findings. Serial
     only when one check's input is another's output, when two executing agents would
     share one environment (playground, test machine, database, deployed origin), when
     an agent in the set can write (that one runs first, alone), or when concurrency
     is capped.
   - Do not narrate between tool calls ("now I will…"); accumulate findings and
     report once, at the end of the work block.
   - Locate before reading: search/grep first, then read only the relevant fragment.
     Never read whole files or directories "for context".
   - Edit surgically (exact-match edits on the changed lines); never rewrite a whole
     file to change one part.
   - Batch clarifying questions at the START of a work block; close every work block
     with an explicit verification step (diff, test, or re-read) before calling it
     done.

This block itself can be outdated: the version stamp on the `KEEL:BEGIN`
delimiter names the Keel that last wrote it. If that stamp differs from the
running Keel version (or is missing), refresh this whole block from the
canonical copy in Keel's `references/project-state.md` ("Portability") —
between the delimiters only, with the user's OK, restamped with the running
version. The stamp alone decides; no content comparison is needed.

If neither the skill nor the embedded copy is available: STOP and tell the user to
install Keel (or restore the embedded copy at `.claude/skills/keel/` /
`.agents/skills/keel/`) before continuing.
<!-- KEEL:END -->
```

**Version stamp and freshness.** The `KEEL:BEGIN` delimiter carries the version of the Keel that last wrote the block (`KEEL:BEGIN — vX.Y.Z do not remove: …`); every write and every refresh stamps it with the RUNNING Keel version — when inserting the canonical block above, replace its stamp with the running version if they differ. The check is stamp-only, by design: stamp equal to the running version → the block is current, nothing else to read; stamp different or missing (blocks written before v1.11.0 carry no stamp) → rewrite the block between the delimiters from this canonical copy, restamped — never a content comparison. Match delimiters by the `KEEL:BEGIN` prefix, never by exact text. The lock-freshness check in SKILL.md's maintenance block (`references/keel-maintenance.md`) runs this in every session; the refresh asks the user's OK (or rides the post-update reconciliation's batched plan). It applies to BOTH lock files — `CLAUDE.md` and `AGENTS.md` are refreshed together — and to the `GEMINI.md` mirror when the project keeps one. The canonical block above keeps its own stamp equal to the skill's current version as part of the skill's release hygiene — the repository's release linter checks it — so a literal copy never seeds a stale stamp.

### 2. The embedded skill copy (recommended — ask the user once)

Copy the installed skill into the repo in TWO trees: `.claude/skills/keel/` (Claude Code loads it automatically as a project-level skill; Cursor, Copilot/VS Code, Cline, opencode, Amp, Warp and Junie also discover this tree) and `.agents/skills/keel/` (the open Agent Skills discovery convention — Codex, Cursor, Gemini CLI, Zed, Warp, Amp, opencode and Windsurf discover it natively). Both trees are identical, byte for byte (SKILL.md + references/, verbatim). Consequences: virtually every tool loads Keel as a project skill on its own; any other environment reads it as plain files via the lock's step 1; the repo is self-sufficient — a collaborator or a future session needs nothing pre-installed. Ask the user once at creation (the pair adds ~300 KB of markdown to the repo; a user who wants only one tree may choose so — record which); record the choice in the project card.

Rules for the embedded copy:

- **Copy the WHOLE skill — every file, verified — never a partial copy.** Copy from the installed skill's own directory, file for file: `SKILL.md` AND the complete `references/` tree (every `phase-*.md`, every template, `project-state.md`, `adoption.md`, `accessibility.md`, and the entire `references/security/` folder), plus `CHANGELOG.md`, `LICENSE`, and `NOTICE`. A partial copy is the single most common failure here and it silently breaks the workflow in the target environment — a missing phase reference makes that phase unrunnable, so the skill never really reaches the other tool. This is therefore a **verified** operation, not fire-and-forget, applied to EACH embedded tree:
  1. **Copy everything at once.** Prefer a recursive copy of the entire `keel/` folder into the target tree (e.g. `cp -R`), not a hand-picked file list — hand-picking is how files get left behind.
  2. **Verify against the source manifest.** After copying, list what actually landed in the tree and compare it file-for-file against the source directory: same file set, nothing missing, nothing zero-bytes. `SKILL.md` must sit at the tree's root (`.claude/skills/keel/SKILL.md`, `.agents/skills/keel/SKILL.md` — not nested one level deeper), and every reference the source has must be present.
  3. **If anything is missing or wrong, retry the copy, then verify again.**
  4. **If it still fails after the retry, STOP and tell the user plainly** — name exactly which files did not arrive and why the copy could not complete from this environment — and ask them to move the `keel/` folder into place themselves. Never leave a half-copied skill in place as if it worked: an embedded skill that reaches other tools with files missing is a defect, not a partial success. Record the outcome (complete / user-completed) in the project card.
  If this environment cannot access the installed skill's files at all, do not reconstruct reference files from memory — tell the user to copy the `keel/` folder from the release into both trees manually, then verify as above once they have.
- **Sync by version, one direction, both trees together.** Each embedded copy's `SKILL.md` frontmatter carries its version. If the installed skill is newer than an embedded tree, update that tree (tell the user); if an embedded tree is newer than what's installed, tell the user to update their installed skill. The two trees must never diverge from each other — a sync that touches one touches both. Never hand-edit an embedded copy. A version sync is also a full-tree copy — apply the same verify → retry → tell-user protocol above so an update can't silently drop a file either.
- **It never ships.** `.claude/`, `.agents/`, `CLAUDE.md`, `AGENTS.md` (and `GEMINI.md` when kept) are repo-only: Phase 7 marks them `export-ignore` so they stay out of the distributable package.

Project card line: `Keel portability: [lock only / lock + embedded vX.Y.Z]`.

### 3. Native assistant configuration (optional)

Beyond the lock and the embedded skill, a project may carry native config for its accepted assistants — path-scoped rules, reviewer subagents, permission allow-lists, a confidential-data pre-commit gate (`.githooks/pre-commit`), and MCP registrations, generated by Keel from the project's own recorded decisions, one container per tool (`.claude/`, `.github/instructions/` + `.github/agents/`, `.cursor/`, `.gemini/`, `.windsurf/`, `.codex/`, nested context files). Each tool loads only its own — the lock remains the universal mechanism, and nothing critical to the workflow lives only there. Offered once at Phase 1 step 0a / adoption step 2; materialized at Phase 2 close and the Phase 5 scaffold; recorded in the project card (`Assistant config:` line, tools listed); covered by the same Phase 7 export-ignore. Full definition: `references/assistant-config.md`.

## Post-update reconciliation — after a Keel update, bring the PROJECT up to date

A Keel update changes the workflow; it does not automatically change the project. A project created (or last reconciled) under an older Keel may be missing what newer versions introduced: state files or directories that now exist, project-card lines that now exist, lock-block changes, questions a phase now asks that this project was never asked, new one-time verifications. This procedure closes that gap deliberately, on the record, without re-opening anything already decided.

### When it runs

- Immediately after the session-start update check (SKILL.md "Update check") replaces any copy, when the session is working inside a Keel project.
- On resume, when the project card's `Keel baseline:` is older than the running Keel version — or the line is missing (legacy project: treat the baseline as unknown and reconcile).

Never skip it silently. If the user defers it, record `Reconciliation pending vX → vY` in PROGRESS.md open items so every later session re-offers it.

### The procedure

1. **Re-read the governing files from the NEW copy.** After an update, the `SKILL.md` and the current phase's reference in context belong to the old version — re-read both, and read the new `MANIFEST.md` (the parity manifest): its Table 2 names every skill file changed since the project's baseline (the exact re-read list), its Table 1 drives step 3's parity check, and its Table 3 is the per-version action list — the concrete actions to apply, so the reconciliation applies a delta instead of interpreting the changelog. This is the single exception to the read-once rule (context & cache discipline, rule 2).
2. **Diff the versions via the changelog.** Read every new `CHANGELOG.md` entry after the baseline version, oldest → newest. The changelog is written to make this cheap — never re-read every reference to find what changed.
3. **Extract what touches the PROJECT, not only the assistant's behavior.** From each entry: files/directories the project should now have; project-card lines that now exist; changes to the lock block (between its `KEEL:BEGIN/END` delimiters); questions a phase now asks that were never asked here; new one-time verifications or gates. Behavior-only changes need nothing — they apply by themselves from the new references.

   **Then run the conformance sweep — mechanically, from the manifest, not from memory (BLOCKING).** `MANIFEST.md` Table 1 is the ABSOLUTE parity check: walk EVERY row, decide whether it applies at this project's position under its recorded conditions, and give it a state. `MANIFEST.md` Table 3 adds the per-version action list for every version newer than the baseline — each action is a row too. Write the result to `docs/keel-conformance.md` (create it if this project predates it): one line per applicable requirement with exactly one state — `present` (and where), `missing`, `declined` (with its `docs/decisions.md` entry), or `n/a` (with the condition that excludes it). A row with no state is an unfinished sweep, and an unfinished sweep is not a reconciliation.

   This exists because the failure mode is specific and repeated: an update is announced, part of the delta is applied, the rest is quietly not, and nobody notices until the user asks why something is missing. Deriving the list from the manifest instead of from what the session recalls makes that impossible — the assistant cannot forget a row it is reading off a table.
4. **Present ONE batched catch-up plan — containing EVERY `missing` row, without curation.** What would be created or refreshed, which new questions need answers, what the new version requires versus what is optional, each with its one-line cost. The user approves, trims, or defers, row by row. Optional mechanisms stay optional: reconciliation asks their never-asked question (e.g. the assistant config package for a project older than v1.10.0) — it never force-installs. But **the assistant never decides on the user's behalf that a row is not worth mentioning**: applying is the user's choice, proposing is not optional. Anything the user declines becomes a `declined` row with its D-entry, so a refusal is a decision on the record and a gap can never be mistaken for one.
5. **Apply.** Refresh the lock block between its delimiters (user OK — the existing safely-updatable mechanism); create missing files/directories from their templates; add new project-card lines without touching the rest; ask the batched questions and record their D-entries; run new one-time verifications where they apply.
6. **Record and report.** One D-entry — `Keel vX → vY reconciliation: applied …; declined …` — update `Keel baseline:` to the running version, save the finished `docs/keel-conformance.md`, and update PROGRESS.md at the moment, as always. Then **report the sweep to the user in full**: applied / declined / not applicable, one line each, with the totals. A reconciliation reported as "done" without that table is a claim, and this skill does not accept claims.

### Rules

- **Nothing already decided is re-opened.** Reconciliation adds what the new version introduces. If something new conflicts with a recorded decision, surface it — the recorded decision wins until the user explicitly reverses it (a new D-entry).
- **No phase is re-run.** Completed phases stay completed; new questions are asked standalone and recorded, never by replaying the phase.
- **It never blocks urgent work.** Deferring is legitimate — but it is recorded as pending, never forgotten.
- **`Keel baseline:` advances ONLY by completing a reconciliation** (or is stamped at creation — Phase 1 step 0a / adoption step 2 — with the running version). A skill update alone never advances it: an advanced baseline over an unapplied catch-up would hide exactly the gap this mechanism exists to close.

## Archiving (`docs/old/`) — what moves, what never moves

At each sprint close (Phase 5) move to `docs/old/sprint-<N>/` only documents that are finished AND no longer consulted: closed sprint files, resolved one-off scratch documents, superseded drafts. Move — never delete.

These NEVER move while the project is alive: `PROGRESS.md`, `decisions.md`, `lessons-learned.md`, `issues.md` (old resolved entries may move to `docs/old/issues-archive.md`, the file itself never), `estimate.md`, `budget.md`, `00-competitive-landscape.md`, `01-discovery.md`, `02-functional-spec.md`, `03-technical-plan.md`, `05-test-points.md`, `BUILD-SPEC.md`, `flows/`, `design/` (brief, handoff, DR register), `api/`, `reference/`, the current sprint file.

## Definition of done (this reference)

- `docs/PROGRESS.md`, `docs/decisions.md`, `docs/lessons-learned.md` exist from Phase 1 and match the templates.
- PROGRESS.md reflects reality at all times: correct phase status, executable "Next action", complete open items.
- Every decision that shapes the project has a D-entry; every solved failure has an L-entry.
- Every Design Request exists as a numbered file with current status.
- If forge issues were ever accessed: `docs/issues.md` exists, its inventory reflects the forge, every worked issue has its entry (diagnosis, resolution, changes, verification, pending), and — on the after-sprint duty — its `Last inbound sweep:` line is never older than the card's `Issue sweep interval:` while the project has an open sprint.
- From Phase 5: `docs/api/INDEX.md` exists and matches the docs; sprint files follow the template.
- Any session ending mid-work produced a continuation prompt — and so did every sprint close, whether or not the session stopped there, with `docs/continuation-prompt.md` left CURRENT rather than describing a commit the work has since moved past.
- Where work was fanned out over worktrees: only the main tree's session wrote `docs/PROGRESS.md`, every worker left its `docs/.keel/slices/<n>.json` report committed on its own branch, every done-signal was written after its commit, and no `blocked` report was merged.
- The project card carries `Keel baseline:`; a completed reconciliation updated it and left its D-entry; a deferred one is listed in PROGRESS.md open items.
- Any reconciliation read `MANIFEST.md`, ran the full conformance sweep (Table 1 parity plus Table 3's per-version delta) and left `docs/keel-conformance.md` complete — every applicable row `present`, `declined` with its D-entry, or `n/a` with its condition. Every `missing` row reached the batched plan and ended in a user decision; the sweep table was reported to the user in full.
