## Build assets — source first, minified for production

Keel now carries a standing contract for front-end assets. Production ships the minified files (`*.min.js`, minified CSS), but the unminified source always exists alongside as the single source of truth, and the minified file is only ever generated from it — never created or edited by hand. The flow is one-directional and never reversed, so source and output can't drift.

### How it works

- Every shipped asset is a pair in the same directory: `name.js` + `name.min.js`, `name.css` + `name.min.css`. The source is what gets edited; the minified file is a build output. This also plugs into the WordPress `SCRIPT_DEBUG` convention — both files present means WordPress serves the readable source while debugging and the minified file in production.
- Minification runs locally, as the build step the working assistant executes — whichever assistant is on the repo (Claude Code, Codex, Copilot, Cursor, Gemini CLI, Windsurf) regenerates the minified files by running the project's own build/minify script before committing. It is never delegated to CI or a forge action, and a project never assumes a remote pipeline will produce its minified assets.
- The build/minify script is named in the technical plan (Phase 2) and created at the scaffold (Phase 5); a per-slice rule regenerates minified assets from source, and `scripts/keel-verify` gains a minified-asset-sync check. The Phase 7 release gate regenerates every minified asset from its source on the candidate and verifies each pair is in sync — a stale or hand-edited minified file blocks the release.

### The override

The contract is in force by default on every project that ships front-end JS/CSS. The developer can override it — a different pipeline, minified-only distribution, or no minification at all — but only by an explicit decision recorded in `docs/decisions.md`. Projects with no front-end assets never trigger it.

### Upgrading an existing project

On reconcile, projects that ship front-end assets settle the source→minified pairing and the local build/minify script at the next sprint kickoff or maintenance touch; a project that currently hand-maintains its minified files regenerates them once from source and adopts the script. Nothing else structural.

Full detail in `keel/CHANGELOG.md`.
