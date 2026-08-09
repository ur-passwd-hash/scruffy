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
            "id": "A-01", "mode": "ui", "context": "general",
            "items": [
                {"surface": str(index), "text": "Your change was rejected."}
                for index in range(8)
            ],
        },
        {
            "id": "B-02", "mode": "prose", "context": "safety",
            "text": "Stop the press. Turn the switch off. Keep both hands clear. Tell the floor lead. Wait behind the line. Do not restart the press.",
        },
    ]
    result = run_packet(samples, "test-runner")
    candidate_ids = {entry["sample_id"] for entry in result["candidates"]}
    cleared_ids = {entry["sample_id"] for entry in result["cleared_suspicions"]}
    if candidate_ids != {"A-01"} or cleared_ids != {"B-02"}:
        print(json.dumps(result, indent=2), file=sys.stderr)
        raise AssertionError("runner did not separate the UI recovery defect from guarded safety copy")
    if result["authorship_assessment"] != "not_performed":
        raise AssertionError("runner performed an authorship assessment")
    if len(result["candidates"][0]["signals"]) < 2:
        raise AssertionError("candidate lacks a compound signal")
    print("PASS: deterministic blind runner separates compound UI defects from guarded safety copy")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
