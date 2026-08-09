# Changelog

All notable changes to the public Scruffy skill, formerly Anti-Slop, are documented here.

## 2.1.1 — 2026-08-09

- Rewrote the README opening and tagline to say plainly that Scruffy finds, proves, and helps fix AI slop in web apps.
- Defined AI slop as observable product, interaction, copy, accessibility, performance, visual, and implementation failures while preserving the no-authorship boundary.
- Aligned the Claude marketplace, Claude plugin, Codex metadata, and shared skill entrypoint around the same simple product promise.

## 2.1.0 — 2026-08-09

- Added a Claude Code plugin manifest and one-plugin marketplace catalog while retaining the root Agent Skills entrypoint used by Codex and standalone Claude skills.
- Made Claude Code marketplace installation the primary quick start and documented the stable `/scruffy:scruffy`, bare `/scruffy`, and `$scruffy` invocation paths without duplicating runtime instructions.
- Extended package validation to enforce Claude and Codex metadata parity and the documented install commands.

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
- Reconciled the American Mahjong Course audit as the golden cross-revision test case.

## 1.0.0 — 2026-08-08

- Converted the original Claude-oriented instruction set to the Agent Skills standard.
- Added Codex metadata and explicit/implicit `$anti-slop` invocation support.
- Replaced the monolithic runtime file with progressive-disclosure verification, scoring, and output references.
- Added capability preflight, privacy boundaries, falsification, calibrated severity/confidence, and checks-not-run behavior.
- Made interactive HTML optional with Markdown and JSON fallbacks.
- Added deterministic package and corpus validators plus trigger evaluation fixtures.
- Renamed `tools/` to the conventional `scripts/` directory.
- Added agent-agnostic installation guidance, contributing rules, and CI validation.
- Validated the method against the American Mahjong Course public test bed.
