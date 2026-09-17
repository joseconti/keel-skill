---
schema: keel.sprint/1
sprint: 2
goal: Keel v6.1.0 — the tool registry becomes data, one row file per assistant, so adding an assistant cannot break another
status: done
slices:
  - id: S-004
    title: Tool rows as files — scripts/keel-tools/<tool>.sh, the contract, the scaffold step, the matrix, the anti-pattern, the checks
    status: done
    hours: 2
    actual_hours: 0.1
    actual_source: measured
    depends_on: []
    criteria: []
  - id: S-006
    title: The hook registration is checked against its row — KEEL_TOOL_HOOK_FILE, and the check that fails on a registration the row forbids
    status: done
    hours: 0.5
    actual_hours: 0.05
    actual_source: measured
    depends_on: [S-004]
    criteria: []
  - id: S-005
    title: Release v6.1.0 — manifest tables, changelog, eval, version sync, lint, tag, publish
    status: done
    hours: 1
    actual_hours: 0.23
    actual_source: measured
    depends_on: [S-004, S-006]
    criteria: []
---

# Sprint 2 — Keel v6.1.0

- Acceptance: the registry exists as one generated file per accepted assistant; `references/project-state.md`
  carries its contract and the launcher contract reads the row instead of branching; the Phase 5 scaffold
  generates the rows; `references/assistant-config.md`'s matrix points at the row for every per-tool launch
  and hook fact; `references/anti-patterns.md` carries the entry for a session adapting a SHARED script to
  its own tool; `scripts/keel-verify` gains the three checks; `python3 tests/lint-release.py` passes; the
  release is published.
- Origin: the user hit this working `new-gymai` with both Claude Code and Codex — the per-agent close and
  open commands live inside `scripts/keel-continue` as `if [ "$TOOL" = ... ]` branches, so a session fixing
  its own tool's launch edits lines belonging to another tool, and a Keel update regenerates the lot.
  `references/project-state.md` already forbade exactly that ("there is no per-tool script and no per-tool
  branch in the skill") while the registry it describes was prose a generator had to turn into branches.
  This sprint gives the registry a container so the rule can be obeyed and checked.
- Close-out (session 2): all three slices done. `v6.1.0` tagged on `main` at 14f0901 and published
  by hand with `gh release create` (Actions is disabled in this repo, so pushing the tag publishes
  nothing). S-006 was not in the plan at kickoff — it was added the moment the user brought the live
  Codex instance, per rule 3 of "Sprints are the ledger of all work", and the remaining time grew
  visibly instead of being absorbed into S-004.
- Note for the next session: `git fetch --tags` reports "would clobber existing tag" for v5.3.0,
  v5.19.0 and v5.20.0 — local tags that diverge from the remote's, left over from the re-anchoring
  after a discarded local merge. Harmless to this release (v6.1.0 is verified an ancestor of
  `origin/main`), but worth resolving deliberately rather than living with a fetch that exits
  non-zero every time.
