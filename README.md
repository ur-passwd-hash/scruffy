<p align="center">
  <img src="assets/scruffy-hero.png" alt="Scruffy sweeping a field of cartoon nuts and bolts with a janitorial push broom" width="100%">
</p>

<h1 align="center">Scruffy</h1>

<p align="center"><strong>Find the AI slop. Prove it. Fix it.</strong></p>

<p align="center">
  <a href="https://github.com/ur-passwd-hash/scruffy/actions/workflows/validate.yml"><img src="https://github.com/ur-passwd-hash/scruffy/actions/workflows/validate.yml/badge.svg" alt="Validation"></a>
  <img src="https://img.shields.io/badge/Agent%20Skills-compatible-13543e" alt="Agent Skills compatible">
  <img src="https://img.shields.io/badge/Codex%20%2B%20Claude-parity-c69b3f" alt="Codex and Claude parity">
  <img src="https://img.shields.io/badge/license-MIT-7a4f8f" alt="MIT license">
</p>

<p align="center"><sub><strong>Scruffy</strong> is the interface janitor for AI slop.</sub></p>

**Scruffy finds AI slop in web apps—and shows its work.** Give Claude or Codex a URL, screenshot, prototype, or source repository. Scruffy operates the real interface, inspects the available code and copy, captures evidence, and returns a prioritized report with practical fixes.

**What “AI slop” means here:** generic layouts, fake or broken interactions, vague or formulaic writing, missing product logic, inaccessible controls, weak performance, and vibe-coded shortcuts that make an app brittle.

**What it does not mean:** Scruffy does not guess whether AI wrote the app. It judges the result, not the author. The same failures can appear in hand-written, template-derived, outsourced, and AI-generated work.

## What you get

- A product frame before anyone starts arguing about border radii
- Live task walkthroughs instead of screenshot astrology
- Findings with evidence, user impact, confidence, falsification attempts, and acceptance checks
- Cleared suspicions published beside confirmed defects
- Sentence-quality analysis with explicit false-positive guards and **no authorship score**
- Stable finding IDs that cannot quietly disappear in a repeat audit
- Complete JSON, Markdown, and self-contained decision-dashboard outputs
- Dependency-ordered work orders when implementation is authorized

## Sixty-second start — Claude Code

Inside Claude Code, add this repository as a marketplace and install Scruffy:

```text
/plugin marketplace add ur-passwd-hash/scruffy
```

```text
/plugin install scruffy@scruffy-marketplace
```

Then run the stable, namespaced plugin command:

```text
/scruffy:scruffy audit https://example.com end to end. Operate the real tasks, capture desktop and mobile evidence, challenge every suspicion, and show me the cleared ones too.
```

### Codex quick start

```sh
git clone https://github.com/ur-passwd-hash/scruffy.git
mkdir -p ~/.agents/skills
ln -s "$(pwd)/scruffy" ~/.agents/skills/scruffy
```

```text
$scruffy audit https://example.com end to end. Operate the real tasks, capture desktop and mobile evidence, test sentence quality without guessing authorship, publish the full findings registry, and generate the decision dashboard.
```

## What it improves

| Layer | What the skill tests | Typical improvement |
|---|---|---|
| Product | Audience, job, primary action, repeat-use reason, success signal | A clearer product and fewer ornamental features |
| Information architecture | Routes, state addressability, content structure, navigation | Shareable states, better retrieval, and scalable navigation |
| Interaction | Real tasks, feedback, errors, persistence, keyboard and mobile behavior | Controls that behave as promised and recover cleanly |
| Accessibility | Semantics, names, focus, states, contrast, reflow | Broader access and more robust interaction contracts |
| Visual identity | Hierarchy, composition, typography, color, density, imagery | A distinctive interface without card soup or decoration theater |
| Copy | Specificity, terminology, sentence cadence, rhetorical scaffolds, responsibility, errors, recovery language | Concrete, product-specific language instead of filler, without guessing authorship |
| Implementation shape | State ownership, routing, shared primitives, tokens, silent failures | Cheaper changes and fewer repeated defects |
| Performance | Runtime traces and interaction measurements | Faster, more truthful loading and response behavior |

