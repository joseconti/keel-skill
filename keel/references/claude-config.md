# Native Claude Code project configuration (`.claude/`) — optional package

Load this reference at three moments, and only these: (a) Phase 1 step 0a (or adoption step 2), when the package is OFFERED; (b) the close of Phase 2 (adoption: after its step 4), when rules and agents are MATERIALIZED; (c) the Phase 5 scaffold, when settings, the pre-commit gate, and `.mcp.json` are COMPLETED.

Claude Code loads certain project files natively: `.claude/rules/*.md` (modular instructions, path-scopable), `.claude/agents/*.md` (project subagents), `.claude/settings.json` (shared permissions and config), and `.mcp.json` at the repo root (MCP servers). Keel can generate these from decisions the project has ALREADY made, so sessions running in Claude Code get the project's conventions, security profile, and quality gates enforced ergonomically — without re-reading the full technical plan into context every time.

## Position in the workflow (read this first)

- **The `CLAUDE.md` lock remains the universal mechanism.** Rules, agents, and settings are loaded by Claude Code only — the Claude app, Cowork, and other AIs do not load them. Nothing critical to the workflow may live ONLY in `.claude/` config: the lock and the `docs/` state remain the source of truth in every environment. This package is reinforcement and ergonomics for Claude Code sessions, never a replacement.
- **Token economy applies.** Rules without a `paths:` filter load into EVERY session's context. Therefore: every generated rule is path-scoped by default, kept short (target under 40 lines), and points to the authoritative `docs/` file instead of duplicating its body. A rule that restates the whole technical plan is a defect.
- **Content derives from recorded decisions only.** Rules and agents are generated FROM `docs/03-technical-plan.md`, the loaded security profile, and Keel's own quality gates. Never invent new policy inside a rule — if something is worth enforcing, it goes into the plan or `docs/decisions.md` first, then into the rule.
- **The whole package is optional and per-project.** Offered once, recorded once, never nagged about again.

## The offer (one batched question — Phase 1 step 0a / adoption step 2)

Alongside the existing embed-the-skill question, ask ONCE whether the project should carry native Claude Code configuration, presenting the pieces and their value in two or three lines. The user may take all of it, part of it, or none. Record the choice in the project card:

```
Claude config: [none / rules / rules+agents / full]
```

