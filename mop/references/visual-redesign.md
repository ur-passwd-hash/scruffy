# Visual redesign (first-class path)

Visual and product findings are the headline job. When an approved item's fix is a
design change — restoring hierarchy, replacing interchangeable composition,
rebuilding a weak component, upgrading a whole visual surface — follow this path
instead of a minimal patch. It layers on top of the `visual`/`product` protocols
in [`fix-protocols.md`](fix-protocols.md) and the floor in
[`craft-bar.md`](craft-bar.md).

The augmentation model is machine-readable in
[`../schema/interop.json`](../schema/interop.json) under `augmentations`.

## 1. Capability preflight — probe, never assume

Run the preflight and record what it finds. **The rule: a capability is `absent`
only after a probe fails. Omission is `not_run`, never `absent`.** Assuming a
capability was missing once produced confident, false disclosures — the exact
failure the method forbids.

```sh
python3 scripts/mop_preflight.py \
  --impeccable available|absent [--impeccable-reason "..."] \
  --design-reference-search available|absent [--design-reference-search-reason "..."]
```

- **browser** (free renderer): probed **mechanically** by the script — it locates
  a headless Chrome/Chromium/Edge/Brave and reports the version, or `absent` only
  after finding none. You need it for real screenshot evidence.
- **impeccable** (free craft engine): a runtime/MCP capability the script cannot
  call, so **you** must probe it (is the skill actually available?) and pass the
  attested result. If present, drive visual work through it; if a probe shows it
  absent, use the built-in craft floor. Either way the fix must clear the bar.
- **design-reference search** (paid; Mobbin is the reference connector, any
  equivalent satisfies it): also agent-probed — actually issue a test query. Maps
  to Scruffy's `design_reference_search` capability. Marking it `absent` requires a
  real failed probe and a reason; the script refuses `absent` otherwise.

Feed the preflight report into the handoff and the dashboard so the disclosure is
the observed truth, not a guess.

## 2. Ground the direction (optional; paid)

If a design-reference search is available:

- Query it for how real shipped products in this app's archetype solve the
  specific problem the finding names (e.g. a billing status, an empty state, a
  pricing comparison).
- Use the references to choose a direction; cite what you drew on in the handoff.
- Never copy a reference wholesale, and never let it override product truth or a
  binding brand constraint.

If it is not available: say so plainly in the handoff, and proceed with the
built-in method. Absence lowers grounding confidence; it does not lower the craft
bar and is not a finding.

## 3. Implement to the highest craft available

- **impeccable present:** drive the visual/interaction change through it, scoped
  strictly to the approved finding. It raises craft; it does not widen scope,
  change product truth, or redesign surfaces Scruffy did not flag.
- **impeccable absent:** apply the built-in craft floor directly — restore the
  intended first fixation and scanning order, work through the existing token
  layer (color, space, type scale, radius), remove arbitrary decoration, and keep
  every state (ready, empty, loading, error, success) working.

Either way: preserve product truth from `product_frame`, keep content and function
intact, honor binding brand constraints, and hold WCAG 2.2 AA on anything you
touch.

## 4. Stay inside the finding

The redesign clears the approved finding — it is not a licence to restyle the app.
If doing it well seems to require changes Scruffy did not find, record those for a
follow-up audit rather than smuggling them in.

## 5. Deliver a self-contained dashboard

The operator reads Mop output in a terminal, so the deliverable is a **single
self-contained HTML dashboard** with every screenshot and reference image embedded
as a `data:` URI — no sibling folder, no external fetch, no login-gated link
needed to render. Build it with the generator, which fails closed if any image
would load externally:

```sh
python3 scripts/mop_dashboard.py <bundle-dir> --assets assets.json --out dashboard.html --authorized
```

The assets manifest carries the embedded screenshots, the shipped-product
references (with their provenance URLs as hrefs), the preflight report, and any
per-item directions. Rendered evidence and grounding thus live *in the file*, not
in chat the operator cannot see richly.

## 6. Disclose in the handoff

The handoff and the dashboard footer report which augmentations were `used` vs
`absent` (browser, impeccable, design-reference), sourced from the preflight — the
observed truth, never a guess. Use `mop_handoff.py --augmentations`. As always,
the repair stage marks the item `implemented-pending-reaudit`; only Scruffy's re-audit
clears it.
