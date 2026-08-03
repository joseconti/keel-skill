# Keel maintenance — update check, permission mode, lock freshness, version policy

Loaded and executed ONCE per session, when Keel is invoked and before the entry-mode decision. Reading this file IS the cue: run the checks the moment you read it, before any project work. In a Keel project's repo the `CLAUDE.md` lock makes the full `SKILL.md` read its step 1, and SKILL.md's maintenance block routes here — precisely so these checks run in every session, whether or not the skill auto-triggered. Everything here is best-effort and must never block, delay, or interrupt the work: if any step fails (no network, no fetch mechanism, API error), skip silently, continue with the running version, and do not retry in this session.

## Version reporting

If the user asks which version of Keel they have or are using (e.g. "what version is this skill", "which Keel version do I have"), state it plainly from the frontmatter — "You're using Keel vX.Y.Z.", with the actual `metadata.version` value. The frontmatter is the source of truth; the heading line in `SKILL.md`, `CHANGELOG.md`, and the `MANIFEST.md` header stay in sync with it whenever the skill is updated (see the version change policy below).

## Update check (start of every session)

Keel is distributed from `https://github.com/joseconti/keel-skill` (releases: `https://github.com/joseconti/keel-skill/releases`). Once per session, check whether a newer release exists.

**Throttle — at most one remote check per 24 hours per project.** The remote lookup (step 1) is the slow part, so it is rate-limited through a tiny machine-local stamp at the project root: `.keel-update-check`, one line — the UTC timestamp of the last attempt and its outcome (e.g. `<UTC timestamp> — checked; running vX.Y.Z; latest vX.Y.Z`, with real values). Before step 1, read it: less than 24 hours old → skip the remote lookup silently. Missing, unparsable, or 24 hours old or more → run it, then REWRITE the stamp with the current UTC timestamp and outcome — after EVERY attempt, success or failure, so a flaky network cannot re-impose the wait on every chat. When an attempt fails and the previous stamp already recorded a failure, carry a consecutive-failure count in the outcome (e.g. `— check failed (3rd consecutive)`); at the fifth consecutive failure, tell the user once, briefly, that the update check has not succeeded in days and how to check the releases page themselves — then continue normally. The throttle covers ONLY the remote lookup: step 2's copy-vs-copy comparison (installed vs embedded — local, no network) still runs every session, and steps 2–3 run in full whenever the remote lookup ran. Never throttled either: the full SKILL.md read, the stamp-only lock-freshness check, and the `Keel baseline:` comparison — all local and free. An explicit user request to check for a new version always bypasses the throttle. The stamp is machine-local state, NEVER committed — it joins the unconditional `.gitignore` entries (`CLAUDE.local.md`, `.claude/settings.local.json`); if it is missing from `.gitignore`, add it. Outside a project (no repo yet), check without the throttle.

