#!/usr/bin/env python3
"""Exercise the Scruffy revision, decision, and rendering invariants."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run(*arguments: str, succeeds: bool = True, contains: str | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [PYTHON, *arguments],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    output = result.stdout + result.stderr
    if succeeds and result.returncode != 0:
        raise SystemExit(f"FAIL: {' '.join(arguments)}\n{output}")
    if not succeeds and result.returncode == 0:
        raise SystemExit(f"FAIL: expected command to fail: {' '.join(arguments)}")
    if contains and contains not in output:
        raise SystemExit(f"FAIL: expected {contains!r} in output from {' '.join(arguments)}\n{output}")
    return result


def main() -> int:
    fixture = ROOT / "evals" / "durability"
    validator = "scripts/validate_audit.py"

    run(
        validator,
        "evals/durability/revision-valid.json",
        "--baseline",
        "evals/durability/baseline.json",
        contains="baseline continuity",
    )
    run(
        validator,
        "evals/durability/revision-invalid-missing.json",
        "--baseline",
        "evals/durability/baseline.json",
        succeeds=False,
        contains="silently dropped baseline IDs",
    )
    run(
        validator,
        "evals/durability/revision-invalid-reuse.json",
        "--baseline",
        "evals/durability/baseline.json",
        succeeds=False,
        contains="reused for a new identity",
    )

    with tempfile.TemporaryDirectory(prefix="anti-slop-durability-") as directory:
        temp = Path(directory)
        decisions = temp / "decisions.json"
        dashboard = temp / "dashboard.html"
        broken_dashboard = temp / "dashboard-broken.html"
        markdown = temp / "audit.md"
        broken_markdown = temp / "audit-broken.md"

        run(
            "scripts/migrate_decisions.py",
            str(fixture / "decisions-v1.json"),
            str(fixture / "revision-valid.json"),
            str(temp / "unsafe-decisions.json"),
            succeeds=False,
            contains="provide --prior-registry",
        )

        run(
            "scripts/migrate_decisions.py",
            str(fixture / "decisions-v1.json"),
            str(fixture / "revision-valid.json"),
            str(decisions),
            "--prior-registry",
            str(fixture / "baseline.json"),
            contains="migrated 2 prior records",
        )
        migrated = json.loads(decisions.read_text(encoding="utf-8"))
        by_id = {row["item_id"]: row for row in migrated["decisions"]}
        expected = {"AS-01": "approve", "ENH-01": "defer", "AS-02": "pending"}
        actual = {item_id: by_id[item_id]["decision"] for item_id in expected}
        if actual != expected:
            raise SystemExit(f"FAIL: migrated decisions changed: {actual}")

        run(
            "scripts/render_dashboard.py",
            str(fixture / "revision-valid.json"),
            str(fixture / "context.json"),
            str(decisions),
            str(dashboard),
            contains="rendered 4 registry items",
        )
        run(
            "scripts/render_markdown.py",
            str(fixture / "revision-valid.json"),
            str(fixture / "context.json"),
            str(decisions),
            str(markdown),
            contains="rendered 4 registry items",
        )
        run(
            validator,
            str(fixture / "revision-valid.json"),
            "--baseline",
            str(fixture / "baseline.json"),
            "--decisions",
            str(decisions),
            "--baseline-decisions",
            str(fixture / "decisions-v1.json"),
            "--dashboard",
            str(dashboard),
            "--markdown",
            str(markdown),
            contains="dashboard completeness",
        )

        broken = dashboard.read_text(encoding="utf-8").replace('id="checks-not-run"', 'id="checks-removed"', 1)
        broken_dashboard.write_text(broken, encoding="utf-8")
        run(
            validator,
            str(fixture / "revision-valid.json"),
            "--dashboard",
            str(broken_dashboard),
            succeeds=False,
            contains="missing required sections",
        )

        broken = markdown.read_text(encoding="utf-8").replace("<!-- anti-slop-item:AS-02 -->", "", 1)
        broken_markdown.write_text(broken, encoding="utf-8")
        run(
            validator,
            str(fixture / "revision-valid.json"),
            "--markdown",
            str(broken_markdown),
            succeeds=False,
            contains="Markdown report omits registry items",
        )

        mahjong = ROOT / "evals" / "mahjong"
        mahjong_dashboard = temp / "mahjong-dashboard.html"
        mahjong_markdown = temp / "mahjong-audit.md"
        run(
            "scripts/render_dashboard.py",
            str(mahjong / "revision.json"),
            str(mahjong / "context.json"),
            str(mahjong / "decisions.json"),
            str(mahjong_dashboard),
            contains="rendered 22 registry items",
        )
        run(
            "scripts/render_markdown.py",
            str(mahjong / "revision.json"),
            str(mahjong / "context.json"),
            str(mahjong / "decisions.json"),
            str(mahjong_markdown),
            contains="rendered 22 registry items",
        )
        run(
            validator,
            str(mahjong / "revision.json"),
            "--baseline",
            str(mahjong / "baseline.json"),
            "--decisions",
            str(mahjong / "decisions.json"),
            "--dashboard",
            str(mahjong_dashboard),
            "--markdown",
            str(mahjong_markdown),
            contains="baseline continuity",
        )

    print("PASS: continuity failures are caught, decisions survive migration, and complete reports validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
