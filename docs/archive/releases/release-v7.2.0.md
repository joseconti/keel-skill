# Keel v7.2.0 — release candidate

Prepared on 2026-10-13 on `develop`, based on v7.1.0 (`f3c3637` on `main`). The skill
content is commit `36a075b`.

## Release notes

A playground on `localhost` can now receive calls from outside. The new reference
`keel/references/inbound-tunnel.md` defines the inbound-call inventory in the technical
plan, the tunnel choice (Cloudflare quick tunnel by default), the generated
`scripts/playground-tunnel` with its three modes, how the application is pointed at the
tunnel, the exposure rules and the negative-control evidence. Keel no longer plans a
deployment to an online server only to be reachable.

`keel/references/test-automation.md` gains "The live drive": at every slice's test point
the assistant also exercises the new or changed behaviour in a real browser against the
running playground with nothing mocked, beside the end-to-end tests.

Version metadata, changelog, manifest and portability-lock stamp are synchronized to
7.2.0. Existing projects apply `MANIFEST.md` Table 3, v7.2.0: one conditional artifact,
no new card line.

## Verification

- `python3 tests/lint-release.py`: all checks passed, including the new check 12.
- `python3 -B -m unittest discover -s tests -p 'test_parallel*.py'`: 32 tests passed.
- `git diff --check`: passed.
- `unzip -t dist/keel-v7.2.0.zip`: no errors. The archive is `git archive HEAD keel` at
  `36a075b`: 49 entries, `keel/` only, the helper executable.

Artifact: `dist/keel-v7.2.0.zip` (ignored build output).

SHA-256: `9671b749d403f7fa790df89a0df5d57b54d76c83e6d24d7a22353bd49430ca59`.

## Evidence boundaries

This release changes instructions. No tunnel was opened and no project was driven in
this repository. The contract generalises one measured case: the Redsys sandbox
notifying a wp-env playground through a Cloudflare quick tunnel, recorded in that
project on 2026-10-13. Web apps, MCP servers, named tunnels, substitutes and other
providers are unexercised. The Cloudflare quick-tunnel limits the reference cites were
not re-verified in this session. The linter checks that the contract text is present,
not that a model follows it; eval scenario E27 was written and not run.

Real writing-backend acceptance from v7.0.0 remains pending.

## Publication

GitHub Actions is disabled in this repository, so a tag publishes nothing. After the
PR from `develop` is merged into `main`: tag `v7.2.0` on that merge commit, then
`gh release create v7.2.0` with the 7.2.0 changelog section as notes and
`dist/keel-v7.2.0.zip` attached.