1. **Detect the latest version.** Preferred method (works in any environment with git, no API and no auth): `git ls-remote --tags https://github.com/joseconti/keel-skill.git` → take the highest semver tag. Strip the leading `v` and compare segment by segment as numbers (`1.10.0` > `1.9.0`) — never as strings; ignore tags that are not `vX.Y.Z`. Fallbacks, in order: GET `https://api.github.com/repos/joseconti/keel-skill/releases/latest` (field `tag_name`) with a web-fetch tool, or fetch the releases page. If the environment provides no mechanism at all, skip.
2. **Compare against EVERY copy in play, not only the running one:** the environment's install AND, when the session is working inside a project that embeds the skill, the project's embedded trees — `.claude/skills/keel/` and `.agents/skills/keel/` (each copy's frontmatter `metadata.version` — the source of truth). A copy can be behind even when the running one is current — in Cowork it is common that the app install is up to date while the opened project's embedded copy is not; that embedded copy must still be updated. All copies at the latest version → say nothing and continue.
3. **Newer release found → update every copy the environment can durably write; inform about the rest.** The copies in play: the environment's own install (a user-level skills directory such as `~/.claude/skills/keel/` or `~/.agents/skills/keel/`, or app-managed skill storage) and the project's embedded trees (`.claude/skills/keel/` + `.agents/skills/keel/` — always updated together, never allowed to diverge).
   - **For each copy that is writable and persists across sessions** — the user-level install, and ALWAYS the project's embedded trees when they exist (the normal case when a coding assistant is working inside a Keel project's repo: the same duty that put the embedded copy there also keeps it current): announce it in one line (vCURRENT → vNEW), download the release once — `git clone --depth 1 --branch vX.Y.Z https://github.com/joseconti/keel-skill.git` or the tag archive `https://github.com/joseconti/keel-skill/archive/refs/tags/vX.Y.Z.tar.gz`; if an already-current local copy exists (e.g. the app install is at the latest version and only the project's embedded copy is behind), copy from it instead of downloading, per the version-sync rule in `references/project-state.md` — and replace that copy's ENTIRE tree with the new `keel/` directory following the verified full-copy protocol in `references/project-state.md` ("Portability"): whole tree, verify file-for-file against the source, retry once; if it still fails, abort that copy's update (never the session), leave it intact, and treat it under the inform path below. After a verified replacement: summarize the improvements to the user from the new `CHANGELOG.md` (every entry after the previously running version), re-read the new `SKILL.md` and the current phase's reference from the new copy (the copies in context belong to the old version), and continue under the new version. When the session is working inside a Keel project, then run the **post-update reconciliation** (`references/project-state.md`, "Post-update reconciliation") so the project itself catches up with what the new version introduces — new required files or directories, new project-card lines, lock-block changes, never-asked questions — tracked by the project card's `Keel baseline:` line. The reconciliation's first input is the new `MANIFEST.md`: its Table 1 is the ABSOLUTE parity check of everything the project must contain at its phase, its Table 2 names the exact skill files to re-read — every row newer than the project's baseline — and its Table 3 lists the concrete per-version actions to apply. **The reconciliation is a sweep, not a summary:** every applicable row of Table 1 and every action of Table 3 newer than the baseline is walked one by one and lands in `docs/keel-conformance.md` with a state (`present` / `missing` / `declined` with its D-entry / `n/a` with its condition), every `missing` row reaches the user's batched plan without curation, and the full table is reported back. Applying an update partially — and not mentioning the rest — is the specific failure this mechanism exists to make impossible (SKILL.md "Applying Keel completely").
   - **For a copy that cannot be updated durably** — app-managed or ephemeral skill storage (common in the Claude app / Cowork) or no write access: tell the user once, briefly, in the conversation language: a newer Keel exists (vCURRENT → vNEW), what it improves (the new `CHANGELOG.md` entries after the running version — e.g. from `https://raw.githubusercontent.com/joseconti/keel-skill/main/keel/CHANGELOG.md`; if unreachable, point to the release notes on the releases page), and how to update it themselves — the app-installed skill is the user's to update (repository `INSTALL.md`, section "Updating"). If the project's embedded copy WAS updated and only the app/environment install could not be, say exactly that — the project is already current; updating the installed skill in the app is what remains. Then continue normally and do not repeat the notice this session.

**Lock freshness (same moment, every session inside a Keel project).** After the update check, verify the project's Keel lock block — in `CLAUDE.md` AND `AGENTS.md`, both — is current by its stamp alone — a one-line look, never a content comparison: the `KEEL:BEGIN` delimiter carries the version of the Keel that last wrote the block (`KEEL:BEGIN — vX.Y.Z do not remove: …`). Stamp equal to the running version → current, done. Stamp different or missing (blocks from before the stamp mechanism carry none; match delimiters by the `KEEL:BEGIN` prefix, never by exact text) → refresh: rewrite the block between the delimiters from the canonical copy in `references/project-state.md` ("Portability" §1), restamped with the running version, with the user's OK — in both lock files, and in the `GEMINI.md` mirror when the project keeps one; a project still carrying a single-file lock gets the missing `AGENTS.md` created in the same refresh. Never touch anything outside the delimiters. This is what keeps the always-loaded `CLAUDE.md` rules from drifting behind the skill.

Overwriting the skill is safe: Keel is stateless — project artifacts live in each project's `docs/`, never in the skill folder (see the repository's `INSTALL.md`). Installing an official newer release is an installation, not an authoring edit: it does not fall under the version change policy below, which governs hand-editing version strings in this copy.

## Permission mode (start of every session, before any work)

