# Sentence-slop audit protocol

Sentence slop is an observable copy-quality failure: repeated rhetorical machinery, monotonous cadence, vague abstraction, conceptual collisions, or obscured responsibility makes a product less clear, less distinctive, or harder to act on. It is **not** evidence that AI authored the text.

## The audit's own prose is in scope

Scruffy holds every interface it audits to a legibility standard. Its own report is an interface, and until 2026-08-17 it was held to none.

The failure that forced this: a twenty-one item registry in which every reader-facing field was populated, accurate, and evidence-backed, and which a human could not read. Each finding rendered as seven equal-weight blocks — observation, impact, cause, recommendation, evidence, acceptance checks, disposition — in the same register, twenty-one times. No sentence anywhere said the plain thing. Nothing failed, because correctness and legibility are different properties and only one of them was checked.

**Every registry item carries a `plain` lead.** One or two sentences, under thirty-two words, naming what is wrong in the reader's own words rather than the taxonomy's. It is a required field at schema 2.1 and `scripts/validate_audit.py` refuses a registry without it.

A lead is not a summary of the finding. It is the finding, said first:

| Instead of | Write |
|---|---|
| "The stale-record join failed silently and reported a number instead of an error" | "The page said one record was going unwatched. Ten were." |
| "Reader-facing titles displayed the source format's markup" | "Formatting marks printed as literal characters in 56 titles." |
| "The surface reports 126 actionable items and offers no way to act on any of them" | "The page lists 126 things needing your attention and gives you no way to act on any of them." |

Two `cognitive_load` signals enforce it. `missing_plain_lead` fires on an absent lead or one over budget. `jargon_lead` fires when the lead is written in the register it was meant to replace — category keys, facet names, `structural cause`, `acceptance check`. The reader's own domain terms are never jargon; a security engineer reading an audit of their own tool knows what a join and a commit are. The audit's private vocabulary is what gets flagged.

**Detail is never traded for readability.** The lead is added, not substituted. Renderers lead with the plain sentence and the recommended change, then disclose the full record progressively — a `<details>` in HTML, forced open in print. Every field stays in the document, in find-on-page, and in the JSON. Summarising discards; disclosing does not.

Run it with `python3 scripts/lint_report_prose.py findings.json --context context.json`, or let `validate_audit.py` run it for you. Add `--strict-prose` to make leads a gate rather than a note.

## Boundary

- Never classify authorship, calculate an “AI probability,” or use perplexity or burstiness as proof. Machine-text detectors fail under paraphrase and domain/model shift, and low-perplexity methods have produced severe false positives for non-native English writers. [SADASIVAN23][MAGE24][LIANG23]
- Treat linguistic measurements as leads. Research finds group-level differences in syntax, semantics, and feature variability, but also substantial domain and model variation; those observations do not identify the author of an individual passage. [ZANOTTO25]
- A finding requires an adequate sample, at least two independent signal families, quoted examples, and a demonstrated product consequence. Count shared evidence once: four repetitions of one “not X, but Y” frame do not become independent because an opening counter and a scaffold counter both see them.
- A single phrase, em dash, triad, short sentence, passive construction, rhetorical question, polished paragraph, or favorite word is not a finding. These are normal resources of human rhetoric and genre writing. [ORgKY9AlybA 4:06–8:32]
- Never infer language background, disability, education, or writing assistance from prose. Apply special-context guards only when the user or product context supplies them.
- The bundled surface analyzer is English-scoped. Supply `--language en` only when that scope is verified. `--language non_en` and `--language unknown` abstain from surface scoring and require a language-competent reviewer; do not translate prose merely to make English regexes run.

## Select the copy mode

### Product prose

Use for landing-page sections, onboarding explanations, lessons, help content, articles, and generated answers. Prefer at least 150 words and five complete sentences. Between 80 and 149 words, label statistical conclusions **limited sample**. Below 80 words, do not score cadence or distribution.

### UI microcopy

Use for labels, buttons, errors, empty states, notifications, and tooltips. Do not apply prose statistics to isolated fragments. Compare at least eight equivalent strings or three related surfaces. Test terminology, grammatical person, specificity, responsibility, recovery information, and repeated filler across the set.

## Extract prose before measuring it

Repository documents are mixed inputs. Exclude frontmatter, HTML-only elements, images, headings, tables, raw URLs, fenced and inline code, and install commands before calculating word count, cadence, repetition, or specificity. Keep visible body copy and list text. Record what was excluded.

This is a trust boundary, not cleanup theater. HTML attributes, Markdown badge syntax, and shell commands can create fake repeated openings, fake proper-name “anchors,” and fragment-heavy sentence counts. A report that measures the source file without proving the extracted reader-facing sample must mark sentence statistics **not run**.

## Candidate signals

The bundled analyzer reports these as review leads, not verdicts:

