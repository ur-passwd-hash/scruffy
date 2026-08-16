# Scruffy repair-workflow maintainer contract

This directory contains Scruffy's compatibility repair runtime. It consumes
Scruffy audit output and is not a separately branded product. This file governs
work on the repair runtime itself. Claude Code imports it through root `CLAUDE.md`.

## Start here

1. Classify the request as `USE` (run Scruffy repair against a Scruffy audit),
   `MAINTAIN` (change this repository), or `SCAFFOLD` (extend the skeleton).
2. Read root `SKILL.md` and `schema/interop.json` before changing runtime
   behavior.
3. State available capabilities and checks that cannot be run. Never invent
   browser, screenshot, source, test, or deployment proof.

## The line with Scruffy

Scruffy owns the audit contract; the repair runtime is a **read-only consumer**. Never edit
or fork Scruffy's schema from this repo. If the handoff needs a schema change,
that change is proposed to Scruffy, not made here. The repair runtime's only schema is the
consumer compatibility key in `schema/interop.json`.

The repair runtime never produces findings, scores authorship, decides approvals, or marks
an item `fixed`/`cleared`. Those are Scruffy audit responsibilities. A repair change that blurs this
line is out of contract.

## Source-of-truth map

| Concern | Canonical source |
|---|---|
| Runtime method and trigger | `SKILL.md` |
| Scruffy interop / compatibility key | `schema/interop.json` |
| Handoff protocol (human-readable) | `references/scruffy-handoff.md` |
| Product truth | `PRODUCT.md` |
| Claude distribution | `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` |
| Codex metadata | `agents/openai.yaml` |

## Improvement protocol

1. Reproduce the need from a real Scruffy audit's raw output, not from memory.
2. Keep the smallest canonical edit. Regenerate any projections; never patch a
   generated file by hand.
3. Preserve the authority gate, the approval gate, the dependency order, and the
   "re-audit evidence clears, implementation does not" rule unless the user explicitly changes the
   product contract.
4. When the interop versions change, update `schema/interop.json` and
   `references/scruffy-handoff.md` together, and confirm against Scruffy's
   current `references/output-schema.md`.

## Validation

Run the dependency-free suite before committing:

```sh
python3 scripts/test_mop.py
python3 scripts/validate_skill.py
```

`test_mop.py` covers version validation and fail-closed behavior, the authority
and approval gates, dependency/lane ordering, token association, and the handoff's
refusal to self-certify. `validate_skill.py` checks interop shape, distribution
metadata agreement, skill frontmatter, routed references, and that the shipped
fixture still loads, validates, and plans in the expected order. When Claude Code
is installed, also run `claude plugin validate .`.

Before any commit, verify:

```sh
git status --short
git branch --show-current
git config user.email
```

## Definition of done

A change is done only when its canonical owner is clear, the consumer-only line
with Scruffy is intact, `test_mop.py` and `validate_skill.py` pass, unsupported
verification is disclosed, and version metadata and `CHANGELOG.md` agree when
releasing.
