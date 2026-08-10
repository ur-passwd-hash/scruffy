#!/usr/bin/env python3
"""Regression tests for sentence-quality measurements and false-positive guards."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from analyze_sentence_slop import analyze


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "evals" / "sentence-slop" / "cases.json"


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) < 12:
        fail("fixture must contain at least twelve cases")

    for case in cases:
        items = case.get("items", [])
        text = case.get("text") or "\n".join(item["text"] for item in items)
        result = analyze(
            text,
            mode=case["mode"],
            context=case["context"],
            language=case.get("language", data.get("language", "unknown")),
            items=items,
        )
        codes = {lead["code"] for lead in result["leads"]}
        missing = set(case.get("expected_leads", [])) - codes
        forbidden = set(case.get("forbidden_leads", [])) & codes
        if missing:
            fail(f"{case['id']} missing expected leads: {sorted(missing)}; got {sorted(codes)}")
        if forbidden:
            fail(f"{case['id']} produced forbidden leads: {sorted(forbidden)}")
        if result["compound_signal"]["review_needed"] is not case["review_needed"]:
            fail(
                f"{case['id']} review_needed was {result['compound_signal']['review_needed']}; "
                f"expected {case['review_needed']}"
            )
        if result["compound_signal"]["finding_eligible"] is not False:
            fail(f"{case['id']} analyzer must never auto-create a finding")
        if result["authorship_assessment"] != "not_performed":
            fail(f"{case['id']} made an authorship assessment")
        if not result["guards"]["no_authorship_inference"]:
            fail(f"{case['id']} lacks the authorship guard")
        if result["schema_version"] != "1.2":
            fail(f"{case['id']} returned an unexpected schema version")
        if any("signal_family" not in lead for lead in result["leads"]):
            fail(f"{case['id']} returned a lead without a signal family")
        families = set(result["compound_signal"]["independent_signal_families"])
        if result["compound_signal"]["independent_signal_count"] != len(families):
            fail(f"{case['id']} independent-signal count does not match its families")

        expected_families = set(case.get("expected_signal_families", []))
        if expected_families and not expected_families.issubset(families):
            fail(
                f"{case['id']} missing expected signal families: "
                f"{sorted(expected_families - families)}; got {sorted(families)}"
            )
        if case.get("expected_dependency_collapse") and not result["compound_signal"]["dependency_collapses"]:
            fail(f"{case['id']} did not collapse duplicated evidence")

        normalization = result["normalization"]
        excluded_minimum = int(case.get("expected_words_excluded_min", 0))
        if normalization["words_excluded"] < excluded_minimum:
            fail(
                f"{case['id']} excluded {normalization['words_excluded']} words; "
                f"expected at least {excluded_minimum}"
            )
        removed = normalization.get("removed", {})
        missing_removed = [name for name in case.get("expected_removed", []) if removed.get(name, 0) < 1]
        if missing_removed:
            fail(f"{case['id']} did not record removed source structures: {missing_removed}")
        rendered = json.dumps(result).lower()
        leaked = [value for value in case.get("forbidden_result_substrings", []) if value.lower() in rendered]
        if leaked:
            fail(f"{case['id']} leaked excluded markup/code into analysis: {leaked}")

        manual_codes = {check["code"] for check in result["manual_review"]["checks"]}
        missing_manual = set(case.get("manual_check_codes", [])) - manual_codes
        if missing_manual:
            fail(f"{case['id']} missing manual checks: {sorted(missing_manual)}")
        if case["mode"] == "prose" and result["sample"]["adequacy"] != "insufficient":
            if not result["manual_review"]["required"]:
                fail(f"{case['id']} did not require the semantic/manual pass")
        expected_language_status = case.get("expected_language_status", "supported")
        if result["language_analysis_status"] != expected_language_status:
            fail(
                f"{case['id']} language status was {result['language_analysis_status']}; "
                f"expected {expected_language_status}"
            )
        if expected_language_status == "abstained":
            if result["leads"] or result["compound_signal"]["review_needed"]:
                fail(f"{case['id']} did not abstain from English-specific leads")
            if not result["guards"]["unsupported_language_abstention"]:
                fail(f"{case['id']} lacks the unsupported-language guard")

    print(
        f"PASS: {len(cases)} sentence-slop cases, markup normalization, independent-family predicate, "
        "manual semantic checks, and authorship guards"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
