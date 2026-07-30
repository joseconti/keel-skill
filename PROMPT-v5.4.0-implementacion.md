Work in `/Users/joseconti/Documents/GitHub/keel-skill`. You are IMPLEMENTING v5.4.0.

## AUTHORISATION

Keel's version policy is UNBREAKABLE and requires the user's explicit instruction.
This prompt is that instruction: **bump to 5.4.0**, in all four places (SKILL.md
frontmatter, SKILL.md heading, MANIFEST.md header, README.md version line), add the
CHANGELOG section, the MANIFEST Table 3 row, and the Table 2 rows for every file
you touch. Do not exceed 5.4.0 and do not invent further versions.

## STATE

v5.3.3 is published (`06cabc0`). The tree is clean apart from two untracked
working documents in the repo root:

- **`INFORME-v5.4.0.md`** — your own verification report from the orchestration
  round. It is the source of most of what follows. **Read it first.**
- `PROMPT-v5.4.0-orquestacion.md` — the mandate that produced it. Historical.

Both can be deleted once v5.4.0 ships.

## WHAT v5.4.0 IS

One idea: **Keel learns what its environment can actually do, and orchestrates
accordingly.** Three pieces, plus one decision to record.

---

### PIECE 1 — The environment preflight tells the truth

Goes in `references/phase-1-discovery.md` §5a (the environment preflight), with a
line in the definition of done, plus the fourth-gate cross-reference already in
`references/project-state.md`.

**1a. `claude` on PATH — probed only when chaining is wanted.**

Ask it only when the `Chaining:` answer is `prefill` or `start`; on `off` the row
is not applicable and nothing is asked. Probe with `command -v claude`.

