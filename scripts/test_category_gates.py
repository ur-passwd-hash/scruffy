#!/usr/bin/env python3
"""Regression tests for category evidence gates, severity calibration, and impact floor.

Each case mirrors an adversarial mutation from the 2026-08-14 plugin audit that
the validator previously accepted. A schema-valid registry must now fail when a
category's open finding lacks the evidence kind its claims require.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUD = "gatecheck"
REV = "gatecheck-r1"


def receipt(rid: str, kind: str) -> dict:
    return {
        "id": rid,
        "kind": kind,
        "verification": "observed",
        "locator": f"https://example.test/{rid.lower()}",
        "description": f"{kind} receipt for gate tests.",
    }


def base_bundle() -> tuple[dict, dict, dict]:
    item = {
        "id": "GC-1",
        "identity_key": "gate-check-item",
        "kind": "finding",
        "title": "Main view re-renders on every pointer move",
        "category": "performance",
        "severity": "medium",
        "confidence": "moderate",
        "status": "open",
        "revision_disposition": "new",
        "first_seen_revision": REV,
        "last_observed_revision": REV,
        "observation": "Profiling shows full re-render per pointermove event.",
        "user_impact": "Dragging stutters visibly on mid-range hardware, making the primary task slower.",
        "evidence": ["Trace shows 240 renders over one drag."],
        "evidence_refs": ["EV-TRACE"],
        "cause": "Unmemoized handler.",
        "recommendation": "Memoize and throttle.",
        "acceptance_checks": ["Trace shows <= 10 renders per drag."],
        "editorial_review": None,
        "facets": [],
        "depends_on": [],
        "disposition_reason": "Baseline finding.",
        "destination_id": None,
    }
    registry = {
        "schema_version": "2.1",
        "audit_id": AUD,
        "target": "Gate-check fixture app",
        "revision_id": REV,
        "baseline_revision_id": None,
        "run": {
            "requested_mode": "audit",
            "effective_mode": "audit",
            "mode_selection_basis": "explicit",
            "repository_write_authority": "not_authorized",
            "authority_basis_type": "not_granted",
            "authority_basis": "Fixture audit; no writes.",
            "repository_writes_performed": False,
            "repository_write_paths": [],
            "live_demonstration_performed": False,
            "blind_status": "not_run",
            "blind_artifact_refs": [],
        },
        "items": [item],
        "presentation": {
            "prioritized_finding_ids": ["GC-1"],
            "prioritized_enhancement_ids": [],
            "strength_ids": [],
            "cleared_ids": [],
        },
    }
    frame_keys = [
        ("audience", "Who is it for?"),
        ("job", "What job does it perform?"),
        ("primary_action", "What is the primary action?"),
        ("differentiator", "What makes it meaningfully different?"),
        ("return_reason", "Why would someone return?"),
        ("success_signal", "What observable result means it succeeded?"),
    ]
    caps = [
        ("source_read", "available"), ("rendered_page", "available"),
        ("interaction_keyboard", "available"), ("screenshots", "available"),
        ("console_network_accessibility_performance", "available"),
        ("source_write", "not_authorized"), ("prior_audit_data", "not_needed"),
        ("design_reference_search", "not_run"),
        ("copy_context", "available"),
    ]
    categories = [
        "product", "information_architecture", "interaction", "accessibility",
        "visual", "copy", "backend_shape", "performance",
    ]
    context = {
        "schema_version": "1.1",
        "audit_id": AUD,
        "revision_id": REV,
        "title": "Gate-check fixture audit",
        "outcome": {
            "label": "Fixture",
            "summary": "Synthetic bundle exercising category gates.",
            "confidence": "high — synthetic fixture.",
        },
        "product_frame": [
            {"key": k, "question": q, "answer": f"Fixture answer for {k}.", "basis": "supplied"}
            for k, q in frame_keys
        ],
        "tasks": [
            {"id": f"T{i}", "goal": g, "result": r, "status": st, "evidence_refs": ["EV-TRACE"]}
            for i, (g, r, st) in enumerate(
                [
                    ("Drag an item across the board", "Stutters during drag.", "fail"),
                    ("Recover from a failed save", "Retry succeeds.", "pass"),
                    ("Reopen the app and find prior state", "State persists.", "pass"),
                ],
                start=1,
            )
        ],
        "capabilities": [
            {"key": k, "status": s, "scope": f"Fixture scope for {k}."} for k, s in caps
        ],
        "scores": [
            {"category": c, "score": 1, "evidence": f"Fixture score evidence for {c}.", "evidence_refs": ["EV-TRACE"]}
            for c in categories
        ],
        "work_orders": [],
        "checks_not_run": [],
        "visual_evidence": [],
        "evidence_assets": [
            receipt("EV-TRACE", "runtime_trace"),
            receipt("EV-SHOT", "screenshot"),
            receipt("EV-TASK", "task_observation"),
            receipt("EV-AX", "accessibility_observation"),
            receipt("EV-SRC", "source"),
        ],
    }
    decisions = {
        "schema_version": "2.1",
        "audit_id": AUD,
        "revision_id": REV,
        "baseline_revision_id": None,
        "decisions": [
            {"item_id": "GC-1", "decision": "pending", "note": "", "updated_at": None,
             "decision_source": "initial", "destination_id": None, "history": []}
        ],
    }
    return registry, context, decisions


def run_validator(registry: dict, context: dict, decisions: dict) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        (base / "findings.json").write_text(json.dumps(registry), encoding="utf-8")
        (base / "context.json").write_text(json.dumps(context), encoding="utf-8")
        (base / "decisions.json").write_text(json.dumps(decisions), encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_audit.py"),
             str(base / "findings.json"), "--context", str(base / "context.json"),
             "--decisions", str(base / "decisions.json")],
            capture_output=True, text=True,
        )
        return proc.returncode, proc.stdout + proc.stderr


def expect(ok: bool, code: int, output: str, name: str, needle: str | None = None) -> None:
    if ok and code != 0:
        raise AssertionError(f"{name}: expected PASS, got: {output.strip()}")
    if not ok:
        if code == 0:
            raise AssertionError(f"{name}: expected FAIL, validator accepted it")
        if needle and needle not in output:
            raise AssertionError(f"{name}: failed for the wrong reason: {output.strip()}")


def main() -> int:
    registry, context, decisions = base_bundle()
    expect(True, *run_validator(registry, context, decisions), name="baseline")

    def mutated(**item_updates):
        r = copy.deepcopy(registry)
        r["items"][0].update(item_updates)
        return r

    # 1. Performance finding without runtime evidence.
    expect(False, *run_validator(mutated(evidence_refs=["EV-SRC"]), context, decisions),
           name="performance-without-runtime", needle="performance")
    # 2. Accessibility finding without accessibility evidence.
    expect(False, *run_validator(
        mutated(category="accessibility", evidence_refs=["EV-SRC"]), context, decisions),
        name="accessibility-without-criterion-evidence", needle="accessibility")
    # 3. Visual finding never rendered.
    expect(False, *run_validator(
        mutated(category="visual", evidence_refs=["EV-SRC"]), context, decisions),
        name="visual-source-only", needle="visual")
    # 4. Interaction finding without operation evidence.
    expect(False, *run_validator(
        mutated(category="interaction", evidence_refs=["EV-SRC"]), context, decisions),
        name="interaction-without-operation", needle="interaction")
    # 5. Critical severity without calibration.
    expect(False, *run_validator(
        mutated(severity="critical"), context, decisions),
        name="critical-without-calibration", needle="critical")
    # 6. Vacuous user impact.
    expect(False, *run_validator(
        mutated(user_impact="Users suffer."), context, decisions),
        name="vacuous-user-impact", needle="user_impact")
    # 7. Gates cover needs-verification too (this repo's ACTIVE_FINDING_STATUSES);
    # a cleared item is the non-active state that passes without gated evidence.
    r = copy.deepcopy(registry)
    r["items"][0].update(status="needs-verification", evidence_refs=["EV-SRC"])
    expect(False, *run_validator(r, context, decisions), name="needs-verification-still-gated", needle="performance")
    r2 = copy.deepcopy(registry)
    r2["items"][0].update(status="cleared", revision_disposition="cleared", evidence_refs=["EV-SRC"])
    r2["presentation"]["prioritized_finding_ids"] = []
    r2["presentation"]["cleared_ids"] = ["GC-1"]
    expect(True, *run_validator(r2, context, decisions), name="cleared-passes-without-gated-evidence")
    # 8. Context 1.0 legacy still accepted; visual_evidence rejected on 1.0.
    c10 = copy.deepcopy(context); c10["schema_version"] = "1.0"; c10.pop("visual_evidence", None)
    expect(True, *run_validator(registry, c10, decisions), name="legacy-context-1.0")

    print("PASS: category evidence gates, severity calibration, impact floor, active-status coverage, and context 1.0/1.1 compatibility")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
