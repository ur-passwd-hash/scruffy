# README editorial-slop dogfood — 2026-08-10

Target: `README.md`

Target SHA-256: `ed0b75cae2778da1426be4931f7969f392e3d5111618b8069ef4983172a2e12c`

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
was added, and the `schema/rules/` lead packs and the product-surface test joined the
validation list and layout tree.
Every edited line sits inside a fenced code block, which the analyzer excludes
as markup, so each rerun reported identical measurements: 2,948 source words, 1,484 analyzed reader-facing words, 1,464 excluded
markup words, 122 sentences, adequacy `adequate`, and one `repeated_openings` lead in
the `rhythm` family. One signal family does not meet the independent-family predicate,
so no sentence-pattern finding is raised. The manual passes below were re-read against
the edited section and their conclusions are unchanged. This receipt makes no
authorship assessment.

## Cognitive-load family addition (same day)

The analyzer gained the `cognitive_load` family (overlong_sentence, clause_pileup,
parenthetical_stacking; wall_paragraph in the report-prose linter). Rerunning on the
unchanged README now reports overlong_sentence and clause_pileup leads alongside the
original repeated_openings lead. These are leads on our own prose and are expected:
the README's install and validation sections carry long enumerated sentences whose
guard ("a single parallel enumerated list reads fine") applies to several but not all.
Manual pass conclusion: tighten opportunistically; no finding. No authorship assessment.

## Release 2.5.0 reference-grounding reconciliation

The new shipped-product-grounding section changed reader-facing prose. The current
run reports 3,097 source words, 1,568 analyzed words, 1,529 excluded markup/code
words, and 133 sentences. It emits four review leads across three independent
families: `overlong_sentence`, `clause_pileup`, `repeated_openings`, and
`paragraph_pattern_reuse`. Those measurements trigger review; they do not establish
a finding or authorship.

The manual passes were rerun on the added section. It has one bounded purpose:
explain the optional capability, name the vendor-neutral rule, point to the canonical
reference, and give the two supported Claude connection paths. The repeated
"Mobbin MCP" opening keeps the paid-plan requirement adjacent to the setup command;
the three-sentence paragraph shape does not obscure the task. The section names the
connector, tools, OAuth constraint, source file, and exact endpoint, so it is not
portable promotional filler. Terminology matches the canonical
`design_reference_search` capability and recovery is explicit: an absent connector
is disclosed and the audit continues. The previous eight manual-check conclusions
remain clear. This receipt makes no authorship assessment.

## Measurement reconcile — end of 2026-08-10

Final rerun after all repository-structure edits: 3103 source words, 1568
analyzed reader-facing words, 1535 excluded markup words, 133 sentences,
adequacy `adequate`, 4 lead(s) including the cognitive_load family. Earlier
figures in this receipt describe earlier README states; this block is
authoritative for the committed revision. Manual-pass conclusions unchanged.
No authorship assessment.


## Refresh — 2026-08-14 (packs, gates, Mop, and scaffold sections added)

Rerun after the README gained the Scruffy's Mop section, the category-gate and
pack-registry bullets, and the scaffold quickstart. Analyzer schema 1.3
(merged pack registry + cognitive-load signals), verified `en` scope.

Sample: 3,333 source words, 1,750 analyzed reader-facing words, 149 sentences,
adequate. Leads:

- `repeated_openings` — 5 repeated openings across 149 sentences
- `paragraph_pattern_reuse` — 1 non-plain paragraph signature(s) recur at least three times
- `overlong_sentence` — 2 of 149 sentences exceed 35 words
- `clause_pileup` — 13 sentences with semicolon chains or five-plus commas
- `parenthetical_stacking` — 1 sentences with two or more parentheticals

Reconciliation. The added prose was tightened before this receipt: the gates
bullet was split into four short sentences and the Mop paragraph into six,
dropping overlong sentences from 4 to 2. The residual leads trace to
pre-existing enumeration sentences — the corpus credit list and the
category/evidence enumerations — which the analyzer's own guards name as
legitimate ("citation strings legitimately carry punctuation density"; "a long
sentence that is one parallel enumerated list reads fine"). The repeated
openings are parallel bullet frames in the harder-to-fool list, kept
deliberately. Manual pass over the four added sections: coherent, portable
only where intended (the scaffold command is product-specific), each paragraph
adds decision-relevant information, and the voice matches the surrounding
document. No authorship assessment performed.
