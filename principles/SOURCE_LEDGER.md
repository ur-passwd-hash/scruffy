# SOURCE_LEDGER — the committed record of what was ingested

`/transcripts/` and `/frames/` are gitignored. That is the right call: raw
creator transcripts are working material and are not redistributed. The cost is
that the repo has had **no durable record of what was ever pulled in**. When a
transcript is deleted or a machine changes, the evidence behind a cited rule
vanishes while the citation survives, and nothing notices.

This file is that record. `scripts/validate_sources.py` enforces it.

`principles/SOURCES.md` answers *which creators are admissible and why*.
This file answers *which specific videos entered, and did any rule come out*.

## Status vocabulary

| Status | Meaning | Validator behaviour |
|---|---|---|
| `queued` | Identified, not yet fetched | No citation required |
| `ingested` | Transcript pulled, **not yet distilled** | **FAILS** until ≥1 citation exists |
| `distilled` | ≥1 `[video_id t]` citation in PRINCIPLES.md | Passes |
| `rejected` | Reviewed, produced no admissible rule | No citation required; keep the row so it is never re-ingested |

`ingested` is deliberately a failing state. A source that sits in a folder
without producing a cited rule is not research, it is hoarding. The build says so.

## Evidence column

`local transcript` — file present in `/transcripts/`.
`vault` — copy in the vault `sources/transcripts/` layer (survives repo churn).
`none retained` — cited, but no artifact survives anywhere. The rule stands on
an unverifiable citation and raises `EVIDENCE_LOST`.

---

## Pending

| video_id | creator | status | evidence | notes |
|---|---|---|---|---|
| `RCneB_MQ7qs` | Kole Jain | queued | none retained | "The one thing vibe coding CAN'T fix about your website" — supplied by Zach 2026-08-19. Founding-source creator; admission gates already satisfied by SOURCES.md row 1. Expected landing zone §7 / §19 (vibe-code tells) and §8 (landing-page ladder). |

## Founding corpus — Kole Jain (evidence lost)

Cited across PRINCIPLES §1–20 (~120 rules). **No transcript for any of these
survives in `/transcripts/`.** The citations are almost certainly accurate — they
carry specific timestamps and were written against real material — but they are
no longer auditable, and no rule sourced here can currently be re-verified,
corrected, or defended against a challenge. Recovering them is a re-sweep of
`https://www.youtube.com/@KoleJain/videos`.

Attribution below is inherited from `SOURCES.md` row 1 (which assigns §1–20 to
Kole Jain) and has not been individually verified per id.

