# Estimation & Budget — AI-time based (cross-cutting)

Load this reference at these moments, and only these:

- **Close of Phase 1 (Discovery)** → produce the **preliminary estimate** (ranges), so the user can answer a client quickly.
- **Close of Phase 2 (Functional spec + technical plan)** → produce the **firm estimate** and the **client-facing budget**.
- **Any recorded scope change after a budget exists** → recompute and issue a new budget version (see "Scope changes").
- **Adoption / existing projects**: when the user needs to quote a piece of planned work (remediation sprint, new feature) to a client, run the same procedure on that scope.
- The user asks "what would this cost / how long will this take" at any point.
- **End of every working session (and every phase/sprint close)** → append the session's row to `docs/token-ledger.md` (see "The token ledger" below — one line, cheap).

## The rule this reference exists for (UNBREAKABLE)

**Budgets are computed from AI working time plus the vibe coder's supervision time — NEVER from traditional human development time.** Keel does not estimate, present, or use "what a human team would take" (weeks/months): that number belongs to a different way of building software and produces absurd quotes for AI-driven work. The client pays for what delivery actually requires: the AI's working sessions, the developer's real hours controlling the AI, and (when applicable) the AI's token cost. If the user wants a human-team comparison for marketing, that is their call — Keel does not produce it by default.

The honest-assessment principle applies to numbers too: **realistic over optimistic**. Include iteration, Design Requests, bug fixing, and an explicit contingency. Ranges, not false precision. State every assumption. An estimate that looks great and blows up mid-project is exactly the failure this skill exists to prevent.

## Itemized breakdown is mandatory (partidas)

Every estimate and every budget is broken down into **itemized lines (partidas)** — never a single global number. Each line has: the segment (tramo), **what is actually done in it**, and its hours (range). Totals come *from* the lines. This is what lets the user defend the quote line by line, and lets the client see what they are paying for. The budget then prices each line (hours × rate = amount per line).

## Step 1 — AI working hours (itemized per phase)

Estimate the AI's **session wall-clock time**: what the working sessions actually take end to end (planning, generating, writing code, running tests, fixing, documenting), including the waiting-on-user gaps compressed out — i.e. active session time. Scale each line by the scope actually known (features, flows, screens, slices, integrations, external-setup items). At Phase 1 close use the v1 feature list; at Phase 2 close use the real spec (slice count from the technical plan).

Baseline table — adjust per project and say why (state the scope basis next to each line):

| Segment (AI does) | Typical session hours |
|-------------------|-----------------------|
| Phase 1 — competitive scan + discovery docs | 1–3 h (more with many competitors) |
| Phase 2 — functional spec, flows, technical plan | 1–3 h (scales with features/flows) |
| Phase 3 — design brief + Design producing the handoff | 1–4 h (scales with screens; template reuse lowers it) |
| Phase 4 — handoff audit, BUILD-SPEC, guided external setup | 1–3 h (scales with setup items / Design Requests) |
| Phase 5 — development | the bulk: **0.5–2 h per slice** (code + tests + docs + test point) |
| Phase 6 — documentation consolidation | 1–2 h |
| Phase 7 — release | 0.5–1.5 h |
| Phase 8 — website (only if intent = yes; usually quoted separately) | 3–8 h |

Add **contingency** (default +20–30%; the user can adjust): iterations, Design Requests, regressions, re-planning. Always a visible line, never silently baked into the segments.

## Step 2 — Vibe coder hours (itemized per segment)

The developer's time controlling the AI is real, billable work — never present it as zero. It has two components:

