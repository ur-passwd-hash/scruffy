---
name: scruffy
description: Find, audit, and fix AI slop in web apps, including generic layouts, broken or fake interactions, vague or formulaic copy, accessibility failures, performance problems, and vibe-coded implementation shortcuts. Use for first, repeat, fresh-eyes, or blind audits of a web app, URL, screenshot, prototype, repository, or blank interface; requests to roast, de-vibe-code, redesign, improve, reconcile, or regression-test a UI; questions about generic or AI-like interface writing; and evidence-backed findings, design directions, implementation work orders, or decision reports. Do not use for AI-authorship classification, security-only reviews, or non-interface code work.
---

# Scruffy

Find and fix observable AI slop in web interfaces. Operate the product, inspect available source and runtime evidence, and turn verified failures into prioritized work orders. Judge the result, never the author: do not infer whether AI made the interface.

This skill is agent-, vendor-, framework-, browser-, and operating-system-agnostic. Use the capabilities available in the current environment and disclose what could not be tested.

## Select a mode

- **AUDIT** — default for an existing URL, app, screenshot, or repository. Inspect and report; modify only when the user also asks for changes.
- **REDESIGN** — audit, propose a coherent direction, implement authorized changes, and verify them.
- **DESIGN** — create a new interface from a blank or weakly specified starting point. Establish product framing before visual direction.
- **DEMONSTRATE-FIX** — when source access is absent but live DOM/style injection is possible, demonstrate reversible improvements. Label them as demonstrations, not repository changes.

## Capability preflight

Before making findings, record each capability as available, unavailable, or not needed:

1. Source read access
2. Rendered-page access
3. Interaction and keyboard operation
4. Screenshots or equivalent visual evidence
5. Console, network, accessibility-tree, and performance inspection
6. File write and implementation access
7. Prior audit registry, reports, and decision data
8. Copy samples, intended audience, and any supplied voice or regulated-language constraints

Missing capability is not evidence of a defect. Reduce confidence, omit unsupported scores, and label the check **not run**. Never inspect passwords, cookies, authentication tokens, browser storage contents, or unrelated private data. Test persistence behavior by changing visible state, reloading or reopening the app, and observing the result.

Read [references/verification.md](references/verification.md) before operating a live interface. Read [references/archetypes.md](references/archetypes.md) after framing the product to select the applicable coverage modules. Read [references/sentence-slop.md](references/sentence-slop.md) whenever sentence construction, cadence, passive voice, rhetorical scaffolding, or synthetic-sounding copy is in scope. For a requested blind or independent run, read [references/blind-audit.md](references/blind-audit.md) before searching for prior artifacts. For implementation or a decision deliverable, read [references/output-schema.md](references/output-schema.md). For every repeat audit or any durable report, read [references/durability.md](references/durability.md). Read [references/scoring.md](references/scoring.md) before assigning severity, confidence, or scores.

## Required order of work

Do not start with color, typography, or screenshots. Work in this order:

1. **Product** — audience, purpose, primary job, differentiator, repeat-use reason, success signal.
2. **Backend shape** — data model, state ownership, content structure, routing, shared primitives, API boundaries, and maintainability constraints.
3. **Interaction** — task completion, navigation, state transitions, forms, feedback, errors, persistence, keyboard operation, responsive behavior, and accessibility semantics.
4. **Visual and copy** — hierarchy, composition, typography, color, density, motion, imagery, empty states, and generic or synthetic language.

When one structural cause creates several visible symptoms, identify that cause once and link the dependent findings to it. Do not prescribe cosmetic changes that leave the blocker intact.

## Workflow

### 0. Establish identity and baseline

If the user requested a blind, independent, or fresh-eyes test, run the two-phase protocol in [references/blind-audit.md](references/blind-audit.md). Before discovery, create a manifest of allowed and forbidden inputs. Do not search for or load prior findings, reports, decisions, work orders, stable IDs, expected answers, or discussion of the same target. Use temporary `CAND-` IDs, freeze the discovery digest, and only then reveal the baseline and reconcile it. If forbidden context is encountered before freeze, mark the run contaminated and restart in a fresh isolated session.

For a normal baseline or repeat audit, assign one stable `audit_id` to the product/target and one unique `revision_id` to this run. Search the supplied workspace and output location for an existing findings registry, audit report, decision export, or matching target before creating IDs.

When any prior artifact exists, this is a revision. Load the prior registry and decisions before testing. Preserve every prior ID and decision history. Every prior item must appear in the new registry with an explicit disposition: carried, reopened, fixed, cleared, merged, or superseded. Silent disappearance and ID reuse are hard failures.

When no baseline exists, state that this is the baseline revision. Create the registry before rendering the final report.

### 1. Frame the product

Answer six questions from supplied context, the interface, and source evidence:

1. Who is it for?
2. What job does it perform?
3. What is the primary action?
4. What makes it meaningfully different?
5. Why would someone return?
6. What observable result means it succeeded?

Mark answers as observed, supplied, or inferred. If the answers remain unknown, state the ambiguity and avoid pretending the product is clear.

Derive three to five representative user tasks. Include the primary task, a recovery or error path, and a repeat-use or persistence task when applicable. Select applicable modules from [references/archetypes.md](references/archetypes.md); use the hybrid/unknown module when the product crosses categories.

### 2. Inspect the implementation shape

When source is available, map pages, routes, shared components, data/state ownership, design tokens, content sources, and tests. Look for monolithic page files, copied structures, inline-style proliferation, unaddressable state, silent error handling, and fake controls. These are candidate causes, not findings until their user or maintenance impact is shown.

### 3. Render and inventory

