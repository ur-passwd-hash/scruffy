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
    r"(?:[$£€]\s?\d+(?:[.,]\d+)?|\b\d+(?:[.,]\d+)?%?\b|\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}\b)",
    re.I,
)
QUOTED_LABEL = re.compile(r"[\"“]([A-Za-z0-9][^\"”\n]{1,48})[\"”]")
FENCED_CODE = re.compile(r"(?ms)^\s*(```|~~~).*?^\s*\1\s*$")
HTML_CODE_BLOCK = re.compile(r"(?is)<(?:script|style|pre|code)\b[^>]*>.*?</(?:script|style|pre|code)>")
HTML_COMMENT = re.compile(r"(?s)<!--.*?-->")
HTML_IMAGE = re.compile(r"(?is)<img\b[^>]*>")
HTML_TAG = re.compile(r"(?s)<[^>]+>")
MARKDOWN_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")
INLINE_CODE = re.compile(r"`[^`\n]+`")
MARKDOWN_TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$")
HORIZONTAL_RULE = re.compile(r"^\s{0,3}(?:[-*_]\s*){3,}$")
COMMAND_LINE = re.compile(
    r"^\s{0,3}(?:[$>]\s*)?(?:git|gh|npm|npx|pnpm|yarn|python\d*|pip|uv|cargo|go|curl|wget|mkdir|ln|cp|mv|claude|codex|/scruffy|\$scruffy)\b"
)

