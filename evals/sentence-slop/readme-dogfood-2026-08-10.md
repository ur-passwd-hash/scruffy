# README sentence-slop dogfood — 2026-08-10

Target: `README.md`

Target SHA-256: `be6f0acd5021cac2147d50895e37fe8763c266c6d739f3b84929f449617de7af`

Command:

```sh
python3 scripts/analyze_sentence_slop.py README.md --mode prose
```

This is a quality review. It makes no authorship assessment.

## Reconciliation with blind finding AS-04

The earlier analyzer treated README HTML, badge markup, tables, headings, URLs,
and install commands as prose. Its baseline run reported 2,318 words, 150
sentences, and 252 “concrete anchors.” That contaminated sentence segmentation
and specificity evidence.

The corrected run reported:

- 2,638 source words
- 1,313 analyzed reader-facing words
- 1,325 excluded markup/code words
- 107 analyzed sentences
- 19 fenced code blocks, 26 table rows, 25 headings, 5 HTML images, and 27
  inline-code spans excluded
- 76 specificity markers after extraction
- zero automated review leads
- manual passage review required

Disposition: **AS-04 fixed and regression-covered.** Automated surface measures
are clear for this README. That result does not clear the required manual pass.

## Manual passage checks

### Conceptual coherence — clear

The janitor/sweeping metaphor stays confined to the brand frame. “Interface
janitor,” “slop,” and the mascot image share one cleaning model. Local jokes such
as “screenshot astrology” and “card soup” do not carry product claims or combine
in ways that obscure the method. The seven category definitions remain literal
and operational.

### Sentence portability — clear

The opening names Scruffy, web apps, Claude and Codex, accepted inputs, live
operation, evidence, reports, and fixes. The category descriptions name distinct
failure modes and proof requirements. A few general claims, such as the method
being evidence-first, are immediately supported by specific workflow rules.
They do not stand as portable promotional filler.

### Discourse purpose — clear

The sequence has distinct jobs: plain promise, deliverables, quick starts,
improvement map, seven-category map, evidence discipline, modes, installation,
repository anatomy, validation, repeat-audit durability, corpus growth, and
boundaries. The analyzer found no repeated non-plain paragraph signature. The
category table deliberately repeats a comparison structure; that repetition
supports scanning and is not prose slop.

### Voice and subtext — clear

The voice is direct, slightly irreverent, and consistent with the Scruffy
janitor character. The copy avoids pretending the tool can identify an author.
Stable internal keys such as `backend_shape` and `copy` are translated into
plain category names instead of being silently renamed.

## Final disposition

**Cleared:** no sentence-slop finding in the current README. The clearance is
bounded to this file and hash. It combines normalized automated measurements
with the four required manual checks; it is not an AI-authorship verdict.
