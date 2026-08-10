#!/usr/bin/env python3
"""Generate Claude Code's discovery wrapper from the canonical root skill."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "SKILL.md"
ADAPTER = ROOT / "skills" / "scruffy" / "SKILL.md"


def frontmatter(text: str) -> tuple[str, str]:
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise ValueError("canonical SKILL.md frontmatter is missing")
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator:
            values[key.strip()] = value.strip()
    if set(values) != {"name", "description"}:
        raise ValueError("canonical frontmatter must contain only name and description")
    return values["name"], values["description"]


def render() -> str:
    name, description = frontmatter(CANONICAL.read_text(encoding="utf-8"))
    return f"""---
name: {name}
description: {description}
---

# Scruffy Claude plugin adapter

Read and follow [the canonical Scruffy skill](../../SKILL.md) completely before taking task actions. That root file is the sole runtime contract. Resolve its linked references from the repository root. This generated adapter exists only because Claude Code discovers plugin skills under `skills/<name>/`; do not add audit rules here.
"""


def check() -> list[str]:
    if not ADAPTER.is_file():
        return ["Claude plugin adapter is missing"]
    return [] if ADAPTER.read_text(encoding="utf-8") == render() else ["Claude plugin adapter is stale"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.write:
            ADAPTER.parent.mkdir(parents=True, exist_ok=True)
            ADAPTER.write_text(render(), encoding="utf-8")
            print("PASS: Claude plugin adapter updated")
            return 0
        failures = check()
        if failures:
            for failure in failures:
                print(f"FAIL: {failure}", file=sys.stderr)
            return 1
        print("PASS: Claude plugin adapter matches the canonical skill")
        return 0
    except (OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
