# Keel Manifest — v2.1.0

One file, three tables, one purpose: looking ONLY at this file, a session can tell (1) whether a project contains everything Keel requires at its current phase, (2) which skill files changed in which Keel version — so after an update it knows exactly what to re-read, without interpreting the changelog — and (3) what concrete actions each version asks of an existing project (the reconciliation delta).

**When to read this file:** after EVERY skill update (it is the post-update reconciliation's first input — see `references/project-state.md`), and any time a full parity audit is wanted. **Authority rule:** the phase references are the contract; this manifest is the verifiable index of them. If they ever disagree, the reference wins and the mismatch is a release bug — fix the manifest.

## Table 1 — What a Keel project must contain

Verification is phase-aware and condition-aware: read the project card and phase status in `docs/PROGRESS.md`, then check that every row required AT OR BEFORE the current position (whose condition the project meets) exists. Anything missing joins the reconciliation's batched plan — whatever version introduced it. Rows marked "conditional" depend on a recorded choice (project card) or a project trait; their absence is only a gap when the condition holds.

| Path (in the project) | What it is / template source | Required from | Condition |
|---|---|---|---|
| `docs/PROGRESS.md` | Living state: project card, phase status, position, deferred items (template: `references/project-state.md`) | Phase 1 step 0a | Always |
| `docs/decisions.md` | Append-only decision log (same template source) | Phase 1 step 0a | Always |
| `docs/lessons-learned.md` | Append-only problem→solution log (same) | Phase 1 step 0a | Always |
| `CLAUDE.md` (repo root) | The portability lock: Keel block between `KEEL:BEGIN/END`, stamped `— vX.Y.Z` | Phase 1 step 0a | Always |
| `AGENTS.md` | Mirror of the lock block | Phase 1 step 0a | Only if the user works with non-Claude assistants |
| `.claude/skills/keel/` | Embedded copy of the whole skill, version-synced | Phase 1 step 0a | Only if embed accepted (card: `Keel portability:`) |
| `docs/00-competitive-landscape.md` | Competitive scan artifacts | Phase 1 step 0 | Unless the scan was skipped on record |
| `docs/01-discovery.md` | Discovery document (verdict + user decision recorded) | Phase 1 | Always |
| `docs/estimate.md` | Estimate v1 preliminary → firm (per `references/estimation-budget.md`) | Phase 1 close | Always |
| `docs/token-ledger.md` | Actual token usage, one row per session | Phase 1 close | Always |
| `docs/02-functional-spec.md` | Functional contract (incl. design split with foreseen assets, per-screen a11y, breakpoints) | Phase 2 | Always |
| `docs/03-technical-plan.md` | Stack, architecture, code map, conventions, testing plan (frameworks + commands + playground recipe) | Phase 2 | Always |
| `docs/flows/` | One file per multi-step/branching journey | Phase 2 | Always |
| `docs/budget.md` | Client-facing budget, approved | Phase 2 close | Only if `Client budget: yes` (card line, asked at Phase 1 step 10) |
| `.claude/rules/` | Path-scoped rules from the plan + security profile (`references/claude-config.md`) | Phase 2 close | Only if accepted (card: `Claude config:`) |
| `.claude/agents/` | Reviewer/verifier subagents (same source) | Phase 2 close | Only if accepted (card: `Claude config:`) |
| `docs/design/DESIGN-BRIEF.md` | Brief handed to Design (user-approved, bracket-clean) | Phase 3 | UI projects only |
| `docs/design/design-handoff/` | The returned handoff per `references/handoff-contract.md` (Design's delivery, or the recorded no-Design branch) — holds NOTHING else, ever (contract rule 10: wholesale-replaceable) | Phase 4 start | UI projects only |
| `docs/BUILD-SPEC.md` | Consolidated faithful-build contract (§1 is the evidence table) | Phase 4 | UI projects only |
| `docs/design/design-requests/` | Numbered DR register | Phase 4 | When the first Design Request appears |
| `.gitignore` + `.gitattributes` | Hygiene boundaries (full rules at Phase 7); `.gitignore` ALWAYS includes `CLAUDE.local.md`, `.claude/settings.local.json`, and `.keel-update-check` (the machine-local update-check throttle stamp) | Phase 5 scaffold | Always |
| `docs/sprints/` | One file per sprint | Phase 5 | Always |
| `docs/05-test-points.md` | Test-point log, all columns including evidence (commands + output + commit) | Phase 5 | Always |
| `docs/api/INDEX.md` | One line per public surface | Phase 5 first slice | Always |
| `docs/playground.md` | Playground access + try-it instructions + seed/reset commands + `last verified:` stamp | Phase 5 scaffold | If the project can be run |
| `scripts/keel-verify` | The project's own release linter (`references/phase-5-development.md`) | Phase 5 scaffold | If the project can be run |
| `.githooks/pre-commit` | Confidential-data gate (+ `core.hooksPath` set) | Phase 5 scaffold | Only if accepted (card: `Claude config:`) |
| `.claude/settings.json` | Minimal confirmed permission allow-list | Phase 5 scaffold | Only if accepted (card: `Claude config:`) |
| CI workflow (e.g. `.github/workflows/ci.yml`) | The plan's verified commands + secret scan + keel-verify (`references/claude-config.md`) | Phase 5 scaffold | Only if accepted (card: `Claude config:`) and the forge has CI |
| `.mcp.json` (repo root) | Development MCP servers, env expansion only | Phase 5 scaffold | Only if the technical plan defines dev MCP servers |
| `docs/architecture.md` | Consolidated architecture | Phase 6 | Always |
| `docs/api/`, `docs/usage/`, `docs/reference/` | Full documentation layout (api/ grows from Phase 5) | Phase 6 | Always (reference/ per project type) |
| `docs/security.md` | Consolidated security posture per the loaded profile(s) | Phase 6 | Always |
| `docs/accessibility.md` | Accessibility record: automated results + guided assistive-technology pass, per item | Phase 6 | Always |
| `README.md` (repo root) | The repository's front door | Phase 6 | Always |
| `guide/` (repo root) | End-user HTML guide: navigable index + one page per topic, one dir per locale, full capability coverage | Phase 6 | Unless declined (card: `User guide:`) |
| `docs/07-release.md` | Release record (incl. full-suite re-run on the candidate + keel-verify output) | Phase 7 | Always |
| `<site-docs>/` (`docs/site/` or the site's own repo, per the recorded decision) | Phase 8 site set: `PRODUCT-BRIEF.md`, site discovery, spec, design docs | Phase 8 | Website intent only |
| `<site-docs>/launch-report.md` | One row per launch check: command/tool, result, date | Phase 8 launch | Website intent only |
| `<site-docs>/operations.md` | Renewal dates, uptime/backup decisions, freshness duty | Phase 8 launch | Website intent only |
| `docs/issues.md` | Forge issue log | First forge contact | Only if the forge's issues were ever accessed |
| `docs/old/` | Archive (move, never delete) | First sprint close | When archiving starts |
| `docs/04-adoption-audit.md` | Gap audit vs Keel standards | Adoption step 5 | Adopted projects only |

Project-card lines that must exist (inside `docs/PROGRESS.md`): the full card per the `references/project-state.md` template, including `Keel portability:`, `Claude config:` (since v1.10.0), `Keel baseline:` (since v1.10.0), `Client budget:` and `User guide:` (both since v2.0.0).

## Table 2 — Skill files and the Keel version that last changed them

After an update, re-read `SKILL.md`, the current phase's reference, and THIS file always; beyond that, the files to re-read are exactly the rows whose version is NEWER than the project's `Keel baseline:`. Rows are the `keel/` tree — what travels in the embedded copy.

| Skill file | Last changed in |
|---|---|
| `SKILL.md` | v2.1.0 |
| `MANIFEST.md` | v2.1.0 |
| `CHANGELOG.md` | v2.1.0 |
| `references/keel-maintenance.md` | v2.0.0 |
| `references/playground-recipes.md` | v2.0.0 |
| `references/maintenance.md` | v2.0.0 |
| `references/claude-config.md` | v2.0.0 |
| `references/phase-5-development.md` | v2.0.0 |
| `references/phase-7-release.md` | v2.0.0 |
| `references/project-state.md` | v2.1.0 |
| `references/phase-1-discovery.md` | v2.0.0 |
| `references/phase-2-functional-spec.md` | v2.0.0 |
| `references/adoption.md` | v1.10.0 |
| `references/estimation-budget.md` | v2.0.0 |
| `references/phase-6-documentation.md` | v2.0.0 |
| `references/phase-3-design-handoff.md` | v2.1.0 |
| `references/phase-4-faithful-build.md` | v2.1.0 |
| `references/handoff-contract.md` | v2.1.0 |
| `references/design-brief-template.md` | v2.0.0 |
| `references/design-request-template.md` | v2.0.0 |
| `references/build-spec-template.md` | v2.0.0 |
| `references/phase-8-website.md` | v2.0.0 |
| `references/phase-8-site-discovery.md` | v2.0.0 |
| `references/phase-8-section-catalogue.md` | v2.0.0 |
| `references/phase-8-domain-decision.md` | v2.0.0 |
| `references/phase-8-design-direction.md` | v2.0.0 |
| `references/phase-8-launch-checklist.md` | v2.0.0 |
| `references/phase-8-technical-seo.md` | v2.0.0 |
| `references/accessibility.md` | v2.0.0 |
| `references/security/wordpress.md` | v2.0.0 |
| `references/security/web-app.md` | v2.0.0 |
| `references/security/mcp-server.md` | v2.0.0 |
| `references/security/library-component.md` | v2.0.0 |
| `references/security/website.md` | v2.0.0 |
| `LICENSE` | v1.0.0 |
| `NOTICE` | v2.0.0 |

## Table 3 — Per-version actions on an existing project (the reconciliation delta)

What the reconciliation APPLIES, version by version, for every version newer than the project's `Keel baseline:`. "None structural" means the version changed skill behavior only — re-reading per Table 2 is enough. Versions before v1.10.0 predate the baseline mechanism; for those, the Table 1 parity audit covers everything.

| Version | Actions for an existing project |
|---|---|
| v1.10.0 | Add `Claude config:` and `Keel baseline:` card lines; offer the optional Claude Code config package once. |
| v1.11.0 | Lock block gains its version stamp — refreshed by the normal lock-freshness check. |
| v1.12.0 | None structural (the manifest itself was introduced, skill-side). |
| v1.12.1 | Ensure `.keel-update-check` is an unconditional `.gitignore` entry. |
| v1.13.0 | None structural. |
| v2.0.0 | Ask the `Client budget:` question if it was never asked and add the card line. On runnable projects, generate `scripts/keel-verify` and add seed/reset to the playground at (or after) the Phase 5 scaffold. If the Claude config package is accepted and the forge has CI, offer the CI workflow. If the project has UI, the next handoff audit or re-audit uses the evidence-table `docs/BUILD-SPEC.md` §1. If Phase 7 is done, set the PROGRESS.md position to "maintenance" and work per `references/maintenance.md`. If website intent is recorded, plan `launch-report.md` and `operations.md` at the next launch or freshness pass. On runnable projects, the debug-log system with its on/off switch (Phase 5 scaffold spec) is added at the next sprint kickoff or maintenance change. The reconciliation itself ASKS whether to create the full end-user guide now (`guide/` — the Phase 6 section, with its language and packaging questions) and records the answer on the new `User guide:` card line; creating it on a released project is a normal maintenance change. The lock-block stamp refreshes through the normal freshness check. |
| v2.1.0 | None structural. Behavioral: nothing is ever written into `docs/design/design-handoff/` again — user-generated assets and acquired fonts go to the PROJECT's tree (contract rule 10). If the current handoff already contains foreign files, move each to its correct home (project tree or `docs/`) at the next Phase 4 touch, restoring the wholesale-replaceable state. |

## Maintenance (part of EVERY release — no exceptions)

- Every file touched by a release updates its "Last changed in" row; a new file gets a new row; a removed file loses its row (noted in the changelog).
- If the release changes what a project must contain (new required file/directory, new project-card line, a condition change), Table 1 is updated in the same release — and Table 3 gets the release's action row (or an explicit "None structural").
- The header line of this manifest carries the skill version and is one of the FOUR synced version locations (frontmatter, SKILL.md heading, CHANGELOG.md, MANIFEST.md header) governed by the version change policy in `references/keel-maintenance.md` — never bumped without explicit user instruction. The repository `README.md` version line and the canonical lock-block stamp in `references/project-state.md` are kept in sync as part of the same release hygiene.
- Verifying this manifest against the release's actual diff is part of release hygiene for the skill itself: a stale manifest defeats its purpose. Run `python3 tests/lint-release.py` before tagging — CI runs it again on every tag.
