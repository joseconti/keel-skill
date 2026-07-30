Work in a scratch directory OUTSIDE any real project. Nothing here touches the
keel-skill repo.

## CONTEXT

Keel v5.3.2 is published. Two roadmap items from your own `VERIFICACION-v5.3.0.md`
report are going into v5.4.0, and **the skill will not be written until you have
found a formula that actually works.** Same arrangement as the chaining work:
iterate, fail, adjust, and explain the formula you land on.

**§4.4 — a CHAT DIRECTOR.** One long-lived chat that never touches code. It
maintains `docs/PROGRESS.md`, decides the next slice, and dispatches one resumable
chat per slice. Its only unique claim over native subagents is exactly that: a chat
a person can enter, read and correct mid-flight. A subagent is born, answers, dies.

**§4.5 — NATIVE WORKFLOWS for Keel's fan-out phases**, starting with the v5.0.0
conformance sweep.

Your own objection to §4.4 still stands and this round must either kill it or
answer it: native subagents and workflows already do parallel work better, with
cost accounting, cancellation and concurrency caps. If the director adds nothing
they do not, say so and recommend dropping it. **A negative result is a successful
result here.**

## ALREADY KNOWN — do not re-derive

Verified on this machine in earlier rounds:

- `claude "<prompt>"` submits immediately and inherits `cwd`.
- `CLAUDE_CODE_ENTRYPOINT` is `claude-vscode` (extension), `cli` (typed by a
  person), `sdk-cli` (launched by another session).
- The `vscode://` URI pre-fills, never submits, and accepts no folder/workspace
  parameter, so it lands in the ACTIVE window.
- Session transcripts live in `~/.claude/projects/<slug>/*.jsonl` and are parseable.
- `osascript` can open a VISIBLE CLI session on macOS. Linux/Windows unverified.
- A three-link chain produced FOUR live sessions in sixteen seconds, because the
  counter could not see launches still in flight.

Shipped since your report, and both change the picture:

- The **single-lane lock** exists, folded into `scripts/keel-handoff-verify`, taken
  by the ARRIVING session, keyed by the real path of `git rev-parse --show-toplevel`,
  living outside the repo.
- The **containment check** exists: a hand-off's real path must be inside the
  session's own `--show-toplevel`. This is what catches a worktree or second clone.

## TEST THIS FIRST — it may remove the director's worst blocker

Before building anything, spend five minutes on one probe.

The director should not poll or infer that a worker finished. The worker should
notify it. So: the director passes its OWN session id to each worker in the slice
prompt, and the worker's close-out ends by notifying it.

Find out whether `claude --resume <director-session-id> "<message>"` actually
delivers a turn into a **live** director session, and what happens if the director
is mid-turn when it arrives.

The handle is the SESSION ID, not the PID: a PID gets you signals and kills, and a
running session has no inbox a signal could reach.

**Why this goes first.** If notification works in flight, the director stops needing
a watch loop — and the watch loop is what your report identified as the third
missing piece, the one that fills the director's context until it can no longer
direct. If it works, the whole shape gets cheaper. If it does not, say so early,
because everything below is planned around polling instead.

Whatever the answer: the notification is **in addition** to an atomic done-signal
file (write temp, then rename — a rename cannot be read half-written), never
instead of it. A director that is busy, dead, or out of context drops the message,
and a worker's finished work must not become invisible when that happens. Establish
which of the two the director actually trusts, and when.

## THE HARD PROBLEM — name it before building

If each worker gets its own git worktree, each worker has its OWN
`docs/PROGRESS.md` on its own branch. Keel's rule is that `PROGRESS.md` is THE
single living state, updated at the moment of every change. Those two facts
contradict each other, and N divergent `PROGRESS.md` files merging back is not a
conflict anyone wants.

Two hypotheses. Try to break both:

1. **Workers never write `PROGRESS.md`.** They report back and the DIRECTOR writes
   it. That inverts a Keel rule, so if it is right it needs recording as a
   deliberate decision — and you should say what the worker writes instead (a
   status file? stdout? its transcript?).
2. **Workers do not consume continuation prompts at all.** The director hands each
   one a fresh, complete slice prompt. The DIRECTOR is the long-lived chat, so the
   director is what needs the hand-off. If this holds, the worktree-versus-
   containment worry from your own §4.5 point 2 never arises for workers.

