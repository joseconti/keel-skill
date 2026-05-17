# Phase 7 — Release

Goal: get the project to a clean, shippable state — nothing secret or unnecessary in git, nothing dev-only in the distributable package, a versioned and documented release.

## Two distinct hygiene boundaries

These are different and both matter:

1. **What never enters git** → `.gitignore`. Secrets, env files, build output, dependencies, OS/editor cruft. If it should not be in history at all, it goes here.
2. **What is in git but must NOT reach the final distributed package** → `.gitattributes` with `export-ignore`. Tests, dev tooling, CI config, the `docs/` source, design handoff, build scripts — useful in the repo, but the user's distributable (e.g. the plugin ZIP produced by `git archive`) must be lean.

Confusing these is a common defect: a dev file ends up shipped, or a needed runtime file is excluded. Decide each path's boundary explicitly.

## Steps

### 1. `.gitignore`

Generate per project type. Always exclude: secrets/credentials, `.env*`, local config with tokens, dependency dirs (`vendor/`, `node_modules/`), build artifacts, logs, OS files (`.DS_Store`), editor dirs (`.idea/`, `.vscode/` unless intentionally shared). Add type-specific entries:
- WordPress plugin: build dirs, `vendor/` if committing only built deps, local WP test env.
- MCP server / web app (e.g. Fly.io): `.env`, deploy secrets, local data volumes.
- Library/component: build output, coverage, packaging artifacts.

Verify nothing sensitive is already tracked (if it is, it must be removed from history, not just ignored — flag this to the user explicitly).

### 2. `.gitattributes` with `export-ignore`

Mark everything that belongs in the repo but not in the shipped package as `export-ignore`, so `git archive` produces a clean distributable. Typically: `/tests`, `/.github`, CI config, `/docs` (source docs — ship a built/user-facing subset if relevant), `/design` handoff, build/dev scripts, linter/formatter configs, `.gitattributes`/`.gitignore` themselves, example/fixture data.

Keep in the package: runtime code, runtime assets, the readme/license the end user needs, the user-facing docs you intend to ship.

State the resulting package contents to the user so the boundary is visible and agreed.

### 3. Versioning & changelog

- Set the version per the project's scheme.
- Update the changelog: **oldest → newest ordering** (e.g. 2.1.0 then 2.1.1). Never invert.
- Each entry: what changed, grouped (added/changed/fixed/security), referencing features from `docs/`.

### 4. Pre-release verification

Before tagging:
- Phase 5 test points all pass; Phase 6 docs complete.
- Security profile checklist passed (link `docs/security.md`).
- Build the distributable the way the user actually ships it (e.g. `git archive` / the plugin packaging step) and inspect the output: no secrets, no dev files, all runtime files present, correct version.
- **Real-environment verification (hard gate — no tag without it).** "Tests pass" is not "it works when installed". Take the exact distributable a user receives and install/deploy it in a real environment of the correct type — a real WordPress site for a plugin, the actual Fly.io app for a service, a clean target install for a library — then exercise the critical path there. If there's an installed base, also run the real upgrade from the previous shipped version on that environment. A failure here blocks the release; it is never waved through because unit tests were green.
- If UI: faithfulness checklist from `docs/BUILD-SPEC.md` still holds.

### 5. Release artifacts

- Tag the release.
- Produce the distributable package and verify its contents one more time against the intended boundary.
- Produce/refresh the end-user README and any required store/marketplace metadata.
- Note the release in `docs/` (e.g. append to changelog and a short release note).

## `docs/07-release.md`

```
# Release — [Project name] v[version]
## .gitignore boundary (what never enters git)
## export-ignore boundary (in repo, not in package)
## Package contents (verified)
## Changelog entry (oldest → newest)
## Pre-release verification results
## Release artifacts
```

## Definition of done

- `.gitignore` and `.gitattributes` (export-ignore) exist, correct for the project type, and the package boundary is agreed with the user.
- No secret is tracked in git; no dev file is in the shipped package; no runtime file is missing from it.
- Version set, changelog updated oldest → newest.
- Distributable built and its contents verified.
- Real-environment verification passed on the actual distributable (and the real upgrade, if there's an installed base).
- `docs/07-release.md` complete.

This is the final phase of the build lifecycle. Report the release summary to the user.

If Phase 1 recorded project-website intent (yes), proceed to Phase 8 (Project Website) if the user is ready, or remind them Phase 8 can be run later whenever they want the site. Phase 8 is part of this skill — not built here in Phase 7.
