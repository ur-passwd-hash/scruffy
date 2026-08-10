# README editorial-slop dogfood — 2026-08-10

Target: `README.md`

Target SHA-256: `99ce16d0d58ea09fe19af32f297a1fe31b3ffedd7649c3ad36ba664cbf5700ed`

Command:

```sh
python3 scripts/analyze_sentence_slop.py README.md --mode prose --language en
```

This is an editorial-quality review. It makes no authorship assessment. The
sentence analyzer supplies one evidence receipt; it does not clear content
strategy, terminology, claims, provenance, information sequence, recovery
language, or voice by itself.

## Reconciliation with blind finding AS-04

The earlier analyzer treated README HTML, badge markup, tables, headings, URLs,
and install commands as prose. Its baseline run reported 2,318 words, 150
sentences, and 252 “concrete anchors.” That contaminated sentence segmentation
and specificity evidence.

The release-2.3.1 dogfood run reported:

- analyzer schema 1.2 with verified `en` scope and `supported` language status
- 2,948 source words
- 1,484 analyzed reader-facing words
- 1,464 excluded markup/code words
- 122 analyzed sentences
- 20 fenced code blocks, 18 table rows, 26 headings, 5 HTML images, and 35
  inline-code spans excluded
- 86 specificity markers after extraction
- one rhythm-family review lead: three opening phrases each appeared twice
- one independent signal family, so the compound predicate remained false and
  the README was not finding-eligible
- manual passage review required

Disposition: **AS-04 fixed and regression-covered.** Automated surface measures
are clear for this README. That result does not clear the required manual pass.

## Manual passage checks

### Conceptual coherence — clear

The janitor/sweeping metaphor stays confined to the brand frame. “Interface
janitor,” “slop,” and the mascot image share one cleaning model. Local jokes such
as “screenshot astrology” and “card soup” do not carry product claims or combine
in ways that obscure the method. The eight category definitions remain literal
and operational.

### Sentence portability — clear

The opening names Scruffy, web apps, Claude and Codex, accepted inputs, live
operation, evidence, reports, and fixes. The category descriptions name distinct
failure modes and proof requirements. A few general claims, such as the method
being evidence-first, are immediately supported by specific workflow rules.
They do not stand as portable promotional filler.

### Discourse purpose — clear

The sequence has distinct jobs: plain promise, deliverables, quick starts,
eight-category map, evidence discipline, modes, installation, maintainer setup,
repository anatomy, validation, repeat-audit durability, corpus growth, and
boundaries. The analyzer found no repeated non-plain paragraph signature. Its
three duplicated sentence openings—“Editorial review,” “Do not,” and “No
claim”—occur in separated explanatory or boundary statements with different
objects. Parallel wording improves recognition there and creates no reader or
task consequence. The category table likewise repeats a comparison structure
to support scanning.

### Voice and subtext — clear

The voice is direct, slightly irreverent, and consistent with the Scruffy
janitor character. The copy avoids pretending the tool can identify an author.
Stable internal keys such as `backend_shape` and `copy` are translated into
plain category names instead of being silently renamed.

## Broader editorial checks

### Terminology and information sequence — clear after reconciliation

The previous README said seven public categories while scoring and runtime
instructions described a different shape. Sentence analysis did not detect that
taxonomy contradiction. Release 2.3.0 fixed it by generating the eight-category
table and details from `schema/taxonomy.json`; package validation now rejects a
stale projection. “Editorial slop” is the public term and `copy` is explicitly
identified as the compatibility key.

### Claim support and provenance — clear

The README limits its claims to observable behavior and named artifacts. It now
says Claude and Codex share one source-compatible skill while explicitly
refusing to claim identical behavior. The validation badge links to the workflow,
and the validation section names the executable checks behind the claim.

### Action and recovery clarity — clear

Claude, Codex, and generic Agent Skills paths each include an install command,
an invocation, and the relevant fallback. The Claude maintainer path now names
the project file, startup command, improvement prompt, and blind-test boundary.
Repeat-audit instructions name the required baseline artifacts and validation
command. No error-state promise is made without a next action.

### Voice and audience fit — clear

The README speaks to developers and design auditors in direct language, keeps
the janitor metaphor local, and translates schema keys at first use. The humor
does not replace install, output, evidence, or compatibility details.

## Final disposition

**Cleared:** no active editorial-slop finding in the current README. The
clearance is bounded to this file and hash. It combines normalized sentence
measurements, four sentence checks, and four broader editorial checks; it is not
an AI-authorship verdict. The former taxonomy contradiction is recorded as a
fixed editorial defect, not erased by the clean current result.

## Reconciliation after the continuity-fixture rename

`README.md` changed for repository structure: the evaluation fixture directory
was renamed to `evals/continuity/`, the known-answer `evals/web-fixtures/` suite
was added, and the `schema/rules/` lead packs joined the validation list and
layout tree.
Every edited line sits inside a fenced code block, which the analyzer excludes
as markup, so each rerun reported identical measurements: 2,948 source words, 1,484 analyzed reader-facing words, 1,464 excluded
markup words, 122 sentences, adequacy `adequate`, and one `repeated_openings` lead in
the `rhythm` family. One signal family does not meet the independent-family predicate,
so no sentence-pattern finding is raised. The manual passes below were re-read against
the edited section and their conclusions are unchanged. This receipt makes no
authorship assessment.
