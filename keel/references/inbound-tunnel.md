# Inbound tunnel — the playground receives calls from outside without a deployment

Load this at three moments: (a) Phase 2 §4 (Testing), when the functional spec's integrations include ANY call that an external system makes TO the project; (b) the Phase 5 scaffold, when `scripts/playground-tunnel` is generated; (c) every test point of a flow that depends on such a call. It is the companion of `references/playground-recipes.md` (what the environment is) and `references/test-automation.md` (who drives it): this file removes the one reason a locally driven flow used to stop halfway.

## The problem this ends

A playground lives on `localhost`. A payment gateway, a webhook sender, a remote client or any other system outside the machine cannot reach it. The flow therefore runs up to the point where the outside world must answer and stops there: the payment is authorised at the gateway and the order stays pending; the webhook is sent and never arrives; the remote client cannot connect. Everything after that point — the order paid, the token stored, the subscription renewed, the state machine advanced — is untested, and it is usually the part where the money is.

Three wrong answers follow from that, and all three are retired by this file:

- **"Deploy it to an online server to test it."** A staging deployment to receive a callback costs a server, credentials, a deploy loop per change, and moves the test off the assistant's machine, where it can no longer drive, reset or read the logs. Keel never asks for a deployment whose only purpose is to be reachable.
- **Tagging the whole flow `CREDENTIAL` or handing it to the user** because "it needs a publicly reachable webhook". Reachability is not a credential and is not the user's job.
- **Simulating the inbound call by hand** (a forged `curl` to the notification endpoint) and calling the flow verified. A hand-built request proves the handler parses what the assistant believes the provider sends. It does not prove what the provider sends, its signature, its timing or its retries. It stays useful as a unit-level check and is never the real exercise.

The answer is an inbound tunnel: a public HTTPS URL that forwards to the playground's local port for as long as the exercise lasts.

## What counts as an inbound call

Inventory these at Phase 2, from the spec's integrations, whatever the project type:

- Server-to-server payment notifications (Redsys, Stripe, PayPal, any gateway that confirms asynchronously).
- Webhooks of any kind: forges, messaging platforms, CRMs, shipping carriers, e-mail providers' delivery and bounce events.
- A URL the third party fetches from the project: a product feed, a callback image, a verification or domain-association file, an OAuth client metadata document.
- OAuth or SSO redirect URIs when the provider refuses `localhost` or requires HTTPS.
- A remote client that connects to the project: a hosted assistant connecting to a locally running MCP server, a mobile device on another network calling a local backend.
- Any browser feature that demands a real HTTPS origin and cannot be satisfied by `localhost`.

One row per inbound call in the technical plan: who calls, which endpoint, how the caller learns the URL (sent in each request, registered once at the provider, or typed by a person), and whether the hostname must be stable.

## The tool

**Default: a Cloudflare quick tunnel.** `cloudflared tunnel --url http://localhost:<port> --no-autoupdate` needs no account, no domain and no configuration, and prints a random `https://<name>.trycloudflare.com` URL that forwards to the local port. Cloudflare terminates TLS and forwards plain HTTP. Each run gets a new hostname.

Limits to know before choosing it, as Cloudflare documented them when this was written (re-check at Phase 2, vendors revise):

- The hostname changes on every run, so nothing that must be registered ahead of time survives a restart.
- Quick tunnels cap concurrent in-flight requests and do not carry Server-Sent Events. A flow that streams over SSE needs a named tunnel.
- A quick tunnel refuses to start when a `config.yml` already exists in the user's `.cloudflared` directory. That is the user's own configuration: report it, never move or edit it.
- It is a testing facility with no uptime guarantee. It is never a hosting answer.

**Named tunnel, when the hostname must be stable.** A provider that only calls URLs registered in its dashboard, a domain-association file, or an allow-list of redirect URIs needs the same hostname every run. That takes the user's Cloudflare account and a domain: the one-off setup is tagged `CREDENTIAL`, covers only that setup, and is guided and recorded like any other external setup step. Once it exists the assistant runs it exactly like the quick tunnel.

