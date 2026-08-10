# Rule packs

Deterministic lead rules live as data in `schema/rules/*.json`. The engine
(`scripts/rule_engine.py`) evaluates every pack against HTML and emits leads.
A lead is never a finding: confirm or clear each one by operating the interface,
then record the engine output as an `analysis_receipt` evidence asset and cite it
from the confirmed finding or the cleared suspicion.

## Run

```sh
python3 scripts/rule_engine.py --check                       # validate packs only
python3 scripts/rule_engine.py page.html --output leads.json # emit leads
python3 scripts/rule_engine.py page.html --min-level warning # filter by severity
python3 scripts/rule_engine.py page.html --pack my-pack.json # add a user pack
```

## Rule format

Each rule: `id` (UPPER-KEBAB, globally unique), `category` (canonical key),
`severity` (`suggestion` → `warning` → `error`), `message`, `citation`
(`principles/PRINCIPLES.md §N`; the section must exist), `false_positive_guard`
(when the matched pattern is legitimate), and a `predicate`.

Predicate types: `element_pattern` (tag + attribute regex), `text_pattern`
(reader-visible block text regex), `unlabeled_input`, `interactive_non_semantic`,
`state_group_without_address`. New predicate types are engine changes and need
regression coverage in `scripts/test_rule_engine.py`.

## Severity ratchet

New rules ship at `suggestion` and are promoted only on evidence: a rule earns
`warning` or `error` after it demonstrates hits on planted defects and zero guard
false positives against `evals/web-fixtures/` (or new fixtures added with it).
Demotion needs no ceremony.

## User packs from supplied sources

A user may supply a transcript, article, or video (`scripts/intake.py` fetches
YouTube captions). Distill it into rules — never reproduce source text:

1. Extract candidate principles the source actually asserts.
2. For each operationalizable principle, write a rule with a narrow predicate and
   an explicit `false_positive_guard`.
3. Set `origin: "user"` and fill `source_attribution` (`title`, `creator`,
   `locator`); user packs fail validation without attribution. Credit flows into
   every lead the rule produces.
4. Baseline packs cite the reconciled corpus; user-pack citations still point at
   the corpus section that covers the concern. If none does, the principle is a
   candidate for corpus intake first.
5. Validate with `--check`, then run against the known-answer fixtures before
   relying on the pack.

Rule packs measure repeatable surface signals. They never assess authorship, and
the engine records `authorship_assessment: not_performed` in every output.
