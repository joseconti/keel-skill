# Accessibility (cross-cutting, non-negotiable)

Load this the moment the project type and target platform(s) are fixed in Phase 1 — the same timing as the security profile — and keep it live through every later phase. Accessibility is not optional, not a phase, and not a final-phase checkbox. It is designed in from the first line on every platform, using every accessibility tool the platform provides.

This reference has a **universal core** that applies to everything, then a **section per platform**. Apply the universal core plus the section(s) matching the project's target platform(s). If a project spans platforms (e.g. a web app with an iOS and Android client), apply every matching section.

## Why this is stated up front (and never retrofitted)

Building accessibly from line one and "making it accessible" at the end are not the same job — the second is a rewrite, exactly like retrofitting internationalization. An accessible name that is added at creation costs nothing; the same name reverse-engineered across a finished codebase, after the semantic structure, focus order, color choices and component APIs are already wrong, costs a rebuild. So this is decided and stated to the user in Phase 1, carried into the functional spec's acceptance criteria, specified by Design in the handoff, built into every Phase 5 slice with its own test point, documented in `docs/accessibility.md`, and verified for real (with actual assistive technology) before release. There is no point in the lifecycle where accessibility is "added later".

## The standard (the floor, then the ceiling)

The commitment is the **maximum reasonably achievable**, never a token gesture. Concretely:

- **WCAG 2.2 Level AA is the floor** for anything with a UI (web and, as the shared vocabulary, native apps too). Meet AA fully; reach **AAA where feasible** (it often is for contrast, target size, and reading level).
- **EN 301 549** and the **European Accessibility Act (EAA)** where they apply. The EAA has applied since 28 June 2025 and covers e-commerce and many digital products/services in the EU — it applies to the user's market and customers, so treat it as in scope by default for anything sold or offered to EU users. Section 508 / ADA (US) map onto the same WCAG criteria if the project targets the US.
- **The native accessibility API and assistive technologies of each target platform**, fully supported — not partially. "Use every accessibility tool the platform offers" is the standing rule: screen readers, switch access, voice control, text scaling, reduced-motion and high-contrast preferences, and every semantic hook the platform exposes.

State the targeted level to the user in Phase 1 and record it in `docs/01-discovery.md`. Aiming below AA is a conscious user decision with a recorded reason — never a silent default.

## Universal core (every platform, no exceptions)

Organized by the four WCAG principles (Perceivable, Operable, Understandable, Robust). These hold whether the surface is HTML, a native mobile screen, or a desktop window — only the API used to satisfy them changes.

### Perceivable

- **Text alternatives for non-text content.** Every image, icon, chart, media element or purely visual control has a text alternative exposed to assistive technology (empty/decorative when it truly carries no meaning). Charts and complex graphics get a real description or data equivalent, not just a filename.
- **Sufficient color contrast.** Text meets **4.5:1** (normal) / **3:1** (large: ≥18pt, or ≥14pt bold); UI components and meaningful graphical objects meet **3:1** against adjacent colors. Aim AAA (7:1 / 4.5:1) where feasible. Verify every foreground/background pair with a contrast tool — do not eyeball it.
- **Never convey meaning by color alone.** Errors, states, required fields, chart series and links carry a second cue (text, icon, underline, pattern, shape) besides color.
- **Support text scaling and reflow.** Content remains usable when text is enlarged (WCAG: to 200% without loss; reflow at 320 CSS px equivalent). Layouts flex; nothing is clipped, overlapped, or truncated at large text sizes. Never disable the platform's text-scaling.
- **Respect user display preferences** (see the dedicated section below): reduced motion, increased/bold text, high contrast, reduced transparency, dark mode, "differentiate without color".
- **No seizure risk.** Nothing flashes more than three times per second.
- **Captions and transcripts** for audio/video; audio description where meaningful visual information isn't otherwise conveyed.

### Operable

