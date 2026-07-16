# Native assistant project configuration — optional package

Load this reference at three moments, and only these: (a) Phase 1 step 0a (or adoption step 2), when the package is OFFERED; (b) the close of Phase 2 (adoption: after its step 4), when rules and agents are MATERIALIZED; (c) the Phase 5 scaffold, when permissions, the pre-commit gate, the MCP registration, and the CI workflow are COMPLETED.

Modern coding assistants load certain project files natively: modular rules (path-scoped where the tool supports it), project subagents, committed permission allow-lists, and MCP server registrations. Keel can generate these from decisions the project has ALREADY made, so sessions running in ANY accepted assistant — Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Gemini CLI, Windsurf — get the project's conventions, security profile, and quality gates enforced ergonomically, without re-reading the full technical plan into context every time. The principle throughout: **one source of content, one container per assistant** — the substance is identical everywhere; only the file path and frontmatter differ.

## Position in the workflow (read this first)

- **The lock (`CLAUDE.md` + `AGENTS.md`) remains the universal mechanism.** Native config is loaded only by its own tool. Nothing critical to the workflow may live ONLY in a tool's config tree: the lock and the `docs/` state remain the source of truth in every environment. This package is reinforcement and ergonomics, never a replacement.
- **Token economy applies.** Rules without a path/glob filter load into EVERY session's context. Therefore: every generated rule is path-scoped by default (where the tool supports scoping), kept short (target under 40 lines), and points to the authoritative `docs/` file instead of duplicating its body. A rule that restates the whole technical plan is a defect.
- **Content derives from recorded decisions only.** Rules and agents are generated FROM `docs/03-technical-plan.md`, the loaded security profile, and Keel's own quality gates. Never invent new policy inside a rule — if something is worth enforcing, it goes into the plan or `docs/decisions.md` first, then into the rule.
- **Parity across tools is a duty.** When a recorded decision changes a source, EVERY accepted tool's container updates in the same change — two assistants reading different conventions is a defect. This is exactly why the content lives in `docs/` and the containers stay thin.
- **The whole package is optional and per-project.** Offered once, recorded once, never nagged about again.

## The offer (one batched question — Phase 1 step 0a / adoption step 2)

Alongside the existing embed-the-skill question, ask ONCE: (a) **which assistants will work on this repo** — Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Gemini CLI, Windsurf, others (any set; solo developers usually name one or two); and (b) whether the project should carry their native configuration, presenting the pieces and their value in two or three lines. The user may take all of it, part of it, or none. Record both in the project card:

```
Assistant config: [none / rules / rules+agents / full] (tools: claude, codex, copilot, cursor, gemini, windsurf, ...)
```

