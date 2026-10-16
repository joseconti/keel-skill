# Keel v7.3.0 — release candidate

Prepared on 2026-10-16 on `develop`, based on v7.2.0 (published 2026-10-13). The skill
content is commit `35204b9`.

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

Version metadata, changelog, manifest and portability-lock stamp are synchronized to
7.3.0. Existing projects apply `MANIFEST.md` Table 3, v7.3.0: no new file, no new card line.

## Verification

- `python3 -B tests/lint-release.py`: all checks passed, including the new checks 13 and 14.
- `python3 -B -m unittest discover -s tests -p 'test_parallel*.py'`: 32 tests passed.
- `git diff --check`: passed.
- `unzip -t dist/keel-v7.3.0.zip`: no errors. The archive is `git archive HEAD keel` at
  `35204b9`: 49 entries, `keel/` only.

Artifact: `dist/keel-v7.3.0.zip` (ignored build output).

SHA-256: `8d7b632e5fd8e3b295eede9cbb75324dc78204fe645a9f262357f4b11b85437c`.

## Evidence boundaries

This release changes instructions. No agent team was launched and no project was run with
`max_workers: max` in this repository. The packaged helper is unchanged: it still takes an
integer `--max-workers`, which the coordinator resolves. The linter checks that the contract
text is present, not that a model follows it; eval scenarios E28 and E29 were written and
not run. Real writing-backend acceptance from v7.0.0 remains pending.

## Publication

GitHub Actions is disabled in this repository, so a tag publishes nothing. After the
PR from `develop` is merged into `main`: tag `v7.3.0` on that merge commit, then
`gh release create v7.3.0` with the 7.3.0 changelog section as notes and
`dist/keel-v7.3.0.zip` attached.
