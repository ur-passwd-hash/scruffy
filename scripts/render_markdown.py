#!/usr/bin/env python3
"""Render a complete Scruffy Markdown report from schema-v2 source data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from report_contract import (
    capability_rows,
    checks_not_run,
    evidence_summary,
    product_rows,
    public_category_label,
    score_rows,
    task_rows,
)


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"FAIL: {path} must contain an object")
    return data


def clean(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def bullets(values: list[Any], empty: str = "None recorded.") -> str:
    return "\n".join(f"- {clean(value)}" for value in values) if values else empty


def table(headers: list[str], rows: list[list[Any]]) -> str:
    output = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    output.extend("| " + " | ".join(clean(value) for value in row) + " |" for row in rows)
    return "\n".join(output)


def render_item(item: dict[str, Any], decision: dict[str, Any] | None, context: dict[str, Any]) -> str:
    destination = f" -> {item['destination_id']}" if item.get("destination_id") else ""
    dependencies = ", ".join(item.get("depends_on", [])) or "none"
    decision_text = ""
    if item["kind"] in {"finding", "enhancement"}:
        row = decision or {}
        decision_text = (
            f"\n\n**Decision:** {clean(row.get('decision', 'pending'))}  "
            f"\n**Decision note:** {clean(row.get('note', '')) or 'None.'}"
        )
    facets = ", ".join(item.get("facets", [])) or "none"
    receipts = evidence_summary(item.get("evidence_refs"), context) or "Legacy untyped evidence"
    editorial = item.get("editorial_review")
    editorial_text = ""
    if isinstance(editorial, dict):
        families = ", ".join(editorial.get("independent_signal_families", [])) or "not applicable"
        editorial_text = (
            f"\n\n**Editorial review:** {clean(editorial.get('review_type', ''))} · "
            f"sample {clean(editorial.get('sample_adequacy', ''))} · "
            f"language {clean(editorial.get('analysis_language_scope', 'legacy'))} "
            f"({clean(editorial.get('language_review_basis', 'unrecorded'))}) · signals {clean(families)} · "
            f"authorship {clean(editorial.get('authorship_assessment', 'not_performed'))}"
        )
    return f"""<!-- anti-slop-item:{item['id']} -->
### {item['id']} · {clean(item['title'])}

**Kind:** {item['kind']} · **Category:** {clean(public_category_label(item['category']))} (`{clean(item['category'])}`) · **Facets:** {clean(facets)}

**Severity/priority:** {item['severity']} · **Confidence:** {item['confidence']}

**Status:** {item['status']} · **Revision disposition:** {item['revision_disposition']}{destination}

{clean(item['observation'])}

**User impact:** {clean(item['user_impact'])}

**Evidence**

{bullets(item.get('evidence', []))}

**Evidence receipts:** {clean(receipts)}{editorial_text}

**Cause:** {clean(item['cause'])}

**Recommended change or preservation rule:** {clean(item['recommendation'])}

**Acceptance checks**

{bullets(item.get('acceptance_checks', []), 'No acceptance checks required for this strength.')}

