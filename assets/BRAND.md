# Scruffy — product theme

Scruffy is an interface-maintenance tool, not a mascot collection. Its theme is
a working kit: inspect the product, ground the judgment, apply named principles,
and clean only the work a person approves.

## Product architecture

| Name | Product role | Boundary |
|---|---|---|
| **Scruffy** | The audit tool and orchestrator | Finds, tests, records, and clears evidence-backed interface problems. |
| **DIRT** — Design Intelligence Research & Translation | The reference workspace | Uses applicable Keys, user taste evidence, and optional external reference connectors such as Mobbin MCP. A reference is evidence of a pattern, not proof of quality. |
| **Scruffy's Keys** | The governed principle corpus | Holds attributed principles, source status, exceptions, and operational checks. Candidate material does not become a Key until it passes the admission gates. |
| **Scruffy's Mop** | The implementation engine | Applies human-approved work under explicit authority. It cannot diagnose from scratch or mark its own work fixed. |

The product sequence is:

> **DIRT finds relevant evidence → Keys establish the applicable principles →
> Scruffy makes the finding → the Mop performs approved work.**

## Theme rules

- Keep the maintenance metaphor functional. DIRT, Keys, and the Mop must name
  real product responsibilities.
- Keep Scruffy as the parent product. DIRT and Keys are not separate plugins.
  The Mop is a companion engine in the same repository.
- Treat Mobbin as an external connector used by DIRT, never as a bundled Scruffy
  feature or an authority whose popularity settles a design decision.
- Use jokes sparingly. Product boundaries, evidence, installation, and recovery
  must remain literal.
- Prefer workmanlike language: inspect, ground, test, clear, approve, implement,
  verify. Avoid magical, autonomous, or purity claims.
- Never claim that Scruffy detects AI authorship. It reviews observable output.

## Visual system

The existing character and hero are the primary Scruffy imagery. The character's
keys and broom already support the working-kit theme; do not add a separate
character for every product part.

- Flat 2D adult-animation style
- Deep green, rust, warm gray, ochre, and neutral paper
- Thick, clean linework
- No gradients or pastel AI palettes
- Saturated color only when it carries meaning
- The root `scruffy-hero.png` belongs to Scruffy; combined Scruffy-and-Mop art
  belongs in Mop contexts

## Human-facing language

Use the full expansion on first mention:

- **DIRT — Design Intelligence Research & Translation**
- **Scruffy's Keys — the principle corpus**
- **Scruffy's Mop — the implementation engine**

After that, use DIRT, Keys, and the Mop. Explain provider names such as Mobbin
inside DIRT's evidence, not in the top-level product promise.