Keel works in long chains of tool calls, and Claude Code's default permission mode is `manual`. In `manual` mode a command is matched **statically** against the `allow` rules, so anything composite — a shell variable, a `&&`, a `;`, a pipe — fails to match even when every command inside it is allowed, and opens a permission dialog. Keel's phases are made of exactly those commands. The result is not slower work, it is stopped work: the unattended stretch this skill assumes never happens, and the user is dragged back into approving links of a chain they already approved as a whole. So the mode is checked and resolved BEFORE any project work, in the same breath as the update check.

**Check first.** Read the session's active mode (the status line / mode indicator, `--permission-mode` if it was passed, and `.claude/settings.local.json` → `permissions.defaultMode` when the file exists). Anything other than `manual` → say nothing and continue. `manual`, or undetermined → resolve it by one of the two routes below, then continue.

### Preferred route — `.claude/settings.local.json` (persistent)

Create or update `.claude/settings.local.json` at the repository root **when question 1 of the setup batch was answered yes** (SKILL.md, "Session start setup"). The mode is the user's call, asked once and recorded on the project card's `Autonomy:` line; writing the FILE that implements it is not a second question — Keel writes it and announces it in one line. A later session on a fresh machine finds the decision recorded and the file absent (it is gitignored, so a new checkout never carries one): it writes the file, says so, and does not re-open a question that is already answered. Answer no, and no file is written at all: the mode stays as it is, Keel asks before each action, and it pushes nothing that was not explicitly requested.

That this file may be written where a committed allow-list may not is not an inconsistency with "committed permissions are ALWAYS confirmed" (`references/assistant-config.md`) — it is the same rule read correctly: `.claude/settings.json` is committed and binds every person who opens the repo, so it needs the user's explicit OK; `.claude/settings.local.json` is machine-local, gitignored and binds nobody but this checkout, so writing it changes nothing outside the user's own machine. It is also the single exception to "Keel never creates a personal config file"; every other personal file stays the user's own.

The contents:

```json
{
  "permissions": {
    "defaultMode": "auto",
    "allow": [
      "Bash(gh issue view:*)",
      "Bash(gh issue list:*)",
      "Bash(gh issue comment:*)",
      "Bash(gh issue create:*)",
      "Bash(gh issue edit:*)",
      "Bash(gh issue close:*)",
      "Bash(gh issue reopen:*)",
      "Bash(gh pr view:*)",
      "Bash(gh pr list:*)",
      "Bash(gh pr diff:*)",
      "Bash(gh pr checks:*)",
      "Bash(gh pr create:*)",
      "Bash(gh pr comment:*)",
      "Bash(gh pr edit:*)",
      "Bash(gh pr merge:*)",
      "Bash(gh label:*)"
    ],
    "deny": [
      "Bash(rm -rf /*)",
      "Bash(sudo *)",
      "Bash(curl * | sh)"
    ]
  },
  "env": {
    "PATH": "/Users/<user>/.local/bin:/opt/local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
  }
}
```

**Merge, never overwrite.** If the file already exists, read it and add only what is missing: set `permissions.defaultMode` to `auto`, union the `allow`, `deny` and `ask` entries with those already present, and set `env.PATH` only if it is absent. A rule the user put there is never removed or reordered, and a `deny` the user added always survives. If the existing file is unparsable, do not rewrite it — say so and use the per-session route instead.

Three contents notes, told to the user when the file is written so none of them surprises them later:

- **The `allow` block exists because `auto` mode alone is not enough for the forge.** Setting the mode to `auto` removes the *static* matching problem described above, but `auto` still routes each command through a classifier, and that classifier treats writing to a place other people read — a comment on a client's issue, a clarifying question to the reporter, a label — as an outward-facing action to confirm. Which is the correct default for an assistant with no standing authorisation, and exactly wrong for Keel's issue cycle: answering issues and asking the reporter questions IS the work of that cycle, so a dialog on each one stops precisely the automatism the mode was set to obtain. The rules above are the standing authorisation, and they are deliberately scoped to the **conversational** surface of the forge — reading, commenting, asking, labelling, opening and closing issues, and merging a PR. What is NOT in the list is as deliberate: no `gh repo delete`, no `gh release create`, no `gh api` blanket. Publishing a release is a Phase 7 decision that the user approves by name (`references/phase-7-release.md`), and it stays a dialog.
- **There is deliberately no `ask` entry for `git push`.** An earlier draft put one there and it was removed: it contradicts the git-flow rule head-on (SKILL.md, "Git flow"), where pushing and merging into `develop` are the assistant's own duty in automatic mode. A dialog on every push recreates the queue of unpushed commits that rule exists to abolish, and it buys no safety — the safety lives at the `develop` → `main` merge, which Keel never performs on its own initiative. Adding `ask` entries of their own is of course the user's prerogative, and a merge preserves them.

  **That safety is a rule, not a mechanism, and the `allow` block above is what makes the difference matter.** `Bash(gh pr merge:*)` is a prefix rule: it cannot tell a PR based on `develop` from one based on `main`, because the two commands are the same text. Neither can an `ask`/`deny` entry, for the same reason — the target branch is not in the command line. So a user who wants the `develop` → `main` boundary *enforced* rather than merely observed needs something that resolves the real target: a `PreToolUse` hook on `Bash` that reads the current branch (`git rev-parse --abbrev-ref HEAD`, following any `checkout`/`switch` earlier in the same command line) and the PR's base (`gh pr view --json baseRefName`), denies when either is a protected branch, and fails closed when it cannot tell. That is the user's own machine configuration, not something Keel writes — but when the question comes up, this is the answer, and "the assistant simply does not do it" is not one.
