# Test automation — the assistant drives every test it can drive

Load this at five moments: (a) Phase 1 §5a, for the environment preflight as soon as the project type and target platforms are fixed; (b) Phase 2 §4/§4d/§4e, when the technical plan picks the drivers, writes the environment requirements table and settles the test-first policy; (c) the Phase 5 scaffold, when `scripts/keel-doctor` is generated and the drivers are stood up; (d) every Phase 5 test point and sprint close, when the tests are actually driven; (e) the Phase 7 gate, for the clean-machine run.

It is the operating manual for one rule. `references/playground-recipes.md` says WHAT environment each project type gets; this file says WHO exercises it and how that is proven.

## The rule this file exists to enforce (UNBREAKABLE)

**The user is not the test runner.** Anything a machine can drive, the assistant drives — start the environment, open the screen, fill every field, click every control, wait for every state, read back what the interface actually says, capture the evidence. The user is asked to touch the product only for what is physically impossible for the assistant to do, and every one of those asks is recorded with its reason.

Three sentences govern everything below:

1. **Driving is not describing.** "Go to Settings, enter an invalid email, and tell me if the error appears" is not a test — it is the assistant outsourcing its own work. The test is a script that enters the invalid email and asserts the error, run by the assistant, with its output recorded.
2. **A delegation needs a reason from a closed list.** If the reason is not on the list in "The division of labour" below, it is not delegable — the assistant automates it instead.
3. **Unverifiable is not the same as unverified.** What genuinely cannot be driven is recorded as `⚠ unverified` with the reason and the exact steps for whoever will verify it. Never silently skipped, never quietly reported as passing.

Why this is a hard rule and not a preference: a human walking a flow is slow, is not reproducible, leaves no artifact, silently skips the boring cases (the empty state, the invalid input, the permission failure), and cannot be re-run on the next commit. A driven test does all five things every time for free. Every hour the user spends clicking through a form the assistant could have filled is an hour subtracted from the only work that actually needs them: deciding what to build.

## The division of labour (the contract)

### The assistant drives, always

| Work | Non-negotiable because |
|---|---|
| Starting, seeding, resetting and stopping the environment | It is a documented command; running it is the assistant's job by definition |
| Filling every form field — text, select, checkbox, radio, date, file upload, rich editors | This is the single most common thing wrongly handed to the user, and every driver in this file does it natively |
| Clicking, tapping, hovering, dragging, scrolling, keyboard navigation | Same |
| Asserting what the interface shows — success text, validation errors, empty states, permission denials | The assertion is the test; a human eyeball is not an assertion |
| Walking every branch of every flow, including failure and recovery paths | Humans test the happy path and skip the rest — that is where the bugs live |
| Reading back console errors, failed requests, 5xx responses, uncaught exceptions, platform logs | These are invisible to a human walking the UI, and they are where the real cause usually is |
| The automated accessibility pass on every screen and every state | Free once the driver exists (see "Accessibility is part of driving") |
| Static analysis and code sniffers | Pure command execution — never a review the user performs |
| Capturing evidence: command, output, screenshots, video, trace, result bundle | An unrecorded check did not happen |

### The user is asked, only for these reasons

Every delegation carries one of these tags in `docs/05-test-points.md`, in its own column, beside the acceptance-criterion ID it belongs to. There are no others.

| Tag | Means | Typical case |
|---|---|---|
| `CREDENTIAL` | Needs an account or secret that belongs to the user | A real payment-gateway sandbox, a live API key, an app-store account |
| `HARDWARE` | Needs a physical device or peripheral | A card reader, a printer, a camera, a specific phone |
| `ASSISTIVE-TECH` | Needs a real screen-reader / switch-control pass by a human | VoiceOver, NVDA, JAWS, TalkBack — the guided loop in `references/accessibility.md` |
| `JUDGMENT` | Needs a human product or aesthetic decision | "Does this wording read right?", "Is this the behaviour you wanted?" |
| `EXTERNAL-APPROVAL` | A third party must act | Store review, bank onboarding, certificate issuance |
| `PLATFORM-IMPOSSIBLE` | The machine that runs the tests cannot run it at all | XCUITest without macOS; a native Windows UI test without an interactive Windows session |
| `PRODUCTION-RISK` | Driving it would touch production data, money, or a live customer system | The one leg that only exists against the real system, after the sandbox equivalent has been driven |
| `NO-EXECUTION` | THIS session has no way to run commands where the repo lives | A chat surface with no shell, or a sandboxed session that cannot reach the user's machine |

Two of these need their own rule, because they are the ones that could otherwise swallow the contract whole:

**`PRODUCTION-RISK` never replaces the test — it replaces one leg of it.** The flow is driven end to end against the sandbox, staging or local equivalent first; only the step that genuinely has no non-production equivalent is delegated, with its steps and its evidence. Tagging a whole flow `PRODUCTION-RISK` because its final step touches a live system is the same escape as tagging a whole checkout `CREDENTIAL`. This tag also aligns with SKILL.md "When to stop and ask": the assistant never drives against production data, money or a live customer system on its own initiative.

**`NO-EXECUTION` is a fact about the session, not about the work — and it is never an excuse to hand the clicking to the user.** When the assistant has no command execution where the repository lives (a chat surface with no shell, a sandboxed session that cannot reach the user's machine), the response is NOT "please go to that screen and tell me what you see". It is: write the driven tests in full, write the exact commands that run them, record the affected criteria as `⚠ unverified — NO-EXECUTION`, and hand over a ready-to-paste prompt for a session that DOES have a shell (the continuation-prompt mechanism in `references/project-state.md`). The work moves to a capable environment; it does not turn into the user's clicking. Check this capability at Phase 1 §5a and at the first test point of every session — a session that assumes it can run commands and cannot will discover it at the worst moment.

**`NO-EXECUTION` has a partial case, and it is the one that catches sessions out.** The tag as written names a session with no way to run commands where the repo lives. Some environments are neither that nor fully capable: they CAN execute, and they CAN touch the user's files, but not both at once, or not with a network. The measured case is Cowork's device bridge — the cloud container has network and no access to the user's files; the bridge has the files and no network, cannot delete anything (`rm` returns `Operation not permitted`, and the `.lock` files git leaves behind then block the user's own repository), and exposes no `localhost` of the user's machine, so a playground started there is invisible. A session in that shape can genuinely run the linters over the files it can see and genuinely cannot install a dependency, boot a playground, or fetch anything. Two rules follow:

