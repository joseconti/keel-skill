---
name: keel
license: GPL-3.0-or-later
metadata:
  version: 1.11.0
description: Use this skill for ANY new software project from idea to release — websites, WordPress/WooCommerce plugins, MCP servers, web apps, components, or libraries. Multi-phase workflow: discovery with competitive scan, functional spec with flows, design handoff to Claude Design, faithful build with zero deviation, development with test points and a real-testing playground, full docs/, per-platform security, non-negotiable accessibility, release hygiene, AI-time estimates with client budgets, and a forge issue log. Trigger when the user starts a new project or feature, says "I have an idea for a plugin/site/app", "let's plan this project", mentions a design handoff, asks for docs or security review, asks what a project will cost or take (quote/budget), works forge issues (GitHub/GitLab/...), prepares a release, resumes an in-progress Keel project (any repo with docs/PROGRESS.md), or applies Keel to an EXISTING project (adoption). Phases load references on demand; living state makes projects resumable across chats.
---

# Keel — project lifecycle (idea → release)

**Keel v1.11.0** — Licensed under GPL-3.0-or-later. *Keel* is the structural backbone laid down first, on which the whole project is built.

## Token economy — everything is created in English by default (READ FIRST)

English is the most token-efficient language for an LLM: the same content in Spanish or another Latin-script language costs roughly 15–30% more tokens (non-Latin scripts, far more), and Keel re-reads its living state (`docs/PROGRESS.md`, `docs/decisions.md`, `docs/lessons-learned.md`) in every session, so any per-word overhead compounds for the entire life of the project.

Therefore **everything Keel creates is written in English by default** — every `docs/` artifact (discovery, specs, progress, decisions, lessons learned, architecture, API reference, playground instructions), every continuation prompt for a new chat, every prompt or brief handed to Claude Code or Claude Design (design briefs, design requests, build specs), every template instance, report, commit message, and code comment — in addition to the product output itself, which is already English-based per "Output language & internationalization" below.

**Announce it up front.** At the start of every new project (and every adoption), tell the user in one line: everything Keel creates will be in English to minimize token consumption and therefore cost; if they prefer another language for the docs or any other artifact set, they only have to say so, knowing that it will increase token usage and spend. If the user chooses another language, honor it, record it in the project card and `docs/decisions.md` with the trade-off acknowledged, and apply it consistently from then on.

**Existing projects whose docs are in another language** (resume or adoption): ask the user once whether they want the existing documentation translated to English, stating the token/cost benefit in one line. If yes, translate it all and record the switch in `decisions.md`; if no, record the choice, keep that language consistently, and do not ask again.

**This is NOT about the conversation.** Keep talking to the user in whatever language the user writes (usually Spanish), exactly as always — the English default governs only what Keel *creates*. And it never removes product locales: what end users see follows the Phase 1 §6 i18n decisions; the product's translations are never dropped to save tokens.

## Version reporting

If the user asks which version of Keel they have or are using (e.g. "what version is this skill", "which Keel version do I have"), state it plainly from the frontmatter: "You're using Keel v1.11.0." Keep the version in the frontmatter (`metadata.version`), this line, and `CHANGELOG.md` in sync whenever the skill is updated; the frontmatter is the source of truth.

## Update check (start of every session)

Keel is distributed from `https://github.com/joseconti/keel-skill` (releases: `https://github.com/joseconti/keel-skill/releases`). Once per session, when Keel is invoked and before the entry-mode decision, check whether a newer release exists. Reading this section IS the cue: run the check the moment you read it, before any project work. In a Keel project's repo the `CLAUDE.md` lock makes this its step 1 — the full read of this SKILL.md comes BEFORE even the state files, at every session start — precisely so this check runs in every session, whether or not the skill auto-triggered. The check is best-effort and must never block, delay, or interrupt the work: if any step fails (no network, no fetch mechanism, API error), skip silently, continue with the running version, and do not retry in this session.

