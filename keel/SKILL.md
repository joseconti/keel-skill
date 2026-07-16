---
name: keel
license: GPL-3.0-or-later
metadata:
  version: 2.0.0
description: Use this skill for ANY new software project from idea to release — websites, WordPress/WooCommerce plugins, MCP servers, web apps, components, or libraries — and for maintaining what it built (hotfixes, dependency updates, new features). Trigger when the user starts a new project or feature, says "I have an idea for a plugin/site/app", "let's plan this project", brings only a vague one-line idea with no technical background (Keel shapes it and proposes the v1 unprompted), mentions a design handoff, asks for docs or a security review of a Keel project, asks what a project will cost (quote/budget), works forge issues (GitHub/GitLab/...), prepares a release or a hotfix, resumes an in-progress Keel project (any repo with docs/PROGRESS.md), or adopts Keel in an EXISTING project. Do NOT trigger for one-off scripts, quick code questions, or repos not managed by Keel unless the user wants to adopt them. Phases load references on demand; living state makes projects resumable across chats.
---

# Keel — project lifecycle (idea → release)

**Keel v2.0.0** — Licensed under GPL-3.0-or-later. *Keel* is the structural backbone laid down first, on which the whole project is built.

## Skill maintenance — update check & version policy (READ AND EXECUTE FIRST)

Once per session, when Keel is invoked and before the entry-mode decision, load `references/keel-maintenance.md` and execute it. It defines the release update check (throttled to one remote lookup per 24 hours via the machine-local `.keel-update-check` stamp), the multi-copy comparison and verified-replacement procedure, the post-update reconciliation trigger, the `CLAUDE.md` lock-freshness check, and version reporting. In a Keel project's repo the `CLAUDE.md` lock makes the full read of this SKILL.md its step 1, and this block routes straight there — so the checks run in every session, whether or not the skill auto-triggered. The check is best-effort and must never block, delay, or interrupt the work.

**Version change policy (UNBREAKABLE):** Keel's own version — `metadata.version` in the frontmatter, the heading above, `CHANGELOG.md`, and the `MANIFEST.md` header — is NEVER changed, and no changelog entry is ever added, without the user's **explicit instruction in the current conversation**. Nothing else counts: not the scale of the edits, not semver conventions, not gratitude, not a past conversation. If a bump seems warranted, propose a specific number and WAIT. The full policy, including what does and does not count as authorisation, lives in `references/keel-maintenance.md` — but this paragraph is binding on its own.

## Token economy — everything is created in English by default (READ FIRST)

English is the most token-efficient language for an LLM: the same content in Spanish or another Latin-script language costs roughly 15–30% more tokens (non-Latin scripts, far more), and Keel re-reads its living state (`docs/PROGRESS.md`, `docs/decisions.md`, `docs/lessons-learned.md`) in every session, so any per-word overhead compounds for the entire life of the project.

Therefore **everything Keel creates is written in English by default** — every `docs/` artifact (discovery, specs, progress, decisions, lessons learned, architecture, API reference, playground instructions), every continuation prompt for a new chat, every prompt or brief handed to Claude Code or Claude Design (design briefs, design requests, build specs), every template instance, report, commit message, and code comment — in addition to the product output itself, which is already English-based per "Output language & internationalization" below.

**Announce it up front.** At the start of every new project (and every adoption), tell the user in one line: everything Keel creates will be in English to minimize token consumption and therefore cost; if they prefer another language for the docs or any other artifact set, they only have to say so, knowing that it will increase token usage and spend. If the user chooses another language, honor it, record it in the project card and `docs/decisions.md` with the trade-off acknowledged, and apply it consistently from then on.

**Existing projects whose docs are in another language** (resume or adoption): ask the user once whether they want the existing documentation translated to English, stating the token/cost benefit in one line. If yes, translate it all and record the switch in `decisions.md`; if no, record the choice, keep that language consistently, and do not ask again.

**This is NOT about the conversation.** Keep talking to the user in whatever language the user writes (usually Spanish), exactly as always — the English default governs only what Keel *creates*. And it never removes product locales: what end users see follows the Phase 1 §6 i18n decisions; the product's translations are never dropped to save tokens.

## Why this skill exists

