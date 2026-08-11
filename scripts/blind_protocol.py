#!/usr/bin/env python3
"""Prepare, freeze, and verify contamination-resistant blind audit artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
IGNORED_TREE_NAMES = {".git", "__pycache__", ".DS_Store"}


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_sha256(root: Path) -> str:
    if not root.is_dir():
        raise ValueError(f"skill root is not a directory: {root}")
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in IGNORED_TREE_NAMES for part in relative.parts) or not path.is_file():
            continue
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(sha256_file(path)))
    return digest.hexdigest()


def input_record(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    if not resolved.is_file():
        raise ValueError(f"allowed input is not a file: {path}")
    return {
        "path": str(resolved),
        "sha256": sha256_file(resolved),
        "bytes": resolved.stat().st_size,
    }


def forbidden_markers(paths: list[Path], explicit: list[str]) -> list[str]:
    markers = {marker for marker in explicit if marker}
    for path in paths:
        markers.add(str(path.resolve()))
        markers.add(path.name)
    return sorted(markers)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def prepare(args: argparse.Namespace) -> int:
    prompt = args.prompt_file.read_bytes()
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "blind_test_id": args.test_id or str(uuid.uuid4()),
        "phase": "blind_discovery",
        "target": args.target,
        "agent": args.agent,
        "created_at": timestamp(),
        "prompt": {"path": str(args.prompt_file.resolve()), "sha256": sha256_bytes(prompt)},
        "skill": {"path": str(args.skill_root.resolve()), "tree_sha256": tree_sha256(args.skill_root)},
        "allowed_inputs": [input_record(path) for path in args.allow],
        "forbidden_inputs": [str(path.resolve()) for path in args.forbid],
        "forbidden_markers": forbidden_markers(args.forbid, args.forbid_marker),
        "integrity_rules": {
            "no_resumed_session": True,
            "temporary_candidate_ids_only": True,
            "freeze_before_reveal": True,
        },
    }
    write_json(args.output, manifest)
    print(f"PASS: prepared {args.output} ({manifest['blind_test_id']})")
    return 0


def validate_discovery_shape(data: dict[str, Any]) -> None:
    if data.get("phase") != "blind_discovery":
        raise ValueError("discovery phase must be blind_discovery")
    if data.get("authorship_assessment") not in {None, "not_performed"}:
        raise ValueError("blind sentence audit must not make an authorship assessment")
    candidates = data.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("discovery must contain a candidates list")
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            raise ValueError(f"candidate {index} must be an object")
        candidate_id = candidate.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id.startswith("CAND-"):
            raise ValueError(f"candidate {index} must use a temporary CAND- ID")


def detect_contamination(manifest: dict[str, Any], discovery_text: str) -> list[str]:
    """Flag forbidden markers that appear as whole tokens in the discovery text.

    Token boundaries prevent innocent-substring false positives (marker "keys"
    must not match "monkeys") while still flagging any real mention of a
    forbidden path or file name, which remains conservative fail-closed
    behavior: a blind discovery has no reason to name its forbidden inputs.
    """
    lowered = discovery_text.lower()
    found = []
    for marker in manifest.get("forbidden_markers", []):
        if not (isinstance(marker, str) and marker):
            continue
        pattern = r"(?<![0-9a-z_])" + re.escape(marker.lower()) + r"(?![0-9a-z_])"
        if re.search(pattern, lowered):
            found.append(marker)
    return found


def freeze(args: argparse.Namespace) -> int:
    manifest = read_json(args.manifest)
    discovery_text = args.discovery.read_text(encoding="utf-8")
    discovery = json.loads(discovery_text)
    if not isinstance(discovery, dict):
        raise ValueError("discovery JSON root must be an object")
    validate_discovery_shape(discovery)
    contamination = detect_contamination(manifest, discovery_text)
    if contamination:
        raise ValueError(f"discovery contains forbidden marker(s): {contamination}")
    freeze_record = {
        "schema_version": SCHEMA_VERSION,
        "blind_test_id": manifest.get("blind_test_id"),
        "phase": "blind_frozen",
        "frozen_at": timestamp(),
        "manifest": {"path": str(args.manifest.resolve()), "sha256": sha256_file(args.manifest)},
        "discovery": {"path": str(args.discovery.resolve()), "sha256": sha256_file(args.discovery)},
        "contamination_status": "verified_no_forbidden_markers",
    }
    write_json(args.output, freeze_record)
    print(f"PASS: froze {args.discovery} as {args.output}")
    return 0


def verify(args: argparse.Namespace) -> int:
    manifest = read_json(args.manifest)
    freeze_record = read_json(args.freeze)
    problems: list[str] = []
    if manifest.get("blind_test_id") != freeze_record.get("blind_test_id"):
        problems.append("blind_test_id mismatch")
    expected_manifest = freeze_record.get("manifest", {}).get("sha256")
    if expected_manifest != sha256_file(args.manifest):
        problems.append("manifest changed after freeze")
    discovery_path = Path(freeze_record.get("discovery", {}).get("path", ""))
    if not discovery_path.is_file():
        problems.append("frozen discovery is missing")
    else:
        expected_discovery = freeze_record.get("discovery", {}).get("sha256")
        if expected_discovery != sha256_file(discovery_path):
            problems.append("discovery changed after freeze")
        contamination = detect_contamination(manifest, discovery_path.read_text(encoding="utf-8"))
        if contamination:
            problems.append(f"forbidden markers present: {contamination}")
    for record in manifest.get("allowed_inputs", []):
        path = Path(record.get("path", ""))
        if not path.is_file() or sha256_file(path) != record.get("sha256"):
            problems.append(f"allowed input changed or disappeared: {path}")
    skill_path = Path(manifest.get("skill", {}).get("path", ""))
    if not skill_path.is_dir() or tree_sha256(skill_path) != manifest.get("skill", {}).get("tree_sha256"):
        problems.append("skill tree changed after manifest creation")
    prompt_path = Path(manifest.get("prompt", {}).get("path", ""))
    if not prompt_path.is_file() or sha256_file(prompt_path) != manifest.get("prompt", {}).get("sha256"):
        problems.append("prompt changed after manifest creation")
    if problems:
        raise ValueError("; ".join(problems))
    print(f"PASS: verified blind run {manifest.get('blind_test_id')}")
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    prepare_parser = commands.add_parser("prepare")
    prepare_parser.add_argument("--target", required=True)
    prepare_parser.add_argument("--agent", required=True)
    prepare_parser.add_argument("--prompt-file", type=Path, required=True)
    prepare_parser.add_argument("--skill-root", type=Path, required=True)
    prepare_parser.add_argument("--allow", type=Path, action="append", default=[], required=True)
    prepare_parser.add_argument("--forbid", type=Path, action="append", default=[])
    prepare_parser.add_argument("--forbid-marker", action="append", default=[])
    prepare_parser.add_argument("--test-id")
    prepare_parser.add_argument("--output", type=Path, required=True)
    prepare_parser.set_defaults(handler=prepare)

    freeze_parser = commands.add_parser("freeze")
    freeze_parser.add_argument("--manifest", type=Path, required=True)
    freeze_parser.add_argument("--discovery", type=Path, required=True)
    freeze_parser.add_argument("--output", type=Path, required=True)
    freeze_parser.set_defaults(handler=freeze)

    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--manifest", type=Path, required=True)
    verify_parser.add_argument("--freeze", type=Path, required=True)
    verify_parser.set_defaults(handler=verify)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return args.handler(args)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
