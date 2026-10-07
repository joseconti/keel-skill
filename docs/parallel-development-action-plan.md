# Keel parallel development implementation plan

Make approved, independent development slices run concurrently, with one coordinator owning scheduling and integration. Preserve Keel's quality gates, permission boundaries, resumability and release rules.

This is an implementation handoff, not an implemented feature or a new project decision. The current request authorizes review and this plan; a subsequent instruction to implement it authorizes the implementation described here. It does not authorize a version bump, release, changes to unrelated projects or global assistant settings.

## Baseline and review verdict

Reviewed on 2026-10-07 at commit `f2e18cb8bddae9b6b363001c70986e4344fa2307`, branch `develop`, skill version 6.6.0. `python3 tests/lint-release.py` passed. That result covers release/document consistency, not live parallel execution. `docs/PROGRESS.md` still describes 6.5.0; do not use its version or release position to overwrite the newer skill metadata. Reconcile the current working position from Git before implementation.

SOL's central conclusion is correct: Keel already describes parallel development, but its normal development path remains sequential and its parallel contract is incomplete. Keep and strengthen the existing worktree architecture rather than introducing a second director chat.

| Finding | Evidence in the current repository | Implementation consequence |
| --- | --- | --- |
| Parallel development is optional, while the general slice rule says to advance only after the current slice passes | `keel/references/phase-5-development.md`, “Fanning the sprint out over worktrees” and the final bullet of §2 | State explicitly that only dependent work waits; schedule approved independent slices whenever the project policy and runtime allow it |
| Capability discovery differs between verification and development | `assistant-config.md`, “Parallel fan-out” allows native agents; Phase 5 requires a CLI for development | Use one capability-based selection rule; native isolated workers do not require an external CLI |
| Tool names are used as capability assumptions | `assistant-config.md` says Codex checks run inline; this review session exposes native agent and messaging tools | Probe the current session; do not generalize this session's capabilities to every Codex installation or invent native config schemas |
| Only PROGRESS has explicit worker write protection | `project-state.md`, “The living state is written by the session that owns the MAIN tree”; Phase 5 §2 requires sprint, test-point and plan writes | Give all aggregate state one writer, with structured worker contributions |
| The worker entry contract conflicts with normal entry and close rules | Worker prompts forbid reading state; the portability lock requires reading it; timing writes sprint files; close and Stop hooks enforce global obligations | Add an explicit worker role with validated scope and role-aware entry, timing, verification and close behavior |
| The example launch does not set its working directory | `project-state.md`, “Dispatching a worker” | Set and verify process cwd mechanically; a worktree path in a prompt is not sufficient |
| The stated bounded wait has no bound in its example | `project-state.md`, “The close-out contract” | Track process exit and deadlines as well as completion reports |
| Reports distinguish only done and blocked | `project-state.md`, “The worker's report” | Distinguish execution outcome, review readiness and integration; identify run and attempt to reject stale reports |
| Existing plan validation is insufficient for scheduling | `project-state.md`, “The sprint plan” validates dependency references and sprint order, but does not specify cycle detection or resource claims | Validate a DAG, explicit write ownership and shared runtime resources |
| Integration and bookkeeping have a known unresolved interaction | `docs/decisions.md`, D-026 explicitly says the ancestry check was not tested against worktree merges | Test worker commits and integration transactions against the real generated hooks and verification rules |
| Native agents alone do not prove safe parallel writes | This session's agents share the directory by default | Require each writer to operate in its assigned worktree; otherwise use a verified CLI backend or serial development |

These are findings from the contracts, not measurements of another project's slowdown. A lack of overlapping filenames does not establish independence: shared interfaces, migrations, fixtures, generated assets and environments also count.

## Fixed design decisions for implementation

