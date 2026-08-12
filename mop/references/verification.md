# Verification and handoff

Scruffy's Mop verifies its own work enough to hand back honestly, but it never
issues the clearance. Only a Scruffy re-audit of a new revision moves an item to
`fixed`/`cleared`. This file covers the self-check before handoff and the handoff
itself.

## Self-check (before you call anything done)

For each implemented item, run its `acceptance_checks` yourself, in the real usage
scene from `context.json` `tasks`:

- **Operate, don't inspect.** Drive the actual task — click, type, tab, reload —
  the way the check describes. A check that only passes when read from the source
  has not been verified.
- **Record a result per check:** `meets`, `partial`, or `unmet`. Be honest;
  `partial` and `unmet` are legitimate outcomes to hand back, and far better than
  a false `meets` that the re-audit will expose.
- **Regression sweep.** Confirm you introduced no new slop (see the anti-camouflage
  tests in [`craft-bar.md`](craft-bar.md)) and that everything outside the approved
  scope is unchanged where it should be.

Verify with the right instrument: keyboard and the accessibility tree for
`accessibility` and `interaction`; rendered evidence for `visual`; a repeatable
measurement for `performance`; the reader's real decision point for `copy`.

## Build the handoff

Write a `work.json` mapping each implemented item to what changed and your
self-check:

```json
{
  "AS-04": {
    "surfaces": ["src/billing/state.ts", "src/billing/BillingSummary.tsx"],
    "notes": "Extracted a single billing-state module; all three surfaces read it.",
    "self_check": [
      {"check": "A single module is the only source of invoice total, tax, and dunning state", "result": "meets"},
      {"check": "Summary, PDF, and email render identical totals for the same invoice", "result": "meets"}
    ]
  }
}
```

Then generate the handoff:

```sh
python3 scripts/mop_handoff.py <bundle-dir> --work work.json --authorized
```

The output records every item as `implemented-pending-reaudit` with
`cleared_by: pending Scruffy re-audit`. It lists any approved-but-unimplemented
items. It contains no `fixed`/`cleared` status — by construction, `mop_handoff.py`
cannot emit one.

## Return and recommend

Give the user:

1. The changed surfaces, mapped to registry IDs.
2. The handoff (Markdown for reading, `--json` for the next tool).
3. An honest statement of any `partial`/`unmet` checks and anything you had to ask
   about or leave for a follow-up audit.
4. The recommendation to **re-run Scruffy** on the new revision so the registry
   moves items to `fixed`/`cleared` on real evidence — closing the loop.

If you cannot verify a check in this environment (no browser, no trace), say so
plainly and mark it `partial` with the reason. Never turn an unrun check into a
pass.
