# Security audit — active hunting, independent validation (optional; a gate on critical projects)

The security profiles in `references/security/` are read from Phase 1 onward and checked at every Phase 5 test point: they keep the build pointed the right way while it is being written. That is a checklist walked by the session that wrote the code, and it has the limit every self-review has: it confirms that the rules were *considered*, not that nobody can break them. This file is the other instrument. An audit takes the same profiles and turns each one into the playbook of a **hunter** whose job is to find where the built project violates them, then hands every candidate to a **verifier** that did not find it and tries to refute it. Only what survives is reported as a vulnerability.

It does not replace the Phase 5 profile check, which stays exactly as it is, and it never runs on every slice. It runs when someone asks for it, and at the Phase 7 gate of a project whose card says `Security audit: required`.

**Lineage.** The method (reconnaissance, coverage-led hunting, a candidate gate, independent validation, three verdicts, a report derived only from verified records) is adapted from Cloudflare's open-source `security-audit-skill` (MIT; credited in `NOTICE`). Keel keeps the method and drops the infrastructure that does not fit its stack: the OS-enforced sandbox with no network and resource limits, the descriptor-level artifact promotion, the multi-wave critic budget and the full JSON schema with its validators. Their job, bounding what executing the target can do, is done here by the project's own disposable playground and by the boundaries below. Cloudflare's low-level hunting modules (memory safety, kernel, IPC, cloud control planes) are not used: Keel's hunting modules are its own profiles, because those are what a Keel project was built against.

## When it runs

- **On request.** "Security audit", "auditoría de seguridad", "audit the security of…", "pen-test the code", "a full or end-to-end security review" of a Keel project → this flow. A review of **a change** (a diff, a PR, a slice) is not an audit: that stays with the profile and, where it exists, the `security-auditor` agent (`references/assistant-config.md`). If the request could mean either, ask one question before creating anything.
- **At the Phase 7 gate** when the card says `Security audit: required` (below). With `optional`, Phase 7 offers it in one line and moves on.
- **At a Phase 8 launch** of a site with a real backend (a form handler, an API, a login). The site's profile is `references/security/website.md` plus `references/security/web-app.md`, and the same flow applies through Phase 8's reuse of Phase 7.
- **Never** as part of a Phase 5 test point or a sprint close.

An audit is work, so it is a slice before it starts ("Sprints are the ledger of all work"), sized by the number of units in step 2: roughly one hunter per unit and one verifier per candidate.

## The card line — `Security audit:`

`required — <criterion>` / `optional` / `declined (D-0XX)`. It is **derived, never asked**. It is set at Phase 2 §4c when `docs/threat-model.md` is written, because the threat model is where these facts are first on record, and it is recomputed whenever the threat model changes (a scope change that adds payments flips it). It is `required` when ANY of these holds, and the line names which one:

1. **Money moves.** A payment gateway, refunds, subscriptions or renewals, a wallet, credits, coupons that discount real orders, or any payment notification the product accepts.
2. **Personal data.** It stores or processes accounts, customer records, orders, addresses, contact submissions, health or financial data, or anything else that identifies a person.
3. **A programmatic surface reachable from outside.** An MCP server, tools or WordPress abilities; REST or GraphQL routes; webhooks; AJAX or `admin-post` handlers reachable by unauthenticated or low-privilege users; a public API.

Otherwise the line is `optional`. `declined` exists only for a project that meets a criterion and whose user explicitly does not want the gate. It needs the D-entry, and the gate then says in one line that it was skipped and why. An existing project gets the line at its v6.3.0 reconciliation, derived from its threat model, or from the code where the threat model predates it.

## Boundaries — what stands in for Cloudflare's sandbox