1. Use the ordinary project session as coordinator. Keep the existing rejection of a separate director chat and of transcript-based messaging.
2. Use a rolling queue within the approved current sprint. Fill available slots again whenever a task finishes, becomes blocked or is integrated. Do not wait for every worker in a batch. Cross-sprint speculative execution is outside this implementation.
3. A dependency is satisfied only when its slice is successfully integrated into the coordinator's authoritative integration branch. A worker's completed branch does not satisfy it. Independent work can continue while reviews and integration occur.
4. Every concurrent product writer gets one worktree and branch, created from a recorded commit of the integration branch. Read-only reviewers may share immutable inputs. Never switch branches in a checkout another agent uses.
5. Only the coordinator merges, updates aggregate state and performs any authorized push. Workers never release, push, launch continuation chats, open forge issues or send external notifications. They send requests and results to the coordinator.
6. Preserve current product/design approval gates. Parallelize work whose inputs and contracts are already settled. Do not use mocks to bypass an unresolved product decision; consumer and provider work can overlap only against a recorded interface contract.
7. Preserve one executing verifier per shared environment. Independent environments may run concurrently within the machine budget. A worktree is file isolation, not a security sandbox or database/browser isolation.
8. Keep implementation and verification scope appropriate to each slice. Affected tests remain the normal change gate; the complete suite remains the release gate or an explicit existing full-suite policy.
9. Use native agent messaging when actually available. Otherwise use per-worker structured progress/results. Messages can request coordination; they cannot silently change approved requirements or grant new permissions.
10. Make the scheduling, ownership and report checks executable. Keep tool-specific agent calls in verified adapters or the main session; do not embed a model service, daemon or new hosted dependency in Keel.

## Policy and capability selection

Add a project-card setting `Parallel development: auto; max_workers: 2`. `off` preserves serial development. The initial default of two writing workers is a conservative configuration, not a performance claim. The coordinator, workers and nested reviewers must all respect the environment's total agent cap and the machine's shared browser/test budget. Reviewers borrow free capacity; workers do not independently spawn unlimited children.

Honor any existing explicit opt-out or restriction. On existing projects, if prior acceptance of development fan-out is recorded, migrate that decision. If permission is unresolved, settle it once in the existing setup/reconciliation batch before launching paid external workers; do not infer consent from `Autonomy: automatic`, `Chaining:` or acceptance of reviewer agents. For a newly approved sprint, show the chosen execution mode and effective cap with its plan.

Probe capabilities per session, without launching paid agents merely to discover them:

1. Native worker API available, writing delegation permitted, assigned worktree reachable, lifecycle/results observable: native backend.
2. Otherwise, an accepted assistant CLI with verified unattended invocation, explicit cwd, inherited project restrictions, and process observation: CLI backend.
3. Otherwise, serial development with a specific recorded reason. Independent read-only checks may still use native agents.

These are runtime capabilities, not promises attached to product names. Preserve the existing rule against bypassing permissions. Consult the installed CLI help and current official documentation before adding vendor flags. Never send Claude flags to another tool. A documented but untested adapter stays unverified and cannot launch unattended writers.

## Plan and execution state

Keep approved scope in the existing sprint files and keep `docs/.keel/plan.json` derived. Do not turn a local execution journal into another scope authority.

Introduce `keel.sprint/2` for migrated sprint files, retaining a reader for `keel.sprint/1`. The new version adds a structured `execution` mapping; existing scope and estimate fields keep their meanings. The existing plan generator must carry this mapping into its derived output for the helper, without inventing or manually editing it there. Version any existing closed derived schema accordingly and retain legacy reading during migration.

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

`parallel` is `eligible` or `serial`. A serial slice needs a concrete reason. Paths are repository-relative exact files or directory prefixes ending in `/`; do not introduce ambiguous glob matching in the first implementation. Include generated outputs, fixtures and test scaffolding. Resolve symlinks and reject paths escaping the assigned worktree. Model shared semantic contracts in the plan, not only filenames: a contract change requires re-evaluation of active consumers before new dispatch.

For legacy slices with no execution mapping, treat eligibility as unknown and perform a scoped planning pass; never interpret missing ownership as permission to edit anything. Migrate only the active sprint initially. Do not renumber slices or rewrite their estimates.