1. **Cadence uniformity** — sentence-length variance is unusually low across an adequate prose sample.
2. **Repeated openings** — several sentences begin with the same two- or three-token frame.
3. **Formulaic scaffolds** — repeated constructions such as “not X, but Y,” the comma-splice reframe “you’re not X, you’re Y,” “here’s the kicker,” “here is the truth,” or “whether you are…” carry structure without adding product information.
4. **Rhetorical-question density** — questions repeatedly manufacture momentum but are not answered with concrete information or a decision.
5. **Short-sentence burst** — several punchline-length sentences replace development with a uniform promotional beat.
6. **Passive candidates** — responsibility may be hidden. Confirm the actor or action is actually unclear; passive voice is legitimate when the actor is unknown, irrelevant, or deliberately deemphasized.
7. **Transition concentration** — paragraphs repeatedly advance through the same discourse markers instead of an information hierarchy.
8. **Paragraph-pattern reuse** — three or more paragraphs repeat the same non-plain sequence of question, scaffold, transition, statement, or short punchline.
9. **Phrase repetition** — nontrivial n-grams recur without being required product terminology.
10. **Detail sparsity** — abstract promises dominate while actors, objects, conditions, numbers, dates, quoted interface labels, examples, or consequences are absent.
11. **Missing error recovery** — a set of error or denial messages states failure but repeatedly omits cause, affected or retained state, and a useful next action.
12. **Hedged profundity** — commitment-free intensity modifiers (“quietly,” “subtly,” “effortlessly,” “on some level”) recur while decorating claims that are never made concrete. The word gestures at significance precisely because it commits to nothing.
13. **Triad density** — a high share of sentences carry short-item three-part lists (“fast, simple, and reliable”). Only triads of one- to two-word interchangeable items are counted; enumerations of distinct noun phrases are not.

### Detector packs

The lexicon- and pattern-driven signals above are grouped into named packs so a team can add, remove, or tweak a detector without editing the statistical core. Current packs: `contrast-scaffolds`, `hook-scaffolds` (both feed `formulaic_scaffolds`), `transition-markers` (`transition_concentration`), `abstract-filler` (`detail_sparsity`), `hedged-profundity`, and `triad-density`. Run `python3 scripts/analyze_sentence_slop.py --list-packs` to enumerate them, and pass `--disable-pack <id>` (repeatable) or `analyze(..., disabled_packs=[...])` to turn one off. Each pack is a self-contained entry in the analyzer's `PACKS` registry carrying its own patterns or terms, signal code, and provenance; packs sharing a signal code merge, so adding a new source is one appended entry (or extra terms in an existing pack) plus the mandatory false-positive fixture in `evals/sentence-slop/cases.json` and a guard note here. Every result discloses active and disabled packs; a durable report that ran with packs disabled must say so in its capability disclosure. Statistical signals (cadence, openings, questions, passives, short bursts, paragraph reuse, phrase repetition) are core and not toggleable. The error-recovery detector's vocabulary is also pack-owned: `error-states` and `recovery-cues` (which recognizes honest retained-state language such as "nothing changed" as a recovery cue). UI items may carry an optional `surface_class`; `label`, `badge`, `cell`, `heading`, and `status` classes are treated as vocabulary rather than messages and never produce missing-recovery leads.

### Required manual passage checks

The analyzer cannot safely score these. Run them on every adequate prose sample:

1. **Conceptual coherence** — trace each metaphor, comparison, and key noun across adjacent sentences. Quote any verb-object or source-target mapping that stops making literal or figurative sense. Smooth local wording can still produce an incoherent claim. [COHESENTIA23][ORgKY9AlybA 10:36–14:36]
2. **Sentence portability** — ask whether a representative claim could move unchanged to several unrelated products. Name the missing actor, object, condition, example, evidence, or consequence; “sounds generic” is not enough.
3. **Discourse purpose** — label what each paragraph contributes to the reader's task. Repeated setup, contrast, validation, summary, and call-to-action moves are slop only when they add no decision-relevant information. Research on discourse similarity supports examining repeated document structure rather than treating one token as a tell. [QUDSIM25]
4. **Voice and subtext** — compare with the supplied voice and neighboring surfaces. Identify a necessary point of view, lived detail, restraint, or subtext that was flattened. Do not invent a preferred voice or use “more human” as an acceptance criterion.

## Compound finding predicate

Promote a lead only when all conditions hold:

1. The sample threshold for its mode is met.
2. At least two independent signal families recur. Rhythm, rhetorical structure, discourse structure, lexical repetition, specificity, and responsibility are the current families. Collapse duplicated measurements that quote the same evidence.
3. The audit quotes representative examples and identifies their surfaces.
4. The copy causes at least one observable consequence: users cannot tell what the product does, who acts, what changed, what to choose, how to recover, or why this product is distinct; or the stated editorial voice is materially flattened.
5. A plausible counterexample was tested and rejected.

Report the consequence, not an authorship story. A valid title is “Repeated rhetorical scaffolds hide the lesson’s concrete outcome,” not “This was written by AI.”

## False-positive guards