- **Source first, read-only.** The audit never edits product code, tests or config. A confirmed finding becomes a slice (see "After the report"), which is the rule "Something looks like a security problem → escalate, never patch quietly" applied to the whole run.
- **Execution happens only in the project's playground** (`docs/playground.md`, `references/playground-recipes.md`), with its synthetic seed data and throwaway credentials. That environment is Keel's bounded local target. Never production, a live customer system, a third-party API in live mode (sandbox keys only), a shared staging server, or any account that is not the playground's. No load, flood or brute-force testing. Stop at the smallest observable effect: the wrong return value, the one foreign record read, the one unescaped string rendered.
- **Nothing is installed to attack with.** Use what `scripts/keel-doctor` already provides. A check that needs a missing tool becomes `needs_validation` naming the tool.
- **What is knowingly given up:** target code executed in the playground runs with the privileges of that environment, not inside an OS-enforced jail. That is acceptable for the project's own tree in a containerised playground (wp-env, Docker). Never execute untrusted third-party input (a payload fetched from the internet, a dependency's post-install script) outside it.
- **A decisive fact only production can show** (web-server headers, WAF rules, a hosting panel setting, the real gateway configuration) is never probed. It is `needs_validation` with an owner-observed check, tagged `PRODUCTION-RISK` per `references/test-automation.md`.

## Where the output lives — and why it is not committed while open

A run writes to `docs/security-audit/<YYYY-MM-DD>-<short-sha>/`: `recon.md`, `coverage.md`, `findings.json` and `SECURITY-AUDIT.md`.

**`docs/security-audit/` is gitignored**, added to `.gitignore` before the first file is written. A report listing confirmed, unfixed vulnerabilities with their file, line and reproduction is a disclosure the moment it reaches a public repository, and a private repository can become public or be cloned by someone it should not reach. So:

- **What IS committed** is `docs/security-audit.md`, the audit log. It has one row per run: date, audited commit, scope, profiles, verification mode, counts (confirmed by severity, `needs_validation`, `rejected`) and how many confirmed findings remain open. While a finding is open, no title, path or wording describes it. When its fix ships, the row gains the finding's title, severity and fix commit: disclosure after the fix, which is the order responsible disclosure uses.
- **This is a recorded exception to "the work never lives only on this machine"**, and it is stated rather than implied. The raw run is reproducible by re-running at the audited commit, and the log survives. A project whose repository is private and whose user wants the runs committed removes the ignore line with a D-entry and the card reads `required — <criterion>, reports committed (D-0XX)`.
- **Slices that fix findings carry neutral titles while open** ("Security fix SA-03 from the 2026-09-23 audit"), because sprint files are committed.
- **A confirmed vulnerability is never filed as a public forge issue**, whatever `Issue capture:` says. The forge's private channel (a GitHub security advisory, a confidential GitLab issue) is used only on the user's word.
- **The confidential-data rule holds inside the output too.** A finding about an exposed secret names the file, the line and the kind of secret, never its value. It also triggers the confidential-data procedure (removal from history and rotation if it was ever pushed) as its fix.

## Step 1 — Reconnaissance: reuse what the project already recorded

Do not re-map the project from scratch. Phases 1–3 and 6 already wrote the map. Read `docs/01-discovery.md` (type, users), `docs/02-functional-spec.md` (flows, roles, permissions, data model), `docs/03-technical-plan.md` (stack, code map, integrations), `docs/threat-model.md` (assumptions, controls with delivery states, "Not defended"), `docs/api/INDEX.md` (every public surface) and `docs/security.md`. On an adopted project, also read `docs/04-adoption-audit.md`.

Then **verify the inventory against the disk, because documentation drifts**. Grep for the stack's registration calls and compare them with `docs/api/INDEX.md`: `register_rest_route`, `wp_ajax_` and `wp_ajax_nopriv_`, `admin_post_`, shortcodes, `wp_register_ability`, MCP tool registrations, framework routers, CLI commands, cron hooks, webhook receivers, file-upload handlers. A surface on disk that INDEX does not list gets its own unit, and the drift is also reported as a documentation defect.

Write `recon.md`, about 800 words at most:

1. Principals and what each is allowed to do by design, from anonymous visitors up to the administrator and the MCP client.
2. Protected resources: money, personal data, credentials and keys, site or server control.
3. Entry surfaces: a table of surface, `file:line`, the authentication it expects and the principal who reaches it.
4. Trust boundaries and the strongest source-visible control on each.
5. What depends on a deployment fact not in the repository.
6. The selected profiles: the card's `Security profile:` line; `website.md` for a Phase 8 site; and every other profile whose surface class is present even though it is not the primary type. A WordPress plugin exposing MCP abilities also gets `mcp-server.md`, per SKILL.md "Security routing", and where profiles conflict the stricter rule wins.

## Step 2 — Coverage plan: the profiles become hunting modules

Every `##` section of each selected profile is a hunting module, with two exceptions:

