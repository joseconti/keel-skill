---
schema: keel.sprint/1
sprint: 1
goal: Keel v6.0.0 — measured session time, and tests scoped to the change at push
status: in-progress
slices:
  - id: S-001
    title: Session time ledger — wall-clock start/end, planned vs done, deviation per session
    status: done
    hours: 1.5
    actual_hours: 0.07
    actual_source: measured
    depends_on: []
    criteria: []
  - id: S-002
    title: Tests scoped to the change before every push; the full suite only at a release
    status: done
    hours: 1.5
    actual_hours: 0.02
    actual_source: measured
    depends_on: []
    criteria: []
  - id: S-003
    title: Release v6.0.0 — manifest, changelog, anti-patterns, evals, version sync, lint, publish
    status: in-progress
    hours: 1
    actual_hours: 0.07
    actual_source: measured
    depends_on: [S-001, S-002]
    criteria: []
---

# Sprint 1 — Keel v6.0.0

- Acceptance: both rules are in the skill with their scripts' contracts, their `keel-verify` checks,
  their Table 1/Table 3 rows and an eval each; `python3 tests/lint-release.py` passes; the release is
  published.
- Notes: first sprint of this repository's own plan (the open item carried from v5.21.0, D-026). The
  repository has no plan generator, so `docs/.keel/plan.json` is not produced here — recorded in
  `docs/PROGRESS.md` deferred items. Raw clock events are in the gitignored `docs/.keel/clock.jsonl`, read
  with `date -u`; the committed record is `docs/sessions.md`.
- Timing note: the phase-5 test-selection edits were written inside S-001's interval, so the split
  between S-001 and S-002 is approximate; the session total read from the clock is exact.
- Close-out (session 1): S-001 and S-002 done; S-003 blocked — PR #14 (develop → main) and the
  v6.0.0 tag/release need the user: the merge hook and the permission classifier refused both.
