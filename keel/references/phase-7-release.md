# Phase 7 — Release

Goal: get the project to a clean, shippable state — nothing secret or unnecessary in git, nothing dev-only in the distributable package, a versioned and documented release.

## Two distinct hygiene boundaries

These are different and both matter:

1. **What never enters git** → `.gitignore`. Secrets, env files, build output, dependencies, OS/editor cruft. If it should not be in history at all, it goes here.
2. **What is in git but must NOT reach the final distributed package** → `.gitattributes` with `export-ignore`. Tests, dev tooling, CI config, the `docs/` source, design handoff, build scripts — useful in the repo, but the user's distributable (e.g. the plugin ZIP produced by `git archive`) must be lean.

Confusing these is a common defect: a dev file ends up shipped, or a needed runtime file is excluded. Decide each path's boundary explicitly.

## Steps

### 1. `.gitignore`

Generate per project type. Always exclude: secrets/credentials, `.env*`, local config with tokens, dependency dirs (`vendor/`, `node_modules/`), build artifacts, logs, OS files (`.DS_Store`), editor dirs (`.idea/`, `.vscode/` unless intentionally shared), personal assistant config (`CLAUDE.local.md`, `.claude/settings.local.json`), and the update-check throttle stamp (`.keel-update-check`). Add type-specific entries:
- WordPress plugin: build dirs, `vendor/` if committing only built deps, local WP test env.
- MCP server / web app (e.g. Fly.io): `.env`, deploy secrets, local data volumes.
- Library/component: build output, coverage, packaging artifacts.

Verify nothing sensitive is already tracked, running the full confidential-data check (SKILL.md "Confidential data never reaches Git") over the WHOLE tracked tree — not only the files changed lately. If something is tracked: flag it to the user explicitly — it must be removed from history (`git filter-repo` / BFG), not just ignored, and any credential that was ever pushed is compromised and must be rotated.

### 2. `.gitattributes` with `export-ignore`

