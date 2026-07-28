# Playground recipes — real verification environments per project type

Load this at two moments: (a) Phase 2 §4 (Testing), when `docs/03-technical-plan.md` chooses the project's recipe; (b) the Phase 5 scaffold, when the chosen recipe is stood up. The playground is where "real functional verification" stops being a phrase: automated tests prove the parts, the playground proves the product, and this file defines — per project type — what that environment IS, which driver exercises it, and what it costs.

**Read `references/test-automation.md` alongside this file.** That one is the protocol — who drives (the assistant, always, wherever a machine can), the eight tags that are the only valid reasons to hand work to the user, the `scripts/keel-doctor` contract, and the evidence rules. This one is the catalogue. A recipe here without that protocol degenerates into the failure it exists to prevent: an environment that exists, and a human clicking through it.

Recipes are operable BY the assistant. "Exercise it for real" means concrete commands with recordable output — the assistant itself starts the environment, drives the flows, fills the fields, and pastes command + output as evidence into `docs/05-test-points.md`. The user gets try-it steps ON TOP of that, maintained in `docs/playground.md` — never instead of it. What the assistant genuinely cannot run is recorded honestly with its tag, never papered over.

Three rules are part of EVERY recipe, not options:

- **Seed data ships with the playground.** Every recipe includes a synthetic seed-data fixture and a documented reset command that returns the environment to a known state. Fixtures are synthetic only — invented names, invented emails, invented orders, invented keys-shaped-like-placeholders. The confidential-data rule (SKILL.md "Confidential data never reaches Git") covers test data too: never real customers, real orders, real emails, real anything — however convenient the production export looks. A flow that "needs" real data needs a synthetic fixture that mimics its shape instead.
- **Gate zero everywhere, and the doctor before it.** `scripts/keel-doctor --check` passes first (the environment can actually run this recipe), then a clean build/compile, a clean lint pass, and one trivial passing test — all green on the freshly stood-up environment (Phase 5 §1). No recipe skips it; a project that cannot pass gate zero has a scaffold defect, not a testing gap.
- **Every recipe declares whether its driver takes over the user's screen**, and where it does, the technical plan records the mitigation. This is decided here, at plan time — never discovered mid-sprint when a test run grabs the keyboard.

## WordPress / WooCommerce plugin

**Environment — pick one deliberately, and record why:**

- **`wp-env` (default when Docker is available).** Commit a `.wp-env.json` pinned to the support matrix in `docs/03-technical-plan.md` — the minimum supported WordPress core and PHP versions, never an implicit "latest" — with the plugin mapped in (`"plugins": [ "." ]`). For WooCommerce projects add WooCommerce to the plugin list. Testing against a version the support matrix does not promise proves nothing about the versions it does. Three settings worth copying from WooCommerce's own e2e config: `"WP_DEBUG_LOG": true` in `config` (it is **not** a default, and without it there is no debug log to read back), a mail-logging plugin so transactional emails are verifiable without SMTP, and pinned core/PHP versions rather than "latest".
 Use `lifecycleScripts.afterStart` / `afterReset` to run the seed script, so reset and seed are one operation.
- **WordPress Playground CLI (`@wp-playground/cli`) when there is no Docker.** Serves real HTTP that Playwright drives, mounts the local plugin (`--auto-mount` or `--mount`), and a blueprint installs plugins, sets options, imports content and logs in before the first test. It boots in seconds and makes a wide WP/PHP matrix cheap. The trade-offs are real and must be recorded: SQLite instead of MySQL, no mail delivery, and — with `wp-env start --runtime=playground` — no `wp-env run`, therefore no WP-CLI and no PHPUnit through that path. `@wp-now/wp-now` is deprecated in favour of this; do not start new projects on it.
- **Substitutes:** LocalWP, WordPress Studio, or Docker directly. Record WHICH substitute and why in the technical plan, and keep the same smoke/seed/e2e/a11y duties on it.

