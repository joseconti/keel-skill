---
schema: keel.sprint/1
sprint: 5
goal: Keel v6.5.0 — browsers stop multiplying per session (browser MCP and local test runner)
status: done
slices:
  - id: S-010
    title: Browser MCP scope, flags, shared browser, browser_close, orphan reaping, doctor rows, local worker cap and minor version sync
    status: done
    hours: 1
    actual_hours: 0.45
    actual_source: estimated
    depends_on: []
    criteria: []
---

# Sprint 5 — Keel v6.5.0

- Acceptance: the browser MCP guidance lives in `references/test-automation.md` and is checked by
  three advisory doctor rows; the fan-out rule and MCP registration section link to it; local
  Playwright workers are capped; reconciliation row and version sync agree; release linter passes.
- Origin: the user's 32 GB laptop ran out of memory with four sessions open. Inspection on the
  machine found no browser MCP registered at all: the memory was a running e2e suite (two workers,
  each a headless browser plus an `ffmpeg` recording, about 2.1 GB), which is why the worker cap
  was added after the MCP rules.
- Close-out: S-010 complete; release linter passed. `actual_hours` is estimated, not measured: the
  work ran in a cloud session whose bridge to the machine was down, and no clock events were
  written to `docs/.keel/clock.jsonl`. The user applied the commits and pushed `develop`, then
  asked for v6.5.0 because v6.4.0 was already released.