- **"Verify with"** is the hunters' toolbox for that profile.
- **"Deliberate omissions"** is the known-omission filter used by the candidate gate.

A profile's "Phase test points" are folded into the section they belong to as concrete assertions. In `wordpress.md`, for example, the modules are Input / output, AuthZ / AuthN, MCP / OAuth, Secrets & data, Files & execution, Common WP pitfalls and Plugin-platform specifics.

A **unit** is one module crossed with the entry surfaces it applies to, split further where one pairing is too large for one reader (per subsystem, per route group). Add one more module that no profile carries, **Declared controls**: one unit per `IN PLACE` row of `docs/threat-model.md`, checking that the control exists in the code and holds. "Declared is not delivered", audited.

`coverage.md` is one table: `| Unit | Surfaces | Module (profile#section) | Starting paths | Status | Owner | Reviewed paths | Result |`. Every unit ends in exactly one status:

- `covered`: paths were reviewed and no candidate survived the hunter's gate.
- `candidate`: it produced one or more candidates.
- `blocked`: a fact is missing, and the table names it.
- `n/a`: with the reason, for example "no file handling exists".
- `deferred`: with the reason.
- `out_of_scope`: scoped runs only.

A unit with no reviewed paths is not `covered`. The table is the coverage claim; a sentence such as "auth was reviewed" is not.

**Scope.** `full` is the default. `scoped` covers named paths or the diff since a previous run's commit. It seeds units only for what is in scope, marks the rest `out_of_scope` and says it is a partial pass wherever it is reported.

## Step 3 — Hunting: find violations, do not tick boxes

One hunter per unit, or per small group of units in one subsystem. Hunters are **reading** verifiers under `references/assistant-config.md` "Parallel fan-out", so they go out in one parallel block. Any hunter that executes a check in the playground takes the environment alone, one at a time. Each hunter receives, in this order:

1. `recon.md`, verbatim.
2. Its units with their surfaces and starting paths.
3. The full text of its profile section(s), with the matching "Phase test points" and "Verify with" lines. Section names alone are not enough.
4. The threat model's "Not defended" table.
5. The method, the gate and the output contract below.

**The hunting method (in every hunter prompt):**

> You are hunting for places where this project violates the rules below, not confirming that it follows them. For every rule, find every place it applies, then try to break it: name the lower-trust principal and what it can send; locate the control that should reject, bind or limit it; trace the path from that input to the sink (query, render, file write, remote call, state change, money movement). Read the siblings that produce the same effect: the `nopriv` twin of an AJAX handler, the REST route beside the admin form, the bulk action, the CLI command, the cron job, the import, the uninstall, the retry and the error path. Check equivalence, not presence: a nonce checked in one handler and not its twin is a finding. Try the sad paths the interface accepts: empty, zero, negative, oversized, duplicated, another user's ID, a stale or revoked token, a replayed notification. When one root cause appears, search your own units for its variants. Stop a line of investigation as soon as it is settled either way and record the result. If you execute anything, do it only in the playground, with seed data, and stop at the smallest observable effect.

**The candidate gate (in every hunter prompt):**

> A candidate names the principal, the input, the control that should have stopped it, the boundary crossed, the affected resource and the concrete result, each backed by `file:line`. A missing best practice with no affected principal is a hardening note, not a candidate. An omission recorded in the threat model's "Not defended" table is a decision, not a finding, unless the source shows a worse consequence than the table states; then it IS a candidate, and the understated row is the finding. Do not inflate: a crash is not code execution, and a user acting on their own data is not privilege escalation. If a decisive fact is outside the source and the playground, propose `needs_validation` with that exact fact.

**The hunter's output: one JSON object and nothing else:**

```json
{
  "units": [{"unit": "U-04", "disposition": "covered|candidate|blocked",
             "reviewed_paths": ["includes/class-rest.php"], "blocker": null}],
  "candidates": [{"title": "", "category": "wordpress.md#AuthZ / AuthN",
                  "file": "includes/class-rest.php", "line": 112,
                  "trace": ["includes/class-rest.php:40", "includes/class-rest.php:112"],
                  "claim": "one sentence: principal → input → control missed → result",
                  "proposed_status": "confirmed|needs_validation",
                  "proposed_severity": "high", "blocker": null}],
  "hardening": ["concrete non-finding note with file:line"],
  "uncovered": [{"surface": "", "why": "a different boundary met on the way"}]
}
```

