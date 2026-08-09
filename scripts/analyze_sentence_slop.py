#!/usr/bin/env python3
"""Measure sentence-slop leads without making an authorship judgment."""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any


WORD = re.compile(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*")
URL = re.compile(r"\b(?:https?://|www\.)\S+", re.I)
NUMBER_OR_DATE = re.compile(
    r"(?:\b\d+(?:[.,]\d+)?%?\b|\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}\b)",
    re.I,
)

SCAFFOLDS: dict[str, re.Pattern[str]] = {
    "not_x_but_y": re.compile(r"\b(?:it'?s|this is|we are)\s+not\b.{0,80}\bbut\b", re.I),
    "here_is_the": re.compile(r"\bhere(?:'s| is)\s+the\b", re.I),
    "truth_frame": re.compile(r"\bthe truth is\b", re.I),
    "whether_you": re.compile(r"\bwhether you(?:'re| are)\b", re.I),
    "in_a_world": re.compile(r"\bin a world where\b", re.I),
    "what_if": re.compile(r"\bwhat if\b", re.I),
    "key_frame": re.compile(r"\bthe key is\b", re.I),
    "not_about": re.compile(r"\bit'?s not about\b", re.I),
    "at_end_of_day": re.compile(r"\bat the end of the day\b", re.I),
    "lets_frame": re.compile(r"\blet'?s\b", re.I),
}

TRANSITIONS = (
    "additionally",
    "furthermore",
    "moreover",
    "however",
    "ultimately",
    "importantly",
    "in conclusion",
    "in today's",
    "at its core",
    "first and foremost",
    "on the other hand",
)

ABSTRACT_FILLER = (
    "seamless",
    "seamlessly",
    "powerful",
    "innovative",
    "transformative",
    "game-changing",
    "elevate",
    "unlock",
    "reimagine",
    "empower",
    "journey",
    "landscape",
    "possibilities",
    "potential",
    "meaningful impact",
    "next level",
)

ERROR_STATE = re.compile(
    r"\b(?:rejected|declined|denied|blocked|removed|failed|error|unavailable|not saved|not created|not completed)\b",
    re.I,
)
RECOVERY_CUE = re.compile(
    r"\b(?:because|due to|try again|retry|contact|check|choose|fix|restore|retained|kept|appeal|update|learn more|return to)\b",
    re.I,
)

PASSIVE_AUX = r"(?:am|is|are|was|were|be|been|being|become|becomes|became|get|gets|got)"
IRREGULAR_PARTICIPLES = {
    "built", "bought", "caught", "chosen", "done", "drawn", "driven", "found",
    "given", "grown", "held", "kept", "known", "left", "lost", "made", "paid",
    "read", "run", "seen", "sent", "shown", "sold", "spoken", "taken", "taught",
    "told", "thought", "understood", "won", "written",
}

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from", "has",
    "have", "he", "her", "his", "i", "in", "is", "it", "its", "of", "on", "or",
    "our", "she", "that", "the", "their", "them", "they", "this", "to", "was", "we",
    "were", "will", "with", "you", "your",
}

PROTECTED_CONTEXTS = {
    "nonnative",
    "translated",
    "technical",
    "scientific",
    "legal",
    "regulated",
    "safety",
    "accessibility-simple",
}


def tokens(text: str) -> list[str]:
    return [match.group(0).lower().replace("’", "'") for match in WORD.finditer(text)]


def split_sentences(text: str) -> list[str]:
    normalized = re.sub(r"```.*?```", " ", text, flags=re.S)
    blocks = re.split(r"\n\s*\n|(?<=[.!?])\s+(?=[\"'“”‘’(]*[A-Z0-9])", normalized)
    sentences: list[str] = []
    for block in blocks:
        for line in block.splitlines():
            cleaned = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s+", "", line).strip()
            if tokens(cleaned):
                sentences.append(cleaned)
    return sentences


