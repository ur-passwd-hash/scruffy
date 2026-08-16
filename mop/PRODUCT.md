# Scruffy repair workflow — product contract

This directory is an internal compatibility boundary inside **Scruffy**. It is
not a companion product. The historic `mop/`, `mop_*`, and `scruffys-mop`
machine identifiers remain stable so existing bundles, scripts, and installed
skills do not break.

## Job

Turn approved, evidence-backed Scruffy findings into coherent source changes,
then return the changed surfaces for a new Scruffy audit. Visual redesign is a
first-class use case, with selectable image-grounded directions and a craft
floor that applies even when external reference or implementation tools are
unavailable.

## Contract

- Scruffy owns `findings.json`, `context.json`, `decisions.json`, and the audit
  schemas. Repair consumes those artifacts read-only.
- Only items marked `approve` are implemented, and only under explicit
  source-write authority. A dashboard decision alone is not write authority.
- Dependency order and `product_frame` constraints are preserved.
- Visual directions cite applicable principles and require an image anchor.
- Evidence from another target is refused as cross-product leakage.
- Implementation never sets `fixed` or `cleared`; a re-audit does.
- Generated dashboards meet the same accessibility and evidence standards as
  the rest of Scruffy.

## Product identity

The only human-facing name is **Scruffy**. Use one Scruffy character and the root
`assets/scruffy-hero.png`. Describe reference grounding, principles, audit,
repair, and verification as workflow stages—not separate mascots or tools.

## Runtime

The canonical repair instructions are `SKILL.md`, the compatibility key is
`schema/interop.json`, and the required entrypoint is
`python3 scripts/mop_run.py <bundle-dir>`. The stable filenames are machine
interfaces, not brand architecture.
