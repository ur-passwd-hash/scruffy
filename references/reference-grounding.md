# Reference grounding

Ungrounded generation regresses to the training mean — the recognizable slop this skill exists to catch. Grounding injects two optional evidence sources that outrank model priors: **live design-reference search** over shipped products, and a **user taste overlay**. Both are optional capabilities. Their absence is never a finding, never blocks a run, and is disclosed once.

## Capability detection

At run start, check the environment for design-reference search tools. These arrive as MCP connectors; the reference implementation is Mobbin MCP, which exposes `search_screens` (single UI screens), `search_flows` (multi-step flows such as onboarding or checkout), and `search_sections` (website sections such as pricing or footers). Tool names may carry a server prefix. Any connector exposing equivalent search over shipped-product interfaces satisfies the capability — do not require a named vendor.

Record the capability as available, unavailable, or not needed in the run's capability disclosure. If unavailable and the run is DESIGN or REDESIGN, state once that direction work proceeds on corpus priors without live references, and continue.

## When to search

- **DESIGN / REDESIGN, before the paradigm round.** Pull 3–8 references for the surface archetype and domain. The goal is to see how shipped products structure this job before proposing structures — including at the real item count and in non-happy states when the connector surfaces them.
- **AUDIT, before convicting a convention.** When a pattern looks wrong but may be a domain norm (progress steppers in regulated flows, price-in-CTA on paywalls), pull comparable screens first. Convention is context, not verdict — see the guards below.
- **Micro-decisions during implementation.** Two or three shipped treatments of one control beat an invented one.
- **Web sections.** Landing, pricing, footer, and hero work routes to `search_sections`.

## Query discipline

Query with concrete surface + domain + state, never adjectives. "KYC document-scan step, banking apps" and "empty state, project management web app" return evidence; "clean modern dashboard" returns the mean. Cap pulls at what will actually be read (3–8 per question); note connector rate limits in long runs.

## What a reference yields

Extract **named patterns**, never pixels: "pre-flight intro before camera open", "soft rejection — em-dash instead of red X in the free column", "price inside the CTA". Each pattern used in a finding, direction, or implementation carries a citation — app name plus source link — recorded as a typed evidence receipt (URL kind) where the output schema is in play. References inform structure and convention; do not reproduce protected trade dress, copy text verbatim, or represent a third-party screen as project work.

## Precedence and false-positive guards

Authority order, highest first:

1. The user's direct verdicts on rendered work in this run.
2. Supplied voice, brand, and regulatory constraints.
3. The user's taste overlay (below).
4. Live shipped-product references.
5. Corpus principles and model priors.

Guards, binding both directions:

- **Popularity is a mean, not a merit.** A pattern shipping in forty top apps is evidence of convention and of what users have been trained to parse — not evidence of quality. Reference sets curated by popularity reproduce exactly the look this method exists to escape.
- **Deviation is not slop.** Failing to match shipped convention is a finding only when the deviation causes observable task friction, comprehension cost, or trust cost. Cite the consequence, not the mismatch.
- **Match is not clearance.** Matching a shipped pattern does not clear a finding whose harm is demonstrated; plenty of shipped products carry dark patterns. Engagement mechanics pulled from references still pass the ethics screens in the taxonomy.

## User taste overlay

An optional local directory of the user's own curated references and rules. Resolution order: `$DESIGN_TASTE_DIR`, then `./.design-taste/`, then `./design/taste/`. Found: read it and apply it at precedence 3. Not found: say "no taste overlay found" once and continue — never an error.

Overlay health check, disclosed when loaded: an overlay curated **by** the user (their verdicts, their rejections) is taste; an overlay curated **for** the user by an agent is a hypothesis and is labeled as such. An overlay seeded from popularity galleries is the mean itself; recommend running without it. When the user's demonstrated taste contradicts an overlay rule or a reference convention, follow the user and say so explicitly — never break a rule silently, and offer to write the verdict back into the overlay so it accumulates.

## Degradation ladder

Full grounding (connector + overlay) → overlay only → connector only → corpus only. Every rung is a valid run; each rung down is disclosed in one line. Never fabricate a reference, never cite an unpulled screen, and never let grounding absence downgrade finding confidence that operation already established.
