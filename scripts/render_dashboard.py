#!/usr/bin/env python3
"""Render a complete, self-contained Anti-Slop decision dashboard."""

from __future__ import annotations

import argparse
import base64
import html
import json
import mimetypes
from pathlib import Path
from typing import Any


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


def evidence_html(item_id: str, context: dict[str, Any], base: Path) -> str:
    assets = context.get("evidence_assets", {}).get(item_id, [])
    rendered: list[str] = []
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        source = embed_asset(str(asset.get("src", "")), base)
        if not source:
            continue
        rendered.append(
            f'<figure><img src="{source}" alt="{esc(asset.get("alt", "Evidence image"))}">'
            f'<figcaption>{esc(asset.get("caption", ""))}</figcaption></figure>'
        )
    return '<div class="evidence-grid">' + "".join(rendered) + "</div>" if rendered else ""


def item_html(item: dict[str, Any], decision: dict[str, Any] | None, context: dict[str, Any], base: Path) -> str:
    destination = f' → {esc(item["destination_id"])}' if item.get("destination_id") else ""
    dependencies = ", ".join(item.get("depends_on", [])) or "none"
    item_id = esc(item["id"])
    return f"""
    <article class="registry-item" data-item-id="{item_id}" data-kind="{esc(item['kind'])}" data-status="{esc(item['status'])}" data-severity="{esc(item['severity'])}">
      <div class="item-rail">
        <span class="item-id">{item_id}</span>
        <span class="badge {esc(item['status'])}">{esc(item['status'])}</span>
        <span class="severity">{esc(item['severity'])}</span>
      </div>
      <div class="item-body">
        <h3>{esc(item['title'])}</h3>
        <p class="meta">{esc(item['category'])} · {esc(item['confidence'])} confidence · {esc(item['revision_disposition'])}{destination}</p>
        <p>{esc(item['observation'])}</p>
        {evidence_html(item['id'], context, base)}
        <div class="item-columns">
          <div><h4>User impact</h4><p>{esc(item['user_impact'])}</p></div>
          <div><h4>Cause</h4><p>{esc(item['cause'])}</p></div>
        </div>
        <h4>Evidence</h4>{list_html(item.get('evidence', []))}
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
    product_rows = [[row.get("question", ""), row.get("answer", ""), row.get("basis", "")] for row in context.get("product_frame", [])]
    task_rows = [[row.get("id", ""), row.get("goal", ""), row.get("result", ""), row.get("status", ""), row.get("evidence", "")] for row in context.get("tasks", [])]
    capability_rows = [[row.get("capability", ""), row.get("status", ""), row.get("scope", "")] for row in context.get("capabilities", [])]
    score_rows = [[row.get("category", ""), row.get("score", ""), row.get("evidence", "")] for row in context.get("scores", [])]
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
    title = context.get("title", "Anti-Slop audit")
    target = registry.get("target", "")
    storage_key = f"anti-slop:{registry['audit_id']}:decisions:v2"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <style>
    :root{{--ink:#24211c;--muted:#645d51;--paper:#f5efe2;--paper2:#e9dfcc;--green:#13543e;--green2:#0a3829;--gold:#e4c56a;--rule:#cfc2aa;--blue:#0669c6;--bad:#8a2a20;--warn:#7a4b00;--ok:#225d46;font-family:Georgia,"Times New Roman",serif;color:var(--ink);background:var(--paper)}}
    *{{box-sizing:border-box}} body{{margin:0;min-height:100vh;background:var(--paper)}} a{{color:var(--green);text-underline-offset:3px}} button,select,input{{font:inherit}} :focus-visible{{outline:3px solid var(--blue);outline-offset:3px}}
    .mast{{color:var(--paper);background:var(--green);border-bottom:6px solid var(--gold)}} .wrap{{width:min(1180px,calc(100% - 32px));margin:0 auto}} .mast .wrap{{padding:34px 0 30px;display:grid;grid-template-columns:1fr auto;gap:28px;align-items:end}}
    .eyebrow{{margin:0 0 8px;color:var(--gold);font:700 .78rem/1.2 Arial,sans-serif;letter-spacing:.12em;text-transform:uppercase}} h1{{margin:0;font-size:clamp(2rem,5vw,4.7rem);line-height:.96;font-weight:500}} .target{{margin:17px 0 0;color:var(--paper2);font:.9rem/1.5 Arial,sans-serif;word-break:break-word}}
    .verdict{{max-width:290px;padding:17px 19px;color:var(--ink);background:var(--gold);border:2px solid var(--ink);box-shadow:5px 5px 0 var(--ink);font:.9rem/1.3 Arial,sans-serif}} .verdict strong{{display:block;margin-top:5px;font:600 1.3rem/1.15 Georgia,serif}}
    main.wrap{{padding:38px 0 72px}} section{{padding:0 0 10px}} section+section{{border-top:1px solid var(--rule);margin-top:38px}} h2{{margin:38px 0 15px;color:var(--green2);font-size:clamp(1.6rem,3vw,2.45rem);font-weight:500}} .subhead{{margin:26px 0 5px;color:var(--green2);font-size:1.25rem}} .section-note,.quiet,.meta{{color:var(--muted);font:.9rem/1.55 Arial,sans-serif}} .lede{{font-size:clamp(1.12rem,2vw,1.45rem);line-height:1.55;max-width:900px}}
    .table-wrap{{overflow:auto;border:1px solid var(--rule)}} table{{width:100%;border-collapse:collapse;font:.88rem/1.45 Arial,sans-serif}} th{{color:var(--paper);background:var(--green);text-align:left}} th,td{{padding:10px 12px;border-right:1px solid var(--rule);border-bottom:1px solid var(--rule);vertical-align:top}} tr:last-child td{{border-bottom:0}}
    .toolbar{{display:flex;flex-wrap:wrap;gap:9px;margin:20px 0}} .toolbar button,.toolbar label{{border:2px solid var(--green2);background:transparent;color:var(--green2);padding:8px 12px;cursor:pointer;font:700 .82rem/1 Arial,sans-serif}} .toolbar button.primary{{background:var(--green);color:var(--paper)}} .toolbar input{{position:absolute;inline-size:1px;block-size:1px;opacity:.01}}
    .registry-item{{display:grid;grid-template-columns:125px minmax(0,1fr);gap:24px;padding:27px 0;border-top:1px solid var(--rule)}} .item-rail{{display:flex;flex-direction:column;align-items:flex-start;gap:8px}} .item-id{{color:var(--green);font:800 1.15rem/1 Arial,sans-serif}} .badge,.severity{{padding:4px 7px;border:1px solid currentColor;font:800 .68rem/1 Arial,sans-serif;letter-spacing:.07em;text-transform:uppercase}} .badge.open{{color:var(--warn)}} .badge.needs-verification{{color:#59498b}} .badge.fixed,.badge.cleared{{color:var(--ok)}} .badge.merged,.badge.superseded{{color:var(--muted)}}
    .item-body h3{{margin:0 0 6px;font-size:1.4rem}} .item-body p,.item-body li{{line-height:1.55}} .item-body h4{{margin:18px 0 4px;color:var(--green2);font:800 .73rem/1.2 Arial,sans-serif;letter-spacing:.08em;text-transform:uppercase}} .item-body ul{{margin:5px 0;padding-left:21px}} .item-columns{{display:grid;grid-template-columns:1fr 1fr;gap:24px}} .dependency{{font:.82rem/1.5 Arial,sans-serif;color:var(--muted)}}
    .decision-row{{display:grid;grid-template-columns:170px 1fr;gap:11px;margin-top:19px;padding-top:17px;border-top:1px dashed var(--rule)}} .decision-row label{{color:var(--muted);font:700 .75rem/1.2 Arial,sans-serif}} .decision-row select,.decision-row input{{width:100%;margin-top:5px;padding:9px;color:var(--ink);background:#fffaf0;border:1px solid var(--muted)}}
    .evidence-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin:18px 0}} figure{{margin:0}} figure img{{display:block;width:100%;border:1px solid var(--rule)}} figcaption{{padding-top:6px;color:var(--muted);font:.78rem/1.45 Arial,sans-serif}} .status{{min-height:1.3em;color:var(--green2);font:700 .82rem/1.4 Arial,sans-serif}}
    .work-list{{counter-reset:work;list-style:none;margin:0;padding:0}} .work-list>li{{counter-increment:work;display:grid;grid-template-columns:42px 1fr;gap:12px;padding:14px 0;border-bottom:1px solid var(--rule)}} .work-list>li:before{{content:counter(work,decimal-leading-zero);color:var(--green);font:800 1rem/1.5 Arial,sans-serif}}
    footer{{color:var(--paper2);background:var(--green2)}} footer .wrap{{padding:23px 0;font:.8rem/1.5 Arial,sans-serif}}
    [hidden]{{display:none!important}} @media(max-width:760px){{.mast .wrap,.registry-item,.item-columns,.decision-row{{grid-template-columns:1fr}} .verdict{{max-width:none}} .registry-item{{gap:11px}} .item-rail{{flex-direction:row;align-items:center;flex-wrap:wrap}}}}
    @media print{{.toolbar,.decision-row{{display:none}} .mast{{color:#000;background:#fff;border-bottom:3px solid #000}} .eyebrow,.target{{color:#000}} .verdict{{box-shadow:none}} .registry-item{{break-inside:avoid}}}}
  </style>
</head>
<body>
  <header class="mast"><div class="wrap"><div><p class="eyebrow">Anti-Slop durable audit · {esc(registry['revision_id'])}</p><h1>{esc(title)}</h1><p class="target">{esc(target)}</p></div><div class="verdict">Overall result<strong>{esc(outcome.get('label','Insufficient evidence'))}</strong></div></div></header>
  <main class="wrap">
    <section id="outcome"><h2>Outcome</h2><p class="lede">{esc(outcome.get('summary',''))}</p><p class="section-note"><strong>Confidence:</strong> {esc(outcome.get('confidence','unknown'))} · <strong>Audit:</strong> {esc(registry['audit_id'])} · <strong>Baseline:</strong> {esc(registry.get('baseline_revision_id') or 'none')}</p></section>
    <section id="product-frame"><h2>Product frame</h2>{table_html(['Question','Answer','Basis'],product_rows)}</section>
    <section id="task-ledger"><h2>Representative tasks</h2>{table_html(['ID','Goal','Result','Status','Evidence'],task_rows)}</section>
    <section id="capability-ledger"><h2>Capability and coverage ledger</h2>{table_html(['Capability','Status','Scope'],capability_rows)}</section>
    <section id="score"><h2>Evidence-calibrated score</h2>{table_html(['Category','Score','Evidence'],score_rows)}</section>
    <section id="findings"><h2>Findings</h2><div class="toolbar" aria-label="Registry controls"><button data-filter="all" class="primary">All active</button><button data-filter="open">Open</button><button data-filter="needs-verification">Needs verification</button><button id="download-findings">Download findings</button><button id="download-decisions">Download decisions</button><button id="copy-decisions">Copy decisions</button><label>Import decisions<input id="import-decisions" type="file" accept="application/json"></label></div><p id="ui-status" class="status" aria-live="polite"></p>{section_items('Prioritized','Maximum eight for executive attention; the registry remains complete.',prioritized_findings,decision_map,context,context_path.parent)}{section_items('Additional active findings','Verified and needs-verification findings outside the executive shortlist.',additional_findings,decision_map,context,context_path.parent)}</section>
    <section id="enhancements"><h2>Enhancements</h2>{section_items('Prioritized enhancements','Maximum five for executive attention.',enhancement_priority,decision_map,context,context_path.parent)}{section_items('Additional enhancements','Retained even when outside the shortlist.',additional_enhancements,decision_map,context,context_path.parent)}</section>
    <section id="strengths"><h2>Strengths to preserve</h2>{section_items('Preserve','Positive evidence is part of the contract, not decoration.',strengths,decision_map,context,context_path.parent)}</section>
    <section id="resolved"><h2>Fixed, cleared, merged, and superseded</h2>{section_items('Resolved registry','Every prior item remains visible with evidence and disposition.',resolved,decision_map,context,context_path.parent)}</section>
    <section id="reconciliation"><h2>Revision reconciliation</h2>{table_html(['ID','Current title','Status','Disposition','Destination','Reason'],reconciliation_rows,'reconciliation')}</section>
    <section id="work-orders"><h2>Dependency-ordered work</h2><ol class="work-list">{''.join(work_rows) or '<li><div>No work orders recorded.</div></li>'}</ol></section>
    <section id="checks-not-run"><h2>Checks not run</h2>{list_html(context.get('checks_not_run',[]),'No checks-not-run entries recorded.')}</section>
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
    document.getElementById('import-decisions').addEventListener('change',async event=>{{const file=event.target.files[0];if(!file)return;try{{const incoming=JSON.parse(await file.text());if(incoming.schema_version!=='2.0'||incoming.audit_id!==registry.audit_id)throw new Error('schema or audit mismatch');state=incoming;hydrate();document.getElementById('ui-status').textContent='Decisions imported and reconciled by item ID.'}}catch(error){{document.getElementById('ui-status').textContent=`Import rejected: ${{error.message}}`}}event.target.value=''}});
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