Validate self-dependencies, cycles, unknown dependencies, references to deferred/dropped prerequisites and scope ownership. Completed prerequisites remain usable. Preserve existing dependency ordering by sprint. Reject invalid plans with exact offending IDs before any worker starts. Overlapping write paths are not necessarily an invalid plan: they prevent simultaneous claims and are serialized. Contract readers may overlap; a contract writer excludes other readers/writers until its change is integrated and their inputs are revalidated. This applies even when the filenames differ.

Use a gitignored coordinator journal under `docs/.keel/parallel/runs/<run-id>/` containing `run.json`, task assignments and events. The coordinator is its only writer. Each run has a unique ID; every retry has a new attempt ID. Atomic updates and a coordinator lock prevent two dispatchers assigning the same slice. Key that lock by the canonical Git common directory and target integration ref, so another worktree cannot start a second coordinator for the same branch; keep the existing per-checkout lane for checkout ownership. Recover a stale lock only after verifying its recorded owner is no longer live. This is a local coordination mechanism, not a distributed lock across machines. Keep recoverable committed summaries in the sprint and test-point records; never make a gitignored journal the only durable record of integrated work.

Keep sprint statuses compatible with the existing schema (`not-started`, `in-progress`, `done`, `dropped`). Track execution detail separately in the journal:

`pending -> running -> awaiting-review -> ready-to-integrate -> integrated`

Additional outcomes: `blocked`, `failed`, `cancelled`. A dependent slice is ready only when every prerequisite is integrated or was already committed as done before this run. Rejected review sends the attempt to a bounded repair stage under the existing three-failure rule, not directly to integrated. Dependency-blocked tasks carry the prerequisite ID; user-blocked tasks carry the question.

The coordinator recomputes ready work after every result and merge. Choose deterministically in approved sprint order among ready slices whose path/resource claims fit. Skip an unavailable claim and consider the next independent item. Do not pause the whole run for one user question. Stop dispatch when no eligible work or capacity remains; distinguish “waiting for live workers” from “all remaining work blocked”.

## Worker role and ownership

Create a worker assignment before launch. It records run/attempt/slice IDs, canonical repository identity, worktree real path, branch, base commit, coordinator identity, permitted write paths, inputs, acceptance criteria, test commands, environment allocation and deadline. The coordinator places an immutable, gitignored assignment copy in the worker's worktree before launch; worker-aware scripts validate it against the registered assignment. The worker reads the relevant immutable specs and recorded decisions supplied by the coordinator.

Update the canonical portability lock and SKILL entry routing so a validated worker assignment selects the worker path before normal project resume/setup. A worker must not run project-wide maintenance, reconciliation, sprint planning or chaining. Do not simply add a prompt that contradicts the lock. A bare environment variable saying “worker” is insufficient: scripts validate the registered assignment against cwd, branch, repository and attempt. Invalid identity fails closed for worker operations without modifying another checkout.

Aggregate paths owned by the coordinator include:

- `docs/PROGRESS.md`, `docs/decisions.md`, `docs/lessons-learned.md` and `docs/issues.md`.
- `docs/sprints/`, derived `docs/.keel/plan.json`, `docs/sessions.md`, `docs/token-ledger.md` and `docs/05-test-points.md`.
- Shared indices and maps, including `docs/api/INDEX.md`, the technical plan/code map and shared threat-model or playground inventories.
- Continuation, close-out and chain state, release metadata and central generated outputs.

Workers may modify their assigned source, tests and module-local documentation. They supply proposed aggregate updates as structured contributions in their report. The coordinator applies those contributions in the integration transaction. For a shared document whose content requires design judgment, schedule a coordinator-owned slice instead of letting multiple workers rewrite it.

