#!/usr/bin/env python3
"""The scaffolder must emit a bundle that validates without edits."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "scaffold_audit.py"),
             "--audit-id", "scaffold-check", "--target", "Scaffold fixture",
             "--title", "Scaffold self-check", "--out", tmp],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            print(f"FAIL: {proc.stdout}{proc.stderr}", file=sys.stderr)
            return 1
    print("PASS: scaffolded bundle self-validates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