- **Everything works without a pointer.** Full keyboard operability on desktop/web; full switch and screen-reader-gesture operability on touch. No functionality is mouse-only or gesture-only. Complex pointer gestures have a single-pointer alternative (WCAG 2.5.7 Dragging Movements, 2.5.1 Pointer Gestures).
- **Visible focus, always.** A clearly visible focus indicator on every interactive element; never remove it without an equal or better replacement. The focused element is not hidden behind sticky headers/overlays (WCAG 2.2 SC 2.4.11 Focus Not Obscured).
- **Logical focus order** that follows the reading/interaction order; no keyboard traps; focus is moved deliberately (into opened dialogs, back on close) and never lost.
- **Adequate target size.** Interactive targets meet at least **24×24 CSS px** (WCAG 2.2 AA SC 2.5.8), and the platform's stronger native guidance where it is larger — 44×44 pt (Apple), 48×48 dp (Android), ~40×40 px (Windows). Prefer the AAA 44×44 where feasible.
- **Enough time.** Timeouts are adjustable/extendable or absent; auto-advancing/moving content can be paused; no data loss on session timeout without warning (WCAG 3.3.4 / 2.2.1).
- **Skip repetition.** A way to bypass repeated blocks (skip link on web, rotor/landmarks via the native API on native).

### Understandable

- **Programmatic labels, names, roles, values and states.** Every control exposes an accessible name, its role/type, and its current state/value to the platform accessibility API. Form fields have real, programmatically-associated labels (not placeholder-only). Grouped controls (radio sets, field groups) are grouped semantically.
- **Clear error identification and recovery.** Errors are identified in text, tied to the field, and describe how to fix them; success and status changes are announced to assistive technology (live region / native announcement). Don't rely on color or position alone.
- **Consistent, predictable UI.** Navigation and repeated components stay consistent; help is in a consistent place (WCAG 2.2 SC 3.2.6); focus/hover/input changes don't trigger surprising context changes.
- **Reduce cognitive load at input.** Don't force redundant re-entry of information already provided (SC 3.3.7); support accessible authentication without a cognitive-function test / allow password managers and paste (SC 3.3.8).
- **Meaningful structure.** A correct heading hierarchy and landmark/region structure so assistive-tech users can navigate by headings and regions. One clear title per screen.

### Robust

- **Use the platform's semantic/native controls first.** Native/standard components come with accessibility built in; only build a custom control when necessary, and when you do, fully implement its name/role/state/keyboard/focus contract (the platform's equivalent of the ARIA Authoring Practices).
- **Valid, well-formed markup / view hierarchy** so assistive tech can parse it. On web, no duplicate IDs, correctly nested landmarks, ARIA only where native semantics are insufficient and always with the required states kept in sync ("no ARIA is better than bad ARIA").
- **Status messages exposed programmatically** without moving focus (live regions / native announcements).

## Respecting user preferences (cross-platform, mandatory)

Whatever the platform exposes, honor it — never override or ignore it:

- **Reduced motion** — gate or replace non-essential animation/parallax/auto-play. Web: `prefers-reduced-motion`. iOS/macOS: `UIAccessibility.isReduceMotionEnabled` / `NSWorkspace.accessibilityDisplayShouldReduceMotion`. Android: `Settings.Global.ANIMATOR_DURATION_SCALE` / `AccessibilityManager`. Windows: "Show animations" system setting. Flutter: `MediaQuery.disableAnimations`. RN: `AccessibilityInfo.isReduceMotionEnabled`.
- **Increased / bold text and text scaling** — layouts adapt; never cap the system text size. iOS: Dynamic Type. Android: `fontScale`. Windows/macOS/web: system/browser text sizing and zoom.
- **High/increased contrast** — honor OS high-contrast / "increase contrast" modes; don't hardcode colors that break them (Windows Contrast Themes / `forced-colors`, macOS/iOS Increase Contrast, `prefers-contrast`).
- **Dark mode / color scheme** — support and don't fight the system setting; keep contrast in both.
- **Reduce transparency**, **differentiate without color**, **bold text**, **button shapes** — honor where the platform offers them.

## Platform sections

### Web / HTML

