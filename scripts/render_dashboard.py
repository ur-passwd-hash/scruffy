#!/usr/bin/env python3
"""Render a complete, self-contained Scruffy decision dashboard."""

from __future__ import annotations

import argparse
import base64
import html
import json
import mimetypes
from pathlib import Path
from typing import Any

from report_contract import (
    capability_rows,
    checks_not_run,
    evidence_by_id,
    evidence_summary,
    product_rows,
    public_category_label,
    score_rows,
    task_rows,
)


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"FAIL: {path} must contain an object")
    return data


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def embed_asset(src: str, base: Path) -> str:
    path = Path(src)
    if not path.is_absolute():
        path = base / path
    if not path.is_file():
        return ""
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def list_html(values: list[Any], empty: str = "None recorded.") -> str:
    if not values:
        return f'<p class="quiet">{esc(empty)}</p>'
    return "<ul>" + "".join(f"<li>{esc(value)}</li>" for value in values) + "</ul>"


def table_html(headers: list[str], rows: list[list[Any]], class_name: str = "") -> str:
    head = "".join(f"<th scope=\"col\">{esc(value)}</th>" for value in headers)
    body = "".join("<tr>" + "".join(f"<td>{esc(value)}</td>" for value in row) + "</tr>" for row in rows)
    return f'<div class="table-wrap"><table class="{esc(class_name)}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def decision_control(item: dict[str, Any], decision: dict[str, Any] | None) -> str:
    if item["kind"] not in {"finding", "enhancement"} or item["status"] not in {"open", "needs-verification"}:
        return ""
    current = (decision or {}).get("decision", "pending")
    note = (decision or {}).get("note", "")
    options = "".join(
        f'<option value="{value}"{" selected" if current == value else ""}>{value}</option>'
        for value in ("pending", "approve", "defer", "reject")
    )
    item_id = esc(item["id"])
    return f"""
      <div class="decision-row">
        <label>Decision<select data-decision-for="{item_id}">{options}</select></label>
        <label>Note<input data-note-for="{item_id}" value="{esc(note)}"></label>
      </div>"""


def evidence_html(item: dict[str, Any], context: dict[str, Any], base: Path) -> str:
    raw_assets = context.get("evidence_assets", {})
    if isinstance(raw_assets, dict):
        assets = raw_assets.get(item["id"], [])
    else:
        lookup = evidence_by_id(context)
        assets = [lookup[evidence_id] for evidence_id in item.get("evidence_refs", []) if evidence_id in lookup]
    rendered: list[str] = []
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        if asset.get("kind") not in {None, "screenshot"}:
            continue
        source = embed_asset(str(asset.get("src") or asset.get("locator") or ""), base)
        if not source:
            continue
        rendered.append(
            f'<figure><img src="{source}" alt="{esc(asset.get("alt") or asset.get("description") or "Evidence image")}">'
            f'<figcaption>{esc(asset.get("caption") or asset.get("description") or "")}</figcaption></figure>'
        )
    return '<div class="evidence-grid">' + "".join(rendered) + "</div>" if rendered else ""


