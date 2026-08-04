# Phase 8 — Project Website: Art Direction

Run this BEFORE the design brief is written, after the section catalogue and before `references/phase-8-design-direction.md` is filled in. It produces the site's visual language as a set of recorded decisions, so Design is not left to invent it — and so two sites built by Keel a month apart do not come out looking like the same site.

`phase-8-design-direction.md` is the logistics of the visual handoff: vanilla, self-hosted fonts, reserved screenshot slots, imagery strategy, accessibility intent. This reference is the *language* those logistics carry. Both go into the brief; neither replaces the other.

## Why this exists

Keel is built against drift: never invent silently, code adapts to the design, divergence is a Design Request and never a creative choice. That discipline is correct everywhere except at the one point where inventing IS the work. A process tuned so that nobody invents anything, arriving at the only step that requires invention with nothing to offer, returns the model's default — which is a look every reader has already seen a thousand times, and which reads as generic precisely because it is.

The failure has a shape and it is worth naming, because it is not "the design was bad". The design is usually competent. It is that **every site comes out resembling the last one**, and it has three causes that compound:

1. **The brief asks for the aesthetic in adjectives.** "Technical and sober", "minimal and editorial", "bold". An adjective is a pointer to the average of everything that adjective has ever described. Ask for "clean and modern" and you get the mean of clean and modern. Field-tested and repeatedly: adjectives return the average, structural instructions return a decision.
2. **Nothing is forbidden.** Keel asks the user for vetoes at discovery (`phase-1-discovery.md`) but contributes none of its own. A model with no blacklist reaches for the patterns most represented in its training data, which are exactly the patterns that read as machine-made.
3. **Nothing remembers the previous site.** Keel has project memory (`PROGRESS.md`, `decisions.md`, `lessons-learned.md`) and class memory (`anti-patterns.md`). It has no memory ACROSS projects. Two similar briefs must produce the same site, because nothing in the system knows the other one exists. This is the cause that produces the complaint as it is actually voiced: *they all look too similar*.

The answer is not to loosen the anti-drift discipline. It is to open one bounded, rule-governed step where invention is mandatory, close it with a recorded decision, and let the normal regime resume. After the direction is chosen and written into `docs/decisions.md`, everything is exactly as strict as before: divergence is a Design Request.

**Attribution.** The Design Read, the numeric dials, the literal-blacklist approach and the pre-flight-as-gate are adapted from `taste-skill` by Leonxlnx (MIT). They are adapted, not imported: that skill targets React / Next.js / Tailwind / Motion and prescribes npm design-system packages, all of which this phase's vanilla rule forbids. Nothing framework-bound survives the adaptation. The divergence round, the signature element, the evidence dial and the anti-repetition ledger are Keel's own and have no counterpart there.

---

## Step 1 — Declare the Design Read

Before any dial, any reference, any token: one sentence, written down, that states how this site was read. It is the record that a reading happened instead of a default firing.

> **Reading this as:** a `<site type>` for `<audience>`, archetype `<archetype>`, leaning toward a `<named aesthetic family>` language.

Archetypes Keel actually builds (pick one; if none fits, name the new one rather than forcing a fit):

- **Technical product catalogue** — several products, prices, versions, compatibility, real screenshots. Buyers compare before they buy, so density and evidence beat atmosphere.
- **Single-product landing** — one thing, one decision, one CTA.
- **Developer tool / library** — the audience reads code before copy. Documentation entry is the primary CTA, not a signup.
- **Docs micro-site** — reading comfort and navigation are the design.
- **Author / practice site** — the person is the product; credibility carries the page.

The read is not a mood. It names an audience and an archetype, both of which have consequences the rest of this reference reads. A read that could be pasted onto any other project has not been done.

**If the read genuinely diverges** — two defensible readings with different consequences — ask the user ONE question naming the two, and do not guess. If it can be inferred confidently from discovery, do not ask.

---

## Step 2 — Set the four dials

Four numbers, each stated with the one-line reason it holds that value. A dial silently left at its preset is not set; the reason is what makes it arguable later.

