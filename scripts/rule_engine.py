#!/usr/bin/env python3
"""Deterministic rule engine: evaluate JSON rule packs against HTML and emit leads.

Leads are not findings. Every lead carries confirmation_required=true and must be
confirmed or cleared by operating the interface under the Scruffy runtime contract.
The engine never assesses authorship.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from taxonomy_contract import load_taxonomy

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RULES_DIR = ROOT / "schema" / "rules"
SEVERITIES = ("suggestion", "warning", "error")
PREDICATE_TYPES = {
    "element_pattern",
    "text_pattern",
    "unlabeled_input",
    "interactive_non_semantic",
    "state_group_without_address",
    "element_missing_attrs",
    "document_missing",
    "blocking_script",
    "empty_interactive",
    "duplicate_id",
    "script_pattern",
    "operated_check",
}
TEXT_BLOCK_TAGS = {
    "p", "li", "h1", "h2", "h3", "h4", "h5", "h6",
    "figcaption", "td", "th", "span", "small", "a", "button", "label", "blockquote", "dd", "dt",
}
VOID_TAGS = {"input", "img", "br", "hr", "meta", "link", "source", "track", "wbr", "area", "base", "col", "embed"}
TEXT_INPUT_TYPES = {"", "text", "email", "search", "url", "tel", "password", "number"}
CITATION_PATTERN = re.compile(r"^principles/PRINCIPLES\.md §([0-9]+)$")


class PackError(ValueError):
    pass


def load_packs(rules_dir: Path, extra_packs: list[Path]) -> list[dict[str, Any]]:
    paths = sorted(rules_dir.glob("*.json")) + list(extra_packs)
    packs = []
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        data["_path"] = str(path)
        packs.append(data)
    return packs


def validate_packs(packs: list[dict[str, Any]]) -> None:
    taxonomy = load_taxonomy()
    categories = {row["key"] for row in taxonomy["categories"]}
    principles = (ROOT / "principles" / "PRINCIPLES.md").read_text(encoding="utf-8")
    seen_ids: dict[str, str] = {}
    for pack in packs:
        label = pack.get("pack") or pack.get("_path", "pack")
        if pack.get("schema_version") != "1.0":
            raise PackError(f"{label}: schema_version must be 1.0")
        if pack.get("origin") not in {"baseline", "user"}:
            raise PackError(f"{label}: origin must be baseline or user")
        if pack["origin"] == "user":
            attribution = pack.get("source_attribution")
            if not isinstance(attribution, dict) or not attribution.get("title") or not attribution.get("creator"):
                raise PackError(f"{label}: user packs must attribute their source (title and creator)")
        if not isinstance(pack.get("rules"), list) or not pack["rules"]:
            raise PackError(f"{label}: rules must be a non-empty list")
        for rule in pack["rules"]:
            rule_id = rule.get("id", "")
            if not re.fullmatch(r"[A-Z][A-Z0-9]*(-[A-Z0-9]+)+", rule_id):
                raise PackError(f"{label}: rule id {rule_id!r} must be UPPER-KEBAB")
            if rule_id in seen_ids:
                raise PackError(f"rule id {rule_id} appears in both {seen_ids[rule_id]} and {label}")
            seen_ids[rule_id] = label
            if rule.get("category") not in categories:
                raise PackError(f"{rule_id}: category must be one of the canonical keys")
            if rule.get("severity") not in SEVERITIES:
                raise PackError(f"{rule_id}: severity must be one of {SEVERITIES}")
            for field in ("message", "false_positive_guard", "citation"):
                if not rule.get(field):
                    raise PackError(f"{rule_id}: {field} is required")
            match = CITATION_PATTERN.fullmatch(rule["citation"])
            if not match:
                raise PackError(f"{rule_id}: citation must look like 'principles/PRINCIPLES.md §N'")
            if f"## {match.group(1)}." not in principles:
                raise PackError(f"{rule_id}: citation section §{match.group(1)} does not exist in PRINCIPLES.md")
            predicate = rule.get("predicate")
            if not isinstance(predicate, dict) or predicate.get("type") not in PREDICATE_TYPES:
                raise PackError(f"{rule_id}: predicate.type must be one of {sorted(PREDICATE_TYPES)}")
            if predicate["type"] == "element_missing_attrs" and not predicate.get("absent_attrs"):
                raise PackError(f"{rule_id}: element_missing_attrs needs absent_attrs")
            if predicate["type"] == "document_missing" and not predicate.get("tag"):
                raise PackError(f"{rule_id}: document_missing needs a tag")
            if predicate["type"] == "operated_check" and not predicate.get("instruction"):
                raise PackError(f"{rule_id}: operated_check needs an instruction")
            if predicate["type"] == "script_pattern":
                re.compile(predicate.get("pattern") or "")
                if not predicate.get("pattern"):
                    raise PackError(f"{rule_id}: script_pattern needs a pattern")
            if predicate["type"] in {"element_pattern", "text_pattern"}:
                pattern = predicate.get("value_pattern" if predicate["type"] == "element_pattern" else "pattern")
                if pattern is None:
                    raise PackError(f"{rule_id}: predicate needs its pattern")
                re.compile(pattern)


class PageIndex(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[dict[str, Any]] = []
        self.stack: list[int] = []
        self.scripts: list[str] = []
        self._in_script = False
        self._in_style = False
        self.label_for: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {name: (value if value is not None else "") for name, value in attrs}
        parent = self.stack[-1] if self.stack else None
        element = {
            "index": len(self.elements),
            "tag": tag,
            "attrs": attr_map,
            "parent": parent,
            "text": [],
            "line": self.getpos()[0],
        }
        self.elements.append(element)
        if tag == "label" and attr_map.get("for"):
            self.label_for.add(attr_map["for"])
        if tag == "script":
            self._in_script = True
        elif tag == "style":
            self._in_style = True
        if tag not in VOID_TAGS:
            self.stack.append(element["index"])

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS and self.stack and self.stack[-1] == len(self.elements) - 1:
            self.stack.pop()

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._in_script = False
        elif tag == "style":
            self._in_style = False
        for position in range(len(self.stack) - 1, -1, -1):
            if self.elements[self.stack[position]]["tag"] == tag:
                del self.stack[position:]
                break

    def handle_data(self, data: str) -> None:
        if self._in_script:
            self.scripts.append(data)
            return
        if self._in_style or not data.strip():
            return
        if self.stack:
            self.elements[self.stack[-1]]["text"].append(data.strip())

    def sample_hint(self, index: int) -> str | None:
        current: int | None = index
        while current is not None:
            element = self.elements[current]
            hint = element["attrs"].get("data-sample")
            if hint:
                return hint
            current = element["parent"]
        return None

    def has_ancestor(self, index: int, tag: str) -> bool:
        current = self.elements[index]["parent"]
        while current is not None:
            if self.elements[current]["tag"] == tag:
                return True
            current = self.elements[current]["parent"]
        return False



def collect_subtree_text(page: PageIndex, root_index: int) -> str:
    parts: list[str] = []
    for element in page.elements[root_index:]:
        current: int | None = element["index"]
        inside = False
        while current is not None:
            if current == root_index:
                inside = True
                break
            current = page.elements[current]["parent"]
        if inside:
            parts.extend(element["text"])
        elif element["index"] > root_index and element["parent"] is not None and element["parent"] < root_index:
            break
    return " ".join(parts)


def subtree_has_named_image(page: PageIndex, root_index: int) -> bool:
    for element in page.elements[root_index + 1 :]:
        current: int | None = element["parent"]
        inside = False
        while current is not None:
            if current == root_index:
                inside = True
                break
            current = page.elements[current]["parent"]
        if not inside:
            continue
        if element["tag"] in {"img", "svg"} and (element["attrs"].get("alt") or element["attrs"].get("aria-label")):
            return True
    return False


def evaluate_page(path: Path, packs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    page = PageIndex()
    page.feed(path.read_text(encoding="utf-8"))
    script_text = "\n".join(page.scripts)
    leads: list[dict[str, Any]] = []

    def emit(rule: dict[str, Any], pack: dict[str, Any], element: dict[str, Any] | None, snippet: str) -> None:
        leads.append({
            "rule_id": rule["id"],
            "pack": pack["pack"],
            "pack_origin": pack["origin"],
            "category": rule["category"],
            "severity": rule["severity"],
            "message": rule["message"],
            "citation": rule["citation"],
            "false_positive_guard": rule["false_positive_guard"],
            "confirmation_required": True,
            "file": path.name,
            "line": element["line"] if element else None,
            "sample_hint": page.sample_hint(element["index"]) if element else None,
            "snippet": snippet[:120],
        })

    for pack in packs:
        for rule in pack["rules"]:
            predicate = rule["predicate"]
            kind = predicate["type"]
            if kind == "element_pattern":
                pattern = re.compile(predicate["value_pattern"], re.IGNORECASE)
                for element in page.elements:
                    if element["tag"] not in predicate.get("tags", [element["tag"]]):
                        continue
                    value = element["attrs"].get(predicate["attr"])
                    if value is None:
                        continue
                    if pattern.fullmatch(value):
                        emit(rule, pack, element, f'<{element["tag"]} {predicate["attr"]}="{value}">')
            elif kind == "text_pattern":
                pattern = re.compile(predicate["pattern"], re.IGNORECASE)
                scope_tags = set(predicate.get("scope_tags", TEXT_BLOCK_TAGS))
                for element in page.elements:
                    if element["tag"] not in scope_tags or not element["text"]:
                        continue
                    text = " ".join(element["text"])
                    match = pattern.search(text)
                    if match:
                        start = max(match.start() - 40, 0)
                        emit(rule, pack, element, text[start:match.end() + 40])
            elif kind == "unlabeled_input":
                for element in page.elements:
                    if element["tag"] != "input":
                        continue
                    if element["attrs"].get("type", "").lower() not in TEXT_INPUT_TYPES:
                        continue
                    attrs = element["attrs"]
                    if attrs.get("aria-label") or attrs.get("aria-labelledby"):
                        continue
                    if attrs.get("id") and attrs["id"] in page.label_for:
                        continue
                    if page.has_ancestor(element["index"], "label"):
                        continue
                    emit(rule, pack, element, f'<input placeholder="{attrs.get("placeholder", "")}">')
            elif kind == "interactive_non_semantic":
                for element in page.elements:
                    if element["tag"] not in {"div", "span"}:
                        continue
                    attrs = element["attrs"]
                    if attrs.get("role") or attrs.get("tabindex"):
                        continue
                    wired = "onclick" in attrs
                    identifier = attrs.get("id")
                    if not wired and identifier:
                        wired = bool(re.search(
                            r"getElementById\(\s*['\"]" + re.escape(identifier) + r"['\"]\s*\)\s*\.\s*addEventListener\(\s*['\"]click",
                            script_text,
                        ))
                    if wired:
                        emit(rule, pack, element, f'<{element["tag"]} id="{identifier or ""}"> wired as a click control')
            elif kind == "element_missing_attrs":
                for element in page.elements:
                    if element["tag"] not in predicate["tags"]:
                        continue
                    required_present = predicate.get("require_attr")
                    if required_present and required_present not in element["attrs"]:
                        continue
                    if any(attr in element["attrs"] for attr in predicate["absent_attrs"]):
                        continue
                    emit(rule, pack, element, f'<{element["tag"]}> missing {"/".join(predicate["absent_attrs"])}')
            elif kind == "document_missing":
                matches = [e for e in page.elements if e["tag"] == predicate["tag"]
                           and (not predicate.get("where_attr")
                                or re.fullmatch(predicate.get("where_pattern", ".*"),
                                                e["attrs"].get(predicate["where_attr"], "") or ""))
                           and (not predicate.get("attr") or e["attrs"].get(predicate["attr"]))]
                if not matches:
                    emit(rule, pack, None, f'no <{predicate["tag"]}' + (f' {predicate["attr"]}=…>' if predicate.get("attr") else ">"))
            elif kind == "blocking_script":
                for element in page.elements:
                    if element["tag"] != "script" or "src" not in element["attrs"]:
                        continue
                    attrs = element["attrs"]
                    if "defer" in attrs or "async" in attrs or attrs.get("type") == "module":
                        continue
                    if page.has_ancestor(element["index"], "head"):
                        emit(rule, pack, element, f'blocking <script src="{attrs["src"][:60]}"> in head')
            elif kind == "empty_interactive":
                for element in page.elements:
                    if element["tag"] not in {"button", "a"}:
                        continue
                    attrs = element["attrs"]
                    if attrs.get("aria-label") or attrs.get("aria-labelledby") or attrs.get("title"):
                        continue
                    subtree = collect_subtree_text(page, element["index"])
                    if subtree.strip():
                        continue
                    if subtree_has_named_image(page, element["index"]):
                        continue
                    emit(rule, pack, element, f'<{element["tag"]}> with no accessible text')
            elif kind == "duplicate_id":
                seen_ids: dict[str, int] = {}
                for element in page.elements:
                    identifier = element["attrs"].get("id")
                    if not identifier:
                        continue
                    seen_ids[identifier] = seen_ids.get(identifier, 0) + 1
                    if seen_ids[identifier] == 2:
                        emit(rule, pack, element, f'id="{identifier}" appears more than once')
            elif kind == "script_pattern":
                if re.search(predicate["pattern"], script_text):
                    emit(rule, pack, None, f'page scripts match /{predicate["pattern"][:60]}/')
            elif kind == "state_group_without_address":
                group_attr = predicate.get("group_attr", "data-view")
                members = [e for e in page.elements if e["tag"] == "button" and group_attr in e["attrs"]]
                if len(members) >= predicate.get("min_count", 2):
                    if not re.search(r"pushState|replaceState|location\.hash|history\.", script_text):
                        names = ", ".join(m["attrs"][group_attr] for m in members)
                        emit(rule, pack, members[0], f"{len(members)} views ({names}) with no URL state")
    return leads


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", type=Path)
    parser.add_argument("--rules-dir", type=Path, default=DEFAULT_RULES_DIR)
    parser.add_argument("--pack", type=Path, action="append", default=[])
    parser.add_argument("--min-level", choices=SEVERITIES, default="suggestion")
    parser.add_argument("--check", action="store_true", help="validate packs and exit")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        packs = load_packs(args.rules_dir, args.pack)
        validate_packs(packs)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2
    if args.check:
        rule_count = sum(len(pack["rules"]) for pack in packs)
        print(f"PASS: {len(packs)} rule packs and {rule_count} rules are valid, cited, and canonical")
        return 0
    if not args.files:
        print("FAIL: no input files (or use --check)", file=sys.stderr)
        return 2

    checklist = [
        {"rule_id": r["id"], "category": r["category"], "pack": p["pack"],
         "instruction": r["predicate"].get("instruction", r["message"]),
         "citation": r["citation"], "false_positive_guard": r["false_positive_guard"]}
        for p in packs for r in p["rules"] if r["predicate"]["type"] == "operated_check"
    ]
    floor = SEVERITIES.index(args.min_level)
    leads: list[dict[str, Any]] = []
    for path in args.files:
        leads.extend(evaluate_page(path, packs))
    leads = [l for l in leads if l["rule_id"] not in {c["rule_id"] for c in checklist}]
    leads = [lead for lead in leads if SEVERITIES.index(lead["severity"]) >= floor]
    by_rule: dict[str, int] = {}
    for lead in leads:
        by_rule[lead["rule_id"]] = by_rule.get(lead["rule_id"], 0) + 1
    feedback = {
        "next_actions": [
            (f"Confirm or clear {count}× {rule_id} by operating the surface; "
             f"guard: {next(l['false_positive_guard'] for l in leads if l['rule_id'] == rule_id)}")
            for rule_id, count in sorted(by_rule.items())
        ] + ([f"Run the {len(checklist)}-item operated walkthrough checklist during the task pass."] if checklist else []),
        "summary": f"{len(leads)} static leads across {len(set(l['file'] for l in leads))} file(s); "
                   f"{len(checklist)} operated checks queued for the walkthrough.",
    }
    payload = {
        "schema_version": "1.0",
        "tool": "rule_engine",
        "min_alert_level": args.min_level,
        "packs": [{"pack": p["pack"], "origin": p["origin"], "rules": len(p["rules"])} for p in packs],
        "lead_count": len(leads),
        "walkthrough_checklist": checklist,
        "session_feedback": feedback,
        "leads": leads,
        "authorship_assessment": "not_performed",
        "note": "Leads are not findings. Confirm or clear each lead by operating the interface before reporting.",
    }
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
        print(f"PASS: {len(leads)} leads written to {args.output}")
        print(f"FEEDBACK: {feedback['summary']}")
        for action in feedback["next_actions"][:8]:
            print(f"  -> {action[:150]}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
