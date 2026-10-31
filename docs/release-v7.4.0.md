# Keel v7.4.0 — release candidate

Prepared on 2026-10-31 on `develop`, based on v7.3.2. Minor release (D-042). The skill content is commit `b6ca789`.

## Release notes

Where Parallels works, a project that would run on an ordinary hosting account gets an isolated site
on one shared `keel-development` VM, and one that needs its own server gets a linked clone. Sites
that must talk to each other, such as an API, a licence manager and a client, reach each other over
named HTTPS. The reconciliation proposes moving each project off Docker and deletes its Docker
resources only after verification. `keel-parallel reap-worktrees` retires dead worktrees, and a new
rule says nothing dead stays behind. Docker remains the complete path without Parallels. Existing
projects apply `MANIFEST.md` Table 3, v7.4.0.

## Verification

- `python3 tests/lint-release.py`: all checks passed, including the new Parallels host check.
- `python3 -B -m unittest discover -s tests -p 'test_*.py'`: 57 tests passed (5 new for `reap-worktrees`).
- `unzip -t dist/keel-v7.4.0.zip`: no errors; 51 entries, `keel/` only.
- Pilot on `woo-redsys-gateway-light`, two sites on one VM: floor 41 unit, 410 integration, 67/67
  browser; ceiling 41, 410, 63/67, with the same 4 accessibility failures on Docker.
- Three connected sites: update applied through the real updater; isolation held.
- Public tunnel: forged notification refused, URL restored, tunnel closed.
- `reap-worktrees` on three real repositories: 253 worktrees retired, none failed, 113 GB of free space gained.

SHA-256: `ed1875313e6637732ebabe0982746c7d7d0b2ee528a90a18f0ae3ae381150568`.

## Evidence boundaries

Host-browser access to named sites is unmeasured and the reference says so. Linked clones are
evidenced only by SupportAI's script, not by this pilot. `scripts/keel-site` is a contract; the pilot
implementation lives on the author's machine and is not shipped. No project has been migrated off
Docker yet: the plugin's Docker resources were kept.