1. **Detect the latest version.** Preferred method (works in any environment with git, no API and no auth): `git ls-remote --tags https://github.com/joseconti/keel-skill.git` → take the highest semver tag. Strip the leading `v` and compare segment by segment as numbers (`1.10.0` > `1.9.0`) — never as strings; ignore tags that are not `vX.Y.Z`. Fallbacks, in order: GET `https://api.github.com/repos/joseconti/keel-skill/releases/latest` (field `tag_name`) with a web-fetch tool, or fetch the releases page. If the environment provides no mechanism at all, skip.
2. **Compare against EVERY copy in play, not only the running one:** the environment's install AND, when the session is working inside a project that embeds the skill, the project's `.claude/skills/keel/` (each copy's frontmatter `metadata.version` — the source of truth). A copy can be behind even when the running one is current — in Cowork it is common that the app install is up to date while the opened project's embedded copy is not; that embedded copy must still be updated. All copies at the latest version → say nothing and continue.
3. **Newer release found → update every copy the environment can durably write; inform about the rest.** Up to two copies can be in play: the environment's own install (a user-level `~/.claude/skills/keel/`, or app-managed skill storage) and the project's embedded copy (`.claude/skills/keel/`).
   - **For each copy that is writable and persists across sessions** — the user-level install, and ALWAYS the project's embedded copy when one exists (the normal case when Claude Code or Cowork is working inside a Keel project's repo: the same duty that put the embedded copy there also keeps it current): announce it in one line (vCURRENT → vNEW), download the release once — `git clone --depth 1 --branch vX.Y.Z https://github.com/joseconti/keel-skill.git` or the tag archive `https://github.com/joseconti/keel-skill/archive/refs/tags/vX.Y.Z.tar.gz`; if an already-current local copy exists (e.g. the app install is at the latest version and only the project's embedded copy is behind), copy from it instead of downloading, per the version-sync rule in `references/project-state.md` — and replace that copy's ENTIRE tree with the new `keel/` directory following the verified full-copy protocol in `references/project-state.md` ("Portability"): whole tree, verify file-for-file against the source, retry once; if it still fails, abort that copy's update (never the session), leave it intact, and treat it under the inform path below. After a verified replacement: summarize the improvements to the user from the new `CHANGELOG.md` (every entry after the previously running version), re-read the new `SKILL.md` and the current phase's reference from the new copy (the copies in context belong to the old version), and continue under the new version. When the session is working inside a Keel project, then run the **post-update reconciliation** (`references/project-state.md`, "Post-update reconciliation") so the project itself catches up with what the new version introduces — new required files or directories, new project-card lines, lock-block changes, never-asked questions — tracked by the project card's `Keel baseline:` line.
   - **For a copy that cannot be updated durably** — app-managed or ephemeral skill storage (common in the Claude app / Cowork) or no write access: tell the user once, briefly, in the conversation language: a newer Keel exists (vCURRENT → vNEW), what it improves (the new `CHANGELOG.md` entries after the running version — e.g. from `https://raw.githubusercontent.com/joseconti/keel-skill/main/keel/CHANGELOG.md`; if unreachable, point to the release notes on the releases page), and how to update it themselves — the app-installed skill is the user's to update (repository `INSTALL.md`, section "Updating"). If the project's embedded copy WAS updated and only the app/environment install could not be, say exactly that — the project is already current; updating the installed skill in the app is what remains. Then continue normally and do not repeat the notice this session.

**Lock freshness (same moment, every session inside a Keel project).** After the update check, verify the project's `CLAUDE.md` Keel block is current by its stamp alone — a one-line look, never a content comparison: the `KEEL:BEGIN` delimiter carries the version of the Keel that last wrote the block (`KEEL:BEGIN — vX.Y.Z do not remove: …`). Stamp equal to the running version → current, done. Stamp different or missing (blocks from before v1.11.0 carry no stamp; match delimiters by the `KEEL:BEGIN` prefix, never by exact text) → refresh: rewrite the block between the delimiters from the canonical copy in `references/project-state.md` ("Portability" §1), restamped with the running version, with the user's OK (mirror `AGENTS.md` if the project keeps one). Never touch anything outside the delimiters. This is what keeps the always-loaded `CLAUDE.md` rules from drifting behind the skill.

Overwriting the skill is safe: Keel is stateless — project artifacts live in each project's `docs/`, never in the skill folder (see the repository's `INSTALL.md`). Installing an official newer release is an installation, not an authoring edit: it does not fall under the version change policy below, which governs hand-editing version strings in this copy.