- **`LAYOUT_VARIANCE` 1-10** — 1 is a strict symmetric grid, everything centred, every row the same shape. 10 is asymmetric composition, deliberate imbalance, sections that do not share a skeleton. Drives the section-layout repetition rule below.
- **`VISUAL_DENSITY` 1-10** — 1 is gallery air, one idea per viewport. 10 is a packed catalogue: comparison tables, spec rows, price columns. Drives whitespace, type scale and how much fits above the fold.
- **`MOTION_INTENSITY` 1-10** — 1 is static. 10 is choreographed. Bounded by the vanilla rule: no animation library, so this is CSS transitions, CSS animations, scroll-driven animations and `IntersectionObserver`. **Above 3, `prefers-reduced-motion` handling is mandatory and specified per animated element**, not added later.
- **`EVIDENCE_RATIO` 1-10** — the proportion of the page that is real, checkable content (product screenshots, actual prices, version numbers, real code, named references, concrete counts) against decoration, abstraction and atmosphere. Low is a mood board. High is a page that could be fact-checked line by line. This dial has no counterpart in any external design skill and it is the one that separates a credible technical catalogue from a landing page: **a technical audience discounts a site in proportion to how much of it is unfalsifiable.**

### Presets by archetype

Presets, not defaults — they are the starting point the read then argues with.

| Archetype | `LAYOUT_VARIANCE` | `VISUAL_DENSITY` | `MOTION_INTENSITY` | `EVIDENCE_RATIO` |
|---|---|---|---|---|
| Technical product catalogue | 6 | 7 | 3 | 9 |
| Single-product landing | 7 | 4 | 5 | 7 |
| Developer tool / library | 5 | 6 | 2 | 9 |
| Docs micro-site | 3 | 5 | 2 | 8 |
| Author / practice site | 8 | 4 | 4 | 6 |

Two overrides bind harder than the read: a site in an accessibility-critical or regulated context caps `MOTION_INTENSITY` at 3 and `LAYOUT_VARIANCE` at 5; and inheritance from an existing brand design system (`phase-8-design-direction.md` §1) constrains type, colour and component shape regardless of what the dials would prefer — the dials then govern composition, density and motion only, which is still most of what makes a site distinct.

---

## Step 3 — Read the anti-repetition ledger BEFORE proposing anything

The ledger is a machine-local file at **`~/.keel/art-ledger.md`** — outside every repository by construction, because its whole job is to span projects. It is never committed anywhere and never travels with the skill.

Read it first. The entries for the **three most recent sites** are a live constraint on this one:

- The primary typeface family, and the pairing, are unavailable. Not "vary the weight": a different family.
- The palette family and the accent hue are unavailable.
- The hero paradigm is unavailable.
- The grid family is unavailable.
- Every signature element is unavailable.

**Missing, empty, or unparsable ledger:** proceed with no constraint, say so in one line, and write the entry at the close. Never block on it, never reconstruct it from memory, never invent past entries. An absent ledger is an absent constraint, not an error.

**When the constraint bites** — a project whose brand system already fixes the typeface, or an archetype so narrow that the last three used the only sane hero — say so explicitly, name what could not be varied and why, and vary something else instead. The ledger's purpose is variety, and a forced-bad decision taken to satisfy it defeats the purpose. What is never acceptable is silently repeating and not mentioning it.

### Entry format

One block per site, appended, newest last:

```
## <site name> — <YYYY-MM-DD>
Archetype: <archetype>
Dials: variance <n> / density <n> / motion <n> / evidence <n>
Type: <primary family> + <secondary family>
Palette: <family name> / accent <hue name>
Hero: <hero paradigm name>
Grid: <grid family name>
Signature: <element 1>; <element 2>
```

The entry is written by the assistant at the close of this reference, from the direction actually chosen — never by hand, never predicted before the choice, never left for the user to maintain. A ledger somebody has to remember to update is a ledger that promises a guarantee it does not deliver, which is worse than not having one.

---

## Step 4 — The divergence round (this is the engine)

Everything above narrows. This step is the only one that generates, and it is what actually produces a site that does not look like the last one.

**Before the full brief, Design produces three directions for ONE section.** Not three sites, not three pages: one section, the one that carries the site's identity — normally the hero, or the product card for a catalogue archetype, or the documentation index for a docs micro-site.

The three are governed:

1. **Each belongs to a different named aesthetic family**, and the name is stated. Not "option A / B / C": a family with a name has a centre of gravity and can be argued about. Three variations on one family is one direction shown three times, and it is the most common way this step is performed without being done.
2. **At least one is a deliberate risk** — a choice that could be rejected outright. The safe-safe-safe triad returns the average through a longer route. If the risky one is never the one chosen, that is fine; its job is to widen what the other two are compared against.
3. **Each is delivered with what it commits to**: its tokens (type, palette, spacing, radii, border treatment), its named hero or card paradigm, and one sentence on why it fits the Design Read. A direction without tokens is a picture, not a direction.
4. **None may reuse anything the ledger blocks.**
5. **All three respect the blacklist** in step 6, the dial values from step 2, and the accessibility floor. Divergence is in the language, never in the conformance.