Worker-aware hooks still enforce confidential-data checks, scoped tests and assignment ownership. They do not demand global sprint/progress writes, global queue completion, pushes or continuation files. `keel-time` records worker intervals locally and returns them to the coordinator rather than editing the sprint. Worker close commits assigned work and its report, then exits. It does not invoke the normal `keel-close` pipeline. A normal session must retain all existing checks; a generic global hook bypass is unacceptable.

Diff validation must include modifications, additions, deletions and both sides of renames. Workers stage explicit validated paths. Out-of-scope writes block integration and are reported; do not automatically delete them. These checks detect and contain accidental scope violations; they do not claim to sandbox a process with unrestricted filesystem access.

## Results and communication

Use one committed report per attempt at `docs/.keel/slices/<run-id>/<slice-id>/<attempt-id>.json`. Replace the ambiguous numeric-only example while accepting old reports only as historical data, never as current completion signals.

Required report fields:

- `schema: keel.worker-result/1`, `run_id`, `attempt_id`, `slice_id`.
- `repo_id`, `worktree`, `branch`, `base_commit`, `code_commit`.
- `outcome`: `ready`, `blocked`, `failed` or `cancelled`; `needs_user` is required for a user block.
- `changed_paths`, `tests` (command, exit code, result and evidence path), `review_findings`.
- `state_contributions` (test points, API index changes, decisions/questions, lessons, issue notes and code-map updates as applicable).
- `timing` (observed start/end, pause intervals, active seconds and measurement source); available usage/cost counters, or explicit unavailable values.

`code_commit` names the completed implementation commit before the separate report commit. The report cannot contain its own commit hash. A local completion envelope names the report commit, report path, run and attempt. Publish that envelope atomically only after committing the report; for native workers, return the same identifiers through the native result channel.

The coordinator verifies the report belongs to the current registered assignment, the report commit is on its branch, `code_commit` has the required ancestry, the intervening report commit changed only allowed report artifacts, the tree is clean, and the claimed paths/evidence exist. A stale signal, malformed report, duplicate delivery or unexpected branch head cannot mark a task done. Consume a successful result idempotently by run/attempt/report commit.

CLI workers run with explicit cwd and an argv array, not a shell-interpolated command string. Confirm their actual checkout before they write. Record a process handle/PID plus start identity; do not treat a reused PID as the worker. Observe exit as well as the completion envelope: an exited worker with no valid report is failed. Each assignment carries an explicit deadline; default 30 minutes, adjustable at kickoff for a measured long task. At expiry, stop dispatching its dependents, report the condition, and use the verified backend cancellation mechanism for that owned worker. Preserve its worktree and partial work. If cancellation cannot be confirmed, retain its locks and record a stuck worker; do not launch a replacement against the same resources.

Native messages or per-worker progress files can carry `progress`, `blocked`, `contract-change-request` and `ready`. Absence of progress alone is not proof of a dead worker. Technical contract changes are routed through the coordinator and recorded before affected tasks proceed. Product questions remain the user's decision. Never use `--resume` or transcript edits as a mailbox.

## Integration and recovery

Integration is serialized. Workers continue on their own snapshots while the coordinator reviews and integrates other tasks. Reviewers receive a fixed commit/diff; never review a worktree being edited. The coordinator must not reuse a reviewer verdict after changing the reviewed product diff without re-reviewing affected changes.

For each ready result:

1. Validate identity, ownership, required worker evidence and independent review. Record the current integration-branch head.
2. Prepare the merge in a coordinator-owned integration worktree and temporary branch. Preserve the branch/worktree of the worker. Use the current integration head, not the original run base.
3. Apply aggregate contributions and update the plan in the same integration transaction. Keep the canonical sprint slice in progress until integration verification succeeds. If conflicts alter behavior or contracts, resolve through the coordinator and repeat affected review/tests; do not auto-select one side.
4. Commit the candidate, run affected tests against the recorded previous integration head, and execute cross-module checks reached by the combined changes. Shared-runtime tests acquire their resource lock. Worker test results alone do not pass this gate.
5. On success, finalize `done`, residual zero, measured worker actuals, evidence and generated plan in a final bookkeeping commit. Run `keel-verify` on that committed candidate. Product/test trees must still match the tested candidate; if they changed, rerun the affected checks. Documentation/examples with executable implications receive their own appropriate verification.
6. Promote the validated candidate only if the integration head is still the recorded head. If it moved, rebuild and revalidate against the new head. Only now record `integrated` and release dependency readiness. Push only under the existing project authorization.

