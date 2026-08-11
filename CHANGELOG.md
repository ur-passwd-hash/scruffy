# Changelog

All notable changes to the public Scruffy skill, formerly Anti-Slop, are documented here.

## Unreleased

- Fixed an innocent-substring false positive in the blind-freeze contamination
  scan: forbidden markers now match as whole tokens (marker "keys" no longer
  flags "monkeys"), with a regression covering both the benign and the
  real-mention case in scripts/test_blind_protocol.py. Documented the
  previously implicit blind-discovery JSON shape (top-level candidates /
  cleared_suspicions / checks_not_run lists keyed by sample_id, CAND-NNN ids,
  two-signal minimum) and the do-not-name-forbidden-paths rule in
  references/blind-audit.md. The web-fixtures contamination rule now also
  forbids evals/web-fixtures/runs/, which archives scored past runs (first
  entry: web-fixtures-blind-20260810, 11/12 disposition agreement, blindness
  verified).

- Implemented the first two product bets as reference CLIs: scripts/scan.py
  (B1: URL or file to static leads plus the operated checklist, honesty note
  built in) and scripts/render_onepager.py (B2: shareable broadsheet one-pager
  whose badge asserts process only — audited, revision, registry SHA-256 —
  never quality). Regressions in scripts/test_product_surfaces.py forbid
  fake-score artifacts and verify the embedded hash. Design agents restyle
  these; the contracts and honesty language are canonical.

## 2.5.0 — 2026-08-10

- Added the operated_check rule class: checklist rules with no static executor
  that the engine queues for the task walkthrough (8 starter checks from NN/g and
  Baymard distillations), plus a session_feedback block in engine output — a
  summary and per-rule next actions printed back to the invoking session so the
  lead-to-fix loop closes without opening the JSON. Dogfooded on Scruffy's own
  rendered dashboard: 20 static leads, all cleared by their own recorded guards
  (self-contained reports inline payloads and size figures by CSS by design).
- Added four source-backed baseline packs (30 rules total across 6 packs) and six
  new engine predicate types. Performance statics distilled from web.dev/Lighthouse
  (unsized images, head-blocking scripts, missing viewport, inline megapayloads);
  accessibility statics mapped from axe-core/WCAG with named criteria (missing alt,
  missing lang, empty controls, positive tabindex, duplicate ids); plain-language
  patterns from the public-domain US Federal Plain Language Guidelines and GOV.UK
  style guide; and generator-residue detection of unmodified builder defaults
  (scaffold titles, generator metas, built-with badges, TODO residue, silent empty
  catch blocks) informed by the public tell-catalogs of kill-ai-slop, SlopCop, and
  Slopdar — framed strictly as skipped decisions, never authorship claims. Every
  rule cites a corpus section and carries a false-positive guard; synthetic
  regressions cover each predicate, and all six packs stay silent on the
  known-answer fixture guards.
- Added the cognitive_load sentence-signal family with a cited pack listing
  (schema/sentence-slop-pack.json) covering all fifteen deterministic signals, a
  pack-parity regression so no analyzer code can ship uncited or unguarded, three
  new analyzer detectors (overlong_sentence, clause_pileup, parenthetical_stacking),
  and scripts/lint_report_prose.py, which turns the detector on our own audit
  artifacts. Dashboards gained plain-language section titles and explainers, task
  outcomes moved to the second column, scores sort worst-first, and every registry
  item carries a category chip in its rail.
- Redesigned the dashboard renderer around a docket architecture selected through
  a five-paradigm, five-material design round against real audit data: the masthead
  now leads with the top prioritized finding and a decision count, a stats strip
  carries open/enhancement/strength/cleared/carried counts with the worst category,
  severity chips gain a non-color lamp indicator, evidence figures take framed
  captions, print output becomes a broadsheet with red reserved for high severity,
  and text-containment rules (min-width:0, overflow-wrap:anywhere) prevent long
  hashes and URLs from painting over adjacent content, with a rendering regression.
- Added reference grounding: an optional design-reference search capability
  (reference implementation: Mobbin MCP — `search_screens`, `search_flows`, and
  `search_sections`) plus the user taste overlay restored from the Anti-Slop
  lineage, with precedence rules and popularity/deviation false-positive guards
  in `references/reference-grounding.md`. Absence is disclosed, never a finding.

## 2.4.0 — 2026-08-10