SCAFFOLDS: dict[str, re.Pattern[str]] = {
    "not_x_but_y": re.compile(r"\b(?:it'?s|this is|we are|that is)?\s*not\s+(?!(?:because|just|about)\b)[^.!?\n]{0,100}\bbut\b", re.I),
    "not_because_but": re.compile(r"\bnot because\b[^.!?\n]{0,100}\bbut because\b", re.I),
    "not_just_but": re.compile(r"\bnot just\b[^.!?\n]{0,100}\b(?:but|also)\b", re.I),
    "here_is_the": re.compile(r"\bhere(?:'s| is)\s+the\s+(?:truth|thing|catch|problem|point)\b", re.I),
    "truth_frame": re.compile(r"\bthe truth is\b", re.I),
    "whether_you": re.compile(r"\bwhether you(?:'re| are)\b", re.I),
    "in_a_world": re.compile(r"\bin a world where\b", re.I),
    "what_if": re.compile(r"\bwhat if\b", re.I),
    "key_frame": re.compile(r"\bthe key is\b", re.I),
    "not_about": re.compile(r"\bit'?s not about\b", re.I),
    "at_end_of_day": re.compile(r"\bat the end of the day\b", re.I),
    "lets_frame": re.compile(r"\blet'?s\b", re.I),
    "this_is_why": re.compile(r"\bthis is why\b", re.I),
    "that_matters": re.compile(r"\band that matters\b", re.I),
    "simply_put": re.compile(r"\bsimply put\b", re.I),
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
SUPPORTED_LANGUAGES = {"en"}
LANGUAGE_CHOICES = {"en", "non_en", "unknown"}

SIGNAL_FAMILIES = {
    "cadence_uniformity": "rhythm",
    "repeated_openings": "rhythm",
    "short_sentence_burst": "rhythm",
    "rhetorical_question_density": "rhetorical_structure",
    "formulaic_scaffolds": "rhetorical_structure",
    "transition_concentration": "rhetorical_structure",
    "paragraph_pattern_reuse": "discourse_structure",
    "phrase_repetition": "lexical_repetition",
    "detail_sparsity": "specificity",
    "passive_candidates": "responsibility",
    "missing_recovery_information": "responsibility",
}


def tokens(text: str) -> list[str]:
    return [match.group(0).lower().replace("’", "'") for match in WORD.finditer(text)]


def normalize_prose(text: str) -> tuple[str, dict[str, Any]]:
    """Remove repository markup and code before measuring reader-facing prose."""
    source_words = len(tokens(text))
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    removed: Counter[str] = Counter()

    if normalized.startswith("---\n"):
        end = normalized.find("\n---", 4)
        if end != -1:
            newline = normalized.find("\n", end + 4)
            normalized = normalized[newline + 1 :] if newline != -1 else ""
            removed["frontmatter_blocks"] += 1

    normalized, count = FENCED_CODE.subn("\n", normalized)
    removed["fenced_code_blocks"] += count
    normalized, count = HTML_CODE_BLOCK.subn(" ", normalized)
    removed["html_code_blocks"] += count
    normalized, count = HTML_COMMENT.subn(" ", normalized)
    removed["html_comments"] += count
    normalized, count = MARKDOWN_IMAGE.subn(" ", normalized)
    removed["markdown_images"] += count
    normalized, count = HTML_IMAGE.subn(" ", normalized)
    removed["html_images"] += count
    normalized, count = INLINE_CODE.subn(" ", normalized)
    removed["inline_code_spans"] += count
    normalized, count = MARKDOWN_LINK.subn(r"\1", normalized)
    removed["markdown_link_destinations"] += count
    normalized, count = URL.subn(" ", normalized)
    removed["raw_urls"] += count

    output: list[str] = []
    for raw_line in normalized.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            output.append("")
            continue
        if re.match(r"^\s{0,3}#{1,6}\s+", line):
            removed["heading_lines"] += 1
            output.append("")
            continue
        if HORIZONTAL_RULE.match(line) or MARKDOWN_TABLE_SEPARATOR.match(line):
            removed["structural_lines"] += 1
            output.append("")
            continue
        if line.count("|") >= 2 and stripped.startswith("|"):
            removed["table_rows"] += 1
            output.append("")
            continue
        if COMMAND_LINE.match(line):
            removed["command_lines"] += 1
            output.append("")
            continue

        without_tags, tag_count = HTML_TAG.subn(" ", line)
        if tag_count:
            removed["html_tag_occurrences"] += tag_count
        cleaned = re.sub(r"^\s*>+\s?", "", without_tags)
        list_match = re.match(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)(.*)$", cleaned)
        if list_match:
            cleaned = list_match.group(1)
            removed["list_markers"] += 1
        cleaned = re.sub(r"(?<!\w)[*_~]{1,2}([^*_~]+)[*_~]{1,2}(?!\w)", r"\1", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if not tokens(cleaned):
            if stripped:
                removed["markup_only_lines"] += 1
            output.append("")
            continue

        output.append(cleaned)
        if list_match:
            output.append("")

    cleaned_text = re.sub(r"\n{3,}", "\n\n", "\n".join(output)).strip()
    analyzed_words = len(tokens(cleaned_text))
    return cleaned_text, {
        "applied": True,
        "source_words": source_words,
        "analyzed_words": analyzed_words,
        "words_excluded": max(0, source_words - analyzed_words),
        "source_characters": len(text),
        "analyzed_characters": len(cleaned_text),
        "removed": dict(sorted(removed.items())),
    }


def split_sentences(text: str) -> list[str]:
    blocks = re.split(r"\n\s*\n|(?<=[.!?])\s+(?=[\"'“”‘’(]*[A-Za-z0-9])", text)
    sentences: list[str] = []
    for block in blocks:
        for line in block.splitlines():
            cleaned = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s+", "", line).strip()
            if tokens(cleaned):
                sentences.append(cleaned)
    return sentences


def sentence_role(sentence: str) -> str:
    lowered = sentence.lower().lstrip("\"'“”‘’(")
    if sentence.rstrip().endswith("?"):
        return "question"
    if any(pattern.search(sentence) for pattern in SCAFFOLDS.values()):
        return "scaffold"
    if any(lowered.startswith(transition) for transition in TRANSITIONS):
        return "transition"
    if len(tokens(sentence)) <= 5:
        return "short"
    return "statement"


def paragraph_patterns(text: str) -> list[dict[str, Any]]:
    signatures: Counter[tuple[str, ...]] = Counter()
    examples: dict[tuple[str, ...], list[str]] = {}
    for paragraph in re.split(r"\n\s*\n", text):
        sentences = split_sentences(paragraph)
        if len(sentences) < 2:
            continue
        signature = tuple(sentence_role(sentence) for sentence in sentences[:3])
        if not any(role != "statement" for role in signature):
            continue
        signatures[signature] += 1
        examples.setdefault(signature, []).append(paragraph[:240])
    return [
        {
            "signature": " > ".join(signature),
            "count": count,
            "examples": examples[signature][:3],
        }
        for signature, count in signatures.most_common()
        if count >= 3
    ]


def specificity_markers(text: str, sentences: list[str]) -> dict[str, Any]:
    numeric = NUMBER_OR_DATE.findall(text)
    quoted = [match.group(1) for match in QUOTED_LABEL.finditer(text)]
    proper: list[str] = []
    for sentence in sentences:
        matches = list(WORD.finditer(sentence))
        for position, match in enumerate(matches):
            value = match.group(0)
            if position == 0 or len(value) < 3:
                continue
            if value.isupper() or value[0].isupper():
                proper.append(value)
    return {
        "count": len(numeric) + len(quoted) + len(proper),
        "numeric_or_date": len(numeric),
        "quoted_labels": len(quoted),
        "proper_names": len(proper),
        "examples": (numeric[:3] + quoted[:3] + proper[:3])[:8],
    }


def load_input(path: Path) -> tuple[str, list[dict[str, str]], str | None, str | None]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() != ".json":
        return raw, [], None, None
    data = json.loads(raw)
    if isinstance(data, str):
        return data, [], None, None
    if not isinstance(data, dict):
        raise ValueError("JSON input must be a string or object")
    supplied_context = data.get("context") if isinstance(data.get("context"), str) else None
    supplied_language = data.get("language") if isinstance(data.get("language"), str) else None
    if isinstance(data.get("text"), str):
        return data["text"], [], supplied_context, supplied_language
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
    return "\n".join(item["text"] for item in items), items, supplied_context, supplied_language


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
    minimum_count = 3 if len(words) >= 300 else 2
    counts: Counter[tuple[str, ...]] = Counter()
    for index in range(len(words) - size + 1):
        gram = tuple(words[index : index + size])
        if sum(word not in STOPWORDS for word in gram) < 2:
            continue
        counts[gram] += 1
    return [
        {"ngram": " ".join(gram), "count": count}
        for gram, count in counts.most_common(8)
        if count >= minimum_count
    ]


def add_lead(leads: list[dict[str, Any]], code: str, measurement: str, reason: str, examples: list[Any], guard: str) -> None:
    leads.append(
        {
            "code": code,
            "signal_family": SIGNAL_FAMILIES[code],
            "measurement": measurement,
            "reason_to_review": reason,
            "examples": examples[:6],
            "false_positive_guard": guard,
        }
    )


def analyze(
    text: str,
    *,
    mode: str = "auto",
    context: str = "general",
    language: str = "unknown",
    items: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    if language not in LANGUAGE_CHOICES:
        raise ValueError(f"language must be one of {sorted(LANGUAGE_CHOICES)}")
    items = items or []
    resolved_mode = "ui_microcopy" if mode == "ui" or (mode == "auto" and items) else "prose"
    if resolved_mode == "prose":
        analysis_text, normalization = normalize_prose(text)
    else:
        analysis_text = text
        normalization = {
            "applied": False,
            "source_words": len(tokens(text)),
            "analyzed_words": len(tokens(text)),
            "words_excluded": 0,
            "source_characters": len(text),
            "analyzed_characters": len(text),
            "removed": {},
        }
    sentences = split_sentences(analysis_text)
    word_list = tokens(analysis_text)
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
        name: len(pattern.findall(analysis_text))
        for name, pattern in SCAFFOLDS.items()
        if pattern.search(analysis_text)
    }
    transition_hits: list[dict[str, Any]] = []
    for index, sentence in enumerate(sentences, 1):
        lowered = sentence.lower().lstrip("\"'“”‘’(")
        hit = next((transition for transition in TRANSITIONS if lowered.startswith(transition)), None)
        if hit:
            transition_hits.append({"sentence": index, "transition": hit, "text": sentence[:240]})
    grams = repeated_ngrams(analysis_text)
    filler_hits = {
        phrase: len(re.findall(rf"\b{re.escape(phrase)}\b", analysis_text, re.I))
        for phrase in ABSTRACT_FILLER
        if re.search(rf"\b{re.escape(phrase)}\b", analysis_text, re.I)
    }
    specificity = specificity_markers(analysis_text, sentences)
    anchors = specificity["count"]
    short_sentences = [
        {"sentence": index, "words": len(tokens(sentence)), "text": sentence[:240]}
        for index, sentence in enumerate(sentences, 1)
        if 1 <= len(tokens(sentence)) <= 5
    ]
    reused_paragraph_patterns = paragraph_patterns(analysis_text) if resolved_mode == "prose" else []
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
    strongly_repeated_opening = any(entry["count"] >= 3 for entry in openings)
    if sentence_count >= 5 and repeated_count >= 3 and (strongly_repeated_opening or len(openings) >= 2):
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
    passive_ratio = len(passives) / sentence_count if sentence_count else 0.0
    if len(passives) >= 3 and sentence_count >= 5 and passive_ratio >= 0.20:
        add_lead(
            leads,
            "passive_candidates",
            f"{len(passives)} approximate passive constructions ({passive_ratio:.0%} of sentences)",
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
    short_sentence_ratio = len(short_sentences) / sentence_count if sentence_count else 0.0
    if prose_stats_allowed and sentence_count >= 10 and len(short_sentences) >= 3 and short_sentence_ratio >= 0.25:
        add_lead(
            leads,
            "short_sentence_burst",
            f"{len(short_sentences)} sentences of five words or fewer ({short_sentence_ratio:.0%})",
            "Repeated punchline-length units can flatten prose into a promotional beat instead of developing the idea.",
            short_sentences,
            "Short sentences are legitimate for emphasis, accessibility, dialogue, instructions, and deliberate pacing; verify repetition and consequence.",
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
    repeated_gram_excess = sum(entry["count"] - 1 for entry in grams)
    if grams and word_count >= 60 and repeated_gram_excess >= 2:
        add_lead(
            leads,
            "phrase_repetition",
            f"{len(grams)} repeated nontrivial trigrams",
            "Unnecessary phrase reuse can make copy feel templated.",
            grams,
            "Exclude required terminology, commands, warnings, and deliberate teaching reinforcement.",
        )
    if reused_paragraph_patterns:
        add_lead(
            leads,
            "paragraph_pattern_reuse",
            f"{len(reused_paragraph_patterns)} non-plain paragraph signature(s) recur at least three times",
            "Repeated paragraph choreography can make different ideas arrive in the same prebuilt rhetorical container.",
            reused_paragraph_patterns,
            "FAQ, lesson, legal, comparison, and procedural formats may deliberately repeat a paragraph shape; confirm that the structure obscures rather than supports the task.",
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

    language_supported = language in SUPPORTED_LANGUAGES
    if not language_supported:
        leads = []
    protected = context in PROTECTED_CONTEXTS
    independent_codes = {lead["code"] for lead in leads}
    independent_families = {lead["signal_family"] for lead in leads}
    dependency_collapses: list[str] = []
    rhythm_codes = independent_codes & {"cadence_uniformity", "repeated_openings", "short_sentence_burst"}
    if rhythm_codes == {"repeated_openings"}:
        repeated_sentence_indexes = {
            index
            for opening in openings
            for index in opening["sentences"]
            if opening["count"] >= 2
        }
        repeated_roles = {
            sentence_role(sentences[index - 1])
            for index in repeated_sentence_indexes
            if 0 < index <= len(sentences)
        }
        if repeated_roles and repeated_roles <= {"question", "scaffold", "transition"}:
            independent_families.discard("rhythm")
            dependency_collapses.append(
                "repeated_openings reused the same question, scaffold, or transition evidence as the rhetorical-structure lead"
            )
    compound_signal = (
        language_supported
        and adequacy != "insufficient"
        and len(independent_families) >= 2
        and not protected
    )
    manual_checks = []
    if resolved_mode == "prose" and (adequacy != "insufficient" or (not language_supported and bool(text.strip()))):
        manual_checks = [
            {
                "code": "conceptual_coherence",
                "procedure": "Trace each metaphor, comparison, and key noun across adjacent sentences; quote any verb-object or source-target mapping that stops making literal or figurative sense.",
                "promotion_rule": "Promote only when the collision changes or obscures the claimed meaning; mixed metaphor alone does not identify an author.",
            },
            {
                "code": "sentence_portability",
                "procedure": "Test whether a representative claim could be pasted into several unrelated products without changing its meaning; then identify the missing actor, object, condition, example, evidence, or consequence.",
                "promotion_rule": "Promote only when the missing detail prevents understanding, choice, trust, recovery, or differentiation.",
            },
            {
                "code": "discourse_purpose",
                "procedure": "Label what each paragraph contributes to the reader's task; challenge repeated setup, contrast, validation, summary, or call-to-action moves that add no new decision-relevant information.",
                "promotion_rule": "Repeated form is acceptable when the genre or task benefits from it.",
            },
            {
                "code": "voice_and_subtext",
                "procedure": "Compare the passage with the product's supplied voice and neighboring surfaces; identify where generic explanation erases a necessary point of view, lived detail, restraint, or subtext.",
                "promotion_rule": "Do not invent a preferred voice and do not equate polish, formality, simplicity, or language background with a defect.",
            },
        ]

    return {
        "schema_version": "1.2",
        "mode": resolved_mode,
        "context": context,
        "language": language,
        "language_analysis_status": "supported" if language_supported else "abstained",
        "authorship_assessment": "not_performed",
        "normalization": normalization,
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
            "specificity_markers": specificity,
            "abstract_filler_matches": filler_total,
            "short_sentences": len(short_sentences),
            "paragraph_patterns_reused": len(reused_paragraph_patterns),
            "error_states_without_recovery_cue": len(unrecoverable_errors),
        },
        "leads": leads,
        "manual_review": {
            "required": bool(manual_checks),
            "automation_boundary": "Conceptual coherence, sentence portability, discourse purpose, and voice fit are not scored automatically.",
            "checks": manual_checks,
        },
        "compound_signal": {
            "review_needed": compound_signal,
            "independent_signal_count": len(independent_families),
            "independent_signal_families": sorted(independent_families),
            "lead_codes": sorted(independent_codes),
            "dependency_collapses": dependency_collapses,
            "finding_eligible": False,
            "reason": (
                "English-specific surface analysis abstained; use a language-competent reviewer and do not promote these measurements."
                if not language_supported
                else (
                    "Protected context supplied; judge clarity and task fit without cadence-based escalation."
                    if protected
                    else "Human review must still prove a product consequence and test a counterexample."
                )
            ),
        },
        "guards": {
            "protected_context_applied": protected,
            "no_authorship_inference": True,
            "statistical_leads_are_length_gated": True,
            "markup_excluded_from_prose_statistics": resolved_mode == "prose",
            "single_surface_tell_is_not_a_finding": True,
            "semantic_coherence_requires_human_review": True,
            "unsupported_language_abstention": not language_supported,
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="UTF-8 text file or JSON object with text/items")
    parser.add_argument("--mode", choices=("auto", "prose", "ui"), default="auto")
    parser.add_argument(
        "--language",
        choices=sorted(LANGUAGE_CHOICES),
        default=None,
        help="Required scope for surface analysis: en, non_en, or unknown. Unknown and non_en abstain.",
    )
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
        text, items, supplied_context, supplied_language = load_input(args.input)
        context = args.context or supplied_context or "general"
        language = args.language or supplied_language or "unknown"
        result = analyze(text, mode=args.mode, context=context, language=language, items=items)
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