- **Semantic HTML first, ARIA second.** Use native elements (`button`, `a[href]`, `label`, `nav`, `main`, `header`, `footer`, `h1`–`h6`, `ul/ol`, `table` with headers, `fieldset/legend`) for built-in semantics and keyboard behavior. Reach for ARIA only when no native element fits, and follow the WAI-ARIA Authoring Practices for the pattern; keep every ARIA state (`aria-expanded`, `aria-selected`, `aria-invalid`, etc.) in sync with reality.
- One `main`, correct landmark regions, a visible **skip link** to `main`, a logical single-`h1`-per-page heading outline.
- Forms: every control has an associated `<label>` (or `aria-labelledby`), errors use `aria-describedby` + `aria-invalid`, required state is programmatic, and the error summary moves focus / is announced.
- Focus: visible focus style (`:focus-visible`), managed focus for dialogs/menus/disclosure, no `tabindex > 0`, no keyboard traps. Modal dialogs use `role="dialog"`/`aria-modal`, trap focus while open, restore focus on close.
- Live updates via `aria-live` regions; don't hijack scrolling or the browser's zoom.
- Honor `prefers-reduced-motion`, `prefers-contrast`, `prefers-color-scheme`, and `forced-colors` (Windows High Contrast) — don't paint over system colors.
- **Verify with:** axe-core / axe DevTools, Lighthouse, WAVE, or pa11y in CI; a **keyboard-only pass** (Tab/Shift-Tab/Enter/Space/Esc/arrows); and a **real screen-reader pass** (NVDA or JAWS on Windows, VoiceOver on macOS/iOS, TalkBack on Android). Automated tools catch at most ~30–40% — the manual passes are mandatory, not optional.

### WordPress / WooCommerce

Everything in the Web/HTML section, plus the WordPress specifics (the user ships WordPress/WooCommerce plugins and Gutenberg blocks):

- Follow the **WordPress Accessibility Coding Standards** (the project targets WCAG 2.x AA) and, for anything theme-facing, the "Accessibility Ready" requirements: keyboard navigation, visible focus, skip links, labelled forms, no color-only meaning, correct heading structure.
- **Admin and settings UIs**: build on core components (`@wordpress/components`) and core patterns — they are already accessible; don't reimplement inputs that strip the accessibility. Label every settings field; keep the admin keyboard-operable; never remove the admin focus outline.
- **Announcements**: use `wp.a11y.speak()` (`@wordpress/a11y`) for dynamic status messages (AJAX results, async saves, validation) so screen-reader users hear them; don't rely on a visual-only toast.
- **Gutenberg blocks**: the block's edit and save markup is semantic and accessible; block controls (toolbar, inspector) use core controls; `RichText` and interactive block markup expose correct roles; the front-end render is keyboard-operable and labelled. This aligns with the user's blocks work — accessibility is part of every block, not a separate pass.
- **WooCommerce**: cart, checkout, account and gateway UIs are keyboard- and screen-reader-operable end to end; payment fields (including Redsys/gateway flows) have real labels, programmatic error identification, and announced state changes; nothing in a checkout step is pointer-only. Given the installed base (40,000+ stores), a broken checkout for AT users is a critical defect, not a nicety.
- Respect the site's `is_rtl()` / text direction and translation layer — accessible names must be translatable strings (ties to the i18n rule), never hardcoded.

### iOS / iPadOS (UIKit & SwiftUI)

- Target the platform accessibility API fully. **UIKit:** set `isAccessibilityElement`, `accessibilityLabel`, `accessibilityHint`, `accessibilityValue`, and correct `accessibilityTraits`; group/order with `accessibilityElements`; expose custom controls' actions via `accessibilityCustomActions`; mark modality with `accessibilityViewIsModal`; post `UIAccessibility` notifications (`.announcement`, `.screenChanged`, `.layoutChanged`) on change. (`accessibilityIdentifier` is for UI tests, not for AT — don't confuse it with the label.)
- **SwiftUI:** `.accessibilityLabel/Value/Hint`, `.accessibilityAddTraits`, `.accessibilityElement(children:)`, `.accessibilityHidden`, `.accessibilityRepresentation`, `.accessibilitySortPriority`; describe charts with `AXChartDescriptor` / Audio Graphs.
- **Dynamic Type**: use text styles / scalable fonts (`@ScaledMetric`), support up to the accessibility text sizes, and reflow — never a fixed point size that clips.
- Support **VoiceOver** (including the rotor), **Voice Control**, **Switch Control**, and **Full Keyboard Access**. Honor **Reduce Motion**, **Increase Contrast**, **Bold Text**, **Reduce Transparency**, **Differentiate Without Color**, **Button Shapes**.
- Meet the 44×44 pt minimum hit target.
- **Verify with:** Xcode **Accessibility Inspector** (audit + live inspection), the SwiftUI Accessibility preview, and a **real VoiceOver pass on a device** with the largest Dynamic Type size.

