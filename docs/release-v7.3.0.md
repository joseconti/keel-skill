# Keel v7.3.0 — release candidate

Prepared on 2026-10-16 on `develop`, based on v7.2.0 (published 2026-10-13). The skill
content is commit `113e166`.

## Release notes

Claude Code agent teams are always enabled. Whenever Claude Code is in use, the
session-start setup merges `env.CLAUDE_CODE_EXPERIMENTAL_AGENTS_TEAMS: "1"` into
`.claude/settings.local.json`, whatever the automatic-mode answer. The key grants no
permission; it takes effect at the next Claude Code start, and the parallel-development
kickoff probe still verifies the capability.

Parallel development runs as many workers as the session can sustain. The project card
default becomes `Parallel development: auto; max_workers: max`; each kickoff resolves the
effective cap to the largest number of writers the observed limits allow and records the
limit that set it. An undecided `max_workers: 2` from v7.x migrates to `max`.

The post-update reconciliation is mandatory: after every update it runs before any other
work, never offered or skipped. Every reconciliation from this version on runs two
standing checks that cannot be declined — the agent teams flag where Claude Code is used,
and `max_workers: max` unless the user chose a ceiling — and the baseline does not advance
until both pass.

Version metadata, changelog, manifest and portability-lock stamp are synchronized to
7.3.0. Existing projects apply `MANIFEST.md` Table 3, v7.3.0: no new file, no new card line.

## Verification

- `python3 -B tests/lint-release.py`: all checks passed, including the new checks 13, 14 and 15.
- `python3 -B -m unittest discover -s tests -p 'test_parallel*.py'`: 32 tests passed.
- `git diff --check`: passed.
- `unzip -t dist/keel-v7.3.0.zip`: no errors. The archive is `git archive HEAD keel` at
  `113e166`: 49 entries, `keel/` only.

Artifact: `dist/keel-v7.3.0.zip` (ignored build output).

SHA-256: `fa0a0525cee265c4f6f409b80ff08ef9423b1960ced543d5ec9e01bda86b2c90`.

## Evidence boundaries

This release changes instructions. No agent team was launched and no project was run with
`max_workers: max` in this repository. The packaged helper is unchanged: it still takes an
integer `--max-workers`, which the coordinator resolves. The linter checks that the contract
text is present, not that a model follows it; eval scenarios E28, E29 and E30 were written
and not run. Real writing-backend acceptance from v7.0.0 remains pending.

## Publication

GitHub Actions is disabled in this repository, so a tag publishes nothing. After the
PR from `develop` is merged into `main`: tag `v7.3.0` on that merge commit, then
`gh release create v7.3.0` with the 7.3.0 changelog section as notes and
`dist/keel-v7.3.0.zip` attached.