## WHAT TO CRACK — §4.4

Build a real toy director with at least TWO workers and iterate until it works, or
until you can show it cannot.

1. **Isolation.** Does one worktree per worker hold up end to end? What happens at
   merge-back — who merges, and what conflicts appear in practice, not in theory?
2. **The lock under worktrees.** Separate worktrees are separate real paths, so they
   take DIFFERENT lanes and do not serialise. Is that correct here, or does parallel
   work on one branch need a different unit of serialisation? This is a design
   question, not only a measurement.
3. **The director's context.** Measure it: how much does the director burn per slice
   dispatched, and after how many slices does it stop being able to direct? Give
   numbers, not an impression. This decides whether the shape is viable at all.
4. **Completion detection.** Given the result of the probe above, what does the
   director actually rely on, and which is more robust when a worker dies mid-slice?
5. **Failure modes.** What happens when a worker fails, hangs, or hits a question
   only the user can answer? A director that cannot handle a worker needing input is
   not a director.
6. **Closing finished windows.** Can the director close a worker's window once that
   worker has signalled done? Establish by running it:
   - On macOS, does closing a Terminal window kill the `claude` child, and does
     killing the child leave an empty window? Cover both.
   - What a killed worker leaves behind, specifically the single lane: a worker
     killed while holding it leaves a lock with a dead PID. Does the worker release
     the lane before exiting, or does the director clean it after? Closing windows
     turns the stale-lock case from an exception into the normal path.
   - Whether anything is actually lost. Transcripts persist and `--resume` exists,
     so state the real cost rather than assuming it is free.
   - Clean exit requested first, force only on no answer. Never kill a worker that
     might be mid-write to `PROGRESS.md` or mid-commit: that leaves a half-written
     state file or a stray `.git/index.lock`, a failure this project has already
     paid for once.

   Then recommend whether closing should happen at all, and if so whether it must be
   opt-in. Opening an unrequested window was gated behind the project card in
   v5.3.0; closing one is more destructive than opening one.

## WHAT TO CRACK — §4.5

Lower risk, and possibly mostly writable already.

1. Run a real workflow over a Keel project and check whether structured output
   (`schema`) fills `docs/keel-conformance.md` with NO post-processing. That was
   your own stated precondition.
2. Does `isolation: 'worktree'` interact badly with anything Keel now does —
   specifically, does a workflow agent ever end up reading a
   `docs/continuation-prompt.md`, and does the containment check fire correctly if
   it does?
3. Availability: confirm the tool needs explicit opt-in and may be absent. Keel
   cannot depend on it without an inline fallback, exactly as it already does for
   subagents. State what that fallback must be.
4. Which of Keel's existing fan-out gates map cleanly onto it and which do not.
   v5.2.0 already describes the fan-out in prose — the question is which parts
   become deterministic code and which must stay judgment.

## HARD RULES

1. Do NOT edit any file in the keel-skill repo. Do NOT change any version. Do NOT
   commit, tag or push anything.
2. Everything in a scratch directory outside real projects.
3. Use `git --no-optional-locks` for read-only git commands. The Cowork bridge
   cannot delete files, so a stray `.git/index.lock` blocks the user's repo. This
   already happened and cost him time.
4. Evidence from commands you ran, with real output. Never fill a gap with a
   plausible mechanism. "unverified" is an acceptable answer; an invented one is not.
5. Iterate. Fail, adjust, try again. That is the point of this round.

## DELIVERABLE — a report in Spanish

1. **The `--resume` probe result** first, and what it changes.
2. **The formula**, if you found one: exact commands, file layout, who writes what,
   and the real division of labour between director and workers.
3. **The dead ends**, with why each failed. These matter as much as the formula —
   they are what stops anyone retrying them.
4. **The director's context numbers.** Per slice, and the slice count at which it
   degrades.
5. **Your verdict on §4.4**, and it is allowed to be negative: does the director
   earn its complexity against native subagents and workflows, given that its only
   unique claim is a chat a person can enter?
6. **§4.5 findings**, and specifically whether it is writable into the skill now or
   needs another round.
7. **Anything you would need Keel to change** for either to work — as a proposal,
   not applied.