**One trap worth knowing before it costs a morning: `"testsEnvironment": false` and the PHPUnit strategy are mutually exclusive.** Recent wp-env deprecates starting both the development and the tests environment from one config and warns about it, and WooCommerce's own e2e config sets `testsEnvironment: false` to silence that warning — but that flag is precisely what stops the tests containers from being created, so `wp-env run tests-cli ... phpunit` then has nothing to run against. Pick deliberately and record the pick in the technical plan: either keep the tests environment (the simple path when one config serves both duties), or adopt the pattern the deprecation points at — a separate `.wp-env.test.json` started with `wp-env start --config .wp-env.test.json`, with the PHPUnit command pointing at that config. Copying `testsEnvironment: false` out of an e2e-only example into a project that also runs integration tests produces a scaffold that half-works and a confusing failure at the first PHPUnit run.

**Driver: Playwright, headless, never takes the screen.** Use `@wordpress/e2e-test-utils-playwright` — it gives `admin`, `editor`, `pageUtils` and `requestUtils` fixtures, authenticates once over REST and persists the `storageState` so no test walks the login form, and resets content between runs (`deleteAllPosts`, `deleteAllPages`, `activateTheme`, `resetPreferences`, and the rest). The `@wordpress/scripts` base Playwright config already wires the base URL, the storage state, the artifacts path, and a `webServer` block that starts wp-env itself — inherit it rather than rebuilding it.

**Smoke checks (WP-CLI):** the plugin activates cleanly (`wp-env run cli wp plugin activate <slug>` exits 0, no fatal, and **the debug log gained nothing**) and a REST route answers the expected shape rather than a 404 or a PHP error page. Both run at the scaffold and stay cheap enough to repeat at any test point.

**Seed:** a WP-CLI-driven fixture script that creates the synthetic products, orders, customers and settings the flows need, and configures payment in sandbox/test mode — never live merchant credentials. For WooCommerce the reproducible sources are the plugin's own sample-data WXR (imported with the WordPress Importer), `wp wc` commands, and the Smooth Generator for volume. The script IS the reset's second half: clean + seed = known state.

**Unit/integration:** PHPUnit against a real WordPress load through the wp-env tests container (`wp-env run tests-cli --env-cwd=... phpunit`), not hand-rolled mocks of WordPress. Pin the PHPUnit major to what the WordPress test suite actually supports — the current suite tops out at PHPUnit 9 via the Yoast polyfills, so the newest PHPUnit is not usable for integration tests however tempting the version number looks. With wp-env there is no need for `install-wp-tests.sh`: the suite and `WP_TESTS_DIR` are already inside the container. Without Docker, wp-browser installs the whole thing through Composer over SQLite.

**End-to-end:** Playwright against the environment URL for every UI-visible flow — checkout, settings screens, admin actions — asserting on what the user sees. This is the detection point for "unit tests green, checkout broken". Two WooCommerce-specific traps: the Cart and Checkout **blocks are React**, so there is no classic form to fill and submit (state syncs to the Store API with debounce — drive by role and label, wait on the block being ready, and never chain a `fill` straight into a submit), and the classic shortcode checkout is a **completely different DOM** with the historical field IDs. Detect which one the site is running rather than assuming.

**Payments — the honest line.** Cash on delivery, cheque and bank transfer are fully drivable end to end with zero credentials and have native block implementations, so the complete purchase flow IS automatable. Anything real — Stripe, PayPal, WooPayments — needs the user's own test keys, outbound network and a publicly reachable webhook: that leg is tagged `CREDENTIAL` and only that leg, never the whole purchase. One trap worth knowing: cash on delivery hides itself for virtual carts unless enabled for them, which makes a test fail in a confusingly unrelated way.

**Static analysis, at every test point:** PHPCS with the WordPress Coding Standards, PHPStan with WordPress stubs, the official Plugin Check, `php -l` on touched files.

**Accessibility:** `@axe-core/playwright` inside the same tests, per screen and per state, excluding the admin bar. The block editor has no official automated accessibility suite to inherit — the project's own coverage is what exists.

## MCP server

**Environment:** the dev build, driven over the protocol. Headless by definition.

