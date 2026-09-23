---
schema: keel.sprint/1
sprint: 3
goal: Keel v6.3.0 — an active, optional security audit that hunts with the existing profiles and confirms nothing a second agent could not re-derive
status: done
slices:
  - id: S-007
    title: references/security-audit.md — recon, profile-driven hunters, independent verifier, findings.json, SECURITY-AUDIT.md; the card line, the Phase 2 detection, the Phase 7 gate, the trigger
    status: done
    hours: 2
    actual_hours: 0.05
    actual_source: measured
    depends_on: []
    criteria: []
  - id: S-008
    title: Release v6.3.0 — manifest tables, changelog, NOTICE credit, eval, version sync, lint, commit and tag on develop (no push, on the user's instruction)
    status: done
    hours: 0.75
    actual_hours: 0.03
    actual_source: measured
    depends_on: [S-007]
    criteria: []
---

# Sprint 3 — Keel v6.3.0

- Acceptance: `references/security-audit.md` defines a six-step audit (recon reusing the project's recorded
  state, one hunter per applicable profile section of `references/security/*.md` plus a threat-model claims
  hunter, an independent verifier per candidate, `findings.json` with `confirmed` / `needs_validation` /
  `rejected`, and `SECURITY-AUDIT.md` derived only from `confirmed`); the audit output is gitignored until its
  confirmed findings are fixed; the verifier falls back inline and says so; the card carries
  `Security audit: required|optional`, set at Phase 2 §4c; the Phase 7 gate requires the audit (or a D-entry
  declining it) when `required`; SKILL.md's trigger routes "security audit" to the new flow; the existing
  `references/security/*.md` profiles are untouched; `python3 tests/lint-release.py` passes; v6.3.0 is
  committed and tagged on `develop` and not pushed.
- Origin: the user asked for an active audit phase adapted from Cloudflare's open-source
  `security-audit-skill` (MIT), fitted to Keel's stack and without its OS-sandbox infrastructure. Design
  questions answered by the user 2026-09-23: v6.3.0; report under `docs/`, gitignored until fixed; inline
  verifier fallback marked `verified_by: inline`; gate for critical projects (audit or decline on record).
- Close-out (session 3): both slices done in one session. Before any file was written, four design
  questions were answered by the user (recorded in D-033/D-034). Cloudflare's skill was read in full from
  a scratch clone before adapting it. `python3 tests/lint-release.py` passed. v6.3.0 committed and tagged
  on `develop`; nothing pushed, per the user's instruction.
- Clock caveat: this repository has no `scripts/keel-time`; boundaries were read with `date -u`. The clock
  was first read AFTER the SKILL.md read, the design questions and the user's answers, so that time is
  unmeasured; S-007's interval also excludes about 0.03 h of reading inside the session.
