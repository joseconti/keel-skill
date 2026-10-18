# Keel v7.3.2 — release candidate

Prepared on 2026-10-18 on `develop`, based on v7.3.1 (published 2026-10-17). Patch release:
it fixes a defect (D-041). The skill content is commit `72417ba`.

## Release notes

Parallel workers develop; the full suite runs once per batch. Every writing worker ran its own
tests — browser suites included — and the coordinator re-ran affected tests at every integration,
so many workers meant many suites at once: memory and CPU saturated and parallel sprints ran slower
than serial ones, or stalled. Workers now run only cheap static checks over their own paths, the
integration checks are cheap too, and the coordinator runs the full verification once, on the
integration head, when no worker is in flight (`scripts/keel-parallel verify-batch`). A
per-repository test lane never runs two suites at once. A failure is fixed by the coordinator, or by
fix slices relaunched as workers, and the batch runs again; a sprint closes only on a verified batch.
Existing projects apply `MANIFEST.md` Table 3, v7.3.2.

## Verification

- `python3 tests/lint-release.py`: all checks passed, including the new check 17.
- `python3 -B -m unittest discover -s tests -p 'test_*.py'`: 52 tests passed (5 new in
  `tests/test_parallel_development.py`: batch after integration, refusal while a worker is in
  flight, failed state until a verified fix, clean checkout at the head, single test lane).
- `git diff --check`: passed.
- `unzip -t dist/keel-v7.3.2.zip`: no errors. The archive is `git archive HEAD keel` at
  `c3f52a1`: 50 entries, `keel/` only.

Artifact: `dist/keel-v7.3.2.zip` (ignored build output).

SHA-256: `485a2a2a69bf4e65893b53a000eca2f3d04c4b14e8f4b2e6dbf7b5c583efebb1`.

## Evidence boundaries

The helper and its tests are executed. No real writing backend ran a batch in this repository;
projects apply the contract at their next dispatch through the reconciliation.

## Publication

Pending: PR `develop` → `main` (merged by the user), then tag `v7.3.2` on the merge commit and
`gh release create v7.3.2` by hand with the archive rebuilt from the tag (Actions is disabled).
