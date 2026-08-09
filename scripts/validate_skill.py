#!/usr/bin/env python3
"""Validate Scruffy packaging and portability with the standard library."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not match:
        fail("SKILL.md frontmatter is missing")
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        key, separator, value = line.partition(":")
        if not separator:
            fail(f"invalid frontmatter line: {line!r}")
        result[key.strip()] = value.strip()
    return result


def validate_frontmatter(text: str) -> None:
    metadata = parse_frontmatter(text)
    if set(metadata) != {"name", "description"}:
        fail(f"SKILL.md frontmatter keys must be name and description; got {sorted(metadata)}")
    if metadata["name"] != "scruffy":
        fail("SKILL.md name must be scruffy")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", metadata["name"]):
        fail("SKILL.md name is invalid")
    description = metadata["description"]
    if not description or len(description) > 1024:
        fail(f"description length must be 1-1024 characters; got {len(description)}")
    required_trigger_terms = ("audit", "redesign", "web", "URL", "screenshot", "generic")
    missing = [term for term in required_trigger_terms if term.lower() not in description.lower()]
    if missing:
        fail(f"description is missing trigger coverage: {missing}")


def validate_budget(text: str) -> None:
    lines = text.splitlines()
    words = re.findall(r"\b\w+[\w’-]*\b", text)
    if len(lines) >= 500:
        fail(f"SKILL.md has {len(lines)} lines; keep it below 500")
    # A conservative proxy for the Agent Skills recommendation of <5,000 tokens.
    if len(words) >= 4000:
        fail(f"SKILL.md has {len(words)} words; keep it below the 4,000-word proxy")


def validate_links(text: str) -> None:
    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
    local_links = [link.split("#", 1)[0] for link in links if "://" not in link]
    if not local_links:
        fail("SKILL.md must route to local progressive-disclosure references")
    missing = sorted({link for link in local_links if link and not (ROOT / link).exists()})
    if missing:
        fail(f"SKILL.md references missing files: {missing}")
    too_deep = sorted({link for link in local_links if link.count("/") > 1})
    if too_deep:
        fail(f"SKILL.md references must remain one level deep: {too_deep}")


def validate_required_files() -> None:
    required = (
        "agents/openai.yaml",
        "assets/scruffy-hero.png",
        "references/verification.md",
        "references/scoring.md",
        "references/output-schema.md",
        "references/durability.md",
        "references/archetypes.md",
        "references/sentence-slop.md",
        "references/blind-audit.md",
        "principles/PRINCIPLES.md",
        "principles/SOURCES.md",
        "principles/INSPIRATIONS.md",
        "scripts/intake.py",
        "scripts/validate_corpus.py",
        "scripts/validate_audit.py",
        "scripts/migrate_decisions.py",
        "scripts/render_dashboard.py",
        "scripts/render_markdown.py",
        "scripts/test_durability.py",
        "scripts/analyze_sentence_slop.py",
        "scripts/blind_protocol.py",
        "scripts/evaluate_blind_outputs.py",
        "scripts/run_sentence_blind.py",
        "scripts/validate_agent_parity.py",
        "scripts/test_sentence_slop.py",
        "scripts/test_blind_protocol.py",
        "scripts/test_blind_evaluator.py",
        "scripts/test_sentence_blind_runner.py",
        "scripts/annotate.html",
        "evals/triggers.json",
        "evals/archetypes.json",
        "evals/sentence-slop/cases.json",
        "evals/durability/baseline.json",
        "evals/durability/revision-valid.json",
        "evals/durability/revision-invalid-missing.json",
        "evals/durability/revision-invalid-reuse.json",
        "evals/durability/decisions-v1.json",
        "evals/durability/context.json",
        "evals/mahjong/baseline.json",
        "evals/mahjong/revision.json",
        "evals/mahjong/decisions.json",
        "evals/mahjong/context.json",
        ".github/workflows/validate.yml",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        "README.md",
        "LICENSE",
    )
    missing = [path for path in required if not (ROOT / path).is_file()]
    if missing:
        fail(f"required files are missing: {missing}")


def validate_durability_contract(text: str) -> None:
    required_fragments = (
        "audit_id",
        "revision_id",
        "identity_key",
        "Silent disappearance",
        "complete registry",
        "presentation",
        "references/durability.md",
        "references/archetypes.md",
    )
    missing = [fragment for fragment in required_fragments if fragment not in text]
    if missing:
        fail(f"SKILL.md is missing durability contract terms: {missing}")


def validate_sentence_contract(text: str) -> None:
    reference = (ROOT / "references" / "sentence-slop.md").read_text(encoding="utf-8")
    required_skill_fragments = (
        "references/sentence-slop.md",
        "never infer authorship",
        "perplexity",
        "non-native",
    )
    missing_skill = [fragment for fragment in required_skill_fragments if fragment not in text]
    if missing_skill:
        fail(f"SKILL.md is missing sentence-slop guards: {missing_skill}")
    required_reference_fragments = (
        "Compound finding predicate",
        "adequate sample",
        "at least two independent signals",
        "authorship_assessment",
        "not_performed",
        "False-positive guards",
        "UI microcopy",
    )
    missing_reference = [fragment for fragment in required_reference_fragments if fragment not in reference]
    if missing_reference:
        fail(f"sentence-slop reference is missing: {missing_reference}")


def validate_blind_contract(text: str) -> None:
    reference = (ROOT / "references" / "blind-audit.md").read_text(encoding="utf-8")
    required_skill_fragments = (
        "references/blind-audit.md",
        "temporary `CAND-` IDs",
        "freeze the discovery digest",
        "mark the run contaminated",
    )
    missing_skill = [fragment for fragment in required_skill_fragments if fragment not in text]
    if missing_skill:
        fail(f"SKILL.md is missing blind-audit guards: {missing_skill}")
    required_reference_fragments = (
        "Phase 1",
        "Phase 2",
        "blind-manifest.json",
        "blind-discovery.json",
        "blind-freeze.json",
        "freeze before reveal",
        "Cross-agent parity test",
    )
    missing_reference = [fragment for fragment in required_reference_fragments if fragment not in reference]
    if missing_reference:
        fail(f"blind-audit reference is missing: {missing_reference}")


def validate_openai_metadata() -> None:
    text = (ROOT / "agents/openai.yaml").read_text(encoding="utf-8")
    required_fragments = (
        'display_name: "Scruffy"',
        "short_description:",
        "default_prompt:",
        "$scruffy",
        "allow_implicit_invocation: true",
    )
    missing = [fragment for fragment in required_fragments if fragment not in text]
    if missing:
        fail(f"agents/openai.yaml is missing: {missing}")


def validate_public_brand() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    required = (
        '<h1 align="center">Scruffy</h1>',
        "assets/scruffy-hero.png",
        "https://github.com/ur-passwd-hash/scruffy",
        "$scruffy",
        "/scruffy",
        "~/.agents/skills/scruffy",
        "~/.claude/skills/scruffy",
        "internal `anti-slop-*` namespace",
    )
    missing = [fragment for fragment in required if fragment not in text]
    if missing:
        fail(f"README.md is missing Scruffy public-brand terms: {missing}")
    forbidden = (
        "assets/anti-slop-hero.png",
        "ur-passwd-hash/anti-slop",
        "$anti-slop",
        "/anti-slop",
    )
    stale = [fragment for fragment in forbidden if fragment in text]
    if stale:
        fail(f"README.md contains stale Anti-Slop public identifiers: {stale}")


def validate_trigger_evals() -> None:
    path = ROOT / "evals" / "triggers.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"trigger evaluation fixture is unreadable: {error}")
    if data.get("skill") != "scruffy":
        fail("trigger evaluation fixture must name scruffy")
    positives = data.get("should_trigger")
    negatives = data.get("should_not_trigger")
    if not isinstance(positives, list) or len(positives) < 6:
        fail("trigger evaluation fixture needs at least six positive cases")
    if not isinstance(negatives, list) or len(negatives) < 4:
        fail("trigger evaluation fixture needs at least four negative cases")
    prompts = [case.get("prompt") for case in positives + negatives if isinstance(case, dict)]
    if len(prompts) != len(positives) + len(negatives) or any(not prompt for prompt in prompts):
        fail("every trigger evaluation case needs a prompt")
    if len(prompts) != len(set(prompts)):
        fail("trigger evaluation prompts must be unique")


def validate_archetype_evals() -> None:
    path = ROOT / "evals" / "archetypes.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"archetype evaluation fixture is unreadable: {error}")
    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) < 8:
        fail("archetype fixture needs at least eight application classes")
    names: list[str] = []
    prompts: list[str] = []
    reference = (ROOT / "references" / "archetypes.md").read_text(encoding="utf-8")
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            fail(f"archetype case {index} must be an object")
        archetype = case.get("archetype")
        prompt = case.get("prompt")
        reference_heading = case.get("reference_heading")
        probes = case.get("required_probes")
        if not isinstance(archetype, str) or not archetype:
            fail(f"archetype case {index} needs a name")
        if not isinstance(prompt, str) or not prompt:
            fail(f"archetype case {index} needs a prompt")
        if not isinstance(reference_heading, str) or f"## {reference_heading}" not in reference:
            fail(f"archetype case {index} does not map to a reference heading")
        if not isinstance(probes, list) or len(probes) < 5 or any(not isinstance(probe, str) or not probe for probe in probes):
            fail(f"archetype case {index} needs at least five named probes")
        if len(probes) != len(set(probes)):
            fail(f"archetype case {index} repeats probes")
        names.append(archetype)
        prompts.append(prompt)
    if len(names) != len(set(names)):
        fail("archetype names must be unique")
    if len(prompts) != len(set(prompts)):
        fail("archetype prompts must be unique")


def validate_sentence_evals() -> None:
    path = ROOT / "evals" / "sentence-slop" / "cases.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"sentence-slop fixture is unreadable: {error}")
    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) < 6:
        fail("sentence-slop fixture needs at least six cases")
    identifiers: list[str] = []
    contexts: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            fail(f"sentence-slop case {index} must be an object")
        identifier = case.get("id")
        if not isinstance(identifier, str) or not identifier:
            fail(f"sentence-slop case {index} needs an id")
        if case.get("mode") not in {"prose", "ui"}:
            fail(f"sentence-slop case {identifier} has invalid mode")
        if not isinstance(case.get("text"), str) and not isinstance(case.get("items"), list):
            fail(f"sentence-slop case {identifier} needs text or items")
        if not isinstance(case.get("review_needed"), bool):
            fail(f"sentence-slop case {identifier} needs boolean review_needed")
        serialized = json.dumps(case).lower()
        if '"authorship"' in serialized or '"ai_generated"' in serialized:
            fail(f"sentence-slop case {identifier} contains an authorship label")
        identifiers.append(identifier)
        contexts.add(str(case.get("context")))
    if len(identifiers) != len(set(identifiers)):
        fail("sentence-slop case IDs must be unique")
    if not {"general", "technical", "nonnative"}.issubset(contexts):
        fail("sentence-slop fixtures must cover general, technical, and supplied nonnative contexts")


def validate_portability() -> None:
    runtime_files = [SKILL, *sorted((ROOT / "references").glob("*.md"))]
    forbidden = {
        "/usr/share/fonts": "OS-specific font path",
        "localStorage.getItem": "browser-storage inspection",
        "sessionStorage.getItem": "browser-storage inspection",
        "~/.claude": "vendor-specific runtime dependency",
        "Playwright is required": "tool-specific runtime dependency",
    }
    violations: list[str] = []
    for path in runtime_files:
        text = path.read_text(encoding="utf-8")
        for needle, reason in forbidden.items():
            if needle in text:
                violations.append(f"{path.relative_to(ROOT)}: {reason} ({needle})")
    if violations:
        fail("portability violations: " + "; ".join(violations))


def main() -> int:
    text = SKILL.read_text(encoding="utf-8")
    validate_frontmatter(text)
    validate_budget(text)
    validate_links(text)
    validate_required_files()
    validate_durability_contract(text)
    validate_sentence_contract(text)
    validate_blind_contract(text)
    validate_openai_metadata()
    validate_public_brand()
    validate_trigger_evals()
    validate_archetype_evals()
    validate_sentence_evals()
    validate_portability()
    print(
        "PASS: metadata, trigger coverage, progressive-disclosure budget, local references, "
        "durability, sentence, and blind contracts, Scruffy public brand, Codex metadata, trigger/archetype/sentence evals, "
        "required files, and portability"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