The session merges results into `coverage.md` and turns each `uncovered` entry into a new unit. Then one **coverage check** runs: a fresh reader receives only `recon.md` and `coverage.md` and lists surfaces with no unit, units closed without reviewed paths, and profile sections nobody took. The gaps it finds that the session accepts get one more hunting round. Anything still open after that round is `deferred` with the reason and is named in the report. Coverage is never claimed silently.

## Step 4 — Independent validation: a second agent tries to refute each candidate

First merge duplicates: the same root cause reached from two surfaces is one candidate carrying the strongest trace. Then every candidate goes to a **fresh verifier that did not hunt it and never sees the hunter's reasoning**. The verifier receives only:

- the candidate card: title, category, file, line, trace and the one-sentence claim;
- the recon facts needed to read the path;
- the profile section text;
- the instructions below.

It never receives the hunter's narrative or another verifier's conclusion.

> You did not write this candidate. Try to refute it. Re-read every cited line from disk. Reconstruct the strongest control on the path, including the ones frameworks provide that a hunter overlooks: a REST `permission_callback`, a capability check in the caller, schema `sanitize_callback`/`validate_callback`, prepared statements, auto-escaping templates, middleware, a gateway's signature verification. If the result can be reproduced in the playground safely, reproduce it and record the command and the observed output. Decide `confirmed` (the path and result are established; give severity, the smallest source fix and the regression test that would have caught it), `needs_validation` (a specific fact outside source and playground is decisive; name it and the owner-observed check that settles it) or `rejected` (source, a control, an impossible precondition or the absence of real impact refutes it; say which). Promote a proposed `needs_validation` to `confirmed` only if you established the path and the result yourself. `needs_validation` is not a parking place for a speculative idea.

**Dispatch** follows the fallback chain in `references/assistant-config.md` ("Parallel fan-out"): workflow → a parallel block of subagents, one per candidate → inline and serial. **Inline** is allowed only where the environment has no subagents. It is disclosed, never hidden:

- Before verifying anything, the session writes every candidate card into `findings.json`. It then verifies from the card and from a fresh read of the disk, never from what it remembers of the hunt, and in file order rather than discovery order.
- Each record carries `verified_by: inline`.
- The first line of `SECURITY-AUDIT.md` states that hunter and verifier were the same session, so independence is reduced.

Where subagents exist, a `confirmed` verdict reached inline is not acceptable.

**Severity, only for `confirmed`, and never above the demonstrated impact:**

- **critical**: an unauthenticated actor gets code execution, reads the whole data store, takes over any account or the site, or forges a payment result that the product acts on.
- **high**: a real control is fully defeated with real consequences. Examples: an authentication bypass on a meaningful action, a customer reading other customers' orders or personal data, stored script execution reaching an administrator, an MCP tool acting with more authority than its caller.
- **medium**: a real boundary violation with a narrow blast radius or uncommon preconditions. Example: a CSRF on a setting that needs a logged-in administrator to follow a link.
- **low**: disclosure of non-secret internals, or an effect that needs sustained effort for little gain.
- **info**: confirmed but minimal on its own, useful mainly as a step in a larger chain.

The discriminator between high and medium: does the result *fully defeat* an explicit control on an action with real consequences, or only weaken it? If the damage cannot be stated concretely, the severity is lower than it feels.

## Step 5 — `findings.json`

Deliberately small: what Keel needs to report, fix and re-run, and nothing more.

```json
{
  "schema": "keel.security-findings/1",
  "commit": "<audited sha>", "dirty": false, "date": "YYYY-MM-DD",
  "scope": "full",
  "profiles": ["references/security/wordpress.md", "references/security/mcp-server.md"],
  "verification": "subagent|inline|mixed",
  "findings": [{
    "id": "SA-01",
    "status": "confirmed|needs_validation|rejected",
    "severity": "critical|high|medium|low|info|null",
    "category": "wordpress.md#AuthZ / AuthN",
    "file": "includes/class-rest.php", "line": 112,
    "title": "", "description": "principal → input → control missed → result",
    "trace": ["includes/class-rest.php:40", "includes/class-rest.php:112"],
    "fix": "confirmed only: smallest source change + the regression test",
    "blocker": "needs_validation only: the missing fact + the owner check",
    "reason": "rejected only: what refutes it",
    "verified_by": "subagent|inline"
  }]
}
```

