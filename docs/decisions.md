# DECISIONS — Keel (the skill itself)

> Append-only. One entry per decision. Never re-litigated by the assistant on its own initiative;
> an explicit later instruction from the user supersedes an entry and is recorded as a new one.

## D-001 — This repository keeps living state, and it is a maintenance project

- Date: 2026-07-30
- Context: The repository that authors Keel had no `docs/PROGRESS.md` and no `docs/decisions.md` — the two files Keel requires of every project it manages. Sessions working on the skill re-derived its position from git history and from whatever the user remembered.
- Decision: Create both files and run this repository in Keel's **maintenance** mode rather than as a greenfield project. Phases 1–4 are recorded `n/a`: the skill exists, is released and has an installed base, so a discovery phase would be fiction. Each version is a change set gated by `python3 tests/lint-release.py`.
- Alternatives considered: (a) a full adoption pass producing `docs/01/02/03` as-built — rejected: for a Markdown instruction set, `SKILL.md` and `MANIFEST.md` already ARE the spec and the parity list, and reconstructing them into as-built docs would create a second source of truth that immediately drifts. (b) Leaving the repo stateless — rejected: the skill that makes state mandatory cannot be the one project without it.
- Consequence: The state files are maintained at the moment of change, like any Keel project. `Keel baseline:` always equals the version being authored, because this repo writes the version it runs.

## D-002 — `develop` integrates; `main` is the user's

- Date: 2026-07-30
- Context: Recorded here as the project-level instance of the git-flow rule introduced skill-side in v5.5.0 (SKILL.md, "Git flow").
- Decision: Work branches start from `develop`. The assistant merges work branches into `develop` and pushes, **without asking**. The assistant **never** merges `develop` into `main`, never tags, and never publishes a release on its own initiative — those are the user's acts, performed only on an explicit instruction in the conversation.
- Alternatives considered: committing straight to `main` — rejected: the skill has an installed base that pulls from tags, so `main` moving unreviewed would ship unreviewed instruction changes to real projects.
- Consequence: Control over what reaches users sits at the `develop` → `main` merge, not at the push. When `develop` holds work ready for release, PROGRESS.md says so under "Ready for `main`" and the assistant stops there.

## D-003 — Pushing is the assistant's job, not the user's

- Date: 2026-07-30
- Context: Work was accumulating as local commits waiting for a human to push them, which is a queue nobody owns: the user has to remember, and a session that ends leaves work invisible to every other checkout.
- Decision: The assistant pushes its own work. No commit is left local "for the human to review and push". Review happens at the `develop` → `main` merge (D-002), not by withholding a push.
- Consequence: `Autonomy:` on the project card records `push: unattended`. Consequently `Bash(git push *)` is NOT in the `ask` list of `.claude/settings.local.json` — an earlier draft of v5.5.0 put it there and it was removed as directly contradicting this decision.

## D-004 — The permission-mode file is written without asking

- Date: 2026-07-30
- Context: v5.5.0 was first drafted with the permission mode as a question in the session-start batch. The user then instructed that Keel write `.claude/settings.local.json` on its own initiative and merely announce it.
- Decision: Keel writes or merges that file itself, announces it in one line, and never asks first — it is machine-local, gitignored, and binds nobody but the checkout it sits in. Merging never removes or reorders a rule the user put there. The committed `.claude/settings.json` is unaffected and still requires explicit confirmation.
- Consequence: The startup batch drops from four questions to two real ones (forge-issue duty, notification channel); the permission mode became an action that is reported, not asked. This entry supersedes the earlier draft, per the rule that a later explicit instruction wins.

## D-005 — Out-of-band notification is protocol-first, and this machine has no channel

- Date: 2026-07-30
- Context: v5.5.0 adds `references/notifications.md` so a blocked session reaches the developer. The intended channel was email through the Gmail connector.
- Decision: Define the protocol around **delivery**, not around a specific vendor: a channel counts only if it actually delivers, the capability is probed every session, and a connector that can compose but not send is recorded as compose-only. The measured fact behind this: the available Gmail connector exposes draft creation, reading and labelling, and **no send operation** — so a draft would have been recorded as a notification while alerting nobody.
- Consequence: The protocol is vendor-neutral and probe-first. See D-007 for the channel actually adopted.

## D-006 — Keel's own version is never bumped without explicit instruction, and v5.5.0 was instructed

- Date: 2026-07-30
- Context: The skill's UNBREAKABLE version policy forbids touching `metadata.version`, the heading, `CHANGELOG.md` and the `MANIFEST.md` header without an explicit instruction in the current conversation.
- Decision: v5.4.1 → **v5.5.0** was authorised explicitly by the user ("Esto sería la 5.5"). All four locations plus `README.md` and the canonical lock stamp in `references/project-state.md` were updated together, and `MANIFEST.md` Tables 2 and 3 were updated for the release.
- Consequence: `python3 tests/lint-release.py` is the mechanical check that these stayed in sync; it passes. The tag and the GitHub release remain the user's act (D-002).

## D-007 — The native harness notification is the default channel

- Date: 2026-07-30
- Context: D-005 left this repository with no channel, on the assumption that email was the route. The harness's own notification tool turned out to be available, and it needs no address, no credential, no server and no setup.
- Decision: Adopt the environment's native notification as the default channel, here and as the first-preference tier in `references/notifications.md`. Build nothing until it proves insufficient.
- Alternatives considered: an SMTP sender via a Google app password (`msmtp` or a small script) — deferred, not rejected: it is the correct escalation for absences the native channel cannot reach. A self-hosted Gmail MCP with a send scope — rejected as more ceremony than the SMTP path for the same result.
- Consequence: Two properties are recorded because both are easy to misread. **Reach:** desktop always, phone only while Remote Control is connected — so it covers "walked away from the desk" and not "out of the building". **Suppression:** it deliberately does not fire while the user is at the terminal and reports "not sent"; that is the anti-noise policy one layer down, so it counts as delivered-or-redundant and is never escalated to another channel or reported as a failure. Untested so far: the only honest test is one fired while the user is genuinely away, which has not happened yet.