On failure, leave the authoritative integration branch unchanged and retain the candidate and worker worktrees for repair. The coordinator records the failure without marking the canonical slice done. Test the ancestry-based plan guard against this exact sequence; never weaken it globally merely to allow intermediate worker commits.

On coordinator interruption, stop new launches. On resume, reconcile the journal with actual processes, worktree heads and already integrated commits before dispatch. Never relaunch a still-live worker or merge the same attempt twice. Preserve partial work. Clean up only known, completed run artifacts and clean worktrees whose commits are retained; no blanket worktree deletion, force-reset or broad process killing.

Timing reports show both elapsed session time and summed worker effort. Do not add parallel worker hours and label that sum as elapsed duration, and do not count the coordinator's waiting interval as duplicate slice implementation effort. Keep existing residual estimates unchanged by scheduling. A critical-path ETA is deferred; the first implementation reports observed elapsed time, worker effort, integration/review time and available token usage without inventing a speedup.

## Implementation sequence and deliverables

Complete these tasks in order of dependency. A task is complete only when its listed acceptance checks pass. During implementation, use serial work until the new worker isolation and role behavior are actually verified; do not depend on the feature being built to protect its own initial changes.

### P1 Define the authoritative parallel contract

Create `keel/references/parallel-development.md` containing the policy, role, scheduler, report, ownership, integration and recovery contracts above. Route to it from `SKILL.md`, Phase 5 and `project-state.md`. Move detailed fan-out instructions out of `project-state.md`, preserving a short pointer and the historical rejected-design record. Avoid maintaining two competing specifications.

Update Phase 5's serial slice sentence to gate dependent work only, and make its kickoff produce the execution mapping and chosen parallel mode. Document the meaning of worker-ready versus integrated-done. Keep sprint-close and release gates intact.

Acceptance: a reader can determine when work may start, who writes each artifact and what makes a dependency complete without resolving contradictory instructions. Add behavioral scenarios for these decisions before changing the rest of the workflow.

### P2 Implement and test the deterministic helper

Ship a canonical standard-library Python helper at `keel/scripts/keel_parallel.py` and tests at `tests/test_parallel_development.py`. Projects copy it to `scripts/keel-parallel`; existing project generation handles the wrapper and records its source checksum. Python 3 is a prerequisite only for this implementation's parallel-development helper. Detect it; never install it silently. A project without it keeps serial development and can still parallelize native read-only reviews.

The helper owns schema/identity/path validation, DAG readiness, capacity/resource allocation, atomic journal transitions, attempt deduplication and result validation. Expose explicit commands `validate`, `ready`, `claim`, `status`, `record-result`, `record-integration` and `reconcile`. Commands consume the existing derived plan plus versioned run/assignment/result JSON; do not add a second YAML parser or editable plan. `ready`, `status` and `validate` are read-only; mutation commands acquire the coordinator lock and write atomically. All commands return machine-readable JSON and nonzero on invalid input; document the argument and output schemas in the reference and test them.

For CLI execution, add a `run-worker` command that consumes a validated assignment and a verified adapter-provided argv, sets cwd explicitly, observes exit/deadline and publishes execution outcome. Native calls remain the coordinator's own tool calls with the same validated assignment/result contract. No vendor agent API is guessed or hardcoded into the scheduler. The helper does not authorize actions, merge product branches, push, install software or call model services on its own.

Acceptance: unit and temporary-Git-fixture tests prove ready selection, duplicate claim rejection, path overlap handling, invalid-result rejection, bounded process observation and reconciliation. The implementation must not consist solely of prose or token/heading-matching tests.