**(a) Supervision alongside the AI** — answering the batched questions, making decisions, approving phase gates, unblocking the AI. Presence factor per phase (of the AI hours): Phases 1–2 ≈ 60–90% (highly interactive), Phases 3–4 ≈ 30–50%, Phase 5 ≈ 20–40% (the AI codes; the developer opens sessions, reads summaries, approves gates, answers blockers — often a **daily cadence of 20–45 min/day** across the build's calendar days), Phases 6–7 ≈ 20–30%.

**(b) Developer-only work the AI cannot do** — estimated per item, typically 0.25–1 h each: external setup (hosting, domain/DNS, API keys, OAuth consoles, payment gateway config, email); real-world testing in the playground as a real user (flows end to end, real devices, gateway test mode, email deliverability); pushing code / PRs / deploys / marketplace submission; and any client-side bridge (forwarding validation packages, coordinating UAT, collecting feedback) when a third party is involved.

Present it as an itemized table — this exact shape (segments adapted to the project):

| Segment | What the developer does | Hours |
|---------|-------------------------|-------|
| Phases 1–2 (kickoff) | Answer question batches, approve spec and design direction | e.g. 2.5–3.5 h |
| Infrastructure / external setup | Hosting, domain, DNS, API keys, gateway, email (guided step by step) | e.g. 1–1.5 h |
| During the build (N calendar days) | Open sessions, read summaries, approve gates, unblock questions (20–45 min/day) | e.g. 4–8 h |
| Test points | Try the flows in the playground as a real user | e.g. 2–3 h |
| Client bridge (if a third party exists) | Forward validation package, return corrections, coordinate UAT | e.g. 3–5 h |
| Final stretch | Correction rounds, deploy to production, pilot/first release | e.g. 4–7 h |

Close the table with: **total (range)** → **planning figure with margin** ("plan for X h") — and, once the rate is known, the cost at the rate. Apply the same contingency policy as Step 1.

## Step 3 — Ask the user (batched — use the interactive question tool if available)

Never assume any of these; ask them together when producing the firm budget (at the preliminary estimate, ask only for what the user wants included):

1. **Hourly rate and currency** for the developer's hours (one rate by default; per-segment rates only if the user wants them).
2. **AI access mode**: subscription (Claude Pro/Max — no marginal per-token cost) or **API pay-per-token**; and which model(s) will be used (e.g. a top model for planning, a mid model for code).
3. **Contingency %** (default 20–30%).
4. **Budget language** — the budget is a client-facing deliverable: ask which language the client reads and write `docs/budget.md` in it (the internal `docs/estimate.md` stays in English per SKILL.md "Token economy").
5. **Taxes**: amounts are stated tax-exclusive with a note (e.g. "+ IVA / VAT") unless the user says otherwise. Keel does not compute tax regimes.
6. **Availability**: how many hours/week the developer will dedicate → converts hours into an estimated **calendar delivery** (always labeled as an estimate).
7. Optional: quote validity period, payment terms, fixed price vs hours. If the user converts the estimate into a **fixed price**, the risk margin on top is their business decision — recommend one explicitly (contingency + margin), never a bare optimistic number.

## Step 4 — AI cost (tokens, per model)

Two modes:

- **Subscription** (Claude Pro/Max or similar): the marginal token cost of this project is ≈ 0 — the user already pays a flat monthly fee. Record the mode in the estimate; the **default recommendation** is not to bill the AI as a separate line (it is not an extra expense), and the supervision hours are already billed as developer hours. Whether to bill it anyway (as tooling overhead) is the user's call in Step 6.
- **API pay-per-token**: estimate and price it:
  1. **Estimate total tokens** per project size — order of magnitude, state as ±50% and round up: small (≤5 slices) ≈ 5–15M total tokens; medium (6–15 slices) ≈ 15–40M; large (16+ slices) ≈ 40–100M+. Input tokens typically run 3–8× output tokens (state re-reads, iteration); Keel's fixed reading order and stable artifacts keep the effective input cost near the low end thanks to prompt caching (cache reads are ~0.1× input price on Anthropic).
  2. **Verify current prices before quoting — ALWAYS.** Model prices change. Check the provider's official pricing page (Anthropic: `https://platform.claude.com/docs/en/about-claude/pricing`; other providers: their own page) with the web tool. If the environment has no web access, use the fallback table below, state its date in the estimate, and say the price should be re-verified.
  3. Compute: `input tokens × input price + output tokens × output price`, with the cached-input share stated as an assumption. Give a cost **range**, not a point.

Fallback table — Anthropic API, **verified July 2026** (per million tokens; cache read ≈ 0.1× input; batch −50%):

| Model | Input | Output |
|-------|-------|--------|
| Claude Fable 5 / Mythos 5 | $10 | $50 |
| Claude Opus 4.8 | $5 | $25 |
| Claude Sonnet 5 | $2 (announced $3 from Sept 2026) | $10 (announced $15) |
| Claude Haiku 4.5 | $1 | $5 |

## Step 5 — `docs/estimate.md` (internal, English, versioned within the file)

```
# Estimate — [Project name]

> Internal working estimate. AI-time based: AI session hours + vibe coder hours.
> Never based on traditional human development time.

## Estimate v[N] — [preliminary (Phase 1 close) | firm (Phase 2 close)] — [date]

### Scope basis
[counts this estimate is computed from: features, flows, screens, slices, integrations,
external-setup items — citing 01-discovery / 02-functional-spec / 03-technical-plan]

### AI working hours (itemized)
| Segment (AI does) | Hours (low–high) | Basis |
Total AI: X–Y h

### Vibe coder hours (itemized)
| Segment | What the developer does | Hours (low–high) |
Total developer: X–Y h → plan for Z h (with margin)

### Contingency: +N% → totals with contingency
### Estimated calendar delivery: [from hours + the user's stated availability]

### AI cost
Mode: [subscription — no marginal cost | API pay-per-token]
[if API: model(s), token estimate (±50%), prices with source + verification date,
cached-input assumption, cost range]

### Assumptions & risks
[what could move the numbers; unknowns; anything excluded]
```

Actuals are recorded in `docs/token-ledger.md` as the project runs; the final reconciliation at release closes the loop (see "The token ledger" below).

Preliminary (v1) uses wide ranges and says so. Firm (v2+) narrows them from the real spec. Never overwrite a previous version's section — append the new one (the history shows how the numbers evolved).

## Step 6 — `docs/budget.md` (client-facing, in the client's language)

Written in the language asked in Step 3.4, with perfect orthography. **The two cost blocks are always separate** — developer services and AI cost — so the user decides exactly what the client sees and what gets billed:

```
# Budget — [Project name] — v[N] — [date]

## Scope summary        [plain-language, from the spec — what will be delivered]
## Deliverables         [the concrete list, including docs/support/warranty terms if agreed]

## Block 1 — Professional services (developer)
| Segment | What it covers | Hours | Rate | Amount |
[the Step 2 segments, priced line by line]
Subtotal — developer: ...

## Block 2 — AI tooling
[API mode: model(s) + estimated cost range |
 subscription mode: "included — no additional cost" or a line item, per the user's choice]

## Contingency          [if agreed as a visible line: +N% → amount]
## Total                [sum; taxes excluded — e.g. "+ IVA" — unless the user said otherwise]

## Estimated delivery   [calendar estimate, labeled as estimate, tied to the availability assumption]
## Terms                [quote validity, payment terms, what is included/excluded,
                         change policy: scope changes trigger a budget revision (new version)]
```

If the user wants a shareable file (PDF or similar) and the environment can produce it, generate it from `docs/budget.md` — the markdown stays the source of truth.

## Step 7 — Present, adjust, approve (mandatory loop)

1. Present both artifacts: the internal estimate (how the numbers were built) and the client budget.
2. Ask explicitly: **does the budget look right, or do you want adjustments?** Typical adjustments, offered proactively: not billing the AI cost (subscription = no extra expense); rounding totals; adding a commercial margin; a different rate; folding contingency into the rate; removing segments the user will not charge for.
3. Iterate until the user **explicitly approves**. Client acceptance is the user's business — Keel does not block the project on it, but the budget document itself must be approved by the user before it is considered done.
4. Record the approval and every choice made (rate, AI-cost decision, contingency, fixed price vs hours) as a D-entry in `docs/decisions.md`; update `docs/PROGRESS.md`.

## The token ledger — actuals, recorded as the project runs (`docs/token-ledger.md`)

An estimate without actuals never improves. From the first estimate on, actual token usage is recorded in `docs/token-ledger.md` — one row per working session, appended at session end and verified at phase/sprint closes. Create it together with Estimate v1.

```
# Token Ledger — [Project name]

> Actual token usage. One row per working session, appended at session end.
> Method is always stated: measured (environment counter, API usage, provider dashboard)
> or estimated (volume-based). An honest estimate beats an empty cell.

## Sessions
| Date | Phase/sprint | Model(s) | Input tokens | Output tokens | Method | Notes |
|------|--------------|----------|--------------|---------------|--------|-------|

Running total: [input] / [output] — updated with each row.

## Final reconciliation (at release — Phase 7)
- Total tokens by model: ...
- Cost at verified prices (source + date): ...
- Estimate vs actual: estimated [range] → actual [figure] → deviation [±%]
- Lesson for future estimates: [one line; if significant, also an L-entry in docs/lessons-learned.md]
```

How to get the numbers, in order of preference:

1. **Measured** — whatever the environment exposes: a session cost/usage counter (e.g. Claude Code's `/cost`), API usage logs, or the provider's console/dashboard (ask the user to read it out when exact figures matter).
2. **Estimated** — when nothing is exposed (typical in subscription apps): estimate from the volume actually produced and read (≈ 4 characters per token in English), state the method, round up. Never leave the row blank because measurement was unavailable — and never present an estimated row as measured.

At release, Phase 7 runs the **final reconciliation** as part of its artifacts: total the ledger by model, price it at verified current prices, compute the deviation vs the estimate (tokens and cost; hours too if the user tracked them), report it to the user plainly, and record the calibration lesson — every finished project makes the next project's estimate better.

## Scope changes (after a budget exists)

Any scope change recorded in `decisions.md` that affects the work (new feature, dropped feature, changed integration) → recompute the affected lines, append **Estimate v[N+1]** to `docs/estimate.md`, produce **budget v[N+1]**, and run Step 7 again. The budget never silently drifts from the recorded scope; "we'll absorb it" is a user decision to record, not a default.

## Definition of done (each run of this reference)

- `docs/estimate.md` has the new version: itemized AI hours, itemized vibe coder hours (segment | what the developer does | hours), contingency, calendar estimate, AI cost with mode — and, if API, prices with source and verification date. All grounded in the recorded scope, with assumptions stated.
- The Step 3 questions were asked and answered (firm budget), including rate + currency and the budget language.
- `docs/budget.md` produced in the client's language, itemized per segment with amounts, the developer block and the AI block **separate**, total and terms present.
- The user explicitly approved the budget (or adjustments were applied and re-approved); the approval and its choices are recorded in `docs/decisions.md`; `docs/PROGRESS.md` updated.
- `docs/token-ledger.md` exists from Estimate v1 on, with a row per working session (method stated); at release the final reconciliation (totals by model, cost at verified prices, deviation vs estimate, calibration lesson) is done and reported to the user.
- No number anywhere is based on traditional human development time.
