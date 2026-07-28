# Adopting Keel in an existing project (brownfield)

Load this when Keel is applied to a project that is **already underway**: there is real code (often already released, often with users), but no `docs/PROGRESS.md` and no Keel artifacts. This is the third entry mode, distinct from the other two:

- **New project** → Phase 1 from zero.
- **Resume** → `docs/PROGRESS.md` exists; follow the fixed reading order in `references/project-state.md`.
- **Adoption (this reference)** → code exists, Keel state does not. Bring the project up to Keel's specifications: ask what must be asked, create every required file, fill everything that can be filled from reality, and record honestly what cannot.

Confirm with the user before starting: "This is an existing project — I'll adopt it into Keel: inventory what exists, ask you what I can't infer, create the state and docs as-built, and audit the gaps against Keel's standards. I won't change any code during adoption."

## Adoption principles (hold throughout)

1. **Document reality; change nothing.** Adoption is read-only for the code: it produces state and docs describing what IS. No refactors, no renames, no "improvements", no drive-by fixes — code changes come afterwards as normal Keel sprints. The single exception: a critical, user-approved emergency (e.g. a tracked secret) may be remediated immediately.
2. **Conventions are observed, not imposed.** The technical plan records the codebase's REAL conventions (prefix, naming, error handling, structure), even if Keel's defaults would differ. Consistency with the existing code beats preference; migrating a convention is a user decision for a later sprint, recorded in `decisions.md`.
3. **Ask, don't assume.** Every Phase 1 decision that was never made explicitly is asked now, batched. What the user doesn't know either is recorded as unknown — not guessed.
4. **Mark inference as inference.** Anything derived from reading code rather than confirmed by the user or a test is labeled `as-built, unverified` in the doc. An unverified section is a candidate for verification when that area is next touched — never silently trusted.
5. **Honest gap audit, no instant fixes.** Gaps against Keel's standards are recorded and prioritized with the user — not silently fixed during adoption, and never hidden to make the project look compliant.

## Steps

### 1. Inventory (read-only)

Walk the project once and record what actually exists:

- Structure and stack: languages, framework/host, minimum versions declared, dependency manifest(s) and pinned versions.
- Released reality: current published version, where it's distributed (wordpress.org, marketplace, npm, deploy), and — critical — the **installed base**: is it in production, with users and stored data? (Adoption almost always means yes: migrations/backward-compat become mandatory per Phase 5.)
- Version touchpoints: every place the version string lives, and whether they currently agree.
- Tests: what exists, how it runs, whether it passes right now (run it — this one execution is allowed and recorded).
- Existing docs: README, changelog (note its ordering), wikis, inline docs — inputs to reuse, not to duplicate.
- License: declared where? Consistent across files?
- i18n reality: are user-facing strings externalized, or hardcoded/concatenated?
- Public surfaces: every function/class/hook/filter/REST route/CLI command/MCP ability intended for external use.
- Git/package hygiene: `.gitignore`/`.gitattributes` present? Anything sensitive tracked? (A tracked secret is the one finding that interrupts adoption for immediate, user-approved remediation.)
- UI surfaces, if any, and whether any design source exists (tokens, styles, a design file).
- Forge issues: does the repo's forge (GitHub, GitLab, Gitea, Bitbucket, any other) have open/closed issues? Count, state, recurring themes — they feed the gap audit and the roadmap.

### 2. Initialize the state and the portability lock

Per `references/project-state.md`, in the existing repo: `docs/PROGRESS.md` (project card filled with the inventory; unknowns marked), `docs/decisions.md`, `docs/lessons-learned.md`. Record the de facto decisions already embodied in the code as D-entries marked **"adopted as-is"** (stack, conventions, license if declared…) so future sessions treat them with the same respect as explicit decisions. Stamp the card's `Keel baseline:` with the running Keel version.

Same as Phase 1 step 0a: create the **portability lock** at the repo root — the same Keel block in `CLAUDE.md` AND `AGENTS.md` (insert between the delimiters if either file already exists — do not touch the rest; Gemini CLI users additionally pick their mirror per the lock section) — and **offer to embed the skill** at `.claude/skills/keel/` + `.agents/skills/keel/` so the project stays governed by Keel from any environment (app, Cowork, Claude Code, Codex, Copilot, Cursor, Gemini CLI, Windsurf, another AI). Record the choice in the project card. In the same batch, ask which assistants work on this repo and offer the **native assistant config package** (`references/assistant-config.md`): the `.gitignore` entries and the confidential-data pre-commit gate can be installed now with approval — they protect from the first commit and touch no code — while rules and agents wait for step 4, because they encode the OBSERVED conventions from the as-built technical plan. If the repo already carries native config for ANY assistant, inventory and keep it — reconcile, never overwrite. Record `Assistant config:` (tools listed) in the project card.

### 3. Ask the user (batched — the Phase 1 decisions that were never made)

