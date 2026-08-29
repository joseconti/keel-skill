# Known traps — the failure catalogue

Load this the moment Phase 1 fixes the project type, together with the security profile and
`references/accessibility.md`. Read the universal section plus the section(s) matching the project
type. Re-read it at the first sign of a shortcut.

This is **prevention**, and it is the counterpart of `docs/lessons-learned.md`, which is **memory**:
lessons-learned records what bit THIS project; this file records what has bitten projects of this
class before it started. They are not the same artifact and neither replaces the other.

Every entry has the same four parts, because the third is the one that changes behavior:

- **The trap** — what the shortcut looks like from inside.
- **Why it happens** — the reason it is attractive, stated fairly. A trap nobody is tempted by is not a trap.
- **What it costs** — the real, concrete damage, not a scolding.
- **The rule** — what Keel does instead, and where the check lives.

## The one idea underneath all of them

**Almost every entry below is documentation and reality drifting apart while both keep looking
healthy.** A doc that describes what the code used to do is worse than no doc at all: the reader has
no way to know it is stale, so it is believed. And the fix is almost never "write it more clearly" —
it is **make the check fail**. Prose asks for discipline once per reader; a check enforces itself
forever.

Which is why nearly every rule in this file ends by naming a mechanical check — a `scripts/keel-verify`
line, a test point condition, a Phase 7 gate item. **A trap whose rule is only prose is a trap that is
still open.** When a new trap is found and it can be checked mechanically, extending `keel-verify` is
part of closing it, not a follow-up.

---

## Universal traps (every project type)

### 1. The declared tool that never runs

**The trap.** A linter, a formatter, a static analyzer, a test framework appears in `package.json`,
`composer.json` or the technical plan. No script invokes it, no configuration file exists, and nothing
fails when it would have complained.

**Why it happens.** Adding the dependency is one line and feels like progress. Actually applying it
surfaces two hundred pre-existing findings, which is work nobody scheduled.

**What it costs.** The illusion of coverage, which is worse than no coverage: a reviewer sees the tool
declared and assumes the rules are running, so nobody looks again.

**The rule.** A tool enters the project in the SAME change that makes it pass and makes it blocking.
If the findings are too many to fix at once, generate a baseline, commit it, and require it to
shrink — never grow. Declared-but-unwired is a Phase 5 slice defect, and the technical plan's tooling
list is verified against what the test-point commands actually run.

### 2. Documentation that contradicts the build

**The trap.** `CLAUDE.md`, `AGENTS.md`, the README or a doc names a command — a build script, a test
invocation, a playground boot — that does not exist, or that was renamed. Every assistant that follows
the instruction fails, then improvises something else.

**Why it happens.** The build was refactored; the instruction was not. Nothing executes documentation,
so nothing detects it.

**What it costs.** Proportional to how much the project relies on assistants, which in a Keel project
is entirely. A failing instruction costs a retry at best and an invented workaround at worst — and the
workaround is now the de-facto process, undocumented.

**The rule.** **Every command cited anywhere in the repository's documentation exists as a real script
or a real CI step.** The documentation cites the script; the script is the truth. `scripts/keel-verify`
checks this mechanically (`references/phase-5-development.md` §1a).

### 3. The same fact pinned in five places

**The trap.** A version, a supported-platform floor, a URL, a limit, a price appears in the manifest,
in a README badge, in a doc table, in a setup guide and in a CI workflow. Three of them are current.

**Why it happens.** Each copy was correct when it was written.

**What it costs.** Every stale copy is a trap for the next reader, and stale setup instructions produce
failures that look like product bugs.

**The rule.** One authoritative location per fact; everything else refers to it rather than repeating
it. Where a value genuinely must appear in several files (a plugin version header, a constant, a
`package.json`), those places are enumerated in the technical plan's **Version touchpoints** and
`keel-verify` cross-checks them on every run.

### 4. The target tree read as an inventory

**The trap.** The code map in `docs/03-technical-plan.md` describes the structure the project is
heading towards. A session reads it, assumes those files exist, and writes code that imports them — or
worse, reports that a component "is in place" because the map shows it.

**Why it happens.** A map and an inventory look identical on the page. Nothing in a plain tree diagram
says which lines are aspiration.

**What it costs.** Confident, wrong work: imports of modules that do not exist, a status report that
does not match the disk, and a user who trusts a claim that was never checked.

**The rule.** Every path in the code map carries a marker — `[E]` exists now, `[A]` to be created by
the assistant in a named slice, `[G]` generated by a tool once its source exists. **A path not marked
`[E]` is treated as absent until a slice creates it**, and confirming the `[E]` inputs is the first
step of every slice. Never claim a path exists because the map shows it
(`references/phase-2-functional-spec.md`, `references/phase-5-development.md`).

### 5. The extension point nobody can reach

**The trap.** A hook, filter, action, event or callback is documented in `docs/api/` — and is never
fired in the code, or is fired with a different name, or fires after the value it was supposed to
influence has already been used.

**Why it happens.** The doc is written from the design intent, at spec time; the code drifts from it
during implementation and the doc is never re-read.

**What it costs.** A third-party integrator writes code against the documented hook, it silently never
runs, and the bug report arrives as "your plugin is broken" with no reproduction the maintainer can
see. This is the single most expensive class of support ticket for extensible projects.

**The rule.** Every documented extension point is exercised by a named automated test that asserts it
actually fires, with the documented arguments, at the documented moment. A documented hook with no test
is a slice defect. `keel-verify` cross-checks the names in `docs/api/INDEX.md` against the names present
in the source.

### 6. The generated artifact nobody consumes

**The trap.** A build step produces something — a translation template, a typed constant file, a
schema, a manifest — that no code imports and no release includes, while the same values sit hardcoded
where they are actually used.

**Why it happens.** The generator was written for completeness; wiring each consumer was left for
"when we need it", and the hardcoded copies already worked.

**What it costs.** The worst possible outcome: the appearance of a single source of truth over an
actual duplicate. Editing the source changes the generated output, every check still passes, and
behavior does not change — so the search for the real value takes an afternoon.

**The rule.** Either wire it or delete the generator, in the slice that notices — there is no third
option, and "leave it for when we need it" is how the duplicate becomes permanent. Where the stack
makes it mechanically checkable (a resolvable import graph, a known consumer path), the check goes
into `scripts/keel-verify`; where it does not, it is a question in the self-audit below, answered by
a search rather than by memory.

### 7. Verification claimed but not run

**The trap.** "Tests pass", "the build is clean", "the playground boots" — asserted from expectation
rather than from a command that was actually executed and read.

**Why it happens.** The change was small and obviously correct, and running the suite is slow.

**What it costs.** More than any other single failure mode, because it converts a known problem into an
unknown one. A reported failure gets fixed; a false green gets built upon, and the real defect surfaces
three slices later where nobody is looking for it.

**The rule.** `docs/05-test-points.md` records the exact command, its output summary and the commit
hash. A result without its command is an empty cell, and an empty cell is a missing check. Where a
gate genuinely cannot run yet because its inputs do not exist, the honest report is **"not yet
applicable"**, naming the missing artifacts — never "passed", never "failed"
(`references/phase-5-development.md`).

### 8. The gate loosened to get green