- **`env.PATH` is written EXPANDED and ABSOLUTE — never `${PATH}`, never `$HOME`, never any other variable (measured, and it breaks the machine).** This field is consumed literally: a value ending in `:${PATH}` does not append the existing PATH, it appends the seven characters `${PATH}`, and `$HOME/...` becomes a directory that does not exist. The consequence is not cosmetic — the base system directories are what get lost, so `/usr/bin` and `/bin` disappear and `git`, `ls`, `cut`, `grep` and everything else stop resolving, in every session and every project, until someone edits the file. The failure is also confusing rather than obvious: the assistant sees `command not found: git` on a machine where git plainly works, and the doctor's corroboration rule (`references/test-automation.md`) is what keeps it from concluding `MISSING` and offering to install it.

  **And its worst symptom does not look like a PATH problem at all: a re-authentication loop.** On macOS the keychain is reached through `/usr/bin/security`, which git and `gh` credential helpers invoke by name. Drop `/usr/bin` from `PATH` and that lookup fails, so the helper cannot read a credential that is sitting right there — and instead of an error naming a missing binary, the tool asks to authenticate, succeeds, fails to store, and asks again. The user sees an identity or login loop and starts debugging tokens, scopes, two-factor and the forge's own settings, none of which is broken. **Whenever authentication loops for no reason, check `PATH` for `/usr/bin` before touching a single credential** — and never rotate a token on that evidence, because rotating one fixes nothing here and costs whatever else was using it.

  So: **enumerate every directory literally, and always include the system ones** — `/usr/bin`, `/bin`, `/usr/sbin`, `/sbin` — even when the interesting entries are the ones in front. The value above is the verified macOS/MacPorts+Homebrew case. On a machine whose layout differs, or where a version manager's directory must lead, resolve the real path first (`echo $PATH` in the user's login shell) and write the RESULT, never the expression that produced it. Before writing the key at all, check whether an existing `env.PATH` — in this file or in the user-level `~/.claude/settings.json` — already carries an unexpanded variable, and fix it in the same breath: a broken PATH inherited from user-level config poisons every project on the machine, not just this one.

  **Always include the user's own per-user installer directory, expanded to its literal absolute value — never the system-package-manager list alone.** Claude Code's native (non-npm) installer places its binary at `~/.local/share/claude/versions/<version>`, symlinked from `~/.local/bin/claude` — a per-user location the MacPorts/Homebrew/system list above does not, and structurally cannot, contain, because it targets package managers rather than per-user installers. Missing it does not merely leave `claude` unresolved for arbitrary commands: `scripts/keel-continue`'s own live re-check (its contract, point 5a) runs `command -v claude` against exactly this `env.PATH`, so on a machine where Claude Code was installed natively, that check reports "not on PATH" while Claude Code is actively running — the single most misleading shape this failure can take. Resolve the real value (`echo $HOME` in the user's login shell, e.g. `/Users/jconti`) and prepend `<that>/.local/bin` the same way every other entry here is written literally; never write the string `$HOME` itself into the file (that is exactly the unexpanded-variable failure two paragraphs up). More generally, before reporting any `command -v <bin>` failure as "not installed," consider whether a per-user installer path (`~/.local/bin`, `~/.local/share/*/bin`) is missing from the list rather than the binary being genuinely absent.

