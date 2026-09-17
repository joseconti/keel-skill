---
schema: keel.sprint/1
sprint: 2
goal: Keel v6.1.0 — the tool registry becomes data, one row file per assistant, so adding an assistant cannot break another
status: in-progress
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
    status: in-progress
    hours: 1
    actual_hours: 0
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