**The trap.** A test is skipped, an assertion relaxed, a lint rule disabled file-wide, a coverage floor
lowered — because the gate is red and the work is "done".

**Why it happens.** Under time pressure this is locally rational and takes thirty seconds. The gate is
also, occasionally, genuinely wrong, which makes the shortcut feel principled.

**What it costs.** The check existed because something broke once. Disabling it re-opens exactly that
failure, silently, and every later reader assumes the area is covered.

**The rule.** There is a defined, narrow escape hatch and nothing outside it: fix the code (the default
assumption) → fix the gate in its own commit with the reason in the message → suppress narrowly (one
line, one rule, a comment with the why and a link to the record) → **never** an override, a file-level
disable, or a deleted test. Suppression count is tracked and must not grow: a growing count means a
standard is not working and needs revisiting, not routing around
(`references/phase-5-development.md`).

### 9. The silent omission

**The trap.** A protection, a capability or a compatibility that was considered and deliberately left
out — and then never written down. Six months later nobody can tell the difference between "we decided
against it" and "we forgot".

**Why it happens.** Recording a decision not to do something feels like paperwork about nothing.

**What it costs.** The next person (or the next session) either re-litigates the decision from scratch,
or assumes the protection is there. Both are expensive; the second is dangerous.

**The rule.** **An omission that is written down is a decision; an omission that is silent is a trap.**
Deliberate omissions go in `docs/decisions.md`, and security omissions specifically go in the
"Not defended" table of `docs/threat-model.md` with their consequence
(`references/phase-2-functional-spec.md`).

### 10. The control claimed but not shipped

**The trap.** A security or quality claim written in the present tense — "input is sanitized",
"a lint rule blocks this", "the endpoint is rate-limited" — when the mechanism is planned, partial, or
lives only in a doc.

**Why it happens.** Documentation is often written at spec time, describing the intended end state,
and the tense is never corrected when reality lands differently.

**What it costs.** Every downstream reader, human or assistant, stops looking. A claimed control is
strictly worse than an acknowledged gap, because a gap gets scheduled and a claim does not.

**The rule.** Every control carries its delivery state: **`IN PLACE`** (built and verified, with the
evidence), **`TO BUILD`** (a named slice will build it), **`MANUAL`** (a human must configure it in a
console or panel) or **`VERIFY`** (only a real-environment test can confirm it). Only `IN PLACE` may be
written in the present tense. Never claim a control that does not ship.

### 11. Two copies of the same source of truth

**The trap.** The same schema, config, string table or asset exists twice — a versioned filename beside
an unversioned one, a doc copy beside a code copy, a `.min` file hand-edited so it no longer matches
its source. Nobody knows which is authoritative, so edits land in whichever one the search found first.

**Why it happens.** A copy was made cautiously, to avoid breaking a reference, and deleting the old one
felt risky.

**What it costs.** Divergence, guaranteed, on the first edit made under time pressure.

**The rule.** Exactly one authoritative file per artifact. Where a build output must exist beside its
source (minified assets), the direction is one-way and mechanically verified: the output is regenerated
from the source and never hand-edited (the source-first assets contract in SKILL.md, checked by
`keel-verify`).

### 12. The orphan document

**The trap.** A document in `docs/` that no index and no other document links to. It is not wrong; it
is invisible. Meanwhile the information it holds gets re-derived, and re-derived differently.

**Why it happens.** It was written for a specific moment and the index was updated "later".

**What it costs.** Search returns two answers with different content and no way to rank them — the
documentation equivalent of the duplicate source of truth, and it defeats the entire premise of a
resumable project.

**The rule.** Every document is reachable from `docs/PROGRESS.md`, `docs/api/INDEX.md` or another
linked document. `keel-verify` reports orphans and broken internal links; archiving moves a document to
`docs/old/` with its link updated, never leaves it dangling.

---

### 12a. The test delegated to the user

**The trap.** An acceptance criterion whose only evidence is a person's verdict: "go to Settings, enter
an invalid email, tell me if the error appears". It looks like verification and it is recorded as a pass.

**Why it happens.** It is genuinely faster in the moment — for the assistant. Writing a locator, waiting
for the right state and asserting the message costs ten minutes; asking costs one line. The cost is
transferred, not removed, and it is transferred to the person whose time the project exists to protect.

**What it costs.** The check runs once and never again, so it catches nothing on the next commit. It
leaves no artifact, so nobody can see what was actually verified. The person walks the happy path and
skips the empty, invalid and permission-denied cases, which is precisely where the defects are. And it
becomes habit: a project that delegates one flow ends up delegating its whole surface.

**The rule.** Every user-visible criterion is driven by the assistant and carries its evidence, or it
carries one of the eight delegation tags with its steps (`references/test-automation.md`). Free-text
excuses are not tags. `keel-verify` cross-checks the criterion IDs against the `Coverage` column, so the
rule is enforced by a command rather than by anyone's good intentions.

---

### 12b. Keel applied halfway, silently

**The trap.** Keel is adopted into a repository, or a project is moved to a newer Keel version, and a
subset of what applies gets applied. Nothing is wrong on the surface: the state files exist, the lock is
there, the phase references are being followed. What is missing was never mentioned, so nobody knows to
look for it.

**Why it happens.** The assistant works from what it recalls of the skill rather than from the manifest,
and recall is partial by nature — especially for the conditional rows, which is exactly where the
valuable, easily-skipped pieces live.

**What it costs.** Months later a gap surfaces (no threat model, no change map, no doctor, no guide) and
it is impossible to tell "we decided against it" from "it was forgotten". The second reading is the
dangerous one, and it corrodes trust in every other claim the project makes about itself.

**The rule.** Adoption and reconciliation both run the conformance sweep from `MANIFEST.md` row by row
into `docs/keel-conformance.md`, every applicable row carries a state, every `missing` row reaches the
user as a proposal, and every refusal becomes a decision entry. Applying is the user's choice; proposing
is not optional. `keel-verify` fails on a due row that is `missing` with no decision.

---

### 12c. The test edited until it passed

**The trap.** A test derived from an acceptance criterion fails. The assertion is adjusted, the expected
value is widened, the awkward case is removed — and the suite goes green. The commit reads like
authorship, because the test was written by this same session, minutes ago, and feels like its own to
change.

**Why it happens.** It is the cheapest action available at the exact moment the pressure is highest: a
gate is one red away from green, the fix is not obvious, and the test is right there and editable. It
does not feel like loosening a standard; it feels like correcting a first draft. Test-first makes this
trap MORE likely, not less, because the test is newest and least defended precisely when it is doing its
most valuable work.

**What it costs.** Everything the test was worth. The requirement now has a test that no longer tests
it, and the mismatch is invisible: the suite is green, the coverage check passes, the criterion has a
row. It is worse than having no test at all, because a missing test is a visible gap and a hollowed-out
one is counted as evidence.

**The rule.** A test derived from a recorded requirement — an `AC-nn`, or a reproduced bug — is never
modified to make it pass. If the test is genuinely wrong, then the REQUIREMENT is wrong, and that is the
user's call: a `docs/decisions.md` entry, or a Design Request where a design contract is involved. The
boundary is precise and it is about the assertion: **if the set of behaviours that would pass the test
changes, the rule applies**; renaming, moving, improving the failure message and fixing the test's own
scaffolding do not. This is `references/phase-5-development.md` §2's "never 'fix' the failure by deleting,
skipping, or loosening the test" stated for the one case where it looks like editing your own draft
(`references/test-automation.md`, "When the test is written").