**Substitutes** (ngrok, Tailscale Funnel, the platform's own CLI forwarder such as a provider's `listen` command): allowed, recorded in the technical plan with the reason, and held to the same script contract, the same safety rules and the same evidence. A provider's own forwarder that replays real events to `localhost` is often the better choice for that provider and needs no public URL at all; prefer it when it exists and covers the flow.

**The provider's acceptance is tested, never assumed.** Some providers reject notification URLs on shared tunnel domains, on non-standard ports or without a valid certificate chain. Before scripting anything, open the tunnel by hand once and drive one real sandbox flow through it. Record the result as a D-entry: the provider, the date, and what arrived. If the provider blocks the shared domain, the named tunnel is the next step, not a deployment.

## `scripts/playground-tunnel` — the contract

Generated at the Phase 5 scaffold for every project whose technical plan lists at least one inbound call. One script, POSIX shell where the stack allows, three modes:

| Invocation | Does |
|---|---|
| `scripts/playground-tunnel` | Opens the tunnel, points the playground at its URL, prints the URL and the exact callback endpoint(s), then waits. Interrupting it closes the tunnel and restores `localhost`. |
| `scripts/playground-tunnel --url <https-url>` | Points the playground at a tunnel that is ALREADY open (one the user started, a named tunnel, a substitute). Opens nothing. |
| `scripts/playground-tunnel --restore` | Points the playground back at `localhost`. Idempotent. |

Rules every generated copy obeys:

- **Preflight before anything changes.** The playground answers on its local port, and the tunnel binary resolves. Otherwise exit 2 with one line naming what is missing and how to get it. Nothing is installed by this script; that is the doctor's job.
- **The port comes from the playground's own configuration**, read from the file that defines it, never hardcoded twice.
- **The URL is polled for with a bound, never slept on.** Read it from the tunnel's own output, give up after a stated number of seconds and print the tail of that output.
- **Restore on every exit path.** A `trap` on exit, interrupt and termination kills the tunnel process, removes its temporary files and puts the base URL back. A playground left pointing at a dead public hostname is broken for the next session in a way that looks like a product bug, so `--restore` also exists on its own.
- **Exit codes:** 0 done, 2 could not run. The script decides nothing else.
- **It never ships.** It lives in `scripts/`, outside the distributable, and the Phase 7 packaging check confirms neither it nor any helper it copies into the playground is in the release artifact.

### Pointing the playground at the tunnel

Opening the tunnel is half the work. The application builds the callback URL it hands to the provider from its own idea of its public address, and it must believe it is being served over HTTPS at the tunnel's hostname. Three things are settled per project, in the technical plan:

1. **The public base URL is one setting, switched by the script and switched back.** WordPress: `WP_HOME` and `WP_SITEURL` through `wp config set`. Web apps: the framework's public-URL setting through an environment variable the dev server reads. A product that hardcodes its callback host has a defect the tunnel has just found; fix the product.
2. **The proxy's scheme is trusted, in the playground only.** The tunnel forwards plain HTTP with `X-Forwarded-Proto: https`. An application that does not honour that header sees an HTTP request for an HTTPS site and redirects forever. WordPress: a small must-use plugin, copied in by the script while the tunnel is up and removed on restore, that sets `$_SERVER['HTTPS']` from the header. Elsewhere: the framework's trusted-proxy setting, enabled by the same environment switch. This shim is playground code. It never enters the product, because trusting a forwarded header unconditionally is a vulnerability on a server that is not behind that proxy.
3. **The dev server accepts the tunnel's Host header.** Dev servers that allow-list hosts (`allowedHosts`, `ALLOWED_HOSTS`, `config.hosts` and equivalents) reject the tunnel hostname with an error that reads like a tunnel failure. Add the tunnel domain to the development configuration only.

Where the caller learns the URL from a registration instead of from each request, the script performs the registration through the provider's API or CLI when one exists, and removes it on restore. Where registration is dashboard-only it is one `CREDENTIAL` leg with its steps, and a quick tunnel's changing hostname makes a named tunnel the practical choice.

## Who opens it

**The assistant, by default.** It is a documented command, and running documented commands is the assistant's job (`references/test-automation.md`). The whole exercise — open the tunnel, drive the flow in the browser, wait for the inbound call, assert the resulting state, read the logs, close the tunnel — is one driven test.

