# Keel

**Keel** is a Claude skill for taking software projects from idea to release. *Keel* is the structural backbone laid down first, on which the whole project is built.

Use it for any new project — WordPress/WooCommerce plugins, MCP servers, web apps, components, libraries, or websites. Keel runs a complete multi-phase workflow so you never have to re-explain your standing requirements every time you start something new.

- **Version:** 1.2.0
- **License:** GPL-3.0-or-later
- **Author:** [José Conti](https://plugins.joseconti.com/en)

## What Keel does

Keel encodes a full project lifecycle as a single skill. When you start a new project, Keel walks Claude through eight phases in order, loading each phase's reference file on demand (progressive disclosure — Claude does not pull every reference into context at once).

| Phase | Purpose |
|-------|---------|
| 1. Discovery | Idea assessment, project type, constraints, accessibility commitment, language model, website intent |
| 2. Functional spec | Flows, data model, integrations, permissions, design split, acceptance criteria |
| 3. Design handoff | What to tell Claude Design and the files Design must read and return |
| 4. Faithful build | Audit Design's return, consolidate the build spec, build with zero deviation, guided external setup |
| 5. Development | Sprint planning, vertical slices with test points, living progress tracker, lessons learned |
| 6. Documentation | Full `docs/` layout: API, classes, functions, usage, architecture, security |
| 7. Release | `.gitignore` vs `.gitattributes` export-ignore, versioning, real-environment verification, release artifacts |
| 8. Project website (conditional) | Product study, site type, sections, domain, design direction, vanilla build, self-hosted fonts, SEO and AEO, launch |

Security is cross-cutting. As soon as Phase 1 fixes the project type, Keel loads the matching security profile (WordPress/WooCommerce, web app, MCP server, library/component) and keeps it in mind through every later phase.

Accessibility is cross-cutting too, and non-negotiable. As soon as Phase 1 fixes the project type and target platform(s), Keel loads `references/accessibility.md` and applies it — from the first line, on every platform (web, iOS, Android, macOS, Windows) — through every later phase, targeting WCAG 2.2 AA (AAA where feasible), EN 301 549 and the European Accessibility Act where they apply, and each platform's native accessibility API. It is stated up front, never retrofitted at the end.

## Operating principles

- Decide the project type early and let it drive everything.
- Assess ideas and decisions honestly, even when it is uncomfortable. No default praise.
- Document as you go, in `docs/`. Documentation is not a final-phase afterthought.
- Never invent or interpret silently. Ask the user. If a design detail is missing downstream, request it from Design.
- Code adapts to the design, never the design to the code.
- Security is per-platform and non-optional.
- Accessibility is non-negotiable, on every platform, and designed in from the first line — never retrofitted.
- Build once, reuse by manifest. Never regenerate structurally-identical pages or screens.
- Confirm before advancing a phase. Each phase has a definition of done.

## Installation

Keel is a skill for Claude (Claude Code, Cowork mode, or any Claude environment that supports skills). See [`INSTALL.md`](INSTALL.md) for the full installation guide, including personal install, plugin install, team install, verification, updating, and troubleshooting.

Quick version: clone the repository and copy the `keel/` directory into your Claude client's skills folder.

Once installed, the skill is invoked automatically whenever you start a new project, say things like "I have an idea for a plugin", "let's plan this project", or ask Claude to handle the handoff between Design and Build.

## Repository layout

```
keel-skill/
├── README.md
├── .gitignore
├── .gitattributes
└── keel/
    ├── SKILL.md           # Skill entry point (frontmatter is the source of truth for version)
    ├── CHANGELOG.md       # Oldest to newest, never inverted
    ├── LICENSE            # GPL-3.0-or-later
    ├── NOTICE             # Copyright notice
    └── references/        # Phase reference files, loaded on demand
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
            └── library-component.md
```

## Version reporting

The version in `keel/SKILL.md` frontmatter (`metadata.version`) is the source of truth. The same version is mirrored in `keel/CHANGELOG.md` and in the introduction line of `SKILL.md`. Keep all three in sync whenever the skill is updated.

## Contributing

Issues and pull requests are welcome. Please open an issue first to discuss any substantial change, so the proposal can be assessed against Keel's operating principles before implementation.

When contributing:

- Follow the existing tone and structure of the reference files.
- Update `CHANGELOG.md` (oldest to newest) and the version in `SKILL.md` frontmatter.
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
