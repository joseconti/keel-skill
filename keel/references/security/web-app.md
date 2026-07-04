# Security Profile — Web App / API / Hosted Service

Load this for SPAs, API backends, or hosted services (e.g. on Fly.io). Apply from Phase 1, verify at every Phase 5 test point.

## Input / output

- Validate every input against a strict schema (type, range, length, format). Reject by default; allow-list, don't block-list.
- Encode/escape output for its sink (HTML, attribute, URL, JSON, SQL). Prevent XSS in the client; never `innerHTML` untrusted data.
- Parameterized queries / ORM bindings only — never string-built SQL.
- **SSRF:** if the server fetches user-supplied URLs (webhooks, imports, previews), allow-list destinations and block internal ranges/metadata endpoints (169.254.169.254, localhost, RFC 1918) — never fetch a raw user URL.
- Uploads: validate type/size server-side, store outside the web root or with non-executable permissions, serve with a safe content type.
- Set a strict Content-Security-Policy and the standard security headers (HSTS, X-Content-Type-Options, Referrer-Policy, frame-ancestors).

## AuthN / AuthZ

- Strong session/token handling: short-lived access tokens, rotated refresh tokens, secure+httponly+samesite cookies. OAuth 2.1 + PKCE for public clients.
- Authorization checked server-side on every request, per resource and action — never trust the client to hide a button.
- Rate-limit auth endpoints; lock out / back off on brute force; generic auth error messages (don't reveal which factor failed).
- CSRF protection on cookie-authenticated state-changing requests.

## Secrets & config

- Secrets only from environment or a secret manager; never in the repo, the image, or client bundles. Verify the client build contains no server secret.
- Separate config per environment; no production secret in dev.
- Rotate-able credentials; document rotation in `docs/security.md`.

## Data

- Encrypt in transit (TLS everywhere) and at rest for sensitive data. Minimize PII; define retention.
- Principle of least privilege for DB and service accounts.
- Log security-relevant events without logging secrets, tokens, or full PII.

## Service / infra (e.g. Fly.io)

- Lock down exposed ports/services to what's needed; no debug endpoints in production.
- Pin and scan dependencies; rebuild on advisories. No known-vulnerable packages shipped.
- Health/liveness endpoints must not leak internal detail.
- Graceful failure: no stack traces or internal config to the client on error.

## Phase test points (verify during Phase 5)

- Every endpoint: schema validation + server-side authz + rate limiting where relevant.
- AuthN flow: token lifetimes, refresh rotation, cookie flags, CSRF on state-changing requests.
- No secret in client bundle or image.
- Security headers + CSP present and effective.
- Error responses leak nothing internal.
- Dependency scan clean.