### P3 Integrate worker roles with existing controls

Update `project-state.md` templates and generated-script contracts for the portability lock, timing, close, Stop hook, verifier, handoff and plan. Add the coordinator-owned state set and worker contribution handling. Update the Phase 5 scaffold to copy/configure the helper only when applicable and register the worker behavior in tools with verified hook support.

Acceptance: a worker can finish and commit a valid assigned slice without touching aggregate state or triggering a continuation chat; its secrets and ownership checks still run. An ordinary session still fails the original dirty-tree, missing-plan, stale-handoff and unpushed-work checks when applicable. The merge transaction passes the plan ancestry guard without exempting coordinator work.

### P4 Connect capability discovery and execution

Update `assistant-config.md` and Phase 1 §5a to use runtime capabilities for both native and CLI execution. Clarify that optional project-agent files and runtime delegation availability are separate facts. Reuse the existing tool registry where appropriate, but do not equate a verified interactive continuation launcher with a verified unattended worker launcher.

Add a verified worker entry per supported backend, with explicit cwd, settings inheritance, model selection from the project's recorded map, lifecycle observation and cancellation behavior. Start with the backend actually testable in the implementation environment. Other backend rows remain unavailable or unverified until tested. Native agents with no usable worktree isolation remain eligible for read-only work, not simultaneous product writes.

Acceptance: native writing capability works without an external CLI; a CLI-only environment uses its verified adapter; lack of both produces serial work with its exact reason. No tool-name-based blanket assertion remains. Project settings are copied only for the chosen tool, with no global configuration writes or permission bypass.

### P5 Implement coordinator scheduling and integration workflow

Wire kickoff, assignment, result collection, incremental dispatch, review and integration to the helper. Keep source claims through worker completion and any repair; release claims only after the attempt is quiescent and safely resolved. Shared environment claims may be acquired just for verification, so a browser queue does not prevent independent code authoring.

Update aggregate state from reports exactly once per integrated attempt. Keep all existing approval and external-message boundaries. Add the measured timing distinction to `estimation-budget.md` and the session reporting contract.

Acceptance: the integration fixture below completes A and B concurrently, starts C after A integrates even while B remains active, parks a blocked task and continues independent work. The coordinator never marks a worker branch done in the canonical sprint before successful integration.

### P6 Complete packaging and migration

Update `README.md`, `INSTALL.md`, `MANIFEST.md` Tables 1 and 2, the copy/update verification in `keel-maintenance.md`, adoption/reconciliation guidance and any skill-copy instructions that enumerate only Markdown files. The new `scripts/` tree must travel with the installed skill. Document `scripts/keel-parallel` as a conditional project artifact, created by the Phase 5 scaffold or active-sprint reconciliation, never as a universally required installed runtime.

Add the new reference to the `SKILL.md` reference index. Update the release linter for relevant packaging checks and temporary Python bytecode handling without weakening manifest parity. Extend the existing `.github/workflows/release.yml` lint job to run the deterministic helper tests, preserving its current branch/tag triggers and release permissions. Keep runtime journals, local signals and raw worker logs gitignored; keep worker result reports and canonical summaries tracked and covered by confidential-data checks. Exclude this repository-only implementation plan from release archives through `.gitattributes`.

No version bump or changelog entry is authorized by this plan. Keep the current version strings; list new manifest files under the current development baseline while implementation is unreleased. Keep the proposed reconciliation delta in the implementation handoff until a release version is explicitly authorized, then move it into Table 3 under that version. Do not invent a historical release entry. Reconcile this repository's stale current-position documentation to actual implementation work without claiming a release occurred.

Acceptance: clean-copy and archive fixtures retain the helper/reference, drop runtime debris, and work from paths with spaces. Existing serial projects continue without new runtime requirements. Migrating an active parallel project preserves slice IDs, approved estimates, decisions and historic worker reports.

## Required verification matrix

