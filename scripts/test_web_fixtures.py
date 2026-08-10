#!/usr/bin/env python3
"""Integrity tests for the known-answer web fixtures and their hidden key."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = ROOT / "evals" / "web-fixtures"
KEY_PATH = FIXTURE_DIR / "keys" / "expectations.json"
PAGES = ("checkout-flow.html", "pricing-page.html", "settings-form.html")
ALLOWED_DISPOSITIONS = {"candidate", "cleared", "not_run"}
SAMPLE_ATTRIBUTE = re.compile(r'data-sample="([A-Z0-9-]+)"')
NONDETERMINISM = re.compile(r"Date\.now\(|Math\.random\(")
EXTERNAL_ASSET = re.compile(r'(?:src|href)="https?://', re.IGNORECASE)
AUTHORSHIP = re.compile(r"authorship|ai-generated|written by ai|perplexity|burstiness", re.IGNORECASE)


def fail(message: str) -> None:
    raise ValueError(message)


def main() -> int:
    key = json.loads(KEY_PATH.read_text(encoding="utf-8"))
    expectations = key.get("sample_expectations")
    if not isinstance(expectations, dict) or not expectations:
        fail("key needs a non-empty sample_expectations object")
    if key.get("authorship_labels_used") is not False:
        fail("key must declare authorship_labels_used false")

    for sample_id, row in expectations.items():
        if row.get("expected_disposition") not in ALLOWED_DISPOSITIONS:
            fail(f"{sample_id}: expected_disposition must be one of {sorted(ALLOWED_DISPOSITIONS)}")
        planted = row.get("planted")
        if row["expected_disposition"] == "candidate" and not planted:
            fail(f"{sample_id}: a planted defect needs a planted description")
        if row["expected_disposition"] == "cleared" and planted:
            fail(f"{sample_id}: a cleared guard must not describe a planted defect")
        if not row.get("detectable_by"):
            fail(f"{sample_id}: record how the disposition is detectable")

    seen: dict[str, str] = {}
    per_page: dict[str, list[str]] = {}
    for page in PAGES:
        text = (FIXTURE_DIR / page).read_text(encoding="utf-8")
        if NONDETERMINISM.search(text):
            fail(f"{page}: fixtures must be deterministic (no Date.now or Math.random)")
        if EXTERNAL_ASSET.search(text):
            fail(f"{page}: fixtures must be self-contained (no external URLs)")
        samples = SAMPLE_ATTRIBUTE.findall(text)
        if len(samples) != len(set(samples)):
            fail(f"{page}: duplicate data-sample attribute")
        for sample_id in samples:
            if sample_id in seen:
                fail(f"{sample_id} appears in both {seen[sample_id]} and {page}")
            seen[sample_id] = page
        per_page[page] = samples

    if set(seen) != set(expectations):
        missing = sorted(set(expectations) - set(seen))
        extra = sorted(set(seen) - set(expectations))
        fail(f"key and pages disagree; missing in pages: {missing}; missing in key: {extra}")

    for page, samples in per_page.items():
        dispositions = {expectations[sample_id]["expected_disposition"] for sample_id in samples}
        if "candidate" not in dispositions or "cleared" not in dispositions:
            fail(f"{page}: every fixture page needs at least one planted defect and one cleared guard")

    joined = KEY_PATH.read_text(encoding="utf-8")
    for match in AUTHORSHIP.findall(joined):
        if match.lower() != "authorship":
            fail(f"key must not carry authorship-detection language: {match}")

    planted_count = sum(1 for row in expectations.values() if row["expected_disposition"] == "candidate")
    cleared_count = sum(1 for row in expectations.values() if row["expected_disposition"] == "cleared")
    print(
        "PASS: web fixtures are deterministic and self-contained; "
        f"{planted_count} planted defects and {cleared_count} cleared guards agree with the hidden key"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
