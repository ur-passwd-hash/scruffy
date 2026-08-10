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
from urllib.parse import urlparse

from audit_contract import load_contract, mode_map
from taxonomy_contract import canonical_category_keys, canonical_facet_keys, load_taxonomy


AUDIT_CONTRACT = load_contract()
TAXONOMY = load_taxonomy()
CURRENT_SCHEMA_VERSION = AUDIT_CONTRACT["current_registry_schema"]
LEGACY_SCHEMA_VERSIONS = set(AUDIT_CONTRACT["legacy_registry_schemas"])
SUPPORTED_SCHEMA_VERSIONS = {CURRENT_SCHEMA_VERSION, *LEGACY_SCHEMA_VERSIONS}
RUN_MODES = mode_map(AUDIT_CONTRACT)
CANONICAL_CATEGORIES = set(canonical_category_keys(TAXONOMY))
CANONICAL_FACETS = set(canonical_facet_keys(TAXONOMY))
CATEGORY_FACETS = {row["key"]: set(row["applicable_facets"]) for row in TAXONOMY["categories"]}
LEGACY_CATEGORY_ALIASES = TAXONOMY["legacy_category_aliases"]
CONTEXT_CONTRACT = AUDIT_CONTRACT["context"]
EDITORIAL_CONTRACT = AUDIT_CONTRACT["editorial_review"]
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
EVIDENCE_ID = re.compile(r"^EV-[A-Z0-9][A-Z0-9-]{0,31}$")
ACTIVE_FINDING_STATUSES = {"open", "needs-verification"}
RUNTIME_EVIDENCE_KINDS = {"runtime_trace", "measurement"}
RENDERED_EVIDENCE_KINDS = {"screenshot", "task_observation"}
ACCESSIBILITY_CRITERION = re.compile(
    r"\b(?:WCAG|SC)\s*\d+\.\d+\.\d+\b|\bEN\s*301\s*549\b|\bSection\s*508\b",
    re.IGNORECASE,
)
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
CURRENT_ITEM_FIELDS = {"facets", "evidence_refs", "editorial_review"}
REQUIRED_RUN_FIELDS = {
    "requested_mode",
    "effective_mode",
    "mode_selection_basis",
    "repository_write_authority",
    "authority_basis_type",
    "authority_basis",
    "repository_writes_performed",
    "repository_write_paths",
    "live_demonstration_performed",
    "blind_status",
    "blind_artifact_refs",
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


def require_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        fail(f"{label} must be a boolean")
    return value


def require_unique_text_list(value: Any, label: str, *, allow_empty: bool = True) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(row, str) or not row.strip() for row in value):
        fail(f"{label} must be an array of non-empty strings")
    if len(value) != len(set(value)):
        fail(f"{label} must not contain duplicates")
    if not allow_empty and not value:
        fail(f"{label} cannot be empty")
    return value


def validate_evidence_id(value: Any, label: str) -> str:
    evidence_id = require_text(value, label)
    if not EVIDENCE_ID.fullmatch(evidence_id):
        fail(f"{label} must match {EVIDENCE_ID.pattern}")
    return evidence_id


