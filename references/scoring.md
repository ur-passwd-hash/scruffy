# Severity, confidence, and scoring

Scores summarize evidence; they do not replace findings. Do not publish a numeric total when required categories were not tested.

## Severity

- **Critical** — prevents nearly all users from completing the product’s defining task, causes irreversible loss through normal use, or makes the interface broadly unusable. Rare in a design audit.
- **High** — blocks a core task for a meaningful user group, removes essential access, or causes repeated failure with no reasonable workaround.
- **Medium** — creates material friction, a standards failure, misleading feedback, fragile maintenance, or a workaround that users must discover.
- **Low** — localized clarity, consistency, polish, or resilience issue with limited task impact.

Do not use Critical for ordinary aesthetics. Security severity belongs to a security review.

## Confidence

- **High** — directly reproduced in the rendered interface and supported by a measurement, state transition, task result, or matching source evidence.
- **Moderate** — directly observed once or strongly supported by source, but environment, coverage, or causality remains incomplete.
- **Low** — inference or heuristic lead that has not been reproduced. Low-confidence items normally belong in “needs verification,” not prioritized findings.

## Category score

Score only categories with adequate coverage. Use a 0–3 defect scale:

- **0 — Clear:** no material issue verified in the tested scope.
- **1 — Contained:** one or more low-severity issues; core tasks remain clear.
- **2 — Material:** a medium-severity issue or a repeated pattern creates meaningful friction.
- **3 — Blocking:** a high/critical issue blocks a core task or user group.
- **N/A — Not tested:** capability or scope was insufficient.

Recommended categories:

1. Product clarity
2. Information architecture and routing
3. Interaction and state
4. Accessibility
5. Visual hierarchy and identity
6. Content and copy
7. Implementation shape
8. Runtime performance

If a single structural cause creates several symptoms, score the affected categories but count the root cause once in the prioritized findings.

## Craft coverage

Positive craft principles may be reported as `verified / applicable`. Mark a principle applicable only when the tested product exposes that concern. Do not penalize a static page for lacking application states it does not need.

## Overall result

Use a verbal result rather than a pseudo-precise percentage:

- **Distinctive and sound** — no blocking issue; product-specific identity and core tasks hold.
- **Sound with material gaps** — core tasks work, but one or more medium issues deserve correction.
- **Generic or fragile** — repeated material issues weaken identity or task reliability.
- **Core experience blocked** — at least one high/critical issue prevents the defining task.
- **Insufficient evidence** — required capabilities or coverage are missing.

Always show the category scores and their evidence boundary beside the result.

