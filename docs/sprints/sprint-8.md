---
schema: keel.sprint/2
sprint: 8
goal: Chaining rests on an idle queue; every machine has a rebuild recipe
status: in-progress
slices:
  - id: S-013
    title: Idle-queue REST verdict and idle-link breaker (issue #30); mandatory docs/machine-recipe.md with standing check 4
    status: done
    original_hours: 1
    residual_hours: 0
    change_kind: added
    parent_slice: null
    owns: [idle-queue-rest, machine-recipe]
    estimate_changes: []
    actual_hours: 0.75
    actual_source: estimated
    depends_on: []
    waiting_on: null
    criteria: []
    execution:
      write_paths: [keel/, tests/, docs/]
      contracts:
        reads: [keel-chaining, machines-contract]
        writes: [keel-chaining, machine-recipe]
      exclusive_resources: [release-metadata]
      parallel: serial
      serial_reason: one contract change across project-state, the Parallels reference and the linter
---

# Sprint 8 — idle queue and machine recipe

- Origin: forge issue #30 (chaining loops on empty sessions when every slice waits on a person) and the
  user's request of 2026-11-10 that every machine be rebuildable from a recipe after a system reinstall.
- Scope: `Handover: idle`, slice `waiting_on`, `plan.json` queue counts, REST as a third verdict, the
  idle-link breaker, `exec claude` in the launch, chain-check row 7c; `docs/machine-recipe.md`, its
  keel-verify drift check, scaffold step, standing check 4, Table 1 row; anti-patterns 12aa/12ab;
  linter checks 18–19.
- Actual hours are estimated: the clock was not read at this session's start.
- Not done: version, CHANGELOG and Table 2/3 rows wait for the user's explicit version instruction.