def load_input(path: Path) -> tuple[str, list[dict[str, str]], str | None]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() != ".json":
        return raw, [], None
    data = json.loads(raw)
    if isinstance(data, str):
        return data, [], None
    if not isinstance(data, dict):
        raise ValueError("JSON input must be a string or object")
    supplied_context = data.get("context") if isinstance(data.get("context"), str) else None
    if isinstance(data.get("text"), str):
        return data["text"], [], supplied_context
    raw_items = data.get("items")
    if not isinstance(raw_items, list):
        raise ValueError("JSON object must contain text or items")
    items: list[dict[str, str]] = []
    for index, item in enumerate(raw_items):
        if isinstance(item, str):
            items.append({"surface": f"item-{index + 1}", "text": item})
        elif isinstance(item, dict) and isinstance(item.get("text"), str):
            surface = item.get("surface")
            items.append({"surface": str(surface or f"item-{index + 1}"), "text": item["text"]})
        else:
            raise ValueError(f"items[{index}] must be a string or an object with text")
    return "\n".join(item["text"] for item in items), items, supplied_context


def passive_candidates(sentences: list[str]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for index, sentence in enumerate(sentences, 1):
        words = tokens(sentence)
        for offset, word in enumerate(words[:-1]):
            if not re.fullmatch(PASSIVE_AUX, word):
                continue
            window = words[offset + 1 : offset + 4]
            hit = next(
                (candidate for candidate in window if candidate.endswith(("ed", "en")) or candidate in IRREGULAR_PARTICIPLES),
                None,
            )
            if hit:
                results.append({"sentence": index, "auxiliary": word, "participle": hit, "text": sentence[:240]})
                break
    return results


def repeated_openings(sentences: list[str]) -> list[dict[str, Any]]:
    grouped: Counter[str] = Counter()
    examples: dict[str, list[int]] = {}
    for index, sentence in enumerate(sentences, 1):
        words = tokens(sentence)
        if len(words) < 2:
            continue
        opening = " ".join(words[:2])
        grouped[opening] += 1
        examples.setdefault(opening, []).append(index)
    return [
        {"opening": opening, "count": count, "sentences": examples[opening]}
        for opening, count in grouped.most_common()
        if count >= 2
    ]


def repeated_ngrams(text: str, size: int = 3) -> list[dict[str, Any]]:
    words = tokens(text)
    counts: Counter[tuple[str, ...]] = Counter()
    for index in range(len(words) - size + 1):
        gram = tuple(words[index : index + size])
        if sum(word not in STOPWORDS for word in gram) < 2:
            continue
        counts[gram] += 1
    return [
        {"ngram": " ".join(gram), "count": count}
        for gram, count in counts.most_common(8)
        if count >= 2
    ]


def add_lead(leads: list[dict[str, Any]], code: str, measurement: str, reason: str, examples: list[Any], guard: str) -> None:
    leads.append(
        {
            "code": code,
            "measurement": measurement,
            "reason_to_review": reason,
            "examples": examples[:6],
            "false_positive_guard": guard,
        }
    )


def analyze(text: str, *, mode: str = "auto", context: str = "general", items: list[dict[str, str]] | None = None) -> dict[str, Any]:
    items = items or []
    resolved_mode = "ui_microcopy" if mode == "ui" or (mode == "auto" and items) else "prose"
    sentences = split_sentences(text)
    word_list = tokens(text)
    lengths = [len(tokens(sentence)) for sentence in sentences if tokens(sentence)]
    word_count = len(word_list)
    sentence_count = len(lengths)
    surface_count = len(items) if items else (1 if text.strip() else 0)

    if resolved_mode == "prose":
        if word_count >= 150 and sentence_count >= 5:
            adequacy = "adequate"
        elif word_count >= 80 and sentence_count >= 5:
            adequacy = "limited"
        else:
            adequacy = "insufficient"
    else:
        adequacy = "adequate" if surface_count >= 8 else ("limited" if surface_count >= 3 else "insufficient")

    mean_length = statistics.fmean(lengths) if lengths else 0.0
    stdev = statistics.pstdev(lengths) if len(lengths) > 1 else 0.0
    coefficient = stdev / mean_length if mean_length else 0.0
    openings = repeated_openings(sentences)
    questions = [
        {"sentence": index, "text": sentence[:240]}
        for index, sentence in enumerate(sentences, 1)
        if sentence.rstrip().endswith("?")
    ]
    passives = passive_candidates(sentences)
    scaffold_hits = {
        name: len(pattern.findall(text)) for name, pattern in SCAFFOLDS.items() if pattern.search(text)
    }
    transition_hits: list[dict[str, Any]] = []
    for index, sentence in enumerate(sentences, 1):
        lowered = sentence.lower().lstrip("\"'“”‘’(")
        hit = next((transition for transition in TRANSITIONS if lowered.startswith(transition)), None)
        if hit:
            transition_hits.append({"sentence": index, "transition": hit, "text": sentence[:240]})
    grams = repeated_ngrams(text)
    filler_hits = {
        phrase: len(re.findall(rf"\b{re.escape(phrase)}\b", text, re.I))
        for phrase in ABSTRACT_FILLER
        if re.search(rf"\b{re.escape(phrase)}\b", text, re.I)
    }
    proper_tokens = re.findall(r"(?<![.!?]\s)\b[A-Z][A-Za-z0-9'-]{2,}\b", text)
    anchors = len(NUMBER_OR_DATE.findall(text)) + len(URL.findall(text)) + len(proper_tokens)
    unrecoverable_errors = [
        {"surface": item["surface"], "text": item["text"][:240]}
        for item in items
        if ERROR_STATE.search(item["text"]) and not RECOVERY_CUE.search(item["text"])
    ]

    leads: list[dict[str, Any]] = []
    prose_stats_allowed = resolved_mode == "prose" and adequacy in {"adequate", "limited"}
    if prose_stats_allowed and sentence_count >= 6 and coefficient <= 0.28:
        add_lead(
            leads,
            "cadence_uniformity",
            f"sentence-length coefficient of variation {coefficient:.2f} across {sentence_count} sentences",
            "Low variation can flatten an intended editorial or product voice.",
            lengths,
            "Short, plain, procedural, safety, or accessibility-focused sentences may be intentionally regular.",
        )
    repeated_count = sum(entry["count"] - 1 for entry in openings)
    if sentence_count >= 5 and repeated_count >= 2:
        add_lead(
            leads,
            "repeated_openings",
            f"{repeated_count} repeated openings across {sentence_count} sentences",
            "Repeated sentence frames can substitute rhythm for information.",
            openings,
            "Parallel structure is legitimate when it clarifies a comparison, procedure, or teaching sequence.",
        )
    if sentence_count >= 5 and len(questions) >= 2 and len(questions) / sentence_count >= 0.25:
        add_lead(
            leads,
            "rhetorical_question_density",
            f"{len(questions)} question sentences ({len(questions) / sentence_count:.0%})",
            "Repeated questions may manufacture momentum without supplying an answer or decision.",
            questions,
            "Questions are appropriate when the interface actually requests an answer or teaches through inquiry.",
        )
    if len(passives) >= 2 and sentence_count >= 4:
        add_lead(
            leads,
            "passive_candidates",
            f"{len(passives)} approximate passive constructions",
            "Responsibility, state, or recovery may be obscured.",
            passives,
            "The heuristic is approximate; passive voice is valid when the actor is unknown, irrelevant, or deliberately deemphasized.",
        )
    scaffold_total = sum(scaffold_hits.values())
    if scaffold_total >= 2:
        add_lead(
            leads,
            "formulaic_scaffolds",
            f"{scaffold_total} scaffold matches",
            "Stock rhetorical frames can crowd out product-specific information.",
            [{"pattern": key, "count": value} for key, value in scaffold_hits.items()],
            "One familiar construction is not a defect; confirm repetition and lost specificity.",
        )
    if sentence_count >= 6 and len(transition_hits) >= 3 and len(transition_hits) / sentence_count >= 0.30:
        add_lead(
            leads,
            "transition_concentration",
            f"{len(transition_hits)} transition-led sentences ({len(transition_hits) / sentence_count:.0%})",
            "Repeated discourse markers may conceal a weak information hierarchy.",
            transition_hits,
            "Transitions are useful in arguments; confirm they repeat without adding structure.",
        )
    if grams and word_count >= 60:
        add_lead(
            leads,
            "phrase_repetition",
            f"{len(grams)} repeated nontrivial trigrams",
            "Unnecessary phrase reuse can make copy feel templated.",
            grams,
            "Exclude required terminology, commands, warnings, and deliberate teaching reinforcement.",
        )
    filler_total = sum(filler_hits.values())
    anchors_per_100 = anchors / word_count * 100 if word_count else 0.0
    if word_count >= 80 and filler_total >= 3 and anchors_per_100 < 2.0:
        add_lead(
            leads,
            "detail_sparsity",
            f"{filler_total} abstract-filler matches and {anchors_per_100:.1f} concrete anchors per 100 words",
            "Abstract promises may dominate actors, objects, conditions, examples, or consequences.",
            [{"phrase": key, "count": value} for key, value in filler_hits.items()],
            "A low anchor count is only a crude lead; inspect whether the surrounding product context already supplies specifics.",
        )
    if resolved_mode == "ui_microcopy" and len(unrecoverable_errors) >= 2:
        add_lead(
            leads,
            "missing_recovery_information",
            f"{len(unrecoverable_errors)} error-state strings lack a cause or recovery cue",
            "Users may not know what failed, what was retained, or what action can resolve the state.",
            unrecoverable_errors,
            "The surrounding surface may supply the missing cause and action; inspect each rendered state before promoting the lead.",
        )

    protected = context in PROTECTED_CONTEXTS
    independent_codes = {lead["code"] for lead in leads}
    compound_signal = adequacy != "insufficient" and len(independent_codes) >= 2 and not protected
    return {
        "schema_version": "1.0",
        "mode": resolved_mode,
        "context": context,
        "authorship_assessment": "not_performed",
        "sample": {
            "words": word_count,
            "sentences": sentence_count,
            "surfaces": surface_count,
            "adequacy": adequacy,
        },
        "metrics": {
            "sentence_lengths": lengths,
            "mean_sentence_words": round(mean_length, 2),
            "sentence_length_stdev": round(stdev, 2),
            "sentence_length_coefficient_of_variation": round(coefficient, 3),
            "rhetorical_questions": len(questions),
            "passive_candidates": len(passives),
            "formulaic_scaffolds": scaffold_total,
            "concrete_anchors": anchors,
            "abstract_filler_matches": filler_total,
            "error_states_without_recovery_cue": len(unrecoverable_errors),
        },
        "leads": leads,
        "compound_signal": {
            "review_needed": compound_signal,
            "independent_signal_count": len(independent_codes),
            "finding_eligible": False,
            "reason": (
                "Protected context supplied; judge clarity and task fit without cadence-based escalation."
                if protected
                else "Human review must still prove a product consequence and test a counterexample."
            ),
        },
        "guards": {
            "protected_context_applied": protected,
            "no_authorship_inference": True,
            "statistical_leads_are_length_gated": True,
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="UTF-8 text file or JSON object with text/items")
    parser.add_argument("--mode", choices=("auto", "prose", "ui"), default="auto")
    parser.add_argument(
        "--context",
        choices=("general", *sorted(PROTECTED_CONTEXTS)),
        default=None,
        help="Use only when the context is supplied; never infer it from prose.",
    )
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        text, items, supplied_context = load_input(args.input)
        context = args.context or supplied_context or "general"
        result = analyze(text, mode=args.mode, context=context, items=items)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
