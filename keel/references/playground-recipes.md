# Playground recipes — real verification environments per project type

Load this at two moments: (a) Phase 2 §4 (Testing), when `docs/03-technical-plan.md` chooses the project's recipe; (b) the Phase 5 scaffold, when the chosen recipe is stood up. The playground is where "real functional verification" stops being a phrase: automated tests prove the parts, the playground proves the product, and this file defines — per project type — what that environment IS and how it is exercised.

Recipes are operable BY the assistant. "Exercise it for real" means concrete commands with recordable output — the assistant itself starts the environment, drives the flows, and pastes command + output as evidence into `docs/05-test-points.md`. The user gets try-it steps ON TOP of that, maintained in `docs/playground.md` — never instead of it. What the assistant genuinely cannot run is recorded honestly (see the cross-cutting rules), never papered over.

Two rules are part of EVERY recipe, not options:

- **Seed data ships with the playground.** Every recipe includes a synthetic seed-data fixture and a documented reset command that returns the environment to a known state. Fixtures are synthetic only — invented names, invented emails, invented orders, invented keys-shaped-like-placeholders. The confidential-data rule (SKILL.md "Confidential data never reaches Git") covers test data too: never real customers, real orders, real emails, real anything — however convenient the production export looks. A flow that "needs" real data needs a synthetic fixture that mimics its shape instead.
- **Gate zero everywhere.** Before the first slice: a clean build/compile, a clean lint pass, and one trivial passing test — all green on the freshly stood-up environment (Phase 5 §1). No recipe skips it; a project that cannot pass gate zero has a scaffold defect, not a testing gap.

## WordPress / WooCommerce plugin

- **Default environment: `wp-env`.** Commit a `.wp-env.json` pinned to the support matrix in `docs/03-technical-plan.md` — the minimum supported WordPress core and PHP versions, never an implicit "latest" — with the plugin mapped in (`"plugins": [ "." ]`). For WooCommerce projects, add WooCommerce to the plugin list so checkout-class flows exist to walk. Testing against a version the support matrix does not promise proves nothing about the versions it does.
- **Start / stop / reset:** `npx wp-env start` / `npx wp-env stop`; reset with `npx wp-env clean all` followed by the seed script below. Document all of them in `docs/playground.md` exactly as they are run — copy-paste-runnable, no prose substitutions.
- **Smoke checks (WP-CLI):** the plugin activates cleanly — `npx wp-env run cli wp plugin activate <slug>` exits 0, no fatal, no notice in debug log — and a REST route answers — `curl -s http://localhost:8888/wp-json/<namespace>/v1/<route>` returns the expected shape, not a 404 or a PHP error page. Both run at the scaffold and stay cheap enough to repeat at any test point.
- **Seed:** a WP-CLI-driven fixture script (e.g. `scripts/seed-playground.sh`) that creates the synthetic products, orders, customers, and settings the flows need — and configures the payment gateway in its sandbox/test mode, never with live merchant credentials. The script IS the reset's second half: clean + seed = known state.
- **Unit/integration tests:** PHPUnit with the WordPress test scaffold (or wp-browser), so hooks, REST handlers, and logic run against a real WordPress load — not hand-rolled mocks of WordPress.
- **End-to-end:** Playwright against the wp-env URL for every UI-visible flow — checkout, settings screens, admin actions — asserting on what the user sees, not on internals. This is the detection point for "unit tests green, checkout broken".
- **What stays user-tested by hand:** anything requiring credentials that are theirs — e.g. a real gateway sandbox checkout with their sandbox account. `docs/playground.md` gives them the exact steps; the test-point row records the delegation, not a pass.
- **Substitutes:** LocalWP, or Docker directly (the official WordPress + database images), are acceptable when `wp-env` cannot run in the environment — record WHICH substitute and why in the technical plan, and keep the same smoke/seed/e2e duties on it.

## MCP server