---

### 12d. The test that could never have failed

**The trap.** A test written before the code, run once, seen to fail, and taken as red — when the
failure was a broken import, a missing fixture, a typo in the module path. The setup is fixed, the code
is written, the test goes green, and nobody ever asks which of the two produced the green.

**Why it happens.** Step one of test-first is "see it fail", and a failure is easy to produce. Reading
the failure message to confirm it names the ABSENT BEHAVIOUR — and not the scaffolding — is a separate
step, it takes ten seconds, and it is the one that gets skipped when the red is expected anyway.

**What it costs.** A test that asserts nothing, permanently, wearing the exact appearance of a test that
asserts something. It never fails again, so it is never re-examined; it is counted in coverage, it
satisfies the criterion's row, and it will still be green on the day the behaviour it names is deleted.
The project has bought confidence with nothing underneath it — the most expensive purchase in this
entire catalogue, because unlike every other trap here it produces no symptom at all.

**The rule.** The red is observed, and the failure message is confirmed to be the absent behaviour before
any production code is written. The failure line is recorded in the test point's evidence cell and the
row's `Red first` column says `observed`. `keel-verify` fails a `Red first` cell that is empty or
outside the five values, fails a row that claims `observed` with no failure output beside it — a claim
without its evidence, which is the same defect as entry 7 — and reports every other row for a person to
judge.

---

### 12e. The second session writing into a checkout somebody else is working in

**The trap.** A repository is open in one session that is mid-slice, with uncommitted work in the
tree. A second session — opened by hand, chained, scheduled, or running on another surface — starts
writing into the same directory. Both are correct in isolation. Together they interleave commits on
one branch, overwrite each other's `docs/PROGRESS.md`, and sweep each other's in-flight files into
unrelated commits.

**Why it happens.** Nothing about the directory announces that it is busy. The single-lane lock
guards CHAINED launches, and it is keyed to the working directory precisely for this reason — but a
session a person opens themselves, or one running on a different surface, never passes through the
launcher and therefore never meets the lane. The second session sees an ordinary repository.

**What it costs.** Measured: a session opened on another surface committed with `git add -A` into a
repository whose live session was mid-slice, swept two of its in-flight files into a documentation
commit under an unrelated message, and appended a decision entry with an ID that was already taken
120 entries earlier. Nothing was destroyed, and the recovery still cost more than the work was worth.
The damage is silent at the moment it happens: every command succeeds.

**The rule.** **Before the first WRITE into a repository this session did not start work in, establish
that nobody else is working in it** — mechanically, never by assumption. Two commands answer it:
`git status --porcelain` (uncommitted work is the first signal) and, for anything it lists, the
modification times of those paths. Files changed in the last few minutes, in an order that looks like
authoring, mean a live session. `claude agents --json --cwd <path>` settles it where the CLI is
available. If another session is working there, do not write: hand the change to that session as a
ready-to-paste instruction, which is the same boundary rule the skill already applies to every other
tool crossing. Reading is always safe; writing is what needs the check.

### 12f. The copy in context read as if it were the repository

**The trap.** A session holds a file in context — a reference, a state file, the skill itself — and
reasons from it for the rest of the session. Meanwhile the repository on disk has moved: another
session edited it, an update landed, the working tree advanced several versions.

**Why it happens.** The skill's own context discipline says to read each static reference once per
session and never re-read what is already in context, which is correct for cost and for cache
behaviour, and which quietly becomes wrong the moment the file on disk is a moving target.

**What it costs.** Measured: a session reasoned for an entire working block from a v5.11.0 copy of
this skill while the repository it was working in held an uncommitted v5.14.0 — then proposed, in
detail, a four-part change that the working tree already contained in full. The advice was coherent,
well-argued and useless, and nothing in the session could have detected it.

**The rule.** **The repository on disk is the authority; a copy in context is a cache with no
invalidation.** Re-read from disk, without exception, in three cases: when the session is working ON
the repository that a file in context came from; after any external process may have touched the tree
(an update, another session, a merge); and before asserting anything about a version, a phase or a
recorded decision. The cheap form is one command — read the frontmatter, the phase status, the
current position — not the whole file.

### 12g. The repair whose effect was never checked

**The trap.** A command that fixes something returns exit 0, and the fix is reported as done. It did
nothing. Restores, checkouts, file replacements and permission changes all have environments in which
they fail without failing loudly.

**Why it happens.** Exit codes report whether the command ran, not whether reality changed, and the
gap between the two is invisible unless someone looks. On restricted filesystems the gap is routine:
a mount that forbids `unlink` lets `git checkout <commit> -- <path>` return success while leaving the
file exactly as it was.

**What it costs.** Measured: two files were reported "restored verbatim" in a commit message, and the
commit that claimed it changed nothing in them. The false claim then sat in the history, which is
worse than the original error, because the next reader has no reason to check.

**The rule.** **A repair is verified by its EFFECT, never by its exit code**, and the verification is
the command that would have caught the failure: `git diff <ref> -- <paths>` after a restore, a
re-read after a write, a re-run after a fix. This is "declared is not delivered" applied to the
commands a session runs on its own behalf. A commit message may only claim what a check confirmed.

### 12h. `git add -A` in a tree you did not author

**The trap.** A session stages everything and commits, in a repository where some of the changes are
not its own — another session's in-flight work, a half-finished slice, a generated file that was
about to be reverted.

**Why it happens.** `-A` is the reflex, and in a tree the session authored entirely it is correct and
convenient.

**What it costs.** Somebody else's incomplete work is now committed, under a message that describes
something unrelated, at a moment they did not choose. The content survives, so nothing looks broken —
but the history now says a slice was finished when it was not, and the ordering evidence a sprint
close depends on is gone.

**The rule.** **Stage explicit paths whenever the session did not author every change in the tree.**
`git status --porcelain` before every commit, and anything on that list the session cannot account
for stops the commit until it is explained. In a tree the session authored end to end, `-A` remains
fine.

### 12i. The identifier chosen from memory

**The trap.** A new entry is appended to an append-only log — a decision, a lesson, a test point, an
acceptance criterion — with the next ID inferred from what the session remembers seeing, rather than
derived from the file.

**Why it happens.** The session read the file earlier, or read a fragment of it, or created it and
assumes it knows its size. Appending is a one-line operation that feels too small to warrant a read.

**What it costs.** Measured: a decision was filed as `D-009` in a log that already ran to `D-105`,
colliding with an unrelated entry. Two entries with one ID break every cross-reference pointing at
either, and the log's whole value is that a reference resolves to exactly one entry.

**The rule.** **Derive the next identifier from the file, in the same command that appends** — one
`grep` for the ID pattern, take the highest, add one. Never from context, never from the last one the
session happens to have seen. `scripts/keel-verify` gains a check that no ID appears twice in any
append-only log the project keeps.

### 12j. The network call inside an unconditional hook

**The trap.** A `PreToolUse` hook matching every command of a class — every `Bash`, every edit — makes
a network call to decide. Every command in the session now waits for the network.