The user builds many projects (WordPress/WooCommerce plugins, MCP servers, web apps, components, libraries) and was repeating the same standing requirements every time: document everything, security per platform, full API/class/function docs in a `docs/` dir, a design handoff that doesn't waste tokens, a build that stays faithful to the design, proper git/package hygiene. This skill encodes that whole process once. Follow the phases in order; load each phase's reference file only when you reach it (progressive disclosure — do not pull every reference into context at once).

## Operating principles (hold across every phase)

- **Keep the living state current from the first minute.** `docs/PROGRESS.md`, `docs/decisions.md`, and `docs/lessons-learned.md` are created the moment Phase 1 starts (per `references/project-state.md`) and updated at the moment of every change — not at phase ends. A fresh chat resumes from state, never from re-scanning code or re-asking the user. Decisions recorded in `decisions.md` are never re-opened by the assistant on its own initiative — but a later **explicit user request** that contradicts a recorded decision supersedes it: record the change as a new decision entry and proceed.
- **Work from recorded state; read code surgically.** Orient via `docs/PROGRESS.md`, the technical plan's code map, `docs/architecture.md`, and `docs/api/INDEX.md` — then open only the specific file needed. Read each static reference once per session, in the fixed order defined in `references/project-state.md`; never re-read files already in context. This keeps sessions cheap, deterministic, and prompt-cache-friendly.
- **Decide the project type early and let it drive everything.** Web / WordPress plugin / WooCommerce extension / MCP server / web app / component / library. Type selects the security profile, the structure, the playground recipe, and what needs design.
- **Assess ideas and decisions honestly, even when it's uncomfortable.** Never default to praise. If an idea, a feature, a scope, or an approach is weak, say so with the reason and a concrete alternative. False encouragement wastes the user's time, which is the opposite of this skill's purpose. The user has explicitly asked for the truth even when it hurts.
- **Document as you go, in `docs/`.** Documentation is not a final-phase afterthought; each phase contributes its artifacts to `docs/`.
- **Never invent or interpret silently.** When something is undefined, ask the user. When a design detail is missing downstream, request it from Design — don't guess.
- **Every chat or tool boundary ships a ready-to-paste prompt — never prose instructions.** Whenever the work crosses to another chat, tool, or agent — this chat to a fresh one (the continuation prompt), Code to Design (the brief's complete opening message; a Design Request), Design back to Code (the Phase 4 kickoff prompt), or any external agent asked to do something — the assistant composes the complete, self-sufficient, copy-paste-ready prompt itself and shows it unprompted. Telling the user "ask Design to fix X" without handing them the exact prompt is a defect: the user is the courier, never the composer.
- **Code adapts to the design, never the design to the code.** The build follows the design to the letter; where the stack forces a change, the code strategy changes (and is logged), never the design intent. This is enforced through the handoff contract (Phases 3–4).
- **Design delivers build-ready assets; the build never transforms them.** Every screen handed to Design is defined by what it *does* (its functionalities), not just how it looks. Design applies the existing design system exactly (divergence is a Design Request, never a creative choice) and delivers every logo and icon in **both SVG and PNG**, plus every asset in a format the build drops in directly — so Code never has to convert, resize, recolor, or re-export. Fonts are assets too: the handoff ships the actual self-hosted font files at their final paths — or, when licensing prevents shipping them, the exact download-and-place instructions per font (source, license, files, target path in the structure) that the Phase 4 guided loop walks with the user. When the handoff arrives, the first action is a completeness gate: verify Design delivered everything without exception — with recorded evidence per checked item, never from memory; anything missing becomes a registered Design Request (a file + a ready-to-paste prompt) for Design to finish, never a build-side workaround. See Phases 3–4 and `references/handoff-contract.md`.
- **Security is per-platform and non-optional.** The relevant profile is consulted from Phase 1 onward, not bolted on at the end.
- **Nothing confidential ever reaches Git (UNBREAKABLE).** Every commit is preceded by a confidential-data check on the files about to enter the repository — secrets, credentials, private keys, tokens, real personal/customer data. A finding STOPS the commit: the user is warned, file by file, that pushing it is a serious security risk, and the fix is applied (`.gitignore` exclusion, untracking, history purge plus credential rotation if it was ever pushed) before anything is committed. See "Confidential data never reaches Git" below.
- **Accessibility is non-negotiable, on every platform, and designed in from the first line — never retrofitted.** Whatever is built — HTML, iOS, Android, macOS, Windows, or a cross-platform framework — is usable with assistive technology from the first slice, using every accessibility tool the platform offers. It is stated up front in Phase 1 (like the internationalization decision) precisely because building accessibly from the start and "making it accessible" at the end are not the same work — the second is a rewrite. The target is the maximum reasonably achievable: WCAG 2.2 AA as the floor (AAA where feasible), EN 301 549 and the European Accessibility Act where they apply, and the native accessibility API on every other platform. See "Accessibility" below and `references/accessibility.md`.
- **Output language is English by default — always, and never Spanish.** The primary language of everything *built* (source strings, UI copy, code identifiers, error messages, commit messages, API responses) defaults to English in every project, regardless of the language the user and the assistant converse in. Spanish is never assumed as the base language of the product. For WordPress/WooCommerce the base language is *always* English and the project is *always* prepared to be multi-language — non-negotiable. The multi-language questions are asked explicitly at project start (see "Output language & internationalization" below and Phase 1 §6). The docs — and everything else Keel creates (continuation prompts, briefs for Code/Design, lessons learned) — default to English as well, for token economy (see "Token economy" at the top); another language only on explicit request, with the extra token cost made clear.
- **Perfect orthography in every language — Spanish especially (UNBREAKABLE).** Everything the assistant writes for the user — chat, `docs/`, code comments, UI copy, commit messages — is spelled and punctuated perfectly. In Spanish this means every ñ, every accent/tilde (á é í ó ú ü) and every opening ¿/¡ is present and correct, with zero spelling or grammatical errors. This is a hard contract, not a preference: dropping accents or the ñ, or writing "espanol"/"anadir"/"informacion", is a defect to be fixed like any other. See "Writing quality — perfect orthography" below.
- **Build once, reuse by manifest.** Never regenerate structurally-identical pages/screens.
- **Reuse internal API; never duplicate code.** Before writing any new function, method, or class, search the project's existing internal API. If a suitable function already exists, reuse it. If one is *close* but not exact, generalize it (parameterize) rather than fork it. Write a new function only when there is no existing fit. Duplication is treated as a defect, the same as a security issue: it gets refactored, not left behind. The internal API grows deliberately and is documented as it grows (see next).
- **Document every public surface at the moment it is created, not retrospectively.** Every new function, method, class, hook, action, filter, REST route, MCP ability, CLI command, or other public surface is documented in `docs/api/` and/or `docs/reference/` at the same test point where it is built. The slice does not pass its Phase 5 test point until its docs are written and its example actually runs. Phase 6 *consolidates* documentation; it does not create it from scratch.
- **Maximum extensibility for extensible project types.** For project types meant to be extended (WordPress/WooCommerce plugins, MCP servers, libraries/components), expose the maximum reasonable set of extension points so third parties can modify texts, behaviors, queries, and responses from outside without forking the code. Concretely: every meaningful user-facing string passes through a filter, every meaningful decision exposes a hook before/after, every query and every response is filterable. This is decided at spec time and built into the slice, not bolted on later.
- **Real functional verification, whenever possible — not only automated tests.** If the project can be run, it gets a runnable verification environment (a *playground*: Docker/docker-compose, wp-env, a playground script, a disposable sandbox — whatever fits the stack), chosen from the per-platform recipes in `references/playground-recipes.md`, defined in the technical plan (Phase 2), stood up at the Phase 5 scaffold with synthetic seed data, and kept current. The assistant uses it at test points to exercise the software for real — full flows end to end, the CLI if one was built, real API calls — because automated tests prove the parts and the playground proves the product. **Right the first time:** anything a compile/build, a lint pass, booting the playground, or a basic test would have caught must be caught *before* the work is handed over — a defect of that class escaping a test point is a process defect (Phase 5 records it and adds the missing check). The user gets to try it too: hand over the access details when needed (URL/host, user, password — local, throwaway credentials only, never production secrets) together with step-by-step try-it instructions, maintained in `docs/playground.md`.
- **Budgets are AI-time based, never human-time based.** When the project has a client to bill or a quote to produce — asked once at Phase 1 (`Client budget:` on the project card) — the estimate is built from the AI's working hours plus the vibe coder's supervision hours (answering questions, making decisions, real-world testing the AI cannot do, uploading code) — never from what a traditional human team would take (months). Everything is itemized into segments with hours; the developer's hours are priced at their asked rate, the AI's token cost is computed per model and payment mode (≈ 0 marginal on subscription), the two blocks stay SEPARATE, and the budget is adjusted with the user before it is final. Preliminary estimate at Phase 1 close, firm estimate at Phase 2 close (plus the client budget when one exists), recomputed on scope changes. See "Estimation & budget" below and `references/estimation-budget.md`.
- **Forge issues are tracked in a living log.** Whenever the project's issues on its Git forge — GitHub, GitLab, Gitea, Bitbucket, or any other — are accessed or worked, `docs/issues.md` records the full picture at the moment it changes: the inventory of what exists, what was resolved and exactly HOW (diagnosis, resolution, commits, verification), and what remains pending. If a problem surfaces later, what was done is on record — never reconstructed from memory. Template and rules in `references/project-state.md`.
- **Confirm before advancing a phase.** Each phase has a definition of done; do not slide into the next phase with the current one's gaps open. A gate that requires evidence is checked by reading the artifact that records it, never from conversation memory.

## Phase map

Work through these in order. The reference file for a phase is the authoritative instruction set for it — read it when you enter the phase.

| Phase | Purpose | Reference to load |
|-------|---------|-------------------|
| 1. Discovery | Competitive scan first, then idea, proposed v1 (assistant proposes, user reacts), project type, constraints, preliminary estimate | `references/phase-1-discovery.md` |
| 2. Functional spec | Flows, requirements, scope, technical plan (stack/architecture/conventions/testing), what needs design, firm estimate & client budget | `references/phase-2-functional-spec.md` |
| 3. Design handoff | What to tell Design + the files Design must read/return | `references/phase-3-design-handoff.md` |
| 4. Faithful build | Audit Design's return with evidence, consolidate spec, build with zero deviation, guided external setup | `references/phase-4-faithful-build.md` |
| 5. Development | How to build: sprints planned in plan mode, assumption re-validation at every kickoff, test points, a real playground, debug logs with a switch, independent review, user verification per sprint | `references/phase-5-development.md` |
| 6. Documentation | `docs/`: API, classes, functions, usage, architecture — plus the end-user HTML guide (`guide/`: languages asked, English suggested as principal; ships-in-release asked) | `references/phase-6-documentation.md` |
| 7. Release | git hygiene, package hygiene, release prep, full-suite gate on the candidate | `references/phase-7-release.md` |
| 8. Project website (conditional) | study the product, plan & build its site: site type, sections, domain, design direction, vanilla build, self-hosted fonts, product screenshots, SEO + AEO, launch, operations | `references/phase-8-website.md` |

Phases 3 and 4 are skipped only if Phase 2 concludes the project genuinely needs no UI/design. If there is any UI, they are mandatory.

Phase 8 is **conditional**: it runs only if Phase 1 recorded website intent (yes). It's normally done after Phase 7 (the release reminds the user) but can be run whenever they're ready. It is not a separate skill — it reuses Keel's own Phases 3–7 treating the site as a "website" project, and loads its own `phase-8-*` references for the web-specific depth. If Phase 1 said no website, skip Phase 8 entirely — unless the user later explicitly asks for the site, which supersedes the recorded "no" (new decision entry, then run Phase 8 normally).

**After Phase 7 the project is not finished — it enters maintenance.** Hotfixes, rollback, dependency and CVE response, "Tested up to" bumps, recurring features, and the website freshness duty live in `references/maintenance.md`; the Resume entry mode routes there when `docs/PROGRESS.md` marks Phase 7 done.

Security is cross-cutting: the moment the project type is fixed in Phase 1, also load the matching profile from `references/security/` and keep it in mind through every later phase. See "Security routing" below.

## Security routing

After Phase 1 sets the project type, load the matching profile (don't load all of them):

| Project type | Security profile |
|--------------|------------------|
| WordPress plugin / WooCommerce extension | `references/security/wordpress.md` |
| Web app (SPA, API backend, hosted service) | `references/security/web-app.md` |
| MCP server | `references/security/mcp-server.md` |
| Reusable component / library / package | `references/security/library-component.md` |
| Website (static/marketing/product site — the Phase 8 default) | `references/security/website.md` |

If a project spans types (e.g. a WordPress plugin that ships an MCP server), load both relevant profiles and apply the stricter rule on any conflict. Phase 8 always loads `references/security/website.md` for the site itself, on top of whatever profile the product uses; a site with a real app backend adds `references/security/web-app.md`.

## Confidential data never reaches Git (cross-cutting, UNBREAKABLE)

Before EVERY commit and EVERY push — test points and sprint closes (Phase 5), the release (Phase 7), website deploys (Phase 8), adoption's first commit, any ad-hoc commit — check that nothing confidential is about to enter the repository. This is not a Phase 7 step: it applies from the project's very first commit, in every environment.

1. **Scan what is actually going in** (the staged/changed files — at Phase 7, the whole tracked tree), by name and by content:
   - By name: `.env*`, `*.pem`, `*.key`, `*.p12`/`*.pfx`, `id_rsa*`, `*credentials*`, `*secret*`, `wp-config.php` with real values, database dumps and exports (`*.sql`, `*.sqlite`), backups, local config carrying tokens.
   - By content: private-key blocks (`-----BEGIN ... PRIVATE KEY-----`), API keys and tokens (`api`+`_key` assignments, `Bearer ...`, provider-prefixed keys such as `AKIA...`, `sk-...`, `ghp_...`), passwords in config, OAuth client secrets, payment-gateway merchant keys (e.g. a Redsys SHA-256 merchant key), license keys, and real personal or customer data (names, emails, orders) in fixtures, seeds, logs, or dumps.
   - Use what the environment offers: `git status` / `git diff --staged` plus grep patterns always; a dedicated scanner (`gitleaks`, `trufflehog`) when available — helpful, never required.
2. **Something found → STOP the commit.** Warn the user explicitly, in the conversation language: name each file, say what it appears to contain, and state plainly that letting it reach the repository is a serious security risk. Then apply the fix that matches its state:
   - Not yet tracked: add it to `.gitignore` so it can never reach the repository; commit only once the exclusion is in place.
   - Tracked but never pushed: `git rm --cached` + `.gitignore`, then commit the removal.
   - Pushed at any point in history: ignoring it is NOT enough — it must be removed from history (`git filter-repo` / BFG) AND the exposed credential treated as compromised and rotated. Say this explicitly and guide the user through it if they want.
3. **The user decides, on record.** If the user confirms a flagged file is genuinely safe (placeholder or example values, sandbox-only keys meant to ship), record that decision in `docs/decisions.md` and proceed. Without that explicit confirmation, the file does not go in. Obvious placeholders (`your-api-key-here`) in templates and docs are not findings.
4. Phase 5 sets up `.gitignore` at the scaffold and Phase 7 re-verifies the whole tree before release — neither replaces this check at each commit.
5. **Never create the false positive.** When the assistant itself writes docs, decision notes, lessons, or examples, it never embeds a literal secret-shaped string (a real-looking key or token, an `api_key`-style assignment, a private-key header line) — it describes it or splits it apart. This keeps `docs/` committable with the pre-commit gate active (`references/claude-config.md`) instead of forcing bypasses on the project's own records. The same rule keeps the design handoff and `docs/BUILD-SPEC.md` committable: secret VALUES never land in `SPEC/external-setup.md` or the BUILD-SPEC — they are recorded as descriptive placeholders and exchanged only in the Phase 4 guided walkthrough (see `references/handoff-contract.md`, rule 7).

## Accessibility (cross-cutting, non-negotiable)

Accessibility is not a project type or a phase — it applies to everything built, on every platform, and it is decided and stated **up front in Phase 1**, not discovered at the end. Building accessibly from line one and "making it accessible" after the fact are different jobs; the second is a rewrite. Treat accessibility exactly like security: load its reference the moment the project type and target platform(s) are fixed in Phase 1, keep it live through every later phase, and tell the user it is in force before anything is built.

Load `references/accessibility.md` once the platform is known. It has a universal core (applies everywhere) plus a section per platform — Web/HTML, WordPress/WooCommerce, iOS/iPadOS, Android, macOS, Windows, and cross-platform frameworks. Apply the universal core plus the section(s) matching the project's target platform(s). If the project spans platforms, apply every matching section.

The commitment is the maximum reasonably achievable, never a token gesture: WCAG 2.2 AA as the floor with AAA where feasible, EN 301 549 and the European Accessibility Act where they apply (they apply to the user's EU market), and the platform's native accessibility API and assistive technologies fully supported — screen readers (VoiceOver, TalkBack, Narrator, NVDA/JAWS), Switch Control / Switch Access, Voice Control / Voice Access, Dynamic Type / system text scaling, and the reduced-motion and high-contrast preferences. "Use every accessibility tool the platform offers" is the standing rule.

Verification is split honestly: automated passes (axe-core, pa11y, Lighthouse, the platform inspectors) are run by the assistant with commands and results recorded; the real assistive-technology pass runs as a **guided user loop** — one instruction at a time, results recorded per item — defined in `references/accessibility.md` ("Guided assistive-technology pass"). It is never declared done by the assistant alone.

## Estimation & budget (cross-cutting)

Keel always produces a realistic estimate of what the work will take (`docs/estimate.md` plus the running `docs/token-ledger.md`), computed from how the work is ACTUALLY delivered: the AI's working hours plus the developer's (vibe coder's) supervision hours — never from traditional human development time. Whether it ALSO produces a client-facing budget is decided once, at Phase 1: **is there a client to bill or a quote to produce?** The answer lives on the project card as `Client budget: yes/no`. The full procedure lives in `references/estimation-budget.md`; load it at each of these moments:

- **Close of Phase 1:** preliminary estimate (wide ranges, stated as such) in `docs/estimate.md`, so the user can answer a client early — and the `Client budget:` question, asked once.
- **Close of Phase 2:** firm estimate — plus, only when `Client budget: yes`, the client-facing `docs/budget.md`: itemized segments with hours, the developer's hours at their rate (asked, with currency), the AI cost per model and payment mode (API per-token prices verified online; ≈ 0 marginal cost on subscription), the two blocks SEPARATE, the budget written in the client's language (asked), and an explicit present → adjust → approve loop with the user (e.g. choosing not to bill the AI cost because a subscription makes it a non-expense). When `Client budget: no`, none of the client questions are asked and no budget.md exists.
- **After any scope change:** follow the "Scope changes" playbook in `references/project-state.md` for the artifact loop, then recompute — new estimate version, and a re-approved budget when one exists.
- **Actuals as the project runs:** `docs/token-ledger.md` (created with Estimate v1) gets one row per working session — measured where the environment exposes usage, honestly estimated where it does not; appending the session's row is part of ending every session (see the continuation-prompt procedure in `references/project-state.md`). At release, Phase 7 closes it with the final reconciliation: total tokens by model, cost at verified prices, and the deviation vs the estimate, reported to the user — every finished project calibrates the next estimate.

## Output language & internationalization (cross-cutting contract)

The language the assistant and the user *talk in* (often Spanish) and the language the product is *built in* are two different things, decided separately. Getting this wrong has been a recurring defect, so it is fixed here as a contract.

- **The base/output language of everything built is English by default, in every project.** Source strings, UI copy, code identifiers, error messages, the code's own README, commit messages — English. Spanish is never assumed as the base language of the product. The `docs/` artifacts follow the same default — English, for token economy (see "Token economy" at the top; confirmed as the docs-language decision in Phase 1 §6). The user may choose another docs language explicitly, accepting the extra token consumption and cost; only the conversation itself follows the user's language.
- **At the start of every new project, ask the internationalization questions explicitly** (batched, in Phase 1 §6) — never assume, never skip:
  1. Will it be multi-language or single-language?
  2. Which output locales must it ship (the target languages for the built product)?
  3. Is English the base/principal language? (Default **yes**; moving off English is a conscious decision with a recorded reason.)
  4. Docs language — English by default (token economy). Confirm it, or record a different choice with the token/cost trade-off acknowledged. On resume/adoption of a project whose docs are in another language, offer a one-time full translation to English.
- **WordPress / WooCommerce projects are a fixed rule, not a matter of taste:** the base language is **always English**, and the project is **always built multi-language-ready** from line one — every user-facing string wrapped in the platform i18n functions with the correct text domain, and a `.pot` generated from the English source. A Spanish-hardcoded (or Spanish-base) WordPress/WooCommerce project is a defect, not a valid outcome. This is recorded in `decisions.md` at Phase 1 and verified in Phase 5.
- Retrofitting i18n, or switching the base language after the fact, is a rewrite — not a tweak. That is exactly why the decision is fixed in Phase 1 and never left implicit.

## Writing quality — perfect orthography (cross-cutting, UNBREAKABLE)

Everything the assistant writes, in any language and on any surface (chat replies, `docs/`, code comments, UI copy, commit messages, release notes), must be orthographically and grammatically perfect. This is a standing contract with no exceptions and is not overridable by speed, informality, or context.

For **Spanish** specifically — because this is where mistakes have repeatedly slipped through — the rule is absolute:

- Every accent/tilde is written: á, é, í, ó, ú, ü. Never "informacion", "espanol", "anadir", "codigo", "articulo", "prestamo" — always "información", "español", "añadir", "código", "artículo", "préstamo".
- Every ñ is written as ñ, never plain "n" (año, not "ano"; señal, not "senal"; diseño, not "diseno").
- Opening marks are always present: ¿…? and ¡…!.
- Agreement (gender/number), verb tenses, and prepositions are correct.

Treat a spelling or grammar mistake exactly like a code bug: it is caught and fixed, never shipped. If unsure of a spelling, verify it instead of guessing. The same standard of correctness applies to every other language the project is written in.

## How to run a phase

1. Announce the phase to the user in one line.
2. Read that phase's reference file (once — do not re-read it later in the session).
3. Do the phase's work, asking the user batched questions for anything undefined (use the interactive question tool if available). **Every question must be answerable by a non-developer:** it carries a recommended default and a one-line plain-language explanation of what it means and why the default is sensible. "I don't know / whatever you think" is a valid answer — record the default in `docs/decisions.md` as "default accepted" and move on. Never stall a phase on a question the user cannot answer.
4. Produce that phase's artifacts into the project (most land in `docs/`; see Phase 6 for the docs layout), updating `docs/PROGRESS.md` and `docs/decisions.md` as the work happens — not at the end.
5. Check the phase's definition of done **item by item**, and report it to the user as an explicit checklist (✓ met / ✗ not met, one line each). Where an item demands evidence (a command's output, a recorded result), the check reads the artifact — never conversation memory. If gaps remain that are the user's call → ask. If gaps are design-side → Design Request (Phase 4 mechanism). Do not advance with any ✗ open.
6. Mark the phase done in `docs/PROGRESS.md` (with its artifacts) and set the next action. Briefly tell the user what was produced and what the next phase will do.

## Entry modes (decide which one applies before doing anything)

1. **New project** — no code yet. Read `references/project-state.md`, initialize the state files (confirming the project directory with the user first), and run Phase 1.
2. **Resume** — `docs/PROGRESS.md` exists. Follow the fixed session-start order from `references/project-state.md`: `docs/PROGRESS.md` (project card, phase status, exact position, open items) → `docs/decisions.md` (never re-litigate) → `docs/lessons-learned.md` (never repeat) → the current phase's reference → only the inputs PROGRESS.md names. Continue from where things stand — never restart, never reinterpret decisions already made. If the project card's `Keel baseline:` is older than the running Keel (or missing), offer the post-update reconciliation from `references/project-state.md` before continuing. If PROGRESS.md marks Phase 7 done, the work is maintenance: load `references/maintenance.md`. (Keel-built projects that somehow lack state: identify the furthest completed phase from the artifacts in `docs/`, create the state files, then continue.)
3. **Adoption** — real code exists (often released, often with users) but no Keel state: the project predates Keel. Read `references/adoption.md` and follow it: inventory read-only, initialize state and the CLAUDE.md lock, ask the never-made Phase 1 decisions, reconstruct `01/02/03` as-built plus a complete `docs/api/INDEX.md`, audit gaps into `docs/04-adoption-audit.md`, prioritize them with the user, then continue as a normal Keel project. Adoption changes no code.

Portability lock: every Keel project carries a `CLAUDE.md` block (plus optionally the skill embedded at `.claude/skills/keel/`) so that ANY environment or AI opening the repo — Claude app, Cowork, Claude Code, or another assistant — is bound to this workflow even without the skill installed. Defined in `references/project-state.md` ("Portability"); created in Phase 1 step 0a / adoption step 2. If you are running in a project whose lock is missing or predates this mechanism, add it (with the user's OK) before continuing. Projects may additionally carry the optional native Claude Code config package — rules, agents, settings, the confidential-data pre-commit gate, CI — defined in `references/claude-config.md`.

Ending a session mid-work (any phase): append the session's row to `docs/token-ledger.md`, then produce the self-sufficient continuation prompt from `references/project-state.md` and SHOW it to the user proactively — with the one-line instruction to paste it into a new chat — so the next chat resumes exactly where this one stopped. The user never has to ask for it.

## Shared templates and contract

- `references/keel-maintenance.md` — the skill's own upkeep: the session-start update check with its 24-hour throttle, lock freshness, version reporting, and the full UNBREAKABLE version change policy. Executed once per session (see "Skill maintenance" at the top).
- `references/project-state.md` — the living state system (PROGRESS.md, decisions.md, lessons-learned.md, Design Request register, api/INDEX.md), the universal continuation prompt, the scope-change playbook, and the context & cache discipline. Read at project start (Phase 1) and on every resume.
- `references/playground-recipes.md` — the per-platform playground recipes (wp-env, MCP Inspector, Playwright, clean consumer project) with seed data and gate zero. Consulted at Phase 2 §4 (Testing) and stood up at the Phase 5 scaffold.
- `references/maintenance.md` — the post-release lifecycle: triage, hotfix path, rollback, dependency/CVE duty, recurring features, site freshness. Loaded on Resume when Phase 7 is done.
- `references/estimation-budget.md` — the AI-time estimation & client-budget procedure (preliminary at Phase 1 close, firm at Phase 2 close, recomputed on scope changes; client budget only when one exists).
- `references/claude-config.md` — the optional native Claude Code package for the project (`.claude/rules/`, `.claude/agents/` — reviewer and verifier subagents, `.claude/settings.json`, the confidential-data pre-commit gate, `.mcp.json`, CI). Offered once at Phase 1 step 0a / adoption step 2; rules and agents materialize at Phase 2 close; settings, gate, `.mcp.json`, and CI at the Phase 5 scaffold.
- `MANIFEST.md` (skill root) — the parity manifest: everything a Keel project must contain (phase- and condition-aware, Table 1), which skill files changed in which version (Table 2 — the re-read map), and the per-version action list (Table 3 — the reconciliation delta). First input of the post-update reconciliation; usable any time for a full audit.
- `references/handoff-contract.md` — the exact `design-handoff/` structure that flows Design → Build. Used by Phases 3 and 4. Read before either.
- `references/design-brief-template.md` — the brief to give Design (Phase 3).
- `references/build-spec-template.md` — the consolidated `docs/BUILD-SPEC.md` (Phase 4).
- `references/design-request-template.md` — the prompt back to Design when the handoff has gaps (Phase 4).

## Reference index

- `references/keel-maintenance.md` (executed at every session start — update check, lock freshness, version policy)
- `references/phase-1-discovery.md`
- `references/phase-2-functional-spec.md`
- `references/phase-3-design-handoff.md`
- `references/phase-4-faithful-build.md`
- `references/phase-5-development.md`
- `references/phase-6-documentation.md`
- `references/phase-7-release.md`
- `references/phase-8-website.md` (conditional — orchestrates the website sub-phase)
- `references/phase-8-site-discovery.md`
- `references/phase-8-section-catalogue.md`
- `references/phase-8-domain-decision.md`
- `references/phase-8-design-direction.md`
- `references/phase-8-technical-seo.md`
- `references/phase-8-launch-checklist.md`
- `references/project-state.md` (cross-cutting — state, resume, scope changes, context & cache discipline, portability lock; loaded at project start and on resume)
- `references/adoption.md` (entry mode 3 — adopting Keel in an existing project)
- `references/maintenance.md` (post-release — hotfix, rollback, dependencies/CVEs, recurring features, site freshness)
- `references/playground-recipes.md` (cross-cutting — per-platform verification environments and seed data; Phase 2 §4 and the Phase 5 scaffold)
- `references/claude-config.md` (cross-cutting — optional native Claude Code project config: rules, agents, settings, pre-commit gate, `.mcp.json`, CI; offered at 0a/adoption, materialized at Phase 2 close and the Phase 5 scaffold)
- `references/estimation-budget.md` (cross-cutting — AI-time estimation & client budget; loaded at Phase 1 close, Phase 2 close, and on scope changes)
- `references/handoff-contract.md`
- `references/design-brief-template.md`
- `references/build-spec-template.md`
- `references/design-request-template.md`
- `references/accessibility.md` (cross-cutting — non-negotiable, loaded from Phase 1 like the security profile; includes the guided assistive-technology pass)
- `references/security/wordpress.md`
- `references/security/web-app.md`
- `references/security/mcp-server.md`
- `references/security/library-component.md`
- `references/security/website.md` (Phase 8 — the site's own profile)
