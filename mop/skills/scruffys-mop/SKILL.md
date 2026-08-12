---
name: scruffys-mop
description: Implement and verify fixes for AI slop that Scruffy has already audited. Use when a Scruffy audit exists (findings.json, context.json, decisions.json, optional tokens.json) and approved findings must be turned into real, high-craft source changes under repository-write authority, then handed back for re-audit. Consumes Scruffy's output contract read-only; implements only approved work orders in dependency order; never diagnoses, scores authorship, or marks its own work fixed. Do not use to produce a fresh audit or findings (that is Scruffy), or for non-interface code work.
---

# Scruffy's Mop (discovery adapter)

This is the discovery projection for Agent Skills runtimes. The canonical runtime
instructions live in the repository-root [`SKILL.md`](../../SKILL.md); load it and
`schema/interop.json` before acting. Do not add fix rules here.
