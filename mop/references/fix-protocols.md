# Fix protocols

One protocol per Scruffy category. Open the section matching the item's
`category`. Each protocol says what *clearing* the finding means, the order to
work in, what to preserve, and the traps that create new slop. All of them sit on
top of [`craft-bar.md`](craft-bar.md) and the dependency order from
[`method.md`](method.md).

A finding is cleared only when its `acceptance_checks` pass in the real usage
scene — not when the code merely differs from before.

---

## `product` — Product slop

The surface has no clear user, job, outcome, or reason to return. These are
usually upstream of everything else; implement them first (lane 1).

- Re-read `product_frame`. The fix must make the confirmed job and success signal
  legible in the interface, not invent a new product.
- Resolve the specific contradiction the finding names (a dead-end terminal state,
  a missing return value, a borrowed feature that serves no job here).
- Do **not** add scope. If the product decision itself is genuinely unmade, that
  is a decision for the user, not a fix to improvise. Record it and ask.
- Cleared when: the named product gap is closed and the primary task reaches a
  real, shareable outcome.

## `information_architecture` — IA slop

People cannot find, address, retrieve, or share what they need (lane 2).

- Fix the structure the finding cites: navigation that exposes the wrong model,
  labels that hide the reader's vocabulary, states with no stable address.
- Prefer real URLs/addressable state over client-only toggles when the finding is
  about shareability or retrieval.
- Keep the reader's existing vocabulary; do not rename things the audit did not
  flag.
- Cleared when: the cited task (find / address / retrieve / share) succeeds with
  evidence, and no sibling path regressed.

## `interaction` — Interaction slop

Controls, state, feedback, or recovery do not behave as promised (lane 3).

- Reproduce the broken operation first. Then give the control honest state:
  pending while in flight, distinct success and failure, and a recovery path.
- Announce state changes to assistive tech (`aria-live`, focus management) as part
  of the same fix — an interaction fix that is invisible to a screen reader is
  half done.
- Preserve existing keyboard and pointer affordances; add the missing ones.
- Cleared when: operating the real task produces correct, perceivable state for
  success, failure, and recovery.

## `accessibility` — Accessibility slop

Semantics, focus, state, contrast, alternatives, or reflow exclude people
(lane 3). Target WCAG 2.2 AA.

- Fix the specific, named barrier with the specific remedy: real contrast (apply
  the token change when `tokens.json` provides one), correct roles and names,
  visible focus, announced state, text alternatives, reflow to 320px.
- Never encode meaning in color alone; pair it with text or shape.
- Verify with the accessibility tree and keyboard, not by eye.
- Cleared when: the named check passes under real assistive operation; nothing you
  touched introduced a new barrier.

## `visual` — Visual slop

Decoration and interchangeable composition replace hierarchy and identity
(lane 4). This is the headline category: for anything beyond a trivial token fix,
follow the first-class path in [`visual-redesign.md`](visual-redesign.md)
(capability preflight, optional design-reference grounding, impeccable-or-floor).

- Restore the hierarchy the finding says is lost: let the primary figure or action
  lead; remove the arbitrary gradient/badge/radius the audit cited.
- Work through tokens (color, space, type scale, radius), not one-off literals.
  Consolidate duplicated styles into the existing token layer.
- Preserve product identity and any binding brand constraint; do not substitute
  your taste for a pinned direction.
- Cleared when: rendered evidence shows the intended first fixation and restored
  scanning order, with no new decorative noise.

## `copy` — Editorial slop

Words, claims, labels, sequence, voice, or provenance fail at the moment of
action (lane 5). Editorial fixes change reader-facing text; move carefully.

- Verify what the reader actually sees, then rewrite for the specific consequence
  the finding names: interchangeable claims → concrete, checkable differences;
  unsupported claim → supported or removed; vague microcopy → the exact next
  action.
- **Ask before inventing facts.** Do not fabricate numbers, testimonials, plan
  limits, or provenance to make a claim concrete. If the real value is unknown,
  ask the user; do not guess.
- Keep the established voice from `product_frame`/brand. Never turn an editorial
  fix into an AI-authorship judgment — that is explicitly outside the method.
- Cleared when: the reader can make the choice / recover / trust the claim at the
  point of action, in the product's own voice.

## `backend_shape` — Structure slop

Routes, data, state, content, or components are shaped so several features fail
together (lane 1). These are the blockers other items depend on.

- Fix the shared cause once: extract the fused state/module, give navigation state
  a real address, tokenize copied styles, replace an empty catch with real
  handling.
- Land the structural change before the symptoms that `depends_on` it. The plan
  already orders these first; keep it that way.
- Migrate completely — a half-extracted module that leaves two sources of truth is
  worse than before.
- Cleared when: the shared cause is single-sourced and every dependent symptom the
  registry links is resolved by it.

## `performance` — Performance slop

Loading or interaction is slow, unstable, wasteful, or dishonest about waiting
(lane 5).

- Fix the measured cause the finding cites (render-blocking resource, layout
  shift, blocking third party, oversized payload, dishonest spinner), not a
  guessed one.
- Preserve correctness and accessibility while optimizing; a faster page that
  drops a landmark or a state has regressed.
- Where you cannot measure, say so; do not claim a performance win you did not
  observe.
- Cleared when: a repeatable measurement shows the user-visible harm is gone and
  nothing else regressed.

---

## Cross-cutting facets

When an item carries a `facets` entry (trust and content integrity, resilience and
recovery, localization and adaptability, agent/AI behavior, privacy and safety
UX), honor it *inside* the category protocol above — it refines the fix, it does
not replace it. A `resilience_recovery` interaction fix must include the recovery
path; a `trust_integrity` copy fix must not trade one unsupported claim for
another.
