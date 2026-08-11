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

        continuity = ROOT / "evals" / "continuity"
        continuity_dashboard = temp / "continuity-dashboard.html"
        continuity_markdown = temp / "continuity-audit.md"
        run(
            "scripts/render_dashboard.py",
            str(continuity / "revision.json"),
            str(continuity / "context.json"),
            str(continuity / "decisions.json"),
            str(continuity_dashboard),
            contains="rendered 22 registry items",
        )
        run(
            "scripts/render_markdown.py",
            str(continuity / "revision.json"),
            str(continuity / "context.json"),
            str(continuity / "decisions.json"),
            str(continuity_markdown),
            contains="rendered 22 registry items",
        )
        run(
            validator,
            str(continuity / "revision.json"),
            "--baseline",
            str(continuity / "baseline.json"),
            "--decisions",
            str(continuity / "decisions.json"),
            "--dashboard",
            str(continuity_dashboard),
            "--markdown",
            str(continuity_markdown),
            contains="baseline continuity",
        )

        # Regression: rendered dashboards must contain long unbreakable strings
        # (hashes, URLs, identity keys) inside their own cells. The stylesheet
        # must ship the containment contract; without it grid children default
        # to min-width:auto and captions paint over their neighbors.
        dashboard_text = continuity_dashboard.read_text(encoding="utf-8")
        for fragment in ("overflow-wrap:anywhere", "min-width:0"):
            if fragment not in dashboard_text:
                print(f"FAIL: dashboard stylesheet lost the text-containment rule {fragment!r}")
                return 1

        from report_contract import score_row_label

        # Regression: a canonical category key names the public slop category first,
        # so a reader can map a score back to the eight public categories.
        if score_row_label("backend_shape") != "Structure slop \u00b7 Implementation shape":
            print("FAIL: canonical category key must name its public slop category")
            return 1
        if not score_row_label("copy").startswith("Editorial slop"):
            print("FAIL: copy must present as Editorial slop")
            return 1
        # Regression: when the score label adds no words beyond the public
        # category, the row must not repeat itself ("Accessibility slop ·
        # Accessibility" reads as a rendering mistake).
        if score_row_label("accessibility") != "Accessibility slop":
            print("FAIL: redundant score label must collapse to the public category")
            return 1

        # Guard: an unrecognized key degrades to the raw key rather than inventing a label.
        if score_row_label("not_a_category") != "not_a_category":
            print("FAIL: unknown category key must fall back to the raw key")
            return 1
        if "slop" in score_row_label("not_a_category"):
            print("FAIL: unknown category key must not be given a slop label")
            return 1

        # Guard: legacy schema-2.0 contexts store display strings, not keys. They must
        # pass through unchanged so existing registries keep rendering.
        legacy = continuity_markdown.read_text(encoding="utf-8")
        for legacy_label in ("Implementation shape", "Runtime performance"):
            if legacy_label not in legacy:
                print(f"FAIL: legacy score label {legacy_label!r} no longer renders")
                return 1
        if score_row_label("Implementation shape") != "Implementation shape":
            print("FAIL: legacy display string must pass through unchanged")
            return 1

    print("PASS: continuity failures are caught, decisions survive migration, complete reports validate, and score rows name canonical categories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
