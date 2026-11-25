# Keel v7.5.0

Ordered by the user on 2026-11-01 ("Publica a 7.5"), on `develop`, based on v7.4.0. Minor release (D-043).

## Release notes

Whoever creates something now removes it as soon as its use ends. The rule is a contract clause in
every project's lock block, and it covers worktrees and machines, Parallels and Docker alike. Machines
for specific tests are never accumulated. `keel-parallel sweep` is the safety net for sessions that
die before cleaning up. Existing projects apply `MANIFEST.md` Table 3, v7.5.0.

## Verification

- `python3 tests/lint-release.py`: all checks passed.
- `python3 -B -m unittest discover -s tests -p 'test_*.py'`: 68 tests passed.
- `sweep --apply` on this machine's real repositories: 5 clean worktrees retired from `new-gymai`, one
  of them under a dead process's lock, 0 failed, all 5 branches kept. `du` counted 2.1 GB; free space
  rose by about 1 GB, because cloned files share disk.
- `sweep-hook` run by hand: 0.04 s.

## Evidence boundaries

Docker reporting is tested with fakes only, because the daemon was stopped. The hook has not yet
started in a real session. Parallels leases were read from a real `prlctl`. By the user's decision, no
machine was deleted: each project decides on its own.

## Publication

Published on 2026-11-01. PR #29 merged `develop` into `main`; tag `v7.5.0` is on the merge commit
`8edd216`. GitHub Actions is disabled, so the release was created by hand with `gh release create
v7.5.0`, marked Latest, with `keel-v7.5.0.zip` attached, built from the tag (`git archive v7.5.0 keel`,
51 entries, no errors). SHA-256:
`96faa6426d8eec8c857d814b6a1973c782399a7004ff243430a14e52c5b5a419`.
