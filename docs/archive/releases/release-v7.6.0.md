# Keel v7.6.0

Ordered by the user on 2026-11-10 ("creas la release 7.6.0"), on `develop`, based on v7.5.0. Minor
release (D-044).

## Release notes

A chain no longer opens empty sessions. When every pending slice waits on a person or an event, the
launcher RESTS: it prints the prompt, says once what the queue waits on, and opens nothing. An
idle-link breaker stops two empty links in a row, whatever the labels said (issue #30).

Every project that uses a machine now carries `docs/machines/`: the recipe, and every file and
script needed to rebuild the machine from a fresh clone. On the shared VM, each repository carries
the VM's documents, never the VM. Nothing a machine depends on may live in a temporary directory or
only beside the VM. Existing projects apply `MANIFEST.md` Table 3, v7.6.0. Standing check 4 is not
declinable.

## Verification

- `python3 tests/lint-release.py`: all checks passed, including the new checks 18 (idle queue) and
  19 (machine recipe). Check 18 was shown to fail when its promise is removed.
- `python3 -B -m unittest discover -s tests -p 'test_*.py'`: 68 tests passed.
- First application of the recipe: `docs/machines/` written from the running `keel-development` into
  `woo-redsys-gateway-light` (f8a255f, plan 7b5257e) and `advanced-subscriptions-for-woocommerce`
  (a45f8694), with base revision `2026-11-10-1` stamped on the VM. That exposed drift the old kit
  did not describe: PHP 8.1, PostgreSQL 16, `php8.4-pgsql`, a MariaDB 10.6 tenant and Chromium
  runtime libraries, all installed after provisioning. Each project's keel-verify and confidential-data
  gate passed on it once two false positives in the copied scripts were renamed.

## Evidence boundaries

The REST path and the breaker are specified and linted; no real chain has run them yet. No recipe has
been proven by a rebuild: each says `never — unproven`. The six other repositories using the shared
VM had live sessions, so they were not written to; their recipes come with their v7.6.0
reconciliation.

## Publication

Published on 2026-11-10. PR #31 merged `develop` into `main`; tag `v7.6.0` is on the merge commit
`c2e8be6`, whose tree equals `develop`'s. GitHub Actions is disabled, so the release was created by
hand with `gh release create v7.6.0`, marked Latest, with `keel-v7.6.0.zip` attached, built from the
tag (`git archive v7.6.0 keel`, 51 entries, no errors). SHA-256:
`b187c4ba257261af4325db30473902d0df581adb92f2560fdaa97d58140e540e`.

