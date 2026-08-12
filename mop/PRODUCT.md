# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

delegated: matches Scruffy's shape — a text-distributed Agent Skill (root
`SKILL.md` + `references/` + `schema/`), portable across Claude Code (plugin) and
Codex (Agent Skill), no framework or build step. Any web output Scruffy's Mop generates
stays self-contained and dependency-free, mirroring Scruffy's constraint.

## Users

Primary: someone who has just run a Scruffy audit and has an authorized mandate
to fix what it found — a developer, designer, or product owner working inside an
agent host (Claude Code, Codex, or another Agent Skills runtime) who wants the
approved findings turned into real, high-craft implemented changes, not another
report. They arrive with Scruffy's output files (`findings.json`, `context.json`,
`decisions.json`, optional `tokens.json`) and repository write authority.

Secondary: the same person auditing the loop — they re-run Scruffy afterward and
expect the findings they approved to move to `fixed`/`cleared` on real evidence.

## Product Purpose

Scruffy's Mop is the fix/redesign executor for Scruffy, with **visual redesign as
its headline job**. Scruffy finds AI slop and proves it; Scruffy's Mop consumes
that verified diagnosis and implements the smallest coherent, genuinely
well-crafted change that clears each approved finding — then hands the result back
to Scruffy to re-audit and confirm. It clears any approved category, but visual
and product findings are first-class: for those it grounds a direction in real
shipped products (via a design-reference search when available) and drives the
change through the impeccable craft engine when present, always falling back to a
built-in craft floor. Success is a finding that moves from `open` to
`fixed`/`cleared` on direct revision evidence, with the fix meeting a real craft
bar rather than a plausible-looking patch. Scruffy's Mop closes the loop Scruffy
opens: **Scruffy finds and proves; Scruffy's Mop fixes to a craft bar; Scruffy
verifies.**

## Positioning

Most "AI fixer" tools re-diagnose and re-decide, drifting from the evidence.
Scruffy's Mop does the opposite: it treats Scruffy's immutable registry as the contract,
implements only `approve`d items, preserves the product truth Scruffy recorded,
and never marks its own work fixed — Scruffy's re-audit is the only authority that
clears a finding. It targets out-of-distribution craft (the impeccable
philosophy) rather than the minimum edit that silences a linter, while staying
strictly inside the authorized, evidence-bound loop. What a neighboring tool could
not truthfully copy: a fix that is verifiable against a named acceptance check by
an independent auditor, produced without ever redefining that auditor's schema.

## Operating Context

- Runs beside Scruffy, in its own repository, as a companion Agent Skill. Scruffy
  and Scruffy's Mop are two skills that hand off, not one merged tool.
- Interoperates through Scruffy's published output contract, consumed read-only.
  Scruffy owns the schema; Scruffy's Mop declares a consumer compatibility key against
  specific versions in `schema/interop.json`: registry **2.1** (legacy 2.0
  readable), context **1.1** (legacy 1.0), decisions **2.1**, tokens **1.0**.
- Authority is inherited, not invented: Scruffy's Mop writes source only under Scruffy's
  `redesign`/`design` authority with explicit `source_write` capability, and acts
  only on decisions whose value is `approve`. It fails closed otherwise.
- The loop: Scruffy audit → approved `decisions.json` + dependency-ordered
  `work_orders` in `context.json` → Scruffy's Mop implements → Scruffy re-audits a new
  revision → items move to `fixed`/`cleared` against their `acceptance_checks`.

## Capabilities and Constraints

- Reads and implements against Scruffy's registry item fields: `recommendation`,
  `acceptance_checks`, `depends_on`, `category`, `severity`, `evidence_refs`,
  and the dependency-ordered `work_orders`.
- Implements in Scruffy's work-order dependency order: structural blockers →
  routing/data/state → semantic and interaction primitives → visual tokens and
  responsive composition → page cleanup → verification.
- Never redefines, extends, or forks Scruffy's schema; never emits findings,
  severities, or authorship judgments; never marks its own output fixed/cleared.
- Preserves the product truth in Scruffy's `product_frame` and all content and
  function outside the approved scope.