**A session whose permissions deny opening an ingress is the measured exception, and it costs one command, not the flow.** Some environments refuse to let the assistant publish a local port, and that refusal is a deliberate guard: do not work around it with another tool or a different binary. The user runs `scripts/playground-tunnel` or the bare tunnel command in their own terminal, the assistant attaches with `--url`, drives everything else, and runs `--restore` afterwards. The launch alone is recorded under the partial `NO-EXECUTION` case, naming "ingress tunnel" as the unreachable half. The criterion itself is still `driven`. This is exactly why `--url` and `--restore` are separate modes.

## Safety — the tunnel publishes the playground

While it runs, anyone who has the URL reaches the playground, including its admin login with the throwaway credentials written in `docs/playground.md`.

- **Only the synthetic playground is ever tunnelled.** Never a site holding real data, a shared staging server, a production database copy, or a machine-wide service. This is the confidential-data rule applied to exposure.
- **Sandbox and test credentials only.** A tunnelled playground never carries live merchant keys.
- **Open for the exercise, closed after it.** The tunnel is started for a test point and stopped when it ends. It is never left running between sessions, in the background, or "for convenience". A session that ends with a tunnel open has a defect to fix before it closes.
- **The URL is not a secret and is not treated as one**, but it is not published either: not in commits, issues or public notes. A quick-tunnel hostname is dead after the run anyway; a named tunnel's hostname is the user's.
- **A security audit (`references/security-audit.md`) runs with the tunnel closed**, unless the unit under audit is the inbound handler itself, in which case only that check holds it open.

## Evidence

The row in `docs/05-test-points.md` records, beside the usual command and commit:

- **The negative control, once per inbound call.** The same flow driven without the tunnel, and the stalled state it leaves (the order still pending, the event never recorded). Then the flow through the tunnel and the completed state. The pair is what proves the inbound leg is the thing being exercised. A single green run does not, because a flow can complete for the wrong reason.
- **The inbound request as the application saw it:** the product's own debug-log line for the received call, with its outcome. This is the read-back duty applied to a request the browser never sees.
- **The sandbox identity used**, by name of the public test fixture. A merchant's or client's own test identifiers are passed through environment variables and never written to the repository.

The tunnel serves the live drive first (`references/test-automation.md`, "The live drive"): each new or changed behaviour that involves an inbound call is exercised by the assistant in a real browser against the tunnelled playground, with the real sandbox on the other end, before the slice is accepted. Committed tests come on top of that.

Automated end-to-end suites that need the tunnel are marked so they run only when it is up, and skip with a stated reason otherwise. A test that silently passes without its inbound leg is worse than one that does not exist.

## What it does not replace

- **The Phase 7 real-environment verification.** Installing the exact distributable in a real environment of the right type remains the hard gate. The tunnel proves the flow; it does not prove the package.
- **Legs that only exist against the live system.** Those stay `PRODUCTION-RISK`, one leg at a time.
- **Provider onboarding.** An agreement, an activation or a review the third party must grant is `EXTERNAL-APPROVAL` with or without a tunnel.

## Where it is written down

- `docs/03-technical-plan.md` §Testing: the inbound-call inventory, the tunnel choice with its reason, the three "pointing" settings, and the tunnel binary as a row in `## Environment requirements`. Severity `optional`: its absence blocks only the flows that need it, and those are recorded `⚠ unverified`, never skipped silently.
- `docs/playground.md`: a section with the three invocations, what is exposed while it runs, the sandbox fixture, and the date and result of the last real run.
- `docs/decisions.md`: the provider-acceptance test and the tunnel choice.

## Definition of done (this reference)

- Every inbound call in the spec is inventoried in the technical plan with its caller, endpoint, how the URL is learned, and whether the hostname must be stable.
- `scripts/playground-tunnel` exists with its three modes, restores on every exit path, and is excluded from the distributable.
- The provider's acceptance of the tunnel URL was tested by hand before the script was trusted, and recorded.
- Each inbound flow has a driven exercise through the tunnel with its negative control and the application's own log line as evidence.
- No flow was deployed to an online server, handed to the user, or replaced by a forged request for lack of reachability.
- The tunnel is closed and the playground is back on `localhost` when the session ends.
