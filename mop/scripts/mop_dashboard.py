#!/usr/bin/env python3
"""Generate the Mop's standard deliverable: a self-contained decision dashboard.

The operator reads Mop output in a terminal, so a dashboard is the only surface
where they can see evidence and act on it. It must therefore be one file with
every image embedded as a ``data:`` URI — no sibling folder, no external fetch,
no login-gated link needed to render — and it must let the operator **close the
loop**: review every Scruffy finding beside the Mop's recommended direction,
Approve / Defer / Reject each in-browser, and export an updated ``decisions.json``
(schema 2.1) that feeds straight back into ``mop_bundle.py`` / ``mop_dashboard.py``.

All interaction is client-side JS embedded in the file (no server): the decision
controls and the copy/download of ``decisions.json`` run offline.

Inputs: a Scruffy audit bundle (findings/context/decisions) plus an assets
manifest (screenshots, references, preflight, per-item directions). See
``ASSETS SCHEMA`` below. Dependency-free (stdlib only). Fails closed if any
referenced image would load externally.
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import sys
from pathlib import Path

from mop_bundle import InteropError, build_plan, load_bundle, load_interop

# ASSETS SCHEMA (JSON) — same as before:
# {
#   "target": "…",  "preflight": {…}|"preflight.json",
#   "screenshots": [{"path":..,"mime":..?,"caption":..,"item_ids":[..]}],
#   "references":  [{"path":..,"mime":..?,"app":..,"url":..,"note":..,"for_items":[..]}],
#   "directions":  {"ITEM_ID":{"recommended":..,"principle":..,"alternates":[..]}}
# }

_MIME_BY_EXT = {
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".webp": "image/webp", ".gif": "image/gif", ".svg": "image/svg+xml",
}
_DECISIONS = ("approve", "defer", "reject", "pending")
_DECISION_LABEL = {"approve": "Approve", "defer": "Defer", "reject": "Reject", "pending": "Pending"}
_ACTIONABLE_KINDS = ("finding", "enhancement")


def _data_uri(path: Path, mime: str | None) -> str:
    if mime is None:
        mime = _MIME_BY_EXT.get(path.suffix.lower())
    if mime is None:
        raise InteropError(f"cannot infer MIME for {path.name}; add \"mime\" to its asset entry")
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def _resolve_preflight(assets: dict, base: Path) -> dict | None:
    pf = assets.get("preflight")
    if pf is None:
        return None
    if isinstance(pf, str):
        return json.loads((base / pf).read_text(encoding="utf-8"))
    return pf


def _e(text) -> str:
    return html.escape(str(text if text is not None else ""))


def _ordered_items(bundle: dict) -> list[dict]:
    """All registry items in presentation order, then any not listed."""
    items = {it["id"]: it for it in bundle["findings"].get("items", [])}
    pres = bundle["findings"].get("presentation", {})
    order: list[str] = []
    for key in ("prioritized_finding_ids", "prioritized_enhancement_ids", "strength_ids"):
        for iid in pres.get(key, []):
            if iid in items and iid not in order:
                order.append(iid)
    for iid in items:
        if iid not in order:
            order.append(iid)
    return [items[i] for i in order]


def build_dashboard_html(bundle: dict, plan: dict, assets: dict, base: Path) -> str:
    findings = bundle["findings"]
    decisions = {d["item_id"]: d for d in bundle["decisions"].get("decisions", [])}
    audit_id = findings.get("audit_id")
    target = assets.get("target") or findings.get("target", "")
    preflight = _resolve_preflight(assets, base)

    screenshots = assets.get("screenshots", [])
    references = assets.get("references", [])
    directions = assets.get("directions", {})
    shot_uri = {s["path"]: _data_uri(base / s["path"], s.get("mime")) for s in screenshots}
    ref_uri = {r["path"]: _data_uri(base / r["path"], r.get("mime")) for r in references}

    p: list[str] = [_HEAD]
    p.append('<div class="wrap">')
    p.append('<header><div class="kick">Scruffy&rsquo;s Mop &middot; decision dashboard '
             '&middot; self-contained</div>'
             f'<h1>{_e(audit_id)}</h1>')
    if target:
        p.append(f'<p class="target">{_e(target)}</p>')
    p.append('</header>')

    # Capabilities from the preflight (never assumed).
    if preflight:
        p.append('<div class="caps">')
        for cap, rec in preflight.get("augmentations", {}).items():
            st = rec.get("status", "not_run")
            extra = rec.get("tool") or rec.get("reason") or rec.get("detail") or ""
            p.append(f'<div class="cap cap-{_e(st)}"><span class="st">{_e(st)}</span>'
                     f'<span class="nm">{_e(cap)}</span><p>{_e(extra)}</p></div>')
        p.append('</div>')

    # Decision bar — live counts + export (closes the loop).
    p.append('<div class="decbar"><div class="counts">'
             '<b id="c-approve">0</b> approved &middot; <b id="c-defer">0</b> deferred &middot; '
             '<b id="c-reject">0</b> rejected &middot; <b id="c-pending">0</b> pending</div>'
             '<div class="acts"><button id="copyBtn" type="button">Copy decisions.json</button>'
             '<button id="dlBtn" type="button" class="primary">Download decisions.json</button></div></div>')

    # Lead screenshots (rendered evidence not tied to one item).
    lead = [s for s in screenshots if not s.get("item_ids")]
    if lead:
        p.append('<section><h2>What it looks like</h2><div class="shots">')
        for s in lead:
            p.append(f'<figure class="shot"><img src="{shot_uri[s["path"]]}" '
                     f'alt="{_e(s.get("caption", "rendered evidence"))}">'
                     f'<figcaption>{_e(s.get("caption", ""))}</figcaption></figure>')
        p.append('</div></section>')

    gate = plan.get("gate", {})
    if not gate.get("permissible", True):
        p.append('<p class="blocked">Authority BLOCKED — advisory only: '
                 + _e("; ".join(gate.get("reasons", []))) + '</p>')

    p.append(f'<section><h2>Findings &amp; decisions &mdash; {len(_ordered_items(bundle))} item(s)</h2>')
    p.append('<p class="hint">Set a decision on each item, then Download decisions.json and feed it back to '
             'the Mop. The Mop implements only <b>approved</b> items; Scruffy re-audits to clear them.</p>')

    for n, item in enumerate(_ordered_items(bundle), 1):
        iid = item["id"]
        kind = item.get("kind", "finding")
        cur = decisions.get(iid, {}).get("decision", "pending")
        if cur not in _DECISIONS:
            cur = "pending"
        note = decisions.get(iid, {}).get("note", "")
        d = directions.get(iid)
        item_shots = [s for s in screenshots if iid in (s.get("item_ids") or [])]
        item_refs = [r for r in references if iid in (r.get("for_items") or [])]

        p.append(f'<article class="item kind-{_e(kind)}">')
        p.append(f'<div class="ihead"><span class="rank">{n}</span><div class="ttl">'
                 f'<h3>{_e(item.get("title"))}</h3>'
                 f'<p class="meta">{_e(kind)} &middot; {_e(item.get("category"))} &middot; '
                 f'{_e(item.get("severity"))} &middot; conf {_e(item.get("confidence"))} &middot; '
                 f'<code>{_e(iid)}</code></p></div>'
                 f'<span class="dpill dpill-{cur}" data-pill="{iid}">{_DECISION_LABEL[cur]}</span></div>')
        p.append('<div class="ibody">')

        # Scruffy finding detail.
        if item.get("observation"):
            p.append(f'<p class="lab">Scruffy found</p><p class="txt">{_e(item["observation"])}</p>')
        if item.get("user_impact"):
            p.append(f'<p class="lab">Who it affects</p><p class="txt">{_e(item["user_impact"])}</p>')
        ev = item.get("evidence") or []
        if ev:
            p.append('<p class="lab">Evidence</p><ul class="ev">'
                     + "".join(f'<li>{_e(x)}</li>' for x in ev) + '</ul>')

        # Mop fix + direction.
        if item.get("recommendation"):
            p.append(f'<p class="do"><b>Fix:</b> {_e(item["recommendation"])}</p>')
        if d:
            p.append('<div class="rec"><span class="tag">Recommended direction</span>'
                     f'<p>{_e(d.get("recommended", ""))}</p></div>')
            if d.get("principle"):
                p.append(f'<p class="principle">{_e(d["principle"])}</p>')
            for alt in d.get("alternates", []):
                p.append(f'<p class="alt">{_e(alt)}</p>')

        if item.get("acceptance_checks"):
            p.append('<p class="lab">Acceptance checks</p><ul class="ac">'
                     + "".join(f'<li>{_e(c)}</li>' for c in item["acceptance_checks"]) + '</ul>')

        for s in item_shots:
            p.append(f'<figure class="shot"><img src="{shot_uri[s["path"]]}" '
                     f'alt="{_e(s.get("caption",""))}"><figcaption>{_e(s.get("caption",""))}'
                     f'</figcaption></figure>')
        if item_refs:
            p.append('<p class="lab">Grounded in</p><div class="refs">')
            for r in item_refs:
                app = _e(r.get("app", "reference"))
                note_r = f' &mdash; {_e(r["note"])}' if r.get("note") else ""
                link = f' <a href="{_e(r["url"])}">source</a>' if r.get("url") else ""
                p.append(f'<figure><img src="{ref_uri[r["path"]]}" alt="{app}">'
                         f'<figcaption><b>{app}</b>{note_r}{link}</figcaption></figure>')
            p.append('</div>')

        # Decision control (only real decisions get one).
        if kind in _ACTIONABLE_KINDS:
            p.append(f'<div class="decide dec-{cur}" data-item-id="{iid}" data-decision="{cur}">')
            p.append('<div class="seg" role="group" aria-label="decision">')
            for opt in ("approve", "defer", "reject"):
                on = " on" if cur == opt else ""
                p.append(f'<button type="button" class="b-{opt}{on}" data-set="{opt}">{_DECISION_LABEL[opt]}</button>')
            p.append('</div>')
            p.append(f'<input class="note" type="text" placeholder="note (optional)" value="{_e(note)}">')
            p.append('</div>')
        p.append('</div></article>')
    p.append('</section>')

    aug = "not reported"
    if preflight:
        aug = ", ".join(f"{k}={v.get('status')}" for k, v in preflight["augmentations"].items())
    p.append(f'<footer><span>Scruffy&rsquo;s Mop &middot; augmentations: {_e(aug)} &middot; self-contained</span>'
             '<span>Approve here &rarr; download decisions.json &rarr; Mop implements &rarr; Scruffy re-audits.</span></footer>')
    p.append('</div>')

    audit_meta = {
        "audit_id": findings.get("audit_id"),
        "revision_id": bundle["decisions"].get("revision_id") or findings.get("revision_id"),
        "baseline_revision_id": bundle["decisions"].get("baseline_revision_id"),
        "schema_version": bundle["decisions"].get("schema_version", "2.1"),
    }
    p.append(_SCRIPT.replace("__AUDIT__", json.dumps(audit_meta)))
    p.append(_TAIL)
    doc = "".join(p)
    _assert_self_contained(doc)
    return doc


def _assert_self_contained(doc: str) -> None:
    import re
    loaders = re.findall(r'src="([^"]+)"', doc) + re.findall(r'url\(([^)]+)\)', doc)
    external = [u for u in loaders if not u.startswith("data:")]
    if external:
        raise InteropError(f"dashboard is not self-contained; external loaders: {external}")


def render(bundle_dir, assets_path, out_path, authorized: bool = False) -> Path:
    interop = load_interop()
    bundle = load_bundle(bundle_dir, interop)
    plan = build_plan(bundle, interop, authorized)
    base = Path(assets_path).resolve().parent if assets_path else Path(bundle_dir)
    assets = json.loads(Path(assets_path).read_text(encoding="utf-8")) if assets_path else {}
    doc = build_dashboard_html(bundle, plan, assets, base)
    out = Path(out_path)
    out.write_text(doc, encoding="utf-8")
    return out


_HEAD = """<!doctype html><html lang="en" data-theme="light"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Scruffy's Mop — decision dashboard</title><style>
:root{--fs:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;--mono:ui-monospace,Menlo,monospace;
--paper:#e9eaec;--surface:#fff;--lane:#f2f3f4;--ink:#14161a;--ink2:#4d525c;--ink3:#6d6b69;--rule:#dcdee1;
--brand:#d40f2e;--acton:#fff;--cob:#2a53d8;--crit:#fdeceb;--ok:#1f6b3f;--ok-soft:#e7f2ec;--warn:#8a5a06;--warn-soft:#f6efe2;
--radius:8px;--shadow:0 1px 2px rgb(20 22 26/.06),0 8px 24px rgb(20 22 26/.05)}
@media(prefers-color-scheme:dark){:root{--paper:#0e0e10;--surface:#17171a;--lane:#131315;--ink:#eae8e4;--ink2:#a5a3a0;
--ink3:#757a85;--rule:#272729;--brand:#ff3542;--acton:#0e0e10;--cob:#5b82ff;--crit:#2a1618;--ok:#5eb37a;--ok-soft:#152a1e;--warn:#e0a13c;--warn-soft:#2a2214}}
:root[data-theme=dark]{--paper:#0e0e10;--surface:#17171a;--lane:#131315;--ink:#eae8e4;--ink2:#a5a3a0;--ink3:#757a85;
--rule:#272729;--brand:#ff3542;--acton:#0e0e10;--cob:#5b82ff;--crit:#2a1618;--ok:#5eb37a;--ok-soft:#152a1e;--warn:#e0a13c;--warn-soft:#2a2214}
*{box-sizing:border-box;margin:0}body{font:14px/1.5 var(--fs);color:var(--ink);background:var(--paper);
font-variant-numeric:tabular-nums;padding:32px 20px 80px}.wrap{max-width:920px;margin:0 auto}a{color:var(--cob)}
code{font-family:var(--mono);font-size:.9em}
header{border-bottom:1px solid var(--rule);padding-bottom:20px;margin-bottom:20px}
.kick{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--brand);font-weight:600}
h1{font-size:25px;margin:8px 0 4px}.target{font-size:12.5px;color:var(--ink3)}
.caps{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:16px}
.cap{border:1px solid var(--rule);border-radius:var(--radius);background:var(--surface);padding:12px 14px;box-shadow:var(--shadow)}
.cap .st{float:right;font-size:11px;text-transform:uppercase;letter-spacing:.06em;font-weight:600;color:var(--ink3)}
.cap-available .st{color:var(--ok)}.cap-absent .st{color:var(--warn)}.cap .nm{font-weight:600;font-size:12.5px}.cap p{font-size:12px;color:var(--ink2);margin-top:6px}
.decbar{position:sticky;top:0;z-index:9;display:flex;flex-wrap:wrap;gap:10px;justify-content:space-between;align-items:center;
background:var(--surface);border:1px solid var(--rule);border-radius:var(--radius);padding:10px 14px;box-shadow:var(--shadow);margin-bottom:24px}
.counts{font-size:12.5px;color:var(--ink2)}.counts b{color:var(--ink);font-variant-numeric:tabular-nums}
.acts{display:flex;gap:8px}.acts button{font:inherit;font-size:12.5px;border:1px solid var(--rule);background:var(--lane);color:var(--ink);
border-radius:var(--radius);padding:7px 12px;cursor:pointer}.acts button:hover{border-color:var(--ink3)}
.acts button.primary{background:var(--brand);color:var(--acton);border-color:var(--brand)}
section{margin-top:24px}h2{font-size:15px;padding-bottom:8px;border-bottom:1px solid var(--rule);margin-bottom:8px}
.hint{font-size:12.5px;color:var(--ink3);margin-bottom:16px}.hint b{color:var(--ink2)}
.shots{display:grid;grid-template-columns:1fr 1fr;gap:12px}@media(max-width:720px){.shots{grid-template-columns:1fr}}
figure.shot{margin:0 0 12px;border:1px solid var(--rule);border-radius:var(--radius);overflow:hidden;background:var(--surface);box-shadow:var(--shadow)}
figure.shot img{display:block;width:100%;height:auto}figure.shot figcaption{font-size:12px;color:var(--ink2);padding:8px 12px;border-top:1px solid var(--rule)}
.blocked{color:var(--brand);font-size:12.5px;margin-bottom:12px}
.item{border:1px solid var(--rule);border-radius:var(--radius);background:var(--surface);box-shadow:var(--shadow);overflow:hidden;margin-bottom:16px}
.ihead{display:flex;gap:12px;align-items:flex-start;padding:14px 16px;border-bottom:1px solid var(--rule)}
.rank{font-family:var(--mono);font-size:12.5px;color:var(--acton);background:var(--ink);border-radius:6px;padding:2px 8px;flex:none;margin-top:2px}
.ttl{flex:1;min-width:0}.ihead h3{font-size:15px}.meta{font-size:12px;color:var(--ink3);margin-top:3px}
.dpill{flex:none;font-size:11px;text-transform:uppercase;letter-spacing:.05em;font-weight:600;border-radius:999px;padding:3px 10px;border:1px solid var(--rule);color:var(--ink3)}
.dpill-approve{color:var(--ok);background:var(--ok-soft);border-color:transparent}
.dpill-defer{color:var(--warn);background:var(--warn-soft);border-color:transparent}
.dpill-reject{color:var(--brand);background:var(--crit);border-color:transparent}
.ibody{padding:14px 16px}
.lab{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink3);margin:12px 0 4px}
.txt{font-size:13px;color:var(--ink2)}ul.ev,ul.ac{margin:2px 0 0 18px;font-size:12.5px;color:var(--ink2)}
.do{font-size:13px;color:var(--ink2);margin-top:12px}.do b{color:var(--ink)}
.rec{border:1px solid var(--brand);background:var(--crit);border-radius:var(--radius);padding:12px;margin:10px 0}
.rec .tag{font-size:11px;text-transform:uppercase;letter-spacing:.08em;font-weight:600;color:var(--brand)}.rec p{margin-top:5px}
.principle{font-size:12.5px;color:var(--cob);margin-bottom:6px}.alt{font-size:12.5px;color:var(--ink2);margin-left:14px}
.refs{display:flex;gap:12px;flex-wrap:wrap}.refs figure{margin:0;width:190px;max-width:100%;border:1px solid var(--rule);border-radius:6px;overflow:hidden;background:var(--lane)}
.refs img{display:block;width:100%;height:112px;object-fit:cover;object-position:top left;border-bottom:1px solid var(--rule)}
.refs figcaption{font-size:11px;color:var(--ink2);padding:5px 8px}.refs b{color:var(--ink)}
.decide{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-top:14px;padding-top:14px;border-top:1px dashed var(--rule)}
.seg{display:inline-flex;border:1px solid var(--rule);border-radius:var(--radius);overflow:hidden}
.seg button{font:inherit;font-size:12.5px;border:0;border-right:1px solid var(--rule);background:var(--surface);color:var(--ink2);padding:7px 14px;cursor:pointer}
.seg button:last-child{border-right:0}.seg button:hover{background:var(--lane)}
.seg .b-approve.on{background:var(--ok);color:#fff}.seg .b-defer.on{background:var(--warn);color:#fff}.seg .b-reject.on{background:var(--brand);color:var(--acton)}
.note{flex:1;min-width:160px;font:inherit;font-size:12.5px;border:1px solid var(--rule);border-radius:var(--radius);background:var(--paper);color:var(--ink);padding:7px 10px}
.note:focus{outline:2px solid var(--cob);outline-offset:1px}
footer{margin-top:24px;padding-top:16px;border-top:1px solid var(--rule);font-size:11px;color:var(--ink3);display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
.tt{position:fixed;top:14px;right:14px;z-index:20;font:inherit;font-size:12px;color:var(--ink2);background:var(--surface);border:1px solid var(--rule);border-radius:999px;padding:6px 12px;cursor:pointer}
</style></head><body><button class="tt" onclick="var r=document.documentElement;r.setAttribute('data-theme',r.getAttribute('data-theme')=='dark'?'light':'dark')">Toggle theme</button>"""

_SCRIPT = """<script>
(function(){
  var AUDIT = __AUDIT__;
  function refresh(){
    var c={approve:0,defer:0,reject:0,pending:0};
    document.querySelectorAll('.decide').forEach(function(el){var d=el.dataset.decision||'pending';c[d]=(c[d]||0)+1;});
    ['approve','defer','reject','pending'].forEach(function(k){var n=document.getElementById('c-'+k);if(n)n.textContent=c[k]||0;});
  }
  document.querySelectorAll('.decide').forEach(function(el){
    var pill=document.querySelector('[data-pill="'+el.dataset.itemId+'"]');
    el.querySelectorAll('.seg button').forEach(function(b){
      b.addEventListener('click',function(){
        var v=b.dataset.set; el.dataset.decision=v; el.className='decide dec-'+v;
        el.querySelectorAll('.seg button').forEach(function(x){x.classList.toggle('on',x===b);});
        if(pill){pill.className='dpill dpill-'+v; pill.textContent=v.charAt(0).toUpperCase()+v.slice(1);}
        refresh();
      });
    });
  });
  function build(){
    var decisions=[].map.call(document.querySelectorAll('.decide'),function(el){
      return {item_id:el.dataset.itemId, decision:el.dataset.decision||'pending',
        note:(el.querySelector('.note')||{}).value||'', updated_at:new Date().toISOString(),
        decision_source:'current', destination_id:null, history:[]};
    });
    return JSON.stringify({schema_version:AUDIT.schema_version||'2.1', audit_id:AUDIT.audit_id,
      revision_id:AUDIT.revision_id, baseline_revision_id:AUDIT.baseline_revision_id||null, decisions:decisions}, null, 2);
  }
  var copyBtn=document.getElementById('copyBtn'), dlBtn=document.getElementById('dlBtn');
  copyBtn.addEventListener('click',function(){
    var t=build();
    if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t).then(function(){
      copyBtn.textContent='Copied \\u2713'; setTimeout(function(){copyBtn.textContent='Copy decisions.json';},1400);});}
  });
  dlBtn.addEventListener('click',function(){
    var b=new Blob([build()],{type:'application/json'}); var u=URL.createObjectURL(b);
    var a=document.createElement('a'); a.href=u; a.download='decisions.json'; document.body.appendChild(a); a.click();
    document.body.removeChild(a); URL.revokeObjectURL(u);
  });
  refresh();
})();
</script>"""

_TAIL = "</body></html>"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Generate a self-contained Mop decision dashboard")
    p.add_argument("bundle", help="Scruffy audit bundle directory")
    p.add_argument("--assets", help="assets manifest JSON")
    p.add_argument("--out", required=True, help="output HTML path")
    p.add_argument("--authorized", action="store_true")
    args = p.parse_args(argv)
    try:
        out = render(args.bundle, args.assets, args.out, args.authorized)
    except InteropError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    print(f"wrote {out} ({out.stat().st_size // 1024} KB), self-contained")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