**Why it happens.** The hook's logic genuinely needs the remote answer for the handful of commands it
exists to guard, and the broad matcher is what guarantees it never misses one. Breadth looks like
safety.

**What it costs.** Measured: a branch-protection hook calling `gh pr view` took 44 seconds to time out
on every git command in the session, read-only ones included. And a hook that times out is a hook
that has failed — so the second, larger cost is the one nobody sees: if it fails OPEN, the protection
is absent exactly when the network is bad, while continuing to look installed.

**The rule.** Three parts, and the third is the one that gets skipped. **Match only the commands the
hook actually guards** — a read-only command cannot violate a rule about pushing. **Split the check by
what it needs**: the local half (`git rev-parse --abbrev-ref HEAD`) is instant and usually decides,
and only the remainder needs the remote. **Bound the remote call with a timeout and fail CLOSED on
it** — denying an action because it could not be verified is cheap and recoverable; hanging and then
allowing is the worst of both. A protection hook's failure mode is part of its specification and is
stated in `docs/decisions.md` when the hook is adopted.

### 12k. The matcher that only sees the start of the command

**The trap.** A rule — a permission entry, a hook matcher, a guard — matches on the beginning of a
command string. `git push` is matched; `git add -A && git push` is not, because it begins with
`git add`.

**Why it happens.** Prefix matching is what the tooling offers by default, and it reads as if it
covers the command.

**What it costs.** The guard is bypassed by the most ordinary thing a session does. Keel already
documents the cost side of this for permissions — a composite command fails to match an `allow` rule
and opens a dialog — and this is the same mechanism with the sign reversed: a composite command fails
to match a DENY rule and sails through. The performance version is an annoyance; the security version
is a hole.

**The rule.** **A guard matches the command line, not its prefix.** Anything that denies, protects or
gates searches for its target anywhere in the string, including after `&&`, `;` and a pipe. Narrowing
a matcher for performance is only correct once this holds — otherwise the narrowing is a security
regression wearing a performance argument.

### 12l. The control that passes by answering a different question

**The trap.** A check runs, passes, and is trusted — and the question it answers is not the question
that matters. It is not broken, and no output ever suggests it might be.

**Why it happens.** The check was written for a real question. The concern then shifted by one step —
from "is the mechanism configured?" to "is this run leaving what the mechanism needs?", from "does
the file exist?" to "does it say something true" — and nothing forces a check to re-state its own
scope when the concern moves.

**What it costs.** Measured twice in one project. A chain checker passed all twelve of its rows on two
consecutive nights while the chain did not fire, because it verified that chaining was configured and
nobody verified that the session was leaving a current hand-off. A test-identifier check reported zero
findings for weeks because it was line-scoped and structurally incapable of ever seeing a real one.
**A control in this state is worse than no control**, because its green result is actively spent as
reassurance.

**The rule.** **Every check states, in one line beside it, the question it answers** — and a check
that has never failed is audited against a case that SHOULD fail it, rather than trusted for its
record. When a green result is used to justify a conclusion, the conclusion is checked against the
check's stated scope, not against its colour. A control whose scope is not written down cannot be
audited, so writing it down is part of adding the control.

### 12m. The guard keyed to the directory enforcing a duty that belongs to the session

**The trap.** A guard reads the state of a working tree and acts on it — blocks, warns, refuses. The
state is a fact about the DIRECTORY; the duty it enforces belongs to a SESSION. With one session in
the checkout the two are the same thing and the guard is correct. With two, it punishes whichever
session did not make the mess, and the one that did carries on untouched.

**Why it happens.** `git status`, `HEAD`, a lock file, a log keyed by working directory: every cheap
way to ask "what is going on here?" answers for the directory, because that is the only thing the
filesystem knows about. Nothing in the answer says which session produced it, so the scope is
inherited by accident rather than chosen — and it is invisible until a second session exists, which
is usually long after the guard was written and trusted.

**What it costs.** Measured, on this skill's own `scripts/keel-stop-hook` two days after it shipped.
Session A was blocked naming two files session B had modified eight seconds earlier and was still
editing. The remedy the block offered was "commit to `develop`" — that is, `git add -A` in a tree it
did not author (12h). Worse, the anti-spin brake never engaged: its fingerprint covered the whole
tree, so B's keystrokes renewed it every turn and A stayed blocked for eight turns until the hourly
cap released it. **Not a block that expires — a block renewed by somebody else's work.** The same
guard's block log was keyed by working directory too, with the sign reversed: two sessions shared one
anti-spin history, so one session's block could satisfy the other's "nothing changed" test and
RELEASE a stop that should have been blocked.

**The rule.** **Every piece of state a guard writes or reads states its scope — repository or session
— and that scope is checked against the duty being enforced, not against what was convenient to
read.** Where the duty is the session's, the state is keyed by the session (`keel_session_pid`), and
the guard establishes concurrency BEFORE acting: another live session, and a guard that cannot be
satisfied by this session CEDES — allowing, saying it ceded and naming to whom — rather than blocking
somebody for work they cannot commit. Ceding is not a hole: the duty moves to the session that
authored the work and carries the same guard. Two boundaries hold it in place. **Concurrency is
detected, authorship is never attributed** — git records that a path changed and never who changed
it, so per-file attribution is a guess and a guess shipped as a check is worse than the gap it fills.
And **a probe that cannot answer means "not established", which keeps the original behaviour**; a fix
that turns an unanswered question into a licence has traded a loud failure for a quiet one. The tell
is never "keyed by directory" on its own — a lock that serialises a TREE is correctly keyed by the
tree — it is state keyed by directory while the duty belongs to one session.

**And fixing the reported instance is not fixing the class.** Measured on this same hook: the release
that wrote this entry fixed the rule that had been reported and left its sibling — three lines away
in the same file, same defect, same file — untouched, so the next project met it again with the
anti-pattern already written down. A generalisation does not travel to its siblings by itself.
**The release that generalises a defect sweeps every instance of the class it can reach and names
where it looked**, because "we understand the shape now" is a belief and the sweep is a list.

### 12n. The assertion that something is ABSENT, satisfied by everything being absent

**The trap.** A test asserts that a bad input was rejected — `assert!(result.is_empty())`,
`expect(rows).not.toContain(x)`, `expect(list.len()).toBe(1)` — and it passes against an
implementation that returns nothing for ANY input. It cannot distinguish "correctly excluded" from
"nothing works at all", and it will keep passing after the function it names is gutted.

**Why it happens.** It is the natural shape of the thought. The requirement is "a relative path must
not be walked", so the test says "the result does not contain the relative path", and an empty result
satisfies that sentence perfectly. Nothing about writing it feels wrong, and if the red was skipped —
or observed against a stub that returns empty — the gap never shows.

**What it costs.** Measured three times in one day, in two languages, in one project: three tests of
`resolved_roots` asserting `is_empty()`; a union test asserting `len() == 1` that passed with the
second source ignored entirely; and a `keel-verify` row asking only that a key appear "somewhere",
which the planted defect walked straight through. **All three were caught by the planted-defect
control and by nothing else** — every one of them was green in the suite, counted in the total, and
attached to a real requirement.