Use a real rendered surface when possible. Enumerate meaningful pages, states, dialogs, menus, forms, responsive breakpoints, empty/loading/error states, and interactive controls. Build a coverage ledger before drawing conclusions.

### 4. Operate the interface

Run each representative task. Exercise every unique interaction pattern at least once, including keyboard operation and mobile layout when available. Observe feedback, focus, validation, persistence, URL/state behavior, recovery, and dead ends. Do not equate an automated click with user success.

### 5. Measure and challenge suspicions

Collect the smallest evidence that can prove or disprove each candidate finding: task outcome and elapsed time, state transition, URL change, computed contrast, DOM semantics, accessibility state, console/network result, source location, or screenshot. Actively try to falsify the suspicion. Record cleared suspicions and retract disproven claims with the same prominence as findings.

Use [principles/PRINCIPLES.md](principles/PRINCIPLES.md) as the detailed pattern library. Use [principles/SOURCES.md](principles/SOURCES.md) and [principles/INSPIRATIONS.md](principles/INSPIRATIONS.md) for provenance and further study. For sentence-copy candidates, apply the compound predicate in [references/sentence-slop.md](references/sentence-slop.md): adequate sample, at least two independent signals, quoted evidence, a task or voice consequence, and a tested counterexample. Measurements remain leads; never infer authorship.

### 6. Synthesize

The complete registry is lossless and has no item-count cap. The executive presentation may show no more than:

- Eight verified findings, ordered by severity and leverage
- Five enhancements, separated from defects
- Three strengths worth preserving
- All material cleared suspicions

Items outside the shortlist remain visible in the full registry and dashboard under additional, resolved, merged, superseded, or enhancement sections. Never drop an item to satisfy a presentation limit.

Each finding needs a stable ID, immutable `identity_key`, category, severity, confidence, lifecycle status, revision disposition, user impact, evidence, structural cause, recommended change, acceptance check, and dependencies. Separate observed fact from inference. A clarified title may change; the ID and identity key may not.

### 7. Implement only within authority

An audit request authorizes inspection and reporting, not source changes. A redesign or fix request authorizes scoped implementation. Preserve the product’s real identity and content; do not replace a distinctive interface with a fashionable template.

After changes, repeat the same tasks and measurements. Report regressions, unresolved items, and checks not run.

### 8. Retrospect

At the end of a substantial audit, record only reusable lessons that survived falsification. Add a principle when the lesson is general, a local note when it is product-specific, and nothing when the evidence is weak. Keep source provenance intact.

## Design mode direction ladder

For new design or redesign work, explore before converging:

1. Five distinct paradigms — for example editorial, utilitarian, spatial, conversational, and data-dense.
2. Five material systems within the strongest paradigm — for example paper, enamel, glass, terminal, and soft industrial.
3. Three compositions within the strongest material system — vary hierarchy and spatial structure, not merely color.

Select using product fit, task clarity, accessibility, feasibility, and distinctiveness. Explain the rejected alternatives briefly. Do not create variant theater: each option must differ structurally.

## Evidence rules

- A visual resemblance is not proof of authorship.
- Repetition is not automatically bad; repeated patterns may be valid system primitives.
- Missing animation, gradients, illustrations, or unusual layouts is not a defect.
- “Generic” must be tied to concrete sameness, weak hierarchy, irrelevant decoration, synthetic copy, or task friction.
- Source-only visual claims are unverified until rendered.
- Automated heuristics generate leads, not verdicts.
- Sentence regularity, passive voice, rhetorical questions, low lexical variation, and familiar phrases never establish AI authorship. Do not calculate or report an AI probability, perplexity score, or burstiness verdict.
- Do not infer language background, disability, education, or writing assistance from prose. Respect supplied technical, legal, regulated, translated, accessibility-simple, and non-native contexts as false-positive guards.
- Accessibility claims require an identified criterion and evidence. Do not claim conformance from a partial audit.
- Performance claims require measured runtime evidence. Do not infer speed from file size alone.
- Security findings are outside this skill’s scope; route them to an appropriate security review.

## Output

Always return a concise Markdown summary with capability coverage, product framing, prioritized findings, strengths, retractions, and next actions.

When files and an interactive viewer are available, also produce:

- A self-contained HTML decision report
- `findings.json` containing the complete durable registry and presentation lists
- `decisions.json` using stable item IDs, revision lineage, approve/defer/reject states, and history
- `tokens.json` when token changes are proposed

For a blind run, also produce `blind-manifest.json`, `blind-discovery.json`, and `blind-freeze.json`; add `blind-reconciliation.json` only after the reveal phase. State whether blindness was verified, contaminated, or not run.

When those capabilities are unavailable, emit the same information as Markdown plus a complete registry JSON block. Never make an HTML dashboard a prerequisite for completing an audit.

Follow the exact schema and fallback behavior in [references/output-schema.md](references/output-schema.md).

## Definition of done

The work is complete only when:

- Product framing and representative tasks are explicit.
- Available capabilities and checks not run are disclosed.
- Findings are evidence-backed and falsification has been attempted.
- Sentence-copy findings meet the compound predicate and make no authorship claim.
- A requested blind run was frozen before baseline reveal, or contamination was disclosed.
- Structural causes precede cosmetic prescriptions.
- Severity, confidence, and any scores follow the calibrated rubric.
- Defects, enhancements, strengths, and retractions are separated.
- Every baseline item has an explicit disposition and no ID or identity key was reused.
- The complete registry and decision history survive presentation filtering.
- The dashboard/report contains every registry item and every required section, or the missing capability is disclosed.
- Authorized changes are verified against the original tasks.
- The report remains useful to a human who does not know which agent or tools produced it.