- **Drive the protocol, not just the functions.** The MCP Inspector has a non-interactive CLI mode (`--cli` with `--method tools/list`, `--method tools/call --tool-name ... --tool-arg k=v`, and the resources/prompts equivalents), which is the smoke test. Scripted JSON-RPC over stdio is the deeper path and the one that controls error cases: one JSON message per line, `initialize`, then `notifications/initialized`, then the calls, asserted with `jq`. A tool that was never called over the protocol was never really tested.
- **Register the dev server in the project's MCP registration** (`.mcp.json` and the other accepted tools' containers, per `references/assistant-config.md`) so the assistant can call the tools live from its own session. A tool the assistant itself invoked, with the real request and response pasted as evidence, is the strongest verification an MCP server can get.
- **Assert that stdout carries only JSON-RPC.** Any log line written to stdout corrupts the stream — it is the single most common defect in stdio MCP servers, it is trivially checkable, and the check belongs in `scripts/keel-verify`. Logs go to stderr.
- **Fixtures:** sample resources for every resource/content type the server returns AND the malicious-content fixture from `references/security/mcp-server.md` — instruction-shaped text returned as data, which must come back delimited and labelled as untrusted content, never obeyed and never allowed to rewrite the tool's framing.
- **Unit tests on every tool handler,** plus schema-invalid and boundary calls as named tests: wrong types, missing required fields, unknown extra fields, oversized inputs, out-of-range identifiers — each rejected cleanly. This automates the security profile's fuzz duty instead of leaving it to a one-time manual pass.
- **Pin the protocol version** the server targets in the technical plan, and re-check it at maintenance: the specification revises, and there is no official conformance suite to lean on — third-party validators are not authoritative.

## Web app / website

**Environment:** the local dev server for single-process stacks; `docker compose` the moment the stack needs services (database, cache, queue) — one command brings up the whole thing, service versions pinned to the support matrix.

**Driver: Playwright, headless, never takes the screen.** Required for UI flows whenever the environment can run a browser. A web UI without a browser-driven e2e is an untested surface, whatever the unit coverage says.

**Seed:** a seed script for the database — synthetic users, records and content sufficient to walk every flow — with a documented reset (drop + re-seed, or an equivalent single command).

**API surfaces:** per-endpoint checks — status, response shape, auth-failure behaviour — recorded as commands with output, repeatable at any test point.

**Read-back is mandatory:** console errors, uncaught page exceptions, failed requests and any 5xx response fail the test. A page that renders correctly while throwing is a bug that ships.

**Visual regression, if the project wants it:** baselines are per-browser and per-platform, and a baseline generated on macOS will never match a Linux run — font hinting and antialiasing differ. Generate and compare inside the official Playwright container from day one, or tag the visual tests and run them only where the baselines were made. Raising the pixel threshold to make the difference go away turns the test into decoration.

**Accessibility:** axe per screen and per state, a driven keyboard-order pass, and an ARIA-tree snapshot as regression. A sitemap-wide sweep with `pa11y-ci` when there are many public URLs.

## Library / component / package

**A clean consumer project is the playground.** Create a scratch project that installs the BUILT artifact — pack the tarball and install it, or the ecosystem's equivalent — never `src/` and never a workspace symlink: users install the package, so the package is what gets verified, packaging defects included.

**Run every README example verbatim** in that consumer, exactly as written. This doubles as the documentation test: an example that does not run is a defect — in the docs or in the package, either way it fails the test point.

**Unit tests** per the stack on the library itself, per the technical plan.

**At release time: diff the public API against the previous release** before publishing — the surface consumers see, not the file list. This ties into the security profile's "Verify with" (`references/security/library-component.md`): an unintended breaking change is caught here, and an intended one is a major, per the disclosure duty.

## Apple app (iOS / iPadOS / macOS)

**Only executable on macOS with full Xcode.** Not the Command Line Tools — `xcodebuild`, `simctl` and the simulator runtimes ship with Xcode.app. On Windows or Linux this recipe is inexecutable: the doctor reports it and stops rather than attempting a workaround, because none exists.

**Preflight, in two halves — and the halves matter, because `keel-doctor --check` must never ask for a password.**

*Detection (no privileges, nothing modified):* `xcode-select -p` prints the active developer directory (it must point at Xcode.app, not the Command Line Tools); `xcodebuild -license check` reports whether the licence is accepted; `xcodebuild -checkFirstLaunchStatus` exits non-zero when components are missing and changes nothing — the ideal probe; `xcrun simctl list runtimes` shows which simulator runtimes exist.

