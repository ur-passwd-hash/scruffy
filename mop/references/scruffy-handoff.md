# Scruffy → Scruffy's Mop handoff

Scruffy's Mop is the consumer side of Scruffy's output contract. Scruffy owns every
schema named here; the canonical definitions live in
`../scruffy/references/output-schema.md` and
`../scruffy/schema/audit-contract.json`. Scruffy's Mop reads them and never redefines
them. The machine-readable compatibility key is [`../schema/interop.json`](../schema/interop.json).

## The loop

```
Scruffy AUDIT ─► findings.json + context.json + decisions.json (+ tokens.json)
                        │
                        ▼
        Scruffy's Mop implements approved work orders  ── (redesign/design authority, source_write)
                        │
                        ▼
Scruffy RE-AUDIT (new revision) ─► items move open → fixed / cleared on real evidence
```

Scruffy's Mop occupies the middle box only. It does not diagnose, decide, or clear.

## What Scruffy's Mop reads

| Artifact | Schema | Scruffy's Mop uses it for |
|---|---|---|
| `findings.json` | registry 2.1 (2.0 read-only) | The immutable item registry: `recommendation`, `acceptance_checks`, `depends_on`, `category`, `severity`, `evidence_refs`. IDs and identity keys are never reassigned. |
| `context.json` | 1.1 (1.0 read-only) | `work_orders` (dependency order to implement in), `product_frame` (product truth to preserve), `tasks`, `scores`, `evidence_assets`, `checks_not_run`. |
| `decisions.json` | 2.1 | The approval gate. Scruffy's Mop implements **only** items whose `decision` is `approve`. |
| `tokens.json` | 1.0 (optional) | Observed-value token corrections to apply, mapped to `finding_ids`. |

## Gates Scruffy's Mop must honor

1. **Mode + authority.** Write source only under Scruffy's `redesign` or `design`
   mode with `source_write` capability. Fail closed otherwise. An audit or a
   dashboard decision alone is not source-edit authorization.
2. **Approval.** Only `approve`d decisions are actioned. `pending`, `defer`, and
   `reject` are never implemented.
3. **Dependency order.** Follow Scruffy's work-order order: structural blockers →
   routing/data/state → semantic and interaction primitives → visual tokens and
   responsive composition → page cleanup → verification.
4. **Preserve product truth.** Everything in `product_frame` and outside the
   approved scope survives unchanged.
5. **Don't self-certify.** Scruffy's Mop never sets `status: fixed`/`cleared`. It reports
   changed surfaces mapped to registry IDs; Scruffy's re-audit clears them.

## Version handling

`schema/interop.json` pins the versions Scruffy's Mop understands. Legacy schemas are
readable but read-only. An unrecognized major schema is a hard stop: disclose the
gap and refuse rather than coerce it.
