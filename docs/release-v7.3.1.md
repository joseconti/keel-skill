# Keel v7.3.1 — release candidate

Prepared on 2026-10-17 on `develop`, based on v7.3.0 (published 2026-10-16). Patch release:
it fixes a defect (D-040). The skill content is commit `ee8a698`.

## Release notes

The session clock measures parallel development. `scripts/keel-time slice-start` closed every
other open slice before opening the new one, so with parallel writers each slice kept only the
minutes until the coordinator's next boundary: a real project measured 22 finished slices
estimated at 48.25 h as 2.92 h (−94 %) inside a 4.86 h session. Slice intervals now overlap,
`slice-end` closes only its own slice, single-writer projects keep an explicit exclusive mode,
and a worker's slice is recorded from the worker's own start and end (`slice-record`). The
session report shows wall-clock and summed slice hours apart, with maximum concurrency and
throughput, and the remaining-time projection uses throughput when work runs in parallel,
naming its basis. The arithmetic ships as `scripts/keel_clock.py` (copied to projects as
`scripts/keel-clock`). Existing projects apply `MANIFEST.md` Table 3, v7.3.1.

## Verification

- `python3 tests/lint-release.py`: all checks passed, including the new check 16.
- `python3 -B -m unittest discover -s tests -p 'test_*.py'`: 47 tests passed (15 new in
  `tests/test_session_clock.py`, among them the six-parallel-worker reproduction).
- `git diff --check`: passed.
- `unzip -t dist/keel-v7.3.1.zip`: no errors. The archive is `git archive HEAD keel` at
  `ee8a698`: 50 entries, `keel/` only.

Artifact: `dist/keel-v7.3.1.zip` (ignored build output).

SHA-256: `673b9a940326d5c2acf85aaa2876a2d0e2ba8dfb8f6974c8667e5666d5f040d9`.

## Evidence boundaries

The helper and its tests are executed. Whether a project's regenerated `scripts/keel-time`
follows the contract is checked by that project's reconciliation, not here; no downstream
project was regenerated in this repository.

## Publication

Pending: PR `develop` → `main`, tag `v7.3.1` on the merge commit, GitHub release by hand.
