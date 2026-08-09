# Blind audit and reconciliation protocol

A blind audit separates independent discovery from historical reconciliation. It prevents a prior report, expected finding list, or discussion from turning the next run into a confirmation exercise. Blindness is a workflow property with an auditable boundary, not a request to “pretend” context was forgotten. The binding rule is **freeze before reveal**.

## When to use it

Use this protocol when the user asks for a blind test, independent audit, fresh-eyes review, inter-agent comparison, or detector evaluation. A normal repeat audit still loads the baseline first under the durability protocol.

## Phase 1 — quarantine and discover

1. Define the target and allowed inputs. Include only the live target, source or copy packet needed to inspect it, product framing explicitly supplied for this run, and this skill’s runtime instructions.
2. List forbidden inputs: prior reports, findings registries, decisions, dashboards, work orders, expected answers, evaluation labels, and conversation summaries that reveal prior results.
3. Create `blind-manifest.json` before discovery. Record the target, agent/runtime label, exact prompt hash, skill-tree hash, allowed-input hashes, forbidden paths or markers, timestamp, and `phase: blind_discovery`.
4. Do not search the workspace for baselines, stable IDs, or related reports during this phase. If a forbidden artifact is encountered accidentally, stop and mark the run contaminated; do not rely on memory to subtract its influence.
5. Use temporary IDs such as `CAND-001`. Do not guess stable IDs or prior dispositions.
6. Write `blind-discovery.json` with candidate findings, strengths, cleared suspicions, capabilities, checks not run, and evidence. It must not mention baseline counts, prior IDs, or expected labels.
7. Freeze the discovery by recording its SHA-256 digest and timestamp in `blind-freeze.json`. Any later change invalidates the blind phase.

Use `python3 scripts/blind_protocol.py prepare`, `freeze`, and `verify` when command execution is available. Otherwise create equivalent JSON and disclose that integrity was checked manually.

## Phase 2 — reveal and reconcile

Only after the discovery digest is frozen:

1. Load the prior registry, reports, and decisions.
2. Map each temporary candidate to an existing immutable `identity_key`, a cleared suspicion, or a genuinely new issue.
3. Give every baseline item an explicit disposition under [durability.md](durability.md). Blind discovery does not authorize silent disappearance.
4. Preserve earlier decisions and history. A candidate’s novelty is not evidence of higher severity, and failure to rediscover an item does not clear it.
5. Create stable IDs for truly new findings only now.
6. Publish a reconciliation table with: blind candidate, baseline match, disposition, evidence change, and decision carry-forward.

## Cross-agent parity test

For comparisons between agents:

- Give each fresh, non-resumed session the same target packet, skill-tree digest, prompt, output schema, tool/capability budget, and time or cost ceiling.
- Do not name expected issues in the prompt. Keep evaluation labels outside every agent-readable directory.
- Freeze each output before opening another agent’s result.
- Compare observable coverage, evidence quality, false positives, cleared suspicions, and schema adherence. Raw finding-count agreement is not sufficient.
- Report environmental differences such as browser access, source access, or model/runtime version. They are confounders, not agent quality.

## Contamination rules

A run is contaminated when any of these occurs before freeze:

- the prompt contains a prior finding, expected label, stable ID, or baseline count;
- the agent reads or is shown a prior report, decision file, work order, or evaluation key;
- a resumed conversation contains substantive findings for the same target;
- discovery is edited after the agent sees the baseline;
- the skill tree changes between compared runs without a new manifest.

When contaminated, retain the artifact for diagnosis but do not label it blind. Start a new isolated session with a new manifest.

## Required blind artifacts

```text
blind-manifest.json
blind-discovery.json
blind-freeze.json
blind-reconciliation.json   # only after reveal when a baseline exists
```

The final report must state whether blindness was verified, contaminated, or not run. It must also distinguish blind discoveries, baseline-only findings, and post-reveal interpretation.
