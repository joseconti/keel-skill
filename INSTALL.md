# Installing Keel

This guide explains how to install the Keel skill in your assistant of choice. Keel is a skill in the open [Agent Skills](https://agentskills.io) format (the standard originated by [Claude skills](https://docs.claude.com)): a directory containing a `SKILL.md` file plus its supporting references. Once placed in a location where your client looks for skills, it is invoked automatically when the user's request matches its trigger description. It works in Claude (Claude Code, Cowork, the Claude apps) and in any assistant that supports the standard — OpenAI Codex, Cursor, Gemini CLI, GitHub Copilot, Windsurf, and others.

The skill itself lives inside the `keel/` directory of this repository. That folder is what you install — not the whole repository.

## What you install

The unit of installation is the **`keel/`** directory:

```
keel/
├── SKILL.md
├── MANIFEST.md
├── CHANGELOG.md
├── LICENSE
├── NOTICE
└── references/
    ├── keel-maintenance.md
    ├── phase-1-discovery.md
    ├── phase-2-functional-spec.md
    ├── ...
    └── security/
        ├── wordpress.md
        ├── web-app.md
        ├── mcp-server.md
        ├── library-component.md
        └── website.md
```

`MANIFEST.md` is part of the skill — a copy without it breaks the post-update reconciliation. Copy the `keel/` directory whole, never file by file.

Top-level files in this repository (`README.md`, `INSTALL.md`, `.gitignore`, `.gitattributes`) are repository metadata. They are **not** part of the skill and do not need to be copied to the install location.

## Getting the skill

Clone the repository:

```bash
git clone https://github.com/joseconti/keel-skill.git
cd keel-skill
```

Or download a release archive from the GitHub releases page and extract it. The release archives already exclude repository-only files via `.gitattributes` `export-ignore`. Note the layout: the tag archive unpacks to a `keel-skill-vX.Y.Z/` root directory that CONTAINS the `keel/` folder — copy that inner `keel/` folder to your skills directory (never the outer directory, or you end up with `keel/keel/SKILL.md`).

Keel is also listed on the author's skills marketplace — [skills.joseconti.com/plugin/keel.html](https://skills.joseconti.com/plugin/keel.html) — which distributes it as part of a Claude Code / Cowork plugin; follow the marketplace's own instructions to add it and install from there.

## Install location

Where to copy `keel/` depends on which assistant you use.

### Option A — Personal skill (single user)

Most clients support a user-level skills directory. Copy the `keel/` folder into the one matching your assistant:

| Assistant | User-level skills directory |
|---|---|
| Claude (Claude Code, Cowork) | `~/.claude/skills/keel` |
| OpenAI Codex | `~/.agents/skills/keel` |
| Cursor | `~/.cursor/skills/keel` (or `~/.agents/skills/keel`) |
| Gemini CLI | `~/.gemini/skills/keel` (or `~/.agents/skills/keel`) |
| GitHub Copilot / VS Code | `~/.copilot/skills/keel` (or `~/.claude/skills/keel`) |
| Windsurf | `~/.codeium/windsurf/skills/keel` (or `~/.agents/skills/keel`) |
| Zed, Warp, Amp, opencode and other standard-compliant tools | `~/.agents/skills/keel` |

If you use several of these tools, `~/.agents/skills/keel` is the shared convention most of them read — one copy serves them all (Claude currently reads `~/.claude/skills/`, so keep that copy too if you use Claude).

**macOS / Linux:**

```bash
# Adjust the destination path to your client's user skills directory.
cp -R keel ~/.claude/skills/keel
```

**Windows (PowerShell):**

```powershell
# Adjust the destination path to your client's user skills directory.
Copy-Item -Recurse keel "$env:USERPROFILE\.claude\skills\keel"
```

If you are not sure where your client looks for user skills, check its documentation under "skills", "custom skills", or "agent skills". The destination must contain `keel/SKILL.md` directly (not `keel/keel/SKILL.md`).

### Option B — Bundled inside a Claude Code plugin

If you maintain a Claude Code or Cowork plugin and want to ship Keel as one of its skills, copy `keel/` into the plugin's `skills/` directory:

```
your-plugin/
├── plugin.json
└── skills/
    └── keel/
        ├── SKILL.md
        └── references/
            └── ...
```

After adding it, bump the plugin version and reinstall the plugin in your Claude client.

### Option C — Shared with a team

For a team installation, host the skill in a shared location your team's environments already read from (an internal plugin marketplace, a shared skills folder synced via your existing tooling, etc.). The skill is plain files; any mechanism that delivers a directory will work, as long as `SKILL.md` ends up at the root of the installed folder. Keel projects can also embed the skill in the repo itself (`.claude/skills/keel/` + `.agents/skills/keel/`) — every collaborator's assistant then loads it with no per-machine install at all; Keel offers this at project creation.

### Option D — Claude apps (claude.ai / desktop) and the API

The Claude apps install skills as an uploaded zip whose root contains `SKILL.md`. Create it from the repository:

```bash
cd keel && zip -r ../keel.zip . && cd ..
```

Then upload `keel.zip` in the app's skills section (under Settings — the exact location and availability depend on your plan; see the current guidance at [docs.claude.com](https://docs.claude.com) and [support.claude.com](https://support.claude.com)). The same zip works for the Claude API's skills endpoint — consult the API documentation for the upload call.

Note that app-managed skill storage is usually not writable by the assistant: Keel's session-start update check will tell you when a newer version exists and what it brings, but replacing the uploaded skill is yours to do (re-upload the new zip).

## Verifying the installation

Once installed:

1. Restart or reload your client so it rescans the skills directory.
2. Start a new conversation and ask: *"What version of Keel do I have?"*
3. If installed correctly, the assistant responds with the version in `keel/SKILL.md` frontmatter, e.g. *"You're using Keel vX.Y.Z."*
4. Try a real trigger phrase such as *"I have an idea for a new WordPress plugin, let's plan it"* — Keel should announce Phase 1 (Discovery) and begin asking discovery questions.

If the skill does not trigger:

- Confirm the directory is named `keel` and contains `SKILL.md` directly.
- Confirm your client's skills directory is correctly configured (see the per-assistant table above).
- Check your client's logs for skill loading errors (often a malformed frontmatter or missing file produces a load error).

## Updating

To update Keel to a newer version:

1. Pull the latest changes from this repository, or download the new release archive.
2. Replace the installed `keel/` directory with the new one. Because Keel is stateless (it produces artifacts into your project's `docs/`, not into the skill folder), it is safe to overwrite.
3. Restart your client.
4. Confirm by asking *"What version of Keel do I have?"* — the new version number should match `keel/SKILL.md` frontmatter and `keel/CHANGELOG.md`.

Project artifacts produced by previous Keel runs (such as `docs/PROGRESS.md` and `docs/lessons-learned.md` inside your project repositories) are not affected by updating the skill.

## Uninstalling

Delete the installed `keel/` directory from your skills location and restart the client. Nothing else needs to be removed — Keel does not write outside the user's project directories.

## Troubleshooting

**The skill triggers when I don't want it to.**
Keel's description is intentionally broad because it covers any new project. If you want to invoke it only on demand, you can rename the directory (for example to `keel-manual`) and invoke it explicitly by name.

**The skill loads but references are not found.**
Verify the `references/` subdirectory is present alongside `SKILL.md` after the install. If the copy was partial, restore the full directory.

**The version reported is wrong.**
The frontmatter in `keel/SKILL.md` (`metadata.version`) is the source of truth. Open it and confirm the installed file matches the version you intended.

## License

Keel is licensed under the [GNU General Public License v3.0 or later](keel/LICENSE). Installation does not change those terms.
