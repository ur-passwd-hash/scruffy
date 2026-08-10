#!/usr/bin/env python3
"""Run the deterministic sentence analyzer over an unlabeled blind packet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from analyze_sentence_slop import analyze


CONSEQUENCES = {
    "detail_sparsity": "The copy does not provide enough concrete product, actor, condition, or outcome detail to support a decision.",
    "formulaic_scaffolds": "Rhetorical structure occupies space that should identify the product or actionable outcome.",
    "rhetorical_question_density": "Repeated questions create momentum without resolving the user's decision.",
    "missing_recovery_information": "The error state does not explain the cause, retained state, or a useful next action.",
    "passive_candidates": "The affected user may not know what acted, what changed, or who can resolve it.",
    "repeated_openings": "Repeated frames flatten distinctions between claims or states.",
    "cadence_uniformity": "Uniform cadence may flatten an intended editorial voice.",
    "short_sentence_burst": "Repeated punchline-length units may replace development with a promotional beat.",
    "transition_concentration": "Discourse markers may conceal a weak information hierarchy.",
    "paragraph_pattern_reuse": "Different ideas may be forced through the same rhetorical paragraph choreography.",
    "phrase_repetition": "Repeated phrasing can make distinct claims or actions harder to distinguish.",
}


def load_packet(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("samples"), list):
        raise ValueError("packet JSON must contain a samples list")
    samples: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, sample in enumerate(data["samples"]):
        if not isinstance(sample, dict) or not isinstance(sample.get("id"), str):
            raise ValueError(f"samples[{index}] needs an id")
        if sample["id"] in seen:
            raise ValueError(f"duplicate sample id: {sample['id']}")
        if not isinstance(sample.get("text"), str) and not isinstance(sample.get("items"), list):
            raise ValueError(f"sample {sample['id']} needs text or items")
        seen.add(sample["id"])
        samples.append(sample)
    return samples


def evidence_for(leads: list[dict[str, Any]]) -> list[str]:
    evidence: list[str] = []
    for lead in leads:
        for example in lead.get("examples", [])[:2]:
            rendered = example if isinstance(example, str) else json.dumps(example, ensure_ascii=False)
            evidence.append(f"{lead['code']}: {rendered}"[:360])
    return evidence[:8] or ["Length-gated analyzer produced multiple independent review leads."]


def run_packet(samples: list[dict[str, Any]], agent: str) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    cleared: list[dict[str, Any]] = []
    checks_not_run: list[dict[str, str]] = []
    for sample in samples:
        items = sample.get("items", [])
        text = sample.get("text") or "\n".join(item["text"] if isinstance(item, dict) else str(item) for item in items)
        result = analyze(
            text,
            mode=sample.get("mode", "auto"),
            context=sample.get("context", "general"),
            language=sample.get("language", "unknown"),
            items=items,
        )
        codes = [lead["code"] for lead in result["leads"]]
        if result["language_analysis_status"] == "abstained":
            checks_not_run.append(
                {
                    "sample_id": sample["id"],
                    "check": "English-specific sentence surface analysis",
                    "reason": "Language was non-English or unknown; use a language-competent reviewer instead of English regexes.",
                }
            )
            continue
        if result["compound_signal"]["review_needed"]:
            consequences = [CONSEQUENCES[code] for code in codes if code in CONSEQUENCES]
            candidates.append(
                {
                    "candidate_id": f"CAND-{len(candidates) + 1:03d}",
                    "sample_id": sample["id"],
                    "category": "error_recovery_copy" if "missing_recovery_information" in codes else "sentence_copy",
                    "signals": codes,
                    "signal_families": result["compound_signal"]["independent_signal_families"],
                    "evidence": evidence_for(result["leads"]),
                    "consequence": " ".join(dict.fromkeys(consequences)) or "Multiple signals require product-context review.",
                    "counterexample_tested": (
                        "Checked supplied genre/context guards and whether repetition was required terminology, teaching, safety, or recovery language; none cleared the compound signal."
                    ),
                    "confidence": (
                        "moderate"
                        if result["sample"]["adequacy"] == "limited" or result["manual_review"]["required"]
                        else "high"
                    ),
                    "finding_eligible": False,
                    "manual_checks_status": "not_run" if result["manual_review"]["required"] else "not_needed",
                }
            )
            if result["manual_review"]["required"]:
                checks_not_run.append(
                    {
                        "sample_id": sample["id"],
                        "check": "manual sentence passage review",
                        "reason": "Conceptual coherence, sentence portability, discourse purpose, and voice fit require product-aware human review.",
                    }
                )
        else:
            if result["manual_review"]["required"]:
                checks_not_run.append(
                    {
                        "sample_id": sample["id"],
                        "check": "manual sentence passage review",
                        "reason": "Automated surface measurements did not escalate, but they cannot clear conceptual coherence, portability, discourse purpose, or voice fit.",
                    }
                )
                continue
            if result["guards"]["protected_context_applied"]:
                reason = "Supplied genre/language context makes regularity or passive construction functional; no unguarded compound signal remains."
            elif result["sample"]["adequacy"] == "insufficient":
                reason = "The sample is insufficient for prose statistics and does not contain two independent UI-copy signals."
            elif len(codes) < 2:
                reason = "Fewer than two independent signals survived the sample and context guards."
            else:
                reason = "Signals were present, but the supplied context guard prevents automatic escalation."
            cleared.append(
                {
                    "sample_id": sample["id"],
                    "suspicion": ", ".join(codes) if codes else "sentence slop",
                    "reason_cleared": reason,
                    "confidence": "high" if result["guards"]["protected_context_applied"] else "moderate",
                }
            )
    return {
        "schema_version": "1.1",
        "phase": "blind_discovery",
        "agent": agent,
        "skill_invoked": "scruffy",
        "authorship_assessment": "not_performed",
        "capabilities": [
            {"capability": "unlabeled text packet", "status": "available"},
            {"capability": "deterministic sentence analyzer", "status": "available"},
            {"capability": "rendered product context", "status": "unavailable"},
        ],
        "candidates": candidates,
        "cleared_suspicions": cleared,
        "checks_not_run": checks_not_run,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--agent", default="deterministic-sentence-analyzer")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        output = run_packet(load_packet(args.packet), args.agent)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2
    rendered = json.dumps(output, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