| video_id | creator | status | evidence | notes |
|---|---|---|---|---|
| `Ksx9C2-3yMo` | Kole Jain | distilled | none retained | §1–2 data-driven form, progressive disclosure |
| `B7k5rOgmOGY` | Kole Jain | distilled | none retained | §1–3 data UI, invisible UI |
| `EcbgbKtOELY` | Kole Jain | distilled | none retained | high-frequency source across §3–13 |
| `EOcY3hPMQkk` | Kole Jain | distilled | none retained | §6 color |
| `PDcQJOPby1k` | Kole Jain | distilled | none retained | §7 vibe-coded tells, §8 universal tells |
| `eMMiLeo_UGI` | Kole Jain | distilled | none retained | §8 four-levels landing-page ladder (bare citation, no timestamp) |
| `AH_ugxmLeUM` | Kole Jain | distilled | none retained | §9–17 spanning source |
| `7sUUzOCv47U` | Kole Jain | distilled | none retained | §10 typography numbers |
| `c1TvOcKdBVE` | Kole Jain | distilled | none retained | §10–14 numbers and components |
| `Lp6ey4AyDzA` | Kole Jain | distilled | none retained | §10–15 spanning source |
| `9WVt1CelBfg` | Kole Jain | distilled | none retained | §10–11 |
| `V3Omp1hm0Sg` | Kole Jain | distilled | none retained | §10–18 |
| `gKM6b2EnW1k` | Kole Jain | distilled | none retained | §12–16 components and charts |
| `BvbFPzLjWcU` | Kole Jain | distilled | none retained | §12, §21 |
| `SfX43uIubj4` | Kole Jain | distilled | none retained | §12, §18, §20–22 |
| `HE4rLEQpiXY` | Kole Jain | distilled | none retained | §12, §17 |
| `66oOi9OLMCw` | Kole Jain | distilled | none retained | §13 components |
| `Vy0KKvZJRH8` | Kole Jain | distilled | none retained | §13, §16 |
| `6CC8lLnqa28` | Kole Jain | distilled | none retained | §13, §17 |
| `NtZeYmTMuo4` | Kole Jain | distilled | none retained | §13, §17 |
| `Yr2uIcFZDDQ` | Kole Jain | distilled | none retained | §14–15 charts, mobile, §21 |
| `Gfsd8NNuD9g` | Kole Jain | distilled | none retained | §14, §16 |
| `pGYLZyBE32o` | Kole Jain | distilled | none retained | §14 charts |
| `P2ksReDwWkE` | Kole Jain | distilled | none retained | §14, §18 |
| `14h1VnkQvIc` | Kole Jain | distilled | none retained | §14, §16–17 |
| `goWOAFqJHpA` | Kole Jain | distilled | none retained | §16 motion, §20 |
| `ixUq4HM4FNg` | Kole Jain | distilled | none retained | §16 motion |
| `ld1zhQMXxXU` | Kole Jain | distilled | none retained | §17 section library |
| `d4MF6pdAZNw` | Kole Jain | distilled | none retained | §17 section library |
| `nl8OFGdx75w` | Kole Jain | distilled | none retained | §17 section library |
| `ZsP20PN14O0` | Kole Jain | distilled | none retained | §17 section library |
| `tNMAFjzapOk` | Kole Jain | distilled | none retained | §17 section library |
| `VPeTgU7la34` | Kole Jain | distilled | none retained | §18 AI-product UI patterns |
| `A_Ozpb0XDuw` | Kole Jain | distilled | none retained | §17 |
| `EHwZzWd-OnQ` | Kole Jain | distilled | none retained | §18 |
| `ulSOdTgoGeY` | Kole Jain | distilled | none retained | §18 |
| `If7iCPDy2vk` | Kole Jain | distilled | none retained | §19 vibe-code tells expanded |
| `xHD01_Onac0` | Kole Jain | distilled | none retained | §20 engagement mechanics |
| `5JxUJ1fuyO8` | Kole Jain | distilled | none retained | §20 |
| `jSxxAFxjxbU` | Kole Jain | distilled | none retained | §20 |
| `BUDipdbKK7Y` | Kole Jain | distilled | none retained | §20 |

## Pilot and targeted corpus (evidence retained)

Pulled during the 2026-08-08 → 2026-08-10 pilots. Transcripts present locally;
still absent from the vault, so a `/transcripts/` wipe would reproduce the
founding-corpus failure. Vault backfill is the fix.