The user chooses one, or asks for two to be consolidated (naming what to take from each). **The choice is recorded in `docs/decisions.md` as a decision entry** with the alternatives that were rejected, and that closes the subject: from this point the normal Keel regime resumes and any later divergence is a Design Request, never a creative choice.

**Cost, stated plainly:** one extra Design round on one section. It is the cheapest possible place to spend it and, in practice, the only step that reliably produces originality — an aesthetic asked for with adjectives comes back as the average no matter how many adjectives are used.

**This step is not optional and not skippable for time.** If the user waives it, that is a recorded `docs/decisions.md` entry naming what was traded away, exactly like waiving any other Keel gate.

---

## Step 5 — Consolidate the signature elements

From the chosen direction, name **one or two elements that recur across the whole site and belong to this project alone.** Not the palette and not the typeface, which are inheritance-level decisions: a treatment. A border behaviour. A way a screenshot meets its frame. A table row's anatomy. A single typographic move used consistently and nowhere else.

This is what makes a site recognisable rather than merely inoffensive. A page can pass every blacklist item, hit every dial and still be forgettable, because avoiding what is wrong is not the same operation as having something of its own.

Each signature element is declared in `SPEC/art-direction.md` with: what it is, exactly where it recurs, and its CSS treatment (`references/handoff-contract.md`, "Website projects add two files to `SPEC/`"). It becomes a checkable item in the Phase 4 completeness gate, and it goes into the ledger so no later site reuses it.

---

## Step 6 — The blacklist

Literal, so it can be audited. A vague prohibition is not a gate: "avoid generic layouts" cannot be checked and therefore is not a rule. Everything here is stated in vanilla CSS terms, because that is what gets built.

These are defaults, and each can be overridden by an explicit, recorded user decision — never by the assistant deciding a project "is the exception".

### Layout

- **No three equal feature cards in a row.** The three-identical-cards feature row is the single most recognisable machine-made layout. Use a two-column alternation, an asymmetric grid, a list with real hierarchy, or a horizontal scroll.
- **No more than two consecutive sections sharing a layout family.** Image-left / image-right / image-left three times is one layout used three times.
- **Across a page of eight or more sections, at least four distinct layout families.**
- **No curved or wave SVG section separators.** A section boundary is spacing, a background change, or a hairline.
- **No decorative hairline grids or crosshairs** drawn purely to make a page feel designed. Rules that organise real content are fine.
- **No `100vh` hero.** Use `100dvh` — `100vh` jumps on mobile browsers when the address bar moves.

### Type

- **Not `Inter`, `Poppins`, `Space Grotesk`, `Montserrat` or `Roboto` as the display face by default.** Each is defensible when the brand system names it or the user asks; none is defensible as the face that was reached for first.
- **Not `Fraunces` or `Instrument Serif`** as the display serif. Both are the reflex serif.
- **Serif display is a decision, not a mood.** "It felt editorial" is not a reason. The brand names it, or the archetype is genuinely editorial or heritage and the specific serif can be justified for this specific brand.
- **Emphasis inside a headline uses italic or weight in the SAME family.** Dropping a serif word into a sans headline for visual interest is an amateur tell.
- **No headline broken with `<br>` and italicised on the second half** as a default composition move.
- **No text-scale-only hierarchy.** If every level is distinguished purely by `font-size`, weight and colour are being wasted.

### Colour and material

- **One accent, used identically across the whole page.** A warm-grey site does not grow a blue CTA in section seven.
- **No purple-to-blue gradient as the default accent.** It is the single most recognisable machine-made palette.
- **No `#000000`.** Off-black.
- **No gradient fill on display text** as a default.
- **No outer glows** as a default. Inner borders or tinted shadows.
- **Not the warm-cream-plus-brass-plus-oxblood palette** as the reflex for anything premium or artisanal. Concretely: backgrounds around `#f5f1ea` / `#faf7f1` / `#efeae0`, accents around `#b08947` / `#b6553a` / `#9a2436`, text around `#1a1714`. It is the default of every machine-made premium page.
- **One radius system per project, and radii between 10px and 18px are the reflex range.** Choose deliberately: sharp (0-4px), soft (20px+), or the middle with a reason.
- **No large-blur, low-opacity ambient shadows on everything.** A shadow means elevation; if everything is elevated, nothing is.
- **One theme per page.** No section flips to inverted mode mid-page unless it is a recorded compositional decision.

