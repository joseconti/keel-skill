# Keel v7.1.0 — release candidate

Prepared on 2026-10-07 from the working tree on `develop`, based on commit
`d2868c4`. The candidate is committed locally on `develop`; publication remains pending.

## Release notes

Static-analysis evidence now distinguishes passing analysis, code findings and
environment failures. A tool that cannot start analysis must retain its command,
exit status, failure output and affected scope. Alternate diagnostic runs remain
separate, with equivalence documented before they can satisfy a required check.
The release checklist applies the same evidence requirements.

Version metadata, changelog, manifest and portability-lock stamp are synchronized
to 7.1.0. Existing projects apply the evidence rule at their next test point;
there are no new required project files or card fields.

## Verification

- `python3 -B -m unittest discover -s tests -p 'test_parallel*.py' -v`: 32 tests passed.
- `python3 tests/lint-release.py`: all checks passed.
- `git diff --check`: passed.
- `unzip -t dist/keel-v7.1.0.zip`: all entries passed integrity checking.
- The archive contains only `keel/`: 44 files, including LICENSE, NOTICE and the
  executable helper. File contents match the working tree byte for byte.

Artifact: `dist/keel-v7.1.0.zip` (ignored build output).

SHA-256: `1c6dde906fca57f64abd09b30d5122794878501b13280d50e7f12870caea421d`.

## Evidence boundaries and publication

This repository contains no PHPStan installation or affected PHP project. The
reported socket incident has not been reproduced here; this release changes
Keel's instructions for handling such evidence. The linter checks the presence of
the instruction contract, not model compliance or PHPStan behavior.

Real writing-backend and generated-hook acceptance from v7.0.0 remains pending
as documented in `docs/parallel-development-review.md`. The fixture suite does
not establish that acceptance; capability-gated serial fallback still applies.

Publication remains pending: merge the reviewed candidate to `main`, and
tag `v7.1.0` when authorized. The existing tag workflow publishes changelog notes
and GitHub source archives; it does not attach this locally prepared skill ZIP.
If distributing this ZIP, attach it explicitly and verify the published asset.