- Any generated web artifact is self-contained and dependency-free, like Scruffy.
- **Deliverable format:** visual-redesign output is a single self-contained HTML
  dashboard with every screenshot and reference embedded as a `data:` URI
  (`scripts/mop_dashboard.py`) — because the operator reads output in a terminal,
  nothing may require a network fetch, a sibling folder, or a login to render.
- **Capability preflight (`scripts/mop_preflight.py`):** the browser renderer is
  probed mechanically; impeccable and the design-reference search are agent-probed.
  A capability is `absent` only after a probe fails; omission is `not_run`, never
  `absent`. Disclosure is the observed truth, not an assumption.
- **Name:** the product is **Scruffy's Mop** (machine name `scruffys-mop`). The
  name is decided, not a placeholder.
- **Craft engine (resolved):** a free floor plus two optional augmentations,
  modeled in `schema/interop.json` under `augmentations` and detailed in
  `references/visual-redesign.md`.
  - **Built-in craft floor** (`references/craft-bar.md`) — depends on nothing and
    always applies, preserving portability across Claude, Codex, and other Agent
    Skills runtimes. Every fix must clear it.
  - **impeccable** — free, and first-class *when present* (Claude Code and runtimes
    that have the skill); drives elevated visual/interaction craft within the
    approved scope. Never a hard dependency; when absent the floor applies.
  - **design-reference search** (Mobbin or any equivalent) — **paid**, so strictly
    optional; grounds a redesign direction in real shipped products when available,
    otherwise disclosed as absent. Maps to Scruffy's `design_reference_search`
    capability.
  - Rule: detect at runtime, use what is present, disclose what is absent in the
    handoff; an absence is never a defect and never a manifest dependency. This is
    the free-tier behavior required for open-sourcing.

## Brand Commitments

Binding: the companion relationship to Scruffy — Scruffy's Mop is unmistakably "the one
that fixes what Scruffy finds," and its voice is a sibling to Scruffy's
(plainspoken, evidence-first, confident, no hedging; blames the result, never the
author). The name **Scruffy's Mop** is a binding commitment — it names the
companion role directly (Scruffy makes the mess visible; the mop cleans it).
Open: mascot, palette, and all visual language — nothing visual is committed yet.

## Evidence on Hand

- Scruffy's real output contract, consumed here:
  `../references/output-schema.md`, `../schema/audit-contract.json`.
- This repo's `schema/interop.json` (the consumer compatibility key) and
  `references/scruffy-handoff.md`.
- Implemented runtime method: `SKILL.md` plus `references/method.md`,
  `fix-protocols.md`, `craft-bar.md`, `verification.md`.
- Deterministic scripts with tests: `scripts/mop_bundle.py` (ingest, validate,
  gate, plan), `scripts/mop_handoff.py` (re-audit handoff), `scripts/validate_skill.py`,
  and `scripts/test_mop.py` (16 tests). Fixture bundle at `fixtures/sample-audit/`.
- No users, testimonials, benchmarks, or real-world audit runs exist yet; the
  regression evidence is the internal test suite, not a product claim.

## Product Principles

- **Consume, don't re-diagnose.** Scruffy's registry is the contract; Scruffy's Mop
  implements it, it does not relitigate it.
- **Only what was approved.** Act on `approve`d items under real write authority;
  fail closed on everything else.
- **The auditor clears the finding, not the fixer.** Scruffy's Mop never marks its own
  work fixed; Scruffy's re-audit is the only authority.
- **Craft, not camouflage.** Aim for out-of-distribution quality that survives
  re-audit, not the smallest edit that hides the symptom.
- **Preserve product truth.** Everything in Scruffy's `product_frame` and outside
  the approved scope survives unchanged.

## Accessibility & Inclusion

Target **WCAG 2.2 AA** for every surface Scruffy's Mop implements or generates. A tool
whose whole job is clearing another auditor's accessibility findings must not
introduce new ones: working keyboard paths, visible focus, correct semantics and
landmarks, sufficient contrast, announced state changes, and layouts that survive
zoom and reflow. Clearing an `accessibility` finding means meeting its named
acceptance check, not approximating it.
