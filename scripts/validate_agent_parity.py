#!/usr/bin/env python3
"""Verify Scruffy source parity across two installed skill trees; not behavior."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from blind_protocol import tree_sha256


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first", type=Path, help="First installed Scruffy directory")
    parser.add_argument("second", type=Path, help="Second installed Scruffy directory")
    args = parser.parse_args(argv)

    for label, path in (("first", args.first), ("second", args.second)):
        if not path.is_dir() or not (path / "SKILL.md").is_file():
            print(f"FAIL: {label} path is not a Scruffy skill directory: {path}", file=sys.stderr)
            return 2
    first_hash = tree_sha256(args.first)
    second_hash = tree_sha256(args.second)
    if first_hash != second_hash:
        print(f"FAIL: skill-tree hashes differ: {first_hash} != {second_hash}", file=sys.stderr)
        return 1
    same_source = args.first.resolve() == args.second.resolve()
    print(f"PASS: identical skill-tree hash {first_hash}; same_source={str(same_source).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