## Version change policy (UNBREAKABLE RULE — never bump under any circumstance without explicit user instruction)

This rule is **unbreakable**. There are no exceptions, no edge cases, no judgment calls. It overrides every other instinct or inference the assistant might have about how version numbers "should" evolve based on the scale of the edit.

The Keel version — in `metadata.version` in the frontmatter, in the heading line above, and in `CHANGELOG.md` — must NEVER be changed unless the user has **explicitly instructed it in the current conversation** (e.g. "bump to 1.1.0", "release 1.0.1", "this is version 2", "tag a new minor release"). An explicit "yes" to a direct question about a specific version also counts as explicit instruction. Nothing else does.

What does NOT count as authorisation to change the version:

- The scale of the edits in this conversation (large rewrites, full re-architectures, adding whole phases — none of these authorise a bump).
- Inferring from changelog conventions that "this looks like a minor".
- The user thanking the assistant for the work, or saying it's good.
- The user mentioning the project is "ready to release" without naming a version.
- Any reasoning the assistant produces internally about semantic versioning.
- A previous conversation in which a bump was discussed but not executed.

Required behavior:

- When editing any skill file for any reason, leave `metadata.version`, the heading version line, and `CHANGELOG.md` untouched. Do not add a new changelog entry on your own initiative.
- If you believe a bump is warranted, ASK the user explicitly: state what was changed, propose a specific number (patch / minor / major with reasoning), and WAIT for explicit approval before touching any of the three locations. Do not pre-edit speculatively.
- If the user explicitly instructs a bump, perform it and keep all three locations in sync (frontmatter is the source of truth).
- If the three locations ever drift, surface the drift to the user and ask which version is correct — never silently realign them.

If at any point the assistant is about to write a version number that the user did not explicitly authorise in the current conversation, the assistant must stop and ask. This rule is not contextual, not negotiable, and not overridable by other instructions in the same conversation unless those instructions are themselves explicit user authorisation for a specific version.

Scope note: this rule governs **Keel's own version** (this skill's files). The versions of projects *built with* Keel follow their own project rules (Phase 7 versioning) and are not restricted by this section. Likewise, replacing the whole running copy with an official newer release per the update check above is an installation, not a version edit — it needs no bump authorisation.

## Why this skill exists

The user builds many projects (WordPress/WooCommerce plugins, MCP servers, web apps, components, libraries) and was repeating the same standing requirements every time: document everything, security per platform, full API/class/function docs in a `docs/` dir, a design handoff that doesn't waste tokens, a build that stays faithful to the design, proper git/package hygiene. This skill encodes that whole process once. Follow the phases in order; load each phase's reference file only when you reach it (progressive disclosure — do not pull every reference into context at once).

## Operating principles (hold across every phase)

