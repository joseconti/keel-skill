# Out-of-band notification — telling the developer that Keel is waiting

Load this at the session-start setup batch (SKILL.md, "Session start setup"), at every point where Keel stops and waits for the person, and at the sprint close when the issue duty produces something the developer has to act on.

## Why this exists

Keel stops on purpose. "When to stop and ask" makes stopping a successful outcome, and the whole test-automation protocol is built on the idea that the person is asked only for what genuinely needs them. But all of that assumes the person finds out. **A session blocked waiting for an answer and a session working look identical from outside: nothing.** The chat sits there, the developer is doing something else, and a stop that was supposed to cost thirty seconds costs the afternoon.

So the rule is: **when Keel stops and the person is not visibly present, Keel tells them out of band.** The notification is not a nicety attached to the workflow, it is what makes an unattended stop recoverable. And it is the counterpart of the permission-mode step: that one lets Keel run without interruption, this one makes sure the interruptions that *are* real reach a human.

## What counts as a channel — delivery, not composition

**A channel is a channel only if it DELIVERS.** This is the whole trap, and it has a concrete instance: the Gmail connector commonly available to a session exposes `create_draft`, `update_draft` and `list_drafts` — and **no send operation**. A draft sitting in the user's own mailbox alerts nobody: no push, no badge, no arrival. Recording "notified by email" after creating a draft is a false claim of exactly the kind SKILL.md's "Declared is not delivered" forbids, and it fails in the precise situation the mechanism exists for — nobody watching.

So every candidate is classified before it is used:

| Tier | What it is | Counts as notification? |
|---|---|---|
| **Delivering** | The environment's own notification tool (the default — see below); a messaging MCP that posts (Slack, Telegram, Discord); a mail MCP or local mailer with a real send operation (`msmtp`, `sendmail`, an SMTP script the project owns) | **Yes** |
| **Compose-only** | Gmail-style connectors offering drafts but no send | **No** — usable as a secondary trace, never as the notification |
| **In-chat only** | Printing the message in the conversation | **No** — it is the fallback, and it is announced as such |

## The probe — capability is measured, never assumed

Keel does not read a tool list and conclude it can notify. A connector can be listed and unauthorized; an MCP server can be present in one session and absent in the next; a headless or scheduled run frequently has neither. This is the same discipline the environment preflight applies to every other capability (`references/test-automation.md`): **a listed tool is a claim, a responding tool is a fact.**

Run the probe once per session, at the setup batch, in this order, and stop at the first tier-1 channel that answers:

1. **The recorded channel from the project card** (`Notify:`), if the project has one. Probe *that* first — the user already chose it.
2. **The environment's own notification tool**, where the session exposes one. **This is the default and it is preferred over building anything** — it needs no address, no credential, no server and no setup, which makes it the only channel that is already true on a fresh machine. Claude Code exposes one; other harnesses may. Two properties of it govern how Keel uses it, and both are easy to misread:

   - **It reaches the desktop always, and the phone only when the harness's remote control is connected.** So it covers "walked away from the desk" natively and covers "out of the house" only if that link is up. When the user's real absence is the away-from-the-building kind, say this plainly and offer a second channel rather than letting them assume reach the mechanism does not have.
   - **It deliberately does not fire while the user is actively at the terminal, and reports "not sent".** That is the anti-noise policy of this reference implemented one layer down, not a failure — so it is NOT reported as a failed notification and NOT retried through another channel. The message was already in front of them. Treat "not sent because redundant" as success; treat "nowhere to go" as the absence of a channel.
3. **A messaging or mail MCP with a real send operation** — the right escalation when the user is genuinely away from their machine. Verify the operation exists by READING ITS SCHEMA; never infer it from the server's name. A mail connector in particular may expose reading, searching, labelling and draft creation and still have no send: that is the measured case, not a hypothetical.
4. **A compose-only connector** — recorded as a secondary, never as the channel.
5. **Nothing.** Then the notification is printed in the conversation, and the setup line says plainly that no out-of-band channel is available in this session, so the user knows silence means silence.

Record the verdict in `docs/01-discovery.md` under `## Environment & test drivers`, beside the other capability answers, and on the project card's `Notify:` line. A verdict is a claim about **this session's environment**, not about the world: it is re-probed each session, and a channel that worked yesterday and does not answer today is reported, not assumed.

## The setup questions (asked once, in the startup batch)

1. **Do you want to be notified out of band when Keel is waiting on you?** Default **yes**. If no, record it and never ask again — the notifications simply do not happen and the in-chat message stands alone.
2. **Through which channel?** Offer only what the probe actually found, naming what each one reaches (a phone, a desktop, a mailbox). Never offer a channel that did not answer.
3. **To which address / recipient?** Ask explicitly — an email address, a Slack handle, a chat id. **Keel never guesses it** from the git config, the commit history or a `mailto:` in the repo: those addresses belong to whoever committed, which is not necessarily who should be interrupted, and a notification sent to the wrong person is both a privacy leak and a missed alert.
4. **Anything else you want notified about**, beyond the standing triggers below.