### Content

- **No placeholder people, companies or numbers in delivered work.** No "John Doe", no "Acme", no `99.9%`, no lorem. If real content is not available yet, the slot is declared, not filled with a plausible lie — the same rule `phase-8-design-direction.md` applies to screenshots.
- **No filler verbs in copy:** elevate, unleash, seamless, revolutionise, next-generation, empower, supercharge.
- **No fake product UI built from styled `<div>` elements.** A product screenshot is a real capture, per the reserved-slot mechanism, or the slot is empty.
- **No section-number eyebrows** (`01 / FEATURES`, `002 · Capabilities`). An eyebrow names the topic in words or does not exist.
- **No scroll cues.** A reader looking at the hero knows scrolling exists.
- **No decorative status dots** before nav items, list rows or badges. A dot means real state or it means nothing.
- **No locale, time or weather strips** unless the site is genuinely about a place or a distributed team.
- **No version stamps or build strings** in marketing page furniture.
- **Middle dot (`·`) rationed to one per metadata line.**

### Punctuation

- **The em-dash (`—`) and the separator en-dash (`–`) are forbidden in every string visible on the built site**: headlines, eyebrows, labels, buttons, body copy, quotes and attributions, captions, alt text, meta descriptions and structured-data strings. Resolve with a full stop, a comma, a colon, parentheses, or a line break. Ranges use a hyphen (`2018-2026`, `40-80`).

  The scope is **the rendered site only**. Keel's own `docs/`, the briefs, the changelog and the conversation are untouched. The reason is narrow and empirical: the em-dash is the most reliable single textual signal that a page's copy was machine-written, and on a site whose credibility rests on being made by a person, that signal costs more than the punctuation is worth. In Spanish, the raya has legitimate uses in prose; this rule is about marketing surface, not about typography in general.

  This is a binary check. One visible em-dash fails it.

---

## Step 7 — The self-critique pass

Before the handoff is considered complete, Design answers two questions in writing, in `SPEC/art-direction.md`:

1. **Which parts of this are the default?** Name the elements that any assistant would have produced from this brief without this reference. Being present is not automatically a failure — a default is sometimes the right answer — but it has to be visible and deliberate.
2. **Which part is not?** Name the specific, concrete thing that makes this site this site, and say why it belongs to this project rather than to the archetype.

An answer to the second question that would read identically pasted into another project has not answered it. This is a two-question pass and not another checklist because the failure it catches is judgment-shaped: the site that ticks every box and has nothing of its own.

---

## Step 8 — Record and close

1. The chosen direction, with the rejected alternatives named, goes into `docs/decisions.md`.
2. The read, the dials with their reasons, the direction, the signature elements and the self-critique go into `SPEC/art-direction.md` (`references/handoff-contract.md`) and into the brief (`references/design-brief-template.md` §2b).
3. The ledger entry is appended to `~/.keel/art-ledger.md` in the format above.
4. Anything the ledger blocked and could not be varied is stated, with the reason.

From here the normal regime resumes and this subject is closed.

---

## Definition of done (this reference)

- Design Read declared in one sentence naming site type, audience and archetype, and recorded.
- All four dials set with an explicit one-line reason each; presets argued with, not inherited silently.
- `~/.keel/art-ledger.md` read; the last three entries' constraints applied, or its absence stated in one line.
- Three directions for one section delivered, each from a differently named aesthetic family, at least one a deliberate risk, each with tokens and a fit rationale, none reusing a ledger-blocked element.
- One direction chosen and recorded in `docs/decisions.md` with the rejected alternatives named (or the waiver recorded as its own decision entry).
- One or two signature elements named, with their recurrence points and CSS treatment, in `SPEC/art-direction.md`.
- Blacklist applied; the em-dash check run against every string visible on the built site and passing at zero.
- Self-critique pass answered, both questions, specifically.
- Ledger entry appended, with anything unvaried stated and justified.
- `SPEC/art-direction.md` complete per `references/handoff-contract.md`; the brief carries the direction.

Then fill in `references/phase-8-design-direction.md` (the technical constraints and logistics of the same handoff) and write the brief.
