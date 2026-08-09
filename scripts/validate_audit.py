#!/usr/bin/env python3
"""Validate durable Scruffy registries, decisions, and HTML dashboards."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "2.0"
KINDS = {"finding", "enhancement", "strength"}
STATUSES = {"open", "fixed", "cleared", "needs-verification", "merged", "superseded"}
DISPOSITIONS = {"new", "carried", "reopened", "fixed", "cleared", "merged", "superseded"}
DECISIONS = {"pending", "approve", "defer", "reject"}
CONFIDENCE = {"high", "moderate", "low", "unknown"}
FINDING_SEVERITIES = {"critical", "high", "medium", "low"}
NON_FINDING_SEVERITIES = {"high", "medium", "low", "none"}
# Preserve legacy public IDs such as ENH-1; continuity outranks cosmetic padding.
ITEM_ID = re.compile(r"^[A-Z][A-Z0-9]{1,5}-\d{1,4}$")
IDENTITY_KEY = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED_ITEM_FIELDS = {
    "id",
    "identity_key",
    "kind",
    "title",
    "category",
    "severity",
    "confidence",
    "status",
    "revision_disposition",
    "first_seen_revision",
    "last_observed_revision",
    "observation",
    "user_impact",
    "evidence",
    "cause",
    "recommendation",
    "acceptance_checks",
    "depends_on",
    "disposition_reason",
    "destination_id",
}
REQUIRED_DASHBOARD_SECTIONS = {
    "outcome",
    "product-frame",
    "task-ledger",
    "capability-ledger",
    "score",
    "findings",
    "enhancements",
    "strengths",
    "resolved",
    "reconciliation",
    "work-orders",
    "checks-not-run",
}


def fail(message: str) -> None:
    raise ValueError(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"{path}: unreadable JSON: {error}")
    if not isinstance(data, dict):
        fail(f"{path}: root must be an object")
    return data


def require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be a non-empty string")
    return value


def validate_registry(registry: dict[str, Any], source: str = "registry") -> dict[str, dict[str, Any]]:
    if registry.get("schema_version") != SCHEMA_VERSION:
        fail(f"{source}: schema_version must be {SCHEMA_VERSION}")
    audit_id = require_text(registry.get("audit_id"), f"{source}.audit_id")
    require_text(registry.get("target"), f"{source}.target")
    revision_id = require_text(registry.get("revision_id"), f"{source}.revision_id")
    baseline_revision = registry.get("baseline_revision_id")
    if baseline_revision is not None and (not isinstance(baseline_revision, str) or not baseline_revision.strip()):
        fail(f"{source}.baseline_revision_id must be null or a non-empty string")

    items = registry.get("items")
    if not isinstance(items, list):
        fail(f"{source}.items must be an array")

    by_id: dict[str, dict[str, Any]] = {}
    by_identity: dict[str, str] = {}
    for index, item in enumerate(items):
        label = f"{source}.items[{index}]"
        if not isinstance(item, dict):
            fail(f"{label} must be an object")
        missing = sorted(REQUIRED_ITEM_FIELDS - set(item))
        if missing:
            fail(f"{label} missing fields: {missing}")
        item_id = require_text(item["id"], f"{label}.id")
        identity = require_text(item["identity_key"], f"{label}.identity_key")
        if not ITEM_ID.fullmatch(item_id):
            fail(f"{label}.id is invalid: {item_id}")
        if not IDENTITY_KEY.fullmatch(identity):
            fail(f"{label}.identity_key is invalid: {identity}")
        if item_id in by_id:
            fail(f"{source}: duplicate item id {item_id}")
        if identity in by_identity:
            fail(f"{source}: identity_key {identity} reused by {by_identity[identity]} and {item_id}")
        by_id[item_id] = item
        by_identity[identity] = item_id

        kind = item["kind"]
        status = item["status"]
        disposition = item["revision_disposition"]
        if kind not in KINDS:
            fail(f"{label}.kind must be one of {sorted(KINDS)}")
        if status not in STATUSES:
            fail(f"{label}.status must be one of {sorted(STATUSES)}")
        if disposition not in DISPOSITIONS:
            fail(f"{label}.revision_disposition must be one of {sorted(DISPOSITIONS)}")
        if item["confidence"] not in CONFIDENCE:
            fail(f"{label}.confidence must be one of {sorted(CONFIDENCE)}")
        allowed_severity = FINDING_SEVERITIES if kind == "finding" else NON_FINDING_SEVERITIES
        if item["severity"] not in allowed_severity:
            fail(f"{label}.severity is invalid for kind {kind}")
        if kind == "strength" and item["severity"] != "none":
            fail(f"{label}: strengths must use severity none")
        for field in ("title", "category", "first_seen_revision", "last_observed_revision"):
            require_text(item[field], f"{label}.{field}")
        for field in ("evidence", "acceptance_checks", "depends_on"):
            if not isinstance(item[field], list):
                fail(f"{label}.{field} must be an array")
        if not item["evidence"] and kind != "strength":
            fail(f"{label}.evidence cannot be empty")
        if not item["acceptance_checks"] and kind != "strength":
            fail(f"{label}.acceptance_checks cannot be empty")
        if disposition != "new":
            require_text(item["disposition_reason"], f"{label}.disposition_reason")
        destination = item["destination_id"]
        if disposition in {"merged", "superseded"} or status in {"merged", "superseded"}:
            require_text(destination, f"{label}.destination_id")
        elif destination is not None:
            fail(f"{label}.destination_id must be null unless merged or superseded")
        expected_status = {"fixed": "fixed", "cleared": "cleared", "merged": "merged", "superseded": "superseded"}
        if disposition in expected_status and status != expected_status[disposition]:
            fail(f"{label}: disposition {disposition} requires status {expected_status[disposition]}")
        if disposition == "reopened" and status not in {"open", "needs-verification"}:
            fail(f"{label}: reopened requires open or needs-verification status")

    for item_id, item in by_id.items():
        destination = item["destination_id"]
        if destination is not None:
            if destination == item_id:
                fail(f"{source}: {item_id} cannot point to itself")
            if destination not in by_id:
                fail(f"{source}: {item_id} points to missing destination {destination}")
        for dependency in item["depends_on"]:
            if dependency not in by_id:
                fail(f"{source}: {item_id} depends on missing item {dependency}")

    presentation = registry.get("presentation")
    if not isinstance(presentation, dict):
        fail(f"{source}.presentation must be an object")
    expected_lists = {
        "prioritized_finding_ids",
        "prioritized_enhancement_ids",
        "strength_ids",
        "cleared_ids",
    }
    missing_lists = sorted(expected_lists - set(presentation))
    if missing_lists:
        fail(f"{source}.presentation missing lists: {missing_lists}")
    for name in expected_lists:
        values = presentation[name]
        if not isinstance(values, list) or len(values) != len(set(values)):
            fail(f"{source}.presentation.{name} must be a unique array")
        unknown = [item_id for item_id in values if item_id not in by_id]
        if unknown:
            fail(f"{source}.presentation.{name} has unknown IDs: {unknown}")
    if len(presentation["prioritized_finding_ids"]) > 8:
        fail(f"{source}: prioritized findings exceed eight")
    if len(presentation["prioritized_enhancement_ids"]) > 5:
        fail(f"{source}: prioritized enhancements exceed five")
    for item_id in presentation["prioritized_finding_ids"]:
        if by_id[item_id]["kind"] != "finding" or by_id[item_id]["status"] not in {"open", "needs-verification"}:
            fail(f"{source}: prioritized finding {item_id} is not an active finding")
    for item_id in presentation["prioritized_enhancement_ids"]:
        if by_id[item_id]["kind"] != "enhancement" or by_id[item_id]["status"] not in {"open", "needs-verification"}:
            fail(f"{source}: prioritized enhancement {item_id} is not active")
    for item_id in presentation["strength_ids"]:
        if by_id[item_id]["kind"] != "strength":
            fail(f"{source}: strength list contains non-strength {item_id}")
    for item_id in presentation["cleared_ids"]:
        if by_id[item_id]["status"] not in {"fixed", "cleared", "merged", "superseded"}:
            fail(f"{source}: cleared list contains active item {item_id}")

    registry["audit_id"] = audit_id
    registry["revision_id"] = revision_id
    return by_id


def validate_baseline(current: dict[str, Any], baseline: dict[str, Any]) -> None:
    current_items = validate_registry(current, "current")
    baseline_items = validate_registry(baseline, "baseline")
    if current["audit_id"] != baseline["audit_id"]:
        fail("current and baseline audit_id differ")
    if current.get("baseline_revision_id") != baseline["revision_id"]:
        fail("current.baseline_revision_id must equal baseline.revision_id")
    missing = sorted(set(baseline_items) - set(current_items))
    if missing:
        fail(f"current registry silently dropped baseline IDs: {missing}")
    baseline_identity = {item["identity_key"]: item_id for item_id, item in baseline_items.items()}
    for item_id, prior in baseline_items.items():
        now = current_items[item_id]
        if now["identity_key"] != prior["identity_key"]:
            fail(f"{item_id} reused for a new identity: {prior['identity_key']} -> {now['identity_key']}")
        if now["first_seen_revision"] != prior["first_seen_revision"]:
            fail(f"{item_id}.first_seen_revision changed")
        if now["revision_disposition"] == "new":
            fail(f"baseline item {item_id} cannot have disposition new")
        if prior["status"] in {"fixed", "cleared"} and now["status"] in {"open", "needs-verification"} and now["revision_disposition"] != "reopened":
            fail(f"resolved item {item_id} became active without disposition reopened")
    for item_id, item in current_items.items():
        if item_id not in baseline_items and item["identity_key"] in baseline_identity:
            fail(f"new ID {item_id} reuses baseline identity from {baseline_identity[item['identity_key']]}")
        if item_id not in baseline_items and item["revision_disposition"] != "new":
            fail(f"new item {item_id} must have disposition new")


def validate_decisions(decisions: dict[str, Any], registry: dict[str, Any], baseline_decisions: dict[str, Any] | None = None) -> None:
    items = validate_registry(registry, "registry")
    if decisions.get("schema_version") != SCHEMA_VERSION:
        fail("decisions.schema_version must be 2.0")
    for field in ("audit_id", "revision_id", "baseline_revision_id"):
        if decisions.get(field) != registry.get(field):
            fail(f"decisions.{field} does not match registry")
    rows = decisions.get("decisions")
    if not isinstance(rows, list):
        fail("decisions.decisions must be an array")
    required_ids = {item_id for item_id, item in items.items() if item["kind"] in {"finding", "enhancement"}}
    by_id: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        label = f"decisions[{index}]"
        if not isinstance(row, dict):
            fail(f"{label} must be an object")
        item_id = row.get("item_id")
        if item_id in by_id:
            fail(f"duplicate decision for {item_id}")
        if item_id not in required_ids:
            fail(f"orphan decision for {item_id}")
        if row.get("decision") not in DECISIONS:
            fail(f"{label}.decision is invalid")
        if not isinstance(row.get("note"), str):
            fail(f"{label}.note must be a string")
        if row.get("updated_at") is not None and not isinstance(row.get("updated_at"), str):
            fail(f"{label}.updated_at must be null or a string")
        if not isinstance(row.get("history"), list):
            fail(f"{label}.history must be an array")
        destination = row.get("destination_id")
        if destination is not None and destination not in items:
            fail(f"{label}.destination_id is unknown")
        by_id[item_id] = row
    missing = sorted(required_ids - set(by_id))
    if missing:
        fail(f"decisions missing item IDs: {missing}")

    if baseline_decisions is not None:
        prior_rows = baseline_decisions.get("decisions")
        if not isinstance(prior_rows, list):
            fail("baseline decisions are invalid")
        prior_by_id = {(row.get("item_id") or row.get("finding_id")): row for row in prior_rows if isinstance(row, dict)}
        for item_id in set(prior_by_id) & set(by_id):
            prior = prior_by_id[item_id]
            now = by_id[item_id]
            if prior.get("decision") != "pending" and now.get("decision_source") == "migrated":
                if now.get("decision") != prior.get("decision"):
                    fail(f"migrated decision changed for {item_id}")


class DashboardParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.section_ids: set[str] = set()
        self.item_ids: list[str] = []
        self.decision_ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            self.section_ids.add(element_id)
        item_id = values.get("data-item-id")
        if item_id:
            self.item_ids.append(item_id)
        decision_for = values.get("data-decision-for")
        if decision_for:
            self.decision_ids.add(decision_for)


def validate_dashboard(path: Path, registry: dict[str, Any]) -> None:
    items = validate_registry(registry, "registry")
    parser = DashboardParser()
    try:
        parser.feed(path.read_text(encoding="utf-8"))
    except OSError as error:
        fail(f"dashboard unreadable: {error}")
    missing_sections = sorted(REQUIRED_DASHBOARD_SECTIONS - parser.section_ids)
    if missing_sections:
        fail(f"dashboard missing required sections: {missing_sections}")
    duplicates = sorted({item_id for item_id in parser.item_ids if parser.item_ids.count(item_id) > 1})
    if duplicates:
        fail(f"dashboard repeats item IDs: {duplicates}")
    missing_items = sorted(set(items) - set(parser.item_ids))
    extra_items = sorted(set(parser.item_ids) - set(items))
    if missing_items:
        fail(f"dashboard omits registry items: {missing_items}")
    if extra_items:
        fail(f"dashboard has unregistered items: {extra_items}")
    decision_required = {
        item_id
        for item_id, item in items.items()
        if item["kind"] in {"finding", "enhancement"} and item["status"] in {"open", "needs-verification"}
    }
    missing_controls = sorted(decision_required - parser.decision_ids)
    if missing_controls:
        fail(f"dashboard lacks decision controls for active items: {missing_controls}")


def validate_markdown(path: Path, registry: dict[str, Any]) -> None:
    items = validate_registry(registry, "registry")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        fail(f"Markdown report unreadable: {error}")
    section_ids = set(re.findall(r"<!--\s*anti-slop-section:([a-z-]+)\s*-->", text))
    item_ids = re.findall(r"<!--\s*anti-slop-item:([A-Z][A-Z0-9-]+)\s*-->", text)
    missing_sections = sorted(REQUIRED_DASHBOARD_SECTIONS - section_ids)
    if missing_sections:
        fail(f"Markdown report missing required sections: {missing_sections}")
    duplicates = sorted({item_id for item_id in item_ids if item_ids.count(item_id) > 1})
    if duplicates:
        fail(f"Markdown report repeats item IDs: {duplicates}")
    missing_items = sorted(set(items) - set(item_ids))
    extra_items = sorted(set(item_ids) - set(items))
    if missing_items:
        fail(f"Markdown report omits registry items: {missing_items}")
    if extra_items:
        fail(f"Markdown report has unregistered items: {extra_items}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry", type=Path)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--decisions", type=Path)
    parser.add_argument("--baseline-decisions", type=Path)
    parser.add_argument("--dashboard", type=Path)
    parser.add_argument("--markdown", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    registry = load_json(args.registry)
    validate_registry(registry)
    if args.baseline:
        validate_baseline(registry, load_json(args.baseline))
    if args.decisions:
        baseline_decisions = load_json(args.baseline_decisions) if args.baseline_decisions else None
        validate_decisions(load_json(args.decisions), registry, baseline_decisions)
    if args.dashboard:
        validate_dashboard(args.dashboard, registry)
    if args.markdown:
        validate_markdown(args.markdown, registry)
    checks = ["registry"]
    if args.baseline:
        checks.append("baseline continuity")
    if args.decisions:
        checks.append("decisions")
    if args.dashboard:
        checks.append("dashboard completeness")
    if args.markdown:
        checks.append("Markdown completeness")
    print("PASS: " + ", ".join(checks))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValueError as error:
        raise SystemExit(f"FAIL: {error}")
