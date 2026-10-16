---
schema: keel.sprint/2
sprint: 7
goal: The session clock measures parallel development
status: in-progress
slices:
  - id: S-012
    title: Concurrent slice intervals, wall-clock vs summed slice hours, throughput-based projection
    status: done
    original_hours: 3
    residual_hours: 0
    change_kind: added
    parent_slice: null
    owns: [session-clock-parallel]
    estimate_changes: []
    actual_hours: 0.103889
    actual_source: measured
    depends_on: []
    criteria: []
    execution:
      write_paths: [keel/, tests/, docs/, README.md, INSTALL.md]
      contracts:
        reads: [parallel-development-v1]
        writes: [keel-session-clock]
      exclusive_resources: [release-metadata]
      parallel: serial
      serial_reason: one contract change spread across the clock, the scheduler reference and the linter
---

# Sprint 7 — the session clock measures parallel development

- Origin: a downstream project (16 Oct 2026, Keel 7.3.0, `Parallel development: auto; max_workers: 6`)
  reported that `keel-time slice-start` closes every other open slice before opening the new one. With
  six writer agents, 22 finished slices estimated at 48.25 h were measured at 2.92 h (−94 %) against a
  4.86 h session wall-clock; the deviation and the pace projection were both wrong.
- Scope: concurrent slice intervals; per-slice hours from each slice's own intervals (worker elapsed
  working time when a worker did it); the report shows wall-clock and summed slice hours side by side;
  throughput (estimated hours finished per active wall-clock hour) drives the projection when work runs
  in parallel, with the basis stated; keel-verify and the stop hook accept overlap; a canonical,
  tested helper (`keel/scripts/keel_clock.py`) owns the arithmetic so no project re-derives it.
- Version: unchanged — the version, CHANGELOG and MANIFEST Table 3 migration row wait for the user's
  explicit instruction (version policy).