def item_html(item: dict[str, Any], decision: dict[str, Any] | None, context: dict[str, Any], base: Path) -> str:
    destination = f' → {esc(item["destination_id"])}' if item.get("destination_id") else ""
    dependencies = ", ".join(item.get("depends_on", [])) or "none"
    item_id = esc(item["id"])
    facets = ", ".join(item.get("facets", [])) or "none"
    receipts = evidence_summary(item.get("evidence_refs"), context) or "Legacy untyped evidence"
    editorial = item.get("editorial_review")
    editorial_html = ""
    if isinstance(editorial, dict):
        families = ", ".join(editorial.get("independent_signal_families", [])) or "not applicable"
        editorial_html = (
            f'<h4>Editorial review</h4><p>{esc(editorial.get("review_type", ""))} · '
            f'sample {esc(editorial.get("sample_adequacy", ""))} · '
            f'language {esc(editorial.get("analysis_language_scope", "legacy"))} '
            f'({esc(editorial.get("language_review_basis", "unrecorded"))}) · signals {esc(families)} · '
            f'authorship {esc(editorial.get("authorship_assessment", "not_performed"))}</p>'
        )
    return f"""
    <article class="registry-item" data-item-id="{item_id}" data-kind="{esc(item['kind'])}" data-status="{esc(item['status'])}" data-severity="{esc(item['severity'])}">
      <div class="item-rail">
        <span class="item-id">{item_id}</span>
        <span class="badge {esc(item['status'])}">{esc(item['status'])}</span>
        <span class="severity {esc(item['severity'])}">{esc(item['severity'])}</span>
        <span class="cat-chip">{esc(public_category_label(item['category']).replace(' slop',''))}</span>
      </div>
      <div class="item-body">
        <h3>{esc(item['title'])}</h3>
        <p class="meta">{esc(public_category_label(item['category']))} ({esc(item['category'])}) · facets {esc(facets)} · {esc(item['confidence'])} confidence · {esc(item['revision_disposition'])}{destination}</p>
        <p>{esc(item['observation'])}</p>
        {evidence_html(item, context, base)}
        <div class="item-columns">
          <div><h4>User impact</h4><p>{esc(item['user_impact'])}</p></div>
          <div><h4>Cause</h4><p>{esc(item['cause'])}</p></div>
        </div>
        <h4>Evidence</h4>{list_html(item.get('evidence', []))}
        <p class="meta"><strong>Receipts:</strong> {esc(receipts)}</p>
        {editorial_html}
        <h4>Recommended change or preservation rule</h4><p>{esc(item['recommendation'])}</p>
        <h4>Acceptance</h4>{list_html(item.get('acceptance_checks', []))}
        <p class="dependency"><strong>Depends on:</strong> {esc(dependencies)} · <strong>Revision:</strong> {esc(item['disposition_reason'] or 'New in this revision.')}</p>
        {decision_control(item, decision)}
      </div>
    </article>"""


def section_items(title: str, intro: str, items: list[dict[str, Any]], decisions: dict[str, dict[str, Any]], context: dict[str, Any], base: Path) -> str:
    content = "".join(item_html(item, decisions.get(item["id"]), context, base) for item in items)
    if not content:
        content = '<p class="quiet">No items in this section.</p>'
    return f'<h3 class="subhead">{esc(title)}</h3><p class="section-note">{esc(intro)}</p><div class="item-list">{content}</div>'


