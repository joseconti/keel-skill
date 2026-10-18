# Parallel development

Use this reference when an approved sprint contains work that may run concurrently. It is the authoritative contract for development workers, scheduling, results, integration and recovery. Read-only verifier fan-out remains in `references/assistant-config.md`.

## Policy and capability gate

The project card records `Parallel development: auto; max_workers: max` or `Parallel development: off`. `max` is the default and the intended setting: development runs as many writing workers at once as the session can really sustain — 2, 4, 6, 8 or more — because the point of parallel development is to finish the sprint as fast as possible. A fixed number (`max_workers: 4`) is only an explicit ceiling the user asked for, recorded in a D-entry; Keel never proposes or writes a small fixed number as a default. A card carrying `max_workers: 2` without a D-entry choosing it is the old v7.x default, not a decision: migrate it to `max` and say so in one line. Settle this once in the normal setup/reconciliation batch before launching paid or writing workers. `Autonomy: automatic`, chaining and acceptance of reviewer agents do not imply consent. An explicit existing fan-out decision migrates to `auto`; otherwise ask once. The approved sprint plan states the effective mode and cap.

At every kickoff probe the current session without launching paid agents merely to test availability:

1. Use a native worker API when it supports writing delegation, lifecycle/results are observable and each writer can be bound to an assigned Git worktree.
2. Otherwise use an accepted assistant CLI only when its unattended worker adapter has been verified on this machine: explicit cwd, project restrictions, model selection, process observation and cancellation.
3. Otherwise develop serially and record the exact missing capability. Read-only reviewers may still run in parallel.

In Claude Code, the native worker API includes agent teams, which stay off unless `CLAUDE_CODE_EXPERIMENTAL_AGENTS_TEAMS` is `"1"` when the session starts. Keel always merges that key into `.claude/settings.local.json` when Claude Code is in use (`references/keel-maintenance.md`, "Agent teams flag"). The flag only makes agent teams available; it does not verify them. Probe them like any other backend, and remember that a session started before the key was written does not have them.

Capabilities are observed runtime facts, never inferred from an assistant's name. Project agent definition files and runtime delegation are separate facts. A verified continuation launcher is not a verified worker launcher. Never use permission bypass. Do not invent vendor flags: inspect the installed CLI help and current official documentation, and leave an untested adapter unavailable.

`max_workers` caps writing attempts. At every kickoff resolve the effective cap to the LARGEST number of concurrent writers that the real limits allow, and pass that integer to `init --max-workers`. The limits, and the only things that may lower it: the session's total agent budget after reserving the coordinator and any reviewer slots; the chosen backend's own concurrency limit; the user's explicit ceiling when the card records one; and the machine's memory and CPU for that many writing agents. The number of ready slices is not a limit on the cap: the rolling scheduler fills every free slot as soon as work becomes ready. State the resolved cap and the limit that set it in the sprint plan (e.g. `effective cap: 6 — session agent budget`). Never settle for a lower cap out of caution or habit; a limit that is not observed does not reduce it. Reviewers borrow only genuinely free capacity; the helper does not count external native-agent tools. A worker never spawns children unless the coordinator assigned capacity. Test suites never lower the cap, because workers never run them ("Testing: one full verification per batch").

## Sprint plan version 2

Parallel-capable active sprints use `schema: keel.sprint/2`. Readers retain `keel.sprint/1` compatibility. Version 2 preserves every existing scope and estimate field and adds this mapping to each slice:

```yaml
execution:
  write_paths: [src/export/, tests/export/, docs/api/export.md]
  contracts:
    reads: [export-format-v1]
    writes: []
  exclusive_resources: [test-db-default]
  parallel: eligible
  serial_reason: null
```

`write_paths` contains repository-relative exact files or directory prefixes ending in `/`; no globs. Include generated output, fixtures and test scaffolding. Resolve symlinks before writing and reject anything outside the assigned worktree. `contracts` models semantic coupling that filenames cannot show. A contract writer excludes readers and other writers until integration and input revalidation. `exclusive_resources` names shared mutable environments such as a database, port, browser or simulator. `parallel` is `eligible` or `serial`; a serial slice names its reason.