State why it is not obvious: **neither the desktop app nor the VS Code extension
puts `claude` on PATH.** The app runs Claude Code graphically; the extension
bundles a private copy for its own panel. Someone can have both installed, use
Claude Code daily, and have no `claude` command. (Verified against the official
docs: "The desktop app includes Claude Code… To use `claude` from the terminal,
install the CLI separately.")

Missing → offer the install and record the answer either way:

- macOS — `curl -fsSL https://claude.ai/install.sh | bash`, or `brew install --cask claude-code`
- Windows — `irm https://claude.ai/install.ps1 | iex`, or `winget install Anthropic.ClaudeCode`
- Linux — the same script, the signed apt/dnf/apk repos, or `npm install -g @anthropic-ai/claude-code`

Declined or unavailable → `start` is not offered, `prefill` is the maximum, reason
recorded. v5.3.2 already names this as the fourth gate on `start`; this adds the
probe and the offer.

**1b. Protected environments are announced up front, not discovered on failure.**

Some environments cannot do what Keel assumes. The measured case is Cowork's
device bridge, and every item below was hit for real during v5.3.x:

- The bridge to the user's disk **cannot delete files**. `rm` returns "Operation
  not permitted". Git leaves `.lock` files that then block the user's own repo —
  this happened repeatedly and cost real time.
- The bridge **has no network**: no `push`, no `fetch`, no dependency install.
- **Two separate filesystems.** The cloud container has network but not the user's
  files; the bridge has the files but no network. **Neither can execute commands
  where the repository lives AND reach the network** — which is exactly what Keel
  assumes for playgrounds, installs and test runs.
- No `localhost` on the user's machine, so a locally-run playground is invisible.
- No screen control or window capture.

Detect what the session can actually do, state it to the user in one line at
Phase 1 alongside the English-docs default and the accessibility commitment, and
record it in `docs/01-discovery.md` under the existing
`## Environment & test drivers`. A protected environment is a fact about the
session, not a failure, and saying it late is what makes it expensive.

**1c. `NO-EXECUTION` gains its partial case** in `references/test-automation.md`.

The tag today means "this session has no way to run commands where the repo
lives". Cowork is neither that nor full capability: it CAN execute, and it CAN
touch the files, but not both at once with network. Give that case language, so a
session in it stops promising what it cannot deliver.

---

### PIECE 2 — §4.5, native workflows for the fan-out phases

Everything here is measured in `INFORME-v5.4.0.md` §7. Write:

- **The conformance sweep as a workflow**: rows of Table 1 plus Table 3's delta are
  an enumerable list — the canonical one-verifier-over-many-independent-units case.
  Proven on a real project: 31 rows, 5 agents, 110 s, zero hallucinations found on
  contrast.
- **Structured output fills `docs/keel-conformance.md` with no model between the
  data and the file** — but say honestly what that requires: a deterministic
  template in the script (six lines of JavaScript, no model), and either a writing
  agent or, cleaner, the workflow RETURNS the markdown and the main session writes
  it. "No post-processing" means no model in the middle, not no code.
- **The three-step fallback chain**, next to the sentence already in
  `references/assistant-config.md`: **workflow (if opted in) → parallel subagent
  block (if subagents exist) → inline and serial.** All three produce the same
  table; only the wall clock changes, and none of them drops a check. The tool
  needs explicit user opt-in, may be absent, and has a user-controlled size cap
  Keel does not govern — identical in kind to the subagent situation Keel already
  handles.
- **Dedup and the concurrency cap become code**: "merging is the main session's
  job" turns into a deterministic function in the script; the cap is native.
- **The cross-unit check becomes an explicit extra agent** in the script, visible
  in code instead of trusted to memory.
- **What stays judgment, and say so**: which verifiers a gate calls for (six of the
  nine agents are conditional), the reader/executor split and one-executor-per-
  environment, `test-driver`'s ordering exception, and the gate's verdict.

**HARD CONDITION — do not write anything about `isolation: 'worktree'`.** It is
the one part of §4.5 still unverified, and it is not needed: a conformance sweep
only reads. Record separately, where the fan-out rule lives, that
**`isolation` isolates FILES, not ENVIRONMENTS** — two worktrees still fight over
one port, one database, one seeded origin — so the serial exception for
"one executor per environment" stands unchanged.

---

### PIECE 3 — Three rescues from the abandoned director

These stand on their own and cost almost nothing:

1. **The `PROGRESS.md` rule for worktree work.** The living state is written by
   the session that owns the MAIN tree; a worker in a worktree writes a report at
   `docs/.keel/slices/<n>.json` (`slice`, `status`, `branch`, `commit`,
   `needs_user`) and **never** the state. Measured: without this, `PROGRESS.md`
   conflicts in 100% of merges, N−1 times for N workers, and the code merges
   clean — the state file is the only casualty. With it, three merges, zero
   conflicts. This inverts a Keel rule, so record it as a deliberate decision with
   its reason. Add the slices path to MANIFEST Table 1 as a CONDITIONAL row (only
   when the project fans out over worktrees).
2. **The worker close-out contract**, in this exact order: `commit` → write the
   report → atomic done-signal (`printf > tmp && mv`, because a rename cannot be
   read half-written). The order is the point: an existing signal implies committed
   work, never the reverse. Not stdout — `claude -p` writes nothing until the end,
   so a live worker and a dead one both show an empty log.
3. **`claude agents --json`** as the supported way to see live sessions (pid, cwd,
   kind, session id, name, `idle`/busy). It replaces parsing `*.jsonl`. **Caveat
   that must be written down: `-p` sessions do NOT appear** — only interactive and
   `--bg`. Also note `--session-id <uuid>` lets a launcher assign the id up front.

**And one note so it is never re-proposed:** closing another session's window is
measured on macOS and is NOT reliable — 40–78 s latency with no confirmation, no
cleanup hooks run (signal traps never fired), and a guaranteed orphaned lane.
Put it beside the `start` material.

---

### THE DECISION TO RECORD

**The chat director is abandoned as a design.** It works — three slices, three
workers, zero conflicts, and it escalated a product question instead of inventing
an answer — but it does not earn its scaffolding against native subagents and
workflows: ~7k context per slice in a toy and 15–20k in a real project, degrading
between the 6th and 9th slice, with no cost accounting, no cancellation and no
concurrency cap, all to obtain parallelism Keel already has.

Its one real advantage — a chat with a person in it, which can be asked a question
and can answer — is obtained by something smaller: **one Keel session that, in a
single turn, dispatches N workers into worktrees, waits for their signals and
merges.** The chat where the person is, is the chat you are already working in.

Record the decision and the reason where a future session will find it before
re-proposing the idea.

---

## A PREVENTION WORTH ADDING — evaluate and propose

v5.3.1, v5.3.2 and v5.3.3 were all the same defect: **a requirement recorded in
MANIFEST Table 1 with no phase reference naming who creates it and in which step.**
Three patches, one shape. That is a mechanical check, not a lesson:

> every Table 1 row required at some phase is named by at least one phase
> reference as something that phase creates.

Assess whether it belongs in `tests/lint-release.py` (the skill's own linter) or in
the `scripts/keel-verify` template Keel generates for projects, or both. Propose
it with the check written; do not add it silently.

---

## HARD RULES

1. **Run `python3 tests/lint-release.py` before declaring anything done.** It
   exists, it is authoritative, and it was ignored during v5.3.0 — which is how the
   README version line shipped stale.
2. Every file you touch needs its MANIFEST Table 2 row bumped to v5.3.4 or v5.4.0
   as appropriate — the linter checks this both ways.
3. Restamp the canonical lock block in `references/project-state.md` to the release
   version; the linter enforces it. If the block's CONTENT does not change, say so
   in the changelog so the refresh is understood as stamp-only.
4. CHANGELOG is ordered oldest → newest; the new section goes LAST.
5. Do NOT commit, tag or push. Leave the tree for José.
6. Use `git --no-optional-locks` for read-only git commands.
7. Anything you cannot verify goes in as "unverified", never as a plausible
   mechanism. Three of the last four releases were fixing exactly that.

## DELIVERABLE — in Spanish

1. Every file touched and what changed in each.
2. The linter output, pasted.
3. The Table 3 delta you wrote, so it can be read as the migration instruction it is.
4. Your proposal for the prevention check, with the check itself written.
5. Anything you found wrong in the existing text while working — proposed, not
   applied.
6. A suggested release title and description, in the voice of the previous ones
   ("v5.3.3 — the sweep stops citing itself, and the lane gets given back").