- Enforced four evidence rules that previously existed only as prose. Schema-2.1
  validation now fails closed when an active performance finding lacks a
  runtime_trace or measurement receipt, an active accessibility finding lacks an
  accessibility_observation receipt or a named criterion (for example WCAG 2.4.3),
  an active visual finding carries no rendered evidence (screenshot or
  task_observation), or the capability ledger claims screenshots while the run
  captured no screenshot evidence; captured screenshots likewise contradict a
  not-run screenshot capability. Cleared and legacy schema-2.0 items are exempt,
  preserving falsified-suspicion records and existing registries.
- Renamed the golden reconciliation fixture to evals/continuity/ and anonymized
  its target, prose, and identifiers; the seventeen-record structure, dispositions,
  and regression value are unchanged.
- Score tables now name the canonical slop category beside the score framing
  (for example "Structure slop · Implementation shape"), with a regression, an
  unknown-key fallback guard, and a legacy display-string passthrough guard.
- Added a deterministic rule engine (`scripts/rule_engine.py`) with rules as data
  in `schema/rules/*.json`. Every rule carries a canonical category, a severity on
  the suggestion/warning/error ratchet, a citation into the reconciled principles
  corpus, an explicit false-positive guard, and a narrow predicate. The engine
  emits leads, never findings: every lead requires confirmation by operating the
  interface, and output records `authorship_assessment: not_performed`. Two
  baseline packs ship (interaction/IA/semantic controls and editorial/synthetic
  proof, 11 rules); user packs load with `--pack`, require source attribution, and
  carry credit into every lead. Against the known-answer fixtures the baseline
  packs surface four of six planted defects statically with zero guard false
  positives; the remaining two are operation-only by design.
- Added `evals/web-fixtures/`: three deterministic, self-contained pages with six
  planted defects and six adjacent legitimate patterns across interaction,
  information architecture, copy, visual, and accessibility, plus a hidden
  discrimination key consumed by `scripts/evaluate_blind_outputs.py`. A new
  `scripts/test_web_fixtures.py` suite enforces page/key agreement, determinism,
  self-containment, per-page defect/guard pairing, and the no-authorship boundary.
  Detection quality on these fixtures is now a measured number rather than a claim.
- Known residual: kind-level checks cannot distinguish a static measurement from
  a runtime one; a measurement receipt derived from source alone still satisfies
  the performance predicate. Closing this requires a runtime attribute on
  measurement receipts in a future schema revision.

## 2.3.1 — 2026-08-10

- Added an agent-neutral root `AGENTS.md` maintainer contract and a thin
  `CLAUDE.md` import that turns the checkout into a Claude-priority project
  without duplicating the runtime skill.
- Mapped canonical sources to generated projections and made package validation
  enforce the DRY edit routes, no-authorship boundary, and blind-test separation.
- Added a paste-ready Claude maintenance prompt and completed the documented
  validation suite.

## 2.3.0 — 2026-08-10

- Made **Editorial slop** a first-class public category spanning content strategy, terminology, microcopy, sentence and passage construction, claims, provenance, information sequence, recovery language, and voice while preserving `copy` as the durable compatibility key.
- Replaced drifting layer, category, facet, run-mode, authority, capability, evidence, and editorial-review definitions with two canonical machine-readable manifests and generated documentation projections.
- Added schema-2.1 run receipts, write-authority enforcement, exact capability and score coverage, typed evidence resolution, captured-file checks, and mandatory editorial review receipts.
- Added current-to-legacy revision compatibility, decision migration across supported registry versions, current and legacy report rendering, and regression tests for invalid categories, unauthorized writes, missing evidence, weak sentence predicates, authorship claims, and missing audit coverage.
- Added explicit English language scope to the sentence analyzer; non-English and unknown-language inputs now abstain and require language-competent editorial review.
- Clarified that Claude and Codex share a source-compatible skill but require independent behavioral testing; compatibility is not a claim of identical output.
- Added a generated `skills/scruffy/SKILL.md` discovery adapter so Claude Code plugins expose `/scruffy:scruffy` while root `SKILL.md` remains the single runtime source of truth.

## 2.2.0 — 2026-08-10

