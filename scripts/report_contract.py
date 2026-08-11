"""Shared display projections for Scruffy Markdown and dashboard renderers."""

from __future__ import annotations

from typing import Any

from audit_contract import load_contract
from taxonomy_contract import load_taxonomy


AUDIT_CONTRACT = load_contract()
TAXONOMY = load_taxonomy()
QUESTION_LABELS = {row["key"]: row["label"] for row in AUDIT_CONTRACT["context"]["product_frame_questions"]}
CAPABILITY_LABELS = {row["key"]: row["label"] for row in AUDIT_CONTRACT["context"]["capabilities"]}
CATEGORY_LABELS = {row["key"]: row["public_label"] for row in TAXONOMY["categories"]}
SCORE_LABELS = {row["key"]: row["score_label"] for row in TAXONOMY["categories"]}


def evidence_by_id(context: dict[str, Any]) -> dict[str, dict[str, Any]]:
    assets = context.get("evidence_assets", [])
    if not isinstance(assets, list):
        return {}
    return {
        row["id"]: row
        for row in assets
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }


def evidence_summary(refs: Any, context: dict[str, Any]) -> str:
    if not isinstance(refs, list):
        return ""
    assets = evidence_by_id(context)
    values = []
    for evidence_id in refs:
        asset = assets.get(evidence_id, {})
        description = asset.get("description")
        values.append(f"{evidence_id}: {description}" if description else str(evidence_id))
    return "; ".join(values)


def product_rows(context: dict[str, Any]) -> list[list[Any]]:
    return [
        [QUESTION_LABELS.get(row.get("key"), row.get("question", "")), row.get("answer", ""), row.get("basis", "")]
        for row in context.get("product_frame", [])
    ]


TASK_STATUS_LABELS = {"pass": "Pass", "fail": "Fail", "partial": "Partial",
                      "needs_verification": "Needs verification", "not_run": "Not run"}


def task_rows(context: dict[str, Any]) -> list[list[Any]]:
    return [
        [
            row.get("id", ""),
            TASK_STATUS_LABELS.get(row.get("status", ""), row.get("status", "")),
            row.get("goal", ""),
            row.get("result", ""),
            row.get("evidence", "") or evidence_summary(row.get("evidence_refs"), context),
        ]
        for row in context.get("tasks", [])
    ]


def capability_rows(context: dict[str, Any]) -> list[list[Any]]:
    return [
        [CAPABILITY_LABELS.get(row.get("key"), row.get("capability", "")), row.get("status", ""), row.get("scope", "")]
        for row in context.get("capabilities", [])
    ]


def score_row_label(key: Any) -> str:
    """Name the canonical slop category first so a reader can map a score to the
    public category, then the measurement framing used for the score itself.
    When the measurement framing adds no words beyond the public label
    ("Accessibility slop · Accessibility"), show the public label alone."""
    public = CATEGORY_LABELS.get(key)
    scored = SCORE_LABELS.get(key)
    if public and scored:
        if scored.lower() == public.lower().removesuffix(" slop"):
            return public
        return f"{public} · {scored}"
    return public or scored or str(key or "")


def score_rows(context: dict[str, Any]) -> list[list[Any]]:
    return [
        [score_row_label(row.get("category")), row.get("score", ""), row.get("evidence", "")]
        for row in context.get("scores", [])
    ]


def checks_not_run(context: dict[str, Any]) -> list[str]:
    output: list[str] = []
    for row in context.get("checks_not_run", []):
        if isinstance(row, str):
            output.append(row)
        elif isinstance(row, dict):
            output.append(f"{row.get('check', '')} — {row.get('reason', '')} Impact: {row.get('impact', '')}".strip())
    return output


def public_category_label(key: str) -> str:
    return CATEGORY_LABELS.get(key, key)