(`full` = rules + agents + permissions + pre-commit gate + MCP registration and the CI workflow when applicable. The gate and CI are tool-agnostic — one each per project, never one per assistant.) Record a D-entry in `docs/decisions.md` with what was accepted. In the same breath, tell the user once that every tool has PERSONAL, non-committed config — `CLAUDE.local.md` and `.claude/settings.local.json` (Claude), a per-directory `AGENTS.override.md` (Codex), user-level directories under `~` (all tools): Keel never creates them (they are the user's own), but always adds the repo-resident ones to `.gitignore` so they can never be committed by accident (see "Personal files and `.gitignore`" below).

Do not block on this question: if the user defers, record `Assistant config: none (deferred)` and move on — the package can be added later from this reference at any phase boundary. Tools not in the accepted list get NOTHING generated: a config tree no tool will read is noise, not coverage. Adding a tool later is a normal recorded change — generate its containers from the same sources at the next phase boundary, and add its card entry.

## Pieces, sources, and timing

| Piece | Generated from | Created at | Updated when |
|-------|----------------|-----------|--------------|
| Rules (one container per accepted tool) | `docs/03-technical-plan.md` §Conventions + the loaded security profile + Keel quality gates | Phase 2 close (adoption: after its step 4) | A recorded decision changes a source — same change, every container, never silently |
| Subagents (per capable tool) | Same sources + `docs/api/INDEX.md` discipline | Phase 2 close (adoption: after its step 4); `launch-verifier` only with website intent — or at Phase 8 start on first need; `guide-qa` only when the end-user guide decision is yes — at Phase 6 on first need | Same rule |
| Permission allow-lists (per capable tool) | Technical plan §Tooling commands + playground commands | Phase 5 scaffold, ALWAYS confirmed with the user | Tooling/playground commands change |
| `.githooks/pre-commit` (one per project) | SKILL.md "Confidential data never reaches Git" | Phase 5 scaffold (adoption: immediately, with approval) | The gate's patterns need tightening (recorded) |
| CI workflow (one per project, e.g. `.github/workflows/ci.yml`) | Technical plan §Tooling commands — the same verified source as the allow-lists | Phase 5 scaffold, if the forge supports CI | The plan's verified commands change |
| MCP registration (per capable tool) | Technical plan — ONLY if it defines development MCP servers | Phase 5 scaffold, confirmed | The dev MCP set changes |

Everything in the table is repo-only: Phase 7 marks every generated config tree `export-ignore` alongside the existing workflow files, so none of it ships in the distributable.

## The container matrix — which file, per assistant

| Piece | Claude Code | OpenAI Codex | GitHub Copilot | Cursor | Gemini CLI | Windsurf |
|---|---|---|---|---|---|---|
| Rules, path-scoped | `.claude/rules/*.md` (frontmatter `paths:`) | nested `AGENTS.md` in each source dir | `.github/instructions/*.instructions.md` (frontmatter `applyTo:`) | `.cursor/rules/*.mdc` (frontmatter `globs:`) | nested `GEMINI.md` in each source dir | `.windsurf/rules/*.md` (frontmatter `trigger: glob`) |
| Subagents | `.claude/agents/*.md` | — (inline fallback; optional `[agents.<name>]` roles in `.codex/config.toml`) | `.github/agents/*.agent.md` | `.cursor/agents/*.md` — also reads `.claude/agents/` natively | `.gemini/agents/*.md` | — (inline fallback) |
| Permission allow-list | `.claude/settings.json` | `.codex/rules/*.rules` (trusted projects only) | — (not committable) | `.cursor/cli.json` | `tools.allowed` in `.gemini/settings.json` | — (not committable) |
| MCP servers | `.mcp.json` (repo root) | `[mcp_servers]` in `.codex/config.toml` | `.vscode/mcp.json` | `.cursor/mcp.json` | `mcpServers` in `.gemini/settings.json` | — (user-level only) |

Notes the generators must respect:

- **A "—" cell removes the mechanism, never the duty.** No subagents → the session runs the same checks inline and says so (the standing fallback). No committable allow-list → the verified commands are documented in the repo's development notes (e.g. the README's development section) instead. No repo MCP file → the server setup goes in `docs/playground.md` for the user to register at user level.
- **Size limits:** Codex reads roughly the first 32 KiB of combined `AGENTS.md` content by default; Windsurf caps a rule file at 12,000 characters; Cursor recommends rules under 500 lines; Copilot caps an agent file at 30,000 characters. Keel's under-40-lines rule keeps every generated piece far inside all of them — the limits matter only if the user asks for more.
- **Syntax rots.** Every one of these tools evolves its config format continuously. The CONTENT below is Keel's contract; the container is the tool's. When in doubt about a frontmatter key or file location, verify against the tool's current documentation rather than guessing.
- **Gemini CLI and the lock:** Gemini reads `GEMINI.md`, not `AGENTS.md`, by default. When Gemini is an accepted tool, the lock section of `references/project-state.md` already covers it (a `GEMINI.md` mirror, or `context.fileName` in `.gemini/settings.json` including `AGENTS.md` — the user's pick, recorded). The nested-rules mechanism here uses whichever context filename that decision fixed.

## Rules — three rules' worth of content, one container per tool

Generate exactly these three rules by default (more only on explicit user request). The canonical content templates below are written once; materialize one copy per accepted tool in its container from the matrix, adapting ONLY the frontmatter/scoping mechanism. Scope every rule to the source globs from the technical plan's code map (e.g. `includes/**/*.php`, `src/**/*.ts`) so they load only when code is actually touched.

**`code-style`** — the conventions, distilled:

```markdown
---
paths:
  - "[source globs from the code map]"
---

# Code style — [Project name]

Source of truth: docs/03-technical-plan.md §Conventions. On any conflict, the plan wins — fix this file.

- Prefix/namespace: every function, class, option, and hook uses `[prefix]`.
- Naming: [the recorded patterns — functions / classes / files / hooks].
- Error handling: [the ONE recorded strategy]. Never mix strategies.
- Logging: [mechanism + levels]; never log secrets.
- Base language of source strings: English ([i18n mechanism + text domain per the plan]).
- Comments: every public surface carries its docblock in [the platform's convention — e.g. PHPDoc / JSDoc / docstrings] (purpose, params, return); comment the why on non-obvious decisions, not the what. English by default, per the recorded language policy.
```

**`security`** — the loaded profile, distilled to its DO/DON'T core (about ten bullets maximum — e.g. for WordPress: sanitize input, escape output at print time, nonce + capability on every state change, `$wpdb->prepare`, ABSPATH guard, no secrets in code or logs). End with: `Full profile: the Keel security reference for this project type governs; this file is the reminder, not the standard.`

**`docs-discipline`** — Keel's build gates where they bite:

```markdown
---
paths:
  - "[source globs from the code map]"
---

# Build discipline — [Project name]

- Before writing ANY new function/method/class: grep docs/api/INDEX.md first; reuse or generalize an existing fit — a near-duplicate is a defect.
- Every new public surface is documented in docs/api/ or docs/reference/ AND gets its INDEX.md row in the same slice, with a runnable example.
- [Extensible types only:] user-facing strings filterable, before/after actions on decisions, filterable queries/responses, prefixed.
- Update docs/PROGRESS.md and docs/decisions.md at the moment of change, never later.
```

Per-container adaptation (content identical, header differs):

- **Claude Code** — as written above (`paths:` list in the frontmatter).
- **Cursor** — `.cursor/rules/<name>.mdc` with `description: [one line]`, `globs: [the same globs]`, `alwaysApply: false`.
- **Copilot** — `.github/instructions/<name>.instructions.md` with `applyTo: "[the same globs, comma-separated]"`.
- **Windsurf** — `.windsurf/rules/<name>.md` with `trigger: glob` and `globs: [the same globs]`.
- **Codex / Gemini CLI** — no glob mechanism exists: place ONE nested context file (`AGENTS.md` for Codex, the project's context filename for Gemini) in each top-level source directory from the code map (e.g. `includes/`, `src/`), containing the three rules' content concatenated, headed by `Scope: this directory's code.` Do NOT also duplicate the content into the root lock — nested files load only when that directory is touched, which is the whole point.

## Subagents — eight project verifiers, defined once

The canonical definitions are markdown files with YAML frontmatter (`name`, `description`, `tools`). Give them read-only tools (`Read, Grep, Glob`) — they flag, they never fix; the verifiers that must EXECUTE to verify (run the playground, fetch the deployed site, run accessibility tooling) add `Bash`/`WebFetch` on top and still never write. Do NOT pin a `model:` (model names age; inherit the session's). The `description` must say WHEN to use the agent — every tool that supports project subagents delegates based on it.

Materialize into each capable container from the matrix: `.claude/agents/*.md` (Claude Code — and Cursor reads this tree natively, so when Cursor is accepted ALONGSIDE Claude, one tree serves both; generate `.cursor/agents/` only when Cursor is accepted without Claude), `.github/agents/<name>.agent.md` (Copilot), `.gemini/agents/*.md` (Gemini CLI). The frontmatter keys are near-identical across the three (name, description, tools); adapt mechanically, never fork the body. Codex has no markdown project subagents — its sessions run the checks inline (the fallback below); optionally, delegation-only roles can be declared in `.codex/config.toml` if the user wants them. Windsurf: inline fallback.

All of them materialize together at Phase 2 close (adoption: after its step 4), except `launch-verifier` — generated only when Phase 1 recorded website intent, or at Phase 8 start on first need — and `guide-qa` — generated at Phase 6 on first need, once the end-user guide decision is yes (the decision does not exist earlier). The conditional agents (`design-fidelity-auditor`, `playground-qa`, `launch-verifier`, `a11y-auditor`, `guide-qa`) are generated only for projects meeting their condition — an agent the project can never use is noise, not coverage.

**`code-reviewer.md`**:

```markdown
---
name: code-reviewer
description: Reviews a slice or diff of [Project name] against the recorded conventions and Keel quality gates. Use after completing a slice, before its commit.
tools: Read, Grep, Glob
---

You review code for [Project name] against its recorded contracts. You flag; you never rewrite.

Check in order: (1) conventions per docs/03-technical-plan.md §Conventions — prefix, naming, error handling, logging; (2) reuse — no near-duplicate of anything in docs/api/INDEX.md; (3) i18n — no hardcoded or concatenated user-facing strings; (4) accessibility on UI slices, per the project's targeted level; (5) docs — every new public surface has its doc AND its INDEX.md row; (6) extension points on extensible types; (7) comments — every public surface in the diff carries its docblock per the platform's convention (purpose, params, return), non-obvious decisions carry a why comment, and comment language follows the recorded policy (English by default).

Report: file:line — what fails — which recorded rule it violates. Order by severity. If everything passes, say so in one line.
```

**`security-auditor.md`** — same skeleton; description: "Audits changes against the [type] security profile. Use before any commit touching input handling, auth, data writes, or external calls." Body: the distilled profile checklist (same ten bullets as the rule), plus: verify no secret, credential, key, or real personal data appears in the changed files. Report file:line + risk + rule.

**`docs-verifier.md`** — same skeleton; description: "Verifies docs/api/INDEX.md and docs/api/ + docs/reference/ are one-to-one. Use at test points and sprint closes." Body: every INDEX row has its doc; every doc has its row; every public surface in the diff appears in both; examples reference symbols that exist. Report mismatches as slice defects.

**`design-fidelity-auditor.md`** — UI projects only; same skeleton, read-only. description: "Verifies the built UI against docs/BUILD-SPEC.md and the design handoff, screen by screen. Use at Phase 4 Step 7 (the fidelity walk) and whenever fidelity is in doubt." Body: read `docs/BUILD-SPEC.md`, `docs/design/design-handoff/`, and the built UI code; verify per screen: (1) computed/token values against the BUILD-SPEC token table (§3), (2) every state row of the state matrix (§4) present and reachable, (3) every asset referenced without build-side transformation. Report screen + file:line — expected vs built. Findings become defects or Design Requests — never silently fixed.

**`playground-qa.md`** — projects with a playground; skeleton plus `Bash` (it executes, it never edits). description: "Runs docs/playground.md literally, with fresh context. Use at sprint closes and at the Phase 7 gate." Body: receive ONLY `docs/playground.md` and follow it to the letter — start commands, every try-it flow, teardown. Report every point where reality diverges from the document: a command that fails, a step that assumes unstated context, a flow that dead-ends. An instruction gap is a defect exactly like a code bug — the document, not the reader, gets fixed.

**`launch-verifier.md`** — website projects (Phase 8); skeleton plus `Bash`/`WebFetch` (it fetches, it never edits). description: "Crawls the deployed site and returns the launch verification table. Use at the Phase 8 launch checklist." Body: from `sitemap.xml`, fetch every page; parse every head (title, description, OG — present and unique per page); validate the JSON-LD; fetch the well-known files; check the security headers. Report the pass/fail table that feeds `<site-docs>/launch-report.md`, one row per check with its evidence.

**`a11y-auditor.md`** — UI and website projects; skeleton plus `Bash` (it runs tooling, it never edits). description: "Runs the automated accessibility pass and prepares the guided assistive-technology script. Use before Phase 4's definition of done and at the Phase 8 launch checklist." Body: run the automated pass (axe-core / pa11y / the platform inspectors) across the screens or the full sitemap URL list, recording command + result; prepare the step-by-step script for the guided assistive-technology pass the user will run (the guided loop in `references/accessibility.md`). Report findings by severity; automated coverage is partial by design — the guided pass closes the rest.

**`guide-qa.md`** — projects with an end-user guide (the Phase 6 decision is yes, not declined); same skeleton, read-only. description: "Verifies the end-user guide (guide/) against the product's capability and settings lists, with fresh context. Use at the Phase 6 guide check and at the Phase 7 gate when the guide ships in the package." Body: receive ONLY `guide/` plus the v1 capability list (`docs/01-discovery.md` / `docs/02-functional-spec.md`) and the settings list (`docs/usage/configuration.md`); verify: (1) mechanical coverage — every capability and every setting has its guide section, and troubleshooting covers the debug-log switch; (2) every internal link and image resolves inside `guide/` — nothing external, per the offline rule; (3) every task's steps are followable exactly as written — no step assumes context the guide never gave; (4) per-locale orthography is perfect and secondary locales mirror the principal's structure; (5) the guide's own HTML meets the accessibility basics (semantic structure, heading outline, alt text on every image). Report each gap as a Phase 6 defect — the guide, never the reader, gets fixed.

This file DEFINES the agents; the phase references INVOKE them: Phase 4 Step 7, Phase 5 test points and sprint closes, the Phase 6 guide check, the Phase 7 gate, the Phase 8 launch checklist. If the environment provides no subagents (Codex, Windsurf, or any tool without them), the session runs the same checks inline and says so — the check never disappears with the mechanism.

## Permission allow-lists — minimal, ALWAYS confirmed

Committed permissions affect every person and session that opens the repo, so these files are never written silently: build the proposed allow-list ONLY from the technical plan's verified tooling commands and the playground's documented start/stop commands, show it to the user, and write it only on their confirmation — once per accepted tool that supports a committable list.

**Claude Code** — `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(composer test:*)",
      "Bash(wp-env start)",
      "Bash(wp-env stop)"
    ]
  }
}
```

**Gemini CLI** — the same commands as `tools.allowed` entries in `.gemini/settings.json` (e.g. `"run_shell_command(composer test)"`). **Cursor** — the same commands under `permissions.allow` in `.cursor/cli.json` (CLI sessions; the IDE keeps permissions at user level). **Codex** — `prefix_rule` entries in `.codex/rules/*.rules`, `decision = "allow"`, one per verified command prefix; note to the user that Codex applies repo config only to projects the user has marked trusted. **Copilot / Windsurf** — no committable equivalent: document the verified commands in the repo's development notes instead.

Rules for every tool: exact commands or tight prefixes only — never a catch-all wildcard, never a deny-list pretending to be a policy. Permission-rule syntax evolves with each tool; when in doubt, verify against the current settings documentation rather than guessing. If the user wants no committed permissions, skip the files entirely — their absence is a valid state.

## The confidential-data pre-commit gate — `.githooks/pre-commit`

The assistant's own pre-commit check (SKILL.md "Confidential data never reaches Git") still runs in every session — this hook is the NET under it, and it also covers commits made outside Keel sessions (the user's own terminal, another tool). A classic git hook was chosen deliberately over an assistant-specific hook: it fires in EVERY environment and editor — Claude Code, Codex, Copilot, Cursor, Gemini, Windsurf, a bare terminal — which is exactly Keel's portability principle. One gate per project, never one per assistant.

Install at the scaffold: commit the script at `.githooks/pre-commit` (executable), run `git config core.hooksPath .githooks`, and record in the project card that the gate is active. `core.hooksPath` is per-clone: document the one-line setup in the project's developer notes (e.g. the repo README's development section) so collaborators run it too. Then VERIFY the gate: stage a synthetic secret, confirm the commit is blocked, and remove the synthetic file. Assemble the synthetic secret when creating the test file — an `api_key`-style assignment (equals sign, then `sk-` plus at least 20 letters); this reference deliberately never writes that assignment verbatim, so the skill's own files never trip the gate. An unverified gate is not a gate.

```sh
#!/bin/sh
# Keel confidential-data gate — blocks commits that stage secrets.
# Rule source: Keel SKILL.md "Confidential data never reaches Git".
# Bypass policy: fix the finding, or record the user's explicit OK in
# docs/decisions.md and repeat that single commit with --no-verify.

files=$(git diff --cached --name-only --diff-filter=ACM)
[ -z "$files" ] && exit 0

fail=0
IFS='
'

# 0)+1) Suspicious names — skipping the canonical trees that legitimately
# CONTAIN the gate's own patterns: the gate's script and the embedded Keel
# skill (either tree). The assistant-side check (Keel SKILL.md) still scans
# them; only this net skips them.
for f in $files; do
  case "$f" in .githooks/*|.claude/skills/*|.agents/skills/*) continue ;; esac
  base=$(basename "$f")
  case "$base" in
    .env|.env.*|*.pem|*.key|*.p12|*.pfx|id_rsa*|*credential*|*secret*|*.sql|*.sqlite|wp-config.php)
      printf 'BLOCKED (name): %s\n' "$f"; fail=1 ;;
  esac
done

# 2) Secret-shaped content in the STAGED blob (not the working tree)
pat="-----BEGIN [A-Z ]*PRIVATE KEY-----|api[_-]?key[\"']?[[:space:]]*[:=]|Bearer [A-Za-z0-9._~+/=-]{20,}|AKIA[0-9A-Z]{16}|sk-(proj-)?[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{36,}|xox[baprs]-[A-Za-z0-9-]{10,}"
for f in $files; do
  case "$f" in .githooks/*|.claude/skills/*|.agents/skills/*) continue ;; esac
  if git show ":$f" 2>/dev/null | LC_ALL=C grep -Eqa -e "$pat"; then
    printf 'BLOCKED (content): %s matches a secret pattern\n' "$f"; fail=1
  fi
done

[ "$fail" -eq 0 ] && exit 0

cat <<'MSG'

Commit stopped by the Keel confidential-data gate.
A staged file looks like it carries secrets, credentials, keys, or real
personal data. Options, in order:
  1. Unstage it and add it to .gitignore (never tracked).
  2. Already tracked: git rm --cached <file> + .gitignore, commit the removal.
  3. Ever pushed: purge it from history (git filter-repo / BFG) AND rotate
     the credential — ignoring it is not enough.
  4. Genuinely safe (placeholders, sandbox keys meant to ship): record the
     user's explicit OK in docs/decisions.md, then repeat this one commit
     with --no-verify.
MSG
exit 1
```

False positives are kept rare by design — field-tested: (1) the gate itself exempts the canonical trees that legitimately contain the very patterns it searches for, `.githooks/` (its own script) and the embedded skill (`.claude/skills/` and `.agents/skills/`, including this reference), while the assistant-side check still scans them like everything else; (2) never CREATE a false positive when writing — in `docs/decisions.md`, `docs/lessons-learned.md`, comments, or any project note, a secret-shaped string is described or split apart (`api` + `_key`), never pasted verbatim (SKILL.md "Confidential data never reaches Git", point 5). The occasional remaining case (e.g. a legitimate `class-secrets-manager.php`) is handled by the conscious bypass policy above, on the record. Never loosen the patterns to avoid a one-time bypass. If the user also wants an assistant-side hook on top (Claude Code, Codex, Gemini CLI, and Cursor all offer native pre-tool-use hooks that can gate `git commit`), add it for their accepted tools — but the git hook is the baseline and never replaced by it.

## The CI workflow — conditional, forge-side

Generated at the Phase 5 scaffold when the package was accepted and the project's forge supports CI (GitHub Actions or the forge's equivalent). ONE workflow, running on push and on pull request: install → lint → build → the FULL test suite — the technical plan's EXACT verified commands, the same verified source as the permission allow-lists, never invented — plus a secret scan (gitleaks) and `scripts/keel-verify`. A command that is not in the plan and verified does not enter the workflow.

