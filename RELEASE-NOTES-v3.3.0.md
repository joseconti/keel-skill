## Per-role model binding

Keel stops running every agent on the session model. Each agent is now bound to the model that fits its work — chosen once per project, in the assistant's own config, and never named in the skill itself. This closes the lever usage statistics kept pointing at (subagent-heavy sessions all inheriting one expensive model) without breaking Keel's multi-assistant portability.

### How it works

- Every agent is assigned an abstract **role** by the kind of work it does:
  - **orchestrator** — the session driver and the judgment-heavy phases (Discovery, plan, architecture, design decisions).
  - **reviewer** — `code-reviewer`, `security-auditor`, `design-fidelity-auditor`.
  - **mechanical** — `docs-verifier`, `playground-qa`, `launch-verifier`, `a11y-auditor`, `guide-qa`, plus any search or exploration agent.
- The concrete model behind each role is chosen per project and written only into each tool's native config (`model:` in `.claude/agents/*.md`, an `[agents.<name>]` entry in `.codex/config.toml`, `.github/agents/*.agent.md`, `.gemini/agents/*.md`), using each vendor's own model names. A model name that ages never reaches the skill or any file that travels.
- At the config-package offer, when agents are taken, Keel proposes a role to model map with a one-line reason each; you confirm or override. It recommends on the axis that matches your billing — speed and rate-limit headroom on a flat subscription, real spend on metered APIs.
- The map is recorded in three places, each with its job: a `docs/decisions.md` entry (the reasoning), the project card `Models:` line (read on every resume), and the tool's native config (the only place a concrete model name lives). It is re-confirmed only on request or when a model becomes unavailable — never re-asked every session.

### Upgrading an existing project

On reconcile, Keel adds the `Models:` card line and, if your assistant config includes agents, settles the map and writes the native model fields at the next Phase 2 close or maintenance touch. Nothing else structural.

Full detail in `keel/CHANGELOG.md`.
