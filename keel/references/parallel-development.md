# Parallel development

Use this reference when an approved sprint contains work that may run concurrently. It is the authoritative contract for development workers, scheduling, results, integration and recovery. Read-only verifier fan-out remains in `references/assistant-config.md`.

## Policy and capability gate

The project card records `Parallel development: auto; max_workers: 2` or `Parallel development: off`. Settle this once in the normal setup/reconciliation batch before launching paid or writing workers. `Autonomy: automatic`, chaining and acceptance of reviewer agents do not imply consent. An explicit existing fan-out decision migrates to `auto`; otherwise ask once. The approved sprint plan states the effective mode and cap.

At every kickoff probe the current session without launching paid agents merely to test availability:

1. Use a native worker API when it supports writing delegation, lifecycle/results are observable and each writer can be bound to an assigned Git worktree.
2. Otherwise use an accepted assistant CLI only when its unattended worker adapter has been verified on this machine: explicit cwd, project restrictions, model selection, process observation and cancellation.
3. Otherwise develop serially and record the exact missing capability. Read-only reviewers may still run in parallel.

Capabilities are observed runtime facts, never inferred from an assistant's name. Project agent definition files and runtime delegation are separate facts. A verified continuation launcher is not a verified worker launcher. Never use permission bypass. Do not invent vendor flags: inspect the installed CLI help and current official documentation, and leave an untested adapter unavailable.

`max_workers` caps writing attempts. At kickoff reduce it to fit the session's total agent budget after reserving the coordinator and any reviewer slots. Reviewers borrow only genuinely free capacity; the helper does not count external native-agent tools. A worker never spawns children unless the coordinator assigned capacity. Shared browser/test-machine limits may lower the effective cap.

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

Before launch, the coordinator creates `keel.worker-assignment/1` and places an immutable, gitignored copy inside the worktree. It records run, attempt and slice IDs; repository identity; real worktree path; branch; base commit; coordinator identity; permitted write paths; immutable inputs; criteria; test commands; allocated environment and deadline. Worker-aware scripts validate it against cwd, branch, repository and the coordinator registration. A bare role environment variable grants nothing.

A validated assignment routes the portability lock to worker entry before normal resume/setup. Generated worker-aware controls invoke `worker-check --run <absolute coordinator journal> --assignment <local assignment>` from the worker's actual cwd. It compares the immutable registration, Git identity and committed/staged/unstaged/untracked paths; a prompt or environment flag cannot replace this call. The worker reads its assignment and named immutable specifications, not the project's living state. It does not run project maintenance, reconciliation, sprint planning, `keel-close`, stop-hook queue enforcement, push or chaining. Worker timing stays in its result rather than editing the sprint. Confidential-data scanning and scoped tests remain separate mandatory controls: a passing role/scope check does not replace them. Normal sessions retain every existing global control.

Validate additions, modifications, deletions and both sides of renames. Stage explicit assigned paths. An out-of-scope change blocks integration and is named; it is never silently deleted. These guards detect mistakes but do not claim to sandbox a process with unrestricted filesystem access.

## Worker results and messages

Each attempt commits one report at `docs/.keel/slices/<run-id>/<slice-id>/<attempt-id>.json` with schema `keel.worker-result/1`:

- identity: run, attempt, slice, repository, worktree, branch and base commit;
- `code_commit`, then `outcome: ready|blocked|failed|cancelled`; a block includes `needs_user`;
- exact `changed_paths`, tests with command/exit/result/evidence, and review findings;
- `state_contributions` for test points, API index, decisions/questions, lessons, issues and maps;
- timing with observed start/end, pauses, active seconds and source; available usage/cost or explicit unavailable values.

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
4. Commit the candidate. Run affected tests from the recorded previous integration head plus cross-module checks reached by the combination. Acquire shared resource locks. Worker results alone never pass this gate. Use `verify-integration` on the separate clean candidate worktree to execute the project's verification command and generate evidence bound to its exact commit. Include the plan ancestry and confidential-data checks in that command.
5. When green, write `done`, residual zero, measured worker effort, evidence and the regenerated plan in a bookkeeping commit. Run `keel-verify` on the committed candidate. If product/test content changes, repeat affected verification.
6. After the final bookkeeping commit, run `verify-integration` again so the evidence covers the exact candidate to promote. Promote only if the authoritative integration head still equals the recorded head; otherwise rebuild and reverify. Use a compare-and-swap ref update or equivalent checked coordinator operation. `record-integration --evidence <json>` checks the actual integration head, report/code/previous-head ancestry and the helper-generated passing evidence before making dependants ready. The helper never merges or promotes a branch itself. Push only under the existing authorization.