def validate_run(registry: dict[str, Any], source: str) -> dict[str, Any]:
    run = registry.get("run")
    if not isinstance(run, dict):
        fail(f"{source}.run must be an object for schema {CURRENT_SCHEMA_VERSION}")
    missing = sorted(REQUIRED_RUN_FIELDS - set(run))
    if missing:
        fail(f"{source}.run missing fields: {missing}")

    requested = run.get("requested_mode")
    effective = run.get("effective_mode")
    if requested not in RUN_MODES:
        fail(f"{source}.run.requested_mode is invalid")
    if effective not in RUN_MODES:
        fail(f"{source}.run.effective_mode is invalid")
    if run.get("mode_selection_basis") not in AUDIT_CONTRACT["run"]["mode_selection_basis"]:
        fail(f"{source}.run.mode_selection_basis is invalid")
    authority = run.get("repository_write_authority")
    if authority not in AUDIT_CONTRACT["run"]["authority_states"]:
        fail(f"{source}.run.repository_write_authority is invalid")
    authority_basis_type = run.get("authority_basis_type")
    if authority_basis_type not in AUDIT_CONTRACT["run"]["authority_basis_types"]:
        fail(f"{source}.run.authority_basis_type is invalid")
    require_text(run.get("authority_basis"), f"{source}.run.authority_basis")
    writes = require_bool(run.get("repository_writes_performed"), f"{source}.run.repository_writes_performed")
    paths = require_unique_text_list(run.get("repository_write_paths"), f"{source}.run.repository_write_paths")
    live_demo = require_bool(run.get("live_demonstration_performed"), f"{source}.run.live_demonstration_performed")
    blind_status = run.get("blind_status")
    if blind_status not in AUDIT_CONTRACT["run"]["blind_statuses"]:
        fail(f"{source}.run.blind_status is invalid")
    blind_refs = require_unique_text_list(run.get("blind_artifact_refs"), f"{source}.run.blind_artifact_refs")
    for index, evidence_id in enumerate(blind_refs):
        validate_evidence_id(evidence_id, f"{source}.run.blind_artifact_refs[{index}]")

    mode = RUN_MODES[effective]
    if requested != effective and not (
        requested in {"redesign", "design"}
        and effective == "audit"
        and authority == "not_authorized"
    ):
        fail(f"{source}.run: requested and effective mode conflict without a valid no-authority downgrade")
    if authority == "authorized" and authority_basis_type != "explicit_request":
        fail(f"{source}.run: authorized writes require an explicit_request authority basis")
    if authority == "not_authorized" and authority_basis_type != "not_granted":
        fail(f"{source}.run: not_authorized must use a not_granted authority basis")
    if effective in {"audit", "demonstrate_fix"} and authority != "not_authorized":
        fail(f"{source}.run: mode {effective} cannot carry repository-write authority")
    if writes and not mode["repository_writes_allowed"]:
        fail(f"{source}.run: mode {effective} forbids repository writes")
    if writes and authority != "authorized":
        fail(f"{source}.run: repository writes occurred without authorization")
    if writes != bool(paths):
        fail(f"{source}.run: repository_write_paths must be present exactly when writes occurred")
    if effective in {"redesign", "design"} and authority != "authorized":
        fail(f"{source}.run: mode {effective} requires explicit repository-write authority")
    if live_demo and not mode["live_demonstration_allowed"]:
        fail(f"{source}.run: mode {effective} does not permit a live demonstration")
    if blind_status == "verified" and len(blind_refs) < 3:
        fail(f"{source}.run: verified blindness requires manifest, discovery, and freeze evidence")
    if blind_status == "not_run" and blind_refs:
        fail(f"{source}.run: blind_artifact_refs must be empty when blindness was not run")
    return run