The method is deliberately evidence-first. It operates representative tasks, challenges its own suspicions, distinguishes defects from enhancements, and publishes cleared suspicions alongside findings. Repeated audits use an immutable registry: every earlier item must be carried, reopened, fixed, cleared, merged, or superseded. A shortlist may change; the historical record cannot silently shrink.

## The recurring slop classes

### Product slop — the wrong thing, confidently

The surface never established who it serves or what job it performs. Common signals include unshareable multi-state experiences, absent recovery or resume behavior, dead-end terminal states, and features present only because similar products have them.

### Interaction slop — behavior that breaks the affordance

A control promises one thing and does another: a contents button opens an unwieldy chip strip, a filter sorts, a media action gives no state feedback, or a visual application has no workable keyboard path. These defects can be found only by operating the interface.

### Backend-shape slop — structure that makes good features expensive

Content is fused to rendering, navigation state has no address, styles are copied instead of tokenized, or failures disappear into empty exception handlers. The binding rule is simple: when several wanted features are expensive for the same structural reason, that shared cause is the finding.

### Visual slop — a generic mean masquerading as design

Card soup, excessive type roles, decorative badges, arbitrary gradients, identical radii everywhere, synthetic proof, and interchangeable hero composition are candidate signals. They become findings only when rendered evidence shows weak hierarchy, task friction, or lost identity.

### Copy slop — words that could belong to any product

Generalized verbs, unexplained “Oops” messages, inconsistent terminology, claims presented as evidence, repeated rhetorical scaffolds, monotonous cadence, and responsibility-obscuring passives can make an interface vague or interchangeable. A word, passive construction, rhetorical question, emoji, exclamation mark, or headline length is never an automatic defect. The sentence analyzer produces length-gated review leads and deliberately refuses to classify authorship.

### Performance slop — quality below the speed floor

Slow interaction, unstable layout, delayed primary content, blocking third parties, or dishonest wait states count only when measured at runtime. Source size alone is not a performance finding.

### Accessibility slop — semantics and state treated as decoration

Missing landmarks, unnamed controls, invisible focus, low contrast, unannounced state changes, and layouts that fail under zoom are functional defects. The skill identifies specific barriers; it does not claim full conformance from a sample.

## Why the method is harder to fool

- Product framing precedes visual critique.
- A capability preflight prevents unsupported claims when source, browser, screenshots, traces, or write access are absent.
- Representative task walkthroughs replace screenshot-only judgment.
- Findings require evidence and a falsification attempt.
- Blind audits quarantine prior reports and expected answers, freeze discovery by hash, and reveal the baseline only during reconciliation.
- Sentence-level measurements require adequate samples, multiple independent signals, and a demonstrated product consequence.
- Stable IDs and identity keys prevent a later report from reusing or dropping earlier findings.
- Application-archetype probes adapt the task walkthrough to courses, SaaS tools, transactions, forms, analytics, collaboration, editors, marketing sites, and hybrids.
- Structural blockers are fixed before cosmetic symptoms.
- Severity, confidence, and category scores use a calibrated rubric.
- Retractions receive the same prominence as findings.
- An interactive decision report is supported, but Markdown and JSON fallbacks keep the skill portable.

## Modes

| Mode | Use it for | Result |
|---|---|---|
| **AUDIT** | Existing URL, app, source tree, prototype, or screenshot | Evidence-backed report; no source changes unless requested |
| **REDESIGN** | Existing experience that should also be improved | Audit, coherent direction, authorized implementation, and regression checks |
| **DESIGN** | Blank or weakly defined interface | Product frame plus structurally different design directions before convergence |
| **DEMONSTRATE-FIX** | Live page without source access | Reversible demonstration labeled separately from repository changes |

## Install