Failure leaves the authoritative integration branch unchanged and preserves candidate and worker worktrees. Never weaken the plan ancestry guard for intermediate worker commits. On coordinator restart, reconcile journal state with live processes, worktree heads and integrated commits before launching. Never relaunch or merge the same attempt twice. Clean only completed, known artifacts and clean worktrees whose commits are retained.

## Timing

Report wall-clock session time, summed worker effort, coordinator review/integration time and available token usage separately. Overlapping worker effort is not elapsed time; coordinator waiting is not duplicate implementation effort. Scheduling never changes residual estimates. Do not claim a real-project speedup from a synthetic fixture.

## Helper interface

The canonical standard-library helper is `scripts/keel_parallel.py` in the installed skill; Phase 5 copies it as executable `scripts/keel-parallel` when policy is `auto`, Python 3.9+ and POSIX locking/process groups are available. Never install Python silently. Otherwise writing development is serial while native read-only review can remain parallel.

All commands emit JSON and return nonzero on invalid input:

- `init --plan <plan.json> --run <run.json> --run-id <id> --integration-ref <ref> --max-workers <n> [--repo <path>]`: validates the plan and creates a run bound to the canonical Git common directory plus integration ref.
- `validate --plan <plan.json>`: schema, DAG, paths and ownership; read-only.
- `ready --plan <plan.json> --run <run.json>`: ordered ready/waiting sets; read-only.
- `claim --plan <plan.json> --run <run.json> --assignment <json>`: atomic claim.
- `status --run <run.json>`: summarized states; read-only.
- `record-result --plan <plan.json> --run <run.json> --assignment <json> --result <json>`: validated, idempotent result.
- `record-review --run <run.json> --attempt <id> --code-commit <sha> --verdict pass|fail --evidence <text>`: records the independent verdict; only `pass` reaches `ready-to-integrate`.
- `verify-integration --run <run.json> --attempt <id> --candidate <worktree> --previous-head <sha> --evidence <json> [--timeout <seconds>] -- <argv...>`: runs coordinator checks before promotion and records `keel.integration-evidence/1` for the exact candidate.
- `record-integration --run <run.json> --attempt <id> --commit <sha> --evidence <json>`: validates promoted ancestry and verified evidence before unlocking dependants.
- `reconcile --plan <plan.json> --run <run.json>`: detects dead processes, stale/missing plan references and current readiness.
- `run-worker --plan <plan.json> --run <run.json> --assignment <json> --envelope <json> -- <argv...>`: registered-attempt, explicit-cwd bounded process adapter. It calls no model itself.
- `worker-check --run <run.json> --assignment <json>`: read-only role/identity/scope guard, invoked inside the actual worker checkout by generated controls.
- `resolve --run <run.json> --attempt <id> --evidence <text>`: explicitly releases a stopped failed/blocked/cancelled attempt's claims for bounded retry; refuses possible live workers/groups.

The coordinator creates `keel.parallel-run/1` with a unique run ID, plan path, integration ref, cap, empty attempts/integrated maps and events. Mutation commands lock and atomically replace the run file. This helper validates/records; it does not authorize, plan product scope, merge, push, install or call agent services.

## Recovery and completion checks

Verification covers: rolling A/B/C scheduling; cycles and missing dependencies; path/contract/resource conflicts; symlink/path escape; total capacity; wrong cwd/branch; aggregate edits; worker-specific hooks without global bypass; early exit/deadline/cancellation; stale/duplicate reports; user blocks with independent progress; combined integration failures; moving integration head; coordinator restart; timing attribution; serial fallback; installation/archive packaging and paths containing spaces.

A backend is supported only after a disposable-repository smoke run proves a real writing worker, explicit worktree, valid report, review and integration. Record backend/version and evidence. Deterministic fake-process tests never establish backend support.