The invariants are mechanical, so they are checked mechanically before the report is written, never by eye:

- `severity` and `fix` are present if and only if the status is `confirmed`;
- `blocker` is present only on `needs_validation`, and `reason` only on `rejected`;
- every `file` is repository-relative and exists at the audited commit;
- ids are unique.

A ten-line `python3` or `jq` check run by the session does this; a failure is fixed in the JSON, not in the report. Rejected records stay in the file so a later run does not raise the same refuted claim again unless the source under it has changed.

## Step 6 — `SECURITY-AUDIT.md`: derived only from the records

Written last, only from `findings.json` and `coverage.md`, and it never changes a verdict, a severity or a blocker.

1. **Header:** audited commit, date, scope, profiles, verification mode (with the inline notice where it applies), coverage counts (covered / blocked / deferred / n/a / out of scope), and what the audit did not do: no production, no deployment facts, no load testing.
2. **Posture** in two or three sentences.
3. **Confirmed findings, grouped by severity** from critical to info. First a table (severity, id, title, boundary, one-line result). Then, for each finding: location, principal, the bounded reproduction in the playground, the observed result, impact, the smallest fix and the regression test.
4. **Needs validation: your call.** A separate table of id, title, trace, the exact blocker and the owner check that settles it. There is no severity, and none of these is called a vulnerability. The user decides each one: investigate, accept or dismiss.
5. **Hardening notes**, labelled as not findings.
6. **Rejected:** the count only. The details stay in `findings.json`.

Zero confirmed findings is a valid result. State it together with the coverage limits and never pad the report with low-severity filler.

## After the report — what the session does

- **Tell the user in the conversation:** counts by severity, the `needs_validation` list, and the local path of the report. Never paste the details into anything committed or public.
- **Every confirmed finding becomes a slice** with a neutral title. On a released product, critical and high take the hotfix path (`references/maintenance.md`), and every fix starts from **a test that reproduces the finding and fails** (the bug-fix rule in `references/test-automation.md`).
- **The `needs_validation` decisions are asked as one batch.** An accepted risk goes into the threat model's "Not defended" table with its D-entry, and in a public repository the user is told that this row is public.
- **`docs/threat-model.md` is corrected.** A control marked `IN PLACE` that the audit found missing or broken goes back to `TO BUILD` with the slice that will build it, in the same commit as the log row.
- **The log row in `docs/security-audit.md` is committed**, with counts only while findings are open.
- **A later run** reads the previous run's `findings.json` where it still exists on this machine. It re-checks open confirmed findings first and does not re-raise a rejected claim over unchanged source. Where no previous run exists locally, the report says so.

## The Phase 7 gate (card `Security audit: required`)

The gate passes when all of these hold, recorded in `docs/07-release.md`:

1. **A run covers the candidate.** Either a full run was made at the candidate commit, or a full run was made earlier in this release cycle and a scoped run covers the diff from its commit to the candidate. That diff counts as code whenever it touches anything outside `docs/`.
2. **No confirmed finding is open.** Each one is either fixed, with its verifier re-run against the candidate and returning `rejected` (the refuted claim is now the evidence), or accepted by a D-entry and moved to "Not defended".
3. **Every `needs_validation` item is resolved or explicitly acknowledged by the user.**
4. **The log row exists.**

`declined`: the gate prints one line naming the D-entry. `optional`: the audit is offered in one line and the release continues either way.

## Definition of done (per run)

- It was a slice before it started, and its hours are recorded when it closes.
- `docs/security-audit/` is gitignored before the first file is written, and the run's four files exist.
- Every unit in `coverage.md` has a status, and no unit is `covered` without reviewed paths. The coverage check ran, and its gaps are closed or `deferred` with a reason.
- Every candidate was decided by a verifier that did not hunt it, or `verified_by: inline` is disclosed where no subagents exist.
- The `findings.json` invariants passed a mechanical check. `SECURITY-AUDIT.md` reports only `confirmed` as findings and lists `needs_validation` separately.
- Confirmed findings are slices. `needs_validation` items were put to the user. The threat model is corrected. The log row is committed and no open finding is described in it.
