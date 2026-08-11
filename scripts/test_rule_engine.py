#!/usr/bin/env python3
"""Regression tests for the deterministic rule engine and its packs."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

from rule_engine import PackError, evaluate_page, load_packs, validate_packs

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "evals" / "web-fixtures"
PLANTED_STATIC = {"WF-A-03", "WF-B-01", "WF-B-03", "WF-C-01"}
OPERATION_ONLY = {"WF-A-01", "WF-C-03"}
GUARDS = {"WF-A-02", "WF-A-04", "WF-B-02", "WF-B-04", "WF-C-02", "WF-C-04"}


def expect_pack_error(packs: list[dict], contains: str) -> None:
    try:
        validate_packs(packs)
    except PackError as error:
        if contains not in str(error):
            raise AssertionError(f"expected {contains!r} in {error!r}") from error
        return
    raise AssertionError(f"expected PackError containing {contains!r}")


def main() -> int:
    packs = load_packs(ROOT / "schema" / "rules", [])
    validate_packs(packs)

    # Pack validation regressions.
    bad = copy.deepcopy(packs)
    bad[0]["rules"][0]["category"] = "vibes"
    expect_pack_error(bad, "canonical")
    bad = copy.deepcopy(packs)
    bad[0]["rules"][0]["severity"] = "catastrophic"
    expect_pack_error(bad, "severity")
    bad = copy.deepcopy(packs)
    bad[1]["rules"][0]["id"] = bad[0]["rules"][0]["id"]
    expect_pack_error(bad, "appears in both")
    bad = copy.deepcopy(packs)
    bad[0]["rules"][0]["citation"] = "principles/PRINCIPLES.md §99"
    expect_pack_error(bad, "does not exist")
    bad = copy.deepcopy(packs)
    bad[0]["rules"][0]["citation"] = "https://example.com/blog"
    expect_pack_error(bad, "citation must look like")
    bad = copy.deepcopy(packs)
    bad[0]["rules"][0]["false_positive_guard"] = ""
    expect_pack_error(bad, "false_positive_guard")
    bad = copy.deepcopy(packs)
    bad[0]["rules"][0]["predicate"] = {"type": "vibe_check"}
    expect_pack_error(bad, "predicate.type")
    bad = copy.deepcopy(packs)
    bad[0]["origin"] = "user"
    bad[0]["source_attribution"] = None
    expect_pack_error(bad, "attribute their source")

    # Fixture behavior: static leads hit planted defects and never hit guards.
    leads: list[dict] = []
    for page in ("checkout-flow.html", "pricing-page.html", "settings-form.html"):
        leads.extend(evaluate_page(FIXTURES / page, packs))
    hints = {lead["sample_hint"] for lead in leads}
    missing = PLANTED_STATIC - hints
    if missing:
        raise AssertionError(f"engine lost coverage of planted defects: {sorted(missing)}")
    wrongly_hit = hints & GUARDS
    if wrongly_hit:
        raise AssertionError(f"engine false-positived on guards: {sorted(wrongly_hit)}")
    leaked = hints & OPERATION_ONLY
    if leaked:
        raise AssertionError(
            f"engine claims static detection of operation-only defects: {sorted(leaked)}; "
            "if a new rule genuinely detects them statically, move the sample out of OPERATION_ONLY"
        )
    for lead in leads:
        if lead["confirmation_required"] is not True:
            raise AssertionError(f"lead {lead['rule_id']} must require confirmation")
        if not lead["citation"] or not lead["false_positive_guard"]:
            raise AssertionError(f"lead {lead['rule_id']} must carry citation and guard")

    # Severity filtering mirrors the engine CLI.
    errors_only = [lead for lead in leads if lead["severity"] == "error"]
    if not errors_only or {lead["rule_id"] for lead in errors_only} != {"OP-UNLABELED-INPUT"}:
        raise AssertionError("error-level leads on the fixtures must be exactly OP-UNLABELED-INPUT")

    with tempfile.TemporaryDirectory(prefix="scruffy-rules-") as directory:
        base = Path(directory)

        # Synthetic guards for element predicates.
        page = base / "synthetic.html"
        page.write_text(
            "<html><body>"
            '<a href="#">dead</a><a href="#real">fine</a><p id="real">target</p>'
            '<label>Wrapped <input type="text"></label>'
            '<input type="text" placeholder="bare">'
            '<div onclick="go()">fake button</div>'
            '<div role="button" tabindex="0" onclick="go()">exempted</div>'
            "</body></html>",
            encoding="utf-8",
        )
        synthetic = evaluate_page(page, packs)
        fired = sorted(lead["rule_id"] for lead in synthetic)
        if fired.count("OP-DEAD-HREF") != 1:
            raise AssertionError(f"bare-# anchor must fire exactly once, got {fired}")
        if fired.count("OP-UNLABELED-INPUT") != 1:
            raise AssertionError("only the unwrapped input may fire")
        if fired.count("OP-DIV-BUTTON") != 1:
            raise AssertionError("role/tabindex div must be exempt; bare onclick div must fire")

        # New predicate types: one synthetic page exercises each.
        residue = base / "residue.html"
        residue.write_text(
            "<html><head><title>Vite + React</title>"
            '<script src="app.js"></script></head><body>'
            '<img src="x.jpg"><img src="y.jpg" width="10" height="10" alt="named">'
            '<button></button><button aria-label="close"></button>'
            '<p id="dup">a</p><p id="dup">b</p>'
            '<a href="/x" tabindex="3">order</a>'
            "<p>Please note that you must simply click continue in order to proceed.</p>"
            "<script>try{go()}catch(e){}</script>"
            "</body></html>",
            encoding="utf-8",
        )
        residue_leads = sorted(l["rule_id"] for l in evaluate_page(residue, packs))
        for expected in ("GEN-DEFAULT-TITLE", "PERF-BLOCKING-SCRIPT", "PERF-IMG-NO-DIMENSIONS",
                         "A11Y-IMG-NO-ALT", "A11Y-EMPTY-CONTROL", "A11Y-DUPLICATE-ID",
                         "A11Y-POSITIVE-TABINDEX", "A11Y-HTML-NO-LANG", "PERF-NO-VIEWPORT",
                         "PL-PLEASE-NOTE", "PL-SIMPLY-JUST", "PL-IN-ORDER-TO", "GEN-SILENT-CATCH"):
            if expected not in residue_leads:
                raise AssertionError(f"{expected} did not fire on the synthetic residue page: {residue_leads}")
        if residue_leads.count("A11Y-IMG-NO-ALT") != 1 or residue_leads.count("A11Y-EMPTY-CONTROL") != 1:
            raise AssertionError("guarded twins must stay silent (named image, aria-label button)")
        for fixture_lead in leads:
            if fixture_lead["pack"] not in {"baseline-interaction", "baseline-editorial"}:
                raise AssertionError(f"new packs false-positived on fixtures: {fixture_lead['rule_id']}")

        # Operated checks queue for the walkthrough and never fire statically.
        operated_ids = {r["id"] for pk in packs for r in pk["rules"] if r["predicate"]["type"] == "operated_check"}
        if not operated_ids:
            raise AssertionError("baseline-operated pack missing")
        for page_name in ("checkout-flow.html", "pricing-page.html", "settings-form.html"):
            for lead in evaluate_page(FIXTURES / page_name, packs):
                if lead["rule_id"] in operated_ids:
                    raise AssertionError(f"operated check {lead['rule_id']} fired statically")

        # User packs load, attribute, and fire.
        user_pack = {
            "schema_version": "1.0",
            "pack": "user-demo",
            "origin": "user",
            "description": "Distilled from a supplied transcript.",
            "source_attribution": {
                "title": "Example design talk",
                "creator": "Example Creator",
                "locator": "transcript supplied 2026-08-10",
            },
            "rules": [
                {
                    "id": "USER-SYNERGY",
                    "category": "copy",
                    "severity": "suggestion",
                    "message": "Synergy filler.",
                    "citation": "principles/PRINCIPLES.md §21",
                    "false_positive_guard": "Legitimate in direct quotation; confirm before reporting.",
                    "predicate": {"type": "text_pattern", "pattern": "synergize"},
                }
            ],
        }
        pack_path = base / "user-demo.json"
        pack_path.write_text(json.dumps(user_pack), encoding="utf-8")
        user_page = base / "copy.html"
        user_page.write_text("<html><body><p>We synergize your workflows.</p></body></html>", encoding="utf-8")
        combined = load_packs(ROOT / "schema" / "rules", [pack_path])
        validate_packs(combined)
        user_leads = [lead for lead in evaluate_page(user_page, combined) if lead["rule_id"] == "USER-SYNERGY"]
        if len(user_leads) != 1 or user_leads[0]["pack_origin"] != "user":
            raise AssertionError("user pack rule must fire once and record its origin")

    print(
        "PASS: rule packs validate with citations and guards, fixture leads hit planted defects only, "
        "operation-only defects stay unclaimed, and user packs load with attribution"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (AssertionError, ValueError, OSError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