- **Say which half is missing, at Phase 1 §5a and at the first test point of the session** (Phase 1 §5a question 6), in the same breath as the capability itself. "This session can execute, but not where the network is" is a usable statement; "this session can execute" is a false one that produces a promise the session then breaks.
- **Tag per leg, never per session.** A criterion whose verification needs the missing half is `⚠ unverified — NO-EXECUTION`, naming what was unreachable (network, the repository's own machine, a listening port) and handing over the ready-to-paste prompt for a session that has it. Everything the session CAN drive, it still drives — a partial capability is not a licence to hand the whole suite back, and it is never a licence to hand the clicking to the user.

**The anti-escape rule.** A delegation without one of these eight tags is a protocol defect, caught at the test point and at the sprint close. "It is faster if the user checks it" and "I could not get the selector to work" are not reasons — the first is false and the second is a task, not an obstacle. If a flow resists automation, the fix is a stable identifier in the product (see "Make the product drivable"), not a message to the user.

**The scope rule for `JUDGMENT`.** `JUDGMENT` never substitutes for functional verification. The criterion is driven and asserted exactly as any other; `JUDGMENT` covers only the product question that remains AFTER the test passed — "this is what it does now, is that what you meant?" — and it is asked over the captured evidence, never by asking the user to reproduce the flow to form an opinion. A `JUDGMENT` tag on a criterion that has no driven test beside it is the laziest escape in the whole contract, and it is a defect.

**The scope rule for `CREDENTIAL`.** A credential blocks only the leg that needs it, never the whole flow. A checkout that cannot complete against a real gateway is still driven end to end against an offline payment method, with only the gateway leg delegated. Delegating the entire purchase because one payment method needs a key is the most common way this contract gets quietly broken.

## When the test is written — the test-first policy

Everything above settles WHO drives a test. This section settles WHEN it is written, and it exists for one failure the rest of this file cannot catch.

**A test written after the implementation is written by someone who already knows how the implementation works.** It describes what the code does, not what the requirement asked for. Where those two differ — which is exactly the case worth catching — the difference is invisible, because it is present in both the code and the test. The suite goes green, stays green, and the defect is now protected by a passing test that everyone will read, correctly, as evidence. It is "declared is not delivered" (SKILL.md) in its most convincing disguise, and no amount of driving fixes it: a driven test that asserts the wrong thing is driven, recorded, reproducible and wrong.

A test written BEFORE the code cannot copy the implementation, because there is nothing to copy. That is the whole argument, and it is the only one this section rests on. The classic case for test-first — design pressure on the API — carries much less weight here, since the shape of the code is already fixed by the technical plan; do not use it to justify going further than the scopes below.

### It is a policy, not a doctrine — three values, one card line

Test-first is deliberately NOT applied uniformly. Where it is cheap it is mandatory; where it is expensive it is opt-in and decided per project; where it is counterproductive it is forbidden outright, and "more rigour" is not a reason to overrule that. The project's choice is one line on the project card — `Test-first policy:` — asked once at Phase 2 §4e and recorded with the rest of the technical plan.

Two levels are referred to throughout, and they are defined in full just below: **Level B** is test-first on pure logic (the cheap half), **Level A** is the slice's acceptance criterion turned into a failing check first (the expensive half).

| Value | What it means |
|---|---|
| `pure-logic` | **Default for new projects.** Level B is mandatory; Level A is not applied. |
| `pure-logic + acceptance` | Levels A and B are both mandatory. |
| `none` | Neither level applies. Requires its own `docs/decisions.md` entry — the default is never dropped silently. |

**The bug-reproduction rule below is not part of this policy and does not move with it.** It applies on every project, at every value, including `none`.

### Level B — pure logic, test first (the half that always pays)

Mandatory wherever the policy is not `none`. It covers code that is a function of its inputs, with a closed contract and no framework state to stand up:

- signature computation and verification, token and hash derivation, cryptographic envelopes;
- parsers, serializers, format converters, encoders;
- validators (identifiers, bank codes, postal formats, schema checks);
- state machines and their transition tables (subscription lifecycles, retry ladders, order status);
- money: proration, tax, rounding, currency conversion, totals;
- entitlement and expiry resolution (licences, trials, grace periods);
- anything else whose test needs no environment beyond the language runtime.

Here the test costs minutes to write, runs in milliseconds, and is where a defect costs the most in the field — a wrong signature or a wrong proration reaches real money. Writing it first is not a ceremony on this code; it is the cheapest verification the project will ever buy.

### Level A — the acceptance criterion first (the opt-in half)

Applied only where the card says `pure-logic + acceptance`. The slice begins by translating the acceptance criterion it implements — the `AC-nn` from `docs/02-functional-spec.md` §6, not a paraphrase of it — into ONE executable check that fails, at whatever level the criterion actually lives (integration, driven end-to-end, a real call against the playground). Then the slice is built until that check passes, and the rest of the slice's tests are written as usual.

This is the level that carries the argument at the top of this section into user-visible behaviour, and it is also the expensive one: expect it to add materially to the front of each slice, concentrated in the slices that need a driver stood up. It is opt-in for exactly that reason. A project that wants it on one subsystem and not on the whole codebase records that scope in the technical plan's `## Testing`, beside the policy line, rather than pretending the card value covers it.

### Where test-first is NOT applied — on any policy value

Naming this is as much of the policy as the mandatory half is, because a rule with no boundary gets applied where it does damage and then gets abandoned entirely:

| Not applied to | Because |
|---|---|
| UI markup, layout, styling, block editor markup | The assertion is a design judgment until the design exists; the test would encode the first guess |
| Framework glue — hook registrations, service wiring, bootstrapping | Standing up the global state costs more than the check is worth, and the playground already exercises it |
| Exploratory integration with a third party whose real behaviour is not yet known | See the spike rule below — a test written against a guessed response shape is a guess with an assertion on it |
| One-line configuration, constants, generated files | There is nothing to get wrong that a compile or a lint does not catch |

Coverage of these still exists — it comes from the driven tests, the playground and the static checks that the rest of this file already mandates. What changes is only the ORDER, and only where the order buys something.

### The spike escape hatch (and its closing condition)

When the real shape of a third-party response, a platform API or an undocumented behaviour is unknown, writing the test first is writing fiction. The correct move is a spike: explore against the real thing until the shape is known, in code that is understood to be disposable. **The escape hatch closes the moment the shape is known** — the behaviour is then pinned with a test, and the spike code is either deleted or rewritten behind it. A spike that quietly becomes the implementation, with its test written afterwards from the code it produced, is the exact failure this section exists to prevent, arriving by the one door left open for it. Record the spike and its closing in the slice's notes.

### Guard 1 — the test is not edited to make it pass (UNBREAKABLE)

When a test-first test fails, the cheapest available action is to change the test. It is also, almost always, the wrong one — and an assistant under pressure to reach a green gate will find it first.

**A test derived from a recorded requirement — an `AC-nn`, or a reproduced bug — is NEVER modified to make it pass.** If the test is genuinely wrong, then the REQUIREMENT is wrong, and that is a decision the user makes: it takes a `docs/decisions.md` entry, or a Design Request where a design contract is involved (`references/phase-4-faithful-build.md`). The assistant proposes; it does not settle it by editing the assertion and moving on.

What is NOT covered by this rule, and needs no entry: renaming a test, moving it between files, improving its failure message, fixing its own scaffolding (a broken import, a wrong fixture path, a flaky wait). The line is precise and it is about the assertion: **if the set of behaviours that would pass the test changes, the rule applies.** If it does not, the rule does not.

This is the same rule as `references/phase-5-development.md`'s "never 'fix' the failure by deleting, skipping, or loosening the test" (§2, the three-attempt rule), stated for the one case where the loosening looks like authorship rather than damage — because the test was written minutes ago, by this session, and feels like its own to change.

### Guard 2 — the red is observed, and for the right reason

A test that has never failed is not evidence of anything, and a test that fails on a missing import is evidence of even less. Before the production code is written:

1. **Run the test and observe the failure.** Not "expect it to fail" — run it.
2. **Confirm the failure message matches the absent behaviour**, not a setup error, a syntax error, a missing dependency or a typo'd fixture. A red for the wrong reason is a green in waiting: it goes away when the setup is fixed, whether or not the behaviour was ever built.
3. **Record the red beside the green.** The one-line failure output goes in the test point's evidence cell, and the row's `Red first` column says `observed`.

Skip step 2 and the project accumulates tests that could never have failed — the most expensive failure mode in this whole file, because it produces confidence with nothing underneath it, and nobody ever re-examines a green test.

### The bug-reproduction rule (every project, every policy value)

**A bug fix begins with a test that reproduces the bug and fails, before the fix is written.** This applies on every project regardless of the `Test-first policy:` line, in Phase 5 slices, in maintenance and in hotfixes (`references/maintenance.md`).

Keel already required that every fixed bug carry a regression test. The order is what this rule adds, and it is not cosmetic: a test written after the fix demonstrates that the code now does what the code now does. It never actually reproduced the bug, so nothing proves it would catch the bug's return — which is the only thing a regression test is for. The reproduction failing first is the proof that the test and the bug are about the same thing.

Under time pressure — a production hotfix, an incident — this is the rule most likely to be skipped, and it is the one whose absence surfaces three versions later as the same report from the same customer. It costs minutes. It is not tradeable against urgency; if the fix is urgent enough to ship without it, that is a `docs/decisions.md` entry with the consequence stated, not a silent omission.

### What is recorded, and what checks it

- **The policy** — the project card's `Test-first policy:` line, plus any narrower scope in `docs/03-technical-plan.md` `## Testing`.
- **The red** — `docs/05-test-points.md` gains a `Red first` column, holding exactly one of five values: `observed` (the failure line is in the evidence cell), `n/a — policy` (the card's `Test-first policy:` does not cover this row — `none`, or a Level A row on a `pure-logic` project), `n/a — out of scope` (the row is in the not-applied table above), `n/a — predates` (the row existed before the project adopted the policy — it is not retroactive), `n/a — delegated` (the row's `Coverage` is one of the eight tags, so nobody here ran it; on `NO-EXECUTION` the test is still WRITTEN first and handed over, and that goes in the delegation steps).
- **`scripts/keel-verify`** checks three things, and the asymmetry between them is deliberate. It **FAILS** a row whose `Red first` cell is empty or holds anything outside the five values — the same enum check `Coverage` already gets, and the reason both enums are closed is that a script can only count what it can recognise. It **FAILS** a row claiming `observed` with no failure output in its evidence cell — a claim without its evidence, which is the one thing this skill never tolerates. And it **REPORTS**, never fails, every row whose value is not `observed` and not `n/a — delegated` — the delegated ones are already accounted for by their tag and their steps, and everything else is an escape valve. The rule is deliberately blunt for one reason: the script cannot decide whether a given piece of code is pure logic, so ANY judgment-bearing value has to be visible, or the assistant simply picks the mildest one that nobody looks at. The list goes in the sprint-close report for a person to judge. On a project whose card says `none` the report is one line naming the policy and its decision entry instead of a row list — there the escape was taken deliberately, once, on the record.

## Make the product drivable (this is a build requirement, not a test requirement)

A UI that cannot be addressed reliably forces a human back into the loop, so addressability is built in from the first slice, exactly like accessibility:

- **Every interactive element carries a stable identifier** that is not its visible text: `data-testid` on the web (or the project's recorded attribute), `accessibilityIdentifier` on Apple platforms, `AutomationId` on Windows UIA, `resource-id` on Android. Visible text is localized and is product content — a test bound to it breaks the moment the copy or the locale changes.
- **Never fake an accessibility label to make a test pass.** Apple states it plainly for `accessibilityIdentifier`: the identifier exists so you can avoid *"inappropriately setting or accessing an element's accessibility label"*. A label rewritten to `btn_save_42` is read aloud to a blind user — the test gained a selector and the product lost its accessibility.
- **Identifier convention:** `<screen>.<element>[.<entity-id>]`, in English, no spaces, never translated — `checkout.payButton`, `productList.row.186`.
- **Prefer role-and-accessible-name locators where the text is stable**, because they assert the accessibility tree and the behaviour at the same time. Fall back to the identifier when the text is content.
- **Expose the state the test needs to wait on.** A flow that can only be tested with an arbitrary sleep is under-instrumented. Sleeps are banned (see "No sleeps").

`code-reviewer` treats a new interactive element without its identifier as a slice defect, exactly like a missing docblock.

## `scripts/keel-doctor` — the environment doctor

Generated at the Phase 5 scaffold from the technical plan's environment requirements table (Phase 2 §4d), committed to the repo, and run before gate zero, at the first test point of every session, and at the Phase 7 gate.

### Three modes, and the default never touches the machine

| Mode | Does | Requires |
|---|---|---|
| `--check` (default) | Detects only. Prints the table. Exits non-zero if anything blocking is missing. | Nothing — never sudo, never network beyond a version probe |
| `--plan` | Detects, then prints the exact commands it WOULD run, verbatim, without running them | Nothing |
| `--fix` | Runs those commands, after the user's explicit OK on the printed list | Whatever each command needs |

`--check` must never require privileges. If detecting something needs sudo, that is not detection.

`--plan` exists for trust: the user sees the literal command list before anything is installed, can copy-paste it to run by hand, and can veto individual lines. An assistant that installs software on someone's machine shows its hand first.

### The output table — six columns, four states

| Requirement | Detected | Required | State | Severity | How to install |
|---|---|---|---|---|---|
| Node.js | 18.19.1 | >= 22 | TOO OLD | blocking | `mise use -g node@lts` |
| Docker (CLI) | 29.4.3 | any | OK | blocking | — |
| Docker (daemon) | not responding | running | NOT OPERATIONAL | blocking | `docker desktop start` |
| Playwright browsers | chromium absent | chromium | MISSING | blocking | `npx playwright install chromium` |
| ext-mbstring | present | required | OK | blocking | — |
| phpMyAdmin | absent | — | MISSING | optional | (not needed for tests) |
| Permission mode | `manual` | not `manual` | MISSING | advisory | write `.claude/settings.local.json` (`defaultMode: "auto"`) or start with `--permission-mode auto` |
| Notification channel | none responding | a delivering channel | MISSING | advisory | authorize the recorded channel, or accept in-chat only (`references/notifications.md`) |

The four states matter more than they look. Collapsing `NOT OPERATIONAL` into `MISSING` is the single most common doctor bug: it makes the assistant propose reinstalling Docker when all that was needed was to start it. Severity is its own column, not a footnote: **blocking** means no work is possible without it, **optional** means quality of life, **advisory** means the work will complete but under friction the user should know about. Neither an optional nor an advisory row that is missing fails the run, and neither gates a release.

**The permission-mode row is the standing advisory one.** The doctor reports the session's active permission mode and whether `.claude/settings.local.json` exists with a `permissions.defaultMode` other than `manual`. `manual` — or no file and no mode passed — is reported as MISSING at **advisory** severity, with the fix named: write the local settings file, or start with `claude --permission-mode auto`. It never exits non-zero on this row and never blocks a gate; it exists because a session in `manual` mode hits a dialog on every composite command and the driven-test protocol quietly degrades into asking the user, which is the failure this whole reference exists to prevent. The full procedure and the file's exact contents are in `references/keel-maintenance.md` ("Permission mode"). The notification-channel row is advisory for the same reason and reports the same way: the channel is PROBED, a compose-only connector is never counted as delivering, and "no channel" is a stated result rather than a silent one (`references/notifications.md`).

Emit the same content as JSON (`--json`) so the assistant decides from structured data instead of parsing its own table.

### Detection rules that are not obvious

- **Use `command -v`, never `which`.** `command -v` is the POSIX builtin and uses the shell's own lookup; `which` is an external tool, absent from minimal images, with inconsistent exit codes. On Windows/PowerShell, `Get-Command <name> -CommandType Application -ErrorAction SilentlyContinue`.
- **A negative probe never concludes `MISSING` on its own — corroborate before writing the row.** The assistant's shell is frequently not the user's shell: a restricted `PATH` (a bare `/usr/bin:/bin:/usr/sbin:/sbin` is the measured case) hides `php`, `gh`, `docker`, `node` and `npm` that are installed and working in the user's login shell. A `MISSING` derived from that offers to install what is already there — the same class of bug as collapsing `NOT OPERATIONAL` into `MISSING`, and it spends the user's machine rather than their patience. Before writing `MISSING`, corroborate in this order: the login shell (`bash -lc 'command -v X'`, `zsh -lc` where that is the user's shell), the platform's known install locations for that tool, and any variable the tool itself exports — **Claude Code exports `CLAUDE_CODE_EXECPATH`, the absolute path of the running binary, and `CLAUDE_CODE_VERSION`, its version**, so a session running under it resolves its own CLI even with an empty `PATH`. A tool found outside `PATH` is **present**, and the row records the absolute path that works, because that is what any later command must use. Only an absence that survives every corroboration is `MISSING`.
- **And a positive probe never concludes operational.** The command existing and the command working are two questions, and the second is the one the project depends on. The measured case: `npm install -g` accepts a package whose `engines` field demands a newer runtime than the one active and emits only an `EBADENGINE` warning, so the binary lands on `PATH`, the probe says yes, and whether it runs is still unknown. Always follow a positive `command -v` with the tool's own version probe, compare it against the requirement, and record `TOO OLD` or `NOT OPERATIONAL` rather than `OK` when it does not meet it. This is the same four-state discipline read in the other direction, and both directions are needed: the row states what is TRUE of the machine, never what the first command happened to return.
- **Docker needs two questions, not one.** `command -v docker` answers "installed"; `docker info` (exit 0) answers "the daemon responds". `docker version --format '{{.Client.Version}}'` prints the client version *and exits non-zero* when the daemon is down, so exit code alone lies. Distinguish three causes in the message: daemon stopped, permission (user not in the `docker` group), and context/`DOCKER_HOST` pointing elsewhere (`docker context ls` works with the daemon down).
- **Version probes that behave badly:** `java -version` writes to stderr (`java --version` on JDK 9+ writes to stdout); as root, Composer warns, disables plugins and — interactively — PROMPTS before continuing, which hangs an unattended probe; export `COMPOSER_ALLOW_SUPERUSER=1` so the version probe returns instead of waiting; `node -p "process.versions.node"` avoids the `v` prefix; `php -r 'echo PHP_VERSION;'` avoids parsing the banner.
- **Architecture under emulation.** On Apple Silicon running under Rosetta, `uname -m` reports `x86_64`. Check `sysctl -n sysctl.proc_translated` (1 = translated, so the real arch is `arm64`) before choosing a download. On Windows, `RuntimeInformation.OSArchitecture` is honest where `$env:PROCESSOR_ARCHITECTURE` reports the process, not the machine.
- **Linux distro:** read `/etc/os-release` (`$ID`, `$VERSION_ID`, `$ID_LIKE`); `$ID_LIKE` avoids a case branch per derivative. Detect the package manager by probing for the binary, never by inferring it from the distro name.
- **Delegate where a real doctor already exists — but check what each probe actually promises.** `xcodebuild -checkFirstLaunchStatus` exits non-zero when Xcode components are missing and modifies nothing: a true probe. `mise doctor --json` reports its own health. **`npx playwright install-deps --dry-run` is NOT a probe:** it prints the install command it would run, and does not tell you whether anything is missing — its exit code says nothing about the state of the machine. Use it to populate `--plan`, never to decide a row's state. The real detection for browser dependencies is to launch the browser: `npx playwright install --dry-run` reports where binaries would go and `npx playwright install --list` shows what is installed, and a two-line smoke script that launches the browser headless and closes it is what actually proves the system libraries are there. A doctor that reads a `--dry-run` exit code as "all good" certifies a broken environment, which is worse than having no doctor.

### Installation rules

- **Nothing global is installed without the user seeing the list first.** `--fix` prints the plan, asks once, then runs it. Granular: the user can decline individual rows.
- **Prefer per-project and reversible over global and permanent**, in this order: the project's own dev dependencies → a version manager in the user's home (`mise` on macOS/Linux/WSL; `fnm` or `volta` on native Windows, where mise runs through shims with degraded activation) → a container → the system package manager last.
- **Never change a global runtime version silently.** It breaks the user's other projects. Runtimes are pinned per project (`mise.toml`, `.nvmrc`, `.tool-versions`).
- **Accepting a licence is the user's act, not the assistant's.** `--accept-package-agreements`, `--accept-source-agreements` and any EULA acceptance are only ever run inside `--fix` after the OK. Docker Desktop in particular can create a paid-licence obligation the developer has no authority to accept: it is free for personal use, education, non-commercial open source and small businesses (fewer than 250 employees **and** under $10M annual revenue — both conditions), and requires a paid subscription otherwise, government entities included. Where only "a Docker daemon" is needed, prefer Docker Engine on Linux or Colima on macOS/Linux (MIT, drop-in, works unchanged with wp-env and docker compose); note that Colima does not ship the `docker` client, which is installed separately.
- **`usermod -aG docker $USER` is effectively granting root** to that user. If it is proposed, say so in that sentence — never run it silently.
- **Say what it will download before downloading it.** Browser binaries are hundreds of megabytes; on a metered connection that matters.
- **Idempotent by construction.** `pacman -S --needed`, `winget install --no-upgrade`, `brew bundle install`, `mise install`. "Already installed" is success, not failure — in winget that means treating `0x8A150061` and `0x8A15010D` as OK. A pending reboot (`0x8A150109`, `0x8A15010A`) is its own state and needs the human. Never append a line to a shell profile without checking it is not already there.
- **Verify after installing; do not assume.** A freshly installed tool is often absent from the current shell's PATH — report "restart your terminal", not "installation failed".
- **If the project has a devcontainer, offer it before installing anything on the machine.**

### What the doctor must never claim it can do

Some things need a human, and saying so immediately is worth more than a workaround:

- **Installing full Xcode** requires an Apple ID with two-factor authentication. `xcodes` and `mas` both hit the same wall. The doctor detects and reports; it never attempts it. Once Xcode is present, `sudo xcodebuild -license accept`, `sudo xcodebuild -runFirstLaunch` and `xcodebuild -downloadPlatform iOS` are automatable after the OK (all need sudo).
- **`xcode-select --install` opens a GUI dialog.** The headless path is the one Homebrew uses (touch the sentinel file, find the label with `softwareupdate -l`, install it with `softwareupdate -i`), and it needs sudo.
- **Granting macOS Accessibility permission to Xcode Helper cannot be scripted.** The only known path is writing to the TCC databases with SIP disabled, which is a serious security downgrade — never do it on a personal machine, and never propose it.
- **`playwright install-deps` only knows Debian and Ubuntu.** Its dependency tables cover those two families and nothing else. On Fedora, RHEL, Arch, openSUSE or Alpine it cannot help: use the official container instead of guessing package names.
- **Native Windows UI automation needs an interactive, unlocked desktop session** with autologon. There is no Windows equivalent of Xvfb, session 0 does not work, and an RDP session that disconnects locks the desktop and blinds the automation.

### Which machine the doctor is talking about

Three machines can be involved and they are not always the same one: the machine the USER works on, the machine where the REPOSITORY lives, and the machine that RUNS THE TESTS. In the common case (a developer, their laptop, their repo) all three are one and the question never comes up. But an assistant running in a cloud sandbox against a mounted folder, a hosted macOS runner, or a dedicated Windows VM splits them — and every question below has a different answer per machine.

So the requirements table names, per row, WHICH machine must satisfy it, and two questions get answered explicitly at Phase 1 §5a and again at the first test point of each session:

- **Can this session run commands where the repository lives?** If not, that is `NO-EXECUTION` and the work moves to a session that can — it never becomes the user's clicking. And the question has a middle answer: a session that executes on one filesystem and reaches the user's files on another, or that reaches the files with no network, answers "partly" — see the partial case above, and say which half is missing rather than which capability exists.
- **Whose screen would a non-headless test take?** The screen-stealing question is only about a machine with a human in front of it. A UI test on a dedicated runner steals nothing; the same test on the user's laptop steals their afternoon.

## Drivers by surface

The technical plan names one driver per surface the project has. What each one is, and whether it can run without stealing the screen:

| Surface | Driver | Steals the screen? | Evidence it produces |
|---|---|---|---|
| Web UI (any stack) | Playwright | No by default; **yes while a headed run lasts** | Trace, video, screenshots, JSON report |
| WordPress / WooCommerce admin and storefront | Playwright against wp-env or Playground CLI | Same as above | Same, plus WP debug log |
| REST / HTTP API | `curl` or the driver's request context | No | Status, body, headers per call |
| MCP server | Inspector CLI (`--cli --method ...`) or scripted JSON-RPC over stdio | No | Request/response transcript |
| CLI (non-interactive) | Direct execution plus output snapshot | No | stdout/stderr, exit code |
| CLI / TUI (interactive) | A real PTY — `script`, `expect`/`unbuffer`, `pexpect` — or tmux with `capture-pane -p` for full-screen TUIs | No | Captured pane / session log |
| Electron | Playwright `_electron.launch` (experimental but supported) | No on Linux under Xvfb; yes on a desktop | Screenshots, video, main-process evaluation |
| iOS / iPadOS | XCUITest via `xcodebuild test` on the Simulator | **No, if done right** — see below | `.xcresult` bundle with screenshots, video, activities |
| macOS app | XCUITest | **Yes — unavoidable** | `.xcresult` bundle |
| Android | Espresso / UI Automator / Maestro on an emulator started with `-no-window` | No — genuinely headless | Screenshots via `adb exec-out screencap`, logcat |
| Linux desktop app (GTK/Qt) | AT-SPI (dogtail) inside `xvfb-run` | No — the virtual display is separate | Screenshots of the virtual display |
| Windows desktop app | FlaUI (or FlaUI.WebDriver / Appium over UIA) | **Yes — needs a live session** | Screenshots, UIA tree dumps |
| Library / package | A clean consumer project installing the BUILT artifact | No | Command output per example |

### The screen-stealing question, answered precisely

This is the point that makes the difference between "the assistant tests everything" and "the assistant takes over my computer for twenty minutes", so it is decided in the technical plan, never discovered mid-sprint.

- **Web, API, MCP, CLI, Android: never an issue.** Playwright is headless by default; the Android emulator's `-no-window` is real headlessness, not a trick.
- **iOS Simulator: not an issue if the assistant closes Simulator.app first.** `xcodebuild test` runs the simulator in the background when `Simulator.app` is not already open; if the user has it open, the run becomes visible and starts capturing the keyboard. So the pre-run sequence is fixed: quit `Simulator.app`, `xcrun simctl shutdown all`, and drive a **dedicated** simulator created for the project (`xcrun simctl create ...` with device type and runtime read from `simctl list`, never hardcoded) rather than the one the user works in. CPU load is still noticeable; that is honest to mention and cheap to accept.
- **macOS apps: it always steals the screen, and there is no fix inside the machine.** A macOS UI test moves the real cursor and types on the real keyboard, which is why Apple requires granting Accessibility permission to Xcode Helper. The mitigations, in order of preference: a dedicated Mac or VM, a separate macOS user account whose session runs the tests, or a hosted macOS runner. Record which one applies in the technical plan. If none is available, macOS UI tests are scheduled deliberately — announced, batched, and run when the user is not working — never fired mid-conversation.
- **Windows native apps: same shape as macOS.** A dedicated Windows VM with autologon, or the tests are scheduled.
- **Linux desktop apps: solved by `xvfb-run`.** The app runs against a virtual display the user never sees. Force X11 inside Xvfb rather than trying to automate a live Wayland session: Wayland has no client API to enumerate or activate another application's windows, and global input injection needs portal consent, which defeats unattended runs. AT-SPI itself works fine under Wayland (it rides D-Bus), which is why the accessibility route survives where `xdotool` does not.

## Filling forms for real

The part most often handed back to the user, and the part every driver does natively.

**Web (Playwright).** `fill()` sets a value and fires input/change; `pressSequentially()` types character by character when the field reacts to each keystroke (autocompletes); `clear()` empties. Native date/time inputs take the value format, not the displayed one (`2020-02-02`, `13:15`, `2020-03-02T05:15`). `selectOption()` accepts value, `{ label }`, `{ index }`, or an array for multi-select. `check()` / `uncheck()` / `setChecked()` for checkboxes and radios. `setInputFiles()` uploads from disk, from an array, from a directory, or **from an in-memory buffer** — `{ name, mimeType, buffer }` — which is how a driven test uploads a generated file without touching the filesystem; when the page opens a native dialog instead of exposing an input, wait for the `filechooser` event and set the files on it. `frameLocator()` enters iframes. CSS and role/text locators pierce open shadow DOM; XPath does not, and closed shadow DOM needs a hook exposed by the app. `dragTo()` for drag and drop, with the manual `hover` → `mouse.down` → `hover` → `mouse.up` sequence for components that need the intermediate events.

Assert the validation, not the vibe: `toHaveAccessibleErrorMessage()` is the right assertion for a field error (it checks the error is programmatically associated, so it doubles as an accessibility assertion), with `toHaveAttribute('aria-invalid', 'true')`, `toContainText` on the alert region, and `toHaveJSProperty('validationMessage', ...)` for native browser validation.

**Apple (XCUITest).** `typeText()`, `tap()`, `swipeUp(velocity:)`, `adjust(toNormalizedSliderPosition:)`, `adjust(toPickerWheelValue:)`, `press(forDuration:thenDragTo:)`. State is asserted with `waitForExistence(timeout:)` and `wait(for:toEqual:timeout:)` over a key path. App state is set up through `launchArguments` and `launchEnvironment`, never by reaching into the app — a UI test sees the app only from outside.

**The rule underneath all of it:** every field the flow has gets filled in at least three shapes — valid, empty, and invalid — because the empty and invalid cases are exactly the ones a human tester skips and exactly where the bugs are.

## No sleeps

An arbitrary wait is a flaky test wearing a disguise. Playwright's actionability checks (visible, stable, receives events, enabled, editable) and its retrying web-first assertions remove the need entirely; XCUITest has `waitForExistence` and `wait(for:toEqual:)`. `waitForTimeout` and `sleep` are banned from driven tests. If a state genuinely cannot be waited on, the product is under-instrumented — expose the state, do not paper over it.

## Reading back what the machine saw

Driving without reading back is half a test. A page can look correct and be throwing an uncaught exception, returning 500s to a background request, or logging a PHP notice.

- **Web:** subscribe to `console`, `pageerror`, `requestfailed` and `response` (flagging status >= 500), collect them per test, attach the collection to the report, and fail the test on any of them. Playwright also exposes pull-style readers for console messages and page errors, which suit an agent better than event handlers. Use `--trace on` and read the trace rather than parsing stdout; the JSON reporter is what the assistant should consume.
- **WordPress:** enable `WP_DEBUG_LOG` in the environment config (it is not on by default) and read the debug log at every test point. A test that passes while `debug.log` gained a fatal or a notice has not passed.
- **Apple:** everything of value lives in the `.xcresult` bundle, never in stdout. `xcrun xcresulttool get test-results summary|tests|test-details|activities|insights` reads it; `xcrun xcresulttool export attachments` extracts screenshots and videos to files (with a `manifest.json` mapping UUIDs to readable names). The legacy `xcresulttool get --format json` path is deprecated — do not build on it. `xcbeautify` is cosmetic formatting of stdout only; never parse stdout for results. Note that `-resultBundlePath` **fails if the path already exists**, so the runner deletes or timestamps it before each run.
- **Android:** `adb logcat`, plus `adb shell uiautomator dump` for the view hierarchy when a locator fails.
- **Everywhere:** attach the evidence to the test result rather than pasting it into chat. Chat is not an artifact.

## Static checks and sniffers — also the assistant's job

Code review by tooling is driving too, and it runs on every slice, not once before release:

- **WordPress / WooCommerce:** PHP_CodeSniffer with the WordPress Coding Standards ruleset, PHPStan (with the WordPress stubs), the official Plugin Check, and `php -l` on every touched file.
- **JavaScript / TypeScript:** ESLint, the type checker, Stylelint for CSS.
- **Swift:** the compiler's own warnings treated as findings, plus the project's chosen linter.
- **Everywhere:** the project's formatter runs and its output is committed, so formatting never appears in a review diff.

Every one of these has an exact command in `docs/03-technical-plan.md` §Tooling commands, runs in the same test point as the tests, and its output is recorded. A finding is a slice defect, not a note for later. Suppressions are narrow, carry a written reason, and are counted at every sprint close so the count can only go down deliberately.

## Accessibility is part of driving, not a separate errand

The automated pass costs almost nothing once a driver exists, and it is the assistant's job in full:

- **Web:** `@axe-core/playwright` inside the existing tests, scoped with `include`/`exclude` and tagged to the target conformance level. Run it **per state**, not per page — the empty form, the form showing errors, the open modal, the expanded menu — because that is what a live-DOM scanner can do and a crawler cannot. `pa11y-ci` adds a sitemap-wide sweep when there are many public URLs. Lighthouse's accessibility score is a weighted average of axe audits and is not a conformance statement.
- **Apple:** `try app.performAccessibilityAudit()` after navigating to each screen — it fails the test automatically when it finds issues, and it takes audit-type filters (`.contrast`, `.dynamicType`, `.hitRegion`, `.sufficientElementDescription`, `.elementDetection`, `.textClipped`, `.trait`, and on macOS `.parentChild` and `.action`). There is no command-line accessibility auditor on Apple platforms: inside a UI test is the only automatable path.
- **Android:** `AccessibilityChecks.enable().setRunChecksFromRootView(true)` in the test target. Accessibility Scanner is a manual app and is not scriptable — do not plan around it.
- **Keyboard and focus order are automatable too:** drive `Tab` through the form and assert the focused element sequence, and snapshot the accessibility tree (Playwright's ARIA snapshots) as a regression artifact.

And the honest boundary, which does not move: automated tooling finds a large share of *issue volume* — Deque measures about 57% with axe — but far less of WCAG success criteria, and the W3C is explicit that no tool alone determines conformance. Alt-text quality, reading order, link purpose out of context, error-message comprehensibility, captions, real screen-reader behaviour: those are the `ASSISTIVE-TECH` delegation, run as the guided loop in `references/accessibility.md`. The automated pass never closes them, and never claims to.

## Which model drives

Driving is not the expensive part of thinking. Deciding *what* to test — reading the acceptance criteria, choosing the cases, working out what "invalid" means for this field, writing the assertions — is authoring work and belongs to the strongest model available. **Executing** those tests, driving the recorded flows, collecting the evidence and triaging a failure into "the product broke" or "the test broke" is mechanical: the expectations were already written down, and the job is running commands and comparing output.

So where the environment supports subagents with per-role models (`references/assistant-config.md`, "Model binding"), the `test-driver` agent is bound to the **mechanical** role — the cheapest capable model — and only a run that resists diagnosis, or one where the driver is being asked to *design* missing cases rather than execute existing ones, is escalated. Escalate the run, not the binding.

This is the binding that pays back most often: test runs are the most repeated agent invocation in the whole of Phase 5 — every slice, every sprint close, every session's freshness check. On a flat subscription the gain is speed and rate-limit headroom; on metered billing it is direct spend. Where the environment has no subagents, the same principle applies by hand: keep the driving loop tight and mechanical, and reserve deep reasoning for writing the cases and for failures that do not explain themselves.

## Evidence — and the format that makes it checkable by a script

Every driven check writes one row in `docs/05-test-points.md` with: the exact command, a result summary, the paths to the artifacts (trace, video, result bundle, screenshots), and the commit hash. A result without its command and its output is an empty cell, and an empty cell is a missing check.

Artifacts live in the project's ignored artifacts directory, never committed — except the small ones a reviewer needs — and the row points at them.

**On every browser surface the trace and the video are not optional extras, they are the evidence.** A headless run leaves nothing a human can inspect, so "the tests passed" is an assertion about work nobody watched. With `trace` and `video` on, the same run leaves a timeline carrying a DOM snapshot before and after each action, the selector used, the network call it triggered, the console at that instant — rewindable, and readable months later by someone who was not there. Configure both in the project's Playwright config, point the test-point row at the trace file, and open it with `npx playwright show-trace <path>` when a result is questioned. A driven check on a browser surface whose row has no trace path is incomplete in exactly the way an unrecorded command is.

**Offering to run it headed is a courtesy, never a substitute.** When the user wants to watch the flow happen — a reasonable thing to want, and the honest answer to "I don't see a browser doing anything" — the assistant offers the documented headed script and says plainly what it costs: it takes over the screen while it runs, it is slower, and it proves nothing the recorded run did not already prove. What is never acceptable is the inverse: skipping the recording because the user could watch, or answering a doubt about coverage by inviting the user to run the tests themselves. That is the delegation this file exists to end, re-entering through the door marked "transparency".

Where something could not be driven, the row records its tag, the exact steps for the person who will do it, and `⚠ unverified` until they report back. `docs/PROGRESS.md` carries the open item.

**Two conventions turn all of this from prose into something `scripts/keel-verify` can actually check.** Without them the coverage rule is self-declared, which is the failure this whole file exists to end:

1. **Every acceptance criterion carries a stable ID** — `AC-01`, `AC-02`, … — assigned in `docs/02-functional-spec.md` §6 and never reused or renumbered. The ID appears in three places: the criterion itself, the name of the test that covers it (`AC-07 checkout rejects an invalid postcode`), and the test-point row. A grep for the IDs across the three is a real check; matching prose against prose is not.
2. **`docs/05-test-points.md` carries two dedicated columns:** `Criterion` (the `AC-nn` ID, or `—` for checks that are not criterion-bound) and `Coverage`, whose value is exactly one of: `driven` (a test drove it — the command and evidence are in the row), or one of the eight tags. Free text in the `Coverage` column is a defect: the point of the enum is that a script can count the rows that are neither.

With those two in place the check is trivial and honest: every `AC-nn` in the spec appears in at least one test-point row whose `Coverage` is `driven` or a valid tag, every tagged row has its steps, and no row has an empty or improvised coverage value.

## What the assistant genuinely cannot drive

Recorded here so it is never rediscovered as a surprise mid-project:

- **A real payment through a live gateway.** Offline methods (cash on delivery, cheque, bank transfer) are fully drivable and are what the end-to-end purchase test uses. Stripe, PayPal and WooPayments need the user's own test credentials, outbound network, and a publicly reachable webhook — that leg is `CREDENTIAL`.
- **XCUITest without macOS.** `xcodebuild` is a macOS binary and the simulator runtime only loads under macOS. There is no emulation, no port, no workaround — only a real Mac, a hosted macOS runner, or a device farm (which is a hosted Mac with extra steps). On Windows or Linux the Apple section of the plan is inexecutable and the doctor says so and stops.
- **A native Windows UI test on a headless runner.** UIA needs a live interactive session.
- **A real assistive-technology pass.** A screen reader tells you what a blind user hears, and no audit reproduces that.
- **Anything behind two-factor authentication owned by the user.**

## Definition of done (this reference)

- The technical plan names one driver per surface the project has, states for each whether it runs without taking over the user's screen, and records the mitigation where it does not.
- `scripts/keel-doctor` exists, is committed, is generated from the plan's environment requirements table, and passes `--check` before gate zero and at the first test point of every session.
- Every acceptance criterion with a user-visible surface has a driven test that fills the real fields and asserts what the interface shows — not an instruction for the user.
- Console errors, failed requests, 5xx responses and platform logs are read back and fail the test.
- The automated accessibility pass runs per screen and per state, inside the same driven tests.
- Static analysis and sniffers run at every test point with recorded output and a tracked suppression count.
- Every acceptance criterion carries its `AC-nn` ID, and every ID appears in `docs/05-test-points.md` with a `Coverage` value that is either `driven` or one of the eight tags — never free text, never blank.
- Every delegation to the user carries its tag and its exact steps; a delegation without a tag is a defect, and `JUDGMENT` or `PRODUCTION-RISK` on a criterion with no driven test beside it is the same defect wearing a label.
- Anything that could not be driven is `⚠ unverified` with its reason — never silently absent and never reported as passing.
- Where the session's environment is protected (no network where the files are, no deletion, no `localhost`, execution and files on separate filesystems), the limitation was stated at Phase 1 §5a and the affected legs carry `NO-EXECUTION` naming the missing half — not the whole suite, and never the user's clicking.
- The project card carries a `Test-first policy:` value, and where it is `none` that value has its `docs/decisions.md` entry.
- Every test written under the policy was seen to fail first, for the absent behaviour and not for a setup error, with the failure line recorded and its row's `Red first` column set.
- No test derived from an `AC-nn` or from a reproduced bug was modified to make it pass without a decision entry or a Design Request behind the change.
- Every bug fixed in this project — slice, maintenance or hotfix — was reproduced by a failing test BEFORE the fix, on any policy value.