**Dependencies:** {clean(dependencies)}  
**Revision reason:** {clean(item.get('disposition_reason') or 'New in this revision.')}{decision_text}
"""


def render(registry: dict[str, Any], context: dict[str, Any], decision_doc: dict[str, Any]) -> str:
    items = registry["items"]
    by_id = {item["id"]: item for item in items}
    decisions = {row["item_id"]: row for row in decision_doc.get("decisions", [])}
    presentation = registry["presentation"]
    prioritized_findings = [by_id[item_id] for item_id in presentation["prioritized_finding_ids"]]
    prioritized_finding_ids = set(presentation["prioritized_finding_ids"])
    additional_findings = [
        item for item in items
        if item["kind"] == "finding"
        and item["status"] in {"open", "needs-verification"}
        and item["id"] not in prioritized_finding_ids
    ]
    prioritized_enhancements = [by_id[item_id] for item_id in presentation["prioritized_enhancement_ids"]]
    prioritized_enhancement_ids = set(presentation["prioritized_enhancement_ids"])
    additional_enhancements = [
        item for item in items
        if item["kind"] == "enhancement"
        and item["status"] in {"open", "needs-verification"}
        and item["id"] not in prioritized_enhancement_ids
    ]
    strengths = [by_id[item_id] for item_id in presentation["strength_ids"]]
    resolved = [item for item in items if item["status"] in {"fixed", "cleared", "merged", "superseded"}]

    def item_group(values: list[dict[str, Any]], empty: str) -> str:
        return "\n\n".join(render_item(item, decisions.get(item["id"]), context) for item in values) if values else empty

    outcome = context.get("outcome", {})
    product_table_rows = product_rows(context)
    task_table_rows = task_rows(context)
    capability_table_rows = capability_rows(context)
    score_table_rows = score_rows(context)
    reconciliation_rows = [
        [item["id"], item["status"], item["revision_disposition"], item.get("destination_id") or "-", item.get("disposition_reason") or "New in this revision."]
        for item in items
    ]
    work_orders = []
    for order in context.get("work_orders", []):
        work_orders.append(
            f"### {clean(order.get('id', ''))} · {clean(order.get('title', ''))}\n\n"
            f"{clean(order.get('summary', ''))}\n\n"
            f"**Items:** {clean(', '.join(order.get('item_ids', [])) or 'none')}  \n"
            f"**Verification:** {clean(order.get('verification', ''))}\n\n"
            f"{bullets(order.get('acceptance_checks', []), 'No acceptance checks recorded.')}"
        )

    title = clean(context.get("title", "Scruffy audit"))
    return f"""# {title}

Target: {clean(registry.get('target', ''))}  
Audit: `{registry['audit_id']}` · Revision: `{registry['revision_id']}` · Baseline: `{registry.get('baseline_revision_id') or 'none'}`
{f"Mode: `{registry['run']['effective_mode']}` · Write authority: `{registry['run']['repository_write_authority']}` · Blindness: `{registry['run']['blind_status']}`" if isinstance(registry.get('run'), dict) else "Mode and authority: legacy schema did not record a machine-enforced run receipt."}

<!-- anti-slop-section:outcome -->
## Outcome and evidence boundary

**{clean(outcome.get('label', 'Insufficient evidence'))}** — {clean(outcome.get('summary', ''))}

Confidence: {clean(outcome.get('confidence', 'unknown'))}

<!-- anti-slop-section:product-frame -->
## Product framing

{table(['Question', 'Answer', 'Basis'], product_table_rows)}

<!-- anti-slop-section:task-ledger -->
## Representative tasks

{table(['ID', 'Goal', 'Result', 'Status', 'Evidence'], task_table_rows)}

<!-- anti-slop-section:capability-ledger -->
## Capability and coverage ledger

{table(['Capability', 'Status', 'Scope'], capability_table_rows)}

<!-- anti-slop-section:score -->
## Category scores and result

{table(['Category', 'Score', 'Evidence'], score_table_rows)}

<!-- anti-slop-section:findings -->
## Prioritized findings

{item_group(prioritized_findings, 'No prioritized findings.')}

## Additional active findings

{item_group(additional_findings, 'No additional active findings.')}

<!-- anti-slop-section:enhancements -->
## Enhancements

{item_group(prioritized_enhancements, 'No prioritized enhancements.')}

## Additional enhancements

{item_group(additional_enhancements, 'No additional enhancements.')}

<!-- anti-slop-section:strengths -->
## Strengths to preserve

{item_group(strengths, 'No strengths recorded.')}

<!-- anti-slop-section:resolved -->
## Fixed, cleared, merged, and superseded

{item_group(resolved, 'No resolved items.')}

<!-- anti-slop-section:reconciliation -->
## Revision reconciliation

{table(['ID', 'Status', 'Disposition', 'Destination', 'Reason'], reconciliation_rows)}

<!-- anti-slop-section:work-orders -->
## Work orders and acceptance checks

{chr(10).join(work_orders) if work_orders else 'No work orders recorded.'}

<!-- anti-slop-section:checks-not-run -->
## Checks not run

{bullets(checks_not_run(context), 'No checks-not-run entries recorded.')}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry", type=Path)
    parser.add_argument("context", type=Path)
    parser.add_argument("decisions", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    registry = load(args.registry)
    context = load(args.context)
    decisions = load(args.decisions)
    rendered = render(registry, context, decisions)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"PASS: rendered {len(registry.get('items', []))} registry items to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
