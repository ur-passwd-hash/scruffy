#!/usr/bin/env python3
"""Render and validate Scruffy's run, context, and editorial contracts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "schema" / "audit-contract.json"
REFERENCE = ROOT / "references" / "audit-contract.md"
README = ROOT / "README.md"
README_START = "<!-- scruffy-modes:start -->"
README_END = "<!-- scruffy-modes:end -->"


def load_contract(path: Path = MANIFEST) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != "1.0":
        raise ValueError("audit-contract schema_version must be 1.0")
    if data.get("current_registry_schema") != "2.1":
        raise ValueError("current registry schema must be 2.1")
    modes = data.get("run", {}).get("modes")
    if not isinstance(modes, list) or len(modes) != 4:
        raise ValueError("audit contract must define four run modes")
    required_mode_fields = {
        "key", "label", "repository_writes_allowed", "live_demonstration_allowed", "description",
    }
    if any(not isinstance(row, dict) or required_mode_fields - set(row) for row in modes):
        raise ValueError("each run mode must define the complete execution contract")
    mode_keys = [row.get("key") for row in modes]
    if len(mode_keys) != len(set(mode_keys)) or any(not isinstance(value, str) for value in mode_keys):
        raise ValueError("run-mode keys must be unique strings")
    run = data["run"]
    for field in ("mode_selection_basis", "blind_statuses", "authority_states", "authority_basis_types"):
        values = run.get(field)
        if not isinstance(values, list) or not values or len(values) != len(set(values)) or any(not isinstance(value, str) for value in values):
            raise ValueError(f"run.{field} must be a non-empty unique string array")
    questions = data.get("context", {}).get("product_frame_questions")
    capabilities = data.get("context", {}).get("capabilities")
    if not isinstance(questions, list) or len(questions) != 6:
        raise ValueError("audit context must define six product-frame questions")
    if not isinstance(capabilities, list) or len(capabilities) != 9:
        raise ValueError("audit context must define nine capabilities")
    capability_keys = [row.get("key") for row in capabilities if isinstance(row, dict)]
    if len(capability_keys) != 9 or len(capability_keys) != len(set(capability_keys)):
        raise ValueError("audit context repeats a capability key")
    context = data["context"]
    if context.get("schema_version") != "1.1":
        raise ValueError("current context schema must be 1.1")
    legacy_context_schemas = context.get("legacy_schema_versions")
    if (
        not isinstance(legacy_context_schemas, list)
        or not legacy_context_schemas
        or len(legacy_context_schemas) != len(set(legacy_context_schemas))
        or any(not isinstance(value, str) for value in legacy_context_schemas)
    ):
        raise ValueError("context.legacy_schema_versions must be a non-empty unique string array")
    for field in (
        "product_frame_bases", "task_statuses", "capability_statuses", "score_values",
        "evidence_kinds", "evidence_verification",
    ):
        values = context.get(field)
        if not isinstance(values, list) or not values or len(values) != len(set(map(str, values))):
            raise ValueError(f"context.{field} must be a non-empty unique array")
    if "analysis_receipt" not in context["evidence_kinds"]:
        raise ValueError("audit context must define analysis_receipt evidence")
    annotation_statuses = context.get("visual_annotation_statuses")
    if annotation_statuses != ["provided", "not_needed"]:
        raise ValueError("context.visual_annotation_statuses must define provided and not_needed")
    max_regions = context.get("visual_annotation_max_regions")
    if not isinstance(max_regions, int) or isinstance(max_regions, bool) or max_regions < 1:
        raise ValueError("context.visual_annotation_max_regions must be a positive integer")
    editorial = data.get("editorial_review", {})
    if editorial.get("authorship_assessment") != "not_performed":
        raise ValueError("editorial contract must prohibit authorship assessment")
    if len(editorial.get("sentence_manual_checks", [])) != 4:
        raise ValueError("editorial contract must define four sentence manual checks")
    if len(editorial.get("editorial_manual_checks", [])) != 4:
        raise ValueError("editorial contract must define four broader editorial checks")
    for field in (
        "review_types", "sample_adequacy", "analysis_language_scopes", "language_review_bases",
        "sentence_signal_families", "manual_check_results",
        "sentence_manual_checks", "editorial_manual_checks",
    ):
        values = editorial.get(field)
        if not isinstance(values, list) or not values or len(values) != len(set(values)):
            raise ValueError(f"editorial_review.{field} must be a non-empty unique array")
    return data


def mode_map(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["key"]: row for row in data["run"]["modes"]}


def render_reference(data: dict[str, Any]) -> str:
    lines = [
        "# Audit execution contract",
        "",
        "> Generated from `schema/audit-contract.json` by `scripts/audit_contract.py`. Do not edit this file directly.",
        "",
        "This contract turns mode selection, source-write authority, capability coverage, evidence receipts, and editorial review into data that validators can enforce.",
        "",
        "## Run modes",
        "",
        "| Mode | Repository writes | Live demonstration | Contract |",
        "|---|---|---|---|",
    ]
    for row in data["run"]["modes"]:
        writes = "Allowed with explicit authority" if row["repository_writes_allowed"] else "Forbidden"
        demo = "Allowed" if row["live_demonstration_allowed"] else "Not part of the mode"
        lines.append(f"| **{row['label']}** (`{row['key']}`) | {writes} | {demo} | {row['description']} |")
    lines.extend(
        [
            "",
            "Every schema-2.1 registry records requested and effective mode, whether selection was explicit or inferred, the authority state, an `explicit_request` or `not_granted` authority basis type, the human-readable authority basis, whether repository writes or a live demonstration occurred, affected write paths, and blind status. AUDIT and DEMONSTRATE-FIX cannot carry repository-write authority and fail validation if repository writes are reported. REDESIGN and DESIGN fail validation without an explicit-request authority receipt. An unauthorized design/redesign request may only downgrade to AUDIT.",
            "",
            "## Capability contract",
            "",
            "Every substantial audit records exactly these capabilities. Missing capability is not a finding; use `not_run`, `unavailable`, `not_needed`, or `not_authorized` and explain the scope.",
            "",
        ]
    )
    for row in data["context"]["capabilities"]:
        lines.append(f"- `{row['key']}` — {row['label']}")
    lines.extend(
        [
            "",
            "## Evidence receipts",
            "",
            "Schema-2.1 context stores evidence as typed receipts with an immutable ID, kind, locator, description, and verification state. Registry items reference those IDs through `evidence_refs`. A local screenshot or source locator must exist when the validator can resolve it. URLs must use HTTP or HTTPS. A non-empty prose claim is not an evidence receipt.",
            "",
            "New audits emit context schema 1.1. Every locally captured screenshot has one claim-specific visual context for each registry item that cites it, or one unlinked context when no item cites it. Each context records the operated state, a precise `look_at` instruction, the connection to the claim, and an annotation decision. `provided` annotations contain one to four percentage-based rectangles with visible labels. `not_needed` requires a reason explaining why the whole frame is the evidence or why an overlay would misrepresent a nonvisual claim. Generic asset descriptions do not satisfy this contract.",
            "",
            "## Editorial review",
            "",
            "Every active `copy` finding carries an `editorial_review` receipt. Editorial review includes content strategy, terminology, information sequence, microcopy, claims and provenance, recovery language, voice, and sentence construction.",
            "",
            "Sentence-pattern findings require an adequate or limited reader-facing sample, a recorded language scope, an analyzer evidence receipt, all four sentence manual checks, a demonstrated consequence, a tested counterexample, and `authorship_assessment: not_performed`. English findings use `verified_english_analyzer`; non-English findings require `language_competent_human` and retain the analyzer's abstention receipt. Unknown language cannot produce a sentence-pattern finding. Other editorial findings use `not_applicable` for sentence sampling and language analysis but must complete the applicable editorial checks and prove their consequence.",
            "",
            "Allowed independent sentence-signal families are: "
            + ", ".join(f"`{value}`" for value in data["editorial_review"]["sentence_signal_families"])
            + ". A receipt cannot invent new family names to satisfy the two-family threshold.",
            "",
            "## Backward compatibility",
            "",
            "Schema 2.0 and context schema 1.0 remain readable so published audit history survives. New audits emit registry schema 2.1 with context schema 1.1. A new revision may reconcile an older baseline without rewriting the baseline artifact.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_readme(data: dict[str, Any]) -> str:
    lines = [
        README_START,
        "## Modes",
        "",
        "| Mode | Use it for | Repository authority |",
        "|---|---|---|",
    ]
    for row in data["run"]["modes"]:
        authority = "Explicit source-write authority required" if row["repository_writes_allowed"] else "Repository writes forbidden"
        lines.append(f"| **{row['label']}** | {row['description']} | {authority} |")
    lines.extend(
        [
            "",
            "New schema-2.1 reports record requested mode, effective mode, selection basis, explicit-request write authority, performed mutations, live demonstrations, and blind status. Validation fails closed when those facts conflict.",
            README_END,
        ]
    )
    return "\n".join(lines)


def replace_readme_block(text: str, rendered: str) -> str:
    generated = re.compile(rf"{re.escape(README_START)}.*?{re.escape(README_END)}", re.S)
    if generated.search(text):
        return generated.sub(rendered, text)
    existing = re.search(r"(?ms)^## Modes\n.*?(?=^## Install\n)", text)
    if not existing:
        raise ValueError("README modes section or generated markers were not found")
    return text[: existing.start()] + rendered + "\n\n" + text[existing.end() :]


def expected_readme(data: dict[str, Any]) -> str:
    return replace_readme_block(README.read_text(encoding="utf-8"), render_readme(data))


def check(data: dict[str, Any]) -> list[str]:
    expected = render_reference(data)
    failures: list[str] = []
    if not REFERENCE.is_file() or REFERENCE.read_text(encoding="utf-8") != expected:
        failures.append("references/audit-contract.md is stale or missing")
    if README.read_text(encoding="utf-8") != expected_readme(data):
        failures.append("README run-mode projection is stale")
    return failures


def write(data: dict[str, Any]) -> None:
    REFERENCE.write_text(render_reference(data), encoding="utf-8")
    README.write_text(expected_readme(data), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    try:
        data = load_contract()
        if args.write:
            write(data)
            print("PASS: audit-contract reference updated")
            return 0
        failures = check(data)
        if failures:
            for failure in failures:
                print(f"FAIL: {failure}", file=sys.stderr)
            return 1
        print("PASS: audit execution contract and reference are synchronized")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
