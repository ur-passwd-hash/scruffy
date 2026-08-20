#!/usr/bin/env python3
"""
Source-ledger validator: proves every ingested source is actually leveraged.

Scruffy's `/transcripts/` folder is gitignored working material (see .gitignore
and principles/SOURCES.md "Intake pipeline"). That is deliberate -- raw creator
transcripts are not redistributed -- but it means the repo has historically had
NO durable record of which videos were ingested. When a transcript folder is
cleared or a machine changes, the evidence behind a cited rule disappears while
the citation survives, and nothing detects it.

principles/SOURCE_LEDGER.md is that durable record. This script enforces it.

Failure states (exit 1):
  ORPHAN_CITATION   PRINCIPLES.md cites a video_id absent from the ledger.
  UNDISTILLED       Ledger row is `ingested` but contributes zero citations.
                    This is the "archived but never leveraged" state -- the
                    whole reason this validator exists.
  UNTRACKED_LOCAL   A transcript exists on disk with no ledger row.
  BAD_STATUS        Ledger row has a status outside the allowed set.

Warning states (exit 0 unless --strict):
  EVIDENCE_LOST     Row is cited and distilled, but no transcript survives
                    locally and no vault copy is recorded. The rule stands on
                    an unverifiable citation.

Two modes, because this file ships to plugin users who have no corpus:

  consumer  No transcripts/ and no --vault-dir. Ledger checks still run -- they
            read only committed files and are meaningful anywhere. Evidence
            checks are reported SKIPPED, never as a pass.
  corpus    Transcripts present. Everything runs.

A check that did not run is never reported as a pass. Users should not have to
guess whether PASS means "verified" or "did not look".

Usage:
  python3 scripts/validate_sources.py
  python3 scripts/validate_sources.py --strict          # warnings also fail
  python3 scripts/validate_sources.py --json
  python3 scripts/validate_sources.py --backfill        # emit ledger rows from
                                                        # observed citations
  python3 scripts/validate_sources.py --vault-dir ~/Documents/Misc/"The Beginning"

Stdlib only, matching the rest of scripts/.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PRINCIPLES = BASE / "principles" / "PRINCIPLES.md"
LEDGER = BASE / "principles" / "SOURCE_LEDGER.md"
TRANSCRIPTS = BASE / "transcripts"

# A YouTube id is exactly 11 chars of [A-Za-z0-9_-]. Several non-video citation
# keys used in PRINCIPLES.md collide with that shape, so they are excluded by
# name. Keys are drawn from the "Cited as" column of principles/SOURCES.md.
NON_VIDEO_TOKENS = {
    # standards / official guidance
    "WCAG22", "W3C-EVAL", "WAI-APG", "WAI-TABS", "WAI-ALT",
    "W3C-READING", "GOVUK-CLEAR", "MDN-FONTDISPLAY",
    # performance guidance
    "WEBDEV-LCP", "WEBDEV-CLS", "WEBDEV-INP", "WEBDEV-RESPIMG", "WEBDEV-3P",
    # research papers
    "SADASIVAN23", "LIANG23", "MAGE24", "ZANOTTO25", "COHESENTIA23", "QUDSIM25",
    # books / published bodies of work
    "RUI", "Butterick", "Tufte", "LawsUX",
    # primary statements & community corpora
    "HANKGREEN26", "REDDIT-WRITING26",
}

VIDEO_ID = re.compile(r"[A-Za-z0-9_-]{11}")
# An id followed by whitespace or a closing bracket. Deliberately permissive so
# it covers every citation shape in PRINCIPLES.md: bare `[id]`, single stamp
# `[id 3:24]`, and en-dash or hyphen ranges `[id 2:49-4:19]`. An earlier version
# anchored on `\]` right after the stamp and silently missed every ranged
# citation - which is most of them. Matches validate_corpus.py's VIDEO_ID shape.
CITATION = re.compile(r"\[([A-Za-z0-9_-]{11})(?=[\s\]])")
SECTION = re.compile(r"^##\s+(\d+)\.\s+(.*?)\s*$")
ALLOWED_STATUS = {"distilled", "ingested", "queued", "rejected"}


def parse_principles(path: Path) -> dict[str, dict]:
    """video_id -> {count, sections:[(num, title)], lines:[int]}"""
    if not path.exists():
        sys.exit(f"missing {path}")
    found: dict[str, dict] = {}
    sec_num, sec_title = "0", "(preamble)"
    for lineno, line in enumerate(path.read_text().splitlines(), 1):
        m = SECTION.match(line)
        if m:
            sec_num, sec_title = m.group(1), m.group(2)
            continue
        for vid in CITATION.findall(line):
            if vid in NON_VIDEO_TOKENS:
                continue
            rec = found.setdefault(vid, {"count": 0, "sections": [], "lines": []})
            rec["count"] += 1
            rec["lines"].append(lineno)
            key = (sec_num, sec_title)
            if key not in rec["sections"]:
                rec["sections"].append(key)
    return found


def parse_ledger(path: Path) -> dict[str, dict]:
    """Parse the markdown table. Columns: video_id | creator | status | evidence | notes"""
    if not path.exists():
        return {}
    rows: dict[str, dict] = {}
    for line in path.read_text().splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        raw_id = cells[0].strip("`")
        if not VIDEO_ID.fullmatch(raw_id) or raw_id in NON_VIDEO_TOKENS:
            continue  # header, separator, or prose row
        rows[raw_id] = {
            "creator": cells[1],
            "status": cells[2].lower().strip("*_ "),
            "evidence": cells[3],
            "notes": cells[4] if len(cells) > 4 else "",
        }
    return rows


def local_transcripts(path: Path) -> dict[str, str]:
    if not path.is_dir():
        return {}
    out = {}
    for f in sorted(path.glob("*.md")):
        vid = f.name.split("_", 1)[0]
        # ids beginning with "_" survive the split as an empty first field
        if not VIDEO_ID.fullmatch(vid):
            vid = f.name[:11]
        if VIDEO_ID.fullmatch(vid):
            out[vid] = f.name
    return out


def vault_transcripts(vault: Path | None) -> set[str]:
    if not vault:
        return set()
    d = vault / "sources" / "transcripts"
    if not d.is_dir():
        return set()
    ids = set()
    for f in d.glob("*.md"):
        for tok in f.stem.split("_"):
            if VIDEO_ID.fullmatch(tok) and tok not in NON_VIDEO_TOKENS:
                ids.add(tok)
    return ids


def backfill(cited: dict, ledger: dict, disk: dict) -> str:
    lines = []
    for vid in sorted(set(cited) | set(disk), key=str.lower):
        if vid in ledger:
            continue
        c = cited.get(vid, {"count": 0, "sections": []})
        secs = ", ".join(f"§{n}" for n, _ in c["sections"]) or "—"
        status = "distilled" if c["count"] else "ingested"
        ev = "local transcript" if vid in disk else "citation only (transcript lost)"
        lines.append(f"| `{vid}` | TODO | {status} | {ev} | {secs}, {c['count']} citations |")
    return "\n".join(lines) or "(nothing to backfill)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="warnings fail too")
    ap.add_argument("--backfill", action="store_true")
    ap.add_argument("--vault-dir", type=Path, default=None)
    args = ap.parse_args()

    cited = parse_principles(PRINCIPLES)
    ledger = parse_ledger(LEDGER)
    disk = local_transcripts(TRANSCRIPTS)
    vault = vault_transcripts(args.vault_dir.expanduser() if args.vault_dir else None)

    if args.backfill:
        print(backfill(cited, ledger, disk))
        return 0

    # Two check families with different audiences:
    #
    #   Ledger checks   read only committed files (SOURCE_LEDGER.md, PRINCIPLES.md).
    #                   They are meaningful in ANY checkout, including a plugin
    #                   install, and always run.
    #   Evidence checks need the gitignored transcripts/ folder or a vault copy.
    #                   They are maintainer-only. In a consumer checkout there is
    #                   nothing to check, so they are reported SKIPPED.
    #
    # A check that did not run must never be reported as a pass. validate_corpus.py
    # currently prints PASS after skipping its transcript-dependent checks; do not
    # copy that behaviour here.
    corpus_mode = bool(disk or vault)

    failures, warnings = [], []

    for vid, rec in sorted(cited.items()):
        if vid not in ledger:
            secs = ", ".join(f"§{n}" for n, _ in rec["sections"])
            failures.append(("ORPHAN_CITATION", vid,
                             f"cited {rec['count']}x in {secs} but absent from SOURCE_LEDGER.md"))

    for vid, row in sorted(ledger.items()):
        if row["status"] not in ALLOWED_STATUS:
            failures.append(("BAD_STATUS", vid, f"status {row['status']!r} not in {sorted(ALLOWED_STATUS)}"))
            continue
        n = cited.get(vid, {}).get("count", 0)
        if row["status"] == "ingested" and n == 0:
            failures.append(("UNDISTILLED", vid,
                             "ingested but contributes zero PRINCIPLES citations "
                             "- source is archived, not leveraged"))
        if row["status"] == "distilled" and n == 0:
            failures.append(("UNDISTILLED", vid,
                             "marked distilled but no citation carries its id"))
        if corpus_mode and n and vid not in disk and vid not in vault:
            warnings.append(("EVIDENCE_LOST", vid,
                             f"{n} citations rest on a transcript that exists neither locally nor in the vault"))

    if corpus_mode:
        for vid, fname in sorted(disk.items()):
            if vid not in ledger:
                failures.append(("UNTRACKED_LOCAL", vid, f"transcript {fname} has no ledger row"))

    skipped = [] if corpus_mode else [
        "EVIDENCE_LOST", "UNTRACKED_LOCAL",
    ]

    report = {
        "mode": "corpus" if corpus_mode else "consumer",
        "cited_ids": len(cited),
        "ledger_rows": len(ledger),
        "local_transcripts": len(disk),
        "vault_transcripts": len(vault),
        "checks_skipped": skipped,
        "failures": [{"code": c, "video_id": v, "detail": d} for c, v, d in failures],
        "warnings": [{"code": c, "video_id": v, "detail": d} for c, v, d in warnings],
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"mode: {report['mode']}  cited ids: {len(cited)}  ledger rows: {len(ledger)}  "
              f"local transcripts: {len(disk)}  vault transcripts: {len(vault)}")
        for c, v, d in failures:
            print(f"FAIL  {c:<16} {v}  {d}")
        for c, v, d in warnings:
            print(f"WARN  {c:<16} {v}  {d}")
        if skipped:
            print(f"SKIP  {', '.join(skipped)} - no transcripts present. "
                  "This is a consumer checkout; evidence retention was NOT verified.")
        if not failures and not warnings:
            print("PASS  ledger checks: every ingested source is cited; every citation is tracked.")
        elif not failures:
            print(f"PASS  ledger checks, with {len(warnings)} warning(s).")

    return 1 if failures or (args.strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
