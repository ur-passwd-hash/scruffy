# Output contract

For durable or repeated audits, [references/durability.md](durability.md) is binding. Keep stable IDs and identity keys across revisions. Never remove a prior item or assign its identity to another problem.

## Required artifact set

For a substantial file-backed audit, produce:

1. `findings.json` — complete registry, revision lineage, and presentation lists
2. `decisions.json` — one decision record per finding/enhancement plus history
3. Markdown report — complete human-readable audit
4. Self-contained HTML dashboard when a viewer is available
5. `tokens.json` only when observed token changes are proposed

Chat-only work emits the same registry as a JSON block when files are unavailable.

## Markdown and dashboard order

1. Outcome and evidence boundary
2. Product framing and representative tasks
3. Capability and coverage ledger
4. Category scores and verbal result
5. Prioritized findings (maximum eight)
6. Additional open and needs-verification findings
7. Prioritized and additional enhancements
8. Strengths to preserve
9. Fixed, cleared, merged, and superseded items
10. Revision reconciliation table
11. Work orders and acceptance checks
12. Checks not run

Every registry item must be present in the Markdown report and HTML dashboard. Collapsing resolved items is allowed; omission is not.

## Registry item

```json
{
  "id": "AS-01",
  "identity_key": "contents-navigation-affordance",
  "kind": "finding",
  "title": "Contents does not behave as scalable navigation",
  "category": "information-architecture",
  "severity": "medium",
  "confidence": "high",
  "status": "open",
  "revision_disposition": "carried",
  "first_seen_revision": "r1",
  "last_observed_revision": "r2",
  "observation": "What happened without interpretation",
  "user_impact": "Who is affected and which task becomes harder",
  "evidence": ["measurement, task result, source location, or screenshot"],
  "cause": "Verified or explicitly inferred cause",
  "recommendation": "Smallest coherent change",
  "acceptance_checks": ["observable pass condition"],
  "depends_on": [],
  "disposition_reason": "Why this item carried or changed state",
  "destination_id": null
}
```

Allowed statuses: `open`, `fixed`, `cleared`, `needs-verification`, `merged`, `superseded`.

Allowed revision dispositions: `new`, `carried`, `reopened`, `fixed`, `cleared`, `merged`, `superseded`.

`merged` and `superseded` require `destination_id`. `fixed` and `cleared` require direct revision evidence. Findings require severity `critical`, `high`, `medium`, or `low`. Strengths use `none`. Enhancements use `high`, `medium`, or `low` as priority.

## Decisions

```json
{
  "schema_version": "2.0",
  "audit_id": "stable-product-id",
  "revision_id": "r2",
  "baseline_revision_id": "r1",
  "decisions": [
    {
      "item_id": "AS-01",
      "decision": "pending",
      "note": "",
      "updated_at": null,
      "decision_source": "current",
      "destination_id": null,
      "history": []
    }
  ]
}
```

Allowed decisions are `pending`, `approve`, `defer`, and `reject`. Preserve history append-only. A merged or superseded source retains its decision; never transfer approval to the destination automatically.

## Token data

Create `tokens.json` only from observed current values:

```json
{
  "schema_version": "1.0",
  "tokens": [
    {
      "name": "color.text.muted",
      "current": "#777777",
      "proposed": "#555555",
      "reason": "Measured contrast correction",
      "finding_ids": ["AS-11"]
    }
  ]
}
```

If no token layer exists, label current values as observed literals and make token extraction part of the work order.

## Interactive HTML report

Include:

- All twelve required sections in the prescribed order
- Every registry item, keyed by immutable ID
- Filterable status/kind/severity views
- Evidence and acceptance checks without hover dependence
- Approve/defer/reject plus notes for findings and enhancements
- Copy/download of schema-v2 decisions and findings
- Prior-decision import or explicit migration instructions
- Print-friendly styling and keyboard-operable controls
- No external runtime dependency unless requested

Use the complete registry as the rendering source. Do not hand-maintain a separate HTML findings list.

## Implementation work orders

Order approved work by dependency:

1. Shared structural blockers
2. Routing, data, and state contracts
3. Semantic and interaction primitives
4. Visual tokens and responsive composition
5. Page-specific cleanup
6. Verification and regression tests

Each work order names affected surfaces, registry IDs, dependencies, acceptance checks, and verification method. An audit or dashboard decision is not source-edit authorization unless the user requested implementation.
