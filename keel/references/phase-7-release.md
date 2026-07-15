# Phase 7 — Release

Goal: get the project to a clean, shippable state — nothing secret or unnecessary in git, nothing dev-only in the distributable package, a versioned and documented release.

## Two distinct hygiene boundaries

These are different and both matter:

1. **What never enters git** → `.gitignore`. Secrets, env files, build output, dependencies, OS/editor cruft. If it should not be in history at all, it goes here.
2. **What is in git but must NOT reach the final distributed package** → `.gitattributes` with `export-ignore`. Tests, dev tooling, CI config, the `docs/` source, design handoff, build scripts — useful in the repo, but the user's distributable (e.g. the plugin ZIP produced by `git archive`) must be lean.

Confusing these is a common defect: a dev file ends up shipped, or a needed runtime file is excluded. Decide each path's boundary explicitly.

## Steps

### 1. `.gitignore`

Generate per project type. Always exclude: secrets/credentials, `.env*`, local config with tokens, dependency dirs (`vendor/`, `node_modules/`), build artifacts, logs, OS files (`.DS_Store`), editor dirs (`.idea/`, `.vscode/` unless intentionally shared), personal assistant config (`CLAUDE.local.md`, `.claude/settings.local.json`). Add type-specific entries:
- WordPress plugin: build dirs, `vendor/` if committing only built deps, local WP test env.
- MCP server / web app (e.g. Fly.io): `.env`, deploy secrets, local data volumes.
- Library/component: build output, coverage, packaging artifacts.

Verify nothing sensitive is already tracked, running the full confidential-data check (SKILL.md "Confidential data never reaches Git") over the WHOLE tracked tree — not only the files changed lately. If something is tracked: flag it to the user explicitly — it must be removed from history (`git filter-repo` / BFG), not just ignored, and any credential that was ever pushed is compromised and must be rotated.

### 2. `.gitattributes` with `export-ignore`

Mark everything that belongs in the repo but not in the shipped package as `export-ignore`, so `git archive` produces a clean distributable. Typically: `/tests`, `/.github`, CI config, `/docs` (source docs — ship a built/user-facing subset if relevant), `/design` handoff, build/dev scripts, linter/formatter configs, `.gitattributes`/`.gitignore` themselves, example/fixture data, and the Keel workflow files (`CLAUDE.md`, `AGENTS.md`, `/.claude/` including the embedded skill and any generated Claude config, `/.githooks`, `/.mcp.json`) — they govern development, never the distributable.

Keep in the package: runtime code, runtime assets, the readme/license the end user needs, the user-facing docs you intend to ship.

State the resulting package contents to the user so the boundary is visible and agreed.

### 3. Versioning & changelog

- Set the version per the project's scheme.
- **Sync every version touchpoint.** `docs/03-technical-plan.md` lists every place the version string lives (e.g. plugin main-file header, readme.txt `Stable tag`, a VERSION constant, package.json). Update ALL of them to the same value and verify they match — a mismatched touchpoint (header says 2.1.1, stable tag says 2.1.0) is a classic release defect that breaks updates.
- Update the changelog: **oldest → newest ordering** (e.g. 2.1.0 then 2.1.1). Never invert.
- Each entry: what changed, grouped (added/changed/fixed/security), referencing features from `docs/`.

### 4. Pre-release verification

