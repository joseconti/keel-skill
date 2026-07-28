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
15. Does every applicable row of `MANIFEST.md` Table 1 carry a state in `docs/keel-conformance.md`, with every `n/a` quoting the manifest's own condition and every `declined` citing a real decision entry?
16. (WordPress) Does `wp i18n make-pot` report zero untranslated or wrongly-domained user-facing strings?
17. (WordPress) Does uninstall remove every option, table, meta key and scheduled event the plugin creates?
18. (WordPress) Does every entry point — admin, AJAX, REST, bulk, CLI — check its capability and its nonce?
19. (MCP) Has every ability been called through a real client with its documented arguments this release?
20. (Web) Is every protected surface refused on a direct server request, with JavaScript disabled?
21. (Library) Is every dependency in the manifest backed by a decision entry?

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