def render(registry: dict[str, Any], context: dict[str, Any], decision_doc: dict[str, Any], context_path: Path) -> str:
    items = registry["items"]
    by_id = {item["id"]: item for item in items}
    decision_map = {row["item_id"]: row for row in decision_doc.get("decisions", [])}
    presentation = registry["presentation"]

    prioritized_findings = [by_id[item_id] for item_id in presentation["prioritized_finding_ids"]]
    prioritized_set = set(presentation["prioritized_finding_ids"])
    additional_findings = [item for item in items if item["kind"] == "finding" and item["status"] in {"open", "needs-verification"} and item["id"] not in prioritized_set]
    enhancement_priority = [by_id[item_id] for item_id in presentation["prioritized_enhancement_ids"]]
    enhancement_set = set(presentation["prioritized_enhancement_ids"])
    additional_enhancements = [item for item in items if item["kind"] == "enhancement" and item["status"] in {"open", "needs-verification"} and item["id"] not in enhancement_set]
    strengths = [by_id[item_id] for item_id in presentation["strength_ids"]]
    resolved = [item for item in items if item["status"] in {"fixed", "cleared", "merged", "superseded"}]

    outcome = context.get("outcome", {})
    product_table_rows = product_rows(context)
    task_table_rows = task_rows(context)
    capability_table_rows = capability_rows(context)
    score_table_rows = score_rows(context)
    reconciliation_rows = [[item["id"], item["title"], item["status"], item["revision_disposition"], item.get("destination_id") or "—", item["disposition_reason"] or "New in this revision."] for item in items]
    work_rows = []
    for order in context.get("work_orders", []):
        work_rows.append(
            f'<li><div><strong>{esc(order.get("id", ""))} · {esc(order.get("title", ""))}</strong>'
            f'<p>{esc(order.get("summary", ""))}</p><p class="meta">Items: {esc(", ".join(order.get("item_ids", [])) or "none")} · Verification: {esc(order.get("verification", ""))}</p>'
            f'{list_html(order.get("acceptance_checks", []), "No acceptance checks recorded.")}</div></li>'
        )

    registry_json = json.dumps(registry, ensure_ascii=False).replace("</", "<\\/")
    decisions_json = json.dumps(decision_doc, ensure_ascii=False).replace("</", "<\\/")
    title = context.get("title", "Scruffy audit")
    target = registry.get("target", "")
    storage_key = f"anti-slop:{registry['audit_id']}:decisions:v2"

    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3, "none": 4}
    additional_findings.sort(key=lambda i: (i["category"], severity_rank.get(i["severity"], 9)))
    additional_enhancements.sort(key=lambda i: (i["category"], severity_rank.get(i["severity"], 9)))
    score_table_rows.sort(key=lambda row: (0, -row[1]) if isinstance(row[1], int) else (1, 0))
    capability_counts: dict[str, int] = {}
    for row in context.get("capabilities", []):
        capability_counts[row.get("status", "?")] = capability_counts.get(row.get("status", "?"), 0) + 1
    capability_summary = " · ".join(f"{k.replace('_', ' ')} ×{v}" for k, v in sorted(capability_counts.items()))
    open_findings = sum(1 for i in items if i["kind"] == "finding" and i["status"] in {"open", "needs-verification"})
    open_enhancements = sum(1 for i in items if i["kind"] == "enhancement" and i["status"] in {"open", "needs-verification"})
    strength_count = sum(1 for i in items if i["kind"] == "strength")
    cleared_count = sum(1 for i in items if i["status"] in {"cleared", "fixed"})
    carried_count = sum(1 for i in items if i.get("revision_disposition") == "carried")
    short_category = {"information_architecture": "IA", "backend_shape": "Structure", "interaction": "Interaction",
                      "accessibility": "Accessibility", "visual": "Visual", "copy": "Editorial",
                      "product": "Product", "performance": "Performance"}
    numeric_scores = [(row.get("category"), row.get("score")) for row in context.get("scores", [])
                      if isinstance(row.get("score"), int)]
    worst = max(numeric_scores, key=lambda pair: pair[1], default=None)
    worst_label = f"{short_category.get(worst[0], worst[0])} · {worst[1]}" if worst else "—"
    hero = next((i for i in prioritized_findings if i["status"] in {"open", "needs-verification"}), None)
    if hero:
        hero_html = (
            f'<p class="eyebrow">Scruffy durable audit · {esc(registry["revision_id"])} · '
            f'{open_findings + open_enhancements} items awaiting decision</p>'
            f'<h1>{esc(hero["title"])}</h1>'
            f'<p class="target">{esc(hero["id"])} · {esc(public_category_label(hero["category"]))} · severity {esc(hero["severity"])} · '
            f'{esc(hero["revision_disposition"])} · decide this first, then <a href="#findings">the queue below</a>.</p>'
        )
    else:
        hero_html = (
            f'<p class="eyebrow">Scruffy durable audit · {esc(registry["revision_id"])}</p>'
            f'<h1>{esc(title)}</h1>'
        )
    strip_html = (
        f'<div class="strip num" aria-label="Registry counts">'
        f'<div><span>Open findings</span><b>{open_findings}</b></div>'
        f'<div><span>Enhancements</span><b>{open_enhancements}</b></div>'
        f'<div><span>Strengths</span><b>{strength_count}</b></div>'
        f'<div><span>Cleared</span><b>{cleared_count}</b></div>'
        f'<div><span>Carried</span><b>{carried_count}</b></div>'
        f'<div><span>Worst category</span><b>{esc(worst_label)}</b></div>'
        f'<div class="strip-target"><span>Target</span><b class="tgt">{esc(target)}</b></div></div>'
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <style>
    :root{{--ink:#0c1210;--panel:#101b16;--panel2:#0f1a15;--paper:#f2f4f1;--mut:#8fa39a;--line:#24352e;--gold:#e4c56a;--warn:#ff9d45;--bad:#ff6a55;--ok:#59d19a;--blue:#6db3ff;--violet:#a99bd6;
      font-family:-apple-system,"Helvetica Neue",Arial,sans-serif;color:var(--paper);background:var(--ink)}}
    *{{box-sizing:border-box}} body{{margin:0;min-height:100vh;background:var(--ink)}} a{{color:var(--gold);text-underline-offset:3px}}
    button,select,input{{font:inherit}} :focus-visible{{outline:3px solid var(--blue);outline-offset:3px}}
    .num,.item-id,.strip b{{font-variant-numeric:tabular-nums}}
    .wrap{{width:min(1220px,calc(100% - 40px));margin:0 auto}}
    .mast{{background:linear-gradient(160deg,#16281f,#0c1210 72%);border-bottom:1px solid var(--line)}}
    .mast .wrap{{padding:36px 0 30px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:28px;align-items:end}}
    .eyebrow{{margin:0 0 10px;color:var(--mut);font:700 11px/1.4 Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase}}
    h1{{margin:0;font:500 clamp(1.7rem,3.2vw,2.8rem)/1.1 Georgia,"Times New Roman",serif;max-width:920px}}
    .target{{margin:12px 0 0;color:var(--mut);font:.88rem/1.55 Arial,sans-serif;overflow-wrap:anywhere;max-width:820px}}
    .verdict{{max-width:300px;padding:16px 19px;color:#171303;background:var(--gold);border-radius:10px;font:.82rem/1.35 Arial,sans-serif;box-shadow:0 18px 40px -20px rgba(0,0,0,.9)}}
    .verdict strong{{display:block;margin-top:5px;font:600 1.25rem/1.2 Georgia,serif}}
    .strip{{display:flex;gap:30px;flex-wrap:wrap;padding:16px 0;border-bottom:1px solid var(--line);background:var(--panel2)}}
    .strip>div>span{{display:block;color:var(--mut);font:700 10.5px/1.4 Arial,sans-serif;letter-spacing:.11em;text-transform:uppercase}}
    .strip b{{font:600 1.7rem/1.15 "Helvetica Neue",Arial,sans-serif}}
    .strip .strip-target{{margin-left:auto;max-width:360px;min-width:0}} .strip .tgt{{font:400 .78rem/1.45 Arial,sans-serif;color:var(--mut);overflow-wrap:anywhere}}
    .strip-holder{{background:var(--panel2)}}
    main.wrap{{padding:34px 0 72px}}
    section{{padding:0 0 8px}} section+section{{border-top:1px solid var(--line);margin-top:36px}}
    h2{{margin:34px 0 12px;color:var(--paper);font:700 12px/1.4 Arial,sans-serif;letter-spacing:.15em;text-transform:uppercase}}
    h2:after{{content:"";display:block;margin-top:10px;width:44px;border-top:2px solid var(--gold)}}
    .subhead{{margin:24px 0 4px;color:var(--paper);font:500 1.15rem/1.3 Georgia,serif}}
    .section-note,.quiet,.meta{{color:var(--mut);font:.88rem/1.55 Arial,sans-serif}}
    .lede{{font:400 clamp(1.05rem,1.8vw,1.3rem)/1.6 Georgia,serif;max-width:920px;color:var(--paper)}}
    .table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:10px}}
    table{{width:100%;border-collapse:collapse;font:.86rem/1.5 Arial,sans-serif}}
    th{{color:var(--mut);background:var(--panel);text-align:left;font:700 10.5px/1.4 Arial,sans-serif;letter-spacing:.1em;text-transform:uppercase}}
    th,td{{padding:11px 13px;border-bottom:1px solid var(--line);vertical-align:top}} td{{overflow-wrap:anywhere}} tr:last-child td{{border-bottom:0}}
    .toolbar{{position:sticky;top:0;z-index:9;display:flex;flex-wrap:wrap;gap:9px;margin:20px 0;padding:12px 14px;background:rgba(12,18,16,.94);border:1px solid var(--line);border-radius:12px}}
    .toolbar button,.toolbar label{{border:1px solid var(--line);background:#16241e;color:var(--paper);padding:9px 13px;cursor:pointer;font:700 .78rem/1 Arial,sans-serif;border-radius:8px}}
    .toolbar button.primary{{background:var(--gold);border-color:var(--gold);color:#171303}}
    .toolbar input{{position:absolute;inline-size:1px;block-size:1px;opacity:.01}}
    .registry-item{{display:grid;grid-template-columns:118px minmax(0,1fr);gap:24px;padding:26px 0;border-top:1px solid var(--line)}}
    .registry-item>*{{min-width:0}}
    .item-rail{{display:flex;flex-direction:column;align-items:flex-start;gap:9px}}
    .item-id{{color:var(--gold);font:800 1.05rem/1 "Helvetica Neue",Arial,sans-serif}}
    .badge,.severity{{padding:5px 9px;border-radius:6px;font:800 .64rem/1 Arial,sans-serif;letter-spacing:.08em;text-transform:uppercase}}
    .severity:before,.badge:before{{content:"●";margin-right:6px;font-size:.7em;vertical-align:1px}}
    .severity.critical,.severity.high{{background:#3a1712;color:var(--bad)}}
    .severity.medium{{background:#33230d;color:var(--warn)}}
    .severity.low{{background:#122b21;color:var(--ok)}} .severity.none{{background:#132433;color:var(--blue)}}
    .badge.open{{background:#33230d;color:var(--warn)}} .badge.needs-verification{{background:#231d3a;color:var(--violet)}}
    .badge.fixed,.badge.cleared{{background:#122b21;color:var(--ok)}} .badge.merged,.badge.superseded{{background:#1c2420;color:var(--mut)}}
    .item-body h3{{margin:0 0 6px;font:500 1.3rem/1.3 Georgia,serif}}
    .item-body p,.item-body li{{line-height:1.6;overflow-wrap:anywhere}}
    .item-body h4{{margin:18px 0 4px;color:var(--mut);font:800 .68rem/1.4 Arial,sans-serif;letter-spacing:.1em;text-transform:uppercase}}
    .item-body ul{{margin:5px 0;padding-left:21px}}
    .item-columns{{display:grid;grid-template-columns:1fr 1fr;gap:24px}} .item-columns>*{{min-width:0}}
    .dependency{{font:.82rem/1.5 Arial,sans-serif;color:var(--mut);overflow-wrap:anywhere}}
    .cat-chip{{padding:5px 9px;border-radius:6px;border:1px solid var(--line);color:var(--mut);font:800 .64rem/1 Arial,sans-serif;letter-spacing:.08em;text-transform:uppercase}}
    .decision-row{{display:grid;grid-template-columns:170px 1fr;gap:11px;margin-top:19px;padding:15px 16px;background:#15221c;border:1px solid var(--line);border-radius:12px}}
    .decision-row>*{{min-width:0}}
    .decision-row label{{color:var(--mut);font:700 .72rem/1.3 Arial,sans-serif;letter-spacing:.06em;text-transform:uppercase}}
    .decision-row select,.decision-row input{{width:100%;margin-top:5px;padding:9px;color:var(--paper);background:#101b16;border:1px solid var(--line);border-radius:8px}}
    .evidence-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin:18px 0}}
    .evidence-grid>*{{min-width:0}}
    figure{{margin:0;min-width:0;background:#f6f3ea;border-radius:6px;padding:8px 8px 10px;box-shadow:0 16px 34px -18px rgba(0,0,0,.75)}}
    figure img{{display:block;width:100%;border:1px solid #d8d2c2}}
    figcaption{{padding-top:7px;color:#3c463f;font:600 .74rem/1.5 Georgia,serif;overflow-wrap:anywhere}}
    .status{{min-height:1.3em;color:var(--ok);font:700 .82rem/1.4 Arial,sans-serif}}
    .work-list{{counter-reset:work;list-style:none;margin:0;padding:0}}
    .work-list>li{{counter-increment:work;display:grid;grid-template-columns:44px minmax(0,1fr);gap:12px;padding:15px 0;border-bottom:1px solid var(--line)}}
    .work-list>li>*{{min-width:0}}
    .work-list>li:before{{content:counter(work,decimal-leading-zero);color:var(--gold);font:800 1rem/1.5 "Helvetica Neue",Arial,sans-serif}}
    footer{{color:var(--mut);background:var(--panel2);border-top:1px solid var(--line)}} footer .wrap{{padding:22px 0;font:.8rem/1.5 Arial,sans-serif}}
    [hidden]{{display:none!important}}
    @media(max-width:760px){{.mast .wrap,.registry-item,.item-columns,.decision-row{{grid-template-columns:1fr}} .verdict{{max-width:none}} .registry-item{{gap:11px}} .item-rail{{flex-direction:row;align-items:center;flex-wrap:wrap}} .strip{{gap:18px}} .strip .strip-target{{margin-left:0}}}}
    @media print{{
      :root{{color:#141414;background:#fff;font-family:Georgia,"Times New Roman",serif}}
      body,.mast,.strip,.strip-holder,footer{{background:#fff!important;color:#141414}}
      .toolbar,.decision-row{{display:none}}
      .mast{{border-bottom:3px double #141414}} .eyebrow,.target,.strip>div>span,.section-note,.meta,.quiet{{color:#5c5c56}}
      h1,.item-body h3,.subhead{{color:#141414}} h2{{color:#141414}} h2:after{{border-color:#141414}}
      .verdict{{background:#fff;border:1.5px solid #141414;box-shadow:none;color:#141414;border-radius:0}}
      .strip{{border-bottom:1px solid #141414}} .strip b{{color:#141414}}
      .registry-item{{break-inside:avoid;border-top:1px solid #d9d9d2}}
      .item-id{{color:#c8102e}}
      .badge,.severity{{border:1.5px solid #141414;background:#fff!important;color:#141414!important;border-radius:0}}
      .severity.critical,.severity.high{{background:#c8102e!important;border-color:#c8102e;color:#fff!important}}
      table,th,td{{color:#141414}} th{{background:#fff;border-bottom:1.5px solid #141414}}
      figure{{box-shadow:none;border:1px solid #d9d9d2}} a{{color:#141414}}
    }}
  </style>
</head>
<body>
  <header class="mast"><div class="wrap"><div>{hero_html}</div><div class="verdict">Overall result<strong>{esc(outcome.get('label','Insufficient evidence'))}</strong></div></div></header>
  <div class="strip-holder"><div class="wrap">{strip_html}</div></div>
  <main class="wrap">
    <section id="outcome"><h2>Outcome</h2><p class="lede">{esc(outcome.get('summary',''))}</p><p class="section-note"><strong>Confidence:</strong> {esc(outcome.get('confidence','unknown'))} · <strong>Audit:</strong> {esc(registry['audit_id'])} · <strong>Baseline:</strong> {esc(registry.get('baseline_revision_id') or 'none')}</p></section>
    <section id="product-frame"><h2>Product frame</h2>{table_html(['Question','Answer','Basis'],product_table_rows)}</section>
    <section id="task-ledger"><h2>Did real journeys work?</h2><p class="section-note">Each row is a user task we operated, its outcome, and the receipt behind it.</p>{table_html(['ID','Outcome','Goal','What happened','Receipts'],task_table_rows)}</section>
    <section id="capability-ledger"><h2>What we could and could not test</h2><p class="section-note">{esc(capability_summary)}. Anything not run carries its reason and the shortest way to unblock it.</p>{table_html(['Capability','Status','Scope'],capability_table_rows)}</section>
    <section id="score"><h2>The eight slop categories, worst first</h2><p class="section-note">0 is clear, 3 is a material problem, N/A means we did not earn the right to score it. Every score cites its evidence.</p>{table_html(['Category','Score','Evidence'],score_table_rows)}</section>
    <section id="findings"><h2>Findings</h2><div class="toolbar" aria-label="Registry controls"><button data-filter="all" class="primary">All active</button><button data-filter="open">Open</button><button data-filter="needs-verification">Needs verification</button><button id="download-findings">Download findings</button><button id="download-decisions">Download decisions</button><button id="copy-decisions">Copy decisions</button><label>Import decisions<input id="import-decisions" type="file" accept="application/json"></label></div><p id="ui-status" class="status" aria-live="polite"></p>{section_items('Prioritized','Maximum eight for executive attention; the registry remains complete.',prioritized_findings,decision_map,context,context_path.parent)}{section_items('Additional active findings','Verified and needs-verification findings outside the executive shortlist.',additional_findings,decision_map,context,context_path.parent)}</section>
    <section id="enhancements"><h2>Enhancements</h2>{section_items('Prioritized enhancements','Maximum five for executive attention.',enhancement_priority,decision_map,context,context_path.parent)}{section_items('Additional enhancements','Retained even when outside the shortlist.',additional_enhancements,decision_map,context,context_path.parent)}</section>
    <section id="strengths"><h2>Strengths to preserve</h2>{section_items('Preserve','Positive evidence is part of the contract, not decoration.',strengths,decision_map,context,context_path.parent)}</section>
    <section id="resolved"><h2>Fixed, cleared, merged, and superseded</h2>{section_items('Resolved registry','Every prior item remains visible with evidence and disposition.',resolved,decision_map,context,context_path.parent)}</section>
    <section id="reconciliation"><h2>Revision reconciliation</h2>{table_html(['ID','Current title','Status','Disposition','Destination','Reason'],reconciliation_rows,'reconciliation')}</section>
    <section id="work-orders"><h2>Dependency-ordered work</h2><ol class="work-list">{''.join(work_rows) or '<li><div>No work orders recorded.</div></li>'}</ol></section>
    <section id="checks-not-run"><h2>Checks not run</h2>{list_html(checks_not_run(context),'No checks-not-run entries recorded.')}</section>
  </main>
  <footer><div class="wrap">Complete registry: {len(items)} items · Prioritized findings: {len(prioritized_findings)} · Prioritized enhancements: {len(enhancement_priority)} · Generated from schema-v2 source data.</div></footer>
  <script>
    const registry={registry_json};
    const embeddedDecisions={decisions_json};
    const storageKey={json.dumps(storage_key)};
    const itemRows=[...document.querySelectorAll('[data-item-id]')];
    const clone=value=>JSON.parse(JSON.stringify(value));
    const baseRows=Object.fromEntries(embeddedDecisions.decisions.map(row=>[row.item_id,clone(row)]));
    const loadLocal=()=>{{try{{return JSON.parse(localStorage.getItem(storageKey)||'null')}}catch{{return null}}}};
    let state=loadLocal()||clone(embeddedDecisions);
    const ensureRows=()=>{{
      const allowed=new Set(registry.items.filter(item=>['finding','enhancement'].includes(item.kind)).map(item=>item.id));
      const incoming=Object.fromEntries((state.decisions||[]).filter(row=>allowed.has(row.item_id)).map(row=>[row.item_id,row]));
      state={{...embeddedDecisions,decisions:[...allowed].map(id=>incoming[id]||baseRows[id]||{{item_id:id,decision:'pending',note:'',updated_at:null,decision_source:'current',destination_id:null,history:[]}})}};
    }};
    const rowFor=id=>state.decisions.find(row=>row.item_id===id);
    const persist=()=>{{try{{localStorage.setItem(storageKey,JSON.stringify(state));return true}}catch{{return false}}}};
    const hydrate=()=>{{ensureRows();document.querySelectorAll('[data-decision-for]').forEach(control=>{{const row=rowFor(control.dataset.decisionFor);control.value=row?.decision||'pending'}});document.querySelectorAll('[data-note-for]').forEach(control=>{{const row=rowFor(control.dataset.noteFor);control.value=row?.note||''}});persist()}};
    document.querySelectorAll('[data-decision-for]').forEach(control=>control.addEventListener('change',()=>{{const row=rowFor(control.dataset.decisionFor);if(!row)return;row.history=row.history||[];row.history.push({{decision:row.decision,note:row.note,updated_at:row.updated_at}});row.decision=control.value;row.updated_at=new Date().toISOString();persist()}}));
    document.querySelectorAll('[data-note-for]').forEach(control=>control.addEventListener('input',()=>{{const row=rowFor(control.dataset.noteFor);if(!row)return;row.note=control.value;row.updated_at=new Date().toISOString();persist()}}));
    const download=(name,value)=>{{const blob=new Blob([JSON.stringify(value,null,2)],{{type:'application/json'}});const link=document.createElement('a');link.href=URL.createObjectURL(blob);link.download=name;link.click();URL.revokeObjectURL(link.href)}};
    document.getElementById('download-findings').addEventListener('click',()=>download(`${{registry.audit_id}}-findings.json`,registry));
    document.getElementById('download-decisions').addEventListener('click',()=>download(`${{registry.audit_id}}-decisions.json`,state));
    document.getElementById('copy-decisions').addEventListener('click',async()=>{{try{{await navigator.clipboard.writeText(JSON.stringify(state,null,2));document.getElementById('ui-status').textContent='Decisions copied.'}}catch{{document.getElementById('ui-status').textContent='Clipboard unavailable; use Download decisions.'}}}});
    document.getElementById('import-decisions').addEventListener('change',async event=>{{const file=event.target.files[0];if(!file)return;try{{const incoming=JSON.parse(await file.text());if(incoming.schema_version!==registry.schema_version||incoming.audit_id!==registry.audit_id)throw new Error('schema or audit mismatch');state=incoming;hydrate();document.getElementById('ui-status').textContent='Decisions imported and reconciled by item ID.'}}catch(error){{document.getElementById('ui-status').textContent=`Import rejected: ${{error.message}}`}}event.target.value=''}});
    document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{{const filter=button.dataset.filter;document.querySelectorAll('[data-filter]').forEach(candidate=>candidate.classList.toggle('primary',candidate===button));itemRows.forEach(row=>{{const active=['open','needs-verification'].includes(row.dataset.status);row.hidden=filter==='all'?!active:row.dataset.status!==filter}})}}));
    hydrate();
  </script>
</body>
</html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry", type=Path)
    parser.add_argument("context", type=Path)
    parser.add_argument("decisions", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    registry = load(args.registry)
    context = load(args.context)
    decisions = load(args.decisions)
    rendered = render(registry, context, decisions, args.context)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"PASS: rendered {len(registry.get('items', []))} registry items to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