Missing execution metadata means unknown, never eligible. Migrate only the active sprint on first use; preserve IDs, approved estimates, residual scope and history. Completed legacy prerequisites remain readable without execution metadata. For a nested plan, exactly one sprint must be `in-progress`; the helper selects only that sprint. A flat `slices` plan represents the current approved sprint. Serial slices are coordinator-owned and are never dispatched by `claim`. The derived `docs/.keel/plan.json` carries the mapping under its versioned schema. It is generated from sprint files and never hand-edited.

`init` snapshots the approved plan and its initially completed prerequisites. A fingerprint binds scope,
dependencies, ownership and execution settings to that run. Accounting and status changes may update the
canonical plan during integration; they do not change the run's readiness snapshot. A scope/contract change
requires resolving active attempts and creating a new run from the regenerated plan. Never overwrite the
journal or a registered assignment to force a retry.

Before dispatch, `scripts/keel-parallel validate` rejects duplicate IDs, self-dependencies, cycles, unknown or dropped prerequisites, invalid paths, coordinator-owned paths and malformed execution mappings. Overlapping write paths are valid planned work but cannot be claimed simultaneously. A dependency is satisfied only by an integrated slice, or by a slice already committed as `done` before the run.

## Rolling scheduler

The ordinary project session is the coordinator. It operates a rolling queue within the approved current sprint:

1. Recompute ready work after every result and integration.
2. In approved sprint order, fill free slots with ready slices whose path, contract and resource claims do not conflict.
3. When a worker finishes or blocks, integrate or park it and fill the slot immediately. Do not wait for a batch.
4. A product question parks that slice and its dependants. Continue every independent ready slice.
5. Stop dispatching only when capacity is occupied, nothing eligible is ready, or all remaining work is blocked. Report which state applies.

The execution journal is gitignored at `docs/.keel/parallel/runs/<run-id>/`. The coordinator alone writes its run, assignment and event files atomically. Every retry has a new attempt ID. The mutex lives under the canonical Git common directory's `keel-parallel/` folder, keyed by integration ref, so every worktree locks the same inode. POSIX `flock` releases a dead process's lock; never unlink the lock file. A persistent owner registry prevents a second run from claiming work on that branch while the first retains claims. Preserve the registered journal until its claims are resolved. This is a local macOS/Linux mechanism, not a distributed lock or a Windows writing backend; without POSIX locking use serial development.

Execution states are `pending -> claimed -> launching -> running -> awaiting-result -> awaiting-review -> ready-to-integrate -> integrated`. `blocked`, `failed`, `cancelled` and `stuck` retain claims until a quiescent attempt is explicitly resolved; stopped workers never silently release resources. `resolve` records the reason and checks the owned process/group before releasing claims. Retries use new IDs, with a three-attempt limit per run. A crash in `launching` before PID registration needs explicit operator investigation: preserve the worktree and claims rather than guessing whether it launched. Sprint status remains `not-started`, `in-progress`, `done` or `dropped`.

## Coordinator and worker ownership

Every writer receives one branch and worktree created from a recorded integration-branch commit. Never switch branches inside another session's checkout. Only the coordinator merges, updates aggregate state and performs an authorized push. Workers never release, push, open issues, send notifications, launch continuation chats or answer product questions.

The coordinator owns all aggregate state:

- `docs/PROGRESS.md`, decisions, lessons, issues and continuation state.
- `docs/sprints/`, `docs/.keel/plan.json`, sessions, token ledger and test points.
- Shared indexes/maps such as `docs/api/INDEX.md`, technical/code maps, threat-model and playground inventories.
- Close/chain state, release metadata and central generated output.

Workers may edit assigned product code, tests and module-local documentation. They return proposed aggregate updates as structured `state_contributions`; the coordinator applies them once during integration. A shared document requiring judgment becomes a coordinator-owned slice.

Before launch, the coordinator creates `keel.worker-assignment/1` and places an immutable, gitignored copy inside the worktree. It records run, attempt and slice IDs; repository identity; real worktree path; branch; base commit; coordinator identity; permitted write paths; immutable inputs; criteria; check commands (`test_commands`: only the cheap checks below); allocated environment and deadline. Worker-aware scripts validate it against cwd, branch, repository and the coordinator registration. A bare role environment variable grants nothing.

