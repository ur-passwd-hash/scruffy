#!/usr/bin/env python3
"""Regression test for deterministic blind packet routing."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from run_sentence_blind import run_packet


def main() -> int:
    samples = [
        {
            "id": "A-01", "mode": "ui", "context": "general", "language": "en",
            "items": [
                {"surface": str(index), "text": "Your change was rejected."}
                for index in range(8)
            ],
        },
        {
            "id": "B-02", "mode": "prose", "context": "safety", "language": "en",
            "text": "Stop the press. Turn the switch off. Keep both hands clear. Tell the floor lead. Wait behind the line. Do not restart the press.",
        },
        {
            "id": "C-03", "mode": "prose", "context": "general", "language": "en",
            "text": "At 6:12 on Friday morning, Maya opened the bakery and found the proofing cabinet at 52 degrees instead of 78. The rye loaves had barely risen. She moved forty trays to the warm oven and called the Elm Street cafe. The new monitor now records cabinet temperature every five minutes. When a reading falls below 74, it names the affected batch and texts the opener. After three weeks, the bakery had two overnight drops. Both were caught before mixing began, and neither delayed a delivery. The owner still keeps a paper checklist beside the ovens because a dead phone should not stop breakfast.",
        },
        {
            "id": "D-04", "mode": "prose", "context": "general", "language": "non_en",
            "text": "Nuestro equipo abre la tienda a las nueve. Cada pan lleva su precio y una lista clara de ingredientes. Cuando falta un producto, el cartel explica cuándo volverá.",
        },
    ]
    result = run_packet(samples, "test-runner")
    candidate_ids = {entry["sample_id"] for entry in result["candidates"]}
    cleared_ids = {entry["sample_id"] for entry in result["cleared_suspicions"]}
    checks_not_run_ids = {entry["sample_id"] for entry in result["checks_not_run"]}
    if candidate_ids != {"A-01"} or cleared_ids != {"B-02"} or checks_not_run_ids != {"C-03", "D-04"}:
        print(json.dumps(result, indent=2), file=sys.stderr)
        raise AssertionError("runner did not separate UI recovery, guarded safety copy, manual prose review, and language abstention")
    by_check = {entry["sample_id"]: entry["check"] for entry in result["checks_not_run"]}
    if by_check["D-04"] != "English-specific sentence surface analysis":
        raise AssertionError("runner did not record unsupported-language abstention")
    if result["authorship_assessment"] != "not_performed":
        raise AssertionError("runner performed an authorship assessment")
    if len(result["candidates"][0]["signals"]) < 2:
        raise AssertionError("candidate lacks a compound signal")
    if result["candidates"][0]["finding_eligible"] is not False:
        raise AssertionError("blind runner promoted a measurement-only candidate")
    if result["schema_version"] != "1.1":
        raise AssertionError("blind runner returned an outdated schema")
    print("PASS: deterministic blind runner separates UI defects, guarded copy, manual prose checks, and language abstention")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
