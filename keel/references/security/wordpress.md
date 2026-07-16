# Security Profile — WordPress / WooCommerce

Load this when the project type is a WordPress plugin or WooCommerce extension. Apply from Phase 1 onward and verify at every Phase 5 test point. This is a working checklist, not background reading.

## Input / output

- **Sanitize on input, escape on output.** Every external input (`$_GET`, `$_POST`, `$_REQUEST`, headers, REST params, options read back) is sanitized with the right `sanitize_*`. Every output is escaped at the point of output with the right `esc_*` (`esc_html`, `esc_attr`, `esc_url`, `wp_kses` for limited HTML).
- **Never trust the database as safe.** Escape on output even for stored data.
- **Prepared statements always.** All custom SQL via `$wpdb->prepare()`. Never concatenate input into SQL.

## AuthZ / AuthN

- **Capability checks, not role checks**, on every privileged action (`current_user_can( '...' )`). Use the least capability that fits.
- **Nonces on every state-changing request** (forms, AJAX, admin-post, custom endpoints): `wp_create_nonce` / `wp_verify_nonce` / `check_admin_referer` / `check_ajax_referer`.
- **REST API**: every route has a real `permission_callback` (never `__return_true` for anything privileged). Validate and sanitize every `args`.
- **AJAX**: separate `nopriv` handlers consciously; verify nonce and capability inside.

## MCP / OAuth (the user's common surface)

- Map every MCP ability/tool to a WordPress capability check, exactly as REST routes map `permission_callback` — no ability without one; use the least capability that fits.
- Application passwords and OAuth tokens carry the full capabilities of their WP user: connect the least-privileged user that works, honor revocation, require HTTPS, and never store, log, or echo one in plaintext — core keeps only the hash.
- **When the plugin ships an MCP server or ability surface, load `references/security/mcp-server.md` IN FULL — this section is the WP mapping, not a substitute for that profile (redirect-URI allow-lists, blast radius, model-facing threats live there).**

## Secrets & data

- No secrets in code or in the repo. Store in options/constants populated from environment or a secure store; redact in logs and debug output.
- PII and order data (WooCommerce): minimize, restrict access by capability, never expose via an unauthenticated endpoint.
- Honor WordPress salts/nonscalar APIs; don't roll custom crypto.

## Files & execution

- No arbitrary file read/write/include from input. Validate paths; use WP filesystem API.
- Uploads: validate type and use `wp_handle_upload`; never trust the client MIME.
- No `eval`, no dynamic `include` of input-derived paths.
- Every PHP file starts with a direct-access guard (`defined( 'ABSPATH' ) || exit;`) so it does nothing when requested directly.

## Common WP pitfalls (verify explicitly)

- Redirects from input go through `wp_safe_redirect()` (+ `exit`), never `wp_redirect()` with an unvalidated URL — open-redirect risk.
- `LIKE` queries escape the term with `$wpdb->esc_like()` *before* `$wpdb->prepare()`.
- Every `register_setting()` has a real `sanitize_callback`; settings are re-sanitized on save, not only on render.
- Cron/background handlers and `admin-post`/`admin-ajax` endpoints re-check capability and nonce — being "not linked in the UI" is not protection.
- SSRF: any `wp_remote_get`/`wp_remote_post` whose URL is influenced by user input is validated first — `wp_http_validate_url()`, reject private/internal ranges, `wp_safe_remote_*` semantics / safe redirects.
- Object injection: never `unserialize()` (or `maybe_unserialize()`) data that crossed a trust boundary — store and transport JSON instead.
- Identifiers: `$wpdb->prepare()` placeholders do not cover table/column names or `ORDER BY` — use the `%i` identifier placeholder (WP 6.2+) or a strict allow-list.
- Timing: compare tokens, license keys and HMACs with `hash_equals()`, never `==`/`===` string comparison.
- Translations are third-party input: translated strings are escaped at output like any other variable (`esc_html__()`, `esc_attr__()`, or escape at the point of output) — a malicious `.po`/`.mo` is a real vector.

## Plugin-platform specifics

- Prefix everything (functions, classes, options, hooks) to avoid collisions — the user uses prefixes like `mcm/`.
- Uninstall cleanly (`uninstall.php` / uninstall hook) without leaving sensitive data unless the user opted in.
- Respect multisite if in scope (network vs site options/capabilities).
- Don't break on missing dependency (e.g. the required MCP Adapter plugin) — fail safe with an admin notice, not a fatal.
- Follow WordPress coding/security guidelines so it survives a .org or marketplace review.

## Phase test points (verify these during Phase 5)

- Every state-changing path: nonce + capability verified.
- Every REST route: real permission_callback + arg validation.
- Every output: escaped at output.
- Every query: prepared.
- MCP/OAuth: token validation + PKCE + per-ability authz confirmed; no secret logged.
- ABSPATH guard present in every PHP file; redirects via `wp_safe_redirect`; LIKE terms escaped; settings have sanitize callbacks.
- Uninstall path leaves no sensitive residue (unless opted in).

## Verify with

- `phpcs` with the WordPress standard including the security sniffs: `phpcs --standard=WordPress` — `WordPress.Security.*` must be clean.
- The Plugin Check plugin: `wp plugin check <slug>`.
- `composer audit` / `npm audit` when the plugin bundles dependencies.

At a test point, the command and its result are the evidence recorded in `docs/05-test-points.md` — an unrecorded check did not happen.