A validated assignment routes the portability lock to worker entry before normal resume/setup. Generated worker-aware controls invoke `worker-check --run <absolute coordinator journal> --assignment <local assignment>` from the worker's actual cwd. It compares the immutable registration, Git identity and committed/staged/unstaged/untracked paths; a prompt or environment flag cannot replace this call. The worker reads its assignment and named immutable specifications, not the project's living state. It does not run project maintenance, reconciliation, sprint planning, `keel-close`, stop-hook queue enforcement, push or chaining. Worker timing stays in its result rather than editing the sprint. Confidential-data scanning and the assigned cheap checks remain separate mandatory controls: a passing role/scope check does not replace them. Normal sessions retain every existing global control.

Validate additions, modifications, deletions and both sides of renames. Stage explicit assigned paths. An out-of-scope change blocks integration and is named; it is never silently deleted. These guards detect mistakes but do not claim to sandbox a process with unrestricted filesystem access.

## Testing: one full verification per batch

Parallel writers exist to finish sooner. Ten workers each running the suite — a browser suite above all — run ten suites at once on one machine: memory and CPU saturate, everything slows down and sessions fail or stall, so the sprint ends later than serial work would. Development is parallel; testing is not.

- **Workers develop; they never run test suites.** No unit, integration or end-to-end suite, no Playwright or other browser, no simulator, no shared database or server. A worker writes the tests its acceptance criteria call for — writing them is part of the slice — and leaves running them to the coordinator. Its assignment's `test_commands` hold only cheap static checks scoped to its own `write_paths`: lint, syntax, type check, formatter. A check that starts a browser, a server or a full test runner is never assigned to a worker.
- **Integration runs cheap checks, not the suite.** Each slice's candidate passes `verify-integration` with the merge, ancestry, scope, confidential-data, plan and the same cheap checks over the combination. That is enough to integrate the slice and unlock its dependants.
- **One full verification per batch.** When no worker is in flight — the ready queue is drained, or every remaining slice is blocked — the coordinator runs the project's full verification ONCE on a clean checkout at the integration head: unit, integration, end-to-end, the test points of every integrated slice, `keel-verify`. It uses `scripts/keel-parallel verify-batch`, which refuses while any worker is in flight and records evidence bound to that exact commit and the slices it covers.
- **One test lane per machine.** `verify-integration` and `verify-batch` hold a per-repository test lock: a second coordinator check fails at once ("test lane busy") instead of running alongside. Never start a suite outside these commands while workers are running.
- **A failure is fixed, then the whole batch runs again.** The coordinator reads the failures and chooses the faster route: it fixes them itself on the integration branch when the fixes are small or interlinked (the usual case); when there are several independent and substantial fixes, it adds them to the sprint as fix slices with their write paths, initializes a new run from the regenerated plan and launches only those workers — still without suites. Either way, `verify-batch` runs again on the new head. Never re-run the suite once per fix.
- **The gate.** `scripts/keel-parallel status` reports `batch.state`: `verified`, `pending` (integrated work not yet covered, or the head moved), `failed` (the last batch at this head failed) or `nothing-integrated`. A sprint close, a merge onward from the integration branch and a release all require `verified`. Until then the slices are integrated but the sprint is not finished.

A slice that builds on an integrated but not yet batch-verified dependency can inherit its defect. That is accepted: the batch catches it, and the fix is local. When one slice has many dependants and its correctness is doubtful, the coordinator may run an intermediate `verify-batch` once the workers in flight have finished, before dispatching the dependants.

## Worker results and messages

Each attempt commits one report at `docs/.keel/slices/<run-id>/<slice-id>/<attempt-id>.json` with schema `keel.worker-result/1`:

