# Parallel development — pre-release correction and acceptance record

## Corrected defects

The initial 14-test suite passed while six material defects remained. The earlier completion claim was
incorrect. The follow-up review reproduced them in disposable repositories before changing the helper.

| Defect | Implemented correction | Regression evidence |
| --- | --- | --- |
| Two slices could claim one worktree/branch | Compare all live immutable assignments; reject checkout or branch reuse | `test_reject_two_claims_in_same_checkout` |
| Same-repository locks were stored in different checkouts | Shared POSIX flock inode under the canonical Git common directory; durable run-owner registry | `test_locks_are_shared_across_journal_directories`, `test_second_run_cannot_claim_while_first_holds_resources` |
| A fictitious integration commit unlocked dependants | Execute candidate checks, bind evidence to the candidate, verify actual branch head and ancestry before integration recording | `test_fake_integration_is_rejected`, `test_integration_evidence_must_cover_current_head_and_green_checks` |
| Another assignment could reuse a registered attempt ID | Store/compare the complete immutable assignment snapshot before launch or result acceptance | `test_substituted_assignment_cannot_change_another_attempt`, `test_changed_registered_assignment_rejected_before_launch` |
| Legacy completed prerequisites failed; future sprints were scheduled | Preserve historical scope, select only the approved active sprint, snapshot baseline completion and scope | `test_legacy_done_dependency_and_future_sprint`, `test_changed_scope_is_rejected_but_accounting_can_update` |
| Process started before acquiring the launch lock | Validate and register launch while holding the shared mutex; preserve uncertain attempts after interruption | `test_launch_under_held_lock_does_not_start_process`, `test_two_concurrent_launches_execute_the_worker_once` |

Additional checks cover new symlinks inside owned directories, real cwd and dirty aggregate-state rejection,
failed-review claim retention, explicit resolution, failed candidate tests without branch promotion, and
idempotent integration after reloading the journal.

## Observed A/B/C fixture

`test_dependency_rolling_queue_starts_c_after_a_integration_while_b_active` uses disposable Git worktrees
and actual Python worker processes, synchronized with explicit start/release files:

1. Claim A and B in separate worktrees at the integration base.
2. Start B; B announces its start and waits on a release barrier.
3. Start A while B remains alive; A writes its assigned file and commits code plus its report.
4. Accept A's report and record the fixture's review verdict.
5. Merge A into a separate candidate worktree; execute candidate verification and record its evidence.
6. Promote the verified candidate, record integration, and claim C from the new integration head.
7. Start C while B is still held. C's checkout contains A's integrated file.
8. Release B and wait for the owned process to exit.

This establishes local concurrency and dependency ordering. The fixture reviewer and workers are test
programs, not independent model agents, and the timing is not a real-project speedup measurement.

## Verification commands

```sh
python3 -B -m unittest discover -s tests -p 'test_parallel*.py' -v
python3 tests/lint-release.py
git diff --check
```

The suite contains 32 tests at this checkpoint. Git is mutated only inside disposable test repositories;
the project itself is left uncommitted for the user. The helper's supported local process/locking platform
is POSIX (macOS/Linux), Python 3.9+. Windows uses the documented serial fallback.

## Acceptance still required before enabling a real writing backend

No model backend has been launched or declared verified in this correction session. The earlier plan
explicitly allows delivery of tested deterministic pieces while reporting backend acceptance incomplete.
Do not convert this into a claim that all P1–P6 acceptance criteria passed.

For Astra or the session with an authorized isolated writing backend:

1. In a disposable project, verify that the actual native/CLI adapter binds each model worker to its
   assigned worktree and inherits project restrictions without bypass flags.
2. Generate the real project's timing/close/Stop/verifier controls. Wire their worker branch through
   `worker-check`, retaining the existing confidential-data and affected-test controls.
3. Observe a real worker committing its assignment and report without changing aggregate state or
   triggering push/continuation. Observe the same hooks rejecting invalid worker identity, secret/scope
   violations, and the ordinary session's original dirty-tree/plan/handoff/unpushed violations.
4. Run candidate verification including the actual generated plan ancestry check; exercise failure and
   interruption recovery; record adapter/version and observed evidence. Only then mark that backend
   verified and close the remaining sprint work.

No architecture choice is awaiting Astra. The outstanding item is execution evidence unavailable in this
session. Until it exists, retain capability-gated serial fallback for model writing. No tag or publication
is implied by this handoff.