### Alternative route — per session

For a user who prefers no file written: start the session with `claude --permission-mode auto`, or press Shift+Tab until the mode indicator reads `auto`. It resolves the same problem for the current session only, and has to be repeated in the next one — say that plainly rather than letting them discover it.

### `.gitignore`

Verify `.claude/settings.local.json` is listed; if it is not, add it. It is already one of the unconditional entries (`references/assistant-config.md`, "Personal files and `.gitignore`"), so this is a check, not a new rule — but the file is being written now, which is exactly the moment a missing entry becomes a real risk.

### Hygiene — no `export PATH=... &&` prefix, ever

With `env.PATH` set in that file, every command Keel runs already resolves the user's tooling. Prefixing a command with `export PATH=... && ...` therefore buys nothing and costs everything: the prefix ALONE makes the command composite, which is precisely what fails the static match and opens a dialog — on every single call, including the ones that would otherwise have matched an `allow` rule cleanly. So Keel never writes that prefix, in a tool call, in a generated `scripts/` file, in a phase reference, or in a command handed to the user. When a tool genuinely does not resolve, the answer is the absolute path of that binary (recorded in the environment requirements table), never a PATH prefix on the command. A milder version of the same mistake — `cd <dir> && <command>` where the tool already takes a working directory — has the same fix: pass the directory, keep the command simple.

### The doctor's check

`scripts/keel-doctor` reports the permission mode as an **advisory** row — never blocking (see `references/test-automation.md`, "`scripts/keel-doctor`").

## Version change policy (UNBREAKABLE RULE — never bump under any circumstance without explicit user instruction)

This rule is **unbreakable**. There are no exceptions, no edge cases, no judgment calls. It overrides every other instinct or inference the assistant might have about how version numbers "should" evolve based on the scale of the edit.

The Keel version — in `metadata.version` in the frontmatter, in the `SKILL.md` heading line, in `CHANGELOG.md`, and in the `MANIFEST.md` header — must NEVER be changed unless the user has **explicitly instructed it in the current conversation** (e.g. "bump to 1.1.0", "release 1.0.1", "this is version 2", "tag a new minor release"). An explicit "yes" to a direct question about a specific version also counts as explicit instruction. Nothing else does.

What does NOT count as authorisation to change the version:

- The scale of the edits in this conversation (large rewrites, full re-architectures, adding whole phases — none of these authorise a bump).
- Inferring from changelog conventions that "this looks like a minor".
- The user thanking the assistant for the work, or saying it's good.
- The user mentioning the project is "ready to release" without naming a version.
- Any reasoning the assistant produces internally about semantic versioning.
- A previous conversation in which a bump was discussed but not executed.

Required behavior:

- When editing any skill file for any reason, leave `metadata.version`, the heading version line, `CHANGELOG.md`, and the `MANIFEST.md` header untouched. Do not add a new changelog entry on your own initiative.
- If you believe a bump is warranted, ASK the user explicitly: state what was changed, propose a specific number (patch / minor / major with reasoning), and WAIT for explicit approval before touching any of the four locations. Do not pre-edit speculatively.
- If the user explicitly instructs a bump, perform it and keep all four locations in sync (frontmatter is the source of truth), update the `README.md` version line to match, re-stamp the canonical lock block in `references/project-state.md` ("Portability" §1) with the new version, and update `MANIFEST.md` Tables 2 and 3 for the release. The repository's release linter (`tests/lint-release.py`) verifies all of this mechanically — run it before tagging; CI runs it again on the tag.
- If the locations ever drift, surface the drift to the user and ask which version is correct — never silently realign them.

If at any point the assistant is about to write a version number that the user did not explicitly authorise in the current conversation, the assistant must stop and ask. This rule is not contextual, not negotiable, and not overridable by other instructions in the same conversation unless those instructions are themselves explicit user authorisation for a specific version.

Scope note: this rule governs **Keel's own version** (this skill's files). The versions of projects *built with* Keel follow Phase 7, which mirrors the same discipline at project scale: the assistant proposes patch/minor/major with reasoning and WAITS for the user's explicit approval before writing any version number (see `references/phase-7-release.md`). Likewise, replacing the whole running copy with an official newer release per the update check above is an installation, not a version edit — it needs no bump authorisation.