def validate_editorial_review(review: Any, label: str, *, kind: str, status: str) -> set[str]:
    if not isinstance(review, dict):
        fail(f"{label} must be an object for copy findings and enhancements")
    required = {
        "review_type",
        "sample_adequacy",
        "analysis_language_scope",
        "language_review_basis",
        "analyzer_evidence_ref",
        "independent_signal_families",
        "manual_checks",
        "consequence",
        "counterexample_tested",
        "authorship_assessment",
    }
    missing = sorted(required - set(review))
    if missing:
        fail(f"{label} missing fields: {missing}")
    review_type = review.get("review_type")
    if review_type not in EDITORIAL_CONTRACT["review_types"]:
        fail(f"{label}.review_type is invalid")
    adequacy = review.get("sample_adequacy")
    if adequacy not in EDITORIAL_CONTRACT["sample_adequacy"]:
        fail(f"{label}.sample_adequacy is invalid")
    language_scope = review.get("analysis_language_scope")
    if language_scope not in EDITORIAL_CONTRACT["analysis_language_scopes"]:
        fail(f"{label}.analysis_language_scope is invalid")
    language_basis = review.get("language_review_basis")
    if language_basis not in EDITORIAL_CONTRACT["language_review_bases"]:
        fail(f"{label}.language_review_basis is invalid")
    if review.get("authorship_assessment") != EDITORIAL_CONTRACT["authorship_assessment"]:
        fail(f"{label}.authorship_assessment must be not_performed")
    require_text(review.get("consequence"), f"{label}.consequence")
    require_text(review.get("counterexample_tested"), f"{label}.counterexample_tested")
    families = require_unique_text_list(
        review.get("independent_signal_families"),
        f"{label}.independent_signal_families",
    )
    unknown_families = sorted(set(families) - set(EDITORIAL_CONTRACT["sentence_signal_families"]))
    if unknown_families:
        fail(f"{label}.independent_signal_families contains unknown values: {unknown_families}")
    analyzer_ref = review.get("analyzer_evidence_ref")
    evidence_refs: set[str] = set()
    if analyzer_ref is not None:
        evidence_refs.add(validate_evidence_id(analyzer_ref, f"{label}.analyzer_evidence_ref"))

    checks = review.get("manual_checks")
    if not isinstance(checks, list) or not checks:
        fail(f"{label}.manual_checks must be a non-empty array")
    by_code: dict[str, dict[str, Any]] = {}
    allowed_codes = set(EDITORIAL_CONTRACT["sentence_manual_checks"]) | set(EDITORIAL_CONTRACT["editorial_manual_checks"])
    for index, check in enumerate(checks):
        check_label = f"{label}.manual_checks[{index}]"
        if not isinstance(check, dict):
            fail(f"{check_label} must be an object")
        code = check.get("code")
        if code not in allowed_codes:
            fail(f"{check_label}.code is invalid")
        if code in by_code:
            fail(f"{label}.manual_checks repeats {code}")
        result = check.get("result")
        if result not in EDITORIAL_CONTRACT["manual_check_results"]:
            fail(f"{check_label}.result is invalid")
        require_text(check.get("evidence"), f"{check_label}.evidence")
        evidence_ref = check.get("evidence_ref")
        if evidence_ref is None:
            fail(f"{check_label}.evidence_ref must link the manual conclusion to typed evidence")
        evidence_refs.add(validate_evidence_id(evidence_ref, f"{check_label}.evidence_ref"))
        by_code[code] = check

    sentence_review = review_type in {"sentence_pattern", "mixed"}
    if sentence_review:
        if adequacy not in {"adequate", "limited"}:
            fail(f"{label}: sentence-pattern review requires an adequate or limited sample")
        if analyzer_ref is None:
            fail(f"{label}: sentence-pattern review requires an analyzer evidence receipt")
        expected_basis = {
            "en": "verified_english_analyzer",
            "non_en": "language_competent_human",
        }.get(language_scope)
        if expected_basis is None:
            fail(f"{label}: sentence-pattern review requires verified en or non_en language scope")
        if language_basis != expected_basis:
            fail(f"{label}: {language_scope} sentence review requires {expected_basis}")
        if len(families) < 2:
            fail(f"{label}: sentence-pattern review requires two independent signal families")
        missing_sentence_checks = sorted(set(EDITORIAL_CONTRACT["sentence_manual_checks"]) - set(by_code))
        if missing_sentence_checks:
            fail(f"{label}: sentence-pattern review is missing {missing_sentence_checks}")
        incomplete = [
            code
            for code in EDITORIAL_CONTRACT["sentence_manual_checks"]
            if by_code[code]["result"] in {"not_run", "not_applicable"}
        ]
        if incomplete:
            fail(f"{label}: sentence manual checks are incomplete: {incomplete}")
        if review_type == "mixed":
            missing_editorial_checks = sorted(set(EDITORIAL_CONTRACT["editorial_manual_checks"]) - set(by_code))
            if missing_editorial_checks:
                fail(f"{label}: mixed editorial review is missing {missing_editorial_checks}")
            incomplete_editorial = [
                code
                for code in EDITORIAL_CONTRACT["editorial_manual_checks"]
                if by_code[code]["result"] == "not_run"
            ]
            if incomplete_editorial and kind == "finding" and status in {"open", "needs-verification"}:
                fail(f"{label}: active mixed editorial finding has not-run checks: {incomplete_editorial}")
    else:
        if adequacy not in {"not_applicable", "insufficient"}:
            fail(f"{label}: non-sentence editorial review must use not_applicable or insufficient sampling")
        if language_scope != "not_applicable" or language_basis != "not_applicable":
            fail(f"{label}: non-sentence editorial review must use not_applicable language fields")
        if families:
            fail(f"{label}: non-sentence editorial review cannot claim sentence signal families")
        if analyzer_ref is not None:
            fail(f"{label}: non-sentence editorial review cannot attach a sentence analyzer receipt")
        missing_editorial_checks = sorted(set(EDITORIAL_CONTRACT["editorial_manual_checks"]) - set(by_code))
        if missing_editorial_checks:
            fail(f"{label}: editorial review is missing {missing_editorial_checks}")
        incomplete = [code for code in EDITORIAL_CONTRACT["editorial_manual_checks"] if by_code[code]["result"] == "not_run"]
        if incomplete and kind == "finding" and status in {"open", "needs-verification"}:
            fail(f"{label}: active editorial finding has not-run checks: {incomplete}")
    return evidence_refs