Everything Phase 1 would have asked and the inventory couldn't answer, in as few batches as possible: problem/outcome and v1-equivalent scope of what exists; project type (fixes the security profile and accessibility reference to load NOW, like any Phase 1); license if unclear; i18n intent vs the code's reality; targeted accessibility level; installed base confirmation and upgrade obligations; docs language (English by default for token economy — adopted projects usually have existing docs: if they are in another language, offer a one-time full translation to English per SKILL.md "Token economy"); design system / brand identity (Phase 1 step 9 — existing, founding, or one-off); project website intent. Offer the **competitive scan** (Phase 1 step 0) as recommended-but-optional for adoption: it feeds the roadmap rather than gating it; if skipped, record that with the standard warning, minus the blocking.

### 4. Reconstruct the artifacts, as-built

Create the Keel artifacts describing what exists — filling everything inferable, marking the rest:

- `docs/01-discovery.md` — retroactive, using the normal template, headed **"Adopted project — reconstructed as-built"**. Contains the step 3 answers and the inventory's findings.
- `docs/02-functional-spec.md` — the REAL features, main flows, data model, integrations, permissions. Depth rule: enough to work safely now; deepen per area when that area is next touched (**progressive backfill**), rather than halting the project for weeks of retro-documentation. Unverified inferences labeled.
- `docs/03-technical-plan.md` — the real stack and versions, the real code map (every path, one line, each row marked `[E]` since it exists — an adopted project starts almost entirely `[E]`, and anything the audit says must still be built is `[A]`), the **change map** built from the change types this codebase actually has (per `references/phase-2-functional-spec.md` step 4b — in an adopted project it is often the single most valuable artifact produced, because the "what else do I have to touch" knowledge currently lives only in the maintainer's head), the **observed** conventions, the real test/build/lint commands (verified by running them in step 1), the real version touchpoints, the license-compatibility rule applied to the existing dependency list.
- `docs/api/INDEX.md` — **complete**, one line per existing public surface. This one is not progressive: it is cheap, and the Phase 5 reuse rule depends on it. Full per-surface docs (`docs/api/`, `docs/reference/`) are backfilled progressively — each surface gets its complete doc the first time a slice touches it — unless the user explicitly wants a documentation sprint now.
- `docs/issues.md` — if the forge has issues: the initial inventory (open issues at least; closed history optional), per `references/project-state.md`. Entries are added as issues are actually worked, from here on.
- If there is a pre-existing UI with no design handoff: do NOT invent a retroactive BUILD-SPEC. Record in PROGRESS.md that the UI predates Keel and has no design contract; the current look is the baseline. From the next UI change on, the normal rules apply (a redesign goes through Phases 3–4; small changes respect the baseline and the design-system decision from step 3).

With the as-built technical plan written, materialize any accepted assistant config rules/agents from the OBSERVED conventions, in every accepted tool's container (per `references/assistant-config.md`, "Adoption specifics").

### 4a. The conformance sweep — every applicable requirement, from the manifest, one by one (BLOCKING)

This is the step that makes "apply Keel to this repo" mean the whole of Keel, not the part this session happened to remember. It is not optional, it is not a summary, and it is not answered from knowledge of what the skill contains: **it is read off `MANIFEST.md`, row by row.**

1. **Enumerate.** Read `MANIFEST.md` Table 1 in full. For every row, decide whether it applies at this project's position and under its recorded conditions. An adopted project sits at "Phases 1–2 adopted (as-built)", so most Phase 1–2 rows apply immediately and the Phase 5–7 rows apply as the project reaches them — but the ones tied to a recorded choice (the assistant config package, the end-user guide, the docs theme, a client budget) apply the moment their condition is true, whether or not this session finds them interesting.
2. **Write `docs/keel-conformance.md`.** One row per applicable requirement:

   ```
   | Requirement (MANIFEST Table 1) | State | Where / decision | Notes |
   |---|---|---|---|
   | docs/PROGRESS.md | present | docs/PROGRESS.md | — |
   | scripts/keel-doctor | missing | — | proposed to the user 2026-… |
   | guide/ | declined | D-014 | user prefers the existing wiki |
   | docs/budget.md | n/a | Client budget: no | condition not met |
   ```

   Four states, and every row has exactly one: `present`, `missing`, `declined` (with the `docs/decisions.md` entry number), `n/a` (with the condition that excludes it). A row left blank is an unfinished sweep, not a pass.
3. **Present every `missing` row to the user in ONE batch**, each with a one-line explanation of what it is, what it costs, and what changes if it is skipped. Then let them decide row by row — or accept the whole batch, which is what most people do. **Applying is their choice; proposing is not.** The failure this step exists to end is the one where a subset gets applied, nobody mentions the rest, and the omission only surfaces when the user asks why something is missing.
4. **Record each refusal as a decision entry** and set the row to `declined`. A declined row is a decision the project can point at; a forgotten row is a hole nobody can distinguish from an intentional choice six months later.
5. **Report the sweep to the user in full** — applied / declined / not applicable, with the totals. "Keel adopted" without that table is a claim, and this skill does not accept claims.
6. **Wire the check.** When `scripts/keel-verify` is created (Phase 5 scaffold, or now if the project already has one), it verifies this file: every requirement applicable at the current position is `present`, or `declined` with a real decision entry, or `n/a` with its condition. From then on the sweep is enforced by a command, not by anyone's diligence.

The same sweep runs — identically, from the same manifest — in the post-update reconciliation when a project moves to a newer Keel version, using Table 3's per-version delta on top of Table 1 (`references/keel-maintenance.md`).

### 5. Gap audit → `docs/04-adoption-audit.md`

Audit the as-built reality against Keel's standards and record every gap honestly — this file only exists in adopted projects:

- **Security:** the loaded profile's checklist against the real code (unescaped output, missing nonces/capabilities, unprepared queries, missing ABSPATH guards, secrets handling…).
- **Accessibility** (if UI): the targeted level vs reality, per `references/accessibility.md`.
- **i18n:** hardcoded/concatenated strings vs the step 3 decision.
- **Duplication:** near-duplicate functions/classes (defects per the reuse rule).
- **Extensibility** (extensible types): missing filters/actions per the Phase 5 density rule.
- **Docs:** public surfaces with no documentation (now visible via INDEX).
- **Hygiene:** `.gitignore`/`.gitattributes` gaps, tracked secrets (critical), version-touchpoint mismatches, changelog ordering.
- **Testability:** does a playground exist and does it start? Is there a driver per user-visible surface? Does `scripts/keel-doctor` exist and pass, and does `scripts/keel-verify`? Do interactive elements carry stable test identifiers, or is every test bound to visible text? How many acceptance criteria (once reconstructed) have a driven test rather than a person's verdict? On a released project the honest answer is usually "none of it exists", and that is a normal, high-value finding: without an environment and drivers, every future bug report becomes "install this and tell me if it works". Building them is a remediation item like any other, and usually the first one worth doing.
- **Known traps:** run the self-audit from `references/anti-patterns.md` against the real tree — every answer evidenced by a command or an artifact, never by reading the code and forming an impression. This is where adoption pays off fastest: a project that predates Keel has usually accumulated several of these silently (a declared tool nothing runs, a documented command that no longer exists, a version pinned in five places, a documented hook that is never fired, a generated file nobody imports), and each one is a concrete finding rather than a vague "needs tidying".
- **Threat model:** produce `docs/threat-model.md` from the loaded profile and the real code, with every control at its HONEST delivery state — an adopted project typically has more `TO BUILD` than `IN PLACE`, and writing that down accurately is the point. The "Not defended" table converts what was silent into decisions the user can weigh.

For each gap: what, where, severity, and the standard it fails. Then **prioritize with the user** into three buckets, recorded in the file and mirrored in PROGRESS.md: fix now (a remediation sprint), fix when touched (bound to the area's next slice), accepted (recorded with the reason — honest, not hidden).

### 6. Continue as a normal Keel project

Mark Phases 1–2 as **"adopted (as-built)"** in PROGRESS.md's phase table, set the next action, and proceed with the standard machinery: remediation and new work planned as Phase 5 sprints (with test points, commits, INDEX upkeep); new features get their slice of discovery/spec first; UI changes respect the design-system decision; the **next release runs the full Phase 7** — which is where the remaining hygiene bucket naturally closes. If the user needs to quote any of this planned work to a client, run `references/estimation-budget.md` on that scope — AI hours plus vibe coder hours, never traditional human development time — creating its token ledger from that point on.

## Definition of done (adoption)

- State files exist and reflect the inventory; de facto decisions recorded as "adopted as-is".
- The portability lock is in place — the same Keel block in `CLAUDE.md` and `AGENTS.md` (with the embed and assistant-config choices recorded in the project card) — so every future environment/AI opening this repo is bound to the workflow.
- The step 3 questions are answered (or recorded as unknown), including project type + loaded security profile and accessibility reference, license, i18n, docs language, design system, website intent.
- `docs/01-discovery.md`, `docs/02-functional-spec.md`, `docs/03-technical-plan.md` exist as-built, with every unverified inference labeled.
- `docs/api/INDEX.md` complete for every existing public surface; progressive backfill rule recorded for full per-surface docs.
- **`docs/keel-conformance.md` exists and is complete (step 4a):** every requirement applicable at this position enumerated FROM `MANIFEST.md` — never from recollection — and carrying exactly one state (`present` / `missing` / `declined` with its decision entry / `n/a` with its condition). Every `missing` row was presented to the user in one batch and ended in a decision; the full sweep table was reported to the user. Adoption does not pass this gate with an unexplained gap.
- `docs/04-adoption-audit.md` complete, every gap prioritized with the user (now / when touched / accepted), mirrored in PROGRESS.md.
- The `references/anti-patterns.md` self-audit was run against the real tree with every answer evidenced, and its findings are gaps in the audit like any other.
- `docs/threat-model.md` exists with controls at their honest delivery state and a "Not defended" table — no control described in the present tense that is not `IN PLACE` with its evidence.
- If the forge has issues: `docs/issues.md` exists with the initial inventory.
- No code was changed (except a user-approved critical remediation, recorded).
- PROGRESS.md shows Phases 1–2 "adopted (as-built)", the current position, and an executable next action.