### Android (Views & Jetpack Compose)

- **Views:** `contentDescription` for non-text/labelled controls (empty for decorative), `labelFor` / `android:hint` for inputs, `android:accessibilityHeading`, `importantForAccessibility`, `stateDescription`, live regions (`accessibilityLiveRegion`), custom actions and correct focus order; drive complex custom views with an `AccessibilityDelegate` / `ExploreByTouchHelper`.
- **Compose:** `Modifier.semantics { }` / `clearAndSetSemantics { }` with `contentDescription`, `Role`, `stateDescription`, `heading()`, `liveRegion`, `onClick(label = …)`; `mergeDescendants` to group; `Modifier.minimumInteractiveComponentSize()` and a 48×48 dp target.
- Support **TalkBack**, **Switch Access**, **Voice Access**, and **Select to Speak**. Honor system **font scale**, **display size**, **dark theme**, **color correction/inversion**, and **remove animations**.
- Ensure a logical traversal order and that touch targets are ≥48 dp with adequate spacing.
- **Verify with:** the **Accessibility Scanner** app, `accessibility-test-framework` / Espresso `AccessibilityChecks` (and Compose UI-test a11y checks) in CI, the Play Console **pre-launch report**, and a **real TalkBack pass on a device** at maximum font scale.

### macOS (AppKit & SwiftUI)

- Implement the **NSAccessibility** protocol for custom views: accessibility label, role, role description, value and help; standard AppKit controls are already accessible — prefer them.
- Full **keyboard access** (all controls reachable and operable; logical key-view loop; standard shortcuts), and full **VoiceOver** support (SwiftUI uses the same accessibility modifiers as iOS).
- Honor **Reduce Motion**, **Increase Contrast**, **Reduce Transparency**, **Differentiate Without Color**, and the system **display text size**; don't hardcode colors that break Increase Contrast.
- **Verify with:** the **Accessibility Inspector**, the keyboard-only pass, and a **real VoiceOver pass**.

### Windows (Win32, WPF, WinUI/UWP, WinForms)

- Expose semantics through **UI Automation (UIA)** — the modern API (MSAA/IAccessible is legacy). Provide `Name`, `ControlType`, `HelpText`, `LabeledBy`, value/toggle/expand patterns, and `LiveSetting` for updates. **WPF/WinUI/UWP:** set `AutomationProperties.Name/HelpText/LabeledBy/LiveSetting`, supply `AutomationPeer`s for custom controls. **Win32:** implement UIA providers for custom windows.
- Full **keyboard access**: every function reachable by keyboard, a logical tab order, access keys/mnemonics, and a visible focus indicator.
- Support **Narrator** (and third-party JAWS/NVDA via UIA). Honor **Contrast Themes** (formerly High Contrast) — use system colors / `SystemColors`, never hardcode; honor system **text scaling** and the **"Show animations in Windows"** setting.
- Meet the platform's minimum target sizing and spacing.
- **Verify with:** **Accessibility Insights for Windows** (FastPass + tab-stop visualizer), **Inspect** and **AccEvent** (Windows SDK), and a **real Narrator pass**.

### Cross-platform frameworks

The framework exposes a semantics layer that maps to each OS's native accessibility API — populate it; do not ship an unlabeled widget tree.

- **Flutter:** `Semantics` widget / `SemanticsProperties` (label, hint, value, button/header/textField flags), `MergeSemantics`, `ExcludeSemantics`, `semanticLabel` on images/icons, `SemanticsService.announce`; support text scaling via `MediaQuery.textScaler`; honor `MediaQuery.disableAnimations`. Verify with the accessibility guideline tests (`meetsGuideline`) and real TalkBack/VoiceOver.
- **React Native:** `accessible`, `accessibilityRole`, `accessibilityLabel`, `accessibilityHint`, `accessibilityState`, `accessibilityValue`, `accessibilityLiveRegion` (Android) / `accessibilityViewIsModal` (iOS), `AccessibilityInfo` (screen-reader/reduce-motion queries, `announceForAccessibility`). Verify on both OSes with their real screen readers.
- **.NET MAUI:** `SemanticProperties.Description/Hint/HeadingLevel`, `SemanticScreenReader.Announce`; maps to VoiceOver/TalkBack/Narrator.
- **Electron / Tauri (web renderer):** all **Web/HTML** rules apply verbatim (it is a browser engine); additionally follow OS integration and keep the Chromium accessibility tree correct. There is no excuse for weaker accessibility than a website.
- **Qt:** set `accessibleName`/`accessibleDescription`, use `QAccessible` for custom widgets; maps to the platform AT.
- **Games / real-time engines (e.g. Unity):** harder, but the principle holds — expose UI to platform AT where possible, and provide scalable/readable text, full remappable controls, captions/subtitles, colorblind-safe palettes, and a reduced-motion/photosensitivity option. If a target here genuinely cannot meet part of the standard, that gap is recorded honestly (see the honesty rule), not hidden.