- **Keep the living state current from the first minute.** `docs/PROGRESS.md`, `docs/decisions.md`, and `docs/lessons-learned.md` are created the moment Phase 1 starts (per `references/project-state.md`) and updated at the moment of every change — not at phase ends. A fresh chat resumes from state, never from re-scanning code or re-asking the user. Decisions recorded in `decisions.md` are never re-opened by the assistant on its own initiative.
- **Work from recorded state; read code surgically.** Orient via `docs/PROGRESS.md`, the technical plan's code map, `docs/architecture.md`, and `docs/api/INDEX.md` — then open only the specific file needed. Read each static reference once per session, in the fixed order defined in `references/project-state.md`; never re-read files already in context. This keeps sessions cheap, deterministic, and prompt-cache-friendly.
- **Decide the project type early and let it drive everything.** Web / WordPress plugin / WooCommerce extension / MCP server / web app / component / library. Type selects the security profile, the structure, and what needs design.
- **Assess ideas and decisions honestly, even when it's uncomfortable.** Never default to praise. If an idea, a feature, a scope, or an approach is weak, say so with the reason and a concrete alternative. False encouragement wastes the user's time, which is the opposite of this skill's purpose. The user has explicitly asked for the truth even when it hurts.
- **Document as you go, in `docs/`.** Documentation is not a final-phase afterthought; each phase contributes its artifacts to `docs/`.
- **Never invent or interpret silently.** When something is undefined, ask the user. When a design detail is missing downstream, request it from Design — don't guess.
- **Code adapts to the design, never the design to the code.** The build follows the design to the letter; where the stack forces a change, the code strategy changes (and is logged), never the design intent. This is enforced through the handoff contract (Phases 3–4).
- **Design delivers build-ready assets; the build never transforms them.** Every screen handed to Design is defined by what it *does* (its functionalities), not just how it looks. Design applies the existing design system exactly (divergence is a Design Request, never a creative choice) and delivers every logo and icon in **both SVG and PNG**, plus every asset in a format the build drops in directly — so Code never has to convert, resize, recolor, or re-export. When the handoff arrives, the first action is a completeness gate: verify Design delivered everything without exception; anything missing becomes a registered Design Request (a file + a ready-to-paste prompt) for Design to finish, never a build-side workaround. See Phases 3–4 and `references/handoff-contract.md`.
- **Security is per-platform and non-optional.** The relevant profile is consulted from Phase 1 onward, not bolted on at the end.
- **Nothing confidential ever reaches Git (UNBREAKABLE).** Every commit is preceded by a confidential-data check on the files about to enter the repository — secrets, credentials, private keys, tokens, real personal/customer data. A finding STOPS the commit: the user is warned, file by file, that pushing it is a serious security risk, and the fix is applied (`.gitignore` exclusion, untracking, history purge plus credential rotation if it was ever pushed) before anything is committed. See "Confidential data never reaches Git" below.
- **Accessibility is non-negotiable, on every platform, and designed in from the first line — never retrofitted.** Whatever is built — HTML, iOS, Android, macOS, Windows, or a cross-platform framework — is usable with assistive technology from the first slice, using every accessibility tool the platform offers. It is stated up front in Phase 1 (like the internationalization decision) precisely because building accessibly from the start and "making it accessible" at the end are not the same work — the second is a rewrite. The target is the maximum reasonably achievable: WCAG 2.2 AA as the floor (AAA where feasible), EN 301 549 and the European Accessibility Act where they apply, and the native accessibility API on every other platform. See "Accessibility" below and `references/accessibility.md`.
- **Output language is English by default — always, and never Spanish.** The primary language of everything *built* (source strings, UI copy, code identifiers, error messages, commit messages, API responses) defaults to English in every project, regardless of the language the user and the assistant converse in. Spanish is never assumed as the base language of the product. For WordPress/WooCommerce the base language is *always* English and the project is *always* prepared to be multi-language — non-negotiable. The multi-language questions are asked explicitly at project start (see "Output language & internationalization" below and Phase 1 §6). The docs — and everything else Keel creates (continuation prompts, briefs for Code/Design, lessons learned) — default to English as well, for token economy (see "Token economy" at the top); another language only on explicit request, with the extra token cost made clear.
- **Perfect orthography in every language — Spanish especially (UNBREAKABLE).** Everything the assistant writes for the user — chat, `docs/`, code comments, UI copy, commit messages — is spelled and punctuated perfectly. In Spanish this means every ñ, every accent/tilde (á é í ó ú ü) and every opening ¿/¡ is present and correct, with zero spelling or grammatical errors. This is a hard contract, not a preference: dropping accents or the ñ, or writing "espanol"/"anadir"/"informacion", is a defect to be fixed like any other. See "Writing quality — perfect orthography" below.
- **Build once, reuse by manifest.** Never regenerate structurally-identical pages/screens.
- **Reuse internal API; never duplicate code.** Before writing any new function, method, or class, search the project's existing internal API. If a suitable function already exists, reuse it. If one is *close* but not exact, generalize it (parameterize) rather than fork it. Write a new function only when there is no existing fit. Duplication is treated as a defect, the same as a security issue: it gets refactored, not left behind. The internal API grows deliberately and is documented as it grows (see next).
- **Document every public surface at the moment it is created, not retrospectively.** Every new function, method, class, hook, action, filter, REST route, MCP ability, CLI command, or other public surface is documented in `docs/api/` and/or `docs/reference/` at the same test point where it is built. The slice does not pass its Phase 5 test point until its docs are written and its example actually runs. Phase 6 *consolidates* documentation; it does not create it from scratch.
- **Maximum extensibility for extensible project types.** For project types meant to be extended (WordPress/WooCommerce plugins, MCP servers, libraries/components), expose the maximum reasonable set of extension points so third parties can modify texts, behaviors, queries, and responses from outside without forking the code. Concretely: every meaningful user-facing string passes through a filter, every meaningful decision exposes a hook before/after, every query and every response is filterable. This is decided at spec time and built into the slice, not bolted on later.
- **Real functional verification, whenever possible — not only automated tests.** If the project can be run, it gets a runnable verification environment (a *playground*: Docker/docker-compose, wp-env, a playground script, a disposable sandbox — whatever fits the stack), defined in the technical plan (Phase 2), stood up at the Phase 5 scaffold, and kept current. The assistant uses it at test points to exercise the software for real — full flows end to end, the CLI if one was built, real API calls — because automated tests prove the parts and the playground proves the product. The user gets to try it too: hand over the access details when needed (URL/host, user, password — local, throwaway credentials only, never production secrets) together with step-by-step try-it instructions, maintained in `docs/playground.md`.
- **Budgets are AI-time based, never human-time based.** When the user needs to quote the project (or a feature) to a client, the estimate is built from the AI's working hours plus the vibe coder's supervision hours (answering questions, making decisions, real-world testing the AI cannot do, uploading code) — never from what a traditional human team would take (months). Everything is itemized into segments with hours; the developer's hours are priced at their asked rate, the AI's token cost is computed per model and payment mode (≈ 0 marginal on subscription), the two blocks stay SEPARATE, and the budget is adjusted with the user before it is final. Preliminary estimate at Phase 1 close, firm estimate and client budget at Phase 2 close, recomputed on scope changes. See "Estimation & budget" below and `references/estimation-budget.md`.
- **Forge issues are tracked in a living log.** Whenever the project's issues on its Git forge — GitHub, GitLab, Gitea, Bitbucket, or any other — are accessed or worked, `docs/issues.md` records the full picture at the moment it changes: the inventory of what exists, what was resolved and exactly HOW (diagnosis, resolution, commits, verification), and what remains pending. If a problem surfaces later, what was done is on record — never reconstructed from memory. Template and rules in `references/project-state.md`.
- **Confirm before advancing a phase.** Each phase has a definition of done; do not slide into the next phase with the current one's gaps open.

