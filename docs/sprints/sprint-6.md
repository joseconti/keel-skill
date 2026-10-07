---
schema: keel.sprint/2
sprint: 6
goal: Keel v7.0.0 — safe rolling parallel development with isolated workers and serialized integration
status: in-progress
slices:
  - id: S-011
    title: Implement the approved parallel-development action plan and major-version migration
    status: in-progress
    original_hours: 3
    residual_hours: 1
    change_kind: added
    parent_slice: null
    owns: [parallel-development-v1]
    actual_hours: 2.5
    actual_source: estimated
    depends_on: []
    criteria: []
    execution:
      write_paths: [keel/, tests/, docs/, README.md, INSTALL.md, .github/, .gitignore, .gitattributes]
      contracts:
        reads: []
        writes: [keel-project-workflow]
      exclusive_resources: [release-metadata]
      parallel: serial
      serial_reason: bootstrapping the worker-isolation feature and updating coordinator-owned release state
---

# Sprint 6 — Keel v7.0.0

- Acceptance: local helper, contract, migration and packaging checks pass after the six review defects
  were corrected. P3/P4 acceptance with a real model backend and actual generated project hooks remains
  incomplete; do not mark P1–P6 collectively done on the strength of deterministic fixtures.
- Residual correction: reopened from zero to an estimated 1 hour for backend/hook acceptance. The original
  3-hour estimate and historical estimated actual are preserved. This is an explicit re-estimate of
  unverified work, not extra scope or a claim of newly measured effort.
- Origin: the user asked whether Keel could make independent development concurrent, asked Astra to
  validate SOL's conclusion and write an implementation plan, then explicitly instructed this session to
  apply the whole plan and make the result v7.0.0.
- Execution: deliberately serial. The plan forbids using the feature being built to protect its own
  bootstrap, and this session had no independently verified isolated writing backend.
- Timing: estimated because this source repository still has no `scripts/keel-time`; no measured clock
  interval covers the complete work. No synthetic test is presented as a measured speedup.
- Backend acceptance: the deterministic scheduler and fake-process/local-Git fixtures are verified. No
  real model writing backend was exercised, so unattended native/CLI writing remains explicitly
  unverified until a disposable-repository smoke run succeeds.