## What Design must deliver (feeds Phase 3)

Accessibility is specified by Design in the handoff, not improvised by the build. The design brief and handoff contract require, and Phase 4 audits, an accessibility spec (`SPEC/accessibility.md` plus per-screen notes) covering, at minimum:

- The **targeted conformance level** (WCAG 2.2 AA floor / AAA where feasible; EN 301 549 / EAA if in EU scope).
- **Contrast-verified color pairs** — every foreground/background and UI-object pair with its measured ratio, so the build inherits passing values rather than guessing.
- The **visible focus indicator** style (exact tokens) and the **focus order** per screen.
- **Accessible name, role, and state** for every component and every state (including error/empty/loading/disabled), and the **heading/landmark structure** per screen.
- **Target sizes** and spacing meeting the platform minimum.
- **Reduced-motion** variants for every animation/transition, and behavior under **increased text size / reflow** and **high-contrast / forced-colors**.
- **Error identification** pattern (how errors are shown and announced, not color-only).
- **Text alternatives** intent for every image/icon/media, and **don't-rely-on-color** confirmed for every status cue.
- **RTL / bidi** behavior if the project is multilingual (ties to the i18n decision).

A missing accessibility spec is a handoff gap → Design Request (Phase 4), the same as a missing token or state.

## How this runs across the phases (quick map)

- **Phase 1:** state the commitment and the targeted level up front; capture target platform(s); load this reference alongside the security profile; record in `docs/01-discovery.md`.
- **Phase 2:** accessibility conditions are part of every feature's acceptance criteria; per-screen a11y requirements feed the design split.
- **Phase 3:** the brief requires Design to deliver the accessibility spec above; the handoff contract includes `SPEC/accessibility.md`.
- **Phase 4:** audit that the accessibility spec is present and complete; gaps → Design Request; carry it into `BUILD-SPEC.md`; build faithfully.
- **Phase 5:** each slice implements accessibility and passes an accessibility test point (automated + keyboard + real AT); logged as a column in `docs/05-test-points.md`.
- **Phase 6:** consolidate `docs/accessibility.md` (applied measures + how to keep them intact + known gaps).
- **Phase 7:** accessibility verification is a release gate — automated checks plus a manual pass with the platform's real assistive technology on the actual distributable.
- **Phase 8 (website):** web accessibility (this section's Web rules) is an explicit, verified deliverable, checked with real AT at launch.

## Honesty rule

Do not claim conformance that wasn't verified, and do not ship an **accessibility overlay/widget** as a substitute for real accessibility — overlays don't fix the underlying barriers and are widely rejected by disabled users. If a specific target genuinely cannot meet part of the standard (a platform limitation, a third-party component that isn't accessible), record the gap plainly in `docs/accessibility.md` with the reason and the plan, rather than papering over it. Real, partial, honestly-documented accessibility beats a false conformance claim.

## Definition of done (this reference)

- The universal core holds for every UI surface built.
- The section(s) matching the target platform(s) are applied, using the platform's native accessibility API and assistive technologies.
- User preferences (reduced motion, text scaling, contrast, color scheme) are honored, not overridden.
- Contrast, keyboard/AT operability, visible focus, programmatic name/role/state, target size, and error identification are verified — automated tools **and** a real assistive-technology pass (automated tooling alone is insufficient).
- The targeted conformance level (WCAG 2.2 AA floor, AAA where feasible; EN 301 549 / EAA where in scope) is met or the shortfall is honestly recorded.
- `docs/accessibility.md` states what was applied, how to keep it intact, and any known gaps.
- No accessibility overlay stands in for real accessibility; no unverified conformance claim.