(`full` = rules + agents + settings + pre-commit gate + `.mcp.json` when applicable.) Record a D-entry in `docs/decisions.md` with what was accepted. In the same breath, tell the user once that `CLAUDE.local.md` and `.claude/settings.local.json` exist for PERSONAL, non-committed preferences: Keel never creates them (they are the user's own), but always adds both to `.gitignore` so they can never be committed by accident.

Do not block on this question: if the user defers, record `Claude config: none (deferred)` and move on — the package can be added later from this reference at any phase boundary.

## Pieces, sources, and timing

| Piece | Generated from | Created at | Updated when |
|-------|----------------|-----------|--------------|
| `.claude/rules/` | `docs/03-technical-plan.md` §Conventions + the loaded security profile + Keel quality gates | Phase 2 close (adoption: after its step 4) | A recorded decision changes a source — same change, never silently |
| `.claude/agents/` | Same sources + `docs/api/INDEX.md` discipline | Phase 2 close (adoption: after its step 4) | Same rule |
| `.claude/settings.json` | Technical plan §Tooling commands + playground commands | Phase 5 scaffold, ALWAYS confirmed with the user | Tooling/playground commands change |
| `.githooks/pre-commit` | SKILL.md "Confidential data never reaches Git" | Phase 5 scaffold (adoption: immediately, with approval) | The gate's patterns need tightening (recorded) |
| `.mcp.json` (repo root) | Technical plan — ONLY if it defines development MCP servers | Phase 5 scaffold, confirmed | The dev MCP set changes |

Everything in the table is repo-only: Phase 7 marks `.claude/`, `.githooks/`, and `.mcp.json` `export-ignore` alongside the existing workflow files, so none of it ships in the distributable.

## `.claude/rules/` — three files, path-scoped

Generate exactly these three by default (more only on explicit user request). Scope every rule's `paths:` to the source globs from the technical plan's code map (e.g. `includes/**/*.php`, `src/**/*.ts`) so they load only when code is actually touched.

**`code-style.md`** — the conventions, distilled:

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
```

**`security.md`** — the loaded profile, distilled to its DO/DON'T core (about ten bullets maximum — e.g. for WordPress: sanitize input, escape output at print time, nonce + capability on every state change, `$wpdb->prepare`, ABSPATH guard, no secrets in code or logs). End with: `Full profile: the Keel security reference for this project type governs; this file is the reminder, not the standard.`

**`docs-discipline.md`** — Keel's build gates where they bite:

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

## `.claude/agents/` — three project subagents

Markdown files with YAML frontmatter (`name`, `description`, `tools`). Give them read-only tools (`Read, Grep, Glob`) — they flag, they never fix. Do NOT pin a `model:` (model names age; inherit the session's). The `description` must say WHEN to use the agent — Claude Code delegates based on it.

**`code-reviewer.md`**:

```markdown
---
name: code-reviewer
description: Reviews a slice or diff of [Project name] against the recorded conventions and Keel quality gates. Use after completing a slice, before its commit.
tools: Read, Grep, Glob
---

You review code for [Project name] against its recorded contracts. You flag; you never rewrite.

Check in order: (1) conventions per docs/03-technical-plan.md §Conventions — prefix, naming, error handling, logging; (2) reuse — no near-duplicate of anything in docs/api/INDEX.md; (3) i18n — no hardcoded or concatenated user-facing strings; (4) accessibility on UI slices, per the project's targeted level; (5) docs — every new public surface has its doc AND its INDEX.md row; (6) extension points on extensible types.

Report: file:line — what fails — which recorded rule it violates. Order by severity. If everything passes, say so in one line.
```

**`security-auditor.md`** — same skeleton; description: "Audits changes against the [type] security profile. Use before any commit touching input handling, auth, data writes, or external calls." Body: the distilled profile checklist (same ten bullets as the rule), plus: verify no secret, credential, key, or real personal data appears in the changed files. Report file:line + risk + rule.

**`docs-verifier.md`** — same skeleton; description: "Verifies docs/api/INDEX.md and docs/api/ + docs/reference/ are one-to-one. Use at test points and sprint closes." Body: every INDEX row has its doc; every doc has its row; every public surface in the diff appears in both; examples reference symbols that exist. Report mismatches as slice defects.

## `.claude/settings.json` — minimal allow-list, ALWAYS confirmed

Committed settings affect every person and session that opens the repo, so this file is never written silently: build the proposed allow-list ONLY from the technical plan's verified tooling commands and the playground's documented start/stop commands, show it to the user, and write it only on their confirmation.

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

Rules: exact commands or tight prefixes only — never `Bash(*)`, never a broad wildcard, never a deny-list pretending to be a policy. Permission-rule syntax evolves with Claude Code; when in doubt, verify against the current settings documentation rather than guessing. If the user wants no committed permissions, skip the file entirely — its absence is a valid state.

## The confidential-data pre-commit gate — `.githooks/pre-commit`

The assistant's own pre-commit check (SKILL.md "Confidential data never reaches Git") still runs in every session — this hook is the NET under it, and it also covers commits made outside Keel sessions (the user's own terminal, another tool). A classic git hook was chosen deliberately over an assistant-specific hook: it fires in EVERY environment and editor, which is exactly Keel's portability principle.

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
# skill. The assistant-side check (Keel SKILL.md) still scans them; only
# this net skips them.
for f in $files; do
  case "$f" in .githooks/*|.claude/skills/*) continue ;; esac
  base=$(basename "$f")
  case "$base" in
    .env|.env.*|*.pem|*.key|*.p12|*.pfx|id_rsa*|*credential*|*secret*|*.sql|*.sqlite|wp-config.php)
      printf 'BLOCKED (name): %s\n' "$f"; fail=1 ;;
  esac
done

# 2) Secret-shaped content in the STAGED blob (not the working tree)
pat="-----BEGIN [A-Z ]*PRIVATE KEY-----|api[_-]?key[\"']?[[:space:]]*[:=]|Bearer [A-Za-z0-9._~+/=-]{20,}|AKIA[0-9A-Z]{16}|sk-(proj-)?[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{36,}|xox[baprs]-[A-Za-z0-9-]{10,}"
for f in $files; do
  case "$f" in .githooks/*|.claude/skills/*) continue ;; esac
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

False positives are kept rare by design — field-tested: (1) the gate itself exempts the canonical trees that legitimately contain the very patterns it searches for, `.githooks/` (its own script) and `.claude/skills/` (the embedded skill, including this reference), while the assistant-side check still scans them like everything else; (2) never CREATE a false positive when writing — in `docs/decisions.md`, `docs/lessons-learned.md`, comments, or any project note, a secret-shaped string is described or split apart (`api` + `_key`), never pasted verbatim (SKILL.md "Confidential data never reaches Git", point 5). The occasional remaining case (e.g. a legitimate `class-secrets-manager.php`) is handled by the conscious bypass policy above, on the record. Never loosen the patterns to avoid a one-time bypass. If the user also wants an assistant-side hook (a Claude Code `PreToolUse` hook in `settings.json` that gates `git commit`), add it on top — but the git hook is the baseline and never replaced by it.

## `.mcp.json` — conditional, at the repo root

Create it ONLY when `docs/03-technical-plan.md` defines MCP servers used during development (e.g. the project's own MCP server under test, or a WordPress content MCP for the playground). Confirm with the user before writing.

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

Hard rule: NEVER a literal secret in this file — environment expansion (`${VAR}`) only, with the variable documented in `docs/playground.md`. `.mcp.json` passes through the same confidential-data gate as everything else. If the project needs no dev MCP servers, this file simply does not exist — do not create an empty one.

## Adoption specifics

- Rules and agents materialize AFTER adoption step 4, because their source is the as-built technical plan — and they encode the OBSERVED conventions (adoption principle: conventions are observed, not imposed), even where Keel's defaults would differ.
- The pre-commit gate and the `.gitignore` entries can be installed immediately at adoption step 2 with the user's approval — they protect from the first commit and impose nothing on the code.
- If the adopted repo already carries `.claude/` config (rules, agents, settings), treat it like existing code: inventory it, keep it, and reconcile — never overwrite. Conflicts between existing rules and the as-built plan are surfaced to the user and recorded, exactly like any other adoption gap.

## Definition of done (this reference)

- The offer was made once (0a / adoption step 2), and the project card carries the `Claude config:` line with a D-entry for what was accepted.
- Accepted rules/agents exist, are path-scoped, under ~40 lines each, generated from recorded decisions, and point to their `docs/` sources instead of duplicating them.
- `settings.json`, if accepted: allow-list built only from verified plan/playground commands and explicitly confirmed by the user before writing.
- The pre-commit gate, if accepted: installed (`.githooks/pre-commit` + `core.hooksPath`), VERIFIED by blocking a synthetic secret, and its collaborator setup line documented.
- `.mcp.json` exists only if the plan defines dev MCP servers, carries no literal secret, and was confirmed.
- `.gitignore` includes `CLAUDE.local.md` and `.claude/settings.local.json` (this entry is unconditional — it applies even when the whole package was declined).
- Phase 7's export-ignore covers `.claude/`, `.githooks/`, and `.mcp.json`; nothing from this package ships.
- Every generated piece is reflected in the project card and `docs/decisions.md`; no piece is ever regenerated silently.