## Phase map

Work through these in order. The reference file for a phase is the authoritative instruction set for it — read it when you enter the phase.

| Phase | Purpose | Reference to load |
|-------|---------|-------------------|
| 1. Discovery | Competitive scan first, then idea, feature discussion, project type, constraints, preliminary estimate | `references/phase-1-discovery.md` |
| 2. Functional spec | Flows, requirements, scope, technical plan (stack/architecture/conventions), what needs design, firm estimate & client budget | `references/phase-2-functional-spec.md` |
| 3. Design handoff | What to tell Design + the files Design must read/return | `references/phase-3-design-handoff.md` |
| 4. Faithful build | Audit Design's return, consolidate spec, build with zero deviation, guided external setup | `references/phase-4-faithful-build.md` |
| 5. Development | How to build, with test points throughout | `references/phase-5-development.md` |
| 6. Documentation | `docs/`: API, classes, functions, usage, architecture | `references/phase-6-documentation.md` |
| 7. Release | git hygiene, package hygiene, release prep | `references/phase-7-release.md` |
| 8. Project website (conditional) | study the product, plan & build its site: site type, sections, domain, design direction, vanilla build, self-hosted fonts, product screenshots, SEO + AEO, launch | `references/phase-8-website.md` |

Phases 3 and 4 are skipped only if Phase 2 concludes the project genuinely needs no UI/design. If there is any UI, they are mandatory.

Phase 8 is **conditional**: it runs only if Phase 1 recorded website intent (yes). It's normally done after Phase 7 (the release reminds the user) but can be run whenever they're ready. It is not a separate skill — it reuses Keel's own Phases 3–7 treating the site as a "website" project, and loads its own `phase-8-*` references for the web-specific depth. If Phase 1 said no website, skip Phase 8 entirely.

Security is cross-cutting: the moment the project type is fixed in Phase 1, also load the matching profile from `references/security/` and keep it in mind through every later phase. See "Security routing" below.

## Security routing