- Do not penalize plain language, short sentences, or predictable terminology when they improve comprehension. WCAG explicitly values readable and understandable text and recognizes that content purpose and audience affect appropriate complexity. [W3C-READING]
- Do not penalize non-native, translated, accessibility-focused, technical, scientific, legal, regulated, or safety-critical prose for low variation. Evaluate whether it serves its intended user and genre. [LIANG23]
- Passive voice becomes a product-copy issue only when it obscures responsibility, state, or recovery. Clear-language guidance favors active voice because passive constructions can lengthen and obscure content, but this is contextual guidance rather than a ban. [GOVUK-CLEAR]
- Repetition is legitimate for commands, safety warnings, legal terms, navigation labels, design-system consistency, and teaching reinforcement.
- Em dashes, parentheticals, rhetorical triads, fragments, contrast frames, and genre calls to action are normal writing devices. Review their density and consequence; never ban them globally. The `triad-density` and `hedged-profundity` leads exist to measure density, not to ban the device; a single triad, one “quietly,” or one contrast reframe is never a finding. [ORgKY9AlybA 7:30–8:32][ORgKY9AlybA 16:28–16:52]
- A distinctive voice is not automatically a good one. Clarity, accessibility, truth, and task completion outrank stylistic flamboyance.

## Evidence record

For each sentence-copy candidate, record:

```json
{
  "mode": "prose | ui_microcopy",
  "sample": {"words": 0, "sentences": 0, "surfaces": 0, "adequacy": "adequate | limited | insufficient"},
  "normalization": {"source_words": 0, "analyzed_words": 0, "removed": {}},
  "signals": [{"code": "repeated_openings", "signal_family": "rhythm", "measurement": "", "examples": []}],
  "manual_checks": [{"code": "conceptual_coherence", "evidence": "", "result": "clear | candidate | not_run"}],
  "consequence": "",
  "counterexample_tested": "",
  "authorship_assessment": "not_performed",
  "disposition": "finding | enhancement | cleared | not_run",
  "confidence": "high | moderate | low"
}
```

When the sample is insufficient, report the check as limited or not run. Do not silently extrapolate from one screenshot headline to an application-wide voice.

## Optional deterministic analyzer

Run `python3 scripts/analyze_sentence_slop.py <text-or-json-file> --language en` when command execution is available and English scope is verified. Use `--list-packs` to enumerate detector packs and `--disable-pack <id>` to run without one; disabled packs are disclosed in the output and must be disclosed in any durable report. Use `--language non_en` or `--language unknown` to record an explicit abstention. The analyzer uses only the Python standard library, strips common repository markup before prose measurement, groups leads by independent signal family, and emits the four required manual checks. The output deliberately contains no authorship score and never makes a finding. Inspect the normalized sample, perform the semantic checks, quote the text, and prove the product consequence before promotion.

## Research basis

- [Sadasivan et al., *Can AI-Generated Text be Reliably Detected?*](https://arxiv.org/abs/2303.11156) — paraphrasing and spoofing stress tests plus theoretical limits.
- [Liang et al., *GPT detectors are biased against non-native English writers*](https://pmc.ncbi.nlm.nih.gov/articles/PMC10382961/) — measured false positives and perplexity bias.
- [Li et al., *MAGE: Machine-generated Text Detection in the Wild*](https://aclanthology.org/2024.acl-long.3/) — domain/model shift and diminishing linguistic differences.
- [Zanotto and Aroyehun, *Linguistic and Embedding-Based Profiling of Texts Generated by Humans and Large Language Models*](https://aclanthology.org/2025.emnlp-main.1163/) — syntax, semantics, and variability as population-level features.
- [Namuduri et al., *QUDsim: Quantifying Discourse Similarities in LLM-Generated Text*](https://openreview.net/forum?id=zFz1BJu211) — repeated discourse structures across generated texts; useful for passage-shape hypotheses, not individual authorship claims.
- [Maimon and Tsarfaty, *COHESENTIA*](https://aclanthology.org/2023.emnlp-main.324/) — human-perceived coherence, incremental sentence-level annotation, and the unsatisfactory reliability of automated coherence models.
- [languagejones, *How to Detect AI Slop*](https://www.youtube.com/watch?v=ORgKY9AlybA) — targeted creator source for the surface-tell counterexample and conceptual-coherence review; used only where corroborated and not as an authorship authority. Auto-captions extracted 2026-08-10.
- [Hank Green, public statement about AI use](https://www.reddit.com/r/nerdfighters/comments/1vc37aw/hanks_comment_about_his_ai_use_posted_here_as_its/) — primary process evidence separating research assistance, personal authorship, voice dilution, trust, and overreliance; not a textual detector rule. [HANKGREEN26]
- [W3C, *Understanding Success Criterion 3.1.5: Reading Level*](https://www.w3.org/WAI/WCAG22/Understanding/reading-level.html) — audience-aware readability and sample-based evaluation.
- [GOV.UK, *Use clear language*](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/) — contextual active-voice and clarity guidance.
- Maintainer field observations, 2026-08-14 — hedged profundity (“quietly”), kicker hooks, comma-splice negative parallelism, profound-but-vague vocabulary, and triad saturation registered as lead patterns with false-positive guards; hypothesis-level provenance corroborated for contrast frames and triads by [ORgKY9AlybA], not an authorship authority. [field 2026-08-14]