This repository follows the [Agent Skills specification](https://agentskills.io/specification). Clone or copy it so the installed skill directory is named `scruffy`.

### Claude Code — priority path

The repository is both a Claude Code plugin and a one-plugin marketplace. Install it from inside Claude Code:

```text
/plugin marketplace add ur-passwd-hash/scruffy
```

```text
/plugin install scruffy@scruffy-marketplace
```

Invoke the installed plugin explicitly:

```text
/scruffy:scruffy audit https://example.com and prioritize the structural fixes
```

The equivalent shell commands are:

```sh
claude plugin marketplace add ur-passwd-hash/scruffy
claude plugin install scruffy@scruffy-marketplace
```

For local plugin development, clone the repository and load it directly:

```sh
git clone https://github.com/ur-passwd-hash/scruffy.git
claude --plugin-dir "$(pwd)/scruffy"
```

If you prefer the bare `/scruffy` command, install the same checkout as a personal skill instead of a plugin:

```sh
mkdir -p ~/.claude/skills
ln -s /absolute/path/to/scruffy ~/.claude/skills/scruffy
```

```text
/scruffy audit https://example.com and prioritize the structural fixes
```

For a private GitHub repository, authenticate Git first. Claude Code uses existing credential helpers for manual installs and updates; GitHub shorthand uses SSH by default. See the [official private-marketplace guidance](https://code.claude.com/docs/en/plugin-marketplaces#private-repositories).

### Codex

Install for all projects:

```sh
mkdir -p ~/.agents/skills
ln -s /absolute/path/to/scruffy ~/.agents/skills/scruffy
```

Or install only for one repository:

```sh
mkdir -p .agents/skills
ln -s /absolute/path/to/scruffy .agents/skills/scruffy
```

Invoke explicitly:

```text
$scruffy audit https://example.com and prioritize the structural fixes
```

Codex may also invoke the skill implicitly when a request matches the `SKILL.md` description.

Codex and Claude load the same root `SKILL.md`; there is no duplicated runtime copy to drift. `agents/openai.yaml` provides Codex UI metadata, while `.claude-plugin/` provides Claude Code distribution metadata.

| Runtime | Native entrypoint | Explicit invocation |
|---|---|---|
| Claude Code plugin | `.claude-plugin/plugin.json` + root `SKILL.md` | `/scruffy:scruffy` |
| Claude Code personal skill | `~/.claude/skills/scruffy/SKILL.md` | `/scruffy` |
| Codex | root `SKILL.md` + `agents/openai.yaml` | `$scruffy` |

### Other agents

Point any Agent Skills-compatible agent at `SKILL.md`. For agents without live-browser or file capabilities, the skill degrades to static analysis and clearly marks runtime checks not run.

## Repository layout

```text
scruffy/
├── .claude-plugin/
│   ├── plugin.json               # Claude Code plugin manifest
│   └── marketplace.json          # installable one-plugin marketplace
├── assets/
│   ├── scruffy-hero.png          # Transparent README action banner
│   └── scruffy-character.png     # Transparent reusable character model
├── SKILL.md                      # shared Agent Skills runtime instructions
├── agents/
│   └── openai.yaml               # Codex UI metadata
├── references/
│   ├── verification.md          # live-operation and falsification protocol
│   ├── scoring.md               # calibrated severity, confidence, and scores
│   ├── durability.md            # immutable identity and revision reconciliation
│   ├── archetypes.md            # task probes by application class
│   ├── sentence-slop.md         # copy-quality signals, thresholds, and false-positive guards
│   ├── blind-audit.md            # quarantine, digest freeze, reveal, and reconciliation
│   └── output-schema.md         # registries, decisions, reports, work orders
├── evals/
│   ├── triggers.json            # positive and negative invocation fixtures
│   ├── archetypes.json          # application-class coverage fixtures
│   ├── sentence-slop/           # quality-signal and false-positive fixtures
│   ├── durability/              # valid and intentionally invalid synthetic revisions
│   └── mahjong/                 # real seventeen-record reconciliation golden case
├── principles/
│   ├── PRINCIPLES.md            # source-of-truth research corpus
│   ├── SOURCES.md               # source registry and intake provenance
│   └── INSPIRATIONS.md          # reference-source tiers
├── scripts/
│   ├── intake.py                # caption intake for corpus research
│   ├── validate_corpus.py        # citation and corpus validation
│   ├── validate_skill.py         # package, reference, and portability validation
│   ├── analyze_sentence_slop.py  # deterministic measurements; never an authorship score
│   ├── blind_protocol.py         # blind manifest, freeze, and integrity verification
│   ├── evaluate_blind_outputs.py # hidden-key scoring with no authorship labels
│   ├── run_sentence_blind.py     # context-free, unlabeled sentence packet runner
│   ├── validate_audit.py         # registry, decisions, and report validation
│   ├── migrate_decisions.py      # carry decisions into a new revision
│   ├── render_dashboard.py       # complete self-contained decision dashboard
│   ├── render_markdown.py        # complete human-readable report
│   ├── test_durability.py        # continuity and rendering regression tests
│   ├── test_sentence_slop.py     # sentence-signal and guard regression tests
│   ├── test_blind_protocol.py    # contamination and post-freeze mutation tests
│   ├── test_blind_evaluator.py   # coverage, temporary-ID, and no-authorship tests
│   ├── test_sentence_blind_runner.py # compound-signal vs guarded-copy regression
│   └── annotate.html             # local screenshot annotation utility
├── .github/workflows/validate.yml # dependency-free CI checks
├── CONTRIBUTING.md
├── CHANGELOG.md
├── README.md
└── LICENSE
```

## Validate

The validators use only the Python standard library:

```sh
python3 scripts/validate_skill.py
python3 scripts/validate_corpus.py
python3 scripts/test_durability.py
python3 scripts/test_sentence_slop.py
python3 scripts/test_blind_protocol.py
python3 scripts/test_blind_evaluator.py
python3 scripts/test_sentence_blind_runner.py
```

The first checks metadata, progressive-disclosure budgets, referenced files, durability and blind-audit terms, sentence and archetype fixtures, Codex metadata, portability traps, and trigger coverage. The second checks corpus coverage, citations, timestamps, aliases, and source-state consistency. The remaining suites prove registry durability, sentence false-positive guards, blind-output immutability, and contamination rejection.

Compatibility note: durable report markers and browser-storage keys retain the internal `anti-slop-*` namespace so existing registries, dashboards, and decisions remain readable after the rename. This does not affect `$scruffy` or `/scruffy` invocation.

## Repeat an audit without losing history

Treat `findings.json` as the canonical record and the dashboard as a view of that record:

```sh
python3 scripts/migrate_decisions.py previous-decisions.json findings.json decisions.json \
  --prior-registry previous-findings.json
python3 scripts/render_dashboard.py findings.json context.json decisions.json audit-report.html
python3 scripts/render_markdown.py findings.json context.json decisions.json audit-report.md
python3 scripts/validate_audit.py findings.json \
  --baseline previous-findings.json \
  --decisions decisions.json \
  --baseline-decisions previous-decisions.json \
  --dashboard audit-report.html \
  --markdown audit-report.md
```

The validator rejects silent disappearance, ID reuse, broken revision lineage, orphaned decisions, missing report sections, duplicated report items, and dashboards that omit registry entries. The “top eight findings” and “top five enhancements” remain presentation limits only; additional and resolved items are still rendered.

## Grow the research corpus

```sh
python3 scripts/intake.py --channel <youtube-channel-videos-url>
```

Transcripts and frames remain local working material and are ignored by Git. Distill durable, attributed principles into `principles/PRINCIPLES.md`; register sources in `principles/SOURCES.md`; then reconcile the operational instructions and validators. A queued creator contributes nothing until the material has been reviewed and distilled.

Do not sweep fashionable gallery or redesign channels indiscriminately. Separate research-backed rules, implementation evidence, explicit AI-default critiques, visual hypotheses, and promotional material.

## Boundaries

- Framework, agent, browser, and operating system agnostic
- No security certification or vulnerability scan
- No accessibility conformance claim from partial coverage
- No performance verdict without runtime measurement
- No claim of AI authorship from visual resemblance
- No claim of AI authorship from sentence statistics, perplexity, “burstiness,” passive voice, or rhetorical patterns
- No implementation changes from an audit-only request
- No inspection of passwords, cookies, tokens, or browser-storage contents
- Broad web-application coverage is capability-dependent; the skill records checks not run instead of inventing proof

## Credits

The corpus distills and attributes work from Kole Jain; Sergei Chyrkov; DesignCourse; UI Collective; Nielsen Norman Group; Deque Systems; Eleken; Kevin Powell; Tim Gabe; Baymard Institute; Y Combinator Design Review; Steven Haney; W3C; web.dev/Chrome; MDN; Refactoring UI; Practical Typography; Edward Tufte; and Laws of UX. See `principles/SOURCES.md` for exact provenance. No source text is reproduced.

## License

MIT — see `LICENSE`. The license covers this repository’s text and code; cited works remain their authors’ own.
