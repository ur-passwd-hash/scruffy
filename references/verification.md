# Verification protocol

Use this protocol for live interfaces. It is intentionally tool-neutral: translate each check into the browser, automation system, accessibility inspector, or manual workflow available in the current environment.

## 1. Declare the evidence boundary

Record whether the audit has source, rendered UI, interaction, keyboard, responsive viewport, screenshot, console/network, accessibility-tree, and performance access. A static screenshot cannot prove interaction. Source cannot prove rendered appearance. A click command cannot prove the resulting state is usable.

Do not inspect cookies, passwords, tokens, browser storage contents, or unrelated browsing state. To test persistence, change a visible preference or progress state, reload or reopen the app, and observe whether the visible state survives.

## 2. Build a coverage ledger

Track every meaningful surface and state:

| Surface | State or task | Viewport | Input | Result | Evidence | Confidence |
|---|---|---|---|---|---|---|
| Example route | Primary task | Desktop | Pointer | Pass/fail | Measurement | High |

Cover the primary route first. Sample every unique component or interaction pattern; do not repeat identical controls solely to inflate coverage.

## 3. Representative task test

For each task record:

- Starting state
- User goal
- Actions taken
- Elapsed time or interaction count when meaningful
- Expected result
- Observed result
- Recovery path
- State after reload, back/forward, or reopen when applicable
- Whether the URL or another durable identifier represents the state

Use realistic tasks, not “click every button.” A control works only when its feedback and resulting state are understandable.

## 4. Interaction checks

- Primary and secondary navigation
- Menus, drawers, tabs, accordions, and dialogs
- Form entry, validation, submission, cancellation, and retries
- Loading, empty, offline, error, and success states
- Focus visibility and logical focus order
- Keyboard activation and escape behavior
- Back/forward behavior and deep linking
- Persistence across reload and reopen
- Touch target size and sticky/fixed regions on small screens
- Feedback for async, media, clipboard, and permission-dependent actions

When an API or platform feature may be unavailable, distinguish “feature unavailable here” from “control is broken.” A resilient UI exposes a disabled, fallback, or error state.

## 5. Accessibility checks

Inspect, as available:

- Document title, language, headings, landmarks, and main region
- Accessible names and roles for interactive controls
- Current, expanded, selected, pressed, invalid, and busy states
- Live-region feedback for important dynamic changes
- Label, help, and error relationships
- Keyboard reachability, activation, focus trapping, and focus return
- Color contrast using computed foreground and background colors
- Zoom/reflow and reduced-motion behavior
- Alternative text and captions/transcripts where applicable

Tie each finding to a specific criterion or functional barrier. Automated scans are leads; manually verify high-impact results. Do not issue a blanket compliance verdict from a partial sample.

## 6. Visual and content checks

Compare actual computed or rendered evidence, not the stylesheet alone:

- Hierarchy: Can a new user identify purpose and primary action quickly?
- Composition: Does the layout express importance or merely distribute boxes?
- Typography: Are roles coherent and readable at real viewport sizes?
- Color: Do functional states and small text meet measured contrast?
- Density: Is information grouped around tasks rather than card count?
- Copy: Is it concrete, product-specific, and free of synthetic filler?
- Imagery: Does it provide information or identity rather than ornamental proof-of-work?
- Responsive behavior: Does content recompose instead of merely shrink or wrap?

A declared font stack is not evidence of a missing font. Verify the rendered face or availability in the tested environment.

## 7. Implementation-shape checks

When source exists, map visible symptoms to their causes:

- Route and state addressability
- Content/data separated from view code where change frequency warrants it
- Shared primitives and tokens versus copied markup or inline styles
- Error handling that surfaces failure rather than swallowing it
- Test seams for task-critical behavior
- Semantic structure owned by reusable shells
- Feature flags, permissions, and environment fallbacks

Large files, inline styles, and duplicated markup are not automatically defects. Report them when they demonstrably obstruct consistency, testing, addressability, accessibility, or safe changes.

## 8. Performance checks

Only report performance defects from runtime measurements such as Core Web Vitals, network waterfalls, long tasks, excessive layout shifts, or repeatable interaction delay. If runtime instrumentation is unavailable, list performance as not run. Source size may justify an optimization hypothesis, not a performance verdict.

## 9. Falsification pass

Before finalizing each candidate finding, ask:

1. Can a realistic task still be completed quickly?
2. Is the pattern intentional and appropriate for this audience?
3. Does another viewport or state resolve it?
4. Does source evidence contradict the rendered observation?
5. Is this an environment limitation rather than an application defect?

Move disproven candidates into cleared suspicions. Lower confidence when evidence remains incomplete.