- identity: run, attempt, slice, repository, worktree, branch and base commit;
- `code_commit`, then `outcome: ready|blocked|failed|cancelled`; a block includes `needs_user`;
- exact `changed_paths`, the assigned cheap checks (in `tests`) with command/exit/result/evidence, and review findings;
- `state_contributions` for test points, API index, decisions/questions, lessons, issues and maps;
- `timing` with `started_at` and `finished_at` (UTC `YYYY-MM-DDTHH:MM:SSZ`, observed by the worker), `paused_seconds` (the worker's own waits), `active_seconds` and `source`; available usage/cost or explicit unavailable values. The coordinator feeds `started_at`/`finished_at`/`paused_seconds` straight into the session clock (`keel-time slice-record`); a result without them cannot be measured and its slice's `actual_hours` is recorded `estimated`, said so.

`code_commit` is the direct single parent of the separate report commit, because a report cannot contain its own commit hash. This applies to blocked/failed reports too; for no code change use the base commit. After the report commit, publish an atomic completion envelope containing run, attempt, report path and report commit. A native result returns the same identifiers. Old numeric-only reports are history and never complete a current attempt.

The coordinator rejects mismatched identity, wrong ancestry, an unexpected branch head, a dirty worker tree, missing evidence, scope violations or a report commit that changed anything besides its report artifacts. Consume the tuple run/attempt/report commit idempotently. A stale signal or duplicate delivery cannot complete new work.

Native messages or per-worker progress artifacts use `progress`, `blocked`, `contract-change-request` and `ready`. Technical contract changes return to the coordinator and are recorded before affected work proceeds; product changes return to the user. Silence alone does not prove death. Never use transcript editing or `--resume` as a mailbox.

## CLI worker execution

`scripts/keel-parallel run-worker` consumes a validated assignment and an adapter-provided argv array, sets cwd directly, records the process and observes both exit and deadline. Shell interpolation is forbidden. Default deadline is 30 minutes and may be adjusted at kickoff for measured long work. Exit without a valid report is failure, not success.

Launch validation and process registration occur under the shared mutex. The durable `launching` state
prevents a second invocation from starting the same worker. Worker stdout/stderr go to the local log beside
the execution envelope, keeping the helper's stdout JSON-only. Process exit 0 is only transport success:
consume the committed result before review. A restart uses `reconcile`; an exited process without a report
becomes failed, while a possible surviving process group remains stuck. If process start identity cannot be
observed, retain claims conservatively when a PID might have been reused.

At deadline, stop its dependants and use only the verified backend cancellation mechanism for that registered worker. Preserve its worktree. If cancellation cannot be confirmed, retain all its path/resource claims and record a stuck worker; do not launch a replacement against them. Do not broadly kill processes or delete worktrees.

## Review and integration transaction

Integration is serial while workers continue. Review a fixed commit/diff, never a moving worktree. Any product change after review invalidates the affected verdict.

For each ready result:

1. Validate the assignment, report, branch, ownership, evidence and independent review. Record the integration head.
2. Prepare a merge in a coordinator-owned integration worktree and temporary branch, based on the current integration head. Preserve the worker branch/worktree.
3. Apply state contributions and update the plan within the same transaction. Keep the slice `in-progress`. Resolve behavioral/contract conflicts through the coordinator and repeat affected review/tests.
4. Commit the candidate. Run the integration checks — the cheap checks over the combination, never the full suite ("Testing: one full verification per batch"). Worker results alone never pass this gate. Use `verify-integration` on the separate clean candidate worktree to execute that command and generate evidence bound to its exact commit. Include the plan ancestry and confidential-data checks in that command.
5. When green, record the worker's own interval with `keel-time slice-record <id> --result <report> --status done` (never `slice-start` at dispatch: dispatch → integration includes queueing and review), then write `done`, residual zero, that measured worker effort, evidence and the regenerated plan in a bookkeeping commit. If product/test content changes, repeat the integration checks.
6. After the final bookkeeping commit, run `verify-integration` again so the evidence covers the exact candidate to promote. Promote only if the authoritative integration head still equals the recorded head; otherwise rebuild and reverify. Use a compare-and-swap ref update or equivalent checked coordinator operation. `record-integration --evidence <json>` checks the actual integration head, report/code/previous-head ancestry and the helper-generated passing evidence before making dependants ready. The helper never merges or promotes a branch itself. Push only under the existing authorization.
7. When no worker is in flight, run the batch verification ("Testing: one full verification per batch"). The sprint closes only on `batch.state: verified`.

Failure leaves the authoritative integration branch unchanged and preserves candidate and worker worktrees. Never weaken the plan ancestry guard for intermediate worker commits. On coordinator restart, reconcile journal state with live processes, worktree heads and integrated commits before launching. Never relaunch or merge the same attempt twice. Clean only completed, known artifacts and clean worktrees whose commits are retained.

## Timing

Report wall-clock session time, summed worker effort, coordinator review/integration time and available token usage separately. Overlapping worker effort is not elapsed time; coordinator waiting is not duplicate implementation effort. Scheduling never changes residual estimates. Do not claim a real-project speedup from a synthetic fixture.

The session clock is built for this (`references/project-state.md`, "Session time"): slice intervals overlap, each slice's `actual_hours` is its own worker's elapsed working time, the session report shows wall-clock and summed slice hours side by side with the maximum concurrency, and the remaining-time projection uses throughput — estimated hours finished per active wall-clock hour — whenever work runs in parallel, naming that basis. A clock that closes one slice when another opens cannot measure a parallel sprint: it charges each slice only the minutes until the coordinator's next boundary. The coordinator never `slice-start`s a dispatched slice; it records the worker's own interval at integration with `keel-time slice-record`. Coordinator-owned (serial) slices use `slice-start`/`slice-end` and may stay open while workers run.

## Helper interface

The canonical standard-library helper is `scripts/keel_parallel.py` in the installed skill; Phase 5 copies it as executable `scripts/keel-parallel` when policy is `auto`, Python 3.9+ and POSIX locking/process groups are available. Never install Python silently. Otherwise writing development is serial while native read-only review can remain parallel.

All commands emit JSON and return nonzero on invalid input:

- `init --plan <plan.json> --run <run.json> --run-id <id> --integration-ref <ref> --max-workers <n> [--repo <path>]`: validates the plan and creates a run bound to the canonical Git common directory plus integration ref.
- `validate --plan <plan.json>`: schema, DAG, paths and ownership; read-only.
- `ready --plan <plan.json> --run <run.json>`: ordered ready/waiting sets; read-only.
- `claim --plan <plan.json> --run <run.json> --assignment <json>`: atomic claim.
- `status --run <run.json>`: summarized states and `batch` (`state`, `head`, `unverified` slices, last batch); read-only.
- `record-result --plan <plan.json> --run <run.json> --assignment <json> --result <json>`: validated, idempotent result.
- `record-review --run <run.json> --attempt <id> --code-commit <sha> --verdict pass|fail --evidence <text>`: records the independent verdict; only `pass` reaches `ready-to-integrate`.
- `verify-integration --run <run.json> --attempt <id> --candidate <worktree> --previous-head <sha> --evidence <json> [--timeout <seconds>] -- <argv...>`: runs coordinator checks before promotion and records `keel.integration-evidence/1` for the exact candidate.
- `record-integration --run <run.json> --attempt <id> --commit <sha> --evidence <json>`: validates promoted ancestry and verified evidence before unlocking dependants.
- `verify-batch --run <run.json> --candidate <worktree> --evidence <json> [--timeout <seconds>] -- <argv...>`: runs the project's full verification once on a clean checkout at the integration head; refuses while any worker is in flight; appends `keel.batch-evidence/1` (commit, covered slices, pass/fail, log) to the run whether it passes or fails.
- `reconcile --plan <plan.json> --run <run.json>`: detects dead processes, stale/missing plan references and current readiness.
- `run-worker --plan <plan.json> --run <run.json> --assignment <json> --envelope <json> -- <argv...>`: registered-attempt, explicit-cwd bounded process adapter. It calls no model itself.
- `worker-check --run <run.json> --assignment <json>`: read-only role/identity/scope guard, invoked inside the actual worker checkout by generated controls.
- `resolve --run <run.json> --attempt <id> --evidence <text>`: explicitly releases a stopped failed/blocked/cancelled attempt's claims for bounded retry; refuses possible live workers/groups.

The coordinator creates `keel.parallel-run/1` with a unique run ID, plan path, integration ref, cap, empty attempts/integrated maps and events. Mutation commands lock and atomically replace the run file. This helper validates/records; it does not authorize, plan product scope, merge, push, install or call agent services.

## Recovery and completion checks

Verification covers: rolling A/B/C scheduling; batch verification only after every worker is quiescent, a single test lane, failed-batch state until a verified fix; cycles and missing dependencies; path/contract/resource conflicts; symlink/path escape; total capacity; wrong cwd/branch; aggregate edits; worker-specific hooks without global bypass; early exit/deadline/cancellation; stale/duplicate reports; user blocks with independent progress; combined integration failures; moving integration head; coordinator restart; timing attribution; serial fallback; installation/archive packaging and paths containing spaces.

A backend is supported only after a disposable-repository smoke run proves a real writing worker, explicit worktree, valid report, review and integration. Record backend/version and evidence. Deterministic fake-process tests never establish backend support.
