# Plan — Adversarial dashboard derby (Claude × Codex, Mobbin-grounded, Zach decides)

**Status:** KICKOFF STAGED 2026-08-10 (Zach: "implement plan"). Shared inputs frozen in `../derby-2026-08-10/shared/` (BRIEF.md + fixture-dense.json, 42 items, seeded); lane dirs created; codex handoff packet issued at `../derby-2026-08-10/codex/HANDOFF_PACKET.md`. Awaiting P0 per lane. Coordination doc, untracked; delete after the derby completes and results are filed.

**Leadership:** none — the lanes are parallel peers in Phases 1–3 (symmetry prevents anchoring; a leading lane would contaminate the second opinion). Codex has two *housekeeping* duties before its Phase 1 (commit in-flight work + fold the work order), which do not gate the Claude lane. The winning lane leads Phase 5 only.
**Objective:** redesign the scruffy **decision-dashboard experience** (`scripts/render_dashboard.py` + `report_contract.py` output) through two independent, Mobbin-grounded design lanes run adversarially, converging to **exactly two rendered options for Zach's decision**. The winning direction is implemented in the repo. The derby doubles as the first real exercise of `references/reference-grounding.md` and a behavioral-parity data point toward roadmap **R6**; the self-audits double as **R2**-style dogfooding.

## Preconditions (hard gates)

- **P0 — Mobbin connected in BOTH lanes.** Claude lane: directory connector (`claude.ai/directory/connectors/mobbin`) — verified NOT visible in the 8/10 planning session; Zach's OAuth click pending. Codex lane: Mobbin lists Codex CLI/App as supported clients — register per `docs.mobbin.com/mcp/clients/codex-cli` with the same paid account. A lane without Mobbin runs corpus-only and must disclose it; a corpus-only derby defeats the point — do not start until both lanes confirm `search_screens` reachable.
- **P1 — gates Phase 5 only (relaxed at kickoff, 2026-08-10):** codex commits or stashes its in-flight work (13 dirty files incl. `render_dashboard.py`) and folds `WORK-ORDER-reference-grounding.md` before any implementation lands. Phases 1–4 are repo-read-only by construction, so design may start in parallel with the housekeeping.
- **P2 — Authority per `references/audit-contract.md`:** Phases 1–4 run as DESIGN exploration with **no repository writes** (prototypes live outside the repo). Phase 5 is REDESIGN with explicit authority = Zach's recorded pick.

## Shared frozen inputs (identical for both lanes, fixed before start)

1. **The brief:** the dashboard is a *decision instrument* — a non-designer owner triages findings, approves/defers/rejects, and relays a summary; agents are the second reader (machine-readable state). Each lane answers scruffy's six framing questions independently as work product; the brief deliberately does not answer them.
2. **Render data:** `evals/continuity/` fixture (anonymized 17-record registry) — every prototype renders it for real, plus two mandatory extra states: **empty registry** and **dense** (≥40 findings, synthetic extension committed to the derby dir so both lanes use the same file). Aging must be visible.
3. **Mobbin budget:** 3–8 pulls per lane, `reference-grounding.md` discipline — concrete surface+domain+state queries, named patterns, app+link citation per borrowed pattern, popularity≠merit guards. Query log is a required artifact.
4. **Output isolation:** co-located at `Nagops/design-audit/derby-2026-08-10/` — `claude/` and `codex/` lane dirs beside `shared/`. Lanes MUST NOT read each other's directories before the Phase 3 exchange (blind-audit quarantine ethos; violation = lane restarts its phase). Each lane runs in a fresh session reading only the vault entry point, this plan, and `shared/BRIEF.md`.

## Phases

**1 · Frame + ground (parallel, isolated, ~1 session/lane).** Product frame answers → Mobbin pulls → a one-page direction brief: chosen paradigm candidates, borrowed patterns with citations, what was deliberately rejected from references and why.

**2 · Design (parallel, isolated, ~1 session/lane).** Each lane builds **two** structurally different candidate directions as self-contained HTML prototypes (real fixture data, all three states, full-width). Validity test applies: describable-with-one-adjective-swap = one variant, start over. Each lane then runs a scruffy **AUDIT on its own two**, kills its weaker candidate, and records the kill reason. Output per lane: 1 survivor + self-audit registry + kill memo.

**3 · Adversarial exchange (~1 session/lane).** Lanes swap survivors. Each runs a full scruffy AUDIT on the opponent's prototype — findings capped at 8 with receipts, **plus a mandatory steal list (≥2 things the opponent did better)**. Then each lane gets exactly **one revision pass** on its own survivor: fix what it concedes, defend what it disputes with evidence (measurements, references, fixture behavior — never taste). No design-by-committee; the two survivors stay two distinct paradigms.

**4 · Zach decides (one sitting, ~10 min).** Present both finals stacked full-width, live-rendered on the fixture: paradigm name in one line, borrowed Mobbin patterns cited, the opponent's strongest UNRESOLVED finding printed under each (transparency beats advocacy), both lanes' agreement stats from the cross-audits. Zach picks A or B (or rejects both → one loop back to Phase 2 with his verdict as a new frozen constraint — one loop max). His pick is recorded as the explicit-authority receipt + a vault decision record; his stated reasons go to the taste library same-day.

**5 · Implement (winning lane, ~1 session).** Land the direction in `scripts/render_dashboard.py`/`report_contract.py`: re-render the continuity fixture, before/after screenshots, `validate_skill.py` + report-contract tests green, CHANGELOG entry, version bump. Surviving steal-list items from the losing direction are filed to `SCRUFFY-IMPROVEMENTS.md` with attribution.

**6 · Retro (both lanes, scruffy §8).** Reusable lessons only; cross-lane agreement rate recorded as an R6 data point; reference-grounding friction (query misses, rate limits, gallery issues in Cowork/Code) filed against the work order.

## Rules that keep it honest

- Zach is the only decider; the cross-audits are evidence for his decision, not a tribunal.
- Every visual claim in the cross-audits needs rendered evidence; behavioral claims need the measurement, per the evidence rules.
- Mobbin references inform structure and convention — no trade-dress copying, no citing unpulled screens, no popularity-as-merit.
- Prototypes are disposable lab-layer HTML; only Phase 5 writes product code.
- If either lane cannot honestly meet a gate, it says so in one line and the derby waits. No corpus-only silent fallback.

## Kickoff checklist

- [ ] Zach: Mobbin OAuth (Claude directory connector) — unblocks Claude lane
- [ ] Zach or codex: Mobbin MCP registered for Codex CLI — unblocks codex lane
- [ ] Codex: fold `WORK-ORDER-reference-grounding.md`, commit/stash dirty files
- [ ] Codex: handoff packet issued from vault `templates/HANDOFF_PACKET.md` referencing this plan
- [ ] Both lanes confirm `search_screens` reachable → derby starts at Phase 1
