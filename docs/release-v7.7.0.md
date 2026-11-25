# Keel v7.7.0

Ordered by the user on 2026-11-25 ("creamos la release", after v7.7.0 was proposed), on `develop`,
based on v7.6.0. Minor release (D-045, D-046).

## Release notes

Every project that writes PHP declares its PHP range on the card, asked at the start: 8.2 through 8.5
at minimum for code many sites run (wider welcome), the client's own version for one-client code.
Merged branches are deleted in the same session, and a pass at session start clears the ones earlier
sessions left. Pull requests opened by Dependabot and equivalents are retargeted to `develop` and
merged when green, checked at most once per 24 hours. In the same window a housekeeping pass deletes
what can be rebuilt (old Playwright browsers, oversized caches, old build artifacts) and reports what
the user must judge. Existing projects apply `MANIFEST.md` Table 3, v7.7.0.

## Verification

- `python3 tests/lint-release.py`: All checks passed. Releasable. New checks 20 and 21; check 21 was shown to fail
  when one of its promises is removed.
- `python3 -B -m unittest discover -s tests -p 'test_*.py'`: Ran 68 tests in 36.095s, OK.
- Applied to this repository: five merged local branches deleted, no bot PRs open, earlier release
  records moved to `docs/archive/releases/`.

## Evidence boundaries

The bot-PR sweep has not yet met a real Dependabot PR: none was open here. The housekeeping pass is
specified and linted; its first full run is this session's cleanup on the user's machine.
