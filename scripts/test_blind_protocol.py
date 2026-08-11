#!/usr/bin/env python3
"""Regression tests for blind manifest, freeze, mutation, and contamination checks."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "blind_protocol.py"


def run(arguments: list[str], expected: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != expected:
        raise AssertionError(
            f"command returned {result.returncode}, expected {expected}: {result.stdout}{result.stderr}"
        )
    return result


def discovery(path: Path, text: str = "Quoted evidence from the allowed packet.") -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "phase": "blind_discovery",
                "authorship_assessment": "not_performed",
                "candidates": [{"candidate_id": "CAND-001", "evidence": text}],
                "strengths": [],
                "cleared_suspicions": [],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="anti-slop-blind-test-") as temporary:
        root = Path(temporary)
        packet = root / "packet.txt"
        prompt = root / "prompt.txt"
        forbidden = root / "prior-report.html"
        manifest = root / "blind-manifest.json"
        result = root / "blind-discovery.json"
        frozen = root / "blind-freeze.json"
        packet.write_text("A novel audit packet.", encoding="utf-8")
        prompt.write_text("Audit only the supplied packet.", encoding="utf-8")
        forbidden.write_text("Expected finding list.", encoding="utf-8")
        discovery(result)

        run(
            [
                "prepare", "--target", "synthetic-packet", "--agent", "test-agent",
                "--prompt-file", str(prompt), "--skill-root", str(ROOT),
                "--allow", str(packet), "--forbid", str(forbidden), "--output", str(manifest),
            ]
        )
        run(["freeze", "--manifest", str(manifest), "--discovery", str(result), "--output", str(frozen)])
        run(["verify", "--manifest", str(manifest), "--freeze", str(frozen)])

        original = result.read_text(encoding="utf-8")
        result.write_text(original + " ", encoding="utf-8")
        run(["verify", "--manifest", str(manifest), "--freeze", str(frozen)], expected=2)
        result.write_text(original, encoding="utf-8")

        contaminated = root / "contaminated.json"
        discovery(contaminated, f"I read {forbidden.name} before deciding.")
        run(
            ["freeze", "--manifest", str(manifest), "--discovery", str(contaminated), "--output", str(root / "bad-freeze.json")],
            expected=2,
        )

        # Innocent-substring guard: a forbidden basename like "keys" must not
        # flag words that merely contain it, but a real mention must still fail.
        keys_dir = root / "keys"
        keys_dir.write_text("expected labels", encoding="utf-8")
        manifest2 = root / "blind-manifest-2.json"
        run(
            [
                "prepare", "--target", "synthetic-packet", "--agent", "test-agent",
                "--prompt-file", str(prompt), "--skill-root", str(ROOT),
                "--allow", str(packet), "--forbid", str(forbidden), "--forbid", str(keys_dir),
                "--output", str(manifest2),
            ]
        )
        benign = root / "benign.json"
        discovery(benign, "The surveyed monkeys and turkeys stayed on the allowed packet.")
        run(["freeze", "--manifest", str(manifest2), "--discovery", str(benign), "--output", str(root / "benign-freeze.json")])
        mention = root / "mention.json"
        discovery(mention, "I opened keys before deciding.")
        run(
            ["freeze", "--manifest", str(manifest2), "--discovery", str(mention), "--output", str(root / "mention-freeze.json")],
            expected=2,
        )

    print("PASS: blind preparation, freeze, verification, mutation rejection, and contamination rejection")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