def validate_registry(registry: dict[str, Any], source: str = "registry") -> dict[str, dict[str, Any]]:
    schema_version = registry.get("schema_version")
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        fail(f"{source}: schema_version must be one of {sorted(SUPPORTED_SCHEMA_VERSIONS)}")
    if schema_version == CURRENT_SCHEMA_VERSION:
        validate_run(registry, source)
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
        required_fields = REQUIRED_ITEM_FIELDS | (CURRENT_ITEM_FIELDS if schema_version == CURRENT_SCHEMA_VERSION else set())
        missing = sorted(required_fields - set(item))
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
        category = item["category"]
        if schema_version == CURRENT_SCHEMA_VERSION:
            if category not in CANONICAL_CATEGORIES:
                legacy_target = LEGACY_CATEGORY_ALIASES.get(category)
                suffix = f"; use canonical key {legacy_target}" if legacy_target else ""
                fail(f"{label}.category is not canonical{suffix}")
            facets = require_unique_text_list(item["facets"], f"{label}.facets")
            unknown_facets = sorted(set(facets) - CANONICAL_FACETS)
            if unknown_facets:
                fail(f"{label}.facets contains unknown values: {unknown_facets}")
            incompatible_facets = sorted(set(facets) - CATEGORY_FACETS[category])
            if incompatible_facets:
                fail(f"{label}.facets are not applicable to {category}: {incompatible_facets}")
            evidence_refs = require_unique_text_list(
                item["evidence_refs"],
                f"{label}.evidence_refs",
                allow_empty=False,
            )
            for evidence_index, evidence_id in enumerate(evidence_refs):
                validate_evidence_id(evidence_id, f"{label}.evidence_refs[{evidence_index}]")
            if category == "copy" and kind in {"finding", "enhancement"}:
                validate_editorial_review(
                    item["editorial_review"],
                    f"{label}.editorial_review",
                    kind=kind,
                    status=status,
                )
            elif item["editorial_review"] is not None:
                fail(f"{label}.editorial_review must be null outside copy findings and enhancements")
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
    if decisions.get("schema_version") != registry.get("schema_version"):
        fail("decisions.schema_version must match the registry schema_version")
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


