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

- The MCP Adapter endpoint and `/mcp/` requests must enforce Bearer token validation; 401 with the correct `WWW-Authenticate` pointing to resource metadata when missing/invalid.
- OAuth 2.1 with PKCE (S256): validate code challenge/verifier; never accept a public client without PKCE.
- Scope every MCP ability to a capability; do not expose a privileged ability without an authorization check equivalent to the underlying WP capability.
- Never log tokens, secrets, or full Authorization headers.

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
