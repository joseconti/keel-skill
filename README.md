# Keel

**Keel** is a skill for taking software projects from idea to release — built for Claude and installable in any assistant that supports the open Agent Skills standard (OpenAI Codex, Cursor, Gemini CLI, GitHub Copilot, Windsurf, and more). *Keel* is the structural backbone laid down first, on which the whole project is built.

Use it for any new project — WordPress/WooCommerce plugins, MCP servers, web apps, components, libraries, or websites. Keel runs a complete multi-phase workflow so you never have to re-explain your standing requirements every time you start something new.

- **Version:** 3.3.0
- **License:** GPL-3.0-or-later
- **Author:** [José Conti](https://plugins.joseconti.com/en)

## What Keel does

Keel encodes a full project lifecycle as a single skill. When you start a new project, Keel walks Claude through eight phases in order, loading each phase's reference file on demand (progressive disclosure — Claude does not pull every reference into context at once).

| Phase | Purpose |
|-------|---------|
| 1. Discovery | Competitive scan, honest idea assessment with a recorded verdict, proposed v1 (the assistant proposes, the user reacts), project type, constraints, license, accessibility commitment, language model, design system (existing or founded), website intent, client-budget question, preliminary AI-time estimate |
| 2. Functional spec | Flows, data model, integrations, permissions, technical plan (stack, architecture, conventions, testing plan with named frameworks and a playground recipe), design split, acceptance criteria, adversarial spec review, firm estimate and client budget |
| 3. Design handoff | What to tell Claude Design and the files Design must read and return — with an approval gate, screenshot-based visual references, and a playbook for when Design is not available |
| 4. Faithful build | Audit Design's return with recorded evidence (including recomputed contrast), consolidate the build spec, build with zero deviation, guided external setup, independent fidelity review |
| 5. Development | Sprint planning, vertical slices with test points and evidence (commands, outputs, commit hashes), unit/integration/e2e coverage per acceptance criterion, real playground with synthetic seed data, independent review subagents, full-suite sprint closes, lessons learned |
| 6. Documentation | Full `docs/` layout: API, classes, functions, usage, architecture, security, accessibility, playground |
| 7. Release | `.gitignore` vs `.gitattributes` export-ignore, proposed version with explicit user approval, full-suite re-run on the exact release candidate, real-environment verification, release artifacts, maintenance handoff |
| 8. Project website (conditional) | Product study, site type, sections, domain, design direction, vanilla build, self-hosted fonts, SEO and AEO, launch report with full-sitemap verification, post-launch operations |

After Phase 7 the project enters **maintenance** (`references/maintenance.md`): triage, a hotfix path from the release tag, rollback guidance, dependency and CVE response ("Tested up to" only after testing), recurring features, and the website freshness duty.

Security is cross-cutting. As soon as Phase 1 fixes the project type, Keel loads the matching security profile (WordPress/WooCommerce, web app, MCP server, library/component, or website for Phase 8 sites) and keeps it in mind through every later phase. Every profile ends in a "Verify with" block naming the exact tools (phpcs with the WordPress security sniffs and Plugin Check, npm/composer/pip audit, OWASP ZAP baseline, MCP Inspector) — at a test point, the command and its result are the evidence, and an unrecorded check did not happen. The MCP profile covers model-facing threats (tool-result injection, description poisoning, confused deputy, destructive-tool consent, Origin validation).

Verification is executable, not declarative. Every gate that can be checked mechanically is: acceptance criteria map to named automated tests (unit, integration, and browser-driven e2e for UI flows), test-point rows carry the exact commands with their output and commit hash, sprint closes run the full suite, the handoff audit leaves evidence per item and recomputes contrast ratios from the delivered hex values, and each project generates its own release linter (`scripts/keel-verify`). Independent subagents (code reviewer, security auditor, docs verifier, design-fidelity auditor, playground QA, launch verifier, accessibility auditor) break the self-certification loop wherever the environment provides them. The standing bar: anything a compile, a boot of the playground, or a basic test would have caught must be caught before the work is handed over.

Accessibility is cross-cutting too, and non-negotiable. As soon as Phase 1 fixes the project type and target platform(s), Keel loads `references/accessibility.md` and applies it — from the first line, on every platform (web, iOS, Android, macOS, Windows) — through every later phase, targeting WCAG 2.2 AA (AAA where feasible), EN 301 549 and the European Accessibility Act where they apply, and each platform's native accessibility API. It is stated up front, never retrofitted at the end.

Project state is cross-cutting as well. From the first minute of Phase 1, Keel maintains a living state system (`docs/PROGRESS.md` with the project card and exact position, `docs/decisions.md` as an append-only decision log, `docs/lessons-learned.md` as a problem-to-solution log, the Design Request register, and `docs/api/INDEX.md` with one line per public surface) defined in `references/project-state.md`. Any fresh chat resumes from these files — in a fixed, cache-friendly reading order — instead of re-scanning code or re-asking questions, and decisions already made are never re-litigated.

Estimation and budgeting are built in, and AI-time based. At the close of Phase 1 Keel produces a preliminary estimate, and at the close of Phase 2 a firm one plus a client-ready budget (`docs/estimate.md` and `docs/budget.md`): itemized segments with hours for both the AI's working time and the developer's supervision time (answering questions, deciding, real-world testing, uploading code), the developer's hours priced at their rate, the AI's token cost computed per model and payment mode, both blocks kept separate, and everything adjusted with the user before it is final — never based on what a traditional human team would take. Actual token usage is recorded per session in `docs/token-ledger.md`, and the release closes with a reconciliation: totals by model, cost at verified prices, and the deviation against the estimate.

Forge issues get their own living log. Whenever issues on the project's Git forge (GitHub, GitLab, Gitea, Bitbucket, or any other) are accessed or worked, `docs/issues.md` tracks the inventory, what was resolved and exactly how (diagnosis, resolution, commits, verification), and what remains pending — full traceability if a problem surfaces later.

Keel has three entry modes: a new project (Phase 1 from zero), resuming an in-progress Keel project (from `docs/PROGRESS.md`), and **adoption** — applying Keel to a project already underway (`references/adoption.md`): read-only inventory, the never-made Phase 1 decisions asked, artifacts reconstructed as-built, and a gap audit against Keel's standards prioritized with the user, changing no code.

Every Keel project also carries a **portability lock**: the same Keel block in `CLAUDE.md` and `AGENTS.md` (optionally plus the skill embedded at `.claude/skills/keel/` and `.agents/skills/keel/`) that binds any environment or AI opening the repo — Claude app, Cowork, Claude Code in VS Code, OpenAI Codex, GitHub Copilot, Cursor, Gemini CLI, Windsurf, or another assistant — to the Keel workflow, even where the skill is not installed. Workflow files never ship in the distributable (Phase 7 export-ignore).

Projects can also opt into **native assistant configuration**, generated from their own recorded decisions (`references/assistant-config.md`) for the tools the user actually works with — Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Gemini CLI, Windsurf: path-scoped rules distilled from the technical plan's conventions and the security profile, reviewer and verifier subagents (code review, security audit, docs verification, design fidelity, playground QA, launch verification, accessibility audit), confirmed minimal permission allow-lists, a confidential-data git pre-commit gate that blocks secrets from any environment or editor, an optional CI workflow built from the plan's exact verified commands, and per-tool MCP registration for development MCP servers — one container per accepted tool, identical substance in each. The lock remains the universal mechanism — this package is per-tool ergonomics on top, offered once per project, always recorded in the project card, and never shipped.

Keel also keeps itself current. At the start of every session it checks this repository for a newer release (`git ls-remote --tags`, with API fallbacks). Every copy is checked separately — an up-to-date app install does not hide an outdated embedded copy in the opened project. It updates every copy it can durably write — the user-level install and, always when present, the project's embedded trees (`.claude/skills/keel/` + `.agents/skills/keel/`) — with a verified full-tree replacement, summarizing the improvements; for a copy it cannot write (app-managed skill storage, as in the Claude app / Cowork), it tells you a newer version exists, what it brings, and how to update. The check is best-effort and never blocks work, and the remote lookup is throttled to at most one check per 24 hours per project via a machine-local stamp (`.keel-update-check` at the project root, always gitignored) — the full SKILL.md read and the stamp-only lock-freshness check still run in every session, since they are local and free. After an update, a **post-update reconciliation** brings the open project itself up to date with what the new version introduces — new required files or directories, new project-card lines, lock-block refreshes, never-asked questions — tracked by the project card's `Keel baseline:` line and recorded like any other decision. Its first input is the **parity manifest** (`keel/MANIFEST.md`): everything a Keel project must contain, phase- and condition-aware, plus the Keel version that last changed each skill file and a per-version action list — the exact re-read list and to-do delta after any update.

## Operating principles

- Keep the living state current from the first minute; a fresh chat resumes from state, never from re-scanning code.
- Work from recorded state; read code surgically. Fixed reading order, cache-friendly sessions.
- Decide the project type early and let it drive everything.
- Assess ideas and decisions honestly, even when it is uncomfortable. No default praise.
- Document as you go, in `docs/`. Documentation is not a final-phase afterthought.
- Never invent or interpret silently. Ask the user. If a design detail is missing downstream, request it from Design.
- Code adapts to the design, never the design to the code.
- Security is per-platform and non-optional.
- Nothing confidential ever reaches Git: every commit is preceded by a confidential-data check on what is about to enter the repository; findings stop the commit, are reported as the security risk they are, and are excluded via `.gitignore` (history-purged and rotated if they were ever pushed).
- Accessibility is non-negotiable, on every platform, and designed in from the first line — never retrofitted.
- Build once, reuse by manifest. Never regenerate structurally-identical pages or screens.
- Reuse the internal API; never duplicate code. Search the existing API before writing anything new; generalize a close fit instead of forking it. Duplication is a defect.
- Document every public surface at the moment it is created — functions, classes, hooks, routes, MCP abilities, CLI commands — with a runnable example. Phase 6 consolidates documentation; it never writes it from zero.
- Maximum extensibility for extensible project types: filterable user-facing strings, before/after hooks on decisions, filterable queries and responses, replaceable public classes.
- Real functional verification whenever possible, not only automated tests: a runnable playground with a per-platform recipe (wp-env, MCP Inspector, Playwright, a clean consumer project) and synthetic seed data, where real flows, CLI, and API calls are exercised — and the user gets access details plus try-it instructions (`docs/playground.md`). Anything a compile, a boot, or a basic test would have caught is caught before hand-over, and a failing test is never weakened to pass.
- Budgets are AI-time based, never human-time based: the AI's hours plus the vibe coder's supervision hours, itemized per segment, with the AI's token cost separate — and the actuals reconciled against the estimate at release.
- Forge issues are tracked in a living log (`docs/issues.md`): everything there is, everything resolved and exactly how, everything still pending.
- Confirm before advancing a phase. Each phase has a definition of done.

## Installation

Keel is a skill in the open Agent Skills format: it works in Claude (Claude Code, Cowork mode, or any Claude environment that supports skills) and in any other assistant that supports the standard — OpenAI Codex, Cursor, Gemini CLI, GitHub Copilot, Windsurf, and others. See [`INSTALL.md`](INSTALL.md) for the full installation guide, including personal install, per-assistant install paths, plugin install, team install, verification, updating, and troubleshooting.

Quick version: clone the repository and copy the `keel/` directory into your client's skills folder (for example `~/.claude/skills/keel` for Claude, or `~/.agents/skills/keel` for tools using the shared discovery convention).

Keel is also listed on the author's skills marketplace: [skills.joseconti.com/plugin/keel.html](https://skills.joseconti.com/plugin/keel.html).

Once installed, the skill is invoked automatically whenever you start a new project, say things like "I have an idea for a plugin", "let's plan this project", or ask Claude to handle the handoff between Design and Build.

## Repository layout

```
keel-skill/
├── README.md
├── INSTALL.md
├── .gitignore
├── .gitattributes
├── .github/workflows/     # Release CI: lints every tag, publishes the release (repo-only)
├── tests/                 # Release linter + eval scenarios (repo-only, never shipped)
└── keel/
    ├── SKILL.md           # Skill entry point (frontmatter is the source of truth for version)
    ├── MANIFEST.md        # Parity manifest: required structure + per-file versions + per-version actions
    ├── CHANGELOG.md       # Oldest to newest, never inverted
    ├── LICENSE            # GPL-3.0-or-later
    ├── NOTICE             # Copyright notice
    └── references/        # Phase reference files, loaded on demand
        ├── keel-maintenance.md
        ├── project-state.md
        ├── adoption.md
        ├── maintenance.md
        ├── playground-recipes.md
        ├── assistant-config.md
        ├── estimation-budget.md
        ├── phase-1-discovery.md
        ├── phase-2-functional-spec.md
        ├── phase-3-design-handoff.md
        ├── phase-4-faithful-build.md
        ├── phase-5-development.md
        ├── phase-6-documentation.md
        ├── phase-7-release.md
        ├── phase-8-website.md
        ├── phase-8-site-discovery.md
        ├── phase-8-section-catalogue.md
        ├── phase-8-domain-decision.md
        ├── phase-8-design-direction.md
        ├── phase-8-technical-seo.md
        ├── phase-8-launch-checklist.md
        ├── handoff-contract.md
        ├── design-brief-template.md
        ├── build-spec-template.md
        ├── design-request-template.md
        ├── accessibility.md
        └── security/
            ├── wordpress.md
            ├── web-app.md
            ├── mcp-server.md
            ├── library-component.md
            └── website.md
```

## Version reporting

The version in `keel/SKILL.md` frontmatter (`metadata.version`) is the source of truth. The same version is mirrored in `keel/CHANGELOG.md`, in the introduction line of `SKILL.md`, and in the `keel/MANIFEST.md` header. This README's version line and the canonical lock-block stamp in `references/project-state.md` are kept in sync as well — `tests/lint-release.py` verifies all of it mechanically and CI runs it on every tag.

## Contributing

Issues and pull requests are welcome. Please open an issue first to discuss any substantial change, so the proposal can be assessed against Keel's operating principles before implementation.

When contributing:

- Follow the existing tone and structure of the reference files.
- Update `CHANGELOG.md` (oldest to newest) and the version in `SKILL.md` frontmatter.
- Run `python3 tests/lint-release.py` before proposing a release — it checks version sync, the description length limit, changelog order, reference-index parity, and the manifest against the tree.
- Do not commit Mac, Windows, Linux, or editor metadata files (see `.gitignore`).

## License

Keel is licensed under the [GNU General Public License v3.0 or later](keel/LICENSE).

```
Copyright (C) 2026 José Conti

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
```

See [`keel/NOTICE`](keel/NOTICE) for the full notice and [`keel/LICENSE`](keel/LICENSE) for the full license text.

## Author

**José Conti** — [plugins.joseconti.com/en](https://plugins.joseconti.com/en)