Why it exists when the pre-commit gate already does: the gate is per-clone (`core.hooksPath` is configured checkout by checkout) — CI is the net that fires in every environment, on every push, including commits made where no hook and no Keel session was present. That is exactly the portability argument this file already makes for the gate, one level up.

## MCP registration — conditional, per capable tool

Create it ONLY when `docs/03-technical-plan.md` defines MCP servers used during development (e.g. the project's own MCP server under test, or a WordPress content MCP for the playground). Confirm with the user before writing. Register the same server set once per accepted tool that supports a repo-level file, per the container matrix.

**Claude Code** — `.mcp.json` at the repo root:

```json
{
  "mcpServers": {
    "[server-name]": {
      "command": "npx",
      "args": ["-y", "[package]"],
      "env": { "API_KEY": "${PROJECT_API_KEY}" }
    }
  }
}
```

**Cursor** — the same object in `.cursor/mcp.json`. **Copilot / VS Code** — the same servers under the `servers` key in `.vscode/mcp.json`. **Gemini CLI** — the same servers under `mcpServers` in `.gemini/settings.json`. **Codex** — `[mcp_servers.<name>]` tables in `.codex/config.toml` (trusted projects). **Windsurf** — no repo-level file: put the server setup in `docs/playground.md` for the user to register at user level.

Hard rule, every container: NEVER a literal secret — each tool's environment-expansion form only (e.g. `${VAR}`; adapt to the container's syntax), with the variable documented in `docs/playground.md`. If a tool offers no expansion mechanism for a needed secret, that server is NOT committed for that tool — user-level registration instead. Every MCP file passes through the same confidential-data gate as everything else. If the project needs no dev MCP servers, these files simply do not exist — do not create empty ones.