*Remediation (needs sudo, only inside `--fix`, only after the user's OK):* `sudo xcodebuild -license accept`, `sudo xcodebuild -runFirstLaunch`, and `xcodebuild -downloadPlatform iOS` for a missing runtime. Installing Xcode itself is not automatable at all — it needs an Apple ID with two-factor authentication — so the doctor reports it and stops.

**Environment:** a **dedicated** simulator created for the project, with the device type and runtime identifiers read from `xcrun simctl list` rather than hardcoded. Reset with `xcrun simctl erase`; prepare state with `simctl privacy`, `simctl openurl`, `simctl status_bar override`.

**Driver: XCUITest via `xcodebuild test`.** Structure the run as `build-for-testing` once, then `test-without-building` N times. Always write to a fresh `-resultBundlePath` — the command **fails outright if the path already exists**. Useful flags: `-only-testing`, `-testPlan`, `-testLanguage`/`-testRegion` (the same suite in another locale, which is what proves identifiers are being used instead of labels), `-retry-tests-on-failure`, `-enumerate-tests` to list the suite without running it.

**Screen behaviour — the decisive difference:**

- **iOS Simulator: headless if `Simulator.app` is not open.** The runner quits it and shuts down stray simulators before every run. The user's machine stays usable; only CPU load is noticeable.
- **macOS app: it takes the screen, always.** A macOS UI test drives the real cursor and keyboard, which is why Apple requires Accessibility permission for Xcode Helper. Mitigations, in order: a dedicated Mac or VM, a separate macOS user account running the tests, or a hosted runner. Record which applies. Never disable SIP to script the permission grant.

**Evidence:** everything valuable is inside the `.xcresult` — read it with `xcresulttool get test-results ...` and extract screenshots and video with `xcresulttool export attachments`. Never parse stdout; `xcbeautify` is formatting, not data. Attachments default to being deleted when a test passes, so evidence screenshots are explicitly marked to be kept always.

**Accessibility:** `try app.performAccessibilityAudit()` after navigating to each screen — it fails the test by itself when it finds issues, and it accepts audit-type filters. There is no command-line accessibility auditor on Apple platforms, so inside a UI test is the only automatable path.

**Cost discipline:** a UI test is orders of magnitude slower and more fragile than a unit test. Put the bulk of coverage in `swift test` on the pure logic (which runs headless, fast, and even on Linux for Swift packages), keep XCUITest for the flows whose failure is expensive, and get the accessibility audit for free inside them.

## Android app

**Environment:** an emulator started from the CLI with `-no-window` — genuinely headless, no virtual display needed. What it does need is hardware acceleration: KVM on Linux, Hypervisor.framework on macOS (with `arm64-v8a` images on Apple Silicon), WHPX on Windows. Boot completion is polled, not slept on. Reset with `-wipe-data`, or a documented `adb` teardown.

**Driver:** Espresso for in-app behaviour (fastest, least flaky, synchronizes with the UI thread), UI Automator for anything crossing into system UI (permissions, notifications, settings), Compose test rules where the UI is Compose, Maestro when a declarative YAML flow is easier for the assistant to generate and maintain than Kotlin.

**Evidence:** `adb exec-out screencap`, `adb shell screenrecord`, `adb logcat`, and `adb shell uiautomator dump` for the view hierarchy when a locator misses.

**Accessibility:** `AccessibilityChecks.enable().setRunChecksFromRootView(true)` in the test target, with narrow, reasoned suppressions. Accessibility Scanner is a manual app and is not scriptable — do not plan around it.

## Desktop app — Electron, Tauri, native Linux, native Windows

- **Electron: Playwright drives it** (`_electron.launch`), including evaluating in the main process, which no WebDriver route offers. On Linux, wrap the run in `xvfb-run` so it never touches the user's screen; that combination also containerizes cleanly.
- **Tauri: WebDriver via `tauri-driver`**, with `msedgedriver` on Windows and `WebKitWebDriver` on Linux. macOS has no WKWebView driver, so desktop coverage there is the gap — record it rather than discovering it.
- **Native Linux (GTK/Qt): AT-SPI through dogtail, inside `xvfb-run`.** Enable the accessibility bridge for the toolkit before launching. Force X11 within Xvfb rather than automating a live Wayland session: Wayland gives clients no way to enumerate or activate another app's windows, and input injection needs portal consent, which defeats unattended runs. AT-SPI itself works under Wayland — it rides D-Bus — which is exactly why the accessibility route survives where screen-scraping tools do not. The quality of the tree depends on the app naming its widgets; check that with an inspector before committing to this route.
- **Native Windows: FlaUI** (directly from .NET, or through its WebDriver server / Appium for other languages). WinAppDriver has had no release in years and speaks an obsolete protocol — do not build new work on it. **This needs a live, unlocked, interactive Windows session with autologon**: there is no Xvfb equivalent, session 0 does not work, and a disconnected RDP session locks the desktop and blinds the automation. Plan a dedicated VM, or schedule the runs.

## CLI and TUI

- **Non-interactive commands:** run them and assert exit code plus normalized output (strip timestamps, absolute paths, PIDs and ANSI codes before comparing against the golden file, or the test fails for reasons that are not the code). `bats-core` for shell, the ecosystem's snapshot testing elsewhere.
- **Interactive prompts need a real PTY.** Without one, many CLIs change behaviour — colour off, prompts skipped, output buffered differently — so the test proves something the user will never experience. `script`, `expect`/`unbuffer`, or `pexpect` provide it.
- **Full-screen TUIs need a terminal emulator, not stdout capture.** Drive through `tmux` (`send-keys` then `capture-pane -p` for plain diffable text) or emulate the terminal in-process and snapshot the cell buffer.

## Cross-cutting rules (every recipe)

- **The per-flow "real exercise" is defined in the plan and executed at test points.** `docs/03-technical-plan.md` §Testing names, per flow, what "exercised for real" means in this playground — walk the checkout, call the tool over the protocol, hit the endpoint, run the README example. At each test point that exercise is executed and its command + output recorded in `docs/05-test-points.md` — an unrecorded check did not happen.
- **The assistant drives it, per `references/test-automation.md`.** A recipe is not satisfied by an environment that exists and a user who clicks. Handing a flow to the user requires one of the eight tags (`references/test-automation.md`), and it covers only the leg that needs it.
- **Containers are always an acceptable isolation layer** — and for web, Electron, Tauri on Linux, native Linux GUIs, CLIs, MCP servers and Android (with the KVM device passed through) they are the cleanest answer. The official Playwright image ships the browsers, their system dependencies and Xvfb; it needs `--ipc=host` for Chromium or Chromium runs out of memory. What containers cannot host: Apple platforms (Xcode and the simulators only run on macOS) and native Windows GUI automation (no desktop in a Windows container). Those need their own machine, which is a plan decision, not a surprise.
- **If the environment cannot run the recipe, say so at the scaffold** — no Docker, no browser, no macOS, no network to the registry. Fall back to what IS runnable (the unit suite, static checks, a partial environment) and record every un-runnable part as `⚠ unverified` in `docs/PROGRESS.md`'s open items, with its tag and its steps in `docs/playground.md`. Never silently skip: an unverified flow that looks verified is exactly the defect this file exists to prevent.

## Definition of done (this reference)

- The technical plan names the chosen recipe (or the recorded substitute, with the reason), the driver per surface, whether that driver takes over the user's screen and the mitigation if it does, and the per-flow real exercises.
- `scripts/keel-doctor --check` passes, then the playground stands up from its documented commands at the scaffold, seeded with synthetic fixtures, with a working reset — and gate zero passes before the first slice.
- Every flow's real exercise is DRIVEN BY THE ASSISTANT at its test points with command + output recorded; end-to-end tests exist for UI flows wherever a driver can run.
- Console/log read-back, static analysis and the automated accessibility pass run inside the same test points.
- Anything the recipe could not run is recorded as `⚠ unverified` with its tag and the steps for whoever will run it — never silently absent. A session with no command execution where the repo lives records `NO-EXECUTION` and hands the written tests to a shell-capable session; it never converts them into instructions for the user.
