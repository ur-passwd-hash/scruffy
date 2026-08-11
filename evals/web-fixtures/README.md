# Known-answer web fixtures

Three self-contained pages with planted defects and adjacent legitimate patterns.
They measure discrimination: can an audit tell a real defect from a lookalike that
must not be flagged. Every inspection point carries a `data-sample` attribute; the
expected disposition for each point lives only in `keys/expectations.json`.

| Page | Sampled categories |
|---|---|
| `checkout-flow.html` | interaction, information_architecture, visual |
| `pricing-page.html` | copy, visual |
| `settings-form.html` | accessibility, interaction |

## Contamination rule

`keys/` is the answer key and `runs/` archives scored past runs (dispositions,
reconciliations, and evaluator output). Never open either during an audit of these
fixtures, and list both as forbidden inputs in every blind manifest that targets them:

```sh
python3 scripts/blind_protocol.py prepare \
  --target evals/web-fixtures/ \
  --agent <agent> \
  --prompt-file <neutral-prompt> \
  --skill-root . \
  --allow evals/web-fixtures/checkout-flow.html \
  --allow evals/web-fixtures/pricing-page.html \
  --allow evals/web-fixtures/settings-form.html \
  --forbid evals/web-fixtures/keys/expectations.json \
  --forbid-marker web-fixtures/keys \
  --forbid-marker web-fixtures/runs \
  --test-id <id> --output <dir>/blind-manifest.json
```

## Neutral run prompt

Serve the directory (`python3 -m http.server`) and give the auditing session only this:

> Audit the three local pages end to end using the Scruffy skill. Operate every
> control. For every element carrying a `data-sample` attribute, record exactly one
> entry in a discovery JSON: a candidate (with a temporary CAND-NNN id, two
> independent signals, evidence, consequence, a tested counterexample, and
> confidence), a cleared suspicion, or a check not run. Record
> `"phase": "blind_discovery"` and `"authorship_assessment": "not_performed"`.
> Do not open anything under `keys/`.

## Scoring

```sh
python3 scripts/evaluate_blind_outputs.py \
  --key evals/web-fixtures/keys/expectations.json \
  --discovery <run>/blind-discovery.json
```

The result reports matched samples, mismatches, and integrity problems. Twelve
samples: six planted defects that must become candidates, six legitimate patterns
that must be cleared. Extra key fields (`category`, `planted`, `detectable_by`)
document the fixture; the evaluator reads only `expected_disposition`.

Editing a fixture page invalidates the key: update both in the same change and run
`python3 scripts/test_web_fixtures.py`.