After Phase 1 sets the project type, load exactly one profile (don't load all of them):

| Project type | Security profile |
|--------------|------------------|
| WordPress plugin / WooCommerce extension | `references/security/wordpress.md` |
| Web app (SPA, API backend, hosted service) | `references/security/web-app.md` |
| MCP server | `references/security/mcp-server.md` |
| Reusable component / library / package | `references/security/library-component.md` |

If a project spans types (e.g. a WordPress plugin that ships an MCP server), load both relevant profiles and apply the stricter rule on any conflict.

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
5. **Never create the false positive.** When the assistant itself writes docs, decision notes, lessons, or examples, it never embeds a literal secret-shaped string (a real-looking key or token, an `api_key`-style assignment, a private-key header line) — it describes it or splits it apart. This keeps `docs/` committable with the pre-commit gate active (`references/claude-config.md`) instead of forcing bypasses on the project's own records.

## Accessibility (cross-cutting, non-negotiable)

Accessibility is not a project type or a phase — it applies to everything built, on every platform, and it is decided and stated **up front in Phase 1**, not discovered at the end. Building accessibly from line one and "making it accessible" after the fact are different jobs; the second is a rewrite. Treat accessibility exactly like security: load its reference the moment the project type and target platform(s) are fixed in Phase 1, keep it live through every later phase, and tell the user it is in force before anything is built.

Load `references/accessibility.md` once the platform is known. It has a universal core (applies everywhere) plus a section per platform — Web/HTML, WordPress/WooCommerce, iOS/iPadOS, Android, macOS, Windows, and cross-platform frameworks. Apply the universal core plus the section(s) matching the project's target platform(s). If the project spans platforms, apply every matching section.

The commitment is the maximum reasonably achievable, never a token gesture: WCAG 2.2 AA as the floor with AAA where feasible, EN 301 549 and the European Accessibility Act where they apply (they apply to the user's EU market), and the platform's native accessibility API and assistive technologies fully supported — screen readers (VoiceOver, TalkBack, Narrator, NVDA/JAWS), Switch Control / Switch Access, Voice Control / Voice Access, Dynamic Type / system text scaling, and the reduced-motion and high-contrast preferences. "Use every accessibility tool the platform offers" is the standing rule.

## Estimation & budget (cross-cutting)

When the user needs to price the project for a client — the normal case when someone asks them for a quote — Keel produces a realistic, itemized estimate and a client-ready budget, computed from how the work is ACTUALLY delivered: the AI's working hours plus the developer's (vibe coder's) supervision hours — never from traditional human development time. The full procedure lives in `references/estimation-budget.md`; load it at each of these moments:

- **Close of Phase 1:** preliminary estimate (wide ranges, stated as such) in `docs/estimate.md`, so the user can answer a client early.
- **Close of Phase 2:** firm estimate plus the client-facing `docs/budget.md` — itemized segments with hours, the developer's hours at their rate (asked, with currency), the AI cost per model and payment mode (API per-token prices verified online; ≈ 0 marginal cost on subscription), the two blocks SEPARATE, the budget written in the client's language (asked), and an explicit present → adjust → approve loop with the user (e.g. choosing not to bill the AI cost because a subscription makes it a non-expense).
- **After any scope change:** recompute, new budget version, re-approve.
- **Actuals as the project runs:** `docs/token-ledger.md` (created with Estimate v1) gets one row per working session — measured where the environment exposes usage, honestly estimated where it does not. At release, Phase 7 closes it with the final reconciliation: total tokens by model, cost at verified prices, and the deviation vs the estimate, reported to the user — every finished project calibrates the next estimate.

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
3. Do the phase's work, asking the user batched questions for anything undefined (use the interactive question tool if available).
4. Produce that phase's artifacts into the project (most land in `docs/`; see Phase 6 for the docs layout), updating `docs/PROGRESS.md` and `docs/decisions.md` as the work happens — not at the end.
5. Check the phase's definition of done **item by item**, and report it to the user as an explicit checklist (✓ met / ✗ not met, one line each). If gaps remain that are the user's call → ask. If gaps are design-side → Design Request (Phase 4 mechanism). Do not advance with any ✗ open.
6. Mark the phase done in `docs/PROGRESS.md` (with its artifacts) and set the next action. Briefly tell the user what was produced and what the next phase will do.

## Entry modes (decide which one applies before doing anything)

1. **New project** — no code yet. Read `references/project-state.md`, initialize the state files (confirming the project directory with the user first), and run Phase 1.
2. **Resume** — `docs/PROGRESS.md` exists. Follow the fixed session-start order from `references/project-state.md`: `docs/PROGRESS.md` (project card, phase status, exact position, open items) → `docs/decisions.md` (never re-litigate) → `docs/lessons-learned.md` (never repeat) → the current phase's reference → only the inputs PROGRESS.md names. Continue from where things stand — never restart, never reinterpret decisions already made. If the project card's `Keel baseline:` is older than the running Keel (or missing), offer the post-update reconciliation from `references/project-state.md` before continuing. (Keel-built projects that somehow lack state: identify the furthest completed phase from the artifacts in `docs/`, create the state files, then continue.)
3. **Adoption** — real code exists (often released, often with users) but no Keel state: the project predates Keel. Read `references/adoption.md` and follow it: inventory read-only, initialize state and the CLAUDE.md lock, ask the never-made Phase 1 decisions, reconstruct `01/02/03` as-built plus a complete `docs/api/INDEX.md`, audit gaps into `docs/04-adoption-audit.md`, prioritize them with the user, then continue as a normal Keel project. Adoption changes no code.

Portability lock: every Keel project carries a `CLAUDE.md` block (plus optionally the skill embedded at `.claude/skills/keel/`) so that ANY environment or AI opening the repo — Claude app, Cowork, Claude Code, or another assistant — is bound to this workflow even without the skill installed. Defined in `references/project-state.md` ("Portability"); created in Phase 1 step 0a / adoption step 2. If you are running in a project whose lock is missing or predates this mechanism, add it (with the user's OK) before continuing. Projects may additionally carry the optional native Claude Code config package — rules, agents, settings, the confidential-data pre-commit gate — defined in `references/claude-config.md`.

Ending a session mid-work (any phase): produce the self-sufficient continuation prompt from `references/project-state.md` so the next chat resumes exactly where this one stopped.

## Shared templates and contract

- `references/project-state.md` — the living state system (PROGRESS.md, decisions.md, lessons-learned.md, Design Request register, api/INDEX.md), the universal continuation prompt, and the context & cache discipline. Read at project start (Phase 1) and on every resume.
- `references/estimation-budget.md` — the AI-time estimation & client-budget procedure (preliminary at Phase 1 close, firm at Phase 2 close, recomputed on scope changes).
- `references/claude-config.md` — the optional native Claude Code package for the project (`.claude/rules/`, `.claude/agents/`, `.claude/settings.json`, the confidential-data pre-commit gate, `.mcp.json`). Offered once at Phase 1 step 0a / adoption step 2; rules and agents materialize at Phase 2 close; settings, gate, and `.mcp.json` at the Phase 5 scaffold.
- `references/handoff-contract.md` — the exact `design-handoff/` structure that flows Design → Build. Used by Phases 3 and 4. Read before either.
- `references/design-brief-template.md` — the brief to give Design (Phase 3).
- `references/build-spec-template.md` — the consolidated `BUILD-SPEC.md` (Phase 4).
- `references/design-request-template.md` — the prompt back to Design when the handoff has gaps (Phase 4).

## Reference index

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
- `references/project-state.md` (cross-cutting — state, resume, context & cache discipline, portability lock; loaded at project start and on resume)
- `references/adoption.md` (entry mode 3 — adopting Keel in an existing project)
- `references/claude-config.md` (cross-cutting — optional native Claude Code project config: rules, agents, settings, pre-commit gate, `.mcp.json`; offered at 0a/adoption, materialized at Phase 2 close and the Phase 5 scaffold)
- `references/estimation-budget.md` (cross-cutting — AI-time estimation & client budget; loaded at Phase 1 close, Phase 2 close, and on scope changes)
- `references/handoff-contract.md`
- `references/design-brief-template.md`
- `references/build-spec-template.md`
- `references/design-request-template.md`
- `references/accessibility.md` (cross-cutting — non-negotiable, loaded from Phase 1 like the security profile)
- `references/security/wordpress.md`
- `references/security/web-app.md`
- `references/security/mcp-server.md`
- `references/security/library-component.md`
