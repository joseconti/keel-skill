## Documentation follows the code: created, modified, removed

Keel already required every public surface to be documented in the same slice that built it. That rule only ever spoke about *new* surfaces — and the gap was quiet, which is what made it expensive. Change a function's signature and nothing obliged you to touch its doc; remove a surface and its entry could stay behind. Neither failure announces itself: a stale doc and a correct doc look identical to whoever reads it next, whether that is a developer or the next agent working the repo.

### The three operations

- **Created** — the full entry (signature, params, return, errors, auth, runnable example) plus its `docs/api/INDEX.md` row.
- **Modified** — the existing entry is updated in the same slice: signature, parameters, return, errors, permissions, behavior, and the example, re-run so it still works. A doc left describing the previous signature is a slice defect exactly like a missing doc.
- **Removed** — never a silent deletion. Never released: entry and row are deleted. Already released: removal is a gated breaking change — the entry stays, marked deprecated/removed with its version and the replacement to use, with its decision on record.

The slice does not pass its Phase 5 test point until the docs match the as-built code and every touched example runs. Phase 6 stops accepting one-to-one INDEX parity as sufficient: no entry may describe a surface the code no longer has, or a signature it no longer matches. And `docs-verifier` now inspects all three operations in a diff instead of additions only.

### Reference artifacts — a requirement carried by a file

A requirement may be specified by something higher-fidelity than prose: a test suite that acts as the executable spec, code to port, a working HTML mockup. Four conditions, none optional — it lives in the repo, a tests-as-spec suite is wired into the project's real test command, ported code carries verified provenance and a compatible license, and every artifact is registered in the spec. The prose requirement stays, reduced to what the file cannot say about itself; where the two disagree, the spec governs.

The same ladder reaches design: a working mockup outranks a screenshot, which outranks a URL. Rich references travel as the file itself, never paraphrased — but a mockup is input to Design, never a build source, and it never shrinks the brief.

### Domain rubrics — verifying shape, not only completeness

A checklist catches what is missing, never what is badly shaped. A spec can pass every mechanical item and still describe an API third parties will curse for years. Phase 2 §6a now asks the user once, in plain language, whether to record what "good" means for one such domain; recommended for plugins, MCP servers and libraries, where the shape others hook into cannot change after release without breaking their sites. Recorded never improvised, the reviewer flags but never rewrites, and the fixed artifact wins any disagreement.

### Upgrading an existing project

On reconcile: from the next slice or maintenance touch, changed and removed surfaces are resolved in their own slice — no retroactive sweep is required, but a stale entry found while working is fixed then, not noted for later. The rubric question is asked once if it never was, and its answer recorded either way. Reference artifacts are opt-in and create no obligation for a project that holds none. Nothing else structural.

Full detail in `keel/CHANGELOG.md`.
