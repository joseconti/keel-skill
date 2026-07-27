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

## Deliberate omissions (seed the "Not defended" table)

This profile hardens what it covers and is silent on the rest. Silence is not protection, so the
project's `docs/threat-model.md` (Phase 2 §4c) carries a "Not defended" table naming what is
deliberately out of scope, its consequence, and what the user would add if their risk profile needs
it. **An omission that is written down is a decision; an omission that is silent is a trap** — six
months on, nobody can tell "we decided against it" from "we forgot".

Start from these rows, keep the ones that apply, add the project's own, and move any row into the
"Defended" table the moment the control actually ships with its evidence:

| Not defended | Consequence | If you need it |
|---|---|---|
| Volumetric denial of service | The site becomes unavailable under a flood | CDN or WAF rate limiting in front of the origin |
| Compromise of the host or the deploy account | Whoever controls the pipeline controls what is served | MFA on the host and forge accounts, and branch protection on the deployed branch |
| Third-party embeds and their content | An embedded widget executes in the page's context and can change what it does after launch | Sandbox iframes, pin script sources, and keep the embed count near zero |
| Form submissions from a determined abuser | Anti-spam measures raise the cost; they do not make abuse impossible | Server-side rate limiting per IP and per address, plus moderation before anything is published |
| Content integrity between deploys | A static site serves whatever was last deployed, correct or not | Subresource integrity on external assets, and a post-deploy smoke check that the expected content is live |
| Visitor privacy beyond the consent banner | Whatever the loaded third parties collect is collected | Remove the third party — the only real control — or self-host the equivalent |

Every remaining control in the "Defended" table carries its delivery state — `IN PLACE` (built and
verified), `TO BUILD` (a named slice), `MANUAL` (a human configures it) or `VERIFY` (only a real
environment confirms it) — and only `IN PLACE` may be written in the present tense anywhere in the
project's documentation.