Before tagging:
- Phase 5 test points all pass; Phase 6 docs complete.
- Security profile checklist passed (link `docs/security.md`).
- If the Claude config package exists (`references/claude-config.md`): rules/agents still match the recorded conventions and security profile, the `settings.json` allow-list still matches the plan's commands, and the pre-commit gate still blocks a synthetic secret.
- **Accessibility verification (gate — no tag without it for anything with a UI).** Automated checks pass, and a manual pass with the platform's **real assistive technology** — screen reader, keyboard/switch, largest text size, reduced-motion and high-contrast on — succeeds on the **actual distributable** in a real environment, not just in dev. It meets the Phase 1 targeted level (WCAG 2.2 AA floor / AAA where feasible; EN 301 549 / EAA where in scope) or the shortfall is honestly recorded in `docs/accessibility.md` (no overlay, no false conformance claim). Link `docs/accessibility.md`. Per `references/accessibility.md`.
- Build the distributable the way the user actually ships it (e.g. `git archive` / the plugin packaging step) and inspect the output: no secrets, no dev files, all runtime files present, correct version.
- **Real-environment verification (hard gate — no tag without it).** "Tests pass" is not "it works when installed". Take the exact distributable a user receives and install/deploy it in a real environment of the correct type — a real WordPress site for a plugin, the actual Fly.io app for a service, a clean target install for a library — then exercise the critical path there. If there's an installed base, also run the real upgrade from the previous shipped version on that environment. The Phase 5 playground can serve as this environment when it is of the correct type — but what gets installed in it is the exact distributable, never the dev tree — and `docs/playground.md` (access details, try-it instructions) is what the user follows for their own final pass. A failure here blocks the release; it is never waved through because unit tests were green.
- If UI: faithfulness checklist from `docs/BUILD-SPEC.md` still holds.

### 5. Release artifacts

- Tag the release.
- Produce the distributable package and verify its contents one more time against the intended boundary.
- **License ships correctly:** the LICENSE file is in the package, file headers carry the license where the platform convention expects it, and every bundled dependency's license is compatible and honored (the Phase 1 decision, checked per dependency in Phase 5).
- Produce/refresh the end-user README and any required store/marketplace metadata. For WordPress.org plugins specifically: `readme.txt` valid (`Requires at least`, `Tested up to` — current WP version actually tested, `Requires PHP`, `Stable tag` = this release), plugin main-file headers in sync, and the assets the listing needs (banner, icon, screenshots with captions).
- Note the release in `docs/` (e.g. append to changelog and a short release note).
- **Close the loop on issues and cost.** If a forge issue log exists (`docs/issues.md`): mark the issues this release closes — entries complete, shipping version recorded — and reference them in the changelog entry where useful. Then run the **final token reconciliation** in `docs/token-ledger.md` (per `references/estimation-budget.md`): total tokens by model, cost at verified current prices, and the deviation vs the estimate — report it to the user plainly, and record the calibration lesson for future estimates in `docs/lessons-learned.md` if significant.
- Update `docs/PROGRESS.md`: Phase 7 done, and Phase 8 pending or n/a per the Phase 1 website intent.

## `docs/07-release.md`

```
# Release — [Project name] v[version]
## .gitignore boundary (what never enters git)
## export-ignore boundary (in repo, not in package)
## Package contents (verified)
## Changelog entry (oldest → newest)
## Pre-release verification results
## Accessibility verification results (automated + real assistive-tech, on the distributable)
## Issues closed by this release (from docs/issues.md — if the log exists)
## Token reconciliation (totals by model, cost at verified prices, deviation vs estimate)
## Release artifacts
```

## Definition of done

- `.gitignore` and `.gitattributes` (export-ignore) exist, correct for the project type, and the package boundary is agreed with the user.
- No secret is tracked in git; no dev file is in the shipped package; no runtime file is missing from it.
- If the Claude config package exists: verified current against the recorded decisions, and none of it (`.claude/`, `.githooks/`, `.mcp.json`) ships.
- Version set and **identical across every touchpoint** listed in the technical plan; changelog updated oldest → newest.
- LICENSE file and headers ship correctly; bundled dependency licenses compatible.
- Distributable built and its contents verified.
- Real-environment verification passed on the actual distributable (and the real upgrade, if there's an installed base).
- Accessibility verification passed on the actual distributable for anything with a UI (automated + real assistive-tech), meeting the Phase 1 targeted level or with the shortfall honestly recorded in `docs/accessibility.md`.
- If `docs/issues.md` exists: the issues this release closes are marked resolved with complete entries and the shipping version recorded.
- Final token reconciliation done in `docs/token-ledger.md` (totals by model, cost at verified prices, deviation vs estimate) and reported to the user.
- `docs/07-release.md` complete.

This is the final phase of the build lifecycle. Report the release summary to the user.

If Phase 1 recorded project-website intent (yes), proceed to Phase 8 (Project Website) if the user is ready, or remind them Phase 8 can be run later whenever they want the site. Phase 8 is part of this skill — not built here in Phase 7.