- Rebuilt sentence-slop analysis around verified reader-facing prose extraction so README HTML, badges, tables, URLs, and install commands no longer inflate sentence counts or specificity markers.
- Added independent signal families, dependency collapse for duplicated evidence, short-sentence bursts, paragraph-pattern reuse, expanded contrast/scaffold coverage, and stricter passive and phrase-repetition thresholds.
- Made conceptual coherence, sentence portability, discourse purpose, and voice/subtext mandatory human checks; the deterministic analyzer explicitly marks them unscored and still refuses authorship classification.
- Expanded the sentence regression corpus from six to eleven cases, including markup contamination, single-device false positives, paragraph choreography, punchline stacks, and semantic collisions.
- Reconciled the supplied languagejones transcript, Hank Green's primary public statement, current r/WritingWithAI discourse, and coherence/discourse research without promoting community folklore into automatic tells.
- Rewrote the README around the then-current plain-language categories and the exact evidence each category requires; 2.3.0 reconciles that prose into the canonical eight-category taxonomy.

## 2.1.1 — 2026-08-09

- Rewrote the README opening and tagline to say plainly that Scruffy finds, proves, and helps fix AI slop in web apps.
- Defined AI slop as observable product, interaction, copy, accessibility, performance, visual, and implementation failures while preserving the no-authorship boundary.
- Aligned the Claude marketplace, Claude plugin, Codex metadata, and shared skill entrypoint around the same simple product promise.

## 2.1.0 — 2026-08-09

- Added a Claude Code plugin manifest and one-plugin marketplace catalog while retaining the root Agent Skills entrypoint used by Codex and standalone Claude skills.
- Made Claude Code marketplace installation the primary quick start and documented the stable `/scruffy:scruffy`, bare `/scruffy`, and `$scruffy` invocation paths without duplicating runtime instructions.
- Extended package validation to enforce Claude and Codex metadata compatibility and the documented install commands.

## 2.0.0 — 2026-08-09

- Renamed the public skill, invocation, install directory, and repository from Anti-Slop to Scruffy.
- Replaced MOP-1 with an original deadpan interface-janitor mascot, a reusable transparent character model, and a flat transparent README hero showing Scruffy sweeping a field of loose nuts and bolts with a commercial push broom.
- Preserved the internal `anti-slop-*` durable-report and browser-storage namespace so existing audit registries, decisions, and dashboards remain compatible.

## 1.2.0 — 2026-08-09

- Added a research-grounded sentence-slop axis that measures copy-quality leads without classifying AI authorship.
- Added length thresholds, compound finding predicates, explicit non-native and genre false-positive guards, and deterministic standard-library analysis.
- Added six sentence-copy fixtures covering formulaic prose, UI filler, technical passive voice, supplied non-native context, concrete prose, and insufficient samples.
- Added a two-phase blind-audit protocol with allowed/forbidden-input manifests, skill and prompt hashes, frozen discovery digests, contamination rejection, and post-reveal reconciliation.
- Added blind-protocol and sentence-detector regression suites to package validation and CI.
- Documented shared-source installation and direct invocation for both Codex and Claude Code.

## 1.1.0 — 2026-08-08

- Added schema-v2 audit registries with immutable IDs, identity keys, revision lineage, and explicit carry/fix/clear/merge/supersede dispositions.
- Made shortlist limits presentation-only and required all active, resolved, merged, and cleared records in durable reports.
- Added decision migration with retained notes and history.
- Added a self-contained dashboard renderer and validators for registry continuity, decision coverage, required sections, and complete item rendering.
- Added positive and negative durability fixtures plus an executable regression suite.
- Added application-archetype probes for reference/course, SaaS, transactional, forms/settings, data-heavy, collaboration/realtime, media/editor, marketing/static, and hybrid interfaces.
- Reconciled an anonymized course audit as the golden cross-revision test case.

## 1.0.0 — 2026-08-08

- Converted the original Claude-oriented instruction set to the Agent Skills standard.
- Added Codex metadata and explicit/implicit `$anti-slop` invocation support.
- Replaced the monolithic runtime file with progressive-disclosure verification, scoring, and output references.
- Added capability preflight, privacy boundaries, falsification, calibrated severity/confidence, and checks-not-run behavior.
- Made interactive HTML optional with Markdown and JSON fallbacks.
- Added deterministic package and corpus validators plus trigger evaluation fixtures.
- Renamed `tools/` to the conventional `scripts/` directory.
- Added agent-agnostic installation guidance, contributing rules, and CI validation.
- Validated the method against an external public test bed.