Mark everything that belongs in the repo but not in the shipped package as `export-ignore`, so `git archive` produces a clean distributable. Typically: `/tests`, `/.github`, CI config, `/docs` (source docs — ship a built/user-facing subset if relevant), `/design` handoff, build/dev scripts, linter/formatter configs, `.gitattributes`/`.gitignore` themselves, example/fixture data, and the Keel workflow files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md` when kept, `/.claude/` and `/.agents/` including the embedded skill, every generated assistant config tree — `/.codex/`, `/.cursor/`, `/.gemini/`, `/.windsurf/`, `/.github/instructions/`, `/.github/agents/`, `/.vscode/mcp.json`, nested context files — `/.githooks`, `/.mcp.json`) — they govern development, never the distributable.

Keep in the package: runtime code, runtime assets, the readme/license the end user needs, the user-facing docs you intend to ship.

State the resulting package contents to the user so the boundary is visible and agreed.

### 3. Versioning & changelog

- **Propose the version; never decide it.** The Keel version discipline applies at project scale: the assistant PROPOSES the number — patch / minor / major per the project's scheme, with one line of reasoning — and WAITS for the user's explicit approval before writing any version number anywhere. Only after that approval does it sync the touchpoints below. A version decided unilaterally is a defect, whatever the number.
- **Sync every version touchpoint.** `docs/03-technical-plan.md` lists every place the version string lives (e.g. plugin main-file header, readme.txt `Stable tag`, a VERSION constant, package.json). Update ALL of them to the same value and verify they match — a mismatched touchpoint (header says 2.1.1, stable tag says 2.1.0) is a classic release defect that breaks updates.
- Update the changelog: **oldest → newest ordering** (e.g. 2.1.0 then 2.1.1). Never invert.
- Each entry: what changed, grouped (added/changed/fixed/security), referencing features from `docs/`.

### 4. Pre-release verification

Before tagging:
- **Executed checks, not log reading.** "Phase 5 test points all pass" is verified by RE-RUNNING now, on the release candidate — never by reading `docs/05-test-points.md`: run the ENTIRE automated suite against the exact distributable being tagged and record command + result in `docs/07-release.md`; run `scripts/keel-verify` on the candidate — clean, output recorded. Phase 6 docs complete.
- **Walk `docs/PROGRESS.md`'s open items.** Every `⚠ unverified` step or asset is re-attempted in the real environment NOW, or the user accepts it explicitly with a `docs/decisions.md` entry. Nothing unverified rides silently into the tag.
- **Zero placeholder copy in the distributable** (`scripts/keel-verify` checks the surfaces mechanically; confirm on the built package).
- **The end-user guide honors its recorded decision** (card `User guide:`): if it ships, it is present in the package, its index navigates, its coverage matches the release's capabilities (a feature shipped without its guide section is a gap), and it is placeholder-clean; if it does not ship, `/guide/` is export-ignored and absent from the package.
- **Performance budgets verified on the candidate,** with the measurement method the plan named, numbers recorded.
- **Debug logging defaults OFF in the release candidate.** The switch and the logging code stay in — they are the day-one diagnostic path — but the shipped default generates nothing until the user enables it (the Phase 5 scaffold set it ON for development; this gate flips and verifies the default on the actual candidate).
- Security profile checklist passed (link `docs/security.md`).
- When the environment provides subagents (per `references/assistant-config.md`), `security-auditor` reviews the final tree before the tag; findings are fixed, or explicitly accepted by the user on the record.
- If the end-user guide ships in the package: `guide-qa` re-verifies it on the exact release candidate (when the environment provides subagents — inline otherwise): coverage still matches the release's capabilities, every internal link and image resolves, placeholder-clean — plus the theme checks (`references/guide-theme.md`): version meta = `Docs theme:` card line, `_theme/` intact vs the theme release's checksums.
- If the assistant config package exists (`references/assistant-config.md`): rules/agents still match the recorded conventions and security profile in EVERY accepted tool's container (no drift between containers), the permission allow-lists still match the plan's commands, and the pre-commit gate still blocks a synthetic secret.
- **Accessibility verification (gate — no tag without it for anything with a UI).** Automated checks pass, and a manual pass with the platform's **real assistive technology** — screen reader, keyboard/switch, largest text size, reduced-motion and high-contrast on — succeeds on the **actual distributable** in a real environment, not just in dev. It meets the Phase 1 targeted level (WCAG 2.2 AA floor / AAA where feasible; EN 301 549 / EAA where in scope) or the shortfall is honestly recorded in `docs/accessibility.md` (no overlay, no false conformance claim). Link `docs/accessibility.md`. Per `references/accessibility.md`.
- **Minified assets regenerated from source and in sync.** For anything shipping front-end JS/CSS, regenerate every `*.min.*` from its committed unminified source with the project's build/minify script on the candidate, and verify each pair matches; a stale or hand-edited minified file blocks the release. Run locally — never assume a CI or forge action produced them. Per SKILL.md "Build assets — source first, minified for production" (unless a different pipeline is recorded in `docs/decisions.md`).
- Build the distributable the way the user actually ships it (e.g. `git archive` / the plugin packaging step) and inspect the output: no secrets, no dev files, all runtime files present, correct version.
- **Real-environment verification (hard gate — no tag without it).** "Tests pass" is not "it works when installed". Take the exact distributable a user receives and install/deploy it in a real environment of the correct type — a real WordPress site for a plugin, the actual Fly.io app for a service, a clean target install for a library — then exercise the critical path there. If there's an installed base, also run the real upgrade from the previous shipped version on that environment. The Phase 5 playground can serve as this environment when it is of the correct type — but what gets installed in it is the exact distributable, never the dev tree — and `docs/playground.md` (access details, try-it instructions) is what the user follows for their own final pass. A failure here blocks the release; it is never waved through because unit tests were green.
- If UI: faithfulness checklist from `docs/BUILD-SPEC.md` still holds.

### 5. Release artifacts

- Tag the release.
- Produce the distributable package and verify its contents one more time against the intended boundary.
- **A forge release that publishes downloadable assets (a consumption zip, checksums, builds) is verified AFTER publishing, never assumed.** Check the attachments for real — `gh release view <tag>` or the forge API's assets list, confirming each expected asset's name AND size — NEVER by reading the rendered release page: the release body may DESCRIBE its assets, and a description is not an attachment. When the environment has no network or no `gh`, the user runs `gh release view <tag>` from their terminal (or opens the release) and reports the assets list back. Record the verification (asset names + sizes) in `docs/07-release.md`. Missing assets → the release is not shipped: attach them (`gh release upload <tag> <files>` or the release's Edit page) and re-verify.
- **License ships correctly:** the LICENSE file is in the package, file headers carry the license where the platform convention expects it, and every bundled dependency's license is compatible and honored (the Phase 1 decision, checked per dependency in Phase 5).
- Produce/refresh the end-user README and any required store/marketplace metadata. For WordPress.org plugins specifically: `readme.txt` valid (`Requires at least`, `Tested up to` — current WP version actually tested, `Requires PHP`, `Stable tag` = this release), plugin main-file headers in sync, and the assets the listing needs (banner, icon, screenshots with captions).
- Note the release in `docs/` (e.g. append to changelog and a short release note).
- **Close the loop on issues and cost.** If a forge issue log exists (`docs/issues.md`): mark the issues this release closes — entries complete, shipping version recorded — and reference them in the changelog entry where useful. Then run the **final token reconciliation** in `docs/token-ledger.md` (per `references/estimation-budget.md`): total tokens by model, cost at verified current prices, and the deviation vs the estimate — report it to the user plainly, and record the calibration lesson for future estimates in `docs/lessons-learned.md` if significant.
- **Maintenance handoff.** The release is not the end state: from here on the project is in maintenance, and anything that arrives — a bug report, a feature request, a dependency alert, a platform update — follows `references/maintenance.md` (triage, the hotfix path, rollback, the dependency/CVE duty, recurring features, site freshness when a Phase 8 site exists).
- Update `docs/PROGRESS.md`: Phase 7 done, current position "maintenance" (per `references/maintenance.md`), and Phase 8 pending or n/a per the Phase 1 website intent.

## `docs/07-release.md`

```
# Release — [Project name] v[version]
## .gitignore boundary (what never enters git)
## export-ignore boundary (in repo, not in package)
## Package contents (verified)
## Changelog entry (oldest → newest)
## Pre-release verification results (full suite re-run on the candidate: command + result; keel-verify output; open items closed)
## Accessibility verification results (automated + real assistive-tech, on the distributable)
## Issues closed by this release (from docs/issues.md — if the log exists)
## Token reconciliation (totals by model, cost at verified prices, deviation vs estimate)
## Release artifacts
```

## Definition of done

- `.gitignore` and `.gitattributes` (export-ignore) exist, correct for the project type, and the package boundary is agreed with the user.
- No secret is tracked in git; no dev file is in the shipped package; no runtime file is missing from it.
- If the assistant config package exists: verified current against the recorded decisions in every container, and none of it (`.claude/`, `.agents/`, the other tools' config trees, `.githooks/`, `.mcp.json`) ships.
- Version proposed by the assistant and explicitly approved by the user, then set and **identical across every touchpoint** listed in the technical plan; changelog updated oldest → newest.
- LICENSE file and headers ship correctly; bundled dependency licenses compatible.
- Distributable built and its contents verified.
- Real-environment verification passed on the actual distributable (and the real upgrade, if there's an installed base).
- The ENTIRE automated suite was re-run on the exact distributable being tagged, command + result recorded in `docs/07-release.md`; `scripts/keel-verify` clean on the candidate.
- If the project ships front-end JS/CSS: every `*.min.*` was regenerated from its committed source on the candidate and verified in sync (no hand-edited or stale minified file), or a different pipeline is recorded in `docs/decisions.md`.
- No `⚠ unverified` item rode into the tag: each was re-attempted in the real environment or explicitly accepted by the user in `docs/decisions.md`; zero placeholder copy in the distributable; performance budgets verified on the candidate.
- If the environment provides subagents: `security-auditor` reviewed the final tree, findings fixed or accepted on the record — otherwise its unavailability recorded.
- If the end-user guide shipped in the package: `guide-qa` re-verified it on the candidate (coverage, links, placeholder-clean, theme checks) — or the environment's lack of subagents recorded.
- If the release publishes downloadable assets: their real attachment was verified post-publication (names + sizes via `gh release view` / the forge API, recorded in `docs/07-release.md`) — never assumed from the rendered release page.
- Maintenance handoff noted: PROGRESS.md's position is "maintenance" and future work follows `references/maintenance.md`.
- Accessibility verification passed on the actual distributable for anything with a UI (automated + real assistive-tech), meeting the Phase 1 targeted level or with the shortfall honestly recorded in `docs/accessibility.md`.
- If `docs/issues.md` exists: the issues this release closes are marked resolved with complete entries and the shipping version recorded.
- Final token reconciliation done in `docs/token-ledger.md` (totals by model, cost at verified prices, deviation vs estimate) and reported to the user.
- `docs/07-release.md` complete.

This is the final phase of the build lifecycle; from here the project lives in maintenance (`references/maintenance.md`). Report the release summary to the user.

If Phase 1 recorded project-website intent (yes), proceed to Phase 8 (Project Website) if the user is ready, or remind them Phase 8 can be run later whenever they want the site. Phase 8 is part of this skill — not built here in Phase 7.
