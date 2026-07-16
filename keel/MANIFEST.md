# Keel Manifest — v1.13.0

One file, two tables, one purpose: looking ONLY at this file, a session can tell (1) whether a project contains everything Keel requires at its current phase, and (2) which skill files changed in which Keel version — so after an update it knows exactly what to re-read, without interpreting the changelog.

**When to read this file:** after EVERY skill update (it is the post-update reconciliation's first input — see `references/project-state.md`), and any time a full parity audit is wanted. **Authority rule:** the phase references are the contract; this manifest is the verifiable index of them. If they ever disagree, the reference wins and the mismatch is a release bug — fix the manifest.

## Table 1 — What a Keel project must contain

Verification is phase-aware and condition-aware: read the project card and phase status in `docs/PROGRESS.md`, then check that every row required AT OR BEFORE the current position (whose condition the project meets) exists. Anything missing joins the reconciliation's batched plan — whatever version introduced it. Rows marked "conditional" depend on a recorded choice (project card) or a project trait; their absence is only a gap when the condition holds.

| Path (in the project) | What it is / template source | Required from | Condition |
|---|---|---|---|
| `docs/PROGRESS.md` | Living state: project card, phase status, position (template: `references/project-state.md`) | Phase 1 step 0a | Always |
| `docs/decisions.md` | Append-only decision log (same template source) | Phase 1 step 0a | Always |
| `docs/lessons-learned.md` | Append-only problem→solution log (same) | Phase 1 step 0a | Always |
| `CLAUDE.md` (repo root) | The portability lock: Keel block between `KEEL:BEGIN/END`, stamped `— vX.Y.Z` | Phase 1 step 0a | Always |
| `AGENTS.md` | Mirror of the lock block | Phase 1 step 0a | Only if the user works with non-Claude assistants |
| `.claude/skills/keel/` | Embedded copy of the whole skill, version-synced | Phase 1 step 0a | Only if embed accepted (card: `Keel portability:`) |
| `docs/00-competitive-landscape.md` | Competitive scan artifacts | Phase 1 step 0 | Unless the scan was skipped on record |
| `docs/01-discovery.md` | Discovery document | Phase 1 | Always |
| `docs/estimate.md` | Estimate v1 preliminary → firm (per `references/estimation-budget.md`) | Phase 1 close | Always |
| `docs/token-ledger.md` | Actual token usage, one row per session | Phase 1 close | Always |
| `docs/02-functional-spec.md` | Functional contract | Phase 2 | Always |
| `docs/03-technical-plan.md` | Stack, architecture, code map, conventions | Phase 2 | Always |
| `docs/flows/` | One file per multi-step/branching journey | Phase 2 | Always |
| `docs/budget.md` | Client-facing budget, approved | Phase 2 close | Always |
| `.claude/rules/` | Path-scoped rules from the plan + security profile (`references/claude-config.md`) | Phase 2 close | Only if accepted (card: `Claude config:`) |
| `.claude/agents/` | Reviewer subagents (same source) | Phase 2 close | Only if accepted (card: `Claude config:`) |
| `docs/design/DESIGN-BRIEF.md` | Brief handed to Design | Phase 3 | UI projects only |
| `docs/BUILD-SPEC.md` | Consolidated faithful-build contract | Phase 4 | UI projects only |
| `docs/design/design-requests/` | Numbered DR register | Phase 4 | When the first Design Request appears |
| `.gitignore` + `.gitattributes` | Hygiene boundaries (full rules at Phase 7); `.gitignore` ALWAYS includes `CLAUDE.local.md`, `.claude/settings.local.json`, and `.keel-update-check` (the machine-local update-check throttle stamp) | Phase 5 scaffold | Always |
| `docs/sprints/` | One file per sprint | Phase 5 | Always |
| `docs/05-test-points.md` | Test-point log, all columns | Phase 5 | Always |
| `docs/api/INDEX.md` | One line per public surface | Phase 5 first slice | Always |
| `docs/playground.md` | Playground access + try-it instructions | Phase 5 scaffold | If the project can be run |
| `.githooks/pre-commit` | Confidential-data gate (+ `core.hooksPath` set) | Phase 5 scaffold | Only if accepted (card: `Claude config:`) |
| `.claude/settings.json` | Minimal confirmed permission allow-list | Phase 5 scaffold | Only if accepted (card: `Claude config:`) |
| `.mcp.json` (repo root) | Development MCP servers, env expansion only | Phase 5 scaffold | Only if the technical plan defines dev MCP servers |
| `docs/architecture.md` | Consolidated architecture | Phase 6 | Always |
| `docs/api/`, `docs/usage/`, `docs/reference/` | Full documentation layout (api/ grows from Phase 5) | Phase 6 | Always (reference/ per project type) |
| `docs/07-release.md` | Release record | Phase 7 | Always |
| `docs/issues.md` | Forge issue log | First forge contact | Only if the forge's issues were ever accessed |
| `docs/old/` | Archive (move, never delete) | First sprint close | When archiving starts |
| `docs/04-adoption-audit.md` | Gap audit vs Keel standards | Adoption step 5 | Adopted projects only |

Project-card lines that must exist (inside `docs/PROGRESS.md`): the full card per the `references/project-state.md` template, including `Keel portability:`, `Claude config:` (since v1.10.0) and `Keel baseline:` (since v1.10.0).

## Table 2 — Skill files and the Keel version that last changed them

After an update, re-read `SKILL.md`, the current phase's reference, and THIS file always; beyond that, the files to re-read are exactly the rows whose version is NEWER than the project's `Keel baseline:`. Rows are the `keel/` tree — what travels in the embedded copy.

| Skill file | Last changed in |
|---|---|
| `SKILL.md` | v1.13.0 |
| `MANIFEST.md` | v1.13.0 |
| `CHANGELOG.md` | v1.13.0 |
| `references/claude-config.md` | v1.12.1 |
| `references/phase-5-development.md` | v1.12.1 |
| `references/phase-7-release.md` | v1.12.1 |
| `references/project-state.md` | v1.12.0 |
| `references/phase-1-discovery.md` | v1.13.0 |
| `references/phase-2-functional-spec.md` | v1.10.0 |
| `references/adoption.md` | v1.10.0 |
| `references/estimation-budget.md` | v1.7.0 |
| `references/phase-6-documentation.md` | v1.7.0 |
| `references/phase-3-design-handoff.md` | v1.5.0 |
| `references/phase-4-faithful-build.md` | v1.5.0 |
| `references/handoff-contract.md` | v1.5.0 |
| `references/design-brief-template.md` | v1.5.0 |
| `references/design-request-template.md` | v1.5.0 |
| `references/build-spec-template.md` | v1.5.0 |
| `references/phase-8-website.md` | v1.3.0 |
| `references/phase-8-site-discovery.md` | v1.3.0 |
| `references/phase-8-section-catalogue.md` | v1.3.0 |
| `references/phase-8-domain-decision.md` | v1.3.0 |
| `references/phase-8-design-direction.md` | v1.3.0 |
| `references/phase-8-launch-checklist.md` | v1.3.0 |
| `references/phase-8-technical-seo.md` | v1.2.0 |
| `references/accessibility.md` | v1.2.0 |
| `references/security/wordpress.md` | v1.3.0 |
| `references/security/web-app.md` | v1.3.0 |
| `references/security/mcp-server.md` | v1.0.0 |
| `references/security/library-component.md` | v1.0.0 |
| `LICENSE` | v1.0.0 |
| `NOTICE` | v1.0.0 |

## Maintenance (part of EVERY release — no exceptions)

- Every file touched by a release updates its "Last changed in" row; a new file gets a new row; a removed file loses its row (noted in the changelog).
- If the release changes what a project must contain (new required file/directory, new project-card line, a condition change), Table 1 is updated in the same release.
- The header line of this manifest carries the skill version and is one of the FOUR synced version locations (frontmatter, SKILL.md heading, CHANGELOG.md, MANIFEST.md header) governed by SKILL.md's version change policy — never bumped without explicit user instruction.
- Verifying this manifest against the release's actual diff is part of release hygiene for the skill itself: a stale manifest defeats its purpose.
