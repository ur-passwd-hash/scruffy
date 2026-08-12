#!/usr/bin/env python3
"""Tests for Scruffy's Mop bundle ingestion, gating, planning, and handoff.

Dependency-free. Run directly: ``python3 scripts/test_mop.py``.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from mop_bundle import (
    InteropError,
    approved_item_ids,
    build_plan,
    gate_state,
    load_bundle,
    load_interop,
)
from mop_handoff import build_handoff

REPO = Path(__file__).resolve().parent.parent
FIXTURE = REPO / "fixtures" / "sample-audit"
INTEROP = load_interop()


def _bundle():
    return load_bundle(FIXTURE, INTEROP)


def test_load_and_validate_fixture():
    b = _bundle()
    assert b["findings"]["audit_id"] == "acme-billing"
    assert b["tokens"] is not None, "optional tokens.json should load when present"


def test_reject_unknown_major_schema():
    b = _bundle()
    b = copy.deepcopy(b)
    b["findings"]["schema_version"] = "3.0"
    try:
        from mop_bundle import validate_versions
        validate_versions(b, INTEROP)
    except InteropError as exc:
        assert "major" in str(exc)
        return
    raise AssertionError("unknown major schema must fail closed")


def test_reject_unknown_minor_schema():
    from mop_bundle import validate_versions
    b = copy.deepcopy(_bundle())
    b["context"]["schema_version"] = "1.9"
    try:
        validate_versions(b, INTEROP)
    except InteropError:
        return
    raise AssertionError("unrecognized minor schema must fail closed")


def test_legacy_schema_is_readable_with_note():
    from mop_bundle import validate_versions
    b = copy.deepcopy(_bundle())
    b["findings"]["schema_version"] = "2.0"  # legacy, readable
    notes = validate_versions(b, INTEROP)
    assert any("legacy" in n for n in notes), "legacy schema should produce a note"


def test_missing_required_artifact_fails():
    try:
        load_bundle({"findings.json": FIXTURE / "findings.json",
                     "context.json": FIXTURE / "context.json"}, INTEROP)
    except InteropError as exc:
        assert "decisions.json" in str(exc)
        return
    raise AssertionError("missing decisions.json must fail")


def test_approved_selection_excludes_defer_and_reject():
    approved = approved_item_ids(_bundle())
    assert approved == {"AS-04", "AS-02", "AS-05", "AS-01"}, approved
    assert "AS-03" not in approved  # deferred
    assert "AS-06" not in approved  # rejected


def test_plan_order_respects_depends_on_and_lanes():
    plan = build_plan(_bundle(), INTEROP)
    order = [s["item_id"] for s in plan["steps"]]
    assert order == ["AS-04", "AS-02", "AS-05", "AS-01"], order
    # AS-04 (structural blocker) precedes its dependents.
    assert order.index("AS-04") < order.index("AS-02")
    assert order.index("AS-04") < order.index("AS-05")


def test_enhancement_included_when_approved():
    b = copy.deepcopy(_bundle())
    for d in b["decisions"]["decisions"]:
        if d["item_id"] == "AS-06":
            d["decision"] = "approve"
    plan = build_plan(b, INTEROP)
    assert "AS-06" in [s["item_id"] for s in plan["steps"]]


def test_explicit_work_orders_are_honored():
    b = copy.deepcopy(_bundle())
    b["context"]["work_orders"] = [
        {"id": "WO-2", "lane": 3, "item_ids": ["AS-05", "AS-02"]},
        {"id": "WO-1", "lane": 1, "item_ids": ["AS-04"]},
        {"id": "WO-5", "lane": 5, "item_ids": ["AS-01"]},
    ]
    plan = build_plan(b, INTEROP)
    assert plan["ordering_basis"] == "explicit_work_orders"
    order = [s["item_id"] for s in plan["steps"]]
    # Lane 1 order before lane 3 before lane 5; within WO-2 the given order holds.
    assert order == ["AS-04", "AS-05", "AS-02", "AS-01"], order


def test_dependency_on_nonapproved_is_flagged_not_dropped():
    b = copy.deepcopy(_bundle())
    # Make AS-01 depend on the deferred AS-03.
    for it in b["findings"]["items"]:
        if it["id"] == "AS-01":
            it["depends_on"] = ["AS-03"]
    plan = build_plan(b, INTEROP)
    assert any("AS-03" in w for w in plan["warnings"]), plan["warnings"]


def test_cycle_is_rejected():
    b = copy.deepcopy(_bundle())
    ids = {"AS-04": "AS-02", "AS-02": "AS-04"}
    for it in b["findings"]["items"]:
        if it["id"] in ids:
            it["depends_on"] = [ids[it["id"]]]
    try:
        build_plan(b, INTEROP)
    except InteropError as exc:
        assert "cycle" in str(exc)
        return
    raise AssertionError("a depends_on cycle must be rejected")


def test_approved_but_terminal_item_is_skipped():
    b = copy.deepcopy(_bundle())
    # Approve AS-03 but mark it already fixed: it must be skipped, with a warning.
    for it in b["findings"]["items"]:
        if it["id"] == "AS-03":
            it["status"] = "fixed"
    for d in b["decisions"]["decisions"]:
        if d["item_id"] == "AS-03":
            d["decision"] = "approve"
    plan = build_plan(b, INTEROP)
    ids = [s["item_id"] for s in plan["steps"]]
    assert "AS-03" not in ids, ids
    assert any("AS-03" in w and "already fixed" in w for w in plan["warnings"]), plan["warnings"]


def test_gate_fails_closed_without_authority():
    b = copy.deepcopy(_bundle())
    b["findings"]["run"]["repository_write_authority"] = "not_authorized"
    gate = gate_state(b, INTEROP)
    assert not gate["permissible"]
    # Explicit user grant re-opens it.
    assert gate_state(b, INTEROP, authorized_override=True)["permissible"]


def test_gate_fails_closed_wrong_mode():
    b = copy.deepcopy(_bundle())
    b["findings"]["run"]["effective_mode"] = "audit"
    gate = gate_state(b, INTEROP)
    assert not gate["permissible"]
    assert any("effective_mode" in r for r in gate["reasons"])


def test_tokens_attach_to_their_item():
    plan = build_plan(_bundle(), INTEROP)
    step = next(s for s in plan["steps"] if s["item_id"] == "AS-02")
    assert step["tokens"] and step["tokens"][0]["name"] == "color.status.pastdue.text"


def test_handoff_never_marks_fixed():
    plan = build_plan(_bundle(), INTEROP)
    work = {
        "AS-04": {"surfaces": ["src/billing/state.ts"],
                  "self_check": [{"check": c, "result": "meets"}
                                 for c in plan["steps"][0]["acceptance_checks"]]},
    }
    handoff = build_handoff(plan, work)
    for it in handoff["items"]:
        assert it["status"] == "implemented-pending-reaudit"
        assert it["status"] not in ("fixed", "cleared")
        assert it["cleared_by"] == "pending Scruffy re-audit"
    assert "AS-02" in handoff["unimplemented"]


def test_handoff_discloses_augmentations():
    plan = build_plan(_bundle(), INTEROP)
    # Default: nothing reported, all three keys present (incl. browser).
    default = build_handoff(plan, {})
    assert default["augmentations"] == {
        "impeccable": "not_reported", "design_reference_search": "not_reported",
        "browser": "not_reported"}
    # Explicit disclosure survives, including a ':detail' suffix.
    h = build_handoff(plan, {}, {"impeccable": "used",
                                 "design_reference_search": "used:mobbin",
                                 "browser": "used"})
    assert h["augmentations"]["design_reference_search"] == "used:mobbin"
    assert h["augmentations"]["browser"] == "used"


def test_handoff_rejects_unknown_augmentation():
    from mop_handoff import _normalize_augmentations
    for bad in ({"nope": "used"}, {"impeccable": "maybe"}):
        try:
            _normalize_augmentations(bad)
        except InteropError:
            continue
        raise AssertionError(f"expected rejection for {bad}")


def test_handoff_rejects_bad_self_check_result():
    plan = build_plan(_bundle(), INTEROP)
    work = {"AS-04": {"surfaces": [], "self_check": [{"check": "x", "result": "done"}]}}
    try:
        build_handoff(plan, work)
    except InteropError:
        return
    raise AssertionError("invalid self_check result must be rejected")


def test_preflight_browser_probe_returns_status():
    from mop_preflight import probe_browser
    r = probe_browser()
    assert r["status"] in ("available", "absent")
    assert "checked" in r and isinstance(r["checked"], list)


def test_preflight_absent_requires_reason():
    from mop_preflight import build_preflight, PreflightError
    # 'absent' without a reason is refused; with a reason it is accepted.
    try:
        build_preflight({"design_reference_search": {"status": "absent"}},
                        browser={"status": "absent", "reason": "test"})
    except PreflightError:
        pass
    else:
        raise AssertionError("absent without reason must be refused")
    ok = build_preflight(
        {"design_reference_search": {"status": "absent", "reason": "MCP call failed"}},
        browser={"status": "absent", "reason": "test"})
    assert ok["augmentations"]["design_reference_search"]["status"] == "absent"


def test_preflight_omission_is_not_run():
    from mop_preflight import build_preflight
    r = build_preflight({}, browser={"status": "available", "tool": "x"})
    assert r["augmentations"]["impeccable"]["status"] == "not_run"
    assert r["augmentations"]["design_reference_search"]["status"] == "not_run"


def test_preflight_maps_to_handoff_vocabulary():
    from mop_preflight import build_preflight, to_handoff_augmentations
    r = build_preflight({"impeccable": {"status": "available"},
                         "design_reference_search": {"status": "absent", "reason": "x"}},
                        browser={"status": "available", "tool": "Chrome"})
    m = to_handoff_augmentations(r)
    assert m == {"browser": "used", "impeccable": "used",
                 "design_reference_search": "absent"}


def _tiny_png(path):
    import base64
    path.write_bytes(base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="))


def test_dashboard_is_self_contained_and_embeds_images(tmp=None):
    import tempfile
    from mop_dashboard import render
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        _tiny_png(d / "s.png")
        (d / "assets.json").write_text(json.dumps({
            "screenshots": [{"path": "s.png", "caption": "shot", "item_ids": ["AS-02"]}],
            "references": [{"path": "s.png", "app": "Linear", "url": "https://m/x",
                            "for_items": ["AS-05"]}],
            "preflight": {"augmentations": {
                "browser": {"status": "available", "tool": "Chrome"},
                "impeccable": {"status": "available"},
                "design_reference_search": {"status": "absent", "reason": "x"}}},
            "directions": {"AS-02": {"recommended": "do X", "principle": "p"}},
        }))
        out = render(FIXTURE, str(d / "assets.json"), str(d / "dash.html"),
                     authorized=True)
        doc = out.read_text()
    assert 'src="data:image/png;base64,' in doc
    import re
    external = [u for u in re.findall(r'src="([^"]+)"', doc) if not u.startswith("data:")]
    assert not external, external
    assert "Payment-status pill" in doc          # an approved item title
    assert "browser=available" in doc            # augmentation disclosure
    assert "Recommended direction" in doc        # direction overlay rendered
    # Decision surface: controls + export present, decision reflects the bundle.
    assert 'data-item-id="AS-02"' in doc
    assert "Download decisions.json" in doc
    assert 'dec-approve' in doc                   # AS-02 is approved in the fixture


def test_dashboard_shows_all_items_as_a_decision_surface():
    import tempfile
    from mop_dashboard import render
    with tempfile.TemporaryDirectory() as d:
        out = render(FIXTURE, None, str(Path(d) / "dash.html"), authorized=True)
        doc = out.read_text()
    # Every registry item is shown, not just approved ones.
    assert "Arbitrary hero gradient" in doc       # AS-03, deferred
    assert "Offer a dark theme" in doc            # AS-06, rejected enhancement
    # Each carries its current decision, and the loop-closing export exists.
    assert 'dec-defer' in doc and 'dec-reject' in doc and 'dec-approve' in doc
    assert 'id="dlBtn"' in doc and "decisions.json" in doc
    assert 'data-decision=' in doc                # in-browser decision state


def test_dashboard_unknown_mime_fails_closed():
    import tempfile
    from mop_dashboard import render
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "x.bin").write_bytes(b"\x00\x01")
        (d / "a.json").write_text(json.dumps(
            {"screenshots": [{"path": "x.bin", "item_ids": []}]}))
        try:
            render(FIXTURE, str(d / "a.json"), str(d / "o.html"), authorized=True)
        except InteropError:
            return
    raise AssertionError("unknown MIME must fail closed")


def _run():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  ok  {t.__name__}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"FAIL  {t.__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run())