**The rule.** **An absence is asserted beside a SURVIVOR.** Put a valid value next to the invalid one
and assert the exact remainder: `resolve([good, bad]) == [good]`, not `resolve([bad]).is_empty()`.
The valid value is what makes the assertion discriminating, because now the only way to pass is to
keep one and drop the other. Where the shape is a count, choose inputs that separate every outcome —
1 means the source was ignored, 3 means it was duplicated, 2 is the answer — and say so in the test.
And when a control is planted (entry 12l), **check WHICH assertions reddened, not how many**: a
control that reddens four of six has just told you the other two are asserting nothing.

---

### 12o. The turn that ends on an intention instead of an action

**The trap.** The work is going well, a natural pause arrives — a commit lands, a suite goes green —
and the session writes *"now I'll do X"*, *"sigo con X"*, *"next I will…"* and stops there. Nothing
runs. From outside, a session that announced its next step and a session that finished are the same
thing.

**Why it happens.** The sentence feels like progress: it names the next step correctly, it reads as
continuity, and it is written at exactly the moment the work is going well enough to be worth
reporting. Reporting and continuing feel like one act, and they are two.

**What it costs.** Measured twice in one day on one project: **ten hours overnight**, and a second
stall the same afternoon that ended only because the person asked *"have you stopped?"*. The whole
close-out apparatus existed and was verified — the hand-off writer, the chain launcher, the lane, the
freshness checks — and none of it fired, because none of it is reached by a turn that simply ends.
The machinery was not missing; it was not run.

**The rule.** **A turn ends when the work is done, or when something is genuinely blocked AND the
close-out has run** — never on a sentence about what happens next. The tell is grammatical and it is
worth watching for in one's own output: **a future-tense clause about this session's own next action,
at the end of a turn, IS the stall.** Do the thing and report it in the past tense, or run the
close-out so stopping costs nothing. A summary of what was accomplished is not a reason to stop
writing tool calls, and it reads to the person coming back in the morning exactly like a session that
finished.


### 12p. The mechanism assumed portable because its trigger is, when its contract is not

**The trap.** A generated script proves itself in one assistant, and the natural next step is to
point every OTHER accepted assistant's equivalent hook setting at the same script, on the assumption
that "it's a `Stop` hook" is enough — the trigger exists in both places, so the reasoning treats the
interface as the same too.

**Why it happens.** Some mechanisms genuinely ARE portable this way: `.githooks/pre-commit` is
deliberately built as a classic git hook rather than an assistant-specific one, precisely so it fires
identically in every environment — Claude Code, Codex, Copilot, Cursor, Gemini, Windsurf, a bare
terminal — because GIT invokes it and git's contract is the only one it has to satisfy. A `Stop` hook
looks like the same shape from outside — an event, a script, a JSON reply — but it is invoked by the
ASSISTANT, not by git, so what it must satisfy is that assistant's OWN contract, and one assistant's
contract is not evidence for another's.

**What it costs.** Measured: `scripts/keel-stop-hook` emits Claude Code's own `Stop`-hook schema
(`hookSpecificOutput`, `decision: "block"`) and was registered verbatim in `.codex/hooks.json` on a
project running both tools on the same repository. Codex does not accept that schema, rejected it
with "invalid stop hook JSON output," and ended the turn the hook exists to keep open — the one
failure mode this class of mechanism is supposed to prevent, produced BY the mechanism itself, in the
tool it was never verified against.

**The rule.** A hook mechanism invoked by the ASSISTANT is never assumed portable across assistants
merely because the trigger name matches; only a mechanism invoked by something OUTSIDE every
assistant (git, the OS, the shell) earns that assumption, and even then only because the outside
caller's contract is the only one being satisfied. Before registering a generated script as a native
hook in a second tool, CONFIRM that tool's own current documentation for its output contract — never
infer it from a different tool's, however similar the trigger looks. Where the contract is
undocumented or unverified, that tool's cell is `—`: no committable mechanism, the duty stays with the
session, exactly like an allow-list cell with nothing to write — never a guessed schema shipped as if
it were confirmed.

### 12q. The launcher that fires the neighbouring tool's action because it is the only one proven

**The trap.** A launcher script detects which assistant is closing out and looks up that assistant's
own row before firing — and then, for a tool whose row is unverified or absent, fires the ONE row
that happens to be proven instead of printing, because "chaining should still do something."

**Why it happens.** The verified row reads as the safe choice: it is the one the generator watched
work, so reaching for it feels like caution rather than substitution. The contract already says an
unmatched or unverified row prints rather than fires — the trap survives a correct reading of that
rule anyway, because "print" looks like doing less than the verified row can, and doing less is easy
to round down to "doing nothing useful."

**What it costs.** Measured: a project accepting both Claude Code and Codex had its
`scripts/keel-continue` open a Claude Code Terminal window at the close of a CODEX session — the CLI
row's action fired under a different tool's detection. The closing session got neither a continuation
in its own tool nor the printed prompt its own contract already promised for this exact case; it got
an extra, unrequested chat window in a tool it was never running, and a launch receipt claimed for a
session nobody asked to open.

**The rule.** The action fired is ALWAYS the DETECTED tool's own row, never a different tool's
substituted as a fallback or a default. Printing is not a lesser outcome to be routed around; for an
unmatched or unverified row it IS the correct outcome, and it costs nothing a person cannot recover
from by reading the prompt. A launcher — like a hook (12p) — that reaches for the one mechanism it has
already proven, on behalf of a tool that mechanism was never proven for, is the same defect from the
firing side.

### 12r. The metered CI budget that fails by never running, not by failing

**The trap.** A workflow triggered on every push looks harmless when the suite is fast and the account
has never been near its limit — until the account's shared, metered minutes run out, and every
subsequent run across every private repository in that account simply stops being scheduled.

**Why it happens.** GitHub Actions' free-tier minutes are billed PER ACCOUNT (or per organisation),
pooled across every private repository — never per repository — while a public repository runs
unmetered on the same GitHub-hosted runners regardless of plan. A workflow tuned for one repository's
convenience spends a budget every OTHER private repository in the account draws from too, and nothing
about a single `git push` reveals that the pool is shared or how close to empty it is.

