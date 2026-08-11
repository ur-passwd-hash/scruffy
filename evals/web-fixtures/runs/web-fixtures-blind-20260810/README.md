# Blind run: web-fixtures-blind-20260810

Agent: `claude-fable-5/cowork-scruffy` · Date: 2026-08-10 · Blind status: **verified** (frozen before reveal, no forbidden inputs opened pre-freeze, zero integrity problems).

## Result

**11/12 disposition agreement.** All 6 planted defects discovered (recall 6/6); 5 of 6 legitimate patterns correctly cleared; 1 false positive.

| Sample | Expected | Blind run | Outcome |
|---|---|---|---|
| WF-A-01 | candidate | CAND-001 (interaction) | match |
| WF-A-02 | cleared | cleared | match |
| WF-A-03 | candidate | CAND-002 (information_architecture) | match |
| WF-A-04 | cleared | cleared | match |
| WF-B-01 | candidate | CAND-003 (copy) | match |
| WF-B-02 | cleared | cleared | match |
| WF-B-03 | candidate | CAND-004 (copy vs key's visual) | match (category lens differed) |
| WF-B-04 | cleared | cleared | match |
| WF-C-01 | candidate | CAND-005 (accessibility) | match |
| WF-C-02 | cleared | CAND-006 | **false positive** |
| WF-C-03 | candidate | CAND-007 (interaction) | match |
| WF-C-04 | cleared | cleared | match |

The miss: the run flagged WF-C-02's hardcoded `Saved at 09:30` confirmation (observed at a 22:05 real clock) and non-persistence across reload. Both observations are factually true of the fixture, but the key treats the section as the clean control; the fixed timestamp is deterministic demo data. Recorded at moderate confidence with the innocent reading credited in the frozen discovery.

## Files

- `blind-manifest.json` / `blind-discovery.json` / `blind-freeze.json` — frozen phase-1 artifacts (discovery SHA-256 `555a6a88…`, archived unmodified post-reveal)
- `blind-discovery-evaluator-view.json` — mechanical field projection for `evaluate_blind_outputs.py`, hash-linked to the frozen source; no content changed
- `evaluation.json` — evaluator output (11 matched, 1 mismatch, 0 integrity problems)
- `blind-reconciliation.json` — candidate-by-candidate reveal reconciliation

Method: fixtures copied to a quarantined temp dir, served via `http.server`, operated in headless Chromium (pointer, keyboard, clipboard instrumentation, reload/persistence, computed contrast). Evidence screenshots live outside the repo with the original run artifacts.

Process note for future runs: the evaluator requires top-level `candidates` / `cleared_suspicions` / `checks_not_run` lists keyed by `sample_id`, and `blind_protocol.py`'s contamination scan matches forbidden markers as bare substrings (an innocent prose mention of a marker word flags the file). Neither is documented in `references/blind-audit.md`.
