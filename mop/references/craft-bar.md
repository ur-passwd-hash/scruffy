# Craft bar

The quality floor that separates **clearing** a finding from **camouflaging** it.
A change that makes the acceptance check technically pass while leaving the
user's experience mediocre is a failure, even if a lint passes. Scruffy's re-audit
operates the real task; so must your fix.

## A free floor, augmented when available

Scruffy's repair stage carries its own craft bar (this file) and depends on nothing to
apply it. This free floor keeps it portable across Claude, Codex, and other Agent
Skills runtimes — the same portability that is Scruffy's contract. Every fix must
clear the floor no matter what else is available.

On top of the floor, two optional augmentations raise craft on visual/product work
(see [`visual-redesign.md`](visual-redesign.md) and `augmentations` in
[`../schema/interop.json`](../schema/interop.json)):

- **impeccable** — free, and first-class *when present* (Claude Code and other
  runtimes that have the skill). Use it to drive elevated visual and interaction
  craft, strictly within the approved scope. It is still never a hard dependency:
  when it is absent you apply this floor directly and the result must still clear
  the bar.
- **design-reference search** (Mobbin or any equivalent) — paid, so strictly
  optional. When present, ground a redesign direction in real shipped products and
  cite it. When absent, disclose that and proceed on the floor.

Detect at runtime, use what is present, disclose what is absent. An absence is
never a blocker, never a defect, and never added as a hard dependency in a
manifest.

## The floor every fix must clear

- **Fix the cause named in the registry, not the symptom.** If `cause` says state
  is fused to the view, extract the state; do not paper over the visible mismatch.
- **Satisfy the acceptance check in the real usage scene.** Operate the task the
  way `context.json` `tasks` describes it, at the widths and inputs a real user
  brings, before believing your own fix.
- **Smallest coherent change.** Prefer the edit that resolves the item and no
  more. Coherent means it does not leave a half-migrated seam behind.
- **Preserve product truth and voice.** Everything in `product_frame`, the
  product's real content, its function, and its established voice survive
  unchanged unless the approved item is explicitly about changing them.
- **No new slop.** A fix that introduces a fresh accessibility barrier, a new
  interchangeable label, an arbitrary token, or a dead interaction has failed,
  even if its own acceptance check passes. You are the tool that clears slop; do
  not deposit more.
- **Tokens over literals.** When a token layer exists, change the token. When it
  does not and a token change is warranted, extract the token as part of the fix
  and note it, rather than sprinkling a literal.
- **State honesty.** Every interactive surface you touch keeps working ready,
  empty, loading, error, and success states. A change that only handles the happy
  path is not finished.
- **Accessibility is not optional.** Target WCAG 2.2 AA on anything you implement
  or generate: keyboard path, visible focus, correct roles and names, contrast,
  announced state, and reflow. Clearing an `accessibility` finding means meeting
  its named check, not approximating it.

## Anti-camouflage tests

Before you consider an item done, ask:

1. Would this survive Scruffy operating the real task again? If it only survives a
   screenshot, it is camouflage.
2. Did I fix the `cause`, or hide the `observation`?
3. Did I introduce anything a fresh audit would flag?
4. Is everything outside the approved scope byte-for-byte unchanged where it
   should be?

If any answer is uncomfortable, the fix is not at the bar yet.