**What it costs.** Measured on this skill's own repository: a completely ordinary, correctly-formed
tag push — confirmed on the remote, confirmed pointing at the right commit — produced NO workflow run
whatsoever. Not a failed run, not a queued one, nothing to inspect: the account's included minutes
were exhausted, and GitHub did not schedule the run at all. The gap surfaced only because the expected
GitHub Release never appeared, hours later, and took a genuine diagnostic pass (checking the tag on
the remote, checking the workflow's enabled state, checking the raw Actions API) to distinguish from
every OTHER thing that can make a tag push not produce a release.

**The rule.** Where the forge is GitHub and the repository is private, the CI-triggers decision
(`CI runs on:`) is argued with this as an explicit, named risk, not folded silently into "reduces
noise" — the account-wide, shared, metered nature of the budget makes the conservative default
(`main`) protection for every OTHER private repository sharing that account, not merely tidiness for
this one. And when a CI-driven mechanism (a release workflow, a required check) appears to have
silently done nothing, a metered-budget exhaustion belongs on the list of causes checked BEFORE
assuming a configuration or a code defect — because from the outside, "no run happened," "the run
failed instantly with no logs," and "the workflow file has a syntax error GitHub silently rejected"
can look identical, and only checking the account's actual billing/usage tells them apart.


### 12s. The negative result recorded without its scope

**The trap.** An enquiry is made, it comes back empty, and the empty result is written down as a
decision: *"there is no way to do X"*, *"the platform does not support Y"*, *"this cannot be done from
here."* What was actually measured is narrower — two interfaces, one command's help output, one
afternoon — and the sentence that gets recorded says nothing about which two. From the next session's
side the entry reads as a property of the world.

**Why it happens.** A measurement that says "no" feels like the end of an enquiry rather than a step
in one. It was made honestly, it was written down responsibly, and citing it afterwards feels like
rigour — the opposite of guessing. Nothing about the moment suggests that the scope is the part
carrying all the weight, because at the moment of writing the scope is still in the writer's head.

**What it costs.** The scope evaporates and the conclusion hardens into a fact. Nobody re-opens it —
least of all when the person who knows the domain says the opposite, because they are no longer
arguing with a colleague's recollection, they are arguing with a recorded measurement, and this skill
correctly says decisions are not re-litigated. **Measured: two days of the wrong architecture.** A
project recorded "there is no channel into an already-running session" after checking exactly two
interfaces — a subcommand group and one flag. The product had an official feature doing exactly that,
on by default. The owner said sessions could message each other THREE times; each time the recorded
decision was cited back at them. The evidence was inside the project's own test output the whole time.

**The rule, and it has two halves.**

1. **Every negative finding carries a `Not checked:` line naming at least one avenue that was not
   examined** — the interfaces not opened, the documentation not read, the version not tried, the
   person not asked. A "no" without its scope is not a measurement; it is an impression with a
   citation. Two interfaces checked and written as "the product does not" is the whole failure in one
   sentence, and the line that would have prevented it costs eight words.
2. **When the user contradicts a recorded negative, that is the trigger to RE-MEASURE, not to restate
   the conclusion.** This is the one place where "a session never re-opens a recorded decision" does
   not apply, and the distinction is exact: the rule protects decisions — things that were CHOSEN —
   from being re-litigated by a session that dislikes them. A negative finding is not a choice, it is
   a claim about the world, and the user's contradiction is fresh evidence about that world while the
   record is evidence about one past enquiry with a scope nobody wrote down. Re-run the enquiry along
   the avenue the record never covered, and append the result either way — a confirmed "no" with a
   wider scope is worth more than the one it replaces.

**The mechanical check.** A `docs/decisions.md` entry whose text asserts an impossibility — `cannot`,
`there is no`, `not possible`, `impossible`, `does not support` — and carries no `Not checked:` line
is INCOMPLETE, and `scripts/keel-verify` says so. It is a grep over one file with a two-pattern
condition, it needs nothing but the log itself, and it fires at exactly the moment the scope is still
recoverable: while the session that made the measurement is still in the room.

---

### 12t. The test that asserts an assumption instead of a requirement

**The trap.** A test is written against how the session BELIEVES a thing works rather than against
what the thing must DO: *"the prompt is last in the argv"*, *"the flag comes before the path"*, *"the
handler is registered second"*. It goes green, it joins the suite, and it is counted as coverage for
the requirement it was written for.

**Why it happens.** The mechanism is what is in the writer's head at the moment of writing — it was
just reasoned out, it feels like the precise, specific, testable version of the vague requirement, and
naming it in the test name reads as rigour. A test called "the prompt reaches the tool" sounds woolly
next to one called "the prompt is last in the argv."

**What it costs.** It is a bug with a green tick, and the suite argues on its side. **Measured:** a
test asserting "the prompt is LAST in the argv" passed for as long as it existed, while the flag
immediately before it was variadic and had been swallowing the prompt the whole time. The test was
certifying the defect as correct behaviour — and it was found by RUNNING the command, never by reading
the vector, because reading the vector only ever confirms the assumption the vector encodes.

**The rule.** **When a test's NAME states a mechanism rather than an outcome, it is asserting an
assumption.** "X is last", "Y comes first", "the array has three elements" — all describe how the
session thinks the thing is wired. Name the OUTCOME instead: the prompt arrives at the tool, the
session starts in the right directory, the file is written. Then get the mechanism from RUNNING the
thing — one real invocation tells you what the argument parser actually does, which no amount of
staring at a constructed vector can. Where a mechanism genuinely IS the requirement (a wire format, a
documented protocol order), say so in the test and cite what makes it a requirement; a mechanism with
no source behind it is an assumption wearing a requirement's clothes. This is the assertion-side
sibling of entry 12d: 12d is a test that could never have failed, and this is one that fails on the
right day for the wrong reason — and passes every other day while the bug ships.

### 12u. The probe whose parser drops every input, so it answers with the default that disables the guard

**The trap.** A guard asks a question of the world, parses the answer, and acts. The parser is written
against the shape the output usually has. On the shapes it does not have, it produces something that
matches nothing — a path that does not exist, a field that is empty, a record that is skipped — and
the loop simply moves on. Every input is discarded, no error is raised, and the probe returns its
EMPTY answer: nothing was found, nothing was recent, nobody else is here. **That empty answer is not
neutral.** It is one of the two verdicts the guard acts on, and it is invariably the one that means
"go ahead and enforce".

**Why it happens.** The parser is written from one example, and the example is the common case. `git
status --porcelain` prints `M  path` far more often than `R  old -> new`, so slicing the line from
the fourth character looks like reading the path — and it is, until it is not. Nothing signals the
failure: `stat` on a string that is not a file is not an error condition, it is a `continue`. And the
guard is usually tested in the state it is MEANT to fire in, where the empty answer is also the
correct one, so the bug is invisible to exactly the test written to prove the guard works.

**What it costs.** Measured on this skill's own `scripts/keel-stop-hook`, at v5.19.1. Its cede — the
whole of 12m's fix — required two facts: another session live, AND something in the dirty tree
touched recently. The second was computed by slicing `git status --porcelain`. On a tree whose only
dirty entry was a staged RENAME, the slice produced `old -> new`, no such file existed, the single
entry was skipped, and "nothing was touched recently" came back as a measurement. A session was then
blocked on a rename it had not made, and offered as its remedy a commit in a checkout that was not
its own. **12m's fix was present, correct and complete, and reached through a parser that made it
unreachable.**

**The rule.** **A probe distinguishes THREE outcomes, never two: found, not found, and could not
tell — and "could not tell" must not be reported in the words of "not found".** Where a parser
discards an input it does not recognise, that input is unanswered, not negative, and the guard says
so and falls back to whatever else can answer. Parse the format rather than slicing the common case,
and prove it against the shapes that are not common — for `git status --porcelain` that is a rename
and a quoted path, four commands in a fixture. The tell is a probe with a `continue` in it: ask what
the loop returns when EVERY iteration takes that branch, and whether the caller can distinguish that
answer from a real one. This is the enforcement-side sibling of 12l — there, a green result answered a
different question; here, an empty result answers no question at all and is read as an answer.

---


## WordPress and WooCommerce

### 13. The user-facing string that skipped i18n

**The trap.** A string written directly into markup or a `printf`, without a translation function or
with the wrong text domain. It works perfectly in the developer's language.

**Why it happens.** It is one string, added while fixing something else, and nothing visibly breaks.

**What it costs.** It never appears in the `.pot`, so no translator ever sees it, so it is permanently
untranslated in every locale — discovered by a user, in production, in a language the maintainer does
not read.

**The rule.** English base plus multi-language-ready from line one (SKILL.md "Output language &
internationalization"). `keel-verify` runs `wp i18n make-pot` (or the PHPCS i18n sniffs) and fails on
an untranslated or wrongly-domained user-facing string.

### 14. Settings with no uninstall path

**The trap.** Options, custom tables, transients, scheduled events, user meta and post meta are created
across the plugin's life. `uninstall.php` (or the uninstall hook) cleans up the three that existed when
it was written.

**Why it happens.** Each addition is one `add_option` in a feature slice; the uninstall routine lives
in a file nobody opens.

**What it costs.** Orphan rows in `wp_options` and `wp_postmeta` forever, autoloaded on every request
of a site that no longer uses the plugin, plus a reinstall that inherits stale state and behaves
differently from a clean install — one of the hardest support cases to reproduce.

**The rule.** Persistent state is registered in the change map (below): a slice that creates an option,
a table, a cron event or a meta key updates the uninstall routine in the same slice. The Phase 7 gate
verifies install → configure → uninstall → reinstall on a clean playground.

### 15. Capability and nonce checked in one branch only

**The trap.** An admin action verifies the nonce and the capability on the main path, and a secondary
entry point to the same handler — an AJAX action, a REST route, a bulk action, a CLI command — does not.

**Why it happens.** The second entry point was added later, reusing the handler, and the guard looked
like it was already there.

**What it costs.** A privilege escalation reachable by any logged-in subscriber, in a plugin whose main
path is correctly protected — which is exactly why review misses it.

**The rule.** The guard belongs to the handler, not the route. Every entry point is enumerated in
`docs/api/INDEX.md` with its required capability, and the security profile's checks run per entry point,
not per feature (`references/security/wordpress.md`).

### 16. "Tested up to" that stopped being true

**The trap.** The readme header names a WordPress or WooCommerce version that shipped two years ago,
while the plugin has been running fine on newer ones.

**Why it happens.** Bumping it means actually testing against the new version, and nothing enforces it.

**What it costs.** The directory shows a compatibility warning to every prospective user, and the ones
who install anyway have no idea what is actually supported. It reads as an abandoned plugin.

**The rule.** The support matrix lives in the technical plan and is a Phase 7 gate item, re-verified on
the playground pinned to the declared floor and ceiling; the maintenance duty
(`references/maintenance.md`) revisits it on every platform major.

### 17. Direct queries and direct superglobals

**The trap.** `$_POST['x']` used unsanitized, output printed without escaping, or SQL concatenated
instead of prepared — in the one place where "the value obviously comes from our own form".

**Why it happens.** The value does come from the project's own form, in every case the developer tried.

**What it costs.** The full injection surface, in the one code path that was never reviewed as
untrusted.

**The rule.** Sanitize on input, escape on output, prepare every query — with no exception for
"internal" values, because an entry point is a contract, not an intention
(`references/security/wordpress.md`).

---

## MCP servers

### 18. The ability whose schema lies

**The trap.** A tool's declared input schema and its actual handler disagree — an optional parameter
the handler requires, an enum the handler does not accept, a described return shape the handler never
produces.

**Why it happens.** The schema is written first, as the design; the handler evolves.

**What it costs.** The model calls the tool exactly as described, gets an error, and either retries
with invented variations or reports the server as broken. The failure is invisible from the server
side — it looks like the model "misusing" the tool.

**The rule.** Every ability is exercised through a real client (MCP Inspector, per
`references/playground-recipes.md`) at its slice's test point, with the documented arguments, and the
returned shape is compared against the documented one.

### 19. The description that never gets the tool called

**The trap.** A tool is correct, tested and well-implemented, and its description is "Content helper".
It is never selected, or it is selected for the wrong task.

**Why it happens.** The description is written as a label for humans reading a list, not as the
selection signal it actually is.

**What it costs.** The whole ability, silently. Nobody reports a tool that is never called.

**The rule.** The description states the trigger, in the terms a caller would use — what it does, when
to use it, what it needs. Ability descriptions are reviewed at the Phase 6 documentation pass exactly
like public API docs, and a never-selected ability is treated as a defect in its description.

### 20. Unbounded output

**The trap.** A tool returns whatever the underlying query produced — a full table, a whole file, an
unpaginated list.

**Why it happens.** Bounding it is extra work and the test dataset was small.

**What it costs.** The caller's context, burned in one call, on real data. The tool becomes unusable
at exactly the scale where it mattered.

**The rule.** Every ability declares its bound — page size, truncation, a hard maximum — and the
playground exercises it against seed data large enough to trigger the bound
(`references/security/mcp-server.md`).

---

## Web apps, websites and libraries

### 21. Client-side-only protection

**The trap.** A route, a section or an action is protected by a check that runs in the browser: a
redirect in a layout, a hidden button, a disabled field.

**Why it happens.** It is the shortest path, it demonstrably works in the browser, and the server-side
equivalent is genuinely more work.

**What it costs.** No protection at all against a direct request, plus a visible flash of protected
content before the redirect. Anything server-rendered is simply public.

**The rule.** The server decides; the client check exists for speed of feedback, never as the gate.
Every protected surface has a server-side test asserting the direct request is refused
(`references/security/web-app.md`).

### 22. The dependency added without a decision

**The trap.** A library is pulled in to solve one small problem — a date format, a slug, a debounce —
and becomes a permanent part of the dependency tree, the bundle, the audit surface and the upgrade
burden.

**Why it happens.** It is one command and it solves the problem immediately.

**What it costs.** For a library or component especially: every consumer inherits it. A transitive
vulnerability, a licence change or an abandoned package becomes the project's problem, in a decision
nobody remembers making.

**The rule.** A dependency of consequence is a `docs/decisions.md` entry with its alternatives — the
rejected options are the part with value later. For libraries and components, the default answer is no:
the dependency budget is stated in the technical plan.

### 23. The breaking change that was not called one

**The trap.** A renamed parameter, a changed default, a stricter validation, a removed public
surface — shipped in a patch or minor release because "nobody was using it that way".

**Why it happens.** The maintainer knows how the surface is meant to be used, and the change is an
obvious improvement.

**What it costs.** Every integration that used it the other way breaks on an update the user believed
was safe. Trust in the project's versioning does not come back easily.

**The rule.** A public surface, once released, is a contract. Removal or incompatible change is a gated
breaking change: recorded in `docs/decisions.md`, reflected in the docs as deprecated/removed with its
replacement, and carried by a major version (SKILL.md "Document every public surface at the moment it
changes").

---

### 24. The site that looks like the last one

**The trap.** A website ships. It is complete, accessible, fast, faithful to its handoff, and it passes
every gate. It also looks like the previous site the same process produced, and like the one before
that, and like a large fraction of everything else built by an assistant that year.

**Why it happens.** Three causes that compound, and none of them is a mistake anyone made. The brief
asks for the aesthetic in adjectives, and an adjective points at the average of everything it has ever
described. Nothing is forbidden, so the model reaches for the patterns most represented in its training
data, which are exactly the patterns readers have learned to recognise as machine-made. And nothing in
the process remembers the previous site: project memory and class memory both exist, cross-project
memory does not, so two similar briefs MUST produce the same site because nothing knows the other one
exists.

**What it costs.** For a site whose job is to sell a person's work, the generic look is not neutral: it
reads as low effort by the very audience the site is trying to convince, and it undoes the credibility
the product earned. It is also the most expensive defect to find late, because nothing is broken — a
rebuild is the only fix, and it lands after launch, when someone finally says out loud that they all
look the same.

**The rule.** `references/phase-8-art-direction.md` runs before the brief, and its gate is the same
shape as every other Keel gate: a definition of done checked item by item, with no advance on an open
✗. The Design Read is declared in a sentence, the four dials are set with reasons, the machine-local
ledger at `~/.keel/art-ledger.md` blocks the last three sites' typeface, palette, hero paradigm, grid
and signature elements, three directions from three named aesthetic families are produced for one
section with at least one deliberate risk, one is chosen and recorded in `docs/decisions.md`, one or
two signature elements are consolidated into `SPEC/art-direction.md`, and the ledger entry is written
at the close. **Mechanical check:** the Phase 4 completeness gate fails a website handoff with no
`SPEC/art-direction.md`, and fails any signature element named there that is absent from the delivered
CSS. The blacklist's em-dash rule is binary and greppable across every string visible on the site.

**What this trap is NOT.** It is not "the design was bad" — the design is usually competent. And the
fix is not loosening the anti-drift discipline that makes Keel work: it is opening one bounded step
where invention is mandatory, closing it with a recorded decision, and resuming the normal regime
unchanged.

---

## The self-audit

Run this against any Keel project at a sprint close, at the Phase 7 gate, at adoption, and whenever a
shortcut is tempting. **Every answer must come from a command or an artifact, never from
recollection** — an answer given from memory is not an answer, it is the trap in entry 7.

1. Does every tool declared in the technical plan actually run in a test-point command, and is it blocking?
2. Does every command cited in `CLAUDE.md`, `AGENTS.md`, the README and `docs/` exist as a real script or CI step?
3. Does every fact in the Version touchpoints list carry the same value everywhere it appears?
4. Does every path in the code map carry its `[E]`/`[A]`/`[G]` marker, and does every `[E]` actually exist on disk?
5. Does every documented extension point have a test asserting it fires with the documented arguments?
6. Does every generated artifact have a consumer, or is the generator gone?
7. Does every row in `docs/05-test-points.md` carry its command and its output?
8. Has the suppression count grown since the last sprint close?
9. Is every deliberate omission recorded — in `docs/decisions.md`, or in the "Not defended" table of `docs/threat-model.md`?
10. Is every control described in the present tense actually `IN PLACE`, with its evidence?
11. Is there exactly one authoritative file per artifact, and does every `*.min.*` match a fresh build of its source?
12. Is every document in `docs/` reachable from an index, and does every internal link resolve?
13. Does every user-visible acceptance criterion have either a driven test with its evidence, or one of the eight delegation tags with its steps — and is there any criterion whose only evidence is a person's verdict without a tag?
14. Does `scripts/keel-doctor --check` pass on this machine, so the suite's green result actually means the suite ran?
15. Was every test written under the project's `Test-first policy:` seen to fail first, for the absent behaviour rather than for a setup error, with its failure line recorded?
16. Did every bug fixed since the last audit start from a failing reproduction test — and can any test derived from an `AC-nn` or a reproduced bug be shown to have been edited to make it pass, without a decision entry behind the change?
17. Does every applicable row of `MANIFEST.md` Table 1 carry a state in `docs/keel-conformance.md`, with every `n/a` quoting the manifest's own condition and every `declined` citing a real decision entry?
17a. Before this session's first WRITE into a repository it did not start, was another session ruled out with `git status --porcelain` plus the modification times of whatever it listed — rather than assumed absent?
17b. Does every append-only log (`docs/decisions.md`, `docs/lessons-learned.md`, `docs/05-test-points.md`) have zero duplicate identifiers, checked by grep rather than by recollection?
17c. Does every check the project relies on state the question it answers — and for any check that has never failed, has it been run against a case that should fail it?
17d. Does every piece of state a guard reads or writes declare its scope — repository or session — and is that the scope the duty it enforces actually has?
17e. For each defect generalised into a rule this release, was every reachable instance of that class swept and the places looked at named — rather than only the instance that was reported?
17f. Before registering any generated script as a native hook in an assistant's settings, was THAT assistant's own documented output contract confirmed — never assumed from a different assistant's, however identical the trigger name?
17g. Does every branch of a tool-detecting launcher fire ONLY the detected tool's own verified action — never a different tool's action substituted as a fallback when the detected tool's own row is absent or unverified?
17h. Where the forge is GitHub and the repository is private, was the account-wide, shared nature of the Actions minutes budget named as its own reason for `CI runs on: main` — not folded silently into "less noise"?
17i. Does every entry in `docs/decisions.md` that asserts an impossibility ("cannot", "there is no", "not possible", "does not support") carry a `Not checked:` line naming an avenue that was not examined — and has every such entry the user has contradicted since been RE-MEASURED rather than restated?
17j. Does every test name state an OUTCOME rather than a mechanism — and for any name that does state a mechanism ("X is last", "Y comes first"), is there a cited source making that mechanism a requirement rather than an assumption?
17k. For every probe a guard acts on, can the caller tell "found nothing" from "could not tell" — and has the parser been run against the input shapes that are not the common case (for `git status --porcelain`: a rename and a quoted path)?
18. (WordPress) Does `wp i18n make-pot` report zero untranslated or wrongly-domained user-facing strings?
19. (WordPress) Does uninstall remove every option, table, meta key and scheduled event the plugin creates?
20. (WordPress) Does every entry point — admin, AJAX, REST, bulk, CLI — check its capability and its nonce?
21. (MCP) Has every ability been called through a real client with its documented arguments this release?
22. (Web) Is every protected surface refused on a direct server request, with JavaScript disabled?
23. (Library) Is every dependency in the manifest backed by a decision entry?
24. (Website) Does `SPEC/art-direction.md` exist with its read, dials, chosen direction and signature elements — is every signature element actually present in the delivered CSS, does `~/.keel/art-ledger.md` carry this site's entry, and does a grep for `—` and `–` across every string visible on the built site return zero?

## Maintaining this file

Two destinations, and the distinction is the whole point:

| What happened | Where it goes |
|---|---|
| A problem specific to THIS project, with its solution | `docs/lessons-learned.md` (memory) |
| A trap that would bite ANY project of this class | **Here, in the skill** (prevention) |

When a project hits something that belongs here, adding the entry to Keel is part of resolving it —
per SKILL.md, an improvement the user agrees to is codified in the skill, not only recorded in the
project. A new entry is not finished until it names its mechanical check, and if that check can live in
`scripts/keel-verify`, it does.

An entry that has never fired on a real project is a guess, and a catalogue of guesses trains readers
to skim. Prefer twenty entries that all happened to fifty that might.
