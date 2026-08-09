# Sentence-slop audit protocol

Sentence slop is an observable copy-quality failure: repeated rhetorical machinery, monotonous cadence, vague abstraction, or obscured responsibility makes a product less clear, less distinctive, or harder to act on. It is **not** evidence that AI authored the text.

## Boundary

- Never classify authorship, calculate an “AI probability,” or use perplexity or burstiness as proof. Machine-text detectors fail under paraphrase and domain/model shift, and low-perplexity methods have produced severe false positives for non-native English writers. [SADASIVAN23][MAGE24][LIANG23]
- Treat linguistic measurements as leads. Research finds group-level differences in syntax, semantics, and feature variability, but also substantial domain and model variation; those observations do not identify the author of an individual passage. [ZANOTTO25]
- A finding requires an adequate sample, at least two independent signals, quoted examples, and a demonstrated product consequence. A single phrase, short sentence, passive construction, rhetorical question, or smooth paragraph is not a finding.
- Never infer language background, disability, education, or writing assistance from prose. Apply special-context guards only when the user or product context supplies them.

## Select the copy mode

### Product prose

Use for landing-page sections, onboarding explanations, lessons, help content, articles, and generated answers. Prefer at least 150 words and five complete sentences. Between 80 and 149 words, label statistical conclusions **limited sample**. Below 80 words, do not score cadence or distribution.

### UI microcopy

Use for labels, buttons, errors, empty states, notifications, and tooltips. Do not apply prose statistics to isolated fragments. Compare at least eight equivalent strings or three related surfaces. Test terminology, grammatical person, specificity, responsibility, recovery information, and repeated filler across the set.

## Candidate signals

The bundled analyzer reports these as review leads, not verdicts:

1. **Cadence uniformity** — sentence-length variance is unusually low across an adequate prose sample.
2. **Repeated openings** — several sentences begin with the same two- or three-token frame.
3. **Formulaic scaffolds** — repeated constructions such as “not X, but Y,” “here is the truth,” or “whether you are…” carry structure without adding product information.
4. **Rhetorical-question density** — questions repeatedly manufacture momentum but are not answered with concrete information or a decision.
5. **Passive candidates** — responsibility may be hidden. Confirm the actor or action is actually unclear; passive voice is legitimate when the actor is unknown, irrelevant, or deliberately deemphasized.
6. **Transition concentration** — paragraphs repeatedly advance through the same discourse markers instead of an information hierarchy.
7. **Phrase repetition** — nontrivial n-grams recur without being required product terminology.
8. **Detail sparsity** — abstract promises dominate while actors, objects, conditions, numbers, dates, examples, or consequences are absent.
9. **Missing error recovery** — a set of error or denial messages states failure but repeatedly omits cause, affected or retained state, and a useful next action.

## Compound finding predicate

Promote a lead only when all conditions hold:

1. The sample threshold for its mode is met.
2. At least two independent signals recur; duplicated measurements of the same repetition count as one signal.
3. The audit quotes representative examples and identifies their surfaces.
4. The copy causes at least one observable consequence: users cannot tell what the product does, who acts, what changed, what to choose, how to recover, or why this product is distinct; or the stated editorial voice is materially flattened.
5. A plausible counterexample was tested and rejected.

Report the consequence, not an authorship story. A valid title is “Repeated rhetorical scaffolds hide the lesson’s concrete outcome,” not “This was written by AI.”

## False-positive guards

- Do not penalize plain language, short sentences, or predictable terminology when they improve comprehension. WCAG explicitly values readable and understandable text and recognizes that content purpose and audience affect appropriate complexity. [W3C-READING]
- Do not penalize non-native, translated, accessibility-focused, technical, scientific, legal, regulated, or safety-critical prose for low variation. Evaluate whether it serves its intended user and genre. [LIANG23]
- Passive voice becomes a product-copy issue only when it obscures responsibility, state, or recovery. Clear-language guidance favors active voice because passive constructions can lengthen and obscure content, but this is contextual guidance rather than a ban. [GOVUK-CLEAR]
- Repetition is legitimate for commands, safety warnings, legal terms, navigation labels, design-system consistency, and teaching reinforcement.
- A distinctive voice is not automatically a good one. Clarity, accessibility, truth, and task completion outrank stylistic flamboyance.

## Evidence record

For each sentence-copy candidate, record:

```json
{
  "mode": "prose | ui_microcopy",
  "sample": {"words": 0, "sentences": 0, "surfaces": 0, "adequacy": "adequate | limited | insufficient"},
  "signals": [{"code": "repeated_openings", "measurement": "", "examples": []}],
  "consequence": "",
  "counterexample_tested": "",
  "authorship_assessment": "not_performed",
  "disposition": "finding | enhancement | cleared | not_run",
  "confidence": "high | moderate | low"
}
```

When the sample is insufficient, report the check as limited or not run. Do not silently extrapolate from one screenshot headline to an application-wide voice.

## Optional deterministic analyzer

Run `python3 scripts/analyze_sentence_slop.py <text-or-json-file>` when command execution is available. It uses only the Python standard library and emits measurements plus length-gated leads. The output deliberately contains no authorship score. Inspect the quoted text and product consequence before creating a finding.

## Research basis

- [Sadasivan et al., *Can AI-Generated Text be Reliably Detected?*](https://arxiv.org/abs/2303.11156) — paraphrasing and spoofing stress tests plus theoretical limits.
- [Liang et al., *GPT detectors are biased against non-native English writers*](https://pmc.ncbi.nlm.nih.gov/articles/PMC10382961/) — measured false positives and perplexity bias.
- [Li et al., *MAGE: Machine-generated Text Detection in the Wild*](https://aclanthology.org/2024.acl-long.3/) — domain/model shift and diminishing linguistic differences.
- [Zanotto and Aroyehun, *Linguistic and Embedding-Based Profiling of Texts Generated by Humans and Large Language Models*](https://aclanthology.org/2025.emnlp-main.1163/) — syntax, semantics, and variability as population-level features.
- [W3C, *Understanding Success Criterion 3.1.5: Reading Level*](https://www.w3.org/WAI/WCAG22/Understanding/reading-level.html) — audience-aware readability and sample-based evaluation.
- [GOV.UK, *Use clear language*](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/) — contextual active-voice and clarity guidance.