Automate deterministic tests using standard-library `unittest`, temporary directories and local Git repositories. Use fake worker processes for timing/failure tests; they must not consume paid model calls. Native/CLI smoke verification is a separate, small authorized test against a disposable repository with the actual backend. Record tested backend/version and distinguish untested adapters.

| Case | Required observable result |
| --- | --- |
| Independent A and B, with C depending only on A | A/B overlap; C starts after A integrates while a deliberately held B is still running; use synchronization barriers rather than timing guesses |
| Dependency cycle or missing prerequisite | Validation rejects exact slice IDs before creating workers |
| Different files but a shared mutable contract | Re-plan or serialize the contract change; no false independence claim |
| Same file, ancestor directory, rename or symlink escape | Overlap/escape detected; no conflicting assignment or integration |
| Shared database/browser | At most one holder; file-isolated workers still queue for that environment |
| All available slots used, nested review requested | Global cap respected; no oversubscription or deadlock waiting for a child slot held by its parent |
| Worker in wrong cwd or branch | Rejected before first write; coordinator tree remains unchanged |
| Worker aggregate-state edit | Integration rejected with the path named; no silent merge-union repair |
| Worker normal completion with hooks installed | No global close/push/chain and no forced aggregate edits; local secrets and scope guards still enforce |
| Ordinary session with the same hooks | Existing duties remain enforced; worker exemption cannot be selected with a bare flag |
| Worker exits before producing a report | Failed outcome, bounded wait, independent work continues |
| Worker deadline or cancellation | Only registered worker targeted; unconfirmed cancellation retains resource ownership; partial work preserved |
| Old run signal, duplicate report or unexpected extra commit | Rejected or idempotently ignored; cannot complete the current attempt |
| One task requires user input | Task and dependents parked; ready independent tasks continue |
| Individually passing changes fail together | Candidate rejected by integration tests; integration branch and done state unchanged |
| Integration branch moves during validation | Candidate rebuilt against new head; old evidence cannot directly promote it |
| Coordinator restarts before or after a merge | No duplicate worker, merge, effort accounting or state contribution |
| Two workers each active for one overlapping interval | Effort sums both; elapsed duration counts the interval once; pauses and retries retain correct attribution |
| No native workers, no verified CLI, Python absent or parallel off | Explicit serial fallback; normal workflow still works |
| Fresh install, embedded copy and release archive | Helper and reference included; no logs, live signals, bytecode or secrets included |

Run `python3 -B -m unittest discover -s tests -p 'test_parallel*.py'`, `python3 tests/lint-release.py` and `git diff --check`. The `-B` prevents test imports from adding bytecode to the packaged skill tree. Run existing relevant behavioral evals and add parallel scenarios to `tests/evals/scenarios.md`. A passing release linter alone never proves this feature.

## Completion and handoff

The implementation handoff must list changed files, supported and actually exercised backends, test evidence, remaining limitations, migration steps and observed concurrency. Show one trace of the A/B/C fixture with dispatch, review and integration transitions. Do not claim a real-project speedup from a synthetic timing test; a pilot can measure that later.

Work is complete when P1–P6 and the verification matrix pass for at least one real writing backend, serial fallback remains functional, no contradictory active worker instructions remain, and the exact result is ready for review. If no real backend can be exercised, deliver the tested deterministic pieces and explicitly mark backend acceptance incomplete; do not declare unattended parallel development verified.

Ready-to-paste instruction for the implementing model:

> Implement `docs/parallel-development-action-plan.md` in this repository. Read its baseline, fixed design decisions, P1–P6 tasks and acceptance matrix first, then inspect the current worktree and applicable repository instructions. Treat the plan's runtime contracts as the target, not as features that already exist. Preserve unrelated changes and existing user decisions. Complete and verify the implementation, including worker-role hooks, rolling dependency scheduling and post-merge checks. Do not bump versions, add a release changelog entry, tag, publish, modify other projects or change global assistant settings unless separately authorized. Report evidence and any unverified backend honestly.
