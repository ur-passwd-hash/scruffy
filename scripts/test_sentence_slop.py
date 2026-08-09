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
    if not isinstance(cases, list) or len(cases) < 6:
        fail("fixture must contain at least six cases")

    for case in cases:
        items = case.get("items", [])
        text = case.get("text") or "\n".join(item["text"] for item in items)
        result = analyze(text, mode=case["mode"], context=case["context"], items=items)
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

    print(f"PASS: {len(cases)} sentence-slop cases, compound predicate, and authorship guards")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