Answers go on the project card (`Notify:`) and into `docs/decisions.md` as a D-entry. The address is a plain contact detail, not a secret, so it lives on the card like the rest — but see "What never travels" below for what may not accompany it.

## When Keel notifies — and when it must not

Notify on:

- **A blocking stop.** Any "When to stop and ask" row that halts the work: a spec silence, two artifacts contradicting each other, a decision that needs the user, a required input that does not exist, a test point that failed three times the same way.
- **A delegation the person must perform.** Any of the eight tags that actually blocks progress — `CREDENTIAL`, `HARDWARE`, `ASSISTIVE-TECH`, `EXTERNAL-APPROVAL`, `PRODUCTION-RISK` — with the exact steps.
- **A deploy or upload the developer must make** so that something can be tested — the second beat of the issue lifecycle below, and the most common real trigger of all.
- **A sprint close or a session close-out that ends blocked** (`Handover: blocked`), so a stalled hand-off is not discovered hours later.
- **A chain that was configured to fire and did not, or that fired DEGRADED.** On a card that says `Chaining: prefill`/`start`, whenever `scripts/keel-continue` prints instead of launching — for any of its four reasons — the printed reason goes out through the channel, with the failing rows of `scripts/keel-chain-check` beside it. This is the trigger whose absence is measured in hours rather than minutes: the launcher refused correctly, printed correctly, and printed into a window nobody was watching, and the work sat still for nine hours before anyone knew. **A chain that stops is a stop, and a stop nobody hears is a stall** (SKILL.md) — the fact that the mechanism behaved exactly as designed is what makes it so easy to miss, not a reason to stay quiet. **But notifying is the smaller half of the fix and must never be mistaken for it:** the person is often asleep, and an unread message at 00:28 turns nine idle hours into nine idle hours plus an email. That is why the DEGRADE/TERMINAL table exists — the notification explains what happened, it does not rescue it. A degraded fire notifies too, at lower urgency: the work continued, and the person should still learn which artifact was in a bad state so it gets repaired in daylight.
- **Anything the user added at setup.**

Do **not** notify on:

- **A question asked inside an active conversation.** If the user wrote a message minutes ago, they are there; an email is noise. The trigger is a stop with no one present, judged by how long the session has been waiting and whether the person has spoken recently — err toward the chat when it is genuinely ambiguous.
- **Routine progress.** A finished slice, a passing test, a clean sprint. A channel that carries good news stops being read, and then it stops working for bad news too.
- **Anything already sent.** One notification per event; a reminder only if the user asked for one at setup.

**Volume is a design constraint, not an afterthought.** The failure mode of a notification system is never "too few" — it is a person who has learned to ignore it.

## What the message contains — and what never travels

The notification leaves the machine. The confidential-data rule (SKILL.md, "Confidential data never reaches Git") governs it exactly as it governs a commit, because a channel is a wider exposure than a repository, not a narrower one.

Contains: the project name, the repository, the current position (phase/sprint/slice), **what is blocking in one sentence**, what the person has to do, and where to continue (the absolute path of `docs/continuation-prompt.md`, or the issue URL).

Never contains: credentials, tokens, keys, `.env` contents, customer or personal data, database rows, or blocks of source code. If explaining the blocker seems to require any of those, it does not — name the file and the line and let the person open it.

Keep it short. This is a pointer to work, not a report; the report is in the repo.

## Failure is reported, never silently absorbed

**First, do not manufacture a failure out of a suppression.** A notification the environment withheld because the user was already looking at the screen delivered its content by definition; it is recorded as sent-or-redundant and nothing escalates. What follows is about a channel that genuinely could not deliver.

If the send fails, or no channel was available, **say so in the conversation** in the same breath as the blocking message: *"I could not notify you out of band — <reason>. This message is the only signal."* An attempted-but-failed notification recorded as sent is worse than no mechanism at all: the developer believes they would have been told.

## The issue-reply lifecycle this serves

The forge-issue duty (`references/project-state.md`, "`docs/issues.md`", and the Phase 5 sprint close) depends on this channel for its middle beat, because that beat is precisely a stop the reporter cannot see and the developer must act on. The three beats, in order:

1. **The fix has landed in the code.** Keel comments on the issue: the fix is implemented, and the reporter will be told when there is something they can actually test. **It does not close the issue** — the code changing is not the same event as the user being able to try it.
2. **Keel notifies the developer** through this channel: a build/upload/deploy is needed before the reporter can test, naming the issue, the version and what has to go up. Then it waits — this is a real stop, recorded in `docs/PROGRESS.md`, and the issue's status is `awaiting deploy`.
3. **The developer confirms it is up.** Keel comments again on the issue: it can now be tested, on which version, with what to look for. Status becomes `awaiting reporter`.

Then the reporter answers, and only then does anything close — see the closing rule in `references/project-state.md`. Keel never closes an issue on its own reading of the code.
