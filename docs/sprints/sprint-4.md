---
schema: keel.sprint/1
sprint: 4
goal: Keel v6.4.0 — mandatory session close with planned and measured time, baseline remaining hours and a pace-adjusted projection
status: done
slices:
  - id: S-009
    title: Mandatory time report, cumulative projection, templates, reconciliation and minor version sync
    status: done
    hours: 0.5
    actual_hours: 0.050936
    actual_source: measured
    depends_on: []
    criteria: []
---

# Sprint 4 — Keel v6.4.0

- Acceptance: every session close shows active time, planned time, like-for-like deviation,
  baseline remaining hours and a labelled projection using the cumulative measured pace of
  completed slices; unavailable data is explicit; generated script contracts, session schema,
  verification and reconciliation agree; release linter passes.
- Origin: user requested the report as mandatory and explicitly authorised a minor update.
- Scope: skill instructions and version metadata; release publication authorised only after the user merges to main.

- Close-out: S-009 complete; release linter and whitespace checks passed. Generic skill validation
  could not run because its environment lacks PyYAML. Measurement starts after initial reading;
  that earlier time is unmeasured. The user subsequently authorised committing and sending this change to develop, then creating the
  release after their merge to main.