| video_id | creator | status | evidence | notes |
|---|---|---|---|---|
| `T96O8dTzi2Q` | Sergei Chyrkov | distilled | local transcript | §23 |
| `1MdwweKCNwg` | Sergei Chyrkov | distilled | local transcript | §23 |
| `1d8vM0TXcTo` | Sergei Chyrkov | distilled | local transcript | §23 |
| `YSYqFBq68Wk` | DesignCourse | distilled | local transcript | §24 |
| `q1lGlhRnzsM` | DesignCourse | distilled | local transcript | §13, §24 |
| `0_PuRInJFrc` | DesignCourse | distilled | local transcript | §24 |
| `4vItmdk8F_M` | UI Collective | distilled | local transcript | §25 |
| `guRNce9XMp4` | UI Collective | distilled | local transcript | §25 |
| `gIvxgXRGGpk` | UI Collective | distilled | local transcript | §25 |
| `nbk0PMS0tos` | UI Collective | distilled | local transcript | §25 |
| `odk2fkPNVRA` | NNgroup | distilled | local transcript | §26 |
| `WmmBLgtkjN4` | NNgroup | distilled | local transcript | §26 |
| `mqNSTz5sX6E` | NNgroup | distilled | local transcript | §26 |
| `UR8jF5xqjnk` | NNgroup | distilled | local transcript | §26 |
| `Yps3BHLE0yY` | Deque Systems | distilled | local transcript | §27 |
| `LaS00N9pOt0` | Deque Systems | distilled | local transcript | §27 |
| `CZ0SG4pH-yM` | Deque Systems | distilled | local transcript | §27 |
| `_eDRLi0C6a4` | Deque Systems | distilled | local transcript | §27 |
| `QtgCnSWZkt4` | Eleken | distilled | local transcript | §28 |
| `K8yLcutmp-M` | Eleken | distilled | local transcript | §28 |
| `rP-I4Oihqc8` | Eleken | distilled | local transcript | §28 |
| `JGmcG1vRmuw` | Eleken | distilled | local transcript | §28 |
| `pJ0GPI7BMIs` | Kevin Powell | distilled | local transcript | §29 |
| `YAqRQoN8ykI` | Kevin Powell | distilled | local transcript | §29 |
| `fI9VM5zzpu8` | Kevin Powell | distilled | local transcript | §29 |
| `BxhsCu9hNpY` | Tim Gabe | distilled | local transcript | §30 |
| `Aa89MC8jX2c` | Tim Gabe | distilled | local transcript | §30 |
| `LXX_qOA5D8E` | Tim Gabe | distilled | local transcript | §30 |
| `Du2lkZ_cux8` | Tim Gabe | distilled | local transcript | §30 |
| `vv74GmBXxHE` | Baymard Institute | distilled | local transcript | §21, §31 |
| `fuAdtcqLC6I` | Baymard Institute | distilled | local transcript | §31 |
| `ss0jhpbAidc` | Baymard Institute | distilled | local transcript | §31 |
| `RynySryqM_0` | Y Combinator (Design Review) | distilled | local transcript | §10, §21, §23, §32 |
| `DBhSfROq3wU` | Y Combinator (Design Review) | distilled | local transcript | §23, §32 |
| `ORgKY9AlybA` | languagejones | distilled | local transcript | §21, §33 |

## Withdrawn coverage claim

| video_id | creator | status | evidence | notes |
|---|---|---|---|---|
| `P06RgnUKX_I` | Y Combinator — Steven Haney (Paper) | queued | none retained | Was recorded in SOURCES.md as **Distilled** with coverage at "skill §C direct". Audit 2026-08-19: **no `[P06RgnUKX_I]` citation exists in PRINCIPLES.md or SKILL.md**, and no transcript survives, so nothing traceable came out of it. The claim is withdrawn rather than defended — this is the third YC *Design Review* episode and belongs in §32 alongside `RynySryqM_0` and `DBhSfROq3wU`, but restoring it needs a re-fetch. Returned to `queued`. |

## Maintenance

Regenerate candidate rows for anything cited or on disk but unlisted:

```bash
python3 scripts/validate_sources.py --backfill
```

Check the invariant (add `--vault-dir` once vault backfill is done):

```bash
python3 scripts/validate_sources.py --strict
```

Rules:

- Never delete a row. `rejected` exists so a dead end is not silently re-ingested.
- A row flips to `ingested` the moment a transcript lands. The build then fails
  until a cited rule comes out of it. That failure is the feature.
- Section notes in this file are a convenience. `validate_sources.py` recomputes
  sections and citation counts from `PRINCIPLES.md` at run time; the script wins.