- **Drive the protocol, not just the functions:** run the dev build under MCP Inspector (`npx @modelcontextprotocol/inspector`) or through scripted JSON-RPC over stdio — initialize, list tools, call every tool with valid arguments, capture the responses. A tool that was never called over the protocol was never really tested.
- **Register the dev server in the project's `.mcp.json`** (per `references/claude-config.md`) so the assistant can call the tools live from its own session. A tool the assistant itself invoked, with the real request and response pasted as evidence, is the strongest possible verification an MCP server can get — use it whenever the environment allows.
- **Fixtures:** sample resources for every resource/content type the server returns AND the malicious-content fixture from `references/security/mcp-server.md` — instruction-shaped text returned as data, which must come back delimited and labelled as untrusted content, never obeyed and never allowed to rewrite the tool's framing.
- **Unit tests on every tool handler,** plus schema-invalid and boundary calls as named tests: wrong types, missing required fields, unknown extra fields, oversized inputs, out-of-range identifiers — each rejected cleanly. This automates the security profile's fuzz duty instead of leaving it to a one-time manual pass.

## Web app / website

- **Environment:** the local dev server for single-process stacks; `docker compose` the moment the stack needs services (database, cache, queue) — one command brings up the whole thing, service versions pinned to the support matrix.
- **Seed:** a seed script for the database — synthetic users, records, and content sufficient to walk every flow — with a documented reset (drop + re-seed, or an equivalent single command).
- **Unit/integration tests** per the stack's idiom, with the exact run commands recorded in the technical plan.
- **End-to-end:** Playwright driving each critical flow in a real browser — REQUIRED for UI flows whenever the environment can run a browser. A web UI without a browser-driven e2e is an untested surface, whatever the unit coverage says.
- **API surfaces:** `curl` checks per endpoint — status, response shape, auth failure behavior — recorded as commands with output, repeatable at any test point.
- **Show, don't describe:** where something is visual, send the user screenshots from the playground alongside the try-it steps; a described screen is not evidence.

## Library / component / package

- **A clean consumer project is the playground.** Create a scratch project that installs the BUILT artifact — `npm pack` and install the tarball, or the ecosystem's equivalent (a composer path/artifact repository, `pip install dist/*.whl`) — never `src/` and never a workspace symlink: users install the package, so the package is what gets verified, packaging defects included.
- **Run every README example verbatim** in that consumer, exactly as written. This doubles as the documentation test: an example that does not run is a defect — in the docs or in the package, either way it fails the test point.
- **Unit tests** per the stack on the library itself, per the technical plan.
- **At release time: diff the public API against the previous release** before publishing — the surface consumers see, not the file list. This ties into the security profile's "Verify with" (`references/security/library-component.md`): an unintended breaking change is caught here, and an intended one is a major, per the disclosure duty.

## Cross-cutting rules (every recipe)

- **The per-flow "real exercise" is defined in the plan and executed at test points.** `docs/03-technical-plan.md` §Testing names, per flow, what "exercised for real" means in this playground — walk the checkout, call the tool over the protocol, hit the endpoint, run the README example. At each test point that exercise is executed and its command + output recorded in `docs/05-test-points.md` — an unrecorded check did not happen.
- **Docker/compose is always an acceptable isolation layer.** Any recipe may run inside a container when the host is unsuitable; what matters is that the documented commands work exactly as written, wherever they run.
- **If the environment cannot run the recipe, say so at the scaffold** — no Docker, no browser, no network to the registry. Fall back to what IS runnable (the unit suite, static checks, a partial environment) and record every un-runnable part as `⚠ unverified` in `docs/PROGRESS.md`'s open items, with the user's try-it steps in `docs/playground.md` so THEIR pass closes it. Never silently skip: an unverified flow that looks verified is exactly the defect this file exists to prevent.

## Definition of done (this reference)

- The technical plan names the chosen recipe (or the recorded substitute, with the reason) and the per-flow real exercises.
- The playground stands up from its documented commands at the scaffold, seeded with synthetic fixtures, with a working reset command — and gate zero passed before the first slice (clean build/compile + lint + one trivial passing test).
- Every flow's real exercise runs at its test points with command + output recorded; end-to-end tests exist for UI flows wherever a browser can run.
- Anything the recipe could not run is recorded as `⚠ unverified` with the user's steps — never silently absent.