def validate_context(
    context: dict[str, Any],
    registry: dict[str, Any],
    *,
    base_path: Path,
) -> dict[str, dict[str, Any]]:
    if registry.get("schema_version") != CURRENT_SCHEMA_VERSION:
        return {}
    required = {
        "schema_version",
        "audit_id",
        "revision_id",
        "title",
        "outcome",
        "product_frame",
        "tasks",
        "capabilities",
        "scores",
        "work_orders",
        "checks_not_run",
        "evidence_assets",
    }
    missing = sorted(required - set(context))
    if missing:
        fail(f"context missing fields: {missing}")
    if context.get("schema_version") != CONTEXT_CONTRACT["schema_version"]:
        fail(f"context.schema_version must be {CONTEXT_CONTRACT['schema_version']}")
    for field in ("audit_id", "revision_id"):
        if context.get(field) != registry.get(field):
            fail(f"context.{field} does not match registry")
    require_text(context.get("title"), "context.title")

    outcome = context.get("outcome")
    if not isinstance(outcome, dict):
        fail("context.outcome must be an object")
    for field in ("label", "summary", "confidence"):
        require_text(outcome.get(field), f"context.outcome.{field}")

    assets = context.get("evidence_assets")
    if not isinstance(assets, list):
        fail("context.evidence_assets must be an array")
    by_evidence: dict[str, dict[str, Any]] = {}
    for index, asset in enumerate(assets):
        label = f"context.evidence_assets[{index}]"
        if not isinstance(asset, dict):
            fail(f"{label} must be an object")
        evidence_id = validate_evidence_id(asset.get("id"), f"{label}.id")
        if evidence_id in by_evidence:
            fail(f"context.evidence_assets repeats {evidence_id}")
        kind = asset.get("kind")
        if kind not in CONTEXT_CONTRACT["evidence_kinds"]:
            fail(f"{label}.kind is invalid")
        locator = require_text(asset.get("locator"), f"{label}.locator")
        require_text(asset.get("description"), f"{label}.description")
        verification = asset.get("verification")
        if verification not in CONTEXT_CONTRACT["evidence_verification"]:
            fail(f"{label}.verification is invalid")
        parsed = urlparse(locator)
        explicit_uri = re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", locator)
        if explicit_uri and parsed.scheme not in {"http", "https"}:
            fail(f"{label}.locator uses an unsupported URI scheme")
        if kind in {"screenshot", "source", "runtime_trace", "copy_sample", "analysis_receipt"} and not explicit_uri and verification == "captured":
            candidate_text = re.sub(r":\d+$", "", locator.split("#", 1)[0])
            candidate = Path(candidate_text)
            if not candidate.is_absolute():
                candidate = base_path / candidate
            if not candidate.exists():
                fail(f"{label}.locator does not exist: {locator}")
        by_evidence[evidence_id] = asset

    def check_refs(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
        refs = require_unique_text_list(value, label, allow_empty=allow_empty)
        for ref_index, evidence_id in enumerate(refs):
            validate_evidence_id(evidence_id, f"{label}[{ref_index}]")
            if evidence_id not in by_evidence:
                fail(f"{label} references missing evidence {evidence_id}")
        return refs

    questions = context.get("product_frame")
    if not isinstance(questions, list):
        fail("context.product_frame must be an array")
    expected_questions = {row["key"] for row in CONTEXT_CONTRACT["product_frame_questions"]}
    by_question: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(questions):
        label = f"context.product_frame[{index}]"
        if not isinstance(row, dict):
            fail(f"{label} must be an object")
        key = row.get("key")
        if key not in expected_questions:
            fail(f"{label}.key is invalid")
        if key in by_question:
            fail(f"context.product_frame repeats {key}")
        require_text(row.get("answer"), f"{label}.answer")
        if row.get("basis") not in CONTEXT_CONTRACT["product_frame_bases"]:
            fail(f"{label}.basis is invalid")
        by_question[key] = row
    if set(by_question) != expected_questions:
        fail(f"context.product_frame must cover exactly {sorted(expected_questions)}")

    tasks = context.get("tasks")
    if not isinstance(tasks, list) or not 3 <= len(tasks) <= 5:
        fail("context.tasks must contain three to five representative tasks")
    task_ids: set[str] = set()
    for index, task in enumerate(tasks):
        label = f"context.tasks[{index}]"
        if not isinstance(task, dict):
            fail(f"{label} must be an object")
        task_id = require_text(task.get("id"), f"{label}.id")
        if task_id in task_ids:
            fail(f"context.tasks repeats {task_id}")
        task_ids.add(task_id)
        for field in ("goal", "result"):
            require_text(task.get(field), f"{label}.{field}")
        if task.get("status") not in CONTEXT_CONTRACT["task_statuses"]:
            fail(f"{label}.status is invalid")
        check_refs(task.get("evidence_refs"), f"{label}.evidence_refs")

    capability_rows = context.get("capabilities")
    if not isinstance(capability_rows, list):
        fail("context.capabilities must be an array")
    expected_capabilities = {row["key"] for row in CONTEXT_CONTRACT["capabilities"]}
    by_capability: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(capability_rows):
        label = f"context.capabilities[{index}]"
        if not isinstance(row, dict):
            fail(f"{label} must be an object")
        key = row.get("key")
        if key not in expected_capabilities:
            fail(f"{label}.key is invalid")
        if key in by_capability:
            fail(f"context.capabilities repeats {key}")
        if row.get("status") not in CONTEXT_CONTRACT["capability_statuses"]:
            fail(f"{label}.status is invalid")
        require_text(row.get("scope"), f"{label}.scope")
        by_capability[key] = row
    if set(by_capability) != expected_capabilities:
        fail(f"context.capabilities must cover exactly {sorted(expected_capabilities)}")
    source_write_status = by_capability["source_write"]["status"]
    run = registry["run"]
    if run["repository_write_authority"] == "not_authorized" and source_write_status != "not_authorized":
        fail("context.capabilities source_write must be not_authorized when the run has no write authority")
    if run["repository_write_authority"] == "authorized" and source_write_status == "not_authorized":
        fail("context.capabilities source_write contradicts the run's write authority")
    if run["repository_writes_performed"] and source_write_status not in {"available", "partial"}:
        fail("context.capabilities source_write must be available or partial when repository writes occurred")

    scores = context.get("scores")
    if not isinstance(scores, list):
        fail("context.scores must be an array")
    by_score: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(scores):
        label = f"context.scores[{index}]"
        if not isinstance(row, dict):
            fail(f"{label} must be an object")
        category = row.get("category")
        if category not in CANONICAL_CATEGORIES:
            fail(f"{label}.category is not canonical")
        if category in by_score:
            fail(f"context.scores repeats {category}")
        if row.get("score") not in CONTEXT_CONTRACT["score_values"]:
            fail(f"{label}.score is invalid")
        require_text(row.get("evidence"), f"{label}.evidence")
        check_refs(row.get("evidence_refs"), f"{label}.evidence_refs")
        by_score[category] = row
    if set(by_score) != CANONICAL_CATEGORIES:
        fail(f"context.scores must cover exactly {sorted(CANONICAL_CATEGORIES)}")

    checks_not_run = context.get("checks_not_run")
    if not isinstance(checks_not_run, list):
        fail("context.checks_not_run must be an array")
    for index, row in enumerate(checks_not_run):
        label = f"context.checks_not_run[{index}]"
        if not isinstance(row, dict):
            fail(f"{label} must be an object")
        for field in ("check", "reason", "impact"):
            require_text(row.get(field), f"{label}.{field}")

    work_orders = context.get("work_orders")
    if not isinstance(work_orders, list):
        fail("context.work_orders must be an array")
    registry_ids = {item["id"] for item in registry["items"]}
    work_ids: set[str] = set()
    for index, row in enumerate(work_orders):
        label = f"context.work_orders[{index}]"
        if not isinstance(row, dict):
            fail(f"{label} must be an object")
        work_id = require_text(row.get("id"), f"{label}.id")
        if work_id in work_ids:
            fail(f"context.work_orders repeats {work_id}")
        work_ids.add(work_id)
        for field in ("title", "summary", "verification"):
            require_text(row.get(field), f"{label}.{field}")
        item_ids = require_unique_text_list(row.get("item_ids"), f"{label}.item_ids", allow_empty=False)
        unknown_items = sorted(set(item_ids) - registry_ids)
        if unknown_items:
            fail(f"{label}.item_ids contains unknown items: {unknown_items}")
        require_unique_text_list(row.get("acceptance_checks"), f"{label}.acceptance_checks", allow_empty=False)

    items = validate_registry(registry, "registry")
    for item_id, item in items.items():
        for evidence_id in item["evidence_refs"]:
            if evidence_id not in by_evidence:
                fail(f"registry item {item_id} references missing evidence {evidence_id}")
            if item["confidence"] == "high" and by_evidence[evidence_id]["verification"] == "not_verified":
                fail(f"registry item {item_id} claims high confidence from unverified evidence {evidence_id}")
        if item["category"] == "copy" and item["kind"] in {"finding", "enhancement"}:
            editorial_refs = validate_editorial_review(
                item["editorial_review"],
                f"registry item {item_id}.editorial_review",
                kind=item["kind"],
                status=item["status"],
            )
            missing_editorial = sorted(editorial_refs - set(by_evidence))
            if missing_editorial:
                fail(f"registry item {item_id} editorial review references missing evidence: {missing_editorial}")
            unattached_editorial = sorted(editorial_refs - set(item["evidence_refs"]))
            if unattached_editorial:
                fail(f"registry item {item_id} editorial review evidence is absent from item evidence_refs: {unattached_editorial}")
            analyzer_ref = item["editorial_review"].get("analyzer_evidence_ref")
            if analyzer_ref is not None and by_evidence[analyzer_ref]["kind"] != "analysis_receipt":
                fail(f"registry item {item_id} analyzer evidence must use kind analysis_receipt")

        evidence_kinds = {
            by_evidence[evidence_id]["kind"]
            for evidence_id in item["evidence_refs"]
            if evidence_id in by_evidence
        }
        if item["kind"] == "finding" and item["status"] in ACTIVE_FINDING_STATUSES:
            if item["category"] == "performance" and not evidence_kinds & RUNTIME_EVIDENCE_KINDS:
                fail(
                    f"registry item {item_id} is an active performance finding without runtime evidence"
                    " (attach a runtime_trace or measurement receipt, or mark the item needs-verification evidence)"
                )
            if item["category"] == "accessibility":
                if "accessibility_observation" not in evidence_kinds:
                    fail(
                        f"registry item {item_id} is an active accessibility finding without an"
                        " accessibility_observation receipt"
                    )
                claim_text = " ".join([item["title"], item["observation"], *item["evidence"]])
                if not ACCESSIBILITY_CRITERION.search(claim_text):
                    fail(
                        f"registry item {item_id} is an active accessibility finding without a named"
                        " criterion (for example WCAG 1.4.3)"
                    )
            if item["category"] == "visual" and not evidence_kinds & RENDERED_EVIDENCE_KINDS:
                fail(
                    f"registry item {item_id} is an active visual finding without rendered evidence"
                    " (attach a screenshot or task_observation receipt; source-only visual claims are unverified)"
                )

    screenshots_status = by_capability["screenshots"]["status"]
    screenshot_assets = [asset for asset in by_evidence.values() if asset["kind"] == "screenshot"]
    if screenshots_status in {"available", "partial"} and not screenshot_assets:
        fail(
            "context.capabilities claims screenshots "
            f"{screenshots_status} but the run captured no screenshot evidence asset;"
            " record the capability as not_run, unavailable, or not_needed instead"
        )
    if screenshots_status in {"unavailable", "not_run", "not_authorized", "not_needed"} and any(
        asset.get("verification") == "captured" for asset in screenshot_assets
    ):
        fail("captured screenshot evidence contradicts the screenshots capability status")

    missing_blind = sorted(set(run["blind_artifact_refs"]) - set(by_evidence))
    if missing_blind:
        fail(f"registry.run.blind_artifact_refs references missing evidence: {missing_blind}")
    return by_evidence


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
    parser.add_argument("--context", type=Path)
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
    if registry.get("schema_version") == CURRENT_SCHEMA_VERSION and not args.context:
        fail(f"schema {CURRENT_SCHEMA_VERSION} registries require --context")
    if args.context:
        validate_context(load_json(args.context), registry, base_path=args.context.parent)
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
    if args.context:
        checks.append("context and evidence")
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
