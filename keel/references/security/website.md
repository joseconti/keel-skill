# Security Profile — Website (static / marketing / product site)

Load this when the project is a static, marketing, or product website — the Phase 8 default. A site with an app backend (accounts, APIs, server logic beyond a contact form) loads `references/security/web-app.md` as well; the stricter rule wins on conflict. Apply from the first section built; verify on the LIVE site at launch. The attack surface is small — keep it small.

## Transport & headers

- HTTPS only, with valid TLS; HTTP redirects to HTTPS. HSTS set (`Strict-Transport-Security`).
- Content-Security-Policy appropriate for a vanilla static site: `'self'` plus the explicitly approved third-party origins, nothing else.
- `X-Content-Type-Options: nosniff`.
- `Referrer-Policy` set — the meta referrer decision from the SEO checklist (`references/phase-8-technical-seo.md`) and this header must agree.
- Clickjacking defense: `frame-ancestors` in the CSP or `X-Frame-Options`.
- All of it verifiable with `curl -sI` against the LIVE site — the launch checklist runs exactly that.

## Forms & mail

- The contact endpoint is usually the site's only dynamic surface — treat it as the attack surface it is.
- Validate and length-limit every field server-side; client-side validation is UX, not security.
- Rate-limit the endpoint.
- Anti-spam by default: honeypot field + minimum-submit-time trap. No third-party CAPTCHA by default; if the user approves one, it MUST have an accessible alternative, per WCAG (`references/accessibility.md`).
- If the form sends mail: fixed sender aligned with SPF/DKIM/DMARC; user input never reaches mail headers (header injection); the visitor's address goes in reply-to.

## Mixed content & third parties

- Zero mixed content: every request on every page is HTTPS.
- Every approved third-party script (the recorded vanilla exceptions) loads over HTTPS from a pinned URL, with Subresource Integrity where the host supports it.
- Preconnect only to approved origins.

## Deploy integrity

- Who can publish is defined and recorded.
- Deploy tokens/credentials live outside the repo — the cross-cutting confidential-data rule applies.
- The deploy pipeline or upload path is itself access-controlled.
- If a static-site generator was approved, its toolchain is a dependency: updating it on CVEs is a maintenance duty (`references/maintenance.md`).

## Phase test points (verify during Phase 5 for dynamic parts; all of it live at launch)

- Headers verified live: HSTS, CSP, `X-Content-Type-Options`, `Referrer-Policy`, frame-ancestors present and correct via `curl -sI`.
- Form abuse attempted: honeypot filled → rejected; N rapid submissions → rate-limited; oversized/invalid fields → rejected server-side.
- Mail-auth check on a received test message: SPF/DKIM/DMARC pass for the fixed sender; no user input in headers.
- Mixed-content scan of every page: zero non-HTTPS requests.

## Verify with

- `curl -sI https://<domain>/` per header (HSTS, CSP, `X-Content-Type-Options`, `Referrer-Policy`, `frame-ancestors`/`X-Frame-Options`).
- An SSL/TLS check (`testssl.sh` or SSL Labs): valid chain, no weak protocols.
- The form abuse attempts above, executed against the deployed endpoint.
- Browser devtools (network panel) or a crawler pass over every page for mixed content.

At a test point, the command and its result are the evidence — recorded in `docs/05-test-points.md` during development and `<site-docs>/launch-report.md` at launch; an unrecorded check did not happen.