## Personal files and `.gitignore`

Unconditional entries (they apply even when the whole package was declined): `CLAUDE.local.md`, `.claude/settings.local.json`, and `.keel-update-check`. Per accepted tool, add its repo-resident personal/transient files: `AGENTS.override.md` (Codex — the user's personal per-directory override), `.gemini/.env` and `.gemini/tmp/` (Gemini CLI). User-level config under `~` never enters the repo, so it needs no entry. Keel never creates any personal file — they are the user's own; the entries only make them uncommittable.

## Adoption specifics

- Rules and agents materialize AFTER adoption step 4, because their source is the as-built technical plan — and they encode the OBSERVED conventions (adoption principle: conventions are observed, not imposed), even where Keel's defaults would differ.
- The pre-commit gate and the `.gitignore` entries can be installed immediately at adoption step 2 with the user's approval — they protect from the first commit and impose nothing on the code.
- If the adopted repo already carries native config for ANY assistant (`.claude/`, `.cursor/`, `.github/instructions/`, `.github/agents/`, `.gemini/`, `.codex/`, `.windsurf/`, nested `AGENTS.md` files), treat it like existing code: inventory it, keep it, and reconcile — never overwrite. Conflicts between existing rules and the as-built plan are surfaced to the user and recorded, exactly like any other adoption gap.

## Definition of done (this reference)

- The offer was made once (0a / adoption step 2), and the project card carries the `Assistant config:` line with the accepted tools listed and a D-entry for what was accepted.
- Accepted rules/agents exist in EVERY accepted tool's container, are path-scoped (where the tool scopes), under ~40 lines each, generated from recorded decisions, and point to their `docs/` sources instead of duplicating them — identical substance across containers.
- Permission allow-lists, if accepted: built only from verified plan/playground commands and explicitly confirmed by the user before writing, one per capable accepted tool.
- The pre-commit gate, if accepted: installed (`.githooks/pre-commit` + `core.hooksPath`), VERIFIED by blocking a synthetic secret, and its collaborator setup line documented.
- MCP registration exists only if the plan defines dev MCP servers, carries no literal secret in any container, and was confirmed.
- The CI workflow, if accepted and the forge supports CI: one workflow, on push and PR, running the plan's EXACT verified commands (install → lint → build → full test suite) plus the secret scan and `scripts/keel-verify` — nothing invented.
- `.gitignore` includes the unconditional entries (`CLAUDE.local.md`, `.claude/settings.local.json`, `.keel-update-check`) plus the accepted tools' personal files.
- Phase 7's export-ignore covers every generated config tree (`.claude/`, `.agents/`, `.codex/`, `.cursor/`, `.gemini/`, `.windsurf/`, `.github/instructions/`, `.github/agents/`, `.vscode/mcp.json`, `.githooks/`, `.mcp.json`, nested context files); nothing from this package ships.
- Every generated piece is reflected in the project card and `docs/decisions.md`; no piece is ever regenerated silently.
